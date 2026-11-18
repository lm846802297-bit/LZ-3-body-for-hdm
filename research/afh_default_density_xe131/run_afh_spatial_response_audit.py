#!/usr/bin/env python3
"""AFH v6.0 Python translation for M/PhiPP and provisional spatial responses.

The shared M/PhiPP/M-PhiPP implementation is cross-checked against native
Xe-131 AFH indices 1, 4 and 7 at eight q anchors. SigmaPrime, Delta and their
interference remain development translations until native Wolfram indices
3, 6 and 8 are compared point by point. No three-body tensor contraction is
included.
"""
from __future__ import annotations
import argparse, csv, json, math
from functools import lru_cache
from pathlib import Path
import numpy as np
from scipy.special import hyp1f1, factorial2
from sympy import Rational, N as symN
from sympy.physics.wigner import wigner_3j, wigner_6j, wigner_9j

ROOT = Path(__file__).resolve().parents[1]
MATRIX_DIR = ROOT / "afh_default_density_natural_xenon_halo" / "input" / "afh_default_density_matrices"
ISOTOPES = (129, 131)
Q_POINTS = (0.0, 0.05, 0.10, 0.158, 0.20, 0.25625, 0.30, 0.365, 0.45, 0.49925, 0.60)
FM_TO_GEV_INV = 5.0677

def h(x):
    return Rational(int(round(2*float(x))), 2)

def jnorm(j):
    return 2.0*float(j)+1.0

def qnorm(j):
    x=2.0*float(j)+1.0
    return math.sqrt(x) if x >= 0 else 0.0

@lru_cache(None)
def w3(a,b,c):
    try: return float(symN(wigner_3j(h(a),h(b),h(c),0,0,0),18))
    except ValueError: return 0.0

@lru_cache(None)
def w6(a,b,c,d,e,f):
    try: return float(symN(wigner_6j(h(a),h(b),h(c),h(d),h(e),h(f)),18))
    except ValueError: return 0.0

@lru_cache(None)
def w9(a,b,c,d,e,f,g,i,j):
    try: return float(symN(wigner_9j(h(a),h(b),h(c),h(d),h(e),h(f),h(g),h(i),h(j)),18))
    except ValueError: return 0.0

def orbital(Np, two_j):
    jp=(two_j+1)//2
    ell=jp if (Np-jp)%2==0 else jp-1
    n=(Np-ell)//2+1
    if n < 1: raise ValueError("invalid AFH oscillator orbital")
    return n,ell

def bessel(y,np_,lp,n,l,L):
    if L < 0: return 0.0
    f1=2.0**L/float(factorial2(2*L+1))*y**(L/2)*math.exp(-y)*math.sqrt(math.factorial(np_-1)*math.factorial(n-1))
    f2=math.sqrt(math.gamma(np_+lp+0.5)*math.gamma(n+l+0.5))
    total=0.0
    for m in range(n):
        for mp in range(np_):
            s1=(-1.0)**(m+mp)/(math.factorial(m)*math.factorial(mp)*math.factorial(n-1-m)*math.factorial(np_-1-mp))
            s2=math.gamma((l+lp+L+2*m+2*mp+3)/2)/(math.gamma(l+m+1.5)*math.gamma(lp+mp+1.5))
            a=(L-lp-l-2*mp-2*m)/2
            total += s1*s2*hyp1f1(a,L+1.5,y)
    return f1*f2*total

def bessel_derivative(y,np_,lp,n,l,L,kind):
    # lcap=1 has a finite y->0 limit; lcap=0 terms vanish in the complete
    # Phi'' combination at y=0 and are set to their limiting value.
    if L < 0 or y < 0 or (y == 0 and L == 0): return 0.0
    f1=2.0**(L-1)/float(factorial2(2*L+1))*y**((L-1)/2)*math.exp(-y)*math.sqrt(math.factorial(np_-1)*math.factorial(n-1))
    f2=math.sqrt(math.gamma(np_+lp+0.5)*math.gamma(n+l+0.5))
    total=0.0
    for m in range(n):
        for mp in range(np_):
            s1=(-1.0)**(m+mp)/(math.factorial(m)*math.factorial(mp)*math.factorial(n-1-m)*math.factorial(np_-1-mp))
            s2=math.gamma((l+lp+L+2*m+2*mp+2)/2)/(math.gamma(l+m+1.5)*math.gamma(lp+mp+1.5))
            a=(L-lp-l-2*mp-2*m-1)/2
            first=-(l+lp+L+2*m+2*mp+2)/2*hyp1f1(a,L+1.5,y)
            second=(2*m if kind=="minus" else 2*l+2*m+1)*hyp1f1(a+1,L+1.5,y)
            total += s1*s2*(first+second)
    return f1*f2*total

def abnormal_allowed(Np,tjp,N,tj,L):
    nrp,lp=orbital(Np,tjp); nr,l=orbital(N,tj)
    jp=tjp/2; j=tj/2
    return nrp>0 and nr>0 and abs(j-jp)<=L<=j+jp and (-1)**(lp+l+L+1)==1

def normal_allowed(Np,tjp,N,tj,L):
    nrp,lp=orbital(Np,tjp); nr,l=orbital(N,tj)
    jp=tjp/2; j=tj/2
    return nrp>0 and nr>0 and abs(j-jp)<=L<=j+jp and (-1)**(lp+l+L)==1

def m_element(y,Np,tjp,N,tj,L):
    if not normal_allowed(Np,tjp,N,tj,L): return 0.0
    nrp,lp=orbital(Np,tjp); nr,l=orbital(N,tj); jp=tjp/2; j=tj/2
    phase=(-1)**int(round(0.5+j+L))
    pref=math.sqrt(jnorm(j)*jnorm(jp)*jnorm(l)*jnorm(lp)*jnorm(L)/(4*math.pi))
    return phase*pref*w3(lp,L,l)*w6(lp,jp,.5,j,l,L)*bessel(y,nrp,lp,nr,l,L)

def sigma_prime_element(y,Np,tjp,N,tj,L):
    if not abnormal_allowed(Np,tjp,N,tj,L): return 0.0
    nrp,lp=orbital(Np,tjp); nr,l=orbital(N,tj); jp=tjp/2; j=tj/2
    def mjl_sigma(lcap):
        if lcap < 0: return 0.0
        pref=(-1)**lp*math.sqrt(jnorm(j)*jnorm(jp)*jnorm(l)*jnorm(lp)*jnorm(L)*jnorm(lcap)/(4*math.pi))*math.sqrt(6)
        return pref*w3(lp,lcap,l)*w9(lp,l,lcap,.5,.5,1,jp,j,L)*bessel(y,nrp,lp,nr,l,lcap)
    return -math.sqrt(L)/qnorm(L)*mjl_sigma(L+1)+math.sqrt(L+1)/qnorm(L)*mjl_sigma(L-1)

def delta_inner_element(y,Np,tjp,N,tj,L):
    """AFH MJLDivQ with lcap=L: Deltaop, the operator called by DeltaJ."""
    nrp,lp=orbital(Np,tjp); nr,l=orbital(N,tj); jp=tjp/2; j=tj/2
    def divq(lcap):
        if lcap < 0: return 0.0
        overall=(-1)**int(round(lcap+j+0.5))*qnorm(lp)*qnorm(jp)*qnorm(j)*qnorm(L)*qnorm(lcap)*w6(lp,jp,.5,j,l,L)/math.sqrt(4*math.pi)
        s1=-math.sqrt(l+1)*qnorm(l+1)*w6(lcap,1,L,l,lp,l+1)*w3(lp,lcap,l+1)*bessel_derivative(y,nrp,lp,nr,l,lcap,"minus")
        s2=0.0
        if l>0:
            s2=math.sqrt(l)*qnorm(l-1)*w6(lcap,1,L,l,lp,l-1)*w3(lp,lcap,l-1)*bessel_derivative(y,nrp,lp,nr,l,lcap,"plus")
        return overall*(s1+s2)
    return divq(L)

def delta_element(y,Np,tjp,N,tj,L):
    # AFH DeltaJ calls Deltaop=MJLDivQ(..., jcap=L, lcap=L); DeltaPrime is distinct.
    if not abnormal_allowed(Np,tjp,N,tj,L): return 0.0
    return delta_inner_element(y,Np,tjp,N,tj,L)

def phi_pp_element(y,Np,tjp,N,tj,L):
    """AFH PhiPPJ translated from the native v6.0 source, Eq. source lines 885-892."""
    if not normal_allowed(Np,tjp,N,tj,L): return 0.0
    nrp,lp=orbital(Np,tjp); nr,l=orbital(N,tj); jp=tjp/2; j=tj/2
    overall=(-1)**int(round(lp+1))*6*qnorm(lp)*qnorm(jp)*qnorm(j)/math.sqrt(4*math.pi)

    def nine(lcap):
        return w9(lp,l,lcap,.5,.5,1,jp,j,L)

    def summand1():
        angular=0.0
        for lc in (L,L+1):
            angular += (-1)**(L-lc+1)*jnorm(lc)*w6(L+1,1,lc,1,L,1)*w6(L+1,1,lc,l,lp,l+1)*nine(lc)
        return qnorm(l+1)*math.sqrt(l+1)*w3(lp,L+1,l+1)*bessel_derivative(y,nrp,lp,nr,l,L+1,"minus")*angular

    def summand2():
        if l==0: return 0.0
        angular=0.0
        for lc in (L,L+1):
            angular += (-1)**(L-lc)*jnorm(lc)*w6(L+1,1,lc,1,L,1)*w6(L+1,1,lc,l,lp,l-1)*nine(lc)
        return qnorm(l-1)*math.sqrt(l)*w3(lp,L+1,l-1)*bessel_derivative(y,nrp,lp,nr,l,L+1,"plus")*angular

    def summand3():
        if L==0: return 0.0
        angular=0.0
        for lc in (L-1,L):
            angular += (-1)**(L-lc+1)*jnorm(lc)*w6(L-1,1,lc,1,L,1)*w6(L-1,1,lc,l,lp,l+1)*nine(lc)
        return qnorm(l+1)*math.sqrt(l+1)*w3(lp,L-1,l+1)*bessel_derivative(y,nrp,lp,nr,l,L-1,"minus")*angular

    def summand4():
        if L==0 or l==0: return 0.0
        angular=0.0
        for lc in (L-1,L):
            angular += (-1)**(L-lc)*jnorm(lc)*w6(L-1,1,lc,1,L,1)*w6(L-1,1,lc,l,lp,l-1)*nine(lc)
        return qnorm(l-1)*math.sqrt(l)*w3(lp,L-1,l-1)*bessel_derivative(y,nrp,lp,nr,l,L-1,"plus")*angular

    upper=qnorm(L+1)*math.sqrt(L+1)*(summand1()+summand2())
    lower=0.0 if L==0 else qnorm(L-1)*math.sqrt(L)*(summand3()+summand4())
    return overall*(upper+lower)

def load_matrix(A):
    path=MATRIX_DIR/f"afh_default_xe{A}_density_matrix.csv"
    with path.open(newline="",encoding="utf-8") as f:
        return [{k:(int(v) if k in {"index","rank","isospin","Nprime","two_jprime","N","two_j"} else float(v))
                 for k,v in row.items()} for row in csv.DictReader(f)]

def amplitudes(A,q,rows):
    Z=54; T=abs(A/2-Z)
    bfm=math.sqrt(41.467/(45*A**(-1/3)-25*A**(-2/3)))
    y=(q*bfm*FM_TO_GEV_INV/2)**2
    iso=math.sqrt(2/(2*T+1))
    out={name:{} for name in ("M","SigmaPrime","Delta","PhiPP")}
    for L in range(15):
        sums={name:0.0 for name in out}
        for r in rows:
            if r["rank"]!=L or r["isospin"]!=0: continue
            args=(r["Nprime"],r["two_jprime"],r["N"],r["two_j"],L)
            c=r["coefficient"]*iso
            sums["M"] += c*m_element(y,*args)
            sums["SigmaPrime"] += c*sigma_prime_element(y,*args)
            sums["Delta"] += c*delta_element(y,*args)
            sums["PhiPP"] += c*phi_pp_element(y,*args)
        for name in out: out[name][L]=sums[name]
    return out

def response_bundle(A,q,rows):
    """Evaluate all four nuclear multipole families once at one q_A."""
    amp=amplitudes(A,q,rows)
    # AFH ResponseNuclear uses 1/2 in the diagonal FF definition and no
    # 1/2 in the interference FF definition. After the isoscalar 1/4
    # combination, all response outputs below carry the same /4 factor.
    wm=sum(v*v for v in amp["M"].values())/4
    ws=sum(v*v for v in amp["SigmaPrime"].values())/4
    wd=sum(v*v for v in amp["Delta"].values())/4
    wsd=sum(amp["SigmaPrime"][L]*amp["Delta"][L] for L in amp["SigmaPrime"])/4
    wphi=sum(v*v for v in amp["PhiPP"].values())/4
    wmphi=sum(amp["M"][L]*amp["PhiPP"][L] for L in amp["M"])/4
    return {
        "W_M00_AFH":wm,
        "W_PhiPP00_AFH":wphi,
        "W_MPhiPP00_AFH":wmphi,
        "W_SigmaPrime00_AFH":ws,
        "W_Delta00_AFH_literal":wd,
        "W_SigmaPrimeDelta00_AFH_literal":wsd,
        "SigmaPrime_over_M":ws/wm if wm else None,
        "Delta_over_M":wd/wm if wm else None,
    },amp


def response(A,q,rows):
    bundle,amp=response_bundle(A,q,rows)
    return (bundle["W_M00_AFH"],bundle["W_SigmaPrime00_AFH"],
            bundle["W_Delta00_AFH_literal"],
            bundle["W_SigmaPrimeDelta00_AFH_literal"],amp)


def phi_response(A,q,rows):
    """Return native-convention W_M, W_PhiPP, W_MPhiPP for tau1=tau2=0."""
    bundle,amp=response_bundle(A,q,rows)
    return (bundle["W_M00_AFH"],bundle["W_PhiPP00_AFH"],
            bundle["W_MPhiPP00_AFH"],amp)


def parity_audit():
    # DeltaJ uses Deltaop with lcap=L; its 3j parity is consistent with abnormal parity.
    return {"delta_wrapper_requires":"l+l'+L odd",
            "deltaop_3j_requires":"l'+L+(l±1) even",
            "logical_conflict":False,
            "delta_prime_is_not_delta_j":True}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,required=True)
    group=p.add_mutually_exclusive_group()
    group.add_argument("--q",type=float,nargs="*",help="explicit q_A values in GeV")
    group.add_argument("--grid-points",type=int,help="uniform q_A grid point count")
    p.add_argument("--q-min",type=float,default=0.0)
    p.add_argument("--q-max",type=float,default=0.6)
    args=p.parse_args()
    if args.grid_points is not None:
        if args.grid_points<2 or args.q_max<=args.q_min:
            p.error("--grid-points must be >=2 and --q-max must exceed --q-min")
        q_values=np.linspace(args.q_min,args.q_max,args.grid_points).tolist()
        grid_mode="uniform"
    else:
        q_values=list(Q_POINTS) if args.q is None else list(args.q)
        if not q_values:
            p.error("at least one q_A value is required")
        grid_mode="selected"
    args.outdir.mkdir(parents=True,exist_ok=True)
    records=[]; summaries={}
    for A in ISOTOPES:
        density_rows=load_matrix(A); isotope=[]
        for q in q_values:
            bundle,_=response_bundle(A,q,density_rows)
            row={"A":A,"q_GeV":q,**bundle}
            records.append(row); isotope.append(row)
        response_ranges={}
        for column in ("W_M00_AFH","W_PhiPP00_AFH","W_MPhiPP00_AFH",
                       "W_SigmaPrime00_AFH","W_Delta00_AFH_literal",
                       "W_SigmaPrimeDelta00_AFH_literal"):
            vals=[float(row[column]) for row in isotope]
            response_ranges[column]={"min":min(vals),"max":max(vals)}
        summaries[str(A)]={
            "density_matrix_entries":len(density_rows),
            "J_A":0.5 if A==129 else 1.5,
            "q_points":len(q_values),
            "q_min_GeV":min(q_values),
            "q_max_GeV":max(q_values),
            "response_ranges":response_ranges,
        }
    csv_name=("afh_spatial_response_full_grid.csv" if grid_mode=="uniform"
              else "afh_spatial_response_selected_q.csv")
    with (args.outdir/csv_name).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    q_grid={"mode":grid_mode,"points":len(q_values),
            "q_min_GeV":min(q_values),"q_max_GeV":max(q_values)}
    if grid_mode=="uniform":
        q_grid["step_GeV"]=(args.q_max-args.q_min)/(args.grid_points-1)
    meta={"source":"AFH DMFormFactor v6.0 operator definitions translated to Python",
          "isospin":"tau1=tau2=0 (AFH isoscalar package convention)",
          "q_grid":q_grid,
          "responses":"W_M, W_PhiPP, W_MPhiPP, W_SigmaPrime, W_Delta, W_SigmaPrimeDelta",
          "normalization":"native ResponseNuclear convention; diagonal and interference FF definitions both reduce to a /4 multipole-amplitude product after the tau1=tau2=0 combination; physical equal-p/n factor four is not applied here",
          "delta_operator_audit":parity_audit(),
          "limitations":["The shared M/PhiPP/M-PhiPP radial and multipole implementation matches native Xe-131 AFH indices 1, 4 and 7 at eight q anchors; this does not validate SigmaPrime or Delta.",
          "SigmaPrime and Delta remain development translations until native Wolfram pointwise comparison of indices 3 and 6; the SigmaPrimeDelta interference requires index 8 comparison.",
          "DeltaJ is mapped to the same-rank MJLDivQ component called by the AFH source; the former parity-conflict diagnosis is withdrawn.",
          "No finite-Q2 baryon-current Pauli form factors or three-body L_mu_nu W_A^mu_nu contraction are included.",
          "No halo integration is included."],
          "isotopes":summaries}
    (args.outdir/"metadata.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"outdir":str(args.outdir),"csv":csv_name,
                      "delta_operator_audit":meta["delta_operator_audit"],
                      "q_grid":q_grid,"isotopes":summaries},indent=2))

if __name__=="__main__": main()
