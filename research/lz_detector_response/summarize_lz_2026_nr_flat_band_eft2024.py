#!/usr/bin/env python3
"""Summarize full-range NR bands from the pinned NEST EFT2024 candidate workflow."""
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

OBS_S1 = 540.07916
OBS_S2 = 9267.53
OBS_LOG_S2 = math.log10(OBS_S2)
BIN_WIDTH = 5.0
MIN_BIN_EVENTS = 100
SIGMA80_FACTOR = 2.5631031311

def quantile(values, p):
    values = sorted(values)
    if not values:
        return None
    x = (len(values) - 1) * p
    lo, hi = math.floor(x), math.ceil(x)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - x) + values[hi] * (x - lo)

def summarize(path):
    bins = defaultdict(list)
    energies, radii, zs, s1s, s2s = [], [], [], [], []
    config = position_mode = None
    n_generated = 0
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            n_generated += 1
            config = row["config"]
            position_mode = row["position_mode"]
            e = float(row["energy_keV"])
            r = float(row["r_mm"])
            z = float(row["z_mm"])
            s1 = float(row["s1c_phd"])
            s2 = float(row["s2c_phd"])
            log_s2 = float(row["log10_s2c_phd"])
            if not all(math.isfinite(x) for x in (e, r, z, s1, s2, log_s2)):
                raise ValueError(f"non-finite value in {path}")
            energies.append(e)
            radii.append(r)
            zs.append(z)
            if s2 <= 0 or log_s2 < 0 or s1 < 0:
                continue
            s1s.append(s1)
            s2s.append(s2)
            lo = math.floor(s1 / BIN_WIDTH) * BIN_WIDTH
            bins[lo].append(log_s2)

    bands = []
    for lo, values in sorted(bins.items()):
        if len(values) < MIN_BIN_EVENTS:
            continue
        q10 = quantile(values, 0.10)
        q50 = quantile(values, 0.50)
        q90 = quantile(values, 0.90)
        bands.append({
            "s1c_low_phd": lo,
            "s1c_high_phd": lo + BIN_WIDTH,
            "n": len(values),
            "log10_s2c_p10": q10,
            "log10_s2c_median": q50,
            "log10_s2c_p90": q90,
        })

    candidate_low = math.floor(OBS_S1 / BIN_WIDTH) * BIN_WIDTH
    candidate = next((b for b in bands if b["s1c_low_phd"] == candidate_low), None)
    if candidate:
        sigma_eq = (candidate["log10_s2c_p90"] - candidate["log10_s2c_p10"]) / SIGMA80_FACTOR
        candidate.update({
            "observed_candidate_log10_s2c": OBS_LOG_S2,
            "sigma80_equivalent": sigma_eq,
            "candidate_minus_median_sigma80": (OBS_LOG_S2 - candidate["log10_s2c_median"]) / sigma_eq,
        })

    return {
        "file": path.name,
        "config": config,
        "position_mode": position_mode,
        "n_generated": n_generated,
        "n_valid_for_band": len(s1s),
        "energy_min_keV": min(energies),
        "energy_max_keV": max(energies),
        "r_min_mm": min(radii),
        "r_max_mm": max(radii),
        "z_min_mm": min(zs),
        "z_max_mm": max(zs),
        "s1c_min_phd": min(s1s) if s1s else None,
        "s1c_max_phd": max(s1s) if s1s else None,
        "candidate_bin": candidate,
        "bin_width_phd": BIN_WIDTH,
        "minimum_events_per_bin": MIN_BIN_EVENTS,
        "bands": bands,
    }

def compare(samples):
    result = []
    groups = defaultdict(dict)
    for sample in samples:
        groups[sample["position_mode"]][sample["config"]] = {
            b["s1c_low_phd"]: b for b in sample["bands"]
        }
    configs = ("eft2024", "ws2024", "generic")
    for position_mode, group in groups.items():
        for i, left_name in enumerate(configs):
            for right_name in configs[i + 1:]:
                if left_name not in group or right_name not in group:
                    continue
                left, right = group[left_name], group[right_name]
                common = sorted(set(left) & set(right))
                if not common:
                    continue
                entry = {"position_mode": position_mode,
                         "left": left_name, "right": right_name,
                         "common_bins": len(common)}
                for key in ("log10_s2c_median", "log10_s2c_p10", "log10_s2c_p90"):
                    diffs = [abs(left[x][key] - right[x][key]) for x in common]
                    entry[key + "_mae_dex"] = statistics.fmean(diffs)
                    entry[key + "_max_abs_dex"] = max(diffs)
                result.append(entry)
    return result

if __name__ == "__main__":
    samples = [summarize(Path(arg)) for arg in sys.argv[1:]]
    print(json.dumps({
        "study": "LZ NR flat-energy event-level band, NEST commit 541b643",
        "interpretation": (
            "EFT2024 is a public LZ-specific configuration candidate, not a confirmed "
            "copy of the exact LZ 2026 production build. WS2024 is the earlier LZ "
            "configuration. Generic uses upstream NEST mean-yield/width defaults on "
            "the same EFT2024 detector-response overrides. uniform_tpc is a uniform "
            "active-cylinder proxy, not the measured D-D/AmBe calibration position "
            "distribution. candidate is a fixed-position local diagnostic."
        ),
        "energy_prior": "Uniform in true NR recoil energy over each CSV's recorded range.",
        "observed_candidate": {
            "S1c_phd": OBS_S1,
            "S2c_phd": OBS_S2,
            "log10_S2c": OBS_LOG_S2
        },
        "samples": samples,
        "full_band_comparisons": compare(samples)
    }, indent=2))
