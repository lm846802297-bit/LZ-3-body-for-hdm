#!/usr/bin/env python3
"""Bin flat-spectrum NR events in S1c and summarize log10(S2c) band quantiles."""
import csv, json, math, statistics, sys
from collections import defaultdict
from pathlib import Path

OBS_S1=540.07916
OBS_S2=9267.53
BIN_WIDTH=5.0

def summarize(path):
    bins=defaultdict(list)
    energies=[]
    n=0
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            s1=float(r["s1c_phd"]); log_s2=float(r["log10_s2c_phd"])
            energies.append(float(r["energy_keV"]))
            n+=1
            if not math.isfinite(s1) or not math.isfinite(log_s2) or log_s2 < 0:
                continue
            lo=math.floor(s1/BIN_WIDTH)*BIN_WIDTH
            bins[lo].append(log_s2)
    out=[]
    for lo, vals in sorted(bins.items()):
        if len(vals)<100: continue
        x=sorted(vals)
        def q(p):
            k=(len(x)-1)*p; a=math.floor(k); b=math.ceil(k)
            return x[a] if a==b else x[a]*(b-k)+x[b]*(k-a)
        out.append({"s1c_low":lo,"s1c_high":lo+BIN_WIDTH,"n":len(x),
                    "log10_s2c_p10":q(.10),"log10_s2c_median":q(.50),
                    "log10_s2c_p90":q(.90)})
    cand_lo=math.floor(OBS_S1/BIN_WIDTH)*BIN_WIDTH
    cand=next((b for b in out if b["s1c_low"]==cand_lo),None)
    cand_log=math.log10(OBS_S2)
    if cand:
        cand["observed_candidate_log10_s2c"]=cand_log
        cand["candidate_minus_band_median"]=cand_log-cand["log10_s2c_median"]
        cand["candidate_position_within_p10_p90"]=(cand_log-cand["log10_s2c_p10"])/(cand["log10_s2c_p90"]-cand["log10_s2c_p10"])
    return {"file":path.name,"n_generated":n,"energy_min_keV":min(energies),"energy_max_keV":max(energies),"bin_width_phd":BIN_WIDTH,
            "candidate_bin":cand,"bands":out}

if __name__=="__main__":
    result={"study":"LZ 2026 flat-energy NR band pilot",
      "energy_spectrum":"Uniform in true recoil energy; the actual sampled range is recorded separately for each input sample.",
      "position":"Fixed approximate candidate position r=45.9 cm, z=26.4 cm above cathode from LZ Fig. 3; no fiducial spatial averaging",
      "definition":"For each S1c bin, report 10th, 50th, and 90th percentiles of log10(S2c), following the flat-in-energy band construction described for LZ Fig. 2.",
      "observed_candidate":{"S1c_phd":OBS_S1,"S2c_phd":OBS_S2,"log10_S2c":math.log10(OBS_S2)},
      "samples":[summarize(Path(p)) for p in sys.argv[1:]]}
    print(json.dumps(result,indent=2))
