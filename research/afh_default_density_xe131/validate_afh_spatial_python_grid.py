#!/usr/bin/env python3
"""Internal-consistency validator for provisional Python AFH spatial q grids.

This checks grid identity, finite values, nonnegative diagonal responses, and
response-matrix Cauchy-Schwarz bounds. It is not a native AFH comparison.
"""
from __future__ import annotations
import argparse, csv, json, math
from collections import defaultdict
from pathlib import Path

DIAGONALS=("W_M00_AFH","W_PhiPP00_AFH","W_SigmaPrime00_AFH","W_Delta00_AFH_literal")
ALL_RESPONSES=DIAGONALS+("W_MPhiPP00_AFH","W_SigmaPrimeDelta00_AFH_literal")
CROSS_PAIRS=(
    ("W_M00_AFH","W_PhiPP00_AFH","W_MPhiPP00_AFH","M-PhiPP"),
    ("W_SigmaPrime00_AFH","W_Delta00_AFH_literal","W_SigmaPrimeDelta00_AFH_literal","SigmaPrime-Delta"),
)

def validate_records(rows, *, expected_points=2401, q_min=0.0, q_max=0.6,
                     isotopes=(129,131), atol=2e-12, rtol=1e-9):
    failures=[]
    grouped=defaultdict(list)
    for row in rows:
        try:
            A=int(float(row["A"])); q=float(row["q_GeV"])
        except (KeyError,TypeError,ValueError) as exc:
            failures.append(f"invalid A/q row: {exc}")
            continue
        grouped[A].append((q,row))
    if set(grouped)!=set(isotopes):
        failures.append(f"isotope set {sorted(grouped)} != expected {list(isotopes)}")
    summaries={}
    expected_step=(q_max-q_min)/(expected_points-1)
    for A in isotopes:
        entries=sorted(grouped.get(A,[]),key=lambda item:item[0])
        if len(entries)!=expected_points:
            failures.append(f"Xe-{A}: {len(entries)} rows != {expected_points}")
            continue
        qs=[item[0] for item in entries]
        if len(set(round(q,12) for q in qs))!=expected_points:
            failures.append(f"Xe-{A}: duplicate q_A values")
        for i,q in enumerate(qs):
            expected_q=q_min+i*expected_step
            if abs(q-expected_q)>max(atol,2e-12):
                failures.append(f"Xe-{A}: q-grid mismatch at row {i}: {q:.16g} != {expected_q:.16g}")
                break
        values={name:[] for name in ALL_RESPONSES}
        for q,row in entries:
            numeric={}
            for name in ALL_RESPONSES:
                try: value=float(row[name])
                except (KeyError,TypeError,ValueError) as exc:
                    failures.append(f"Xe-{A} q={q:.10g}: invalid {name}: {exc}")
                    value=math.nan
                if not math.isfinite(value):
                    failures.append(f"Xe-{A} q={q:.10g}: non-finite {name}")
                numeric[name]=value; values[name].append(value)
            for name in DIAGONALS:
                if math.isfinite(numeric[name]) and numeric[name]<-atol:
                    failures.append(f"Xe-{A} q={q:.10g}: negative diagonal {name}")
            for left,right,cross,label in CROSS_PAIRS:
                a,b,c=numeric[left],numeric[right],numeric[cross]
                if all(math.isfinite(v) for v in (a,b,c)):
                    lhs=c*c; rhs=max(0.0,a)*max(0.0,b)
                    tol=max(atol,rtol*max(lhs,rhs,1e-300))
                    if lhs>rhs+tol:
                        failures.append(f"Xe-{A} q={q:.10g}: {label} Cauchy-Schwarz violation (lhs={lhs:.8g}, rhs={rhs:.8g})")
        def minima(column):
            arr=values[column]; found=[]
            for i in range(1,len(arr)-1):
                if arr[i]<arr[i-1] and arr[i]<=arr[i+1]:
                    found.append({"q_GeV":qs[i],"value":arr[i]})
            return found
        max_ratios={}
        for numerator,label in (("W_SigmaPrime00_AFH","SigmaPrime_over_M"),
                                ("W_Delta00_AFH_literal","Delta_over_M")):
            candidates=[]
            for q,row in entries:
                m=float(row["W_M00_AFH"]); n=float(row[numerator])
                if m>0 and math.isfinite(m) and math.isfinite(n): candidates.append((n/m,q))
            max_ratios[label]=({"ratio":max(candidates)[0],"q_GeV":max(candidates)[1]} if candidates else None)
        summaries[str(A)]={
            "rows":len(entries),"q_min_GeV":qs[0],"q_max_GeV":qs[-1],
            "max_response_over_M":max_ratios,
            "sampled_local_minima":{
                "W_M00_AFH":minima("W_M00_AFH"),
                "W_SigmaPrime00_AFH":minima("W_SigmaPrime00_AFH"),
                "W_Delta00_AFH_literal":minima("W_Delta00_AFH_literal")},
            "response_ranges":{name:{"min":min(vals),"max":max(vals)} for name,vals in values.items()},
        }
    return {
        "status":"PASS" if not failures else "FAIL",
        "scope":"Python internal-consistency only; no native AFH comparison",
        "native_afh_validated":False,
        "expected_points_per_isotope":expected_points,
        "expected_total_rows":expected_points*len(isotopes),
        "actual_total_rows":len(rows),
        "q_min_GeV":q_min,"q_max_GeV":q_max,"step_GeV":expected_step,
        "isotopes":summaries,"failures":failures,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--csv",type=Path,required=True)
    parser.add_argument("--out-json",type=Path,required=True)
    parser.add_argument("--expected-points",type=int,default=2401)
    parser.add_argument("--q-min",type=float,default=0.0)
    parser.add_argument("--q-max",type=float,default=0.6)
    args=parser.parse_args()
    with args.csv.open(newline="",encoding="utf-8-sig") as stream: rows=list(csv.DictReader(stream))
    result=validate_records(rows,expected_points=args.expected_points,q_min=args.q_min,q_max=args.q_max)
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    if result["status"]!="PASS": raise SystemExit(1)

if __name__=="__main__": main()
