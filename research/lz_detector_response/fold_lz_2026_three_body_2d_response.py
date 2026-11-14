#!/usr/bin/env python3
"""Fold pre-detector natural-xenon three-body recoil spectra through NEST NR response.

The response MC is uniform in true recoil energy over the exact analysis ROI and
uniform in active-TPC volume. Per-energy-bin cell probabilities are therefore
estimated as N_cell/N_generated_in_bin (not normalized only over positive cells).
The output is a pre-selection observable intensity. The published scalar WIMP-search
efficiency is deliberately NOT multiplied into this 2D PDF.
"""
from __future__ import annotations
import argparse, csv, json, math, statistics
from collections import defaultdict
from pathlib import Path

E_WIDTH=10.0
S1_WIDTH=10.0
LOGS2_WIDTH=0.02
ROI_MIN=5.4
ROI_MAX=269.9
BENCHMARKS=("red_ms200_dm1","green_ms300_dm1","black_ms360_dm1","blue_ms300_dm10")
RESPONSE_FAMILIES=("eft2024","tableS5","ws2024","generic")

def read_spectrum(path: Path, nuclear_model: str):
    rows=[]
    with path.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["halo_model"] != "shm_cutoff" or r["model"] != nuclear_model:
                continue
            rows.append((float(r["ER_keV"]),float(r["rate_events_kg_day_keV"])))
    rows.sort()
    if len(rows)<2: raise ValueError(f"insufficient {nuclear_model} spectrum points in {path}")
    xs=[r[0] for r in rows]; ys=[r[1] for r in rows]
    if xs[0]>ROI_MIN or xs[-1]<ROI_MAX: raise ValueError(f"spectrum does not cover ROI: {path}")
    if any(not math.isfinite(x) for x in xs+ys) or any(y<0 for y in ys):
        raise ValueError(f"non-finite or negative rate in {path}")
    if any(b<=a for a,b in zip(xs,xs[1:])): raise ValueError(f"non-increasing energies in {path}")
    return xs,ys

def interp(x,xs,ys):
    if x<=xs[0]: return ys[0]
    if x>=xs[-1]: return ys[-1]
    lo,hi=0,len(xs)-1
    while hi-lo>1:
        mid=(lo+hi)//2
        if xs[mid]<=x: lo=mid
        else: hi=mid
    t=(x-xs[lo])/(xs[hi]-xs[lo])
    return ys[lo]+t*(ys[hi]-ys[lo])

def integrate_linear(xs,ys,lo,hi):
    if not lo<hi: return 0.0
    knots=sorted({lo,hi}|{x for x in xs if lo<x<hi})
    total=0.0
    for a,b in zip(knots,knots[1:]):
        total += 0.5*(interp(a,xs,ys)+interp(b,xs,ys))*(b-a)
    return total

def read_response(path: Path):
    generated=defaultdict(int)
    valid=defaultdict(int)
    cells=defaultdict(lambda:defaultdict(int))
    total=0
    with path.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            e=float(r["energy_keV"])
            s1=float(r["s1c_signed_phd"]); s2=float(r["s2c_signed_phd"])
            if not math.isfinite(e): raise ValueError("non-finite recoil energy")
            eb=math.floor(e/E_WIDTH)*E_WIDTH
            generated[eb]+=1; total+=1
            if not (math.isfinite(s1) and math.isfinite(s2) and s1>0 and s2>0):
                continue
            valid[eb]+=1
            s1b=math.floor(s1/S1_WIDTH)*S1_WIDTH
            logb=math.floor(math.log10(s2)/LOGS2_WIDTH)*LOGS2_WIDTH
            logb=round(logb,2)
            cells[eb][(s1b,logb)]+=1
    bins={}
    for eb,n_gen in sorted(generated.items()):
        n_valid=valid[eb]
        bins[eb]={"n_generated":n_gen,"n_valid_positive":n_valid,
                  "positive_fraction":n_valid/n_gen if n_gen else 0,
                  "cells":cells[eb]}
    return {"file":path.name,"n_generated":total,"energy_bins":bins}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--response-dir",type=Path,required=True)
    ap.add_argument("--spectrum-dir",type=Path,default=Path("research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum"))
    ap.add_argument("--out-dir",type=Path,required=True)
    args=ap.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=True)

    response={}
    for family in RESPONSE_FAMILIES:
        path=args.response_dir/f"{family}.csv"
        if not path.is_file(): raise FileNotFoundError(path)
        response[family]=read_response(path)

    summary={"study":"three-body natural-xenon rate folded through NEST NR 2D response",
      "roi_keV":[ROI_MIN,ROI_MAX],"rate_units":"events/kg/day/keV",
      "folded_cell_units":"events/kg/day per (10 phd x 0.02 dex) cell",
      "response_nest_commit":"541b6430dae6ea289cf110c99f174a9187f7fdee",
      "response_energy_prior":"uniform true recoil energy in exact ROI 5.4-269.9 keV",
      "response_spatial_prior":"uniform active-TPC cylinder volume; not calibration-source geometry",
      "response_binning":{"energy_keV":E_WIDTH,"S1c_phd":S1_WIDTH,"log10S2c_dex":LOGS2_WIDTH},
      "response_probability_definition":"P(cell|E-bin) estimated by N_cell/N_generated_in_energy_bin; positive S1c/S2c cells retain their unconditional probability mass. Zero/nonpositive observables are tracked as lost probability, not renormalized away.",
      "selection_and_efficiency":"No detector efficiency or event-selection efficiency is multiplied into this 2D intensity. The separately published energy-only final-ROI efficiency cannot specify a selected 2D shape; applying it here would risk double counting and would not reproduce selection migration.",
      "benchmark_results":[]}
    intensity_path=args.out_dir/"signal_2d_intensity.csv"
    with intensity_path.open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["benchmark","nuclear_model","response_family","s1c_low_phd","s1c_high_phd","log10s2c_low","log10s2c_high","rate_events_kg_day_cell"])
        for benchmark in BENCHMARKS:
            spectrum_path=args.spectrum_dir/benchmark/"natural_xenon_continuous_spectrum.csv"
            for nuc in ("GCN","JJ55"):
                xs,ys=read_spectrum(spectrum_path,nuc)
                raw_roi=integrate_linear(xs,ys,ROI_MIN,ROI_MAX)
                for family in RESPONSE_FAMILIES:
                    bins=response[family]["energy_bins"]
                    total_cells=defaultdict(float)
                    response_weighted_rate=0.0
                    response_weighted_mc_variance=0.0
                    bin_records=[]
                    for eb,rb in sorted(bins.items()):
                        lo=max(ROI_MIN,float(eb)); hi=min(ROI_MAX,float(eb)+E_WIDTH)
                        if hi<=lo: continue
                        rate_bin=integrate_linear(xs,ys,lo,hi)
                        n_gen=rb["n_generated"]
                        if n_gen<=0: raise ValueError(f"empty response energy bin {eb} in {family}")
                        posfrac=rb["positive_fraction"]
                        response_weighted_rate += rate_bin*posfrac
                        # Binomial MC uncertainty on the retained positive-observable fraction.
                        response_weighted_mc_variance += (rate_bin**2)*posfrac*(1-posfrac)/n_gen
                        for cell,count in rb["cells"].items():
                            total_cells[cell] += rate_bin*count/n_gen
                        bin_records.append({"energy_bin_low_keV":eb,"integral_rate_events_kg_day":rate_bin,
                          "n_generated":n_gen,"positive_fraction":posfrac})
                    cell_sum=math.fsum(total_cells.values())
                    closure=abs(cell_sum-response_weighted_rate)/max(abs(response_weighted_rate),1e-300)
                    if closure>5e-12: raise RuntimeError(f"2D cell normalization does not close for {benchmark}/{nuc}/{family}: {closure}")
                    mc_sigma=math.sqrt(response_weighted_mc_variance)
                    for (s1b,logb),rate_cell in sorted(total_cells.items()):
                        w.writerow([benchmark,nuc,family,s1b,s1b+S1_WIDTH,logb,round(logb+LOGS2_WIDTH,2),f"{rate_cell:.12g}"])
                    positive_fraction=response_weighted_rate/raw_roi if raw_roi>0 else 0.0
                    summary["benchmark_results"].append({
                      "benchmark":benchmark,"nuclear_response":nuc,"response_family":family,
                      "raw_pre_detector_rate_roi_events_kg_day":raw_roi,
                      "positive_S1c_S2c_rate_events_kg_day":response_weighted_rate,
                      "positive_observable_fraction_of_raw_rate":positive_fraction,
                      "positive_rate_MC_standard_error_events_kg_day":mc_sigma,
                      "positive_rate_MC_relative_standard_error":mc_sigma/response_weighted_rate if response_weighted_rate>0 else None,
                      "number_of_2d_cells":len(total_cells),
                      "sum_of_2d_cells_events_kg_day":cell_sum,
                      "cell_sum_relative_closure_error":closure,
                      "response_energy_bin_integrals":bin_records,
                      "conditional_pdf_normalization":"For a PDF conditional on positive S1c and S2c, divide each cell intensity by positive_S1c_S2c_rate; for an unconditioned pre-selection intensity, retain the rates as written."
                    })
    # Export response MC acceptance/validity by family and energy bin for auditing.
    response_audit={"families":{}}
    for family,obj in response.items():
        response_audit["families"][family]=[
          {"energy_low_keV":eb,"energy_high_keV":eb+E_WIDTH,
           "n_generated":rb["n_generated"],"n_valid_positive":rb["n_valid_positive"],
           "positive_fraction":rb["positive_fraction"]}
          for eb,rb in sorted(obj["energy_bins"].items())]
    (args.out_dir/"response_validity_by_energy.json").write_text(json.dumps(response_audit,indent=2)+"\n")
    (args.out_dir/"fold_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps({"n_folded_combinations":len(summary["benchmark_results"]),
      "intensity_csv":str(intensity_path),"fold_summary":str(args.out_dir/"fold_summary.json"),
      "max_closure_error":max(x["cell_sum_relative_closure_error"] for x in summary["benchmark_results"])},indent=2))

if __name__=="__main__": main()
