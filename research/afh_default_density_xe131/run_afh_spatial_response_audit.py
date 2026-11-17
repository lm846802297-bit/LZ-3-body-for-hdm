#!/usr/bin/env python3
"""AFH v6.0 source translation audit for Sigma' and Delta responses.

The implementation follows the operator definitions in v6/dmformfactor-V6.m.
It is a nuclear-response calculation only (isoscalar tau1=tau2=0), not a
three-body L_mu nu W_A^mu nu contraction. The Delta parity inconsistency is
reported explicitly rather than silently repaired.
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
Q_POINTS = (0.0, 0.05, 0.10, 0.158, 0.20, 0.256, 0.30, 0.365, 0.45, 0.60)
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
    if L < 0 or y <= 0: return 0.0
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
    """Literal AFH DeltaPrime/MJLDivQ expression, before parity wrapper."""
    nrp,lp=orbital(Np,tjp); nr,l=orbital(N,tj); jp=tjp/2; j=tj/2
    def divq(lcap):
        if lcap < 0: return 0.0
        overall=(-1)**int(round(lcap+j+0.5))*qnorm(lp)*qnorm(jp)*qnorm(j)*qnorm(L)*qnorm(lcap)*w6(lp,jp,.5,j,l,L)/math.sqrt(4*math.pi)
        s1=-math.sqrt(l+1)*qnorm(l+1)*w6(lcap,1,L,l,lp,l+1)*w3(lp,lcap,l+1)*bessel_derivative(y,nrp,lp,nr,l,lcap,"minus")
        s2=0.0
        if l>0:
            s2=math.sqrt(l)*qnorm(l-1)*w6(lcap,1,L,l,lp,l-1)*w3(lp,lcap,l-1)*bessel_derivative(y,nrp,lp,nr,l,lcap,"plus")
        return overall*(s1+s2)
    return -math.sqrt(L)/qnorm(L)*divq(L+1)+math.sqrt(L+1)/qnorm(L)*divq(L-1)

def delta_element(y,Np,tjp,N,tj,L):
    # Exact source wrapper: DeltaJ uses PhysicalConditionsAbnormal.
    if not abnormal_allowed(Np,tjp,N,tj,L): return 0.0
    return delta_inner_element(y,Np,tjp,N,tj,L)

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
    out={name:{} for name in ("M","SigmaPrime","Delta")}
    for L in range(15):
        sums={name:0.0 for name in out}
        for r in rows:
            if r["rank"]!=L or r["isospin"]!=0: continue
            args=(r["Nprime"],r["two_jprime"],r["N"],r["two_j"],L)
            c=r["coefficient"]*iso
            sums["M"] += c*m_element(y,*args)
            sums["SigmaPrime"] += c*sigma_prime_element(y,*args)
            sums["Delta"] += c*delta_element(y,*args)
        for name in out: out[name][L]=sums[name]
    return out

def response(A,q,rows):
    amp=amplitudes(A,q,rows)
    wm=sum(v*v for v in amp["M"].values())/4
    ws=sum(v*v for v in amp["SigmaPrime"].values())/4
    wd=sum(v*v for v in amp["Delta"].values())/4
    wsd=sum(amp["SigmaPrime"][L]*amp["Delta"][L] for L in amp["SigmaPrime"])/4
    return wm,ws,wd,wsd,amp

def parity_conflict():
    # Delta's internal 3j requires l'+(J±1)+(l±1) even, i.e. l+l'+J even.
    # Its PhysicalConditionsAbnormal wrapper instead requires l+l'+J odd.
    return {"delta_wrapper_requires":"l+l'+J odd",
            "delta_inner_3j_requires":"l+l'+J even",
            "logical_conflict":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,required=True)
    p.add_argument("--q",type=float,nargs="*",default=list(Q_POINTS),help="q_A values in GeV")
    args=p.parse_args(); args.outdir.mkdir(parents=True,exist_ok=True)
    records=[]; summaries={}
    for A in ISOTOPES:
        rows=load_matrix(A); isotope=[]
        for q in args.q:
            wm,ws,wd,wsd,amp=response(A,q,rows)
            row={"A":A,"q_GeV":q,"W_M00_AFH":wm,"W_SigmaPrime00_AFH":ws,
                 "W_Delta00_AFH_literal":wd,"W_SigmaPrimeDelta00_AFH_literal":wsd,
                 "SigmaPrime_over_M":ws/wm if wm else None}
            records.append(row); isotope.append(row)
        summaries[str(A)]={"density_matrix_entries":len(rows),"J_A":0.5 if A==129 else 1.5,
            "points":isotope}
    with (args.outdir/"afh_spatial_response_selected_q.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    meta={"source":"AFH DMFormFactor v6.0 operator definitions translated to Python",
          "isospin":"tau1=tau2=0 (AFH isoscalar package convention)",
          "responses":"W_M, W_SigmaPrime, W_Delta, W_SigmaPrimeDelta",
          "normalization":"same AFH package normalization as ResponseNuclear[y,i,0,0]; factor four for physical equal-p/n response is not applied here",
          "delta_parity_audit":parity_conflict(),
          "limitations":["No native Wolfram cross-check has yet been run for SigmaPrime.",
          "AFH DeltaJ source wrapper and its internal 3j parity selection are mutually incompatible; literal Delta output is zero and must not be interpreted as a physical prediction.",
          "No finite-Q2 baryon-current Pauli form factors or three-body L_mu_nu W_A^mu_nu contraction are included.",
          "No halo integration is included."],
          "isotopes":summaries}
    (args.outdir/"metadata.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"outdir":str(args.outdir),"delta_parity_audit":meta["delta_parity_audit"],
                      "summary":{A:[{"q_GeV":r["q_GeV"],"W_M":r["W_M00_AFH"],
                                     "W_SigmaPrime":r["W_SigmaPrime00_AFH"],
                                     "ratio":r["SigmaPrime_over_M"]} for r in v["points"]]
                                for A,v in summaries.items()}},indent=2))

if __name__=="__main__": main()
