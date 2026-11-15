#!/usr/bin/env python3
"""ER-band and conditional 2D response-PDF summary for the pinned NEST EFT2024 candidate."""
import csv
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

OBS_S1 = 540.07916
OBS_S2 = 9267.53
OBS_LOG_S2 = math.log10(OBS_S2)
BAND_BIN_WIDTH = 5.0
MIN_BAND_EVENTS = 100
SIGMA80_FACTOR = 2.5631031311
ENERGY_BIN_WIDTH = 10.0
PDF_S1_BIN_WIDTH = 10.0
PDF_LOGS2_BIN_WIDTH = 0.02

def quantile(values, p):
    values = sorted(values)
    if not values:
        return None
    x = (len(values) - 1) * p
    lo, hi = math.floor(x), math.ceil(x)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - x) + values[hi] * (x - lo)

def make_band(bins):
    bands = []
    for lo, vals in sorted(bins.items()):
        if len(vals) < MIN_BAND_EVENTS:
            continue
        q10, q50, q90 = quantile(vals, .10), quantile(vals, .50), quantile(vals, .90)
        bands.append({
            "s1c_low_phd": lo, "s1c_high_phd": lo + BAND_BIN_WIDTH, "n": len(vals),
            "log10_s2c_p10": q10, "log10_s2c_median": q50, "log10_s2c_p90": q90,
            "log10_s2c_mean": statistics.fmean(vals),
            "log10_s2c_sd": statistics.stdev(vals) if len(vals) > 1 else 0.0,
        })
    return bands

def candidate_bin(bands):
    low = math.floor(OBS_S1 / BAND_BIN_WIDTH) * BAND_BIN_WIDTH
    b = next((x.copy() for x in bands if x["s1c_low_phd"] == low), None)
    if b:
        sig80 = (b["log10_s2c_p90"] - b["log10_s2c_p10"]) / SIGMA80_FACTOR
        b.update({
            "observed_candidate_log10_s2c": OBS_LOG_S2,
            "candidate_minus_median_sigma80": (OBS_LOG_S2 - b["log10_s2c_median"]) / sig80,
            "candidate_minus_mean_sigma_sd": (OBS_LOG_S2 - b["log10_s2c_mean"]) / b["log10_s2c_sd"] if b["log10_s2c_sd"] > 0 else None,
            "sigma80_equivalent": sig80,
        })
    return b

def sparse_pdf(counter):
    total = sum(counter.values())
    if total == 0:
        return []
    return [[s1, log_s2, count / total] for (s1, log_s2), count in sorted(counter.items())]

def summarize(path, make_2d):
    bins_all, bins_trigger, bins_roi = defaultdict(list), defaultdict(list), defaultdict(list)
    energy_hist = defaultdict(lambda: {
        "n_generated": 0, "n_valid": 0, "n_trigger_pass": 0,
        "all": Counter(), "trigger": Counter()
    })
    energies, radii, zs = [], [], []
    config = position_mode = None
    n_generated = n_s1_pass = n_s2_pass = n_roi_pass = 0
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            n_generated += 1
            config, position_mode = row["config"], row["position_mode"]
            e, r, z = float(row["energy_keV"]), float(row["r_mm"]), float(row["z_mm"])
            s1, s2, log_s2 = float(row["s1c_phd"]), float(row["s2c_phd"]), float(row["log10_s2c_phd"])
            s1_pass, s2_pass = int(row["s1_pass"]) == 1, int(row["s2_pass"]) == 1
            roi_pass = int(row["analysis_roi_pass"]) == 1
            energies.append(e); radii.append(r); zs.append(z)
            n_s1_pass += int(s1_pass); n_s2_pass += int(s2_pass); n_roi_pass += int(roi_pass)
            if s2 <= 0 or log_s2 < 0 or s1 < 0:
                continue
            band_lo = math.floor(s1 / BAND_BIN_WIDTH) * BAND_BIN_WIDTH
            bins_all[band_lo].append(log_s2)
            if s1_pass and s2_pass:
                bins_trigger[band_lo].append(log_s2)
            if roi_pass:
                bins_roi[band_lo].append(log_s2)

            if make_2d:
                ebin = math.floor(e / ENERGY_BIN_WIDTH) * ENERGY_BIN_WIDTH
                item = energy_hist[ebin]
                item["n_generated"] += 1
                item["n_valid"] += 1
                s1bin = math.floor(s1 / PDF_S1_BIN_WIDTH) * PDF_S1_BIN_WIDTH
                logbin = math.floor(log_s2 / PDF_LOGS2_BIN_WIDTH) * PDF_LOGS2_BIN_WIDTH
                item["all"][(s1bin, round(logbin, 2))] += 1
                if s1_pass and s2_pass:
                    item["n_trigger_pass"] += 1
                    item["trigger"][(s1bin, round(logbin, 2))] += 1

    bands_all, bands_trigger, bands_roi = make_band(bins_all), make_band(bins_trigger), make_band(bins_roi)
    out = {
        "file": path.name, "config": config, "position_mode": position_mode,
        "n_generated": n_generated, "n_s1_pass": n_s1_pass,
        "n_s2_pass": n_s2_pass, "n_analysis_roi_pass": n_roi_pass,
        "energy_min_keV": min(energies), "energy_max_keV": max(energies),
        "r_min_mm": min(radii), "r_max_mm": max(radii),
        "z_min_mm": min(zs), "z_max_mm": max(zs),
        "candidate_bin_all": candidate_bin(bands_all),
        "candidate_bin_trigger_pass": candidate_bin(bands_trigger),
        "candidate_bin_analysis_roi": candidate_bin(bands_roi),
        "bands_all": bands_all,
        "bands_trigger_pass": bands_trigger,
        "bands_analysis_roi": bands_roi,
    }
    if make_2d:
        conditional = []
        for ebin, item in sorted(energy_hist.items()):
            conditional.append({
                "energy_low_keV": ebin,
                "energy_high_keV": ebin + ENERGY_BIN_WIDTH,
                "n_valid": item["n_valid"],
                "n_trigger_pass": item["n_trigger_pass"],
                "trigger_pass_fraction": item["n_trigger_pass"] / item["n_valid"] if item["n_valid"] else None,
                "pdf_all_sparse": sparse_pdf(item["all"]),
                "pdf_trigger_pass_sparse": sparse_pdf(item["trigger"]),
            })
        out["conditional_2d_pdf"] = {
            "definition": "Empirical P(S1c, log10(S2c) | true ER energy bin) from uniform-in-energy, uniform-active-TPC samples. Each sparse cell stores (S1c-bin-low phd, log10S2c-bin-low, normalized probability).",
            "energy_bin_width_keV": ENERGY_BIN_WIDTH,
            "s1c_bin_width_phd": PDF_S1_BIN_WIDTH,
            "log10_s2c_bin_width_dex": PDF_LOGS2_BIN_WIDTH,
            "energy_bins": conditional,
        }
    return out

def compare(samples):
    result = []
    for band_key in ("bands_all", "bands_trigger_pass", "bands_analysis_roi"):
        groups = defaultdict(dict)
        for s in samples:
            groups[s["position_mode"]][s["config"]] = {b["s1c_low_phd"]: b for b in s[band_key]}
        configs = ("eft2024", "table_s3", "generic")
        for pos, group in groups.items():
            for i, left_name in enumerate(configs):
                for right_name in configs[i+1:]:
                    if left_name not in group or right_name not in group:
                        continue
                    left, right = group[left_name], group[right_name]
                    common = sorted(set(left) & set(right))
                    if not common:
                        continue
                    entry = {"band_definition": band_key, "position_mode": pos,
                             "left": left_name, "right": right_name, "common_bins": len(common)}
                    for key in ("log10_s2c_median", "log10_s2c_p10", "log10_s2c_p90"):
                        ds = [abs(left[x][key] - right[x][key]) for x in common]
                        entry[key + "_mae_dex"] = statistics.fmean(ds)
                        entry[key + "_max_abs_dex"] = max(ds)
                    result.append(entry)
    return result

if __name__ == "__main__":
    paths = [Path(x) for x in sys.argv[1:]]
    samples = [summarize(p, make_2d=(p.stem.endswith("uniform_tpc"))) for p in paths]
    print(json.dumps({
        "study": "LZ ER flat-energy event-level band and 2D response, NEST commit 541b643",
        "interpretation": (
            "EFT2024 uses the public LZ-specific executable candidate with ERYieldsParam[5]=-1. "
            "table_s3 changes only ERYieldsParam[5] to the literal Table S3 value 0, which disables "
            "the density/W correction branch in GetYieldBetaGR. generic uses generic ER yield and "
            "NRERWidths defaults on the same EFT2024 detector overrides. All runs use NEST's "
            "default SkewnessER=-999 path, which evaluates its LUX Run04 energy/field-dependent "
            "ER charge skewness; this is distinct from the Table S4 alpha1/alpha2 parameters."
        ),
        "energy_prior": "Uniform true ER energy from 0.1 to 300 keV.",
        "observed_candidate": {"S1c_phd": OBS_S1, "S2c_phd": OBS_S2, "log10_S2c": OBS_LOG_S2},
        "samples": samples,
        "band_comparisons": compare(samples)
    }, indent=2))
