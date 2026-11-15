#!/usr/bin/env python3
"""Aggregate independent-seed paired S1 2D maps and quantify seed-to-seed spread.

Each seed directory must contain:
  fold/paired_s1_mode_2d_signal_intensity.csv
  fold/paired_s1_mode_2d_response_summary.csv
  fold/sampling-noise/paired_s1_2d_sampling_noise_summary.csv

Before aggregation, map integrals are checked against the corresponding
per-seed rate summaries and the split-half audit must close to the pooled map.

The script forms equal-weight ensemble-mean maps, computes Parametric/Full TV
for each seed and for the ensemble-mean maps, and measures within-mode
pairwise seed-to-seed TV. These are Monte Carlo ensemble diagnostics, not
detector-systematic uncertainties or a final likelihood.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

BENCHMARKS = (
    "red_ms200_dm1",
    "green_ms300_dm1",
    "black_ms360_dm1",
    "blue_ms300_dm10",
)
NUCLEAR_MODELS = ("GCN", "JJ55")
MODES = ("parametric", "full")
STAGES = ("nest", "ws_roi")


def total_variation(map_a: dict, map_b: dict) -> float | None:
    total_a = math.fsum(map_a.values())
    total_b = math.fsum(map_b.values())
    if total_a <= 0.0 or total_b <= 0.0:
        return None
    keys = set(map_a) | set(map_b)
    return 0.5 * math.fsum(
        abs(map_a.get(key, 0.0) / total_a - map_b.get(key, 0.0) / total_b)
        for key in keys
    )


def ensemble_mean_map(seed_maps: list[dict]) -> dict:
    if not seed_maps:
        raise ValueError("at least one seed map is required")
    n = len(seed_maps)
    output = defaultdict(float)
    for source in seed_maps:
        for cell, value in source.items():
            if not math.isfinite(value) or value < 0.0:
                raise ValueError("map weights must be finite and non-negative")
            output[cell] += value / n
    return dict(output)


def pairwise_tv_values(seed_maps: list[dict]) -> list[float]:
    values = []
    for left, right in itertools.combinations(seed_maps, 2):
        value = total_variation(left, right)
        if value is not None:
            values.append(value)
    return values


def summarize_seed_maps(seed_maps: dict[str, dict[str, dict]]) -> dict:
    """Summarize one benchmark/nuclear/stage: seed -> mode -> cell map."""
    seeds = list(seed_maps)
    if len(seeds) < 2:
        raise ValueError("at least two independent seeds are required")
    for seed in seeds:
        if set(seed_maps[seed]) != set(MODES):
            raise ValueError(f"seed {seed} must contain both S1 modes")

    per_seed_mode_tv = {
        seed: total_variation(
            seed_maps[seed]["parametric"], seed_maps[seed]["full"]
        )
        for seed in seeds
    }
    if any(value is None for value in per_seed_mode_tv.values()):
        raise ValueError("every seed must have non-empty Parametric and Full maps")

    mean_parametric = ensemble_mean_map([
        seed_maps[seed]["parametric"] for seed in seeds
    ])
    mean_full = ensemble_mean_map([
        seed_maps[seed]["full"] for seed in seeds
    ])
    mean_map_tv = total_variation(mean_parametric, mean_full)

    parametric_pairwise = pairwise_tv_values([
        seed_maps[seed]["parametric"] for seed in seeds
    ])
    full_pairwise = pairwise_tv_values([
        seed_maps[seed]["full"] for seed in seeds
    ])
    within_mode_pairwise = parametric_pairwise + full_pairwise
    if not within_mode_pairwise:
        raise ValueError("no valid within-mode seed-pair comparisons")

    seed_tv_values = list(per_seed_mode_tv.values())
    mean_seed_tv = statistics.fmean(seed_tv_values)
    std_seed_tv = statistics.stdev(seed_tv_values) if len(seed_tv_values) > 1 else 0.0
    mean_within_mode_tv = statistics.fmean(within_mode_pairwise)
    return {
        "n_seeds": len(seeds),
        "seed_labels": seeds,
        "mean_map_parametric_vs_full_tv": mean_map_tv,
        "mean_seed_parametric_vs_full_tv": mean_seed_tv,
        "std_seed_parametric_vs_full_tv": std_seed_tv,
        "min_seed_parametric_vs_full_tv": min(seed_tv_values),
        "max_seed_parametric_vs_full_tv": max(seed_tv_values),
        "mean_parametric_seed_pairwise_tv": (
            statistics.fmean(parametric_pairwise) if parametric_pairwise else None
        ),
        "mean_full_seed_pairwise_tv": (
            statistics.fmean(full_pairwise) if full_pairwise else None
        ),
        "mean_within_mode_seed_pairwise_tv": mean_within_mode_tv,
        "mean_map_tv_over_within_mode_seed_pairwise_tv": (
            mean_map_tv / mean_within_mode_tv if mean_map_tv is not None and mean_within_mode_tv > 0 else None
        ),
        "per_seed_parametric_vs_full_tv": per_seed_mode_tv,
        "mean_parametric_map": mean_parametric,
        "mean_full_map": mean_full,
    }


def _read_maps(path: Path) -> dict:
    output = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {
            "benchmark", "nuclear_model", "response_model", "s1_mode",
            "stage", "s1_bin_index", "s1_bin_low_phd",
            "log10s2_bin_index", "log10s2_bin_low", "rate_events_kg_day",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} missing columns: {sorted(missing)}")
        for row in reader:
            key = (
                row["benchmark"], row["nuclear_model"], row["response_model"],
                row["s1_mode"], row["stage"],
            )
            s1_bin = int(row["s1_bin_index"])
            s2_bin = int(row["log10s2_bin_index"])
            cell = (s1_bin, s2_bin)
            value = float(row["rate_events_kg_day"])
            s1_low = float(row["s1_bin_low_phd"])
            s2_low = float(row["log10s2_bin_low"])
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"invalid map weight in {path}: {row}")
            if abs(s1_low - s1_bin * 10.0) > 1e-9:
                raise ValueError(f"inconsistent S1 bin coordinate in {path}: {row}")
            if abs(s2_low - s2_bin * 0.02) > 1e-9:
                raise ValueError(f"inconsistent log10(S2c) bin coordinate in {path}: {row}")
            map_key = (key, cell)
            if map_key in output:
                raise ValueError(f"duplicate 2D cell in {path}: {map_key}")
            output[map_key] = value
    return output


def _read_rates(path: Path) -> dict:
    output = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {
            "benchmark", "nuclear_model", "response_model", "stage",
            "parametric_rate_events_kg_day", "full_rate_events_kg_day",
            "full_vs_parametric_relative_rate_difference",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} missing columns: {sorted(missing)}")
        for row in reader:
            if row["response_model"] != "eft2024":
                raise ValueError(f"unexpected response model in {path}: {row['response_model']}")
            key = (row["benchmark"], row["nuclear_model"], row["stage"])
            if key in output:
                raise ValueError(f"duplicate summary row in {path}: {key}")
            values = {
                "parametric_rate_events_kg_day": float(row["parametric_rate_events_kg_day"]),
                "full_rate_events_kg_day": float(row["full_rate_events_kg_day"]),
                "full_vs_parametric_relative_rate_difference": float(
                    row["full_vs_parametric_relative_rate_difference"]
                ),
            }
            if any(not math.isfinite(value) or value < 0.0 for name, value in values.items()
                   if name != "full_vs_parametric_relative_rate_difference"):
                raise ValueError(f"invalid rate in {path}: {row}")
            output[key] = values
    return output


def _read_split_half(path: Path) -> dict:
    output = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {
            "benchmark", "nuclear_model", "stage",
            "mean_within_mode_split_half_tv",
            "pooled_tv_reproduction_abs_difference",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} missing columns: {sorted(missing)}")
        for row in reader:
            key = (row["benchmark"], row["nuclear_model"], row["stage"])
            if key in output:
                raise ValueError(f"duplicate split-half row in {path}: {key}")
            tv = float(row["mean_within_mode_split_half_tv"])
            closure = float(row["pooled_tv_reproduction_abs_difference"])
            if not math.isfinite(tv) or tv < 0.0:
                raise ValueError(f"invalid split-half TV in {path}: {row}")
            if not math.isfinite(closure) or closure > 1e-10:
                raise ValueError(f"split-half audit does not close in {path}: {row}")
            output[key] = {
                "mean_within_mode_split_half_tv": tv,
                "pooled_tv_reproduction_abs_difference": closure,
            }
    return output


def _expected_summary_keys() -> set[tuple[str, str, str]]:
    return {
        (benchmark, nuclear, stage)
        for benchmark in BENCHMARKS
        for nuclear in NUCLEAR_MODELS
        for stage in STAGES
    }


def aggregate(seed_root: Path, seeds: list[int]) -> tuple[list[dict], list[dict], dict]:
    if len(seeds) < 3 or len(set(seeds)) != len(seeds):
        raise ValueError("provide at least three distinct seed labels")
    maps_by_seed = {}
    rates_by_seed = {}
    split_half_by_seed = {}
    expected_rate_keys = _expected_summary_keys()
    expected_map_keys = {
        (benchmark, nuclear, "eft2024", mode, stage)
        for benchmark in BENCHMARKS
        for nuclear in NUCLEAR_MODELS
        for mode in MODES
        for stage in STAGES
    }
    for seed in seeds:
        seed_dir = seed_root / f"seed-{seed}" / "fold"
        maps_by_seed[seed] = _read_maps(
            seed_dir / "paired_s1_mode_2d_signal_intensity.csv"
        )
        rates_by_seed[seed] = _read_rates(
            seed_dir / "paired_s1_mode_2d_response_summary.csv"
        )
        split_half_by_seed[seed] = _read_split_half(
            seed_dir / "sampling-noise/paired_s1_2d_sampling_noise_summary.csv"
        )
        if set(rates_by_seed[seed]) != expected_rate_keys:
            raise ValueError(f"seed {seed} does not contain the complete 16-row rate summary")
        if set(split_half_by_seed[seed]) != expected_rate_keys:
            raise ValueError(f"seed {seed} does not contain the complete 16-row split-half audit")
        observed_map_keys = {key for key, _cell in maps_by_seed[seed]}
        if observed_map_keys != expected_map_keys:
            raise ValueError(f"seed {seed} does not contain the complete 32 mode/stage maps")

        # A map is an event-weighted rate density. Its cell integral must close
        # to the corresponding per-seed integrated rate before seed averaging.
        map_totals = defaultdict(float)
        for (map_key, _cell), value in maps_by_seed[seed].items():
            map_totals[map_key] += value
        for benchmark, nuclear, stage in sorted(expected_rate_keys):
            summary = rates_by_seed[seed][(benchmark, nuclear, stage)]
            for mode, rate_name in (
                ("parametric", "parametric_rate_events_kg_day"),
                ("full", "full_rate_events_kg_day"),
            ):
                map_key = (benchmark, nuclear, "eft2024", mode, stage)
                map_rate = map_totals[map_key]
                summary_rate = summary[rate_name]
                relative_closure = abs(map_rate - summary_rate) / max(abs(summary_rate), 1e-300)
                if relative_closure > 1e-10:
                    raise ValueError(
                        f"seed {seed} map/rate closure failed for {map_key}: "
                        f"map={map_rate}, summary={summary_rate}, rel={relative_closure}"
                    )

    per_seed_rows = []
    ensemble_rows = []
    mean_map_rows = []
    for benchmark in BENCHMARKS:
        for nuclear in NUCLEAR_MODELS:
            for stage in STAGES:
                key_prefix = (benchmark, nuclear, "eft2024")
                seed_maps = {}
                for seed in seeds:
                    seed_maps[seed] = {}
                    for mode in MODES:
                        selected = {
                            cell: value
                            for (key, cell), value in maps_by_seed[seed].items()
                            if key == (*key_prefix, mode, stage)
                        }
                        if not selected:
                            raise ValueError(
                                f"empty map for seed={seed}, benchmark={benchmark}, "
                                f"nuclear={nuclear}, mode={mode}, stage={stage}"
                            )
                        seed_maps[seed][mode] = selected

                result = summarize_seed_maps({
                    str(seed): seed_maps[seed] for seed in seeds
                })
                rate_records = [
                    rates_by_seed[seed][(benchmark, nuclear, stage)]
                    for seed in seeds
                ]
                split_half_records = [
                    split_half_by_seed[seed][(benchmark, nuclear, stage)]
                    for seed in seeds
                ]
                mean_within_stream_split_half_tv = statistics.fmean(
                    row["mean_within_mode_split_half_tv"] for row in split_half_records
                )
                mean_p_rate = statistics.fmean(
                    row["parametric_rate_events_kg_day"] for row in rate_records
                )
                mean_f_rate = statistics.fmean(
                    row["full_rate_events_kg_day"] for row in rate_records
                )
                rate_relative = mean_f_rate / mean_p_rate - 1.0 if mean_p_rate > 0 else None
                seed_rate_differences = [
                    row["full_vs_parametric_relative_rate_difference"]
                    for row in rate_records
                ]
                ensemble_rows.append({
                    "benchmark": benchmark,
                    "nuclear_model": nuclear,
                    "response_model": "eft2024",
                    "stage": stage,
                    "n_seeds": len(seeds),
                    "mean_map_parametric_vs_full_tv": result["mean_map_parametric_vs_full_tv"],
                    "mean_seed_parametric_vs_full_tv": result["mean_seed_parametric_vs_full_tv"],
                    "std_seed_parametric_vs_full_tv": result["std_seed_parametric_vs_full_tv"],
                    "min_seed_parametric_vs_full_tv": result["min_seed_parametric_vs_full_tv"],
                    "max_seed_parametric_vs_full_tv": result["max_seed_parametric_vs_full_tv"],
                    "mean_parametric_seed_pairwise_tv": result["mean_parametric_seed_pairwise_tv"],
                    "mean_full_seed_pairwise_tv": result["mean_full_seed_pairwise_tv"],
                    "mean_within_mode_seed_pairwise_tv": result["mean_within_mode_seed_pairwise_tv"],
                    "mean_map_tv_over_within_mode_seed_pairwise_tv": result["mean_map_tv_over_within_mode_seed_pairwise_tv"],
                    "mean_within_stream_split_half_tv": mean_within_stream_split_half_tv,
                    "mean_map_tv_over_within_stream_split_half_tv": (
                        result["mean_map_parametric_vs_full_tv"] / mean_within_stream_split_half_tv
                        if mean_within_stream_split_half_tv > 0.0 else None
                    ),
                    "mean_parametric_rate_events_kg_day": mean_p_rate,
                    "mean_full_rate_events_kg_day": mean_f_rate,
                    "full_over_parametric_mean_rate_relative_difference": rate_relative,
                    "mean_seed_rate_relative_difference": statistics.fmean(seed_rate_differences),
                    "std_seed_rate_relative_difference": statistics.stdev(seed_rate_differences),
                })
                for seed in seeds:
                    rate = rates_by_seed[seed][(benchmark, nuclear, stage)]
                    per_seed_rows.append({
                        "seed": seed,
                        "benchmark": benchmark,
                        "nuclear_model": nuclear,
                        "stage": stage,
                        "parametric_vs_full_2d_tv": result["per_seed_parametric_vs_full_tv"][str(seed)],
                        "within_stream_split_half_tv": split_half_by_seed[seed][
                            (benchmark, nuclear, stage)
                        ]["mean_within_mode_split_half_tv"],
                        "mode_tv_over_within_stream_split_half_tv": (
                            result["per_seed_parametric_vs_full_tv"][str(seed)]
                            / split_half_by_seed[seed][(benchmark, nuclear, stage)][
                                "mean_within_mode_split_half_tv"
                            ]
                            if split_half_by_seed[seed][(benchmark, nuclear, stage)][
                                "mean_within_mode_split_half_tv"
                            ] > 0.0 else None
                        ),
                        **rate,
                    })
                for mode, mean_map in (
                    ("parametric", result["mean_parametric_map"]),
                    ("full", result["mean_full_map"]),
                ):
                    for (s1_bin, s2_bin), rate in mean_map.items():
                        mean_map_rows.append({
                            "benchmark": benchmark,
                            "nuclear_model": nuclear,
                            "response_model": "eft2024",
                            "s1_mode": mode,
                            "stage": stage,
                            "s1_bin_index": s1_bin,
                            "s1_bin_low_phd": s1_bin * 10.0,
                            "log10s2_bin_index": s2_bin,
                            "log10s2_bin_low": s2_bin * 0.02,
                            "mean_rate_events_kg_day": rate,
                        })

    metadata = {
        "study": "independent-seed ensemble for paired Parametric/Full S1 2D response",
        "status": "INDEPENDENT_SEED_2D_RESPONSE_DIAGNOSTIC_ONLY",
        "seeds": seeds,
        "n_seeds": len(seeds),
        "benchmarks": list(BENCHMARKS),
        "nuclear_models": list(NUCLEAR_MODELS),
        "response_model": "eft2024",
        "stages": list(STAGES),
        "mean_map_definition": "Equal-weight arithmetic mean of the event-weighted per-seed rate maps.",
        "seed_spread_definition": "Pairwise TV between independent seed maps within each S1 mode; descriptive only, not the standard error or confidence interval of the ensemble-mean TV.",
        "mean_map_tv_over_pairwise_spread_definition": "Descriptive scale comparison only; it does not estimate uncertainty on ensemble-mean TV and is not an equivalence test.",
        "limitations": [
            f"Uses {len(seeds)} independent pseudorandom seeds; no bootstrap confidence interval is included.",
            "No detector-systematic uncertainty is included.",
            "NEST EFT2024 response is not official waveform-level LZ reconstruction.",
            "DAQ, SS/data-analysis, official FV, Skin/OD, and live-time migration remain absent.",
            "The map TV depends on the 10-phd by 0.02-dex histogram binning."
        ],
        "per_key_summaries": ensemble_rows,
    }
    return ensemble_rows, per_seed_rows, {"mean_maps": mean_map_rows, "metadata": metadata}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-root", type=Path, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    ensemble_rows, per_seed_rows, extra = aggregate(args.seed_root, args.seeds)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "ensemble": args.out_dir / "paired_s1_independent_seed_ensemble_summary.csv",
        "per_seed": args.out_dir / "paired_s1_independent_seed_per_seed_summary.csv",
        "mean_maps": args.out_dir / "paired_s1_independent_seed_mean_maps.csv",
        "metadata": args.out_dir / "paired_s1_independent_seed_ensemble_metadata.json",
    }
    for key, rows in (
        ("ensemble", ensemble_rows),
        ("per_seed", per_seed_rows),
        ("mean_maps", extra["mean_maps"]),
    ):
        with outputs[key].open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    outputs["metadata"].write_text(
        json.dumps(extra["metadata"], indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": extra["metadata"]["status"],
        "n_seeds": len(args.seeds),
        "n_ensemble_rows": len(ensemble_rows),
        "n_per_seed_rows": len(per_seed_rows),
        "n_mean_map_rows": len(extra["mean_maps"]),
        "outputs": [str(path) for path in outputs.values()],
    }, indent=2))


if __name__ == "__main__":
    main()
