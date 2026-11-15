#!/usr/bin/env python3
"""Ten-seed event-weighted S1 upper-tail and ROI-migration audit for black ms=360 keV."""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import converge_lz_2026_three_body_energy_grid as grid

BENCHMARK = "black_ms360_dm1"
MODES = ("parametric", "full")
NUCLEAR_MODELS = ("GCN", "JJ55")
SEED_COUNT_MIN = 3
EVENTS_PER_SEED = 470_000
EVENTS_PER_BIN = 2_000
REPLICAS_PER_BIN = 1_000
ENERGY_MIN_KEV = 35.0
ENERGY_MAX_KEV = 269.9
ENERGY_BIN_WIDTH_KEV = 1.0
S1_THRESHOLDS_PHD = (500, 550, 575, 590, 600, 610, 625, 650, 700, 800)
S1_HIST_WIDTH_PHD = 10.0
S1_QUANTILE_WIDTH_PHD = 1.0
BOOTSTRAP_REPLICATES_DEFAULT = 2000
BOOTSTRAP_SEED = 20261116
T95_BY_DF = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
    21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
    26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
}
ENERGY_BANDS_KEV = {
    "black_support_205_269p9": (205.0, 269.9),
    "legacy_tail_225p4_269p9": (225.4, 269.9),
    "band_205_225": (205.0, 225.0),
    "band_225_240": (225.0, 240.0),
    "band_240_255": (240.0, 255.0),
    "band_255_269p9": (255.0, 269.9),
}
REQUIRED_COLUMNS = {
    "event", "replica", "energy_bin_index", "energy_bin_low_keV",
    "energy_bin_high_keV", "energy_keV", "s1_param_signed_phd",
    "s1_param_abs_phd", "s1_param_pass", "s1_full_signed_phd",
    "s1_full_abs_phd", "s1_full_pass", "s2_signed_phd", "s2_abs_phd",
    "s2_raw_phd", "s2_threshold_pass",
}


def add_weight(target: dict, key, weight: float) -> None:
    target[key] = target.get(key, 0.0) + weight


def total_variation(a: dict, b: dict) -> float | None:
    total_a = math.fsum(a.values())
    total_b = math.fsum(b.values())
    if total_a <= 0.0 or total_b <= 0.0:
        return None
    return 0.5 * math.fsum(
        abs(a.get(key, 0.0) / total_a - b.get(key, 0.0) / total_b)
        for key in set(a) | set(b)
    )


def normalized_map(values: dict) -> dict:
    total = math.fsum(values.values())
    if total <= 0.0:
        return {}
    return {key: value / total for key, value in values.items() if value != 0.0}


def mean_normalized_map(maps: list[dict]) -> dict:
    if not maps:
        raise ValueError("cannot average an empty map collection")
    output = defaultdict(float)
    for values in maps:
        normalized = normalized_map(values)
        for key, value in normalized.items():
            output[key] += value / len(maps)
    return dict(output)


def bootstrap_tv_interval(
    maps_a: list[dict],
    maps_b: list[dict],
    replicates: int = BOOTSTRAP_REPLICATES_DEFAULT,
    seed: int = BOOTSTRAP_SEED,
) -> list[float] | None:
    if len(maps_a) != len(maps_b) or len(maps_a) < 3:
        raise ValueError("paired bootstrap requires at least three matched seed maps")
    if replicates < 200:
        raise ValueError("at least 200 bootstrap replicates are required")
    rng = random.Random(seed)
    n = len(maps_a)
    values = []
    for _ in range(replicates):
        indices = [rng.randrange(n) for _ in range(n)]
        mean_a = mean_normalized_map([maps_a[i] for i in indices])
        mean_b = mean_normalized_map([maps_b[i] for i in indices])
        tv = total_variation(mean_a, mean_b)
        if tv is not None:
            values.append(tv)
    if len(values) != replicates:
        raise ValueError("bootstrap encountered an empty resampled distribution")
    values.sort()
    lo = values[math.floor(0.025 * (replicates - 1))]
    hi = values[math.ceil(0.975 * (replicates - 1))]
    return [lo, hi]


def weighted_quantile_from_hist(hist: dict, quantile: float) -> float | None:
    if not 0.0 <= quantile <= 1.0:
        raise ValueError("quantile must lie in [0, 1]")
    total = math.fsum(hist.values())
    if total <= 0.0:
        return None
    target = quantile * total
    cumulative = 0.0
    for lower_bin in sorted(hist):
        cumulative += hist[lower_bin]
        if cumulative >= target:
            return float(lower_bin) * S1_QUANTILE_WIDTH_PHD
    return float(max(hist)) * S1_QUANTILE_WIDTH_PHD


def scalar_stats(values: list[float]) -> dict:
    if len(values) < 2:
        raise ValueError("at least two independent seed estimates are required")
    if any(not math.isfinite(value) for value in values):
        raise ValueError("seed estimates must be finite")
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    sem = sd / math.sqrt(len(values))
    critical = T95_BY_DF.get(len(values) - 1, 1.96)
    return {
        "mean": mean,
        "sd": sd,
        "sem": sem,
        "t95_ci": [mean - critical * sem, mean + critical * sem],
    }


def normalized_stratum_event_weight(exact_bin_rate: float, differential_rate: float, sum_differential_rate: float) -> float:
    if exact_bin_rate < 0.0 or differential_rate < 0.0 or sum_differential_rate < 0.0:
        raise ValueError("event-rate weights must be non-negative")
    if exact_bin_rate == 0.0:
        return 0.0
    if sum_differential_rate <= 0.0:
        raise ValueError("positive exact bin rate has zero sampled differential-rate sum")
    return exact_bin_rate * differential_rate / sum_differential_rate


def s1_roi_pass(pass_flag: bool, s1c: float) -> bool:
    return bool(pass_flag) and grid.S1_MIN_PHD <= s1c <= grid.S1_MAX_PHD


def ws_roi_pass(pass_flag: bool, s1c: float, s2r: float, s2c: float, s2_flag: bool) -> bool:
    return bool(pass_flag and s2_flag) and grid.ws_roi_pass(s1c, s2r, s2c)


def new_bucket() -> dict:
    return {
        "n_events": 0,
        "raw_weight": 0.0,
        "p_coin_weight": 0.0, "f_coin_weight": 0.0,
        "p_s1_roi_weight": 0.0, "f_s1_roi_weight": 0.0,
        "p_ws_roi_weight": 0.0, "f_ws_roi_weight": 0.0,
        "p_hist_1phd": defaultdict(float), "f_hist_1phd": defaultdict(float),
        "p_hist_10phd": defaultdict(float), "f_hist_10phd": defaultdict(float),
        "p_upper_hist_10phd": defaultdict(float), "f_upper_hist_10phd": defaultdict(float),
        "p_nest_map": defaultdict(float), "f_nest_map": defaultdict(float),
        "p_ws_map": defaultdict(float), "f_ws_map": defaultdict(float),
        "p_tail_weight": {t: 0.0 for t in S1_THRESHOLDS_PHD},
        "f_tail_weight": {t: 0.0 for t in S1_THRESHOLDS_PHD},
        "paired_tail_difference_weight": {t: 0.0 for t in S1_THRESHOLDS_PHD},
        "p_to_f_cross_600_weight": 0.0,
        "f_to_p_cross_600_weight": 0.0,
        "p_only_s1_roi_weight": 0.0, "f_only_s1_roi_weight": 0.0,
        "p_only_ws_roi_weight": 0.0, "f_only_ws_roi_weight": 0.0,
    }


def in_band(energy: float, low: float, high: float) -> bool:
    if high == ENERGY_MAX_KEV:
        return low <= energy <= high
    return low <= energy < high


def update_bucket(bucket: dict, row: dict, weight: float) -> None:
    bucket["n_events"] += 1
    bucket["raw_weight"] += weight
    p = float(row["s1_param_abs_phd"])
    f = float(row["s1_full_abs_phd"])
    p_pass = bool(int(row["s1_param_pass"]))
    f_pass = bool(int(row["s1_full_pass"]))
    s2c = float(row["s2_abs_phd"])
    s2r = float(row["s2_raw_phd"])
    s2_pass = bool(int(row["s2_threshold_pass"]))

    p_roi = s1_roi_pass(p_pass, p)
    f_roi = s1_roi_pass(f_pass, f)
    p_ws = ws_roi_pass(p_pass, p, s2r, s2c, s2_pass)
    f_ws = ws_roi_pass(f_pass, f, s2r, s2c, s2_pass)

    if p_pass:
        bucket["p_coin_weight"] += weight
        add_weight(bucket["p_hist_1phd"], math.floor(p / S1_QUANTILE_WIDTH_PHD), weight)
        add_weight(bucket["p_hist_10phd"], math.floor(p / S1_HIST_WIDTH_PHD), weight)
        if p > 500.0:
            add_weight(bucket["p_upper_hist_10phd"], math.floor(p / S1_HIST_WIDTH_PHD), weight)
        for threshold in S1_THRESHOLDS_PHD:
            if p > threshold:
                bucket["p_tail_weight"][threshold] += weight
    if f_pass:
        bucket["f_coin_weight"] += weight
        add_weight(bucket["f_hist_1phd"], math.floor(f / S1_QUANTILE_WIDTH_PHD), weight)
        add_weight(bucket["f_hist_10phd"], math.floor(f / S1_HIST_WIDTH_PHD), weight)
        if f > 500.0:
            add_weight(bucket["f_upper_hist_10phd"], math.floor(f / S1_HIST_WIDTH_PHD), weight)
        for threshold in S1_THRESHOLDS_PHD:
            if f > threshold:
                bucket["f_tail_weight"][threshold] += weight
    if p_roi:
        bucket["p_s1_roi_weight"] += weight
    if f_roi:
        bucket["f_s1_roi_weight"] += weight
    if p_ws:
        bucket["p_ws_roi_weight"] += weight
    if f_ws:
        bucket["f_ws_roi_weight"] += weight
    if p_roi and not f_roi:
        bucket["p_only_s1_roi_weight"] += weight
    if f_roi and not p_roi:
        bucket["f_only_s1_roi_weight"] += weight
    if p_ws and not f_ws:
        bucket["p_only_ws_roi_weight"] += weight
    if f_ws and not p_ws:
        bucket["f_only_ws_roi_weight"] += weight

    if p_pass and f_pass:
        if p <= 600.0 and f > 600.0:
            bucket["p_to_f_cross_600_weight"] += weight
        if f <= 600.0 and p > 600.0:
            bucket["f_to_p_cross_600_weight"] += weight

    for threshold in S1_THRESHOLDS_PHD:
        bucket["paired_tail_difference_weight"][threshold] += weight * (
            int(f_pass and f > threshold) - int(p_pass and p > threshold)
        )

    if s2_pass and s2c > 0.0:
        log_s2 = math.log10(s2c)
        s2_bin = math.floor(log_s2 / grid.LOG10_S2_BIN_WIDTH + 1e-12)
        if p_pass and p > 0.0:
            cell = (math.floor(p / grid.S1_BIN_WIDTH_PHD), s2_bin)
            add_weight(bucket["p_nest_map"], cell, weight)
        if f_pass and f > 0.0:
            cell = (math.floor(f / grid.S1_BIN_WIDTH_PHD), s2_bin)
            add_weight(bucket["f_nest_map"], cell, weight)
    if p_ws:
        cell = (
            math.floor(p / grid.S1_BIN_WIDTH_PHD),
            math.floor(math.log10(s2c) / grid.LOG10_S2_BIN_WIDTH + 1e-12),
        )
        add_weight(bucket["p_ws_map"], cell, weight)
    if f_ws:
        cell = (
            math.floor(f / grid.S1_BIN_WIDTH_PHD),
            math.floor(math.log10(s2c) / grid.LOG10_S2_BIN_WIDTH + 1e-12),
        )
        add_weight(bucket["f_ws_map"], cell, weight)


def seed_record(seed: int, model: str, band: str, bucket: dict) -> dict:
    raw = bucket["raw_weight"]
    p_coin, f_coin = bucket["p_coin_weight"], bucket["f_coin_weight"]
    p_s1, f_s1 = bucket["p_s1_roi_weight"], bucket["f_s1_roi_weight"]
    p_ws, f_ws = bucket["p_ws_roi_weight"], bucket["f_ws_roi_weight"]
    if raw <= 0.0:
        raise ValueError(f"{seed}/{model}/{band}: zero physical signal weight")
    if p_coin <= 0.0 or f_coin <= 0.0:
        raise ValueError(f"{seed}/{model}/{band}: empty S1-coincidence distribution")

    record = {
        "seed": seed, "nuclear_model": model, "energy_band": band,
        "n_generated": bucket["n_events"], "raw_rate_events_kg_day": raw,
        "parametric_s1_coincidence_efficiency": p_coin / raw,
        "full_s1_coincidence_efficiency": f_coin / raw,
        "parametric_s1_roi_efficiency": p_s1 / raw,
        "full_s1_roi_efficiency": f_s1 / raw,
        "full_vs_parametric_s1_roi_relative_rate_change": (f_s1 - p_s1) / p_s1 if p_s1 else None,
        "parametric_ws_roi_efficiency": p_ws / raw,
        "full_ws_roi_efficiency": f_ws / raw,
        "full_vs_parametric_ws_roi_relative_rate_change": (f_ws - p_ws) / p_ws if p_ws else None,
        "parametric_s1_q90_q95_q99_phd": [
            weighted_quantile_from_hist(bucket["p_hist_1phd"], q) for q in (0.90, 0.95, 0.99)
        ],
        "full_s1_q90_q95_q99_phd": [
            weighted_quantile_from_hist(bucket["f_hist_1phd"], q) for q in (0.90, 0.95, 0.99)
        ],
        "parametric_fraction_above_threshold_given_coincidence": {
            str(t): bucket["p_tail_weight"][t] / p_coin for t in S1_THRESHOLDS_PHD
        },
        "full_fraction_above_threshold_given_coincidence": {
            str(t): bucket["f_tail_weight"][t] / f_coin for t in S1_THRESHOLDS_PHD
        },
        "paired_tail_difference_full_minus_parametric_over_raw_weight": {
            str(t): bucket["paired_tail_difference_weight"][t] / raw for t in S1_THRESHOLDS_PHD
        },
        "s1_conditional_histogram_tv_10phd": total_variation(
            bucket["p_hist_10phd"], bucket["f_hist_10phd"]
        ),
        "s1_upper_tail_histogram_tv_10phd_given_s1_gt_500": total_variation(
            bucket["p_upper_hist_10phd"], bucket["f_upper_hist_10phd"]
        ),
        "nest_stage_2d_tv_10phd_0p02dex": total_variation(
            bucket["p_nest_map"], bucket["f_nest_map"]
        ),
        "ws_roi_2d_tv_10phd_0p02dex": total_variation(
            bucket["p_ws_map"], bucket["f_ws_map"]
        ),
        "both_modes_s1_coincidence_cross_600_phd_p_to_f_weight_fraction": (
            bucket["p_to_f_cross_600_weight"] / raw
        ),
        "both_modes_s1_coincidence_cross_600_phd_f_to_p_weight_fraction": (
            bucket["f_to_p_cross_600_weight"] / raw
        ),
        "parametric_only_s1_roi_weight_fraction": bucket["p_only_s1_roi_weight"] / raw,
        "full_only_s1_roi_weight_fraction": bucket["f_only_s1_roi_weight"] / raw,
        "parametric_only_ws_roi_weight_fraction": bucket["p_only_ws_roi_weight"] / raw,
        "full_only_ws_roi_weight_fraction": bucket["f_only_ws_roi_weight"] / raw,
        "_p_hist_10phd": dict(bucket["p_hist_10phd"]),
        "_f_hist_10phd": dict(bucket["f_hist_10phd"]),
        "_p_upper_hist_10phd": dict(bucket["p_upper_hist_10phd"]),
        "_f_upper_hist_10phd": dict(bucket["f_upper_hist_10phd"]),
        "_p_nest_map": dict(bucket["p_nest_map"]),
        "_f_nest_map": dict(bucket["f_nest_map"]),
        "_p_ws_map": dict(bucket["p_ws_map"]),
        "_f_ws_map": dict(bucket["f_ws_map"]),
    }
    return record


def summarize_band(records: list[dict], model: str, band: str, bootstrap_replicates: int) -> dict:
    if len(records) < SEED_COUNT_MIN:
        raise ValueError("at least three independent seeds are required for the ensemble audit")
    records = sorted(records, key=lambda row: row["seed"])
    def values(key):
        return [float(row[key]) for row in records]
    p_hist = [row["_p_hist_10phd"] for row in records]
    f_hist = [row["_f_hist_10phd"] for row in records]
    p_upper = [row["_p_upper_hist_10phd"] for row in records]
    f_upper = [row["_f_upper_hist_10phd"] for row in records]
    p_nest = [row["_p_nest_map"] for row in records]
    f_nest = [row["_f_nest_map"] for row in records]
    p_ws = [row["_p_ws_map"] for row in records]
    f_ws = [row["_f_ws_map"] for row in records]

    seed_tv = [row["s1_conditional_histogram_tv_10phd"] for row in records]
    seed_upper_tv = [row["s1_upper_tail_histogram_tv_10phd_given_s1_gt_500"] for row in records]
    seed_nest_tv = [row["nest_stage_2d_tv_10phd_0p02dex"] for row in records]
    seed_ws_tv = [row["ws_roi_2d_tv_10phd_0p02dex"] for row in records]

    result = {
        "nuclear_model": model,
        "energy_band": band,
        "n_independent_seeds": len(records),
        "raw_rate_mean_events_kg_day": statistics.fmean(values("raw_rate_events_kg_day")),
        "parametric_s1_roi_efficiency_mean": statistics.fmean(values("parametric_s1_roi_efficiency")),
        "full_s1_roi_efficiency_mean": statistics.fmean(values("full_s1_roi_efficiency")),
        "s1_roi_efficiency_difference_full_minus_parametric": scalar_stats([
            row["full_s1_roi_efficiency"] - row["parametric_s1_roi_efficiency"] for row in records
        ]),
        "s1_roi_relative_rate_change": scalar_stats(values("full_vs_parametric_s1_roi_relative_rate_change")),
        "parametric_ws_roi_efficiency_mean": statistics.fmean(values("parametric_ws_roi_efficiency")),
        "full_ws_roi_efficiency_mean": statistics.fmean(values("full_ws_roi_efficiency")),
        "ws_roi_relative_rate_change": scalar_stats(values("full_vs_parametric_ws_roi_relative_rate_change")),
        "ensemble_mean_s1_conditional_histogram_tv_10phd": total_variation(
            mean_normalized_map(p_hist), mean_normalized_map(f_hist)
        ),
        "ensemble_mean_s1_conditional_histogram_tv_cluster_bootstrap_95pct_ci": bootstrap_tv_interval(
            p_hist, f_hist, bootstrap_replicates, BOOTSTRAP_SEED + len(band)
        ),
        "mean_per_seed_s1_conditional_histogram_tv_10phd": statistics.fmean(seed_tv),
        "sd_per_seed_s1_conditional_histogram_tv_10phd": statistics.stdev(seed_tv),
        "ensemble_mean_s1_upper_tail_histogram_tv_10phd_given_s1_gt_500": total_variation(
            mean_normalized_map(p_upper), mean_normalized_map(f_upper)
        ),
        "ensemble_mean_s1_upper_tail_histogram_tv_cluster_bootstrap_95pct_ci": bootstrap_tv_interval(
            p_upper, f_upper, bootstrap_replicates, BOOTSTRAP_SEED + 100 + len(band)
        ),
        "mean_per_seed_s1_upper_tail_histogram_tv_10phd": statistics.fmean(seed_upper_tv),
        "sd_per_seed_s1_upper_tail_histogram_tv_10phd": statistics.stdev(seed_upper_tv),
        "ensemble_mean_nest_stage_2d_tv_10phd_0p02dex": total_variation(
            mean_normalized_map(p_nest), mean_normalized_map(f_nest)
        ),
        "mean_per_seed_nest_stage_2d_tv_10phd_0p02dex": statistics.fmean(seed_nest_tv),
        "ensemble_mean_ws_roi_2d_tv_10phd_0p02dex": total_variation(
            mean_normalized_map(p_ws), mean_normalized_map(f_ws)
        ),
        "mean_per_seed_ws_roi_2d_tv_10phd_0p02dex": statistics.fmean(seed_ws_tv),
        "both_modes_cross_600_phd_parametric_under_full_over_mean_weight_fraction": statistics.fmean(
            values("both_modes_s1_coincidence_cross_600_phd_p_to_f_weight_fraction")
        ),
        "both_modes_cross_600_phd_full_under_parametric_over_mean_weight_fraction": statistics.fmean(
            values("both_modes_s1_coincidence_cross_600_phd_f_to_p_weight_fraction")
        ),
        "parametric_only_s1_roi_mean_weight_fraction": statistics.fmean(values("parametric_only_s1_roi_weight_fraction")),
        "full_only_s1_roi_mean_weight_fraction": statistics.fmean(values("full_only_s1_roi_weight_fraction")),
        "parametric_only_ws_roi_mean_weight_fraction": statistics.fmean(values("parametric_only_ws_roi_weight_fraction")),
        "full_only_ws_roi_mean_weight_fraction": statistics.fmean(values("full_only_ws_roi_weight_fraction")),
        "parametric_s1_q90_q95_q99_phd_mean": [
            statistics.fmean(row["parametric_s1_q90_q95_q99_phd"][i] for row in records) for i in range(3)
        ],
        "full_s1_q90_q95_q99_phd_mean": [
            statistics.fmean(row["full_s1_q90_q95_q99_phd"][i] for row in records) for i in range(3)
        ],
        "mean_parametric_fraction_above_threshold_given_coincidence": {},
        "mean_full_fraction_above_threshold_given_coincidence": {},
        "paired_tail_difference_full_minus_parametric_over_raw_weight": {},
    }
    for threshold in S1_THRESHOLDS_PHD:
        key = str(threshold)
        result["mean_parametric_fraction_above_threshold_given_coincidence"][key] = statistics.fmean(
            row["parametric_fraction_above_threshold_given_coincidence"][key] for row in records
        )
        result["mean_full_fraction_above_threshold_given_coincidence"][key] = statistics.fmean(
            row["full_fraction_above_threshold_given_coincidence"][key] for row in records
        )
        result["paired_tail_difference_full_minus_parametric_over_raw_weight"][key] = scalar_stats([
            row["paired_tail_difference_full_minus_parametric_over_raw_weight"][key] for row in records
        ])
    return result


def run_audit(args: argparse.Namespace) -> tuple[list[dict], list[dict], dict]:
    if len(args.seeds) < SEED_COUNT_MIN or len(set(args.seeds)) != len(args.seeds):
        raise ValueError("provide at least three distinct independent seed labels")
    expected_bins = len(grid.make_edges(ENERGY_MIN_KEV, ENERGY_MAX_KEV, ENERGY_BIN_WIDTH_KEV)) - 1
    if expected_bins != 235:
        raise AssertionError(f"unexpected 1-keV production grid: {expected_bins} bins")

    spectra = {}
    spectrum_path = args.spectrum_dir / BENCHMARK / "natural_xenon_continuous_spectrum.csv"
    for model in NUCLEAR_MODELS:
        spectra[model] = grid.read_spectrum(spectrum_path, model)

    seed_records = []
    total_events = 0
    max_weight_closure_relative_residual = 0.0
    for seed in args.seeds:
        event_path = args.seed_root / f"seed-{seed}" / "paired_s1_mode_2d_events.csv"
        if not event_path.is_file():
            raise FileNotFoundError(event_path)
        buckets = {
            (model, band): new_bucket()
            for model in NUCLEAR_MODELS for band in ENERGY_BANDS_KEV
        }

        # Reuse the exact per-bin integrated rates produced by the original fold.
        fold_path = args.seed_root / f"seed-{seed}" / "fold" / "paired_s1_mode_2d_response_by_energy_bin.csv"
        if not fold_path.is_file():
            raise FileNotFoundError(fold_path)
        exact_bin_rates = {model: {} for model in NUCLEAR_MODELS}
        with fold_path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row["benchmark"] != BENCHMARK or row["nuclear_model"] not in NUCLEAR_MODELS:
                    continue
                model = row["nuclear_model"]
                ibin = int(row["energy_bin_index"])
                if ibin in exact_bin_rates[model]:
                    raise ValueError(f"{fold_path}: duplicate exact-rate row for {model}/{ibin}")
                if int(row["n_events"]) != EVENTS_PER_BIN:
                    raise ValueError(f"{fold_path}: wrong event count for {model}/{ibin}")
                exact_bin_rates[model][ibin] = float(row["exact_raw_rate_events_kg_day"])
        for model in NUCLEAR_MODELS:
            if len(exact_bin_rates[model]) != expected_bins:
                raise ValueError(f"{fold_path}: expected {expected_bins} exact-rate bins for {model}")

        # First pass: sum dR/dER(E_i) over all 2,000 events in each stratum.
        # This is the same denominator used by the original paired 2D fold.
        sum_differential = {model: defaultdict(float) for model in NUCLEAR_MODELS}
        with event_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"{event_path} missing columns: {sorted(missing)}")
            for row in reader:
                ibin = int(row["energy_bin_index"])
                energy = float(row["energy_keV"])
                for model in NUCLEAR_MODELS:
                    differential = grid.interpolate(energy, spectra[model][0], spectra[model][1])
                    if not math.isfinite(differential) or differential < 0.0:
                        raise ValueError(f"{event_path}: invalid dR/dER for {model}/{ibin}")
                    sum_differential[model][ibin] += differential

        # Second pass: normalize each event's interpolated spectrum weight to the
        # exact integral of its 1-keV stratum. This reproduces the original fold:
        # w_i = R_bin_exact * f(E_i) / sum_j f(E_j).
        bin_counts = defaultdict(int)
        replica_counts = defaultdict(int)
        bin_weight_sums = {model: defaultdict(float) for model in NUCLEAR_MODELS}
        n_events = 0
        with event_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                event = int(row["event"])
                if event != n_events:
                    raise ValueError(f"{event_path}: non-sequential event index {event}, expected {n_events}")
                n_events += 1
                ibin = int(row["energy_bin_index"])
                replica = int(row["replica"])
                if not 0 <= ibin < expected_bins or replica not in (0, 1):
                    raise ValueError(f"{event_path}: invalid energy-bin/replica label {ibin}/{replica}")
                bin_counts[ibin] += 1
                replica_counts[(ibin, replica)] += 1
                energy = float(row["energy_keV"])
                low = float(row["energy_bin_low_keV"])
                high = float(row["energy_bin_high_keV"])
                if not (math.isfinite(energy) and low <= energy <= high and high > low):
                    raise ValueError(f"{event_path}: invalid energy coordinate at event {event}")
                p_signed = float(row["s1_param_signed_phd"])
                f_signed = float(row["s1_full_signed_phd"])
                s2_signed = float(row["s2_signed_phd"])
                p_pass = int(row["s1_param_pass"])
                f_pass = int(row["s1_full_pass"])
                s2_pass = int(row["s2_threshold_pass"])
                if any(flag not in (0, 1) for flag in (p_pass, f_pass, s2_pass)):
                    raise ValueError(f"{event_path}: non-binary selection flag at event {event}")
                if (p_signed > 0.0) != bool(p_pass) or (f_signed > 0.0) != bool(f_pass):
                    raise ValueError(f"{event_path}: S1 sign/pass mismatch at event {event}")
                if (s2_signed > 0.0) != bool(s2_pass):
                    raise ValueError(f"{event_path}: S2 sign/pass mismatch at event {event}")
                if energy < min(low, high) or energy > max(low, high):
                    raise ValueError(f"{event_path}: event energy outside its stratum at event {event}")

                weights = {}
                for model in NUCLEAR_MODELS:
                    differential = grid.interpolate(energy, spectra[model][0], spectra[model][1])
                    weight = normalized_stratum_event_weight(
                        exact_bin_rates[model][ibin],
                        differential,
                        sum_differential[model][ibin],
                    )
                    weights[model] = weight
                    bin_weight_sums[model][ibin] += weight

                active_bands = [
                    band for band, (band_low, band_high) in ENERGY_BANDS_KEV.items()
                    if in_band(energy, band_low, band_high)
                ]
                for model, weight in weights.items():
                    for band in active_bands:
                        update_bucket(buckets[(model, band)], row, weight)

        if n_events != EVENTS_PER_SEED:
            raise ValueError(f"{event_path}: expected {EVENTS_PER_SEED} events, found {n_events}")
        if len(bin_counts) != expected_bins or any(bin_counts[i] != EVENTS_PER_BIN for i in range(expected_bins)):
            raise ValueError(f"{event_path}: expected {EVENTS_PER_BIN} events in each of {expected_bins} energy bins")
        if any(replica_counts[(i, replica)] != REPLICAS_PER_BIN
               for i in range(expected_bins) for replica in (0, 1)):
            raise ValueError(f"{event_path}: replica split is not {REPLICAS_PER_BIN}/{REPLICAS_PER_BIN} in every energy bin")
        for model in NUCLEAR_MODELS:
            for ibin in range(expected_bins):
                exact_rate = exact_bin_rates[model][ibin]
                observed_rate = bin_weight_sums[model][ibin]
                tolerance = 5e-12 * max(abs(exact_rate), 1e-300)
                if abs(observed_rate - exact_rate) > tolerance:
                    raise ValueError(
                        f"{seed}/{model}/{ibin}: stratum weight closure failed; "
                        f"observed={observed_rate:.17g}, exact={exact_rate:.17g}"
                    )
                max_weight_closure_relative_residual = max(
                    max_weight_closure_relative_residual,
                    abs(observed_rate - exact_rate) / max(abs(exact_rate), 1e-300)
                    if exact_rate > 0.0 else abs(observed_rate),
                )
        total_events += n_events
        for model in NUCLEAR_MODELS:
            for band in ENERGY_BANDS_KEV:
                seed_records.append(seed_record(seed, model, band, buckets[(model, band)]))

    per_seed_rows = []
    threshold_rows = []
    summary_rows = []
    json_summary = {}
    for model in NUCLEAR_MODELS:
        json_summary[model] = {}
        for band in ENERGY_BANDS_KEV:
            records = [row for row in seed_records if row["nuclear_model"] == model and row["energy_band"] == band]
            summary = summarize_band(records, model, band, args.bootstrap_replicates)
            summary_rows.append(summary)
            json_summary[model][band] = summary
            for row in records:
                clean = {key: value for key, value in row.items() if not key.startswith("_")}
                clean = {
                    key: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value
                    for key, value in clean.items()
                }
                per_seed_rows.append(clean)
                for threshold in S1_THRESHOLDS_PHD:
                    key = str(threshold)
                    threshold_rows.append({
                        "seed": row["seed"], "nuclear_model": model, "energy_band": band,
                        "threshold_phd": threshold,
                        "parametric_fraction_above_threshold_given_coincidence": row["parametric_fraction_above_threshold_given_coincidence"][key],
                        "full_fraction_above_threshold_given_coincidence": row["full_fraction_above_threshold_given_coincidence"][key],
                        "paired_tail_difference_full_minus_parametric_over_raw_weight": row["paired_tail_difference_full_minus_parametric_over_raw_weight"][key],
                    })

    metadata = {
        "study": "ten-seed paired S1 upper-tail and ROI-migration audit",
        "status": "TEN_SEED_BLACK_S1_UPPER_TAIL_DIAGNOSTIC_ONLY",
        "benchmark": BENCHMARK,
        "source_production_run_id": 43750948249,
        "source_artifact_id": 14176882910,
        "source_artifact_zip_sha256": "606397d9eac594008630a18b97f1e72fbbfa1d157e34779de7ce5fd0fe5b8cb5",
        "seed_count": len(args.seeds),
        "seeds": args.seeds,
        "events_per_seed": EVENTS_PER_SEED,
        "total_events_audited": total_events,
        "energy_grid_keV": [ENERGY_MIN_KEV, ENERGY_MAX_KEV, ENERGY_BIN_WIDTH_KEV],
        "events_per_energy_stratum": EVENTS_PER_BIN,
        "replicas_per_stratum": [REPLICAS_PER_BIN, REPLICAS_PER_BIN],
        "nuclear_models": list(NUCLEAR_MODELS),
        "response_model": "EFT2024",
        "nest_commit": grid.NEST_COMMIT,
        "detector_configuration": "LZ_Detector_2024::SetEFT2024Configuration",
        "event_weighting": (
            "Within each seed, nuclear model, and 1-keV true-energy stratum, event i receives "
            "w_i = R_bin_exact * f(E_i) / sum_j f(E_j), where f(E)=grid.interpolate(E,xs,ys) "
            "and R_bin_exact is read from that seed's original fold response-by-energy-bin CSV. "
            "This exactly reproduces the original fold's event-weight normalization; GCN and "
            "JJ55 are folded separately."
        ),
        "stratum_weight_closure": {
            "max_relative_residual_across_all_seeds_models_bins": max_weight_closure_relative_residual,
            "tolerance": "5e-12 relative to exact per-bin integrated rate",
            "required_identity": "sum_i w_i = R_bin_exact for every seed, nuclear model, and 1-keV stratum"
        },
        "pairing": (
            "Each event shares the same NR quanta, true recoil energy, true position, and "
            "S2 draw between Parametric and Full S1; the two S1 response modes use separate "
            "deterministic NEST random streams."
        ),
        "energy_bands_keV": {
            key: list(value) for key, value in ENERGY_BANDS_KEV.items()
        },
        "s1_coincidence": "Pinned NEST GetS1 sign/pass flag; no substitute threshold is imposed.",
        "s1_roi_phd": [grid.S1_MIN_PHD, grid.S1_MAX_PHD],
        "ws_roi": {
            "s1c_phd": [grid.S1_MIN_PHD, grid.S1_MAX_PHD],
            "s2_raw_min_phd_strict": grid.S2_RAW_MIN_PHD,
            "log10_s2c": [grid.LOG10_S2C_MIN, grid.LOG10_S2C_MAX],
            "s2_threshold": "Pinned NEST GetS2 sign/pass flag",
        },
        "s1_histogram": {
            "full_distribution_bin_width_phd": S1_HIST_WIDTH_PHD,
            "upper_tail_condition": "S1c > 500 phd",
            "upper_tail_bin_width_phd": S1_HIST_WIDTH_PHD,
            "quantile_histogram_bin_width_phd": S1_QUANTILE_WIDTH_PHD,
            "thresholds_phd": list(S1_THRESHOLDS_PHD),
        },
        "bootstrap": {
            "unit": "independent production seed; paired Parametric/Full maps remain together",
            "replicates": args.bootstrap_replicates,
            "seed": BOOTSTRAP_SEED,
            "interpretation": "cluster bootstrap interval for descriptive histogram TV, not a detector-systematic interval or formal equivalence proof",
        },
        "uncertainty_interpretation": (
            "Student-t intervals are based on the ten independent production-level seed "
            "estimates. Bootstrap intervals resample whole paired seeds. Neither includes "
            "NEST model uncertainty, detector calibration uncertainty, or official LZ "
            "waveform/selection covariance."
        ),
        "spatial_prior": (
            "Uniform active-TPC cylinder proxy from the source production; not the official "
            "4.71-tonne fiducial-volume or calibration-source geometry."
        ),
        "limitations": [
            "NEST Full S1 is a PMT/time-window response model, not official LZ waveform-level reconstruction.",
            "The S1-only [3,600] phd acceptance is reported separately from the full WS ROI, which also uses the common S2 threshold and S2c/S2raw boundaries.",
            "DAQ trigger, SS reconstruction, data-analysis cuts, official fiducial-volume mask, Skin/OD veto, and live-time migration are not included.",
            "The 1-phd quantile histogram and 10-phd TV histogram are descriptive summaries; the native event samples remain the primary record.",
            "Ten independent seeds quantify production-level Monte Carlo variation but do not establish Parametric/Full statistical equivalence.",
            "No detector-systematic covariance or profile likelihood is constructed."
        ],
        "n_summary_rows": len(summary_rows),
        "n_per_seed_rows": len(per_seed_rows),
        "n_threshold_rows": len(threshold_rows),
        "summary": json_summary,
    }
    return summary_rows, per_seed_rows, threshold_rows, metadata


def write_outputs(
    summary_rows: list[dict], per_seed_rows: list[dict],
    threshold_rows: list[dict], metadata: dict, out_dir: Path
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = [
        ("black_s1_upper_tail_summary.csv", summary_rows),
        ("black_s1_upper_tail_per_seed.csv", per_seed_rows),
        ("black_s1_upper_tail_thresholds.csv", threshold_rows),
    ]
    for filename, rows in outputs:
        if not rows:
            raise ValueError(f"refusing to write empty output: {filename}")
        with (out_dir / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    (out_dir / "black_s1_upper_tail_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-root", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", required=True)
    parser.add_argument(
        "--spectrum-dir", type=Path,
        default=Path("research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum")
    )
    parser.add_argument("--bootstrap-replicates", type=int, default=BOOTSTRAP_REPLICATES_DEFAULT)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    summary, per_seed, thresholds, metadata = run_audit(args)
    write_outputs(summary, per_seed, thresholds, metadata, args.out_dir)
    print(json.dumps({
        "status": metadata["status"],
        "seed_count": metadata["seed_count"],
        "total_events_audited": metadata["total_events_audited"],
        "n_summary_rows": len(summary),
        "n_per_seed_rows": len(per_seed),
        "n_threshold_rows": len(thresholds),
        "outputs": [
            "black_s1_upper_tail_summary.csv",
            "black_s1_upper_tail_per_seed.csv",
            "black_s1_upper_tail_thresholds.csv",
            "black_s1_upper_tail_metadata.json",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
