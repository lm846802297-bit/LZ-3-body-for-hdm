#!/usr/bin/env python3
"""Compare B-baseline isotope and natural-xenon outputs across halo quadratures."""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path


def rows(path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))


def f(row,key):
    x=float(row[key])
    if not math.isfinite(x):
        raise ValueError(f"non-finite {key}: {x}")
    return x


def shift(high,base):
    if base==0.0:
        return 0.0 if high==0.0 else None
    return (high/base-1.0)*100.0


def compare(base_dir:Path,high_dir:Path,out_dir:Path):
    base_nat=rows(base_dir/"natural_xenon_B_baseline.csv")
    high_nat=rows(high_dir/"natural_xenon_B_baseline.csv")
    high_by_E={f(r,"ER_keV"):r for r in high_nat}
    if set(f(r,"ER_keV") for r in base_nat)!=set(high_by_E):
        raise ValueError("natural-xenon recoil grids do not match")
    nat_out=[]
    sf,si,se=[],[],[]
    for b in base_nat:
        E=f(b,"ER_keV"); h=high_by_E[E]
        df=shift(f(h,"natural_xenon_full_B_relative_rate"),f(b,"natural_xenon_full_B_relative_rate"))
        di=shift(f(h,"natural_xenon_I_D_B_relative_rate"),f(b,"natural_xenon_I_D_B_relative_rate"))
        eb=f(b,"full_vs_I_D_error_B_pct"); eh=f(h,"full_vs_I_D_error_B_pct")
        de=float(eh)-float(eb) if eb!="" and eh!="" else ""
        if df is not None: sf.append(abs(df))
        if di is not None: si.append(abs(di))
        if de!="": se.append(abs(de))
        nat_out.append({
            "ER_keV":E,
            "full_B_base":f(b,"natural_xenon_full_B_relative_rate"),
            "full_B_high":f(h,"natural_xenon_full_B_relative_rate"),
            "full_B_quadrature_shift_pct":"" if df is None else df,
            "I_D_B_base":f(b,"natural_xenon_I_D_B_relative_rate"),
            "I_D_B_high":f(h,"natural_xenon_I_D_B_relative_rate"),
            "I_D_B_quadrature_shift_pct":"" if di is None else di,
            "full_vs_I_D_error_B_base_pct":eb,
            "full_vs_I_D_error_B_high_pct":eh,
            "approximation_error_shift_pp":de,
        })
    base_iso=rows(base_dir/"seven_isotope_B_baseline.csv")
    high_iso=rows(high_dir/"seven_isotope_B_baseline.csv")
    key=lambda r:(f(r,"ER_keV"),int(r["A"]))
    bmap={key(r):r for r in base_iso}; hmap={key(r):r for r in high_iso}
    if bmap.keys()!=hmap.keys():
        raise ValueError("isotope recoil grids do not match")
    iso_out=[]
    for k in sorted(bmap):
        b,h=bmap[k],hmap[k]
        full_shift=shift(f(h,"full_contribution_B_relative_units"),f(b,"full_contribution_B_relative_units"))
        id_shift=shift(f(h,"I_D_contribution_B_relative_units"),f(b,"I_D_contribution_B_relative_units"))
        iso_out.append({
            "ER_keV":k[0],"A":k[1],
            "full_B_quadrature_shift_pct":"" if full_shift is None else full_shift,
            "I_D_B_quadrature_shift_pct":"" if id_shift is None else id_shift,
            "full_vs_I_D_error_B_base_pct":b["isotope_relative_error_B_pct"],
            "full_vs_I_D_error_B_high_pct":h["isotope_relative_error_B_pct"],
        })
    out_dir.mkdir(parents=True,exist_ok=True)
    for name,data in (("natural_xenon_B_quadrature_comparison.csv",nat_out),
                      ("seven_isotope_B_quadrature_comparison.csv",iso_out)):
        with (out_dir/name).open("w",newline="",encoding="utf-8") as fobj:
            w=csv.DictWriter(fobj,fieldnames=list(data[0]),lineterminator="\n")
            w.writeheader();w.writerows(data)
    summary={
        "natural_xenon":{
            "points":len(nat_out),
            "max_abs_full_B_rate_shift_pct":max(sf,default=0.0),
            "max_abs_I_D_B_rate_shift_pct":max(si,default=0.0),
            "max_abs_approximation_error_shift_pp":max(se,default=0.0),
        },
        "seven_isotopes":{"points":len(iso_out)},
    }
    (out_dir/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline-dir",type=Path,required=True)
    p.add_argument("--highorder-dir",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(compare(a.baseline_dir,a.highorder_dir,a.out_dir),indent=2))


if __name__=="__main__":
    main()
