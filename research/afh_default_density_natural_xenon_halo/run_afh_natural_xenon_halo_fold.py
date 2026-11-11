#!/usr/bin/env python3
"""AFH-default natural-xenon halo fold for selected Figure-2 recoil points."""
from __future__ import annotations
import argparse, csv, json, math, sys
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

def vmin_three_body_km_s(mchi, ms, mA, ER):
    q=math.sqrt(2.0*mA*ER+ER*ER)
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
    args=ap.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=True)

    isotope_rows=read_csv(args.isotope_weights)
    available=[r for r in isotope_rows if r["AFH_default_density_available"].lower()=="true"]
    abundance={int(r["A"]):float(r["natural_atom_fraction"]) for r in available}
    atomic_mass={int(r["A"]):float(r["atomic_mass_u"]) for r in isotope_rows}
    mean_atomic_weight=sum(float(r["atomic_mass_u"])*float(r["natural_atom_fraction"]) for r in isotope_rows)
    nuclear_mass={A:(atomic_mass[A]-Z_XE*ME_U)*U_GEV for A in abundance}

    response={}
    for r in read_csv(args.response_samples):
        response[(int(r["A"]),float(r["ER_keV"]))]=float(r["R_A"])
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
                q_response=math.sqrt(2.0*mA*ER+ER*ER)
                RA=response[(A,er_keV)]
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
                    "q_response_GeV":q_response,"R_A":RA,
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
    metadata={
        "available_isotopes":list(abundance),
        "available_natural_atom_fraction":sum(abundance.values()),
        "omitted_isotopes":[124,126],
        "omitted_natural_atom_fraction":1.0-sum(abundance.values()),
        "mean_atomic_weight_g_mol":mean_atomic_weight,
        "mass_scheme":"(NIST atomic isotope mass - 54 electron masses)*u; electronic binding neglected",
        "mchi_GeV":args.mchi_GeV,"mV_GeV":args.mV_GeV,
        "coupling_product_squared":args.coupling_product_squared,"g2":args.g2,
        "rho_chi_GeV_cm3":args.rho_GeV_cm3,
        "halo_models":{"shm_cutoff":{"v0":220,"vE":232,"vesc":544,"vmax_lab":776},
                       "mb_untruncated":{"v0":220,"vE":232,"numerical_vmax":1600}},
        "width_scheme":"pole chi2 -> chi1 s; conditional Dirac/real-scalar/pure-scalar/single-channel",
        "quadrature":{"speed_nodes":args.nv,"kernel":[args.nw,args.nz,args.nphi]},
        "rate_units":"events/(kg day keV)","detector_response":"not applied",
    }
    (args.out_dir/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
