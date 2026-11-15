#!/usr/bin/env python3
"""Summarize the two fixed-energy NEST event-level pilot CSVs."""
import csv, json, math, statistics, sys
from pathlib import Path

def quantile(xs, q):
    a=sorted(xs)
    if not a: return None
    x=(len(a)-1)*q; lo=math.floor(x); hi=math.ceil(x)
    return a[lo] if lo==hi else a[lo]*(hi-x)+a[hi]*(x-lo)

def summarize(path):
    with path.open(newline="") as f: rows=list(csv.DictReader(f))
    if not rows: raise ValueError(f"empty event sample: {path}")
    fields=("n_photons","n_electrons","s1c_phd","s2c_phd","s1r_phd","s2r_phd")
    data={k:[float(r[k]) for r in rows] for k in fields}
    out={"file":path.name,"n_events":len(rows)}
    for k,x in data.items():
        if not all(math.isfinite(v) for v in x): raise ValueError(f"non-finite {k}")
        out[k]={"mean":statistics.fmean(x),"sd":statistics.stdev(x) if len(x)>1 else 0.,
                "p10":quantile(x,.10),"median":quantile(x,.50),"p90":quantile(x,.90)}
    out["s1c_nonzero_fraction"]=sum(x>0 for x in data["s1c_phd"])/len(rows)
    out["s2c_nonzero_fraction"]=sum(x>0 for x in data["s2c_phd"])/len(rows)
    out["pearson_s1c_s2c"]=(
        statistics.correlation(data["s1c_phd"],data["s2c_phd"])
        if len(rows)>1 and statistics.pstdev(data["s1c_phd"])>0 and statistics.pstdev(data["s2c_phd"])>0 else None)
    return out

if __name__=="__main__":
    result={"study":"LZ 2026 NR event-level candidate pilot",
            "interpretation":"Fixed 248 keV, central reference drift-time, LZ WS2024 detector class; compare NR width vectors only. Not official LZ likelihood or full spatial-response reproduction.",
            "samples":[summarize(Path(p)) for p in sys.argv[1:]]}
    print(json.dumps(result,indent=2))
