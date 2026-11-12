#!/usr/bin/env python3
"""Direct exact-q AME2020 natural-xenon three-body halo fold.

Primary rates use the selected-point direct AFH finite-sum responses independently
validated against 60-digit mpmath. PCHIP values are retained only as a historical
interpolation diagnostic. No CI/GitHub Actions dependency is required.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
sys.path.insert(0, str(RESEARCH / "figure2_full_reproduction"))
import eq6_kernel
from isotope_mass_schemes import (
    AME2020_XE_ATOMIC_MASS_U, NIST_XE_ATOMIC_MASS_U, isotope_mass_GeV,
)
from rate_kinematics import vmin_three_body_km_s

AFH_ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
MASS_SCHEMES = ("nist_nuclear", "ame2020_nuclear")
CASES = (
    ("red_ms200_dm1", 101.0),
    ("green_ms300_dm1", 101.0),
    ("black_ms360_dm1", 101.0),
    ("blue_ms300_dm10", 101.0),
    ("green_ms300_dm1", 200.0),
    ("green_ms300_dm1", 267.0),
    ("green_ms300_dm1", 542.0),
)
BENCHMARKS = {
    "red_ms200_dm1": (200.0e-6, 1.0e-3),
    "green_ms300_dm1": (300.0e-6, 1.0e-3),
    "black_ms360_dm1": (360.0e-6, 1.0e-3),
    "blue_ms300_dm10": (300.0e-6, 10.0e-3),
}
KERNEL_ANCHORS = (
    ("red_ms200_dm1", 101.0, "shm_cutoff"),
    ("green_ms300_dm1", 267.0, "shm_cutoff"),
    ("green_ms300_dm1", 542.0, "mb_untruncated"),
)
C_KM_S = 299_792.458
AVOGADRO = 6.02214076e23
C_CM_S = 2.99792458e10
GEV2_TO_CM2 = 0.3893793721e-27

def read_csv(path: Path):
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(path: Path, rows):
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def load_abundances(path: Path):
    rows = read_csv(path)
    d = {int(r["A"]): float(r["natural_atom_fraction"]) for r in rows}
    expected = {124,126,128,129,130,131,132,134,136}
    if set(d) != expected or not math.isclose(sum(d.values()), 1.0, abs_tol=2e-6):
        raise ValueError("natural xenon abundance table is incomplete or not normalized")
    return d

def load_selected_responses(path: Path):
    rows = read_csv(path)
    out = {}
    for r in rows:
        key = (r["mass_scheme"], int(r["A"]), float(r["ER_keV"]))
        out[key] = {
            "q": float(r["q_exact_spatial_GeV"]),
            "exact": float(r["R_A_exact_q_mpmath"]),
            "pchip": float(r["R_A_PCHIP_2401_grid"]),
            "b_A_fm": float(r["b_A_fm"]),
        }
    expected = {
        (scheme, A, ER)
        for scheme in MASS_SCHEMES for A in AFH_ISOTOPES
        for ER in (101.0, 200.0, 267.0, 542.0)
    }
    if set(out) != expected:
        raise ValueError(f"selected exact-q table must have 56 unique rows; got {len(out)}")
    for scheme, A, ER in expected:
        mA = isotope_mass_GeV(A, scheme)
        q = math.sqrt(2.0*mA*ER*1e-6 + (ER*1e-6)**2)
        if abs(q-out[(scheme,A,ER)]["q"]) > 2e-10:
            raise ArithmeticError(f"exact spatial q mismatch for {scheme}, Xe-{A}, {ER} keV")
        if not all(math.isfinite(out[(scheme,A,ER)][x]) and out[(scheme,A,ER)][x] >= 0
                   for x in ("exact","pchip")):
            raise ArithmeticError("invalid AFH response value")
    return out

def mean_atomic_weight(abundances, scheme):
    masses = NIST_XE_ATOMIC_MASS_U if scheme == "nist_nuclear" else AME2020_XE_ATOMIC_MASS_U
    return sum(abundances[A] * masses[A] for A in abundances)

def target_rate_factor(rho_dm, mchi, mean_aw):
    n_target_per_kg = AVOGADRO * 1000.0 / mean_aw
    return (rho_dm/mchi) * C_CM_S * n_target_per_kg * GEV2_TO_CM2 * 1e-6 * 86400.0

def mb_pdf(v, v0=220.0, ve=232.0):
    return v/(math.sqrt(math.pi)*v0*ve) * (
        math.exp(-((v-ve)/v0)**2) - math.exp(-((v+ve)/v0)**2)
    )

def shm_pdf(v, v0=220.0, ve=232.0, vesc=544.0):
    if v < 0.0 or v >= vesc+ve:
        return 0.0
    z = vesc/v0
    norm = math.erf(z) - 2.0*z/math.sqrt(math.pi)*math.exp(-z*z)
    if v < vesc-ve:
        bracket = math.exp(-((v-ve)/v0)**2)-math.exp(-((v+ve)/v0)**2)
    else:
        bracket = math.exp(-((v-ve)/v0)**2)-math.exp(-z*z)
    return v*bracket/(math.sqrt(math.pi)*v0*ve*norm)

def speed_nodes(vmin, vmax, n):
    if vmax <= vmin:
        return np.empty(0), np.empty(0)
    x,w = leggauss(n)
    return 0.5*(vmax+vmin)+0.5*(vmax-vmin)*x, 0.5*(vmax-vmin)*w

def compute_integral(task):
    A, scheme, benchmark, ER_keV, halo, nv, nw, nz, nphi = task
    ms, delta_m = BENCHMARKS[benchmark]
    mchi, mV, g2 = 1000.0, 10.0, 1.0
    mA = isotope_mass_GeV(A, scheme)
    ER = ER_keV * 1e-6
    vmin = vmin_three_body_km_s(mchi, ms, mA, ER)
    vmax = 776.0 if halo == "shm_cutoff" else 1600.0
    if vmin >= vmax:
        return {
            "A":A,"mass_scheme":scheme,"benchmark":benchmark,"ER_keV":ER_keV,
            "halo_model":halo,"nv":nv,"nw":nw,"nz":nz,"nphi":nphi,
            "mA_GeV":mA,"vmin_km_s":vmin,"vmax_km_s":vmax,
            "speed_integral_dsigma_GeVminus3":0.0,
        }
    velocities, weights = speed_nodes(vmin, vmax, nv)
    integral = 0.0
    for velocity, weight in zip(velocities, weights):
        v = float(velocity)
        pdf = shm_pdf(v) if halo == "shm_cutoff" else mb_pdf(v)
        if pdf == 0.0:
            continue
        beta = v/C_KM_S
        pchi = mchi*beta/math.sqrt(1.0-beta*beta)
        I6 = eq6_kernel.reduced_kernel(
            mchi, ms, delta_m, mA, ER, v,
            nw=nw, nz=nz, nphi=nphi, width_scheme="pole", g2=g2,
        )
        mediator_denominator = (mV*mV + 2.0*mA*ER)**2
        dsigma = mA*1.0e-8*I6/(256.0*math.pi**3*pchi**2*mediator_denominator)
        integral += float(weight)*pdf*beta*dsigma
    return {
        "A":A,"mass_scheme":scheme,"benchmark":benchmark,"ER_keV":ER_keV,
        "halo_model":halo,"nv":nv,"nw":nw,"nz":nz,"nphi":nphi,
        "mA_GeV":mA,"vmin_km_s":vmin,"vmax_km_s":vmax,
        "speed_integral_dsigma_GeVminus3":integral,
    }

def relative_difference(a,b):
    if a == 0.0 and b == 0.0: return 0.0
    if a == 0.0: return math.inf
    return abs(b/a-1.0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--response-csv", type=Path, default=HERE/"output/afh_default_xenon_responses/selected_q_mpmath/afh_selected_exact_q_responses.csv")
    ap.add_argument("--abundance-csv", type=Path, default=HERE/"input/natural_xenon_isotope_weights.csv")
    ap.add_argument("--nist-reference-csv", type=Path, default=HERE/"results/natural_xenon_halo_rates.csv")
    ap.add_argument("--nist-isotope-reference-csv", type=Path, default=HERE/"results/isotope_halo_contributions_compact.csv")
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--nv-orders", type=int, nargs="+", default=[32,64])
    ap.add_argument("--nw", type=int, default=8)
    ap.add_argument("--nz", type=int, default=8)
    ap.add_argument("--nphi", type=int, default=4)
    ap.add_argument("--skip-kernel-crosschecks", action="store_true")
    ap.add_argument("--integral-cache", type=Path, default=None,
                    help="reuse a previously archived base_kernel_halo_integrals.csv")
    ap.add_argument("--kernel-crosscheck-cache", type=Path, default=None,
                    help="reuse a previously archived kernel_quadrature_convergence.csv")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    abund = load_abundances(args.abundance_csv)
    responses = load_selected_responses(args.response_csv)
    nv_orders = sorted(set(args.nv_orders))
    if len(nv_orders) < 2:
        raise ValueError("at least two speed quadrature orders are required")
    tasks = [
        (A,scheme,b,ER,h,nv,args.nw,args.nz,args.nphi)
        for scheme in MASS_SCHEMES for b,ER in CASES
        for h in ("shm_cutoff","mb_untruncated")
        for A in AFH_ISOTOPES for nv in nv_orders
    ]
    if args.integral_cache is not None:
        integral_rows = read_csv(args.integral_cache)
        for r in integral_rows:
            for k in ("A","nv"):
                r[k] = int(r[k])
            for k in ("ER_keV","mA_GeV","vmin_km_s","vmax_km_s","speed_integral_dsigma_GeVminus3"):
                r[k] = float(r[k])
        expected_keys={(t[0],t[1],t[2],t[3],t[4],t[5]) for t in tasks}
        found_keys={(r["A"],r["mass_scheme"],r["benchmark"],r["ER_keV"],r["halo_model"],r["nv"]) for r in integral_rows}
        if found_keys != expected_keys:
            raise ValueError("integral cache keys do not match the requested full fold")
    elif args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            integral_rows = list(pool.map(compute_integral,tasks,chunksize=1))
    else:
        integral_rows = [compute_integral(t) for t in tasks]
    integral_lookup = {
        (r["A"],r["mass_scheme"],r["benchmark"],r["ER_keV"],r["halo_model"],r["nv"]):r
        for r in integral_rows
    }

    mean_aw = {s:mean_atomic_weight(abund,s) for s in MASS_SCHEMES}
    rate_factors = {s:target_rate_factor(0.3,1000.0,mean_aw[s]) for s in MASS_SCHEMES}
    contributions = []
    sums = defaultdict(float)
    open_isotopes = defaultdict(list)
    for r in integral_rows:
        A,scheme,b,ER,h,nv = (r["A"],r["mass_scheme"],r["benchmark"],r["ER_keV"],r["halo_model"],r["nv"])
        response = responses[(scheme,A,ER)]
        common = rate_factors[scheme]*abund[A]*r["speed_integral_dsigma_GeVminus3"]
        for method,R in (("direct_exact_q",response["exact"]),("historical_2401_PCHIP",response["pchip"])):
            rate = common*R
            row = dict(r)
            row.update({
                "natural_atom_fraction":abund[A],
                "q_exact_spatial_GeV":response["q"],
                "R_A":R,"response_method":method,
                "mean_atomic_weight_g_mol":mean_aw[scheme],
                "rate_contribution_events_kg_day_keV":rate,
            })
            contributions.append(row)
            key=(scheme,b,ER,h,nv,method)
            sums[key]+=rate
            if r["vmin_km_s"] < r["vmax_km_s"]:
                open_isotopes[key].append((A,abund[A]))
    summaries=[]
    for key,total in sorted(sums.items()):
        scheme,b,ER,h,nv,method=key
        opens=open_isotopes[key]
        summaries.append({
            "mass_scheme":scheme,"benchmark":b,"ER_keV":ER,"halo_model":h,"nv":nv,
            "response_method":method,"AFH_7_isotope_rate_events_kg_day_keV":total,
            "open_isotopes":";".join(str(A) for A,f in opens),
            "open_abundance_fraction":sum(f for A,f in opens),
            "AFH_abundance_coverage":sum(abund[A] for A in AFH_ISOTOPES),
        })

    # Reproduce the archived NIST-mass/PCHIP mainline at its original 32-node order.
    old_totals = {
        (r["benchmark"],float(r["ER_keV"]),r["halo_model"]):float(r["rate_events_kg_day_keV"])
        for r in read_csv(args.nist_reference_csv)
    }
    old_iso131 = {
        (r["benchmark"],float(r["ER_keV"]),r["halo_model"]):float(r["rate_contribution_events_kg_day_keV"])
        for r in read_csv(args.nist_isotope_reference_csv) if int(r["A"])==131
    }
    nist_repro=[]
    for key,old in sorted(old_totals.items()):
        b,ER,h=key
        new=sums[("nist_nuclear",b,ER,h,32,"historical_2401_PCHIP")]
        nist_repro.append({
            "benchmark":b,"ER_keV":ER,"halo_model":h,
            "archived_NIST_PCHIP_rate":old,"recomputed_NIST_PCHIP_rate_nv32":new,
            "relative_difference":relative_difference(old,new),
        })
    max_nist_repro=max((r["relative_difference"] for r in nist_repro),default=0.0)
    if max_nist_repro>5e-8:
        raise ArithmeticError(f"NIST PCHIP baseline reproduction failed: {max_nist_repro:.3e}")

    # Speed quadrature convergence, totals and isotope contributions.
    speed_conv=[]
    for scheme in MASS_SCHEMES:
        for b,ER in CASES:
            for h in ("shm_cutoff","mb_untruncated"):
                for method in ("direct_exact_q","historical_2401_PCHIP"):
                    r32=sums[(scheme,b,ER,h,32,method)]
                    r64=sums[(scheme,b,ER,h,64,method)]
                    speed_conv.append({
                        "mass_scheme":scheme,"benchmark":b,"ER_keV":ER,"halo_model":h,
                        "response_method":method,"rate_nv32":r32,"rate_nv64":r64,
                        "relative_difference_32_to_64":relative_difference(r32,r64),
                    })
    isotope_speed_conv=[]
    contrib_lookup={
        (r["mass_scheme"],r["benchmark"],r["ER_keV"],r["halo_model"],r["A"],r["nv"],r["response_method"]):r["rate_contribution_events_kg_day_keV"]
        for r in contributions
    }
    for scheme in MASS_SCHEMES:
        for b,ER in CASES:
            for h in ("shm_cutoff","mb_untruncated"):
                for A in AFH_ISOTOPES:
                    for method in ("direct_exact_q","historical_2401_PCHIP"):
                        a=contrib_lookup[(scheme,b,ER,h,A,32,method)]
                        c=contrib_lookup[(scheme,b,ER,h,A,64,method)]
                        isotope_speed_conv.append({
                            "mass_scheme":scheme,"benchmark":b,"ER_keV":ER,"halo_model":h,
                            "A":A,"response_method":method,"rate_nv32":a,"rate_nv64":c,
                            "relative_difference_32_to_64":relative_difference(a,c),
                        })

    def ppm(new,old):
        if old==0.0: return 0.0 if new==0.0 else math.inf
        return (new/old-1.0)*1e6

    # Interpolation impact and full NIST-vs-AME2020 comparison at 64 speed nodes.
    interpolation=[]
    mass_comparison=[]
    for b,ER in CASES:
        for h in ("shm_cutoff","mb_untruncated"):
            nist_p=sums[("nist_nuclear",b,ER,h,64,"historical_2401_PCHIP")]
            nist_x=sums[("nist_nuclear",b,ER,h,64,"direct_exact_q")]
            ame_p=sums[("ame2020_nuclear",b,ER,h,64,"historical_2401_PCHIP")]
            ame_x=sums[("ame2020_nuclear",b,ER,h,64,"direct_exact_q")]
            interpolation.append({
                "benchmark":b,"ER_keV":ER,"halo_model":h,
                "NIST_PCHIP_rate_nv64":nist_p,"NIST_direct_exact_q_rate_nv64":nist_x,
                "NIST_direct_vs_PCHIP_shift_ppm":ppm(nist_x,nist_p),
                "AME2020_PCHIP_rate_nv64":ame_p,"AME2020_direct_exact_q_rate_nv64":ame_x,
                "AME2020_direct_vs_PCHIP_shift_ppm":ppm(ame_x,ame_p),
            })
            mass_comparison.append({
                "benchmark":b,"ER_keV":ER,"halo_model":h,
                "NIST_direct_exact_q_rate_nv64":nist_x,
                "AME2020_direct_exact_q_rate_nv64":ame_x,
                "AME2020_vs_NIST_direct_exact_q_shift_ppm":ppm(ame_x,nist_x),
                "NIST_PCHIP_rate_nv64":nist_p,"AME2020_PCHIP_rate_nv64":ame_p,
                "AME2020_vs_NIST_PCHIP_shift_ppm":ppm(ame_p,nist_p),
            })

    # Xe-131-only hybrid: preserve all six non-Xe131 NIST historical terms.
    hybrid=[]
    for key,old_total in sorted(old_totals.items()):
        b,ER,h=key
        old131=old_iso131[key]
        nist131_direct=contrib_lookup[("nist_nuclear",b,ER,h,131,32,"direct_exact_q")]
        ame131_direct=contrib_lookup[("ame2020_nuclear",b,ER,h,131,32,"direct_exact_q")]
        new_total=old_total-old131+ame131_direct
        hybrid.append({
            "benchmark":b,"ER_keV":ER,"halo_model":h,
            "NIST_historical_total_PCHIP":old_total,
            "Xe131_NIST_historical_PCHIP":old131,
            "Xe131_NIST_direct_exact_q_nv32":nist131_direct,
            "Xe131_AME2020_direct_exact_q_nv32":ame131_direct,
            "Xe131_only_AME2020_hybrid_total":new_total,
            "Xe131_only_hybrid_shift_vs_historical_NIST_ppm":None if old_total==0 else ppm(new_total,old_total),
            "NIST_Xe131_direct_vs_historical_PCHIP_ppm":None if old131==0 else ppm(nist131_direct,old131),
            "mass_scheme_scope":"Xe-131=AME2020 direct exact-q; other six AFH terms=NIST historical PCHIP",
        })

    # Independent kernel quadrature cross-checks on three anchors.
    kernel_conv=[]
    if args.kernel_crosscheck_cache is not None:
        kernel_conv = read_csv(args.kernel_crosscheck_cache)
        for r in kernel_conv:
            for k in ("ER_keV","rate_low","rate_high","relative_difference"):
                r[k] = float(r[k])
            for k in ("A","speed_nodes"):
                r[k] = int(r[k])
    elif not args.skip_kernel_crosschecks:
        high_tasks=[
            (A,"ame2020_nuclear",b,ER,h,32,16,16,8)
            for b,ER,h in KERNEL_ANCHORS for A in AFH_ISOTOPES
        ]
        if args.workers>1:
            with ProcessPoolExecutor(max_workers=args.workers) as pool:
                high_rows=list(pool.map(compute_integral,high_tasks,chunksize=1))
        else:
            high_rows=[compute_integral(t) for t in high_tasks]
        for hi in high_rows:
            A,b,ER,h,nv=(hi["A"],hi["benchmark"],hi["ER_keV"],hi["halo_model"],hi["nv"])
            low=integral_lookup[(A,"ame2020_nuclear",b,ER,h,nv)]["speed_integral_dsigma_GeVminus3"]
            high=hi["speed_integral_dsigma_GeVminus3"]
            R=responses[("ame2020_nuclear",A,ER)]["exact"]
            rate_factor_here=rate_factors["ame2020_nuclear"]*abund[A]*R
            kernel_conv.append({
                "mass_scheme":"ame2020_nuclear","benchmark":b,"ER_keV":ER,
                "halo_model":h,"A":A,"speed_nodes":nv,
                "kernel_low":"8x8x4","kernel_high":"16x16x8",
                "rate_low":rate_factor_here*low,"rate_high":rate_factor_here*high,
                "relative_difference":relative_difference(low,high),
            })

    # Output native tables.
    out=args.out_dir
    write_csv(out/"base_kernel_halo_integrals.csv",integral_rows)
    write_csv(out/"seven_isotope_contributions.csv",contributions)
    write_csv(out/"seven_isotope_halo_rates.csv",summaries)
    write_csv(out/"response_interpolation_impact.csv",interpolation)
    write_csv(out/"mass_scheme_comparison.csv",mass_comparison)
    write_csv(out/"xe131_only_ame2020_hybrid_direct_exactq.csv",hybrid)
    write_csv(out/"speed_quadrature_convergence.csv",speed_conv)
    write_csv(out/"isotope_speed_quadrature_convergence.csv",isotope_speed_conv)
    write_csv(out/"kernel_quadrature_convergence.csv",kernel_conv)
    write_csv(out/"nist_mainline_reproduction.csv",nist_repro)
    mass_rows=[]
    for A in AFH_ISOTOPES:
        m_nist=isotope_mass_GeV(A,"nist_nuclear")
        m_ame=isotope_mass_GeV(A,"ame2020_nuclear")
        mass_rows.append({
            "A":A,"mA_NIST_GeV":m_nist,"mA_AME2020_GeV":m_ame,
            "AME2020_minus_NIST_ppm":(m_ame/m_nist-1.0)*1e6,
        })
    write_csv(out/"nuclear_mass_scheme_comparison.csv",mass_rows)

    response_rel = {
        scheme:max(abs(responses[(scheme,A,ER)]["pchip"]/responses[(scheme,A,ER)]["exact"]-1.0)
                   for A in AFH_ISOTOPES for ER in (101.0,200.0,267.0,542.0))
        for scheme in MASS_SCHEMES
    }
    meta={
        "calculation":"Selected-point seven-isotope natural-xenon three-body halo fold using direct AFH exact-spatial-q responses",
        "status":"locally recomputed; selected-point result only; not a continuous recoil spectrum or detector-level prediction",
        "ci_used":False,
        "source_branch_head_before_local_recalculation":"fd325c13e0aa82f7c829fa85a3ee3a744e5d8e03",
        "response_input":str(args.response_csv),
        "response_input_sha256":sha256(args.response_csv),
        "response_rows":len(responses),
        "response_validation":"direct AFH finite-sum values independently checked against 60-digit mpmath at selected q points",
        "max_abs_PCHIP_over_direct_response_minus_one_by_mass_scheme":response_rel,
        "AFH_source_archive_sha256":"4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727",
        "AFH_source_file_sha256":"dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372",
        "AFH_isotopes":list(AFH_ISOTOPES),
        "AFH_abundance_coverage":sum(abund[A] for A in AFH_ISOTOPES),
        "missing_AFH_isotopes":[124,126],
        "missing_isotope_abundance":abund[124]+abund[126],
        "abundance_convention":"natural atom fractions; no renormalization of the seven AFH-supported isotopes",
        "mass_schemes":{
            "nist_nuclear":"NIST atomic isotope mass minus 54 electron masses, CODATA-2018 constants; electron binding neglected",
            "ame2020_nuclear":"unrounded AME2020 atomic masses minus 54 CODATA-2022 electron masses plus B_e(54)",
        },
        "dark_sector":{
            "mchi1_GeV":1000.0,"mV_GeV":10.0,"coupling_product_squared":1e-8,
            "g2":1.0,"rho_chi_GeV_cm3":0.3,
            "benchmarks":{k:{"ms_keV":v[0]*1e6,"Delta_m_MeV":v[1]*1e3} for k,v in BENCHMARKS.items()},
            "chi2_width":"pole width for chi2 -> chi1 s, conditional on Dirac chi2, real scalar, pure scalar off-diagonal Yukawa and no other open channels",
        },
        "halo":{
            "shm_cutoff":{"v0_km_s":220.0,"vE_km_s":232.0,"vesc_km_s":544.0,"vmax_km_s":776.0},
            "mb_untruncated":{"v0_km_s":220.0,"vE_km_s":232.0,"integration_vmax_km_s":1600.0,"role":"tail diagnostic"},
        },
        "quadrature":{
            "speed_orders":nv_orders,"baseline_kernel":[args.nw,args.nz,args.nphi],
            "kernel_crosscheck":"16x16x8 at three anchors for all seven isotopes; AME2020 masses",
            "max_total_speed_32_to_64_relative_difference":max(r["relative_difference_32_to_64"] for r in speed_conv),
            "max_isotope_speed_32_to_64_relative_difference":max(r["relative_difference_32_to_64"] for r in isotope_speed_conv),
            "max_kernel_8x8x4_to_16x16x8_relative_difference":max((r["relative_difference"] for r in kernel_conv),default=None),
        },
        "NIST_historical_PCHIP_baseline":{
            "max_reproduction_relative_difference":max(r["relative_difference"] for r in nist_repro),
            "tolerance":5e-8,
            "result":"reproduced with 32-node speed quadrature",
        },
        "response_comparison":{
            "max_rate_shift_NIST_direct_vs_PCHIP_ppm":max(abs(r["NIST_direct_vs_PCHIP_shift_ppm"]) for r in interpolation if math.isfinite(r["NIST_direct_vs_PCHIP_shift_ppm"])),
            "max_rate_shift_AME2020_direct_vs_PCHIP_ppm":max(abs(r["AME2020_direct_vs_PCHIP_shift_ppm"]) for r in interpolation if math.isfinite(r["AME2020_direct_vs_PCHIP_shift_ppm"])),
        },
        "Xe131_only_hybrid":{
            "max_abs_total_shift_ppm":max(abs(r["Xe131_only_hybrid_shift_vs_historical_NIST_ppm"]) for r in hybrid if r["Xe131_only_hybrid_shift_vs_historical_NIST_ppm"] is not None),
            "scope":"Xe-131 is replaced by AME2020 direct exact-q partial; other six isotope terms remain the archived NIST/PCHIP baseline; hybrid only, not full AME2020",
        },
        "rate_units":"events/(kg day keV)",
        "detector_response":"not applied; no efficiency, resolution, exposure, cuts or likelihood",
        "limitations":[
            "Only four selected recoil energies are calculated: 101, 200, 267 and 542 keV.",
            "Direct AFH exact-q response values are validated at these selected points only; no continuous response curve is inferred.",
            "Xe-124 and Xe-126 have no AFH v6.0 default density matrices and are not included in the seven-isotope AFH central result.",
            "The seven-isotope AFH abundance coverage is 0.998158 and is not renormalized.",
            "The 2401-node PCHIP response is retained only as a diagnostic comparison, not used for primary direct-exact-q rates.",
        ],
    }
    (out/"metadata.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")

    # Hash every output file except the manifest itself.
    manifest=[]
    for p in sorted(out.iterdir()):
        if p.is_file() and p.name!="SHA256SUMS.txt":
            manifest.append(f"{sha256(p)}  {p.name}")
    (out/"SHA256SUMS.txt").write_text("\n".join(manifest)+"\n",encoding="utf-8")

    print(json.dumps({
        "status":"LOCAL_DIRECT_EXACT_Q_RECOMPUTATION_COMPLETE",
        "integral_rows":len(integral_rows),"contribution_rows":len(contributions),
        "rate_summary_rows":len(summaries),"NIST_reproduction_max_rel":meta["NIST_historical_PCHIP_baseline"]["max_reproduction_relative_difference"],
        "speed_convergence_max_rel":meta["quadrature"]["max_total_speed_32_to_64_relative_difference"],
        "kernel_convergence_max_rel":meta["quadrature"]["max_kernel_8x8x4_to_16x16x8_relative_difference"],
        "max_hybrid_shift_ppm":meta["Xe131_only_hybrid"]["max_abs_total_shift_ppm"],
        "output_dir":str(out),
    },indent=2))

if __name__=="__main__":
    main()
