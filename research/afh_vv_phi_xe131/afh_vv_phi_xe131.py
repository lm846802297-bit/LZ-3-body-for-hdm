#!/usr/bin/env python3
"""AFH v6.0 Xe-131 W_M, Phi'' and M-Phi'' response audit.

The one-body matrix elements follow the definitions in the archived
DMFormFactor v6.0 source. This program computes nuclear responses only; it
must not be interpreted as a three-body cross-section correction.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, platform
from pathlib import Path
import sys
import numpy as np
import scipy
from scipy.special import factorial2, hyp1f1
import sympy
from sympy import Rational, Integer, pi, sqrt, N as symN
from sympy.physics.wigner import wigner_3j, wigner_6j, wigner_9j

MASS_SCHEME_DIR = Path(__file__).resolve().parent.parent / 'three_body_calculation_and_validation'
sys.path.insert(0, str(MASS_SCHEME_DIR))
from isotope_mass_schemes import isotope_mass_GeV

A, Z, J_A, T_ISO = 131, 54, 1.5, 11.5
B_FM = math.sqrt(41.467 / (45*A**(-1/3) - 25*A**(-2/3)))
B_GEV_INV = B_FM * 5.0677
M_A_GEV = isotope_mass_GeV(A, 'ame2020_nuclear')
RANKS = (0, 2)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def read_matrix(path: Path) -> list[dict]:
    with path.open(newline='', encoding='utf-8') as f:
        rows = [{k: (float(v) if k == 'coefficient' else int(v))
                 for k, v in row.items()} for row in csv.DictReader(f)]
    if len(rows) != 67:
        raise ValueError(f'Expected 67 AFH Xe-131 density-matrix rows, got {len(rows)}')
    return rows


def qnorm(j): return math.sqrt(2*j + 1)
def jnorm(j): return 2*j + 1


def orbital(N, two_j):
    jph = (two_j + 1)//2
    ell = jph if (N-jph) % 2 == 0 else jph-1
    n = (N-ell)//2 + 1
    if n < 1: raise ValueError('Invalid AFH oscillator orbital')
    return n, ell


def _wigner(fn, *args):
    try: return float(symN(fn(*args), 30))
    except ValueError: return 0.0


def bessel_array(y, np_, lp, n, ell, L):
    y = np.asarray(y, dtype=float)
    f1 = (2.0**L)/float(factorial2(2*L+1))*np.power(y, L/2)*np.exp(-y)*math.sqrt(math.factorial(np_-1)*math.factorial(n-1))
    f2 = math.sqrt(math.gamma(np_+lp+0.5)*math.gamma(n+ell+0.5))
    total = np.zeros_like(y)
    for m in range(n):
        for mp in range(np_):
            s1 = (-1.0)**(m+mp)/(math.factorial(m)*math.factorial(mp)*math.factorial(n-1-m)*math.factorial(np_-1-mp))
            s2 = math.gamma((ell+lp+L+2*m+2*mp+3)/2)/(math.gamma(ell+m+1.5)*math.gamma(lp+mp+1.5))
            a = (L-lp-ell-2*mp-2*m)/2
            total += s1*s2*hyp1f1(a, L+1.5, y)
    return f1*f2*total


def bessel_pm_array(y, np_, lp, n, ell, L, kind):
    y = np.asarray(y, dtype=float)
    f1 = (2.0**(L-1))/float(factorial2(2*L+1))*np.power(y, (L-1)/2)*np.exp(-y)*math.sqrt(math.factorial(np_-1)*math.factorial(n-1))
    f2 = math.sqrt(math.gamma(np_+lp+0.5)*math.gamma(n+ell+0.5))
    total = np.zeros_like(y)
    for m in range(n):
        for mp in range(np_):
            s1 = (-1.0)**(m+mp)/(math.factorial(m)*math.factorial(mp)*math.factorial(n-1-m)*math.factorial(np_-1-mp))
            s2 = math.gamma((ell+lp+L+2*m+2*mp+2)/2)/(math.gamma(ell+m+1.5)*math.gamma(lp+mp+1.5))
            a1 = (L-lp-ell-2*mp-2*m-1)/2
            a2 = (L-lp-ell-2*mp-2*m+1)/2
            h1, h2 = hyp1f1(a1, L+1.5, y), hyp1f1(a2, L+1.5, y)
            if kind == 'minus':
                s3 = -(ell+lp+L+2*m+2*mp+2)/2*h1 + 2*m*h2
            elif kind == 'plus':
                s3 = -(ell+lp+L+2*m+2*mp+2)/2*h1 + (2*ell+2*m+1)*h2
            else: raise ValueError(kind)
            total += s1*s2*s3
    return f1*f2*total


def build_m_terms(rows):
    terms = {j: [] for j in RANKS}
    iso = math.sqrt(2/(2*T_ISO+1))
    for r in rows:
        jc = r['rank']
        if r['isospin'] != 0 or jc not in RANKS: continue
        np_, lp = orbital(r['Nprime'], r['two_jprime'])
        n, ell = orbital(r['N'], r['two_j'])
        jp, j, J = Rational(r['two_jprime'],2), Rational(r['two_j'],2), Integer(jc)
        if not (abs(float(j-jp)) <= jc <= float(j+jp) and (lp+ell+jc)%2 == 0): continue
        phase = (-1)**(Rational(1,2)+j+J)
        pref = sqrt((2*j+1)*(2*jp+1)*(2*ell+1)*(2*lp+1)*(2*J+1)/(4*pi))
        val = phase*pref*wigner_3j(Integer(lp),J,Integer(ell),0,0,0)*wigner_6j(Integer(lp),jp,Rational(1,2),j,Integer(ell),J)
        ang = float(symN(val,30))
        terms[jc].append((r['coefficient']*iso*ang,np_,lp,n,ell))
    return terms


def build_phi_terms(rows):
    """Precompute the q-independent Wigner/recoupling factors in AFH PhiPPJ."""
    terms = {j: [] for j in RANKS}
    iso = math.sqrt(2/(2*T_ISO+1))
    for r in rows:
        jc = r['rank']
        if r['isospin'] != 0 or jc not in RANKS: continue
        np_, lp = orbital(r['Nprime'], r['two_jprime'])
        n, ell = orbital(r['N'], r['two_j'])
        jp, j = Rational(r['two_jprime'],2), Rational(r['two_j'],2)
        if not (abs(float(j-jp)) <= jc <= float(j+jp) and (lp+ell+jc)%2 == 0): continue
        overall = (-1.0)**(lp+1)*6*qnorm(lp)*qnorm(float(jp))*qnorm(float(j))/math.sqrt(4*math.pi)
        def nine(lc):
            return _wigner(wigner_9j, Integer(lp),Integer(ell),Integer(lc),Rational(1,2),Rational(1,2),Integer(1),jp,j,Integer(jc))
        def six_prod(Jc,lc,ellp):
            return (_wigner(wigner_6j,Integer(Jc),Integer(1),Integer(lc),Integer(1),Integer(jc),Integer(1))
                    *_wigner(wigner_6j,Integer(Jc),Integer(1),Integer(lc),Integer(ell),Integer(lp),Integer(ellp)))
        c1 = sum((-1.0)**(jc-lc+1)*jnorm(lc)*six_prod(jc+1,lc,ell+1)*nine(lc) for lc in range(jc,jc+2))
        c1 *= qnorm(ell+1)*math.sqrt(ell+1)*_wigner(wigner_3j,Integer(lp),Integer(jc+1),Integer(ell+1),0,0,0)
        if ell == 0: c2 = 0.0
        else:
            c2 = sum((-1.0)**(jc-lc)*jnorm(lc)*six_prod(jc+1,lc,ell-1)*nine(lc) for lc in range(jc,jc+2))
            c2 *= qnorm(ell-1)*math.sqrt(ell)*_wigner(wigner_3j,Integer(lp),Integer(jc+1),Integer(ell-1),0,0,0)
        if jc > 0:
            c3 = sum((-1.0)**(jc-lc+1)*jnorm(lc)*_wigner(wigner_6j,Integer(jc-1),Integer(1),Integer(lc),Integer(1),Integer(jc),Integer(1))*_wigner(wigner_6j,Integer(jc-1),Integer(1),Integer(lc),Integer(ell),Integer(lp),Integer(ell+1))*nine(lc) for lc in range(jc-1,jc+1))
            c3 *= qnorm(ell+1)*math.sqrt(ell+1)*_wigner(wigner_3j,Integer(lp),Integer(jc-1),Integer(ell+1),0,0,0)
            if ell == 0: c4 = 0.0
            else:
                c4 = sum((-1.0)**(jc-lc)*jnorm(lc)*_wigner(wigner_6j,Integer(jc-1),Integer(1),Integer(lc),Integer(1),Integer(jc),Integer(1))*_wigner(wigner_6j,Integer(jc-1),Integer(1),Integer(lc),Integer(ell),Integer(lp),Integer(ell-1))*nine(lc) for lc in range(jc-1,jc+1))
                c4 *= qnorm(ell-1)*math.sqrt(ell)*_wigner(wigner_3j,Integer(lp),Integer(jc-1),Integer(ell-1),0,0,0)
        else: c3 = c4 = 0.0
        terms[jc].append((r['coefficient']*iso*overall,np_,lp,n,ell,jc,c1,c2,c3,c4))
    return terms


def amplitudes(q, m_terms, phi_terms):
    y = (np.asarray(q)*B_GEV_INV/2)**2
    m_amp, phi_amp = {}, {}
    for jc in RANKS:
        am = np.zeros_like(y); ap = np.zeros_like(y)
        for weight,np_,lp,n,ell in m_terms[jc]:
            am += weight*bessel_array(y,np_,lp,n,ell,jc)
        for weight,np_,lp,n,ell,jc0,c1,c2,c3,c4 in phi_terms[jc]:
            val = qnorm(jc+1)*math.sqrt(jc+1)*(c1*bessel_pm_array(y,np_,lp,n,ell,jc+1,'minus') + c2*bessel_pm_array(y,np_,lp,n,ell,jc+1,'plus'))
            if jc > 0:
                val += qnorm(jc-1)*math.sqrt(jc)*(c3*bessel_pm_array(y,np_,lp,n,ell,jc-1,'minus') + c4*bessel_pm_array(y,np_,lp,n,ell,jc-1,'plus'))
            ap += weight*val
        m_amp[jc], phi_amp[jc] = am, ap
    return m_amp, phi_amp


def calculate(q, rows):
    m_terms, phi_terms = build_m_terms(rows), build_phi_terms(rows)
    m_amp, phi_amp = amplitudes(q,m_terms,phi_terms)
    wm = 0.25*sum(m_amp[j]**2 for j in RANKS)
    wp = 0.25*sum(phi_amp[j]**2 for j in RANKS)
    wmp = 0.25*sum(m_amp[j]*phi_amp[j] for j in RANKS)
    return wm, wp, wmp, m_amp, phi_amp


def load_minima(path):
    with path.open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rows)


def run(outdir: Path, matrix_path: Path, minima_path: Path, baseline_path: Path|None, dq: float):
    rows=read_matrix(matrix_path)
    q=np.arange(round(0.6/dq)+1,dtype=float)*dq
    wm,wp,wmp,ma,pa=calculate(q,rows)
    cs=np.divide(np.abs(wmp),np.sqrt(wm*wp),out=np.zeros_like(wm),where=(wm*wp)>0)
    if np.max(cs)>1+1e-9: raise RuntimeError(f'Cauchy-Schwarz violation: {np.max(cs)}')
    baseline_check={'status':'not supplied'}
    if baseline_path and baseline_path.exists():
        with baseline_path.open(newline='',encoding='utf-8') as f: base=list(csv.DictReader(f))
        if len(base)!=len(q): raise RuntimeError('Baseline W_M row count mismatch')
        oldq=np.array([float(r['q_GeV']) for r in base])
        oldwm=np.array([float(r['W_M00_AFH_package']) for r in base])
        if not np.array_equal(oldq,q): raise RuntimeError('Baseline q grid differs; interpolation is forbidden')
        rel=np.max(np.abs(wm-oldwm)/np.maximum(np.abs(oldwm),1e-300))
        baseline_check={'status':'PASS' if rel<=2e-12 else 'FAIL','max_relative_difference':float(rel),'points':len(q)}
        if rel>2e-12: raise RuntimeError(f'W_M baseline mismatch {rel:.3e}')
    # Equal physical proton/neutron couplings: multiply the AFH isoscalar
    # response by four, then by 4 pi/(2J+1). No M-only q=0 correction is
    # silently applied to Phi'' or the interference response.
    physical_factor=4*4*math.pi/(2*J_A+1)
    wm0=float(wm[0])
    full=[]
    for i,qi in enumerate(q):
        er=(math.sqrt(M_A_GEV**2+qi**2)-M_A_GEV)*1e6
        full.append({'q_GeV':f'{qi:.8f}','ER_keV':f'{er:.10f}',
          'W_M00_AFH':f'{wm[i]:.16e}','W_PhiPP_AFH':f'{wp[i]:.16e}','W_MPhiPP_AFH':f'{wmp[i]:.16e}',
          'R_M_raw_over_A2':f'{physical_factor*wm[i]/A**2:.16e}',
          'R_PhiPP_raw_over_A2':f'{physical_factor*wp[i]/A**2:.16e}',
          'R_MPhiPP_raw_over_A2':f'{physical_factor*wmp[i]/A**2:.16e}',
          'R_M_shape_normalized_over_A2':f'{wm[i]/wm0:.16e}',
          'R_PhiPP_shape_normalized_over_A2':f'{wp[i]/wm0:.16e}',
          'R_MPhiPP_shape_normalized_over_A2':f'{wmp[i]/wm0:.16e}',
          'W_PhiPP_over_W_M':f'{wp[i]/wm[i]:.16e}' if wm[i] else '',
          'W_MPhiPP_over_W_M':f'{wmp[i]/wm[i]:.16e}' if wm[i] else '',
          'interference_correlation':f'{cs[i]:.16e}'})
    outdir.mkdir(parents=True,exist_ok=True)
    full_path=outdir/'afh_vv_phi_xe131_full_grid.csv'
    fields=list(full[0]); write_csv(full_path,fields,full)
    selected=[]
    for r in load_minima(minima_path):
        qi=float(r['q_min_MeV'])/1000
        swm,swp,swmp,sma,spa=calculate(np.array([qi]),rows)
        x,y,z=float(swm[0]),float(swp[0]),float(swmp[0])
        corr=abs(z)/math.sqrt(x*y)
        er_min=(math.sqrt(M_A_GEV**2+qi**2)-M_A_GEV)*1e6
        selected.append({'q_min_MeV':f'{qi*1000:.9f}','ER_min_keV':f'{er_min:.10f}',
          'W_M00_AFH':f'{x:.16e}','W_PhiPP_AFH':f'{y:.16e}','W_MPhiPP_AFH':f'{z:.16e}',
          'R_M_raw_over_A2':f'{physical_factor*x/A**2:.16e}',
          'R_PhiPP_raw_over_A2':f'{physical_factor*y/A**2:.16e}',
          'R_MPhiPP_raw_over_A2':f'{physical_factor*z/A**2:.16e}',
          'R_M_shape_normalized_over_A2':f'{x/wm0:.16e}',
          'R_PhiPP_shape_normalized_over_A2':f'{y/wm0:.16e}',
          'R_MPhiPP_shape_normalized_over_A2':f'{z/wm0:.16e}',
          'W_PhiPP_over_W_M':f'{y/x:.16e}','W_MPhiPP_over_W_M':f'{z/x:.16e}',
          'interference_correlation':f'{corr:.16e}',
          'M_rank0_amplitude':f'{float(sma[0][0]):.16e}','M_rank2_amplitude':f'{float(sma[2][0]):.16e}',
          'Phi_rank0_amplitude':f'{float(spa[0][0]):.16e}','Phi_rank2_amplitude':f'{float(spa[2][0]):.16e}'})
    sel_path=outdir/'afh_vv_phi_xe131_selected_points.csv'
    write_csv(sel_path,list(selected[0]),selected)
    native_dir=outdir/'native_mathematica'
    native_csv=native_dir/'afh_vv_phi_xe131_native.csv'
    native_comparison_path=native_dir/'comparison.json'
    native_check='PENDING'
    if native_csv.exists() and native_comparison_path.exists():
        native_comparison=json.loads(native_comparison_path.read_text(encoding='utf-8'))
        if (native_comparison.get('passed') is True
                and native_comparison.get('python_csv_sha256') == sha256(full_path)
                and native_comparison.get('mathematica_csv_sha256') == sha256(native_csv)):
            native_check={'status':'PASS','points':native_comparison.get('points'),
                'comparison_sha256':sha256(native_comparison_path),
                'max_abs_q_grid_difference_GeV':native_comparison.get('q_grid_max_abs_difference_GeV')}
        else:
            native_check={'status':'STALE_OR_FAILED','comparison_sha256':sha256(native_comparison_path)}
    meta={'status':'Python_AFH_v6_translation_reproducible_native_Mathematica_crosscheck_' + (native_check['status'] if isinstance(native_check,dict) else 'PENDING'),
      'source_commit':__import__('os').environ.get('GITHUB_SHA','not_recorded_local_run'),
      'isotope':{'A':A,'Z':Z,'J_A':J_A,'T_iso':T_ISO},
      'input':{'density_matrix':str(matrix_path),'density_matrix_sha256':sha256(matrix_path),'minima_csv_sha256':sha256(minima_path),'entries':len(rows),
        'AFH_source':'v6/dmformfactor-V6.m','AFH_source_sha256_expected':'dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372'},
      'oscillator':{'b_A_fm':B_FM,'b_A_GeV_inverse':B_GEV_INV,'fm_to_GeV_inverse':5.0677},
      'grid':{'q_min_GeV':0.0,'q_max_GeV':0.6,'dq_GeV':dq,'points':len(q),'m_A_GeV':M_A_GEV,'mass_scheme':'AME2020 nuclear mass with CODATA-2022 constants'},
      'AFH_mapping':{'ResponseNuclear_index_1':'W_M','ResponseNuclear_index_4':'W_PhiPP = W_Phi double-prime','ResponseNuclear_index_7':'W_MPhiPP interference','isospin_components':[0,0]},
      'physical_normalization':{'equal_pn_factor':4,'factor_4pi_over_2Jplus1':4*math.pi/(2*J_A+1),'combined_factor':physical_factor,
        'note':'Raw physical response is reported. The separate 1.00008253 mass-response q=0 shape correction is not imposed on Phi or M-Phi.'},
      'checks':{'W_M_against_existing_AFH_grid':baseline_check,'Cauchy_Schwarz_max':float(np.max(cs)),
        'Cauchy_Schwarz_max_q_GeV':float(q[int(np.argmax(cs))]),'native_Mathematica_Phi_crosscheck':native_check},
      'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'sympy':sympy.__version__},
      'code':{'path':str(Path(__file__).name),'sha256':sha256(Path(__file__))},
      'outputs':{full_path.name:{'sha256':sha256(full_path),'rows':len(full)},sel_path.name:{'sha256':sha256(sel_path),'rows':len(selected)}},
      'interpretation_boundary':'Nuclear response functions only. The three-body WIMP coefficients multiplying these responses have not yet been derived.'}
    if native_csv.exists() and native_comparison_path.exists():
        meta['outputs'][str(native_csv.relative_to(outdir)).replace('\\','/')]={'sha256':sha256(native_csv),'rows':2401}
        meta['outputs'][str(native_comparison_path.relative_to(outdir)).replace('\\','/')]={'sha256':sha256(native_comparison_path),'rows':1}
        native_metadata= native_dir/'native_metadata.txt'
        if native_metadata.exists():
            meta['outputs'][str(native_metadata.relative_to(outdir)).replace('\\','/')]={'sha256':sha256(native_metadata)}
    meta_path=outdir/'run_manifest.json'
    meta_path.write_bytes((json.dumps(meta,indent=2,sort_keys=True)+'\n').encode('utf-8'))
    return meta


def main():
    p=argparse.ArgumentParser()
    here=Path(__file__).resolve().parent
    p.add_argument('--matrix',type=Path,default=here.parent/'afh_default_density_xe131'/'input'/'afh_default_xe131_density_matrix.csv')
    p.add_argument('--minima',type=Path,default=here.parent/'afh_default_density_xe131'/'output'/'minima.csv')
    p.add_argument('--baseline',type=Path,default=here.parent/'afh_default_density_xe131'/'output'/'afh_default_xe131_WM00.csv')
    p.add_argument('--outdir',type=Path,default=here/'output')
    p.add_argument('--dq',type=float,default=0.00025)
    a=p.parse_args()
    meta=run(a.outdir,a.matrix,a.minima,a.baseline,a.dq)
    print(json.dumps(meta['checks'],indent=2))

if __name__=='__main__': main()
