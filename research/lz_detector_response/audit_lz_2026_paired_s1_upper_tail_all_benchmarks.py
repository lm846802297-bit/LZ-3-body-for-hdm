#!/usr/bin/env python3
"""Ten-seed paired S1 upper-tail audit for all four LZ three-body benchmarks.

The immutable NEST event sample is reused. Only the benchmark-specific
three-body recoil-spectrum weights change.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import audit_lz_2026_paired_s1_upper_tail as base
import converge_lz_2026_three_body_energy_grid as grid

BENCHMARKS = (
    "red_ms200_dm1",
    "green_ms300_dm1",
    "black_ms360_dm1",
    "blue_ms300_dm10",
)
ENERGY_BAND_CANDIDATES_KEV = {
    "common_support_205_269p9": (205.0, 269.9),
    "band_205_225": (205.0, 225.0),
    "band_225_240": (225.0, 240.0),
    "band_240_255": (240.0, 255.0),
    "band_255_269p9": (255.0, 269.9),
}
OUTPUT_FILES = {
    "summary": "multi_benchmark_s1_upper_tail_summary.csv",
    "per_seed": "multi_benchmark_s1_upper_tail_per_seed.csv",
    "thresholds": "multi_benchmark_s1_upper_tail_thresholds.csv",
    "metadata": "multi_benchmark_s1_upper_tail_metadata.json",
}


def bin_edges(index: int) -> tuple[float, float]:
    low = base.ENERGY_MIN_KEV + index * base.ENERGY_BIN_WIDTH_KEV
    high = min(low + base.ENERGY_BIN_WIDTH_KEV, base.ENERGY_MAX_KEV)
    return low, high


def build_benchmark_energy_bands(exact_bin_rates: dict) -> tuple[list[int], dict]:
    """Derive each benchmark's physical support and non-empty comparison bands."""
    support_by_model = {
        model: {
            index for index, rate in rates.items()
            if math.isfinite(rate) and rate > 0.0
        }
        for model, rates in exact_bin_rates.items()
    }
    if not support_by_model:
        raise ValueError("no nuclear-model rates supplied")
    support_sets = list(support_by_model.values())
    if any(support != support_sets[0] for support in support_sets[1:]):
        raise ValueError("GCN/JJ55 non-zero recoil supports do not match")
    support_bins = sorted(support_sets[0])
    if not support_bins:
        raise ValueError("benchmark has no non-zero recoil-rate support")
    if support_bins != list(range(support_bins[0], support_bins[-1] + 1)):
        raise ValueError("benchmark recoil support is not contiguous")
    support_low = bin_edges(support_bins[0])[0]
    support_high = bin_edges(support_bins[-1])[1]
    bands = {"full_support": (support_low, support_high)}

    for name, (low, high) in ENERGY_BAND_CANDIDATES_KEV.items():
        if low < support_low or high > support_high:
            continue
        model_rates = []
        for rates in exact_bin_rates.values():
            total = math.fsum(
                rate for index, rate in rates.items()
                if bin_edges(index)[0] >= low - 1e-12
                and bin_edges(index)[1] <= high + 1e-12
            )
            model_rates.append(total)
        if any(value > 0.0 for value in model_rates):
            if not all(value > 0.0 for value in model_rates):
                raise ValueError(f"{name}: GCN/JJ55 band support does not match")
            bands[name] = (low, high)

    if "common_support_205_269p9" not in bands:
        raise ValueError("benchmark has no common 205--269.9 keV comparison support")
    return support_bins, bands


def new_selection_audit() -> dict:
    return {
        "n_events": 0,
        "parametric_s1_coincidence_pass": 0,
        "full_s1_coincidence_pass": 0,
        "s2_threshold_pass": 0,
        "s2_raw_roi_pass": 0,
        "s2c_roi_pass": 0,
        "combined_s2_roi_pass": 0,
        "parametric_s1_roi_events_failing_s2_roi": 0,
        "full_s1_roi_events_failing_s2_roi": 0,
        "s2_raw_min_phd": math.inf,
        "s2c_min_phd": math.inf,
        "s2c_max_phd": -math.inf,
    }


def update_selection_audit(audit: dict, row: dict) -> None:
    p_abs = float(row["s1_param_abs_phd"])
    f_abs = float(row["s1_full_abs_phd"])
    s2c = float(row["s2_abs_phd"])
    s2r = float(row["s2_raw_phd"])
    p_pass = bool(int(row["s1_param_pass"]))
    f_pass = bool(int(row["s1_full_pass"]))
    s2_pass = bool(int(row["s2_threshold_pass"]))

    s2_raw_pass = s2r > grid.S2_RAW_MIN_PHD
    s2c_pass = (
        s2c > 0.0
        and grid.LOG10_S2C_MIN <= math.log10(s2c) <= grid.LOG10_S2C_MAX
    )
    combined_s2_pass = bool(s2_pass and grid.ws_roi_pass(100.0, s2r, s2c))
    p_roi = base.s1_roi_pass(p_pass, p_abs)
    f_roi = base.s1_roi_pass(f_pass, f_abs)

    audit["n_events"] += 1
    audit["parametric_s1_coincidence_pass"] += int(p_pass)
    audit["full_s1_coincidence_pass"] += int(f_pass)
    audit["s2_threshold_pass"] += int(s2_pass)
    audit["s2_raw_roi_pass"] += int(s2_raw_pass)
    audit["s2c_roi_pass"] += int(s2c_pass)
    audit["combined_s2_roi_pass"] += int(combined_s2_pass)
    audit["parametric_s1_roi_events_failing_s2_roi"] += int(p_roi and not combined_s2_pass)
    audit["full_s1_roi_events_failing_s2_roi"] += int(f_roi and not combined_s2_pass)
    audit["s2_raw_min_phd"] = min(audit["s2_raw_min_phd"], s2r)
    audit["s2c_min_phd"] = min(audit["s2c_min_phd"], s2c)
    audit["s2c_max_phd"] = max(audit["s2c_max_phd"], s2c)


def load_exact_bin_rates(fold_path: Path) -> dict:
    rates = {
        benchmark: {model: {} for model in base.NUCLEAR_MODELS}
        for benchmark in BENCHMARKS
    }
    with fold_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            benchmark = row["benchmark"]
            model = row["nuclear_model"]
            if benchmark not in BENCHMARKS or model not in base.NUCLEAR_MODELS:
                continue
            index = int(row["energy_bin_index"])
            if index in rates[benchmark][model]:
                raise ValueError(f"{fold_path}: duplicate exact-rate row for {benchmark}/{model}/{index}")
            if int(row["n_events"]) != base.EVENTS_PER_BIN:
                raise ValueError(f"{fold_path}: wrong event count for {benchmark}/{model}/{index}")
            value = float(row["exact_raw_rate_events_kg_day"])
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"{fold_path}: invalid exact rate for {benchmark}/{model}/{index}")
            rates[benchmark][model][index] = value

    expected_bins = len(grid.make_edges(
        base.ENERGY_MIN_KEV, base.ENERGY_MAX_KEV, base.ENERGY_BIN_WIDTH_KEV
    )) - 1
    for benchmark in BENCHMARKS:
        for model in base.NUCLEAR_MODELS:
            if len(rates[benchmark][model]) != expected_bins:
                raise ValueError(
                    f"{fold_path}: expected {expected_bins} rows for {benchmark}/{model}, "
                    f"found {len(rates[benchmark][model])}"
                )
    return rates


def run_audit(args: argparse.Namespace) -> tuple[list[dict], list[dict], list[dict], dict]:
    if len(args.seeds) < base.SEED_COUNT_MIN or len(set(args.seeds)) != len(args.seeds):
        raise ValueError("provide at least three distinct independent seed labels")
    if len(set(args.benchmarks)) != len(args.benchmarks):
        raise ValueError("benchmark list contains duplicates")
    if not args.benchmarks or any(item not in BENCHMARKS for item in args.benchmarks):
        raise ValueError(f"benchmarks must be selected from {BENCHMARKS}")

    expected_bins = len(grid.make_edges(
        base.ENERGY_MIN_KEV, base.ENERGY_MAX_KEV, base.ENERGY_BIN_WIDTH_KEV
    )) - 1
    if expected_bins != 235:
        raise AssertionError(f"unexpected 1-keV production grid: {expected_bins} bins")

    spectra = {
        benchmark: {
            model: grid.read_spectrum(
                args.spectrum_dir / benchmark / "natural_xenon_continuous_spectrum.csv",
                model,
            )
            for model in base.NUCLEAR_MODELS
        }
        for benchmark in args.benchmarks
    }

    support_bins_by_benchmark = {}
    bands_by_benchmark = {}
    support_bounds_by_benchmark = {}
    support_selection_audit = {
        benchmark: new_selection_audit() for benchmark in args.benchmarks
    }
    seed_records = []
    total_events = 0
    max_weight_closure_relative_residual = 0.0
    closure_checks = 0

    for seed in args.seeds:
        event_path = args.seed_root / f"seed-{seed}" / "paired_s1_mode_2d_events.csv"
        fold_path = args.seed_root / f"seed-{seed}" / "fold" / "paired_s1_mode_2d_response_by_energy_bin.csv"
        if not event_path.is_file():
            raise FileNotFoundError(event_path)
        if not fold_path.is_file():
            raise FileNotFoundError(fold_path)

        exact_rates_all = load_exact_bin_rates(fold_path)
        exact_rates = {
            benchmark: exact_rates_all[benchmark] for benchmark in args.benchmarks
        }
        for benchmark in args.benchmarks:
            support_bins, bands = build_benchmark_energy_bands(exact_rates[benchmark])
            if benchmark not in support_bins_by_benchmark:
                support_bins_by_benchmark[benchmark] = support_bins
                bands_by_benchmark[benchmark] = bands
                support_bounds_by_benchmark[benchmark] = bands["full_support"]
            elif support_bins_by_benchmark[benchmark] != support_bins or bands_by_benchmark[benchmark] != bands:
                raise ValueError(f"{seed}/{benchmark}: recoil support or energy bands changed across seeds")

        buckets = {
            (benchmark, model, band): base.new_bucket()
            for benchmark in args.benchmarks
            for model in base.NUCLEAR_MODELS
            for band in bands_by_benchmark[benchmark]
        }

        # First pass: reproduce the exact fold's per-stratum dR/dER denominator
        # for every benchmark and nuclear response, using the same interpolation.
        sum_differential = {
            (benchmark, model): defaultdict(float)
            for benchmark in args.benchmarks for model in base.NUCLEAR_MODELS
        }
        with event_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            missing = base.REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"{event_path} missing columns: {sorted(missing)}")
            for row in reader:
                index = int(row["energy_bin_index"])
                energy = float(row["energy_keV"])
                for benchmark in args.benchmarks:
                    for model in base.NUCLEAR_MODELS:
                        xs, ys = spectra[benchmark][model]
                        differential = grid.interpolate(energy, xs, ys)
                        if not math.isfinite(differential) or differential < 0.0:
                            raise ValueError(
                                f"{event_path}: invalid dR/dER for {benchmark}/{model}/{index}"
                            )
                        sum_differential[(benchmark, model)][index] += differential

        bin_counts = defaultdict(int)
        replica_counts = defaultdict(int)
        bin_weight_sums = {
            (benchmark, model): defaultdict(float)
            for benchmark in args.benchmarks for model in base.NUCLEAR_MODELS
        }
        n_events = 0
        with event_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                event = int(row["event"])
                if event != n_events:
                    raise ValueError(f"{event_path}: non-sequential event index {event}, expected {n_events}")
                n_events += 1
                index = int(row["energy_bin_index"])
                replica = int(row["replica"])
                if not 0 <= index < expected_bins or replica not in (0, 1):
                    raise ValueError(f"{event_path}: invalid energy-bin/replica label {index}/{replica}")
                bin_counts[index] += 1
                replica_counts[(index, replica)] += 1
                energy = float(row["energy_keV"])
                low = float(row["energy_bin_low_keV"])
                high = float(row["energy_bin_high_keV"])
                if not (math.isfinite(energy) and low <= energy <= high and high > low):
                    raise ValueError(f"{event_path}: invalid energy coordinate at event {event}")
                p_signed = float(row["s1_param_signed_phd"])
                f_signed = float(row["s1_full_signed_phd"])
                s2_signed = float(row["s2_signed_phd"])
                p_abs = float(row["s1_param_abs_phd"])
                f_abs = float(row["s1_full_abs_phd"])
                s2c = float(row["s2_abs_phd"])
                s2r = float(row["s2_raw_phd"])
                p_pass = int(row["s1_param_pass"])
                f_pass = int(row["s1_full_pass"])
                s2_pass = int(row["s2_threshold_pass"])
                if any(flag not in (0, 1) for flag in (p_pass, f_pass, s2_pass)):
                    raise ValueError(f"{event_path}: non-binary selection flag at event {event}")
                if (p_signed > 0.0) != bool(p_pass) or (f_signed > 0.0) != bool(f_pass):
                    raise ValueError(f"{event_path}: S1 sign/pass mismatch at event {event}")
                if (s2_signed > 0.0) != bool(s2_pass):
                    raise ValueError(f"{event_path}: S2 sign/pass mismatch at event {event}")
                if not all(math.isfinite(value) for value in (p_abs, f_abs, s2c, s2r)):
                    raise ValueError(f"{event_path}: non-finite absolute response at event {event}")
                if energy < min(low, high) or energy > max(low, high):
                    raise ValueError(f"{event_path}: event energy outside its stratum at event {event}")

                for benchmark in args.benchmarks:
                    if base.in_band(energy, *support_bounds_by_benchmark[benchmark]):
                        update_selection_audit(support_selection_audit[benchmark], row)

                for benchmark in args.benchmarks:
                    for model in base.NUCLEAR_MODELS:
                        xs, ys = spectra[benchmark][model]
                        differential = grid.interpolate(energy, xs, ys)
                        weight = base.normalized_stratum_event_weight(
                            exact_rates[benchmark][model][index],
                            differential,
                            sum_differential[(benchmark, model)][index],
                        )
                        bin_weight_sums[(benchmark, model)][index] += weight
                        for band, (band_low, band_high) in bands_by_benchmark[benchmark].items():
                            if base.in_band(energy, band_low, band_high):
                                base.update_bucket(
                                    buckets[(benchmark, model, band)], row, weight
                                )

        if n_events != base.EVENTS_PER_SEED:
            raise ValueError(f"{event_path}: expected {base.EVENTS_PER_SEED} events, found {n_events}")
        if len(bin_counts) != expected_bins or any(
            bin_counts[index] != base.EVENTS_PER_BIN for index in range(expected_bins)
        ):
            raise ValueError(f"{event_path}: expected {base.EVENTS_PER_BIN} events in each of {expected_bins} bins")
        if any(
            replica_counts[(index, replica)] != base.REPLICAS_PER_BIN
            for index in range(expected_bins) for replica in (0, 1)
        ):
            raise ValueError(f"{event_path}: replica split is not 1000/1000 in every energy bin")

        for benchmark in args.benchmarks:
            for model in base.NUCLEAR_MODELS:
                for index in range(expected_bins):
                    exact_rate = exact_rates[benchmark][model][index]
                    observed_rate = bin_weight_sums[(benchmark, model)][index]
                    tolerance = 5e-12 * max(abs(exact_rate), 1e-300)
                    if abs(observed_rate - exact_rate) > tolerance:
                        raise ValueError(
                            f"{seed}/{benchmark}/{model}/{index}: stratum closure failed; "
                            f"observed={observed_rate:.17g}, exact={exact_rate:.17g}"
                        )
                    max_weight_closure_relative_residual = max(
                        max_weight_closure_relative_residual,
                        abs(observed_rate - exact_rate) / max(abs(exact_rate), 1e-300)
                        if exact_rate > 0.0 else abs(observed_rate),
                    )
                    closure_checks += 1

        total_events += n_events
        for benchmark in args.benchmarks:
            for model in base.NUCLEAR_MODELS:
                for band in bands_by_benchmark[benchmark]:
                    record = base.seed_record(
                        seed, model, band, buckets[(benchmark, model, band)]
                    )
                    record["benchmark"] = benchmark
                    seed_records.append(record)

    for benchmark in args.benchmarks:
        expected_support_events = (
            len(support_bins_by_benchmark[benchmark])
            * base.EVENTS_PER_BIN * len(args.seeds)
        )
        audit = support_selection_audit[benchmark]
        if audit["n_events"] != expected_support_events:
            raise ValueError(
                f"{benchmark}: support event-count closure failed: "
                f"{audit['n_events']} != {expected_support_events}"
            )
        for key in (
            "parametric_s1_coincidence_pass", "full_s1_coincidence_pass",
            "s2_threshold_pass", "s2_raw_roi_pass", "s2c_roi_pass",
            "combined_s2_roi_pass",
        ):
            if not 0 <= audit[key] <= audit["n_events"]:
                raise ValueError(f"{benchmark}: invalid selection count {key}={audit[key]}")
        audit["support_energy_range_keV"] = list(support_bounds_by_benchmark[benchmark])
        audit["support_bin_count"] = len(support_bins_by_benchmark[benchmark])
        audit["expected_support_events"] = expected_support_events
        all_s2_pass = all(
            audit[key] == audit["n_events"]
            for key in (
                "s2_threshold_pass", "s2_raw_roi_pass",
                "s2c_roi_pass", "combined_s2_roi_pass",
            )
        )
        audit["interpretation"] = (
            "All events in this benchmark's non-zero recoil support pass the S2 "
            "threshold and both S2 ROI bounds."
            if all_s2_pass else
            "S2 selection is not fully efficient in this benchmark's non-zero recoil "
            "support; WS-ROI migration must be distinguished from S1-only migration."
        )

    summary_rows = []
    per_seed_rows = []
    threshold_rows = []
    json_summary = {}
    for benchmark in args.benchmarks:
        json_summary[benchmark] = {}
        for model in base.NUCLEAR_MODELS:
            json_summary[benchmark][model] = {}
            for band in bands_by_benchmark[benchmark]:
                records = [
                    row for row in seed_records
                    if row["benchmark"] == benchmark
                    and row["nuclear_model"] == model
                    and row["energy_band"] == band
                ]
                summary = base.summarize_band(
                    records, model, band, args.bootstrap_replicates
                )
                summary["benchmark"] = benchmark
                summary_rows.append(summary)
                json_summary[benchmark][model][band] = summary
                for row in records:
                    clean = {
                        key: value for key, value in row.items()
                        if not key.startswith("_")
                    }
                    per_seed_rows.append(base.csv_safe_row(clean))
                    for threshold in base.S1_THRESHOLDS_PHD:
                        key = str(threshold)
                        threshold_rows.append({
                            "benchmark": benchmark,
                            "seed": row["seed"],
                            "nuclear_model": model,
                            "energy_band": band,
                            "threshold_phd": threshold,
                            "parametric_fraction_above_threshold_given_coincidence":
                                row["parametric_fraction_above_threshold_given_coincidence"][key],
                            "full_fraction_above_threshold_given_coincidence":
                                row["full_fraction_above_threshold_given_coincidence"][key],
                            "paired_tail_difference_full_minus_parametric_over_raw_weight":
                                row["paired_tail_difference_full_minus_parametric_over_raw_weight"][key],
                        })

    metadata = {
        "study": "ten-seed paired S1 upper-tail and ROI-migration audit across all four three-body benchmarks",
        "status": "TEN_SEED_MULTI_BENCHMARK_S1_UPPER_TAIL_DIAGNOSTIC_ONLY",
        "benchmarks": list(args.benchmarks),
        "source_production_run_id": 43750948249,
        "source_artifact_id": 14176882910,
        "source_artifact_zip_sha256": "606397d9eac594008630a18b97f1e72fbbfa1d157e34779de7ce5fd0fe5b8cb5",
        "seed_count": len(args.seeds),
        "seeds": args.seeds,
        "events_per_seed": base.EVENTS_PER_SEED,
        "total_events_audited": total_events,
        "benchmark_weighted_event_instances": total_events * len(args.benchmarks),
        "energy_grid_keV": [
            base.ENERGY_MIN_KEV, base.ENERGY_MAX_KEV, base.ENERGY_BIN_WIDTH_KEV
        ],
        "events_per_energy_stratum": base.EVENTS_PER_BIN,
        "replicas_per_stratum": [base.REPLICAS_PER_BIN, base.REPLICAS_PER_BIN],
        "nuclear_models": list(base.NUCLEAR_MODELS),
        "response_model": "EFT2024",
        "nest_commit": grid.NEST_COMMIT,
        "detector_configuration": "LZ_Detector_2024::SetEFT2024Configuration",
        "event_weighting": (
            "For every benchmark, seed, nuclear model, and 1-keV true-energy stratum, "
            "event i receives w_i = R_bin_exact * f(E_i) / sum_j f(E_j), with f(E) "
            "evaluated by the same grid.interpolate routine as the original fold and "
            "R_bin_exact read from that seed's original response-by-energy-bin CSV. "
            "No NEST events are regenerated. GCN/JJ55 and the four benchmark spectra "
            "are folded independently over the same paired detector-response events."
        ),
        "stratum_weight_closure": {
            "checks": closure_checks,
            "max_relative_residual_across_all_benchmarks_seeds_models_bins":
                max_weight_closure_relative_residual,
            "tolerance": "5e-12 relative to exact per-bin integrated rate",
            "required_identity":
                "sum_i w_i = R_bin_exact for every benchmark, seed, nuclear model, and 1-keV stratum",
        },
        "benchmark_supports": {
            benchmark: {
                "energy_range_keV": list(support_bounds_by_benchmark[benchmark]),
                "support_bin_indices": support_bins_by_benchmark[benchmark],
                "n_support_bins": len(support_bins_by_benchmark[benchmark]),
            }
            for benchmark in args.benchmarks
        },
        "energy_bands_keV": {
            benchmark: {
                band: list(bounds)
                for band, bounds in bands_by_benchmark[benchmark].items()
            }
            for benchmark in args.benchmarks
        },
        "support_selection_audit": support_selection_audit,
        "pairing": (
            "Each event shares the same intrinsic NR quanta, true recoil energy, true "
            "position, and S2 draw between Parametric and Full S1; the two S1 modes use "
            "separate deterministic NEST random streams."
        ),
        "s1_coincidence": "Pinned NEST GetS1 sign/pass flag; no substitute threshold is imposed.",
        "s1_roi_phd": [grid.S1_MIN_PHD, grid.S1_MAX_PHD],
        "ws_roi": {
            "s1c_phd": [grid.S1_MIN_PHD, grid.S1_MAX_PHD],
            "s2_raw_min_phd_strict": grid.S2_RAW_MIN_PHD,
            "log10_s2c": [grid.LOG10_S2C_MIN, grid.LOG10_S2C_MAX],
            "s2_threshold": "Pinned NEST GetS2 sign/pass flag",
        },
        "s1_histogram": {
            "full_distribution_bin_width_phd": base.S1_HIST_WIDTH_PHD,
            "upper_tail_condition": "S1c > 500 phd",
            "upper_tail_bin_width_phd": base.S1_HIST_WIDTH_PHD,
            "quantile_histogram_bin_width_phd": base.S1_QUANTILE_WIDTH_PHD,
            "thresholds_phd": list(base.S1_THRESHOLDS_PHD),
        },
        "bootstrap": {
            "unit": "independent production seed; paired Parametric/Full maps remain together",
            "replicates": args.bootstrap_replicates,
            "seed": base.BOOTSTRAP_SEED,
            "interpretation": (
                "Cluster-bootstrap interval for descriptive histogram TV, not a "
                "detector-systematic interval or formal equivalence proof."
            ),
        },
        "uncertainty_interpretation": (
            "Student-t intervals use the ten independent production-level seed estimates. "
            "Bootstrap intervals resample whole paired seeds. Neither includes NEST model "
            "uncertainty, detector calibration uncertainty, or official LZ waveform/selection covariance."
        ),
        "spatial_prior": (
            "Uniform active-TPC cylinder proxy from the source production; not the official "
            "4.71-tonne fiducial-volume or calibration-source geometry."
        ),
        "limitations": [
            "NEST Full S1 is a PMT/time-window response model, not official LZ waveform-level reconstruction.",
            "The S1-only [3,600] phd acceptance is reported separately from the full WS ROI.",
            "DAQ trigger, SS reconstruction, data-analysis cuts, official fiducial-volume mask, Skin/OD veto, and live-time migration are not included.",
            "The 1-phd quantile histogram and 10-phd TV histogram are descriptive summaries; native event samples remain the primary record.",
            "Ten independent seeds quantify production-level Monte Carlo variation but do not establish Parametric/Full statistical equivalence.",
            "No detector-systematic covariance or profile likelihood is constructed.",
        ],
        "n_summary_rows": len(summary_rows),
        "n_per_seed_rows": len(per_seed_rows),
        "n_threshold_rows": len(threshold_rows),
        "summary": json_summary,
        "outputs": OUTPUT_FILES,
    }
    return summary_rows, per_seed_rows, threshold_rows, metadata


def write_outputs(summary_rows: list[dict], per_seed_rows: list[dict],
                  threshold_rows: list[dict], metadata: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, rows in (
        ("summary", summary_rows),
        ("per_seed", per_seed_rows),
        ("thresholds", threshold_rows),
    ):
        if not rows:
            raise ValueError(f"refusing to write empty output: {OUTPUT_FILES[key]}")
        with (out_dir / OUTPUT_FILES[key]).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(base.csv_safe_row(row) for row in rows)
    (out_dir / OUTPUT_FILES["metadata"]).write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-root", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", required=True)
    parser.add_argument("--benchmarks", nargs="+", default=list(BENCHMARKS))
    parser.add_argument(
        "--spectrum-dir", type=Path,
        default=Path("research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum"),
    )
    parser.add_argument("--bootstrap-replicates", type=int, default=base.BOOTSTRAP_REPLICATES_DEFAULT)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    summary, per_seed, thresholds, metadata = run_audit(args)
    write_outputs(summary, per_seed, thresholds, metadata, args.out_dir)
    print(json.dumps({
        "status": metadata["status"],
        "benchmarks": metadata["benchmarks"],
        "seed_count": metadata["seed_count"],
        "total_events_audited": metadata["total_events_audited"],
        "benchmark_weighted_event_instances": metadata["benchmark_weighted_event_instances"],
        "n_summary_rows": len(summary),
        "n_per_seed_rows": len(per_seed),
        "n_threshold_rows": len(thresholds),
        "outputs": list(OUTPUT_FILES.values()),
    }, indent=2))


if __name__ == "__main__":
    main()
