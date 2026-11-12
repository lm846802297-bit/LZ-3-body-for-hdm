#!/usr/bin/env python3
"""Fixed-speed Xe-131 d sigma/dER curve for the supplied 450 keV benchmark.

Numerical run uses the AFH GCN/JJ55 Xe-131 response tables and the Eq. (6) kernel.
"""
from __future__ import annotations
import argparse, csv, math, sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import eq6_kernel
from joint_xe131 import isotope_mass_GeV, load_nuclear_response

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--response-dir",type=Path,default=HERE/"results"/"anand_wm_response")
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--nw",type=int,default=20)
    ap.add_argument("--nz",type=int,default=16)
    ap.add_argument("--nphi",type=int,default=12)
    ap.add_argument("--step-keV",type=float,default=5.)
    args=ap.parse_args()
    A=131
    mA=isotope_mass_GeV(A)
    mchi=1000.
    dm=450e-6
    ms=300e-6
    mchi2=mchi+dm
    mV=10.
    v=776.
    coupling_product_sq=1.
    beta=v/eq6_kernel.C_KM_S
    pchi=mchi*beta/math.sqrt(1-beta*beta)
    responses={model:load_nuclear_response(args.response_dir/f"xe{A}_{model.upper()}_WM.csv",A,model) for model in ("gcn","jj55")}
    # Determine the open recoil interval, then scan it on a common grid.
    ers=np.arange(130.,671.,args.step_keV)
    rows=[]
    for erkeV in ers:
        ER=erkeV*1e-6
        wmin,wmax=eq6_kernel.limits(mchi,ms,dm,mA,ER,v)
        opened=wmax>wmin
        if not opened:
            continue
        I6=eq6_kernel.reduced_kernel(mchi,ms,dm,mA,ER,v,nw=args.nw,nz=args.nz,nphi=args.nphi,width_scheme="zero")
        denominator=(mV*mV+2*mA*ER)**2
        for model,response in responses.items():
            RA,_=response.at_recoil(ER,mA)
            dsigma=(mA*coupling_product_sq*RA*I6)/(256*math.pi**3*pchi**2*denominator)
            rows.append({"A":A,"model":model.upper(),"ER_keV":float(erkeV),"RA":RA,"I6_GeV2":I6,"pchi_GeV":pchi,"mV_GeV":mV,"coupling_product_sq":coupling_product_sq,"speed_km_s":v,"width_scheme":"zero","dsigma_dER_GeVminus3":dsigma,"dsigma_dER_cm2_per_keV":dsigma*0.3893793721e-27*1e-6})
    if not rows:
        raise RuntimeError("No open recoil points were generated; check the scan range and kinematic inputs.")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    print(f"rows={len(rows)}; ER range={rows[0]['ER_keV']}..{rows[-1]['ER_keV']} keV")
    print(f"Xe-131 mA={mA:.12g} GeV; pchi={pchi:.12g} GeV; mchi2={mchi2:.12g} GeV")
    for model in ("GCN","JJ55"):
        rr=[r for r in rows if r["model"]==model]
        imax=max(rr,key=lambda x:x["dsigma_dER_GeVminus3"])
        print(f"{model}: max dσ/dER={imax['dsigma_dER_GeVminus3']:.12e} GeV^-3 at ER={imax['ER_keV']} keV")

if __name__=="__main__":
    main()
