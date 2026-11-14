#!/usr/bin/env python3
"""Summarize full-volume NR calibration-band proxy samples by S1c."""
import csv, json, math, statistics, sys
from collections import defaultdict
from pathlib import Path

BIN_WIDTH=5.0
MIN_BIN_EVENTS=100
OBS_S1=540.07916
OBS_S2=9267.53

def quantile(xs,p):
    x=sorted(xs)
    if not x: return None
    k=(len(x)-1)*p; lo=math.floor(k); hi=math.ceil(k)
    return x[lo] if lo==hi else x[lo]*(hi-k)+x[hi]*(k-lo)

def summarize(path):
    bins=defaultdict(list); energies=[]; positions=[]; n=0; pass_s1=pass_s2=0
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            n+=1
            e=float(row["energy_keV"]); x=float(row["x_mm"]); y=float(row["y_mm"]); z=float(row["z_mm"])
            s1=float(row["s1c_signed_phd"]); s2=float(row["s2c_signed_phd"])
            energies.append(e); positions.append((x*x+y*y,z))
            if s1>0: pass_s1+=1
            if s2>0: pass_s2+=1
            # Band samples are conditioned on valid reconstructed positive observables.
            if not (math.isfinite(s1) and math.isfinite(s2) and s1>0 and s2>0): continue
            lo=math.floor(s1/BIN_WIDTH)*BIN_WIDTH
            bins[lo].append(math.log10(s2))
    bands=[]
    for lo,vals in sorted(bins.items()):
        if len(vals)<MIN_BIN_EVENTS: continue
        bands.append({"s1c_low_phd":lo,"s1c_high_phd":lo+BIN_WIDTH,"n":len(vals),
          "log10_s2c_mean":statistics.fmean(vals),"log10_s2c_p10":quantile(vals,.10),
          "log10_s2c_median":quantile(vals,.50),"log10_s2c_p90":quantile(vals,.90)})
    candidate_bin=math.floor(OBS_S1/BIN_WIDTH)*BIN_WIDTH
    cand=next((b for b in bands if b["s1c_low_phd"]==candidate_bin),None)
    if cand:
        sig_eq=(cand["log10_s2c_p90"]-cand["log10_s2c_p10"])/2.5631
        cand["sigma_eq_10_90"]=sig_eq
        cand["observed_candidate_log10_s2c"]=math.log10(OBS_S2)
        cand["candidate_minus_median_sigma_eq"]=(math.log10(OBS_S2)-cand["log10_s2c_median"])/sig_eq
    return {"file":path.name,"n_generated":n,"energy_min_keV":min(energies),
      "energy_max_keV":max(energies),"mean_energy_keV":statistics.fmean(energies),
      "s1_positive_fraction":pass_s1/n,"s2_positive_fraction":pass_s2/n,
      "position_prior":"uniform volume in public detector cylinder: r=Rmax*sqrt(U), phi=2piU, z uniform over active drift",
      "mean_r2_mm2":statistics.fmean(p[0] for p in positions),
      "mean_z_mm":statistics.fmean(p[1] for p in positions),
      "s1_bin_width_phd":BIN_WIDTH,"min_bin_events":MIN_BIN_EVENTS,
      "candidate_bin":cand,"bands":bands}

def compare(samples):
    by={Path(s["file"]).stem:s for s in samples}
    names=list(by)
    reference=by.get("eft2024")
    if not reference: return {}
    out={}
    for name in names:
        if name=="eft2024": continue
        other=by[name]
        joined={b["s1c_low_phd"]:b for b in other["bands"]}
        pairs=[(a,joined[a["s1c_low_phd"]]) for a in reference["bands"] if a["s1c_low_phd"] in joined]
        out[name]={}
        for key in ("log10_s2c_mean","log10_s2c_p10","log10_s2c_median","log10_s2c_p90"):
            ds=[abs(a[key]-b[key]) for a,b in pairs]
            out[name][key+"_mean_abs_difference_dex"]=statistics.fmean(ds) if ds else None
            out[name][key+"_max_abs_difference_dex"]=max(ds) if ds else None
        out[name]["matched_s1_bins"]=len(pairs)
    return out

if __name__=="__main__":
    samples=[summarize(Path(p)) for p in sys.argv[1:]]
    print(json.dumps({"study":"LZ NR full-volume calibration-band candidate comparison",
      "nest_source_commit":"541b6430dae6ea289cf110c99f174a9187f7fdee",
      "energy_prior":"uniform true NR recoil energy in 0.1-330 keV",
      "spatial_prior":"uniform active-TPC cylinder proxy; not actual D-D/AmBe source distribution",
      "families":{"eft2024":"public LZ-specific executable candidate: EFT2024 means, NRERWidthsParam and detector overrides",
       "tableS5":"rounded printed Table S5 NR mean vector with EFT2024 widths and detector overrides",
       "ws2024":"WS2024 detector class and its own NR mean-yield and width vectors",
       "generic":"generic upstream NEST NR means and widths with EFT2024 detector overrides"},
      "candidate":{"S1c_phd":OBS_S1,"S2c_phd":OBS_S2,"log10_S2c":math.log10(OBS_S2)},
      "samples":samples,"comparisons_vs_eft2024":compare(samples)},indent=2))
