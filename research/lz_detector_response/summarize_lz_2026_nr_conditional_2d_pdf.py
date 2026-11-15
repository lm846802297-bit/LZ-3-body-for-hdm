#!/usr/bin/env python3
"""Build conditional NR P(S1c, log10 S2c | true ER) sparse 2D histograms."""
import csv, json, math, sys
from collections import defaultdict
from pathlib import Path

E_WIDTH=10.0
S1_WIDTH=10.0
LOGS2_WIDTH=0.02

def summarize(path):
    cells=defaultdict(lambda:defaultdict(int))
    generated=0
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            generated+=1
            e=float(row["energy_keV"])
            s1=float(row["s1c_signed_phd"])
            s2=float(row["s2c_signed_phd"])
            # This driver stores corrected observables but not the separate S1 coincidence flag.
            # Restrict only to positive reconstructed S1c and S2c; do not call this post-selection.
            if not (math.isfinite(e) and math.isfinite(s1) and math.isfinite(s2)) or s1<=0 or s2<=0:
                continue
            eb=math.floor(e/E_WIDTH)*E_WIDTH
            s1b=math.floor(s1/S1_WIDTH)*S1_WIDTH
            log_s2=math.log10(s2)
            logb=round(math.floor(log_s2/LOGS2_WIDTH)*LOGS2_WIDTH,2)
            cells[eb][(s1b,logb)]+=1
    bins=[]
    for eb,counter in sorted(cells.items()):
        total=sum(counter.values())
        bins.append({"energy_low_keV":eb,"energy_high_keV":eb+E_WIDTH,
          "n_valid":total,"pdf_sparse":[[x,y,n/total] for (x,y),n in sorted(counter.items())]})
    return {"file":path.name,"n_generated":generated,"energy_bins":bins}

if __name__=="__main__":
    result={"study":"LZ NR conditional 2D response PDFs",
      "nest_commit":"541b6430dae6ea289cf110c99f174a9187f7fdee",
      "energy_prior":"Uniform true NR recoil energy 0.1-330 keV",
      "spatial_prior":"Uniform active-TPC cylinder proxy; not actual D-D/AmBe calibration-source distribution",
      "binning":{"energy_keV":E_WIDTH,"S1c_phd":S1_WIDTH,"log10S2c_dex":LOGS2_WIDTH},
      "definition":"Each energy bin stores a normalized sparse histogram for P(S1c, log10(S2c) | true NR energy bin), conditional only on positive reconstructed observables.",
      "limitation":"The compact driver does not export the separate S1 coincidence flag. These are not official post-selection PDFs and must not be combined with the published efficiency as though they were already selection-corrected.",
      "samples":[summarize(Path(p)) for p in sys.argv[1:]]}
    print(json.dumps(result,separators=(",",":")))
