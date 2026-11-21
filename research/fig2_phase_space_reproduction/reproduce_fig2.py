#!/usr/bin/env python3
"""Exact fixed-speed, matched-threshold 2->2 / 2->3 Fig. 2 phase-space benchmark.

Implements source-PDF Eqs. (90)-(92) in the constant-amplitude limit.
The source PDF is not redistributed; its vector-path digitization and hash
are documented in the accompanying audit and summary.
"""
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.optimize import brentq, minimize_scalar
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
MCHI=1.0e9       # keV; adopted 1 TeV benchmark (not stated in Fig. 2 caption)
MT=122.0e6       # keV; approximate xenon target mass
MS=300.0         # keV
SPEED=780.0      # km/s
C=299792.458     # km/s
PDF_SHA256="b4fc7bd73265df2bc2ce1640cbf8847b63323ec1dda220f9e7903f4620b871bb"

def delta_w2(er):
    beta=SPEED/C
    gamma=1/math.sqrt(1-beta*beta)
    p=gamma*MCHI*beta
    e=gamma*MCHI
    er=np.asarray(er,dtype=float)
    q=np.sqrt(np.maximum(er*(er+2*MT),0))
    return 2*p*q-2*(e+MT)*er-2*MCHI*MS-MS*MS

def endpoints():
    f=lambda x: float(delta_w2(x))
    grid=np.linspace(0,1000,2001)
    vals=[f(x) for x in grid]
    roots=[]
    for a,b,fa,fb in zip(grid[:-1],grid[1:],vals[:-1],vals[1:]):
        if fa*fb<0: roots.append(brentq(f,a,b,xtol=1e-12))
    if len(roots)!=2: raise RuntimeError(f"Expected two endpoints, got {roots}")
    return roots

def phase_space(er,order=512):
    d=delta_w2(er)
    out=np.zeros_like(np.asarray(er,dtype=float))
    mask=d>0
    x,w=leggauss(order)
    u=(x+1)/2
    wu=w/2
    dm=d[mask,None]
    s=dm*u[None,:]**2
    integ=dm*u[None,:]*np.sqrt(np.maximum(s*(4*MCHI*MS+s),0))/((MCHI+MS)**2+s)
    out[mask]=integ@wu
    return out

def nr_shape(er):
    beta=SPEED/C
    mu=MCHI*MT/(MCHI+MT)
    q=np.sqrt(np.maximum(2*MT*np.asarray(er),0))
    D=beta*q-q*q/(2*mu)-MS
    z=np.maximum(D,0)
    root=np.sqrt(z*(z+2*MS))
    return np.where(D>0,((z+MS)*root-MS*MS*np.arcsinh(np.sqrt(z*(z+2*MS))/MS))/2,0)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--quadrature-order",type=int,default=512)
    ap.add_argument("--n-grid",type=int,default=701)
    args=ap.parse_args()
    lo,hi=endpoints()
    er=np.unique(np.r_[np.linspace(0,700,args.n_grid),lo,hi])
    raw=phase_space(er,args.quadrature_order)
    norm=np.trapezoid(raw,er)
    p23=raw/norm
    p22=np.where((er>=lo)&(er<=hi),1/(hi-lo),0)
    nr=nr_shape(er); pnr=nr/np.trapezoid(nr,er)
    peak=minimize_scalar(lambda x:-float(phase_space(np.array([x]),args.quadrature_order)[0]),
                         bounds=(lo,hi),method="bounded",options={"xatol":1e-8})
    peak_y=-peak.fun/norm
    # Exact-versus-heavy-particle endpoint cross-check.
    beta=SPEED/C; mu=MCHI*MT/(MCHI+MT)
    root=math.sqrt(beta*beta-2*MS/mu)
    nr_ep=(mu*mu*(beta-root)**2/(2*MT),mu*mu*(beta+root)**2/(2*MT))
    # Quadrature-order convergence on open recoil points.
    raw256=phase_space(er,256); mask=raw>0
    qerr=float(np.max(np.abs(raw256[mask]-raw[mask])/raw[mask]))
    out=HERE/"data"; figs=HERE/"figures"
    out.mkdir(exist_ok=True); figs.mkdir(exist_ok=True)
    rows=[]
    for x in np.arange(0,700.0001,5):
        rows.append({"ER_keV":x,"P22_unit_area_per_keV":float(np.interp(x,er,p22)),
                     "P23_exact_unit_area_per_keV":float(np.interp(x,er,p23)),
                     "P23_heavy_particle_unit_area_per_keV":float(np.interp(x,er,pnr)),
                     "deltaW2_exact_keV2":float(delta_w2(x))})
    with (out/"fig2_spectra_780km_s.csv").open("w",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=rows[0]); wr.writeheader(); wr.writerows(rows)
    summary={"status":"reproducible constant-amplitude phase-space diagnostic; source input discrepancy open",
      "source_pdf":{"page":3,"sha256":PDF_SHA256,"curves_digitized_from_pdf_vector_paths":True},
      "inputs":{"mchi1_GeV":1000,"mT_GeV":122,"ms_keV":300,"delta_iDM_keV":300,"speed_km_s":780,
                "mchi1_is_adopted_not_in_Fig2_caption":True,"nuclear_response":"omitted as in source caption"},
      "exact_Eq_90_92":{"recoil_endpoints_keV":[lo,hi],"P22_plateau_1e3_per_keV":1e3/(hi-lo),
        "P23_peak_ER_keV":float(peak.x),"P23_peak_1e3_per_keV":1e3*peak_y,
        "P23_unit_area_integral":float(np.trapezoid(p23,er)),"quadrature_order":args.quadrature_order,
        "max_relative_difference_order256_vs_order512":qerr},
      "heavy_particle_Eq_95_97":{"endpoints_keV":list(nr_ep),
        "max_endpoint_difference_keV":max(abs(lo-nr_ep[0]),abs(hi-nr_ep[1])),
        "unit_area_integral":float(np.trapezoid(pnr,er))},
      "source_vector_digitization":{"2to2_lower_keV":108.4582840178,"2to2_upper_keV":660.2604492825,
        "2to2_plateau_1e3_per_keV":1.8146911620,"2to3_peak_keV":326.4215893122,
        "2to3_peak_1e3_per_keV":3.0931007954},
      "source_comparison":{"plateau_relative_difference":(1/(hi-lo))/0.0018146911620-1,
        "peak_position_difference_keV":float(peak.x)-326.4215893122,
        "peak_height_relative_difference":peak_y/(3.0931007954e-3)-1},
      "interpretation":"The nominal 780 km/s result is retained; no parameter tuning to force source-curve agreement."}
    (out/"fig2_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    plt.figure(figsize=(8,5))
    plt.plot(er,p22*1e3,label="2→2 exact, unit area")
    plt.plot(er,p23*1e3,label="2→3 exact phase space, unit area")
    plt.plot(er,pnr*1e3,"--",label="2→3 heavy-particle check")
    plt.xlabel(r"$E_R$ [keV]"); plt.ylabel(r"$10^3 P(E_R)$ [keV$^{-1}$]")
    plt.title(r"Matched threshold: $m_s=\delta_{\rm iDM}=300$ keV, $v=780$ km/s")
    plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
    plt.savefig(figs/"fig2_reproduction.svg"); plt.close()
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
