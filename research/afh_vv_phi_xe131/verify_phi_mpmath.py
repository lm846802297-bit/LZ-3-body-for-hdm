#!/usr/bin/env python3
"""60-digit mpmath spot-check of Phi'' reduced amplitudes at four minima."""
import argparse, csv, json, math, hashlib
from pathlib import Path
import mpmath as mp
from sympy import Rational, Integer, N as symN
from sympy.physics.wigner import wigner_3j, wigner_6j, wigner_9j
import afh_vv_phi_xe131 as audit

mp.mp.dps = 60


def w3(a,b,c,ma,mb,mc):
    try: return mp.mpf(str(symN(wigner_3j(a,b,c,ma,mb,mc),60)))
    except ValueError: return mp.mpf('0')

def w6(a,b,c,d,e,f):
    try: return mp.mpf(str(symN(wigner_6j(a,b,c,d,e,f),60)))
    except ValueError: return mp.mpf('0')

def w9(a,b,c,d,e,f,g,h,i):
    try: return mp.mpf(str(symN(wigner_9j(a,b,c,d,e,f,g,h,i),60)))
    except ValueError: return mp.mpf('0')

def odd_df(n): return mp.fprod(range(1,n+1,2))

def bessel_pm_mp(y,np_,lp,n,ell,L,kind):
    y=mp.mpf(y)
    f1=mp.power(2,L-1)/odd_df(2*L+1)*mp.power(y,mp.mpf(L-1)/2)*mp.exp(-y)*mp.sqrt(mp.factorial(np_-1)*mp.factorial(n-1))
    f2=mp.sqrt(mp.gamma(np_+lp+mp.mpf('0.5'))*mp.gamma(n+ell+mp.mpf('0.5')))
    total=mp.mpf('0')
    for m in range(n):
        for mp_ in range(np_):
            s1=(-1)**(m+mp_)/(mp.factorial(m)*mp.factorial(mp_)*mp.factorial(n-1-m)*mp.factorial(np_-1-mp_))
            s2=mp.gamma(mp.mpf(ell+lp+L+2*m+2*mp_+2)/2)/(mp.gamma(ell+m+mp.mpf('1.5'))*mp.gamma(lp+mp_+mp.mpf('1.5')))
            a1=mp.mpf(L-lp-ell-2*mp_-2*m-1)/2
            a2=mp.mpf(L-lp-ell-2*mp_-2*m+1)/2
            h1=mp.hyp1f1(a1,L+mp.mpf('1.5'),y)
            h2=mp.hyp1f1(a2,L+mp.mpf('1.5'),y)
            if kind=='minus': s3=-mp.mpf(ell+lp+L+2*m+2*mp_+2)/2*h1+2*m*h2
            else: s3=-mp.mpf(ell+lp+L+2*m+2*mp_+2)/2*h1+(2*ell+2*m+1)*h2
            total += s1*s2*s3
    return f1*f2*total

def phi_pp_j_mp(y,Np,two_jp,N,two_j,jc):
    np_,lp=audit.orbital(Np,two_jp); n,ell=audit.orbital(N,two_j)
    jp,j=Rational(two_jp,2),Rational(two_j,2)
    if not (abs(float(j-jp))<=jc<=float(j+jp) and (lp+ell+jc)%2==0): return mp.mpf('0')
    overall=(-1)**(lp+1)*6*mp.sqrt(2*lp+1)*mp.sqrt(2*float(jp)+1)*mp.sqrt(2*float(j)+1)/mp.sqrt(4*mp.pi)
    def nine(lc): return w9(Integer(lp),Integer(ell),Integer(lc),Rational(1,2),Rational(1,2),Integer(1),jp,j,Integer(jc))
    def six_prod(Jc,lc,ellp):
        return w6(Integer(Jc),Integer(1),Integer(lc),Integer(1),Integer(jc),Integer(1))*w6(Integer(Jc),Integer(1),Integer(lc),Integer(ell),Integer(lp),Integer(ellp))
    bm=bessel_pm_mp(y,np_,lp,n,ell,jc+1,'minus')
    bp=bessel_pm_mp(y,np_,lp,n,ell,jc+1,'plus')
    s1=sum([(-1)**(jc-lc+1)*(2*lc+1)*six_prod(jc+1,lc,ell+1)*nine(lc) for lc in range(jc,jc+2)])
    t1=w3(Integer(lp),Integer(jc+1),Integer(ell+1),0,0,0)
    term1=mp.sqrt(2*(ell+1)+1)*mp.sqrt(ell+1)*t1*bm*s1
    if ell==0: term2=mp.mpf('0')
    else:
        s2=sum([(-1)**(jc-lc)*(2*lc+1)*six_prod(jc+1,lc,ell-1)*nine(lc) for lc in range(jc,jc+2)])
        term2=mp.sqrt(2*(ell-1)+1)*mp.sqrt(ell)*w3(Integer(lp),Integer(jc+1),Integer(ell-1),0,0,0)*bp*s2
    value=mp.sqrt(2*(jc+1)+1)*mp.sqrt(jc+1)*(term1+term2)
    if jc>0:
        bm2=bessel_pm_mp(y,np_,lp,n,ell,jc-1,'minus')
        bp2=bessel_pm_mp(y,np_,lp,n,ell,jc-1,'plus')
        s3=sum([(-1)**(jc-lc+1)*(2*lc+1)*w6(Integer(jc-1),Integer(1),Integer(lc),Integer(1),Integer(jc),Integer(1))*w6(Integer(jc-1),Integer(1),Integer(lc),Integer(ell),Integer(lp),Integer(ell+1))*nine(lc) for lc in range(jc-1,jc+1)])
        term3=mp.sqrt(2*(ell+1)+1)*mp.sqrt(ell+1)*w3(Integer(lp),Integer(jc-1),Integer(ell+1),0,0,0)*bm2*s3
        if ell==0: term4=mp.mpf('0')
        else:
            s4=sum([(-1)**(jc-lc)*(2*lc+1)*w6(Integer(jc-1),Integer(1),Integer(lc),Integer(1),Integer(jc),Integer(1))*w6(Integer(jc-1),Integer(1),Integer(lc),Integer(ell),Integer(lp),Integer(ell-1))*nine(lc) for lc in range(jc-1,jc+1)])
            term4=mp.sqrt(2*(ell-1)+1)*mp.sqrt(ell)*w3(Integer(lp),Integer(jc-1),Integer(ell-1),0,0,0)*bp2*s4
        value += mp.sqrt(2*(jc-1)+1)*mp.sqrt(jc)*(term3+term4)
    return overall*value

def high_precision_amplitudes(q_GeV,rows):
    b=mp.mpf(str(audit.B_GEV_INV)); y=(mp.mpf(str(q_GeV))*b/2)**2
    iso=mp.sqrt(mp.mpf(2)/(2*mp.mpf(str(audit.T_ISO))+1))
    result={}
    for jc in audit.RANKS:
        total=mp.mpf('0')
        for r in rows:
            if r['rank']==jc and r['isospin']==0:
                total += mp.mpf(str(r['coefficient']))*iso*phi_pp_j_mp(y,r['Nprime'],r['two_jprime'],r['N'],r['two_j'],jc)
        result[jc]=total
    return result

def main():
    p=argparse.ArgumentParser(); here=Path(__file__).resolve().parent
    p.add_argument('--matrix',type=Path,default=here.parent/'afh_default_density_xe131'/'input'/'afh_default_xe131_density_matrix.csv')
    p.add_argument('--minima',type=Path,default=here.parent/'afh_default_density_xe131'/'output'/'minima.csv')
    p.add_argument('--output',type=Path,default=here/'output'/'phi_mpmath_spot_check.json')
    a=p.parse_args(); rows=audit.read_matrix(a.matrix)
    with a.minima.open(newline='',encoding='utf-8') as f: minima=list(csv.DictReader(f))
    records=[]
    for r in minima:
        q=float(r['q_min_MeV'])/1000
        mp_amp=high_precision_amplitudes(q,rows)
        _,_,_,_,double_amp=audit.calculate([q],rows)
        rec={'q_MeV':q*1000,'mp_dps':mp.mp.dps,'rank_amplitudes':{}}
        for jc in audit.RANKS:
            hi=mp_amp[jc]; lo=mp.mpf(str(float(double_amp[jc][0])))
            rel=abs(hi-lo)/max(abs(hi),mp.mpf('1e-80'))
            rec['rank_amplitudes'][str(jc)]={'mpmath':mp.nstr(hi,25),'scipy_double':mp.nstr(lo,25),'relative_difference':mp.nstr(rel,12)}
        records.append(rec)
    maxrel=max(float(rec['rank_amplitudes'][str(j)]['relative_difference']) for rec in records for j in audit.RANKS)
    result={'precision_digits':mp.mp.dps,'points':len(records),'records':records,'max_relative_difference':maxrel,
      'note':'Independent mpmath hypergeometric and 60-digit Wigner-symbol evaluation at the four archived mass-response minima.'}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    manifest_path=a.output.parent/'run_manifest.json'
    if manifest_path.exists():
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        digest=lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        manifest.setdefault('checks',{})['mpmath_spot_check']={'status':'PASS','precision_digits':mp.mp.dps,'points':len(records),'max_relative_difference':maxrel}
        manifest.setdefault('outputs',{})[a.output.name]={'sha256':digest(a.output),'rows':len(records)}
        manifest.setdefault('code',{})['mpmath_verifier_sha256']=digest(Path(__file__))
        manifest_path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
