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

def summarize_bins(bins):
    out = []
    for lo, values in sorted(bins.items()):
        if len(values) < MIN_BIN_EVENTS:
            continue
        q10, q50, q90 = quantile(values, .10), quantile(values, .50), quantile(values, .90)
        out.append({
            "s1c_low_phd": lo, "s1c_high_phd": lo + BIN_WIDTH, "n": len(values),
            "log10_s2c_p10": q10, "log10_s2c_median": q50, "log10_s2c_p90": q90,
            "log10_s2c_mean": statistics.fmean(values),
            "log10_s2c_sd": statistics.stdev(values) if len(values) > 1 else 0.0,
        })
    return out

def candidate_summary(bands):
    low = math.floor(OBS_S1 / BIN_WIDTH) * BIN_WIDTH
    band = next((b.copy() for b in bands if b["s1c_low_phd"] == low), None)
    if band:
        sigma80 = (band["log10_s2c_p90"] - band["log10_s2c_p10"]) / SIGMA80_FACTOR
        sd = band["log10_s2c_sd"]
        band.update({
            "observed_candidate_log10_s2c": OBS_LOG_S2,
            "sigma80_equivalent": sigma80,
            "candidate_minus_median_sigma80": (OBS_LOG_S2 - band["log10_s2c_median"]) / sigma80,
            "candidate_minus_mean_sigma_sd": (OBS_LOG_S2 - band["log10_s2c_mean"]) / sd if sd > 0 else None,
        })
    return band

def summarize(path):
    bins_all = defaultdict(list)
    bins_trigger = defaultdict(list)
    bins_roi = defaultdict(list)
    energies, radii, zs = [], [], []
    config = position_mode = None
    n_generated = n_s1_pass = n_s2_pass = n_roi_pass = 0
    for_s2 = []
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            n_generated += 1
            config, position_mode = row["config"], row["position_mode"]
            e, r, z = float(row["energy_keV"]), float(row["r_mm"]), float(row["z_mm"])
            s1, s2 = float(row["s1c_phd"]), float(row["s2c_phd"])
            log_s2 = float(row["log10_s2c_phd"])
            s1_pass, s2_pass = int(row["s1_pass"]) == 1, int(row["s2_pass"]) == 1
            roi_pass = int(row["analysis_roi_pass"]) == 1
            if not all(math.isfinite(x) for x in (e, r, z, s1, s2, log_s2)):
                raise ValueError(f"non-finite value in {path}")
            energies.append(e); radii.append(r); zs.append(z)
            n_s1_pass += int(s1_pass); n_s2_pass += int(s2_pass); n_roi_pass += int(roi_pass)
            if s2 <= 0 or log_s2 < 0 or s1 < 0:
                continue
            lo = math.floor(s1 / BIN_WIDTH) * BIN_WIDTH
            bins_all[lo].append(log_s2)
            if s1_pass and s2_pass:
                bins_trigger[lo].append(log_s2)
            if roi_pass:
                bins_roi[lo].append(log_s2)

    bands_all = summarize_bins(bins_all)
    bands_trigger = summarize_bins(bins_trigger)
    bands_roi = summarize_bins(bins_roi)
    return {
        "file": path.name, "config": config, "position_mode": position_mode,
        "n_generated": n_generated, "n_s1_pass": n_s1_pass,
        "n_s2_pass": n_s2_pass, "n_analysis_roi_pass": n_roi_pass,
        "energy_min_keV": min(energies), "energy_max_keV": max(energies),
        "r_min_mm": min(radii), "r_max_mm": max(radii),
        "z_min_mm": min(zs), "z_max_mm": max(zs),
        "bin_width_phd": BIN_WIDTH, "minimum_events_per_bin": MIN_BIN_EVENTS,
        "candidate_bin_all": candidate_summary(bands_all),
        "candidate_bin_trigger_pass": candidate_summary(bands_trigger),
        "candidate_bin_analysis_roi": candidate_summary(bands_roi),
        "bands_all": bands_all,
        "bands_trigger_pass": bands_trigger,
        "bands_analysis_roi": bands_roi,
    }

def compare(samples):
    result = []
    for band_key in ("bands_all", "bands_trigger_pass", "bands_analysis_roi"):
        groups = defaultdict(dict)
        for sample in samples:
            groups[sample["position_mode"]][sample["config"]] = {
                b["s1c_low_phd"]: b for b in sample[band_key]
            }
        configs = ("eft2024", "eftmean_wswidth", "eftmean_genericwidth", "ws2024", "generic")
        for position_mode, group in groups.items():
            for i, left_name in enumerate(configs):
                for right_name in configs[i + 1:]:
                    if left_name not in group or right_name not in group:
                        continue
                    left, right = group[left_name], group[right_name]
                    common = sorted(set(left) & set(right))
                    if not common:
                        continue
                    entry = {"band_definition": band_key, "position_mode": position_mode,
                             "left": left_name, "right": right_name, "common_bins": len(common)}
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
            "distribution. candidate is a fixed-position local diagnostic. "
            "bands_all are before NEST S1/S2 threshold flags; bands_trigger_pass "
            "require both NEST flags; bands_analysis_roi additionally apply the "
            "published S1c/S2/S2c ROI cuts as a diagnostic."
        ),
        "energy_prior": "Uniform in true NR recoil energy over each CSV's recorded range.",
        "observed_candidate": {"S1c_phd": OBS_S1, "S2c_phd": OBS_S2, "log10_S2c": OBS_LOG_S2},
        "samples": samples,
        "full_band_comparisons": compare(samples)
    }, indent=2))
