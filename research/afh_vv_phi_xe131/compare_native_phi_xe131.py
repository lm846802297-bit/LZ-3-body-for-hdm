#!/usr/bin/env python3
"""Pointwise comparison of Python and native AFH Mathematica Xe-131 responses."""
import argparse, csv, hashlib, json
from pathlib import Path
import numpy as np

FIELDS = ('W_M00_AFH','W_PhiPP_AFH','W_MPhiPP_AFH')

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--python-csv',type=Path,required=True)
    p.add_argument('--mathematica-csv',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--rtol',type=float,default=2e-8)
    p.add_argument('--atol',type=float,default=2e-10)
    a=p.parse_args()
    with a.python_csv.open(newline='',encoding='utf-8') as f: py=list(csv.DictReader(f))
    with a.mathematica_csv.open(newline='',encoding='utf-8') as f: ma=list(csv.DictReader(f))
    if len(py)!=len(ma): raise SystemExit(f'row count differs: Python={len(py)}, Mathematica={len(ma)}')
    qpy=np.array([float(r['q_GeV']) for r in py]); qma=np.array([float(r['q_GeV']) for r in ma])
    # The archived Python CSV stores q to eight decimal places. Normalize
    # both coordinate arrays to that storage precision, then require exact
    # node-by-node equality. This permits CSV rounding only; no interpolation
    # or shifted-node comparison is performed.
    qpy_stored=np.round(qpy,8); qma_stored=np.round(qma,8)
    if not np.array_equal(qpy_stored,qma_stored): raise SystemExit('q grids differ after matching the Python CSV precision; interpolation is forbidden')
    q_grid_max_abs_difference=float(np.max(np.abs(qpy-qma)))
    details={}; passed=True
    for field in FIELDS:
        x=np.array([float(r[field]) for r in py]); y=np.array([float(r[field]) for r in ma])
        absd=np.abs(x-y); scale=np.maximum(np.maximum(np.abs(x),np.abs(y)),a.atol)
        rel=absd/scale
        ok=bool(np.all(absd <= a.atol+a.rtol*np.abs(y)))
        passed &= ok
        details[field]={'passed':ok,'max_abs_difference':float(np.max(absd)),
          'max_scaled_difference':float(np.max(rel)),'worst_q_GeV':float(qpy[int(np.argmax(rel))])}
    result={'passed':bool(passed),'points':len(py),'rtol':a.rtol,'atol':a.atol,
      'q_grid_match':'exact node equality after rounding both grids to the Python CSV 8-decimal precision; no interpolation',
      'q_grid_max_abs_difference_GeV':q_grid_max_abs_difference,
      'python_csv_sha256':sha(a.python_csv),'mathematica_csv_sha256':sha(a.mathematica_csv),
      'responses':details,'interpolation':'none; exact q-grid match required'}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes((json.dumps(result,indent=2,sort_keys=True)+'\n').encode('utf-8'))
    print(json.dumps(result,indent=2))
    if not passed: raise SystemExit(1)
if __name__=='__main__': main()
