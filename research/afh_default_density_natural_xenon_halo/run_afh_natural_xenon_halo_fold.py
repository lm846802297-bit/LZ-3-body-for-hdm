#!/usr/bin/env python3
"""AFH-default natural-xenon halo fold for selected Figure-2 recoil points."""
from __future__ import annotations
import argparse, csv, hashlib, json, math, sys
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "figure2_full_reproduction"))
import eq6_kernel

U_GEV = 0.93149410242
ME_U = 0.000548579909065
Z_XE = 54
C_KM_S = 299792.458
C_CM_S = 2.99792458e10
GEV2_TO_CM2 = 0.3893793721e-27
AVOGADRO = 6.02214076e23

BENCHMARKS = {
    "red_ms200_dm1": (200e-6, 1e-3),
    "green_ms300_dm1": (300e-6, 1e-3),
    "black_ms360_dm1": (360e-6, 1e-3),
    "blue_ms300_dm10": (300e-6, 10e-3),
}
CASES = [(name, 101.0) for name in BENCHMARKS] + [
    ("green_ms300_dm1", er) for er in (200.0, 267.0, 542.0)
]

def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def mb_untruncated_pdf(v, v0=220.0, ve=232.0):
    if v < 0.0:
        return 0.0
    return v/(math.sqrt(math.pi)*v0*ve) * (
        math.exp(-((v-ve)/v0)**2) - math.exp(-((v+ve)/v0)**2)
    )

def shm_truncated_pdf(v, v0=220.0, ve=232.0, vesc=544.0):
    if v < 0.0 or v > vesc+ve:
        return 0.0
    z=vesc/v0
    norm=math.erf(z)-2.0*z/math.sqrt(math.pi)*math.exp(-z*z)
    if v < vesc-ve:
        bracket=math.exp(-((v-ve)/v0)**2)-math.exp(-((v+ve)/v0)**2)
    else:
        bracket=math.exp(-((v-ve)/v0)**2)-math.exp(-z*z)
    return v*bracket/(math.sqrt(math.pi)*v0*ve*norm)

def q_response_nr_approx(mA, ER):
    """Non-relativistic approximation q^2=2*m_A*E_R."""
    return math.sqrt(2.0*mA*ER)

def q_kinematic_exact(mA, ER):
    """Exact spatial recoil momentum from the nuclear mass-shell condition."""
    return math.sqrt(2.0*mA*ER+ER*ER)

def q_response_from_convention(mA, ER, convention):
    if convention in ("exact_spatial", "legacy_exact"):
        return q_kinematic_exact(mA,ER)
    if convention=="nr_approx":
        return q_response_nr_approx(mA,ER)
    raise ValueError(f"unknown response-q convention: {convention}")

def vmin_three_body_km_s(mchi, ms, mA, ER):
    q=q_kinematic_exact(mA,ER)
    a=ms+(mA*ER+0.5*ms*ms)/mchi
    beta=(q*ER+a*math.sqrt(q*q-ER*ER+a*a))/(q*q+a*a)
    return C_KM_S*beta

def write_csv(path, rows):
    if not rows:
        raise ValueError(f"no rows for {path}")
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--response-samples",type=Path,default=HERE/"input"/"afh_response_samples.csv")
    ap.add_argument("--isotope-weights",type=Path,default=HERE/"input"/"natural_xenon_isotope_weights.csv")
    ap.add_argument("--out-dir",type=Path,default=HERE/"results")
    ap.add_argument("--mchi-GeV",type=float,default=1000.0)
    ap.add_argument("--mV-GeV",type=float,default=10.0)
    ap.add_argument("--coupling-product-squared",type=float,default=1e-8)
    ap.add_argument("--g2",type=float,default=1.0)
    ap.add_argument("--rho-GeV-cm3",type=float,default=0.3)
    ap.add_argument("--nv",type=int,default=32)
    ap.add_argument("--nw",type=int,default=8)
    ap.add_argument("--nz",type=int,default=8)
    ap.add_argument("--nphi",type=int,default=4)
    ap.add_argument("--response-q-convention",choices=("exact_spatial","nr_approx","legacy_exact"),
                    default="exact_spatial",
                    help="AFH response momentum: exact_spatial is the physical spatial transfer used by AFH and the exact three-body kinematics; nr_approx is the q^2=2*m_A*E_R approximation; legacy_exact is a backward-compatible alias.")
    args=ap.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=True)

    isotope_rows=read_csv(args.isotope_weights)
    available=[r for r in isotope_rows if r["AFH_default_density_available"].lower()=="true"]
    abundance={int(r["A"]):float(r["natural_atom_fraction"]) for r in available}
    atomic_mass={int(r["A"]):float(r["atomic_mass_u"]) for r in isotope_rows}
    mean_atomic_weight=sum(float(r["atomic_mass_u"])*float(r["natural_atom_fraction"]) for r in isotope_rows)
    nuclear_mass={A:(atomic_mass[A]-Z_XE*ME_U)*U_GEV for A in abundance}

    response={}
    response_q={}
    b_values={}
    for r in read_csv(args.response_samples):
        key=(int(r["A"]),float(r["ER_keV"]))
        response[key]=float(r["R_A"])
        response_q[key]=float(r["q_response_GeV"])
        b_values[str(int(r["A"]))]=float(r["b_A_fm"])
    for _, er in CASES:
        for A in abundance:
            if (A,er) not in response:
                raise ValueError(f"missing AFH response sample for Xe-{A}, ER={er} keV")

    rate_factor=(args.rho_GeV_cm3/args.mchi_GeV)*C_CM_S * (
        AVOGADRO*1000.0/mean_atomic_weight
    )*GEV2_TO_CM2*1e-6*86400.0
    speed_orders, speed_weights=leggauss(args.nv)
    results=[]
    for benchmark, er_keV in CASES:
        ms, dm=BENCHMARKS[benchmark]
        ER=er_keV*1e-6
        for halo in ("shm_cutoff","mb_untruncated"):
            vmax=776.0 if halo=="shm_cutoff" else 1600.0
            pdf=shm_truncated_pdf if halo=="shm_cutoff" else mb_untruncated_pdf
            isotope_partials=[]
            for A, xA in abundance.items():
                mA=nuclear_mass[A]
                q_response=q_response_from_convention(mA,ER,args.response_q_convention)
                q_kinematic=q_kinematic_exact(mA,ER)
                RA=response[(A,er_keV)]
                if not math.isclose(q_response,response_q[(A,er_keV)],rel_tol=0.0,abs_tol=2e-10):
                    raise ValueError(
                        f"AFH response sample q mismatch for Xe-{A}, ER={er_keV} keV: "
                        f"selected convention={args.response_q_convention}, "
                        f"computed q={q_response:.12g} GeV, sample q={response_q[(A,er_keV)]:.12g} GeV. "
                        "Regenerate R_A at the selected q; do not relabel the old response sample."
                    )
                vmin=vmin_three_body_km_s(args.mchi_GeV,ms,mA,ER)
                J=0.0
                if vmin < vmax:
                    vs=0.5*(vmax+vmin)+0.5*(vmax-vmin)*speed_orders
                    ws=0.5*(vmax-vmin)*speed_weights
                    for v,w in zip(vs,ws):
                        fv=pdf(float(v))
                        if fv==0.0:
                            continue
                        beta=float(v)/C_KM_S
                        pchi=args.mchi_GeV*beta/math.sqrt(1.0-beta*beta)
                        I6=eq6_kernel.reduced_kernel(
                            args.mchi_GeV,ms,dm,mA,ER,float(v),
                            nw=args.nw,nz=args.nz,nphi=args.nphi,
                            width_scheme="pole",g2=args.g2
                        )
                        pref=mA*args.coupling_product_squared*RA*I6/(
                            256.0*math.pi**3*pchi**2
                        )
                        J+=float(w)*fv*beta*pref
                den=(args.mV_GeV**2+2.0*mA*ER)**2
                contribution=rate_factor*xA*J/den
                isotope_partials.append({
                    "benchmark":benchmark,"ER_keV":er_keV,"halo_model":halo,
                    "A":A,"abundance":xA,"mA_GeV":mA,
                    "q_response_GeV":q_response,"q_kinematic_GeV":q_kinematic,"R_A":RA,
                    "vmin_km_s":vmin,"vmax_km_s":vmax,
                    "open":vmin<vmax,"J_A_GeV":J,
                    "rate_contribution_events_kg_day_keV":contribution,
                    "nv":args.nv,"kernel_quadrature":f"{args.nw}x{args.nz}x{args.nphi}",
                })
            total=sum(r["rate_contribution_events_kg_day_keV"] for r in isotope_partials)
            for r in isotope_partials:
                r["natural_rate_events_kg_day_keV"]=total
            results.extend(isotope_partials)
            opened=";".join(str(r["A"]) for r in isotope_partials if r["open"])
            print(f"{benchmark:18s} ER={er_keV:6.1f} {halo:14s} "
                  f"rate={total:.8e} open={opened or 'none'}")

    write_csv(args.out_dir/"isotope_halo_contributions.csv",results)
    summary=[]
    for benchmark, er in CASES:
        for halo in ("shm_cutoff","mb_untruncated"):
            g=[r for r in results if r["benchmark"]==benchmark and
               r["ER_keV"]==er and r["halo_model"]==halo]
            summary.append({
                "benchmark":benchmark,"ER_keV":er,"halo_model":halo,
                "rate_events_kg_day_keV":sum(r["rate_contribution_events_kg_day_keV"] for r in g),
                "open_isotopes":";".join(str(r["A"]) for r in g if r["open"]),
                "open_abundance_fraction":sum(r["abundance"] for r in g if r["open"]),
            })
    write_csv(args.out_dir/"natural_xenon_halo_rates.csv",summary)
    hash_file=HERE/"results"/"afh_response_input_sha256.txt"
    response_sha=None
    if hash_file.exists():
        for line in hash_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("SHA256:"):
                response_sha=line.split(":",1)[1].strip()
    canonical_response_q = ("exact_spatial" if args.response_q_convention in ("exact_spatial","legacy_exact") else "nr_approx")
    metadata={
        "calculation":"AFH-default natural-xenon isotope-specific halo-folded three-body differential rate",
        "AFH_reference":"Anand, Fitzpatrick and Haxton, Phys. Rev. C 89 (2014) 065501, arXiv:1308.6288; DMFormFactor v6.0 built-in sdgXeA default densities",
        "response_source_sha256":response_sha,
        "response_sample_file":str(args.response_samples),
        "response_sample_sha256":hashlib.sha256(args.response_samples.read_bytes()).hexdigest(),
        "response_sample_rows":len(response),
        "available_isotopes":list(abundance),
        "available_natural_atom_fraction":sum(abundance.values()),
        "omitted_isotopes":[124,126],
        "omitted_natural_atom_fraction":1.0-sum(abundance.values()),
        "abundance_source":"NIST Atomic Weights and Isotopic Compositions for Xenon",
        "abundance_convention":"natural atomic fractions; no renormalization",
        "mean_atomic_weight_g_mol":mean_atomic_weight,
        "mass_scheme":"(NIST atomic isotope mass - 54 electron masses)*u; electronic binding neglected",
        "response_q_convention":canonical_response_q,
        "response_q_formula":("sqrt(2*m_A*E_R+E_R^2) [exact spatial transfer]" if canonical_response_q=="exact_spatial" else "sqrt(2*m_A*E_R) [non-relativistic approximation]"),
        "requested_response_q_mode":args.response_q_convention,
        "kinematic_q_convention":"sqrt(2*m_A*E_R+E_R^2); exact nuclear mass-shell momentum used for v_min and three-body kinematics",
        "b_A_formula":"sqrt(41.467/(45*A^(-1/3)-25*A^(-2/3))) fm",
        "b_A_fm":b_values,
        "m_chi1_GeV":args.mchi_GeV,"m_V_GeV":args.mV_GeV,
        "coupling_product_squared":args.coupling_product_squared,"g2":args.g2,
        "rho_chi_GeV_cm3":args.rho_GeV_cm3,
        "benchmark_sets":{"red_ms200_dm1":{"m_s_keV":200,"Delta_m_MeV":1},
                          "green_ms300_dm1":{"m_s_keV":300,"Delta_m_MeV":1},
                          "black_ms360_dm1":{"m_s_keV":360,"Delta_m_MeV":1},
                          "blue_ms300_dm10":{"m_s_keV":300,"Delta_m_MeV":10}},
        "halo_models":{"shm_cutoff":{"v0_km_s":220,"vE_km_s":232,"vesc_km_s":544,"vmax_lab_km_s":776},
                       "mb_untruncated":{"v0_km_s":220,"vE_km_s":232,"numerical_vmax_km_s":1600}},
        "width_scheme":"pole chi2 -> chi1 s; conditional Dirac/real-scalar/pure-scalar/single-channel",
        "quadrature":{"speed_nodes":args.nv,"kernel":[args.nw,args.nz,args.nphi]},
        "rate_units":"events/(kg day keV)","detector_response":"not applied",
        "native_Mathematica_validation":"pending; response samples are from the source-translated AFH v6.0 table",
    }
    (args.out_dir/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
