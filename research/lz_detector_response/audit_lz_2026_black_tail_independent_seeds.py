#!/usr/bin/env python3
"""Compare independent-seed 1-keV and 0.5-keV EFT2024 black-benchmark tail MC."""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import compare_lz_2026_nr_high_energy_half_kev as high
import converge_lz_2026_three_body_energy_grid as grid

FAMILY = "eft2024"
BENCHMARK = "black_ms360_dm1"
TAIL_MIN_KEV = 225.4
TAIL_MAX_KEV = 269.9
MODES = ("nest", "ws_roi")


def mean_sd_se(values: list[float]) -> tuple[float, float, float]:
    if len(values) < 2:
        raise ValueError("at least two independent seeds are required")
    if any(not math.isfinite(value) for value in values):
        raise ValueError("seed estimates must be finite")
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    return mean, sd, sd / math.sqrt(len(values))


def mean_intensity(intensities: list[dict]) -> dict:
    if not intensities:
        raise ValueError("cannot average an empty set of intensity maps")
    output = defaultdict(float)
    for intensity in intensities:
        for cell, value in intensity.items():
            output[cell] += value / len(intensities)
    return dict(output)


def max_pairwise_rate_difference(values: list[float]) -> float:
    if len(values) < 2:
        raise ValueError("at least two independent seeds are required")
    return max(
        grid.relative_difference(a, b)
        for a, b in itertools.combinations(values, 2)
    )


def pairwise_tv_distances(intensities: list[dict]) -> list[float]:
    if len(intensities) < 2:
        raise ValueError("at least two independent seeds are required")
    return [
        grid.total_variation(a, b)
        for a, b in itertools.combinations(intensities, 2)
    ]


def load_seed_fold(
    response_dir: Path,
    seed: int,
    width: float,
    xs: list[float],
    ys: list[float],
) -> dict:
    path = response_dir / f"{FAMILY}.csv"
    stats = grid.read_response(path)
    pooled = high.fold_interval(
        stats, xs, ys, TAIL_MIN_KEV, TAIL_MAX_KEV, width, None
    )
    split = [
        high.fold_interval(
            stats, xs, ys, TAIL_MIN_KEV, TAIL_MAX_KEV, width, replica
        )
        for replica in (0, 1)
    ]
    return {
        "seed": seed,
        "width_keV": width,
        "pooled": pooled,
        "split_rate_difference": {
            mode: grid.relative_difference(
                split[0][mode]["accepted_rate_events_kg_day"],
                split[1][mode]["accepted_rate_events_kg_day"],
            )
            for mode in MODES
        },
        "split_tv_distance": {
            mode: grid.total_variation(
                split[0]["intensity"][mode], split[1]["intensity"][mode]
            )
            for mode in MODES
        },
    }


def summarize_comparison(
    coarse: list[dict],
    fine: list[dict],
    nuclear_model: str,
    mode: str,
) -> dict:
    coarse_rates = [
        item["pooled"][mode]["accepted_rate_events_kg_day"] for item in coarse
    ]
    fine_rates = [
        item["pooled"][mode]["accepted_rate_events_kg_day"] for item in fine
    ]
    coarse_mean, coarse_sd, coarse_se = mean_sd_se(coarse_rates)
    fine_mean, fine_sd, fine_se = mean_sd_se(fine_rates)
    combined_se = math.sqrt(coarse_se**2 + fine_se**2)
    rate_difference = grid.relative_difference(coarse_mean, fine_mean)
    z_score = (
        abs(fine_mean - coarse_mean) / combined_se
        if combined_se > 0.0 else (0.0 if fine_mean == coarse_mean else math.inf)
    )

    coarse_maps = [item["pooled"]["intensity"][mode] for item in coarse]
    fine_maps = [item["pooled"]["intensity"][mode] for item in fine]
    coarse_mean_map = mean_intensity(coarse_maps)
    fine_mean_map = mean_intensity(fine_maps)
    mean_map_tv = grid.total_variation(coarse_mean_map, fine_mean_map)
    coarse_pair_tv = pairwise_tv_distances(coarse_maps)
    fine_pair_tv = pairwise_tv_distances(fine_maps)

    return {
        "benchmark": BENCHMARK,
        "nuclear_model": nuclear_model,
        "response_family": FAMILY,
        "acceptance_mode": mode,
        "n_independent_seeds_per_grid": len(coarse),
        "coarse_grid_keV": 1.0,
        "fine_grid_keV": 0.5,
        "coarse_mean_accepted_rate_events_kg_day": coarse_mean,
        "coarse_seed_sd_events_kg_day": coarse_sd,
        "coarse_seed_sem_events_kg_day": coarse_se,
        "fine_mean_accepted_rate_events_kg_day": fine_mean,
        "fine_seed_sd_events_kg_day": fine_sd,
        "fine_seed_sem_events_kg_day": fine_se,
        "relative_rate_difference_fine_vs_coarse": rate_difference,
        "combined_seed_sem_events_kg_day": combined_se,
        "rate_difference_z_score": z_score,
        "coarse_max_pairwise_seed_rate_difference": max_pairwise_rate_difference(coarse_rates),
        "fine_max_pairwise_seed_rate_difference": max_pairwise_rate_difference(fine_rates),
        "coarse_max_pairwise_seed_tv_distance": max(coarse_pair_tv),
        "fine_max_pairwise_seed_tv_distance": max(fine_pair_tv),
        "tv_distance_between_mean_2d_maps": mean_map_tv,
        "coarse_max_within_seed_split_rate_difference": max(
            item["split_rate_difference"][mode] for item in coarse
        ),
        "fine_max_within_seed_split_rate_difference": max(
            item["split_rate_difference"][mode] for item in fine
        ),
        "coarse_max_within_seed_split_tv_distance": max(
            item["split_tv_distance"][mode] for item in coarse
        ),
        "fine_max_within_seed_split_tv_distance": max(
            item["split_tv_distance"][mode] for item in fine
        ),
        "independent_coarse_seeds": [item["seed"] for item in coarse],
        "independent_fine_seeds": [item["seed"] for item in fine],
    }


def run_audit(args: argparse.Namespace) -> dict:
    if len(args.coarse_response_dirs) != 3 or len(args.fine_response_dirs) != 3:
        raise ValueError("exactly three independent seeds are required per grid")
    if len(args.coarse_seeds) != 3 or len(args.fine_seeds) != 3:
        raise ValueError("exactly three seed labels are required per grid")
    if len(set(args.coarse_seeds)) != 3 or len(set(args.fine_seeds)) != 3:
        raise ValueError("seed labels must be unique within each grid")
    if set(args.coarse_seeds) & set(args.fine_seeds):
        raise ValueError("coarse- and fine-grid productions must use disjoint seeds")
    if args.events_per_stratum < 2 or args.events_per_stratum % 2:
        raise ValueError("events-per-stratum must be a positive even integer")

    spectrum_path = (
        args.spectrum_dir / BENCHMARK / "natural_xenon_continuous_spectrum.csv"
    )
    coarse_samples = {}
    fine_samples = {}
    for seed, directory in zip(args.coarse_seeds, args.coarse_response_dirs):
        coarse_samples[seed] = directory
    for seed, directory in zip(args.fine_seeds, args.fine_response_dirs):
        fine_samples[seed] = directory

    comparisons = []
    seed_details = []
    for nuclear in args.nuclear_models:
        xs, ys = grid.read_spectrum(spectrum_path, nuclear)
        coarse = [
            load_seed_fold(coarse_samples[seed], seed, 1.0, xs, ys)
            for seed in args.coarse_seeds
        ]
        fine = [
            load_seed_fold(fine_samples[seed], seed, 0.5, xs, ys)
            for seed in args.fine_seeds
        ]
        for label, samples in (("1-keV", coarse), ("0.5-keV", fine)):
            for sample in samples:
                for bin_row in sample["pooled"]["bin_rows"]:
                    if bin_row["n_generated"] != args.events_per_stratum:
                        raise ValueError(
                            f"{label} seed {sample['seed']} has "
                            f"{bin_row['n_generated']} events in a stratum; "
                            f"expected {args.events_per_stratum}"
                        )
        for mode in MODES:
            comparisons.append(summarize_comparison(coarse, fine, nuclear, mode))
        for width, samples in ((1.0, coarse), (0.5, fine)):
            for item in samples:
                for mode in MODES:
                    seed_details.append({
                        "nuclear_model": nuclear,
                        "acceptance_mode": mode,
                        "grid_width_keV": width,
                        "seed": item["seed"],
                        "accepted_rate_events_kg_day": (
                            item["pooled"][mode]["accepted_rate_events_kg_day"]
                        ),
                        "within_seed_split_rate_difference": item["split_rate_difference"][mode],
                        "within_seed_split_tv_distance": item["split_tv_distance"][mode],
                    })

    return {
        "study": "independent-seed EFT2024 black-benchmark high-energy response audit",
        "status": "INDEPENDENT_SEED_RATE_AND_SHAPE_DIAGNOSTIC",
        "benchmark": BENCHMARK,
        "response_family": FAMILY,
        "true_recoil_interval_keV": [TAIL_MIN_KEV, TAIL_MAX_KEV],
        "events_per_stratum_per_seed": args.events_per_stratum,
        "independent_seed_count_per_grid": 3,
        "coarse_grid_keV": 1.0,
        "fine_grid_keV": 0.5,
        "coarse_seeds": args.coarse_seeds,
        "fine_seeds": args.fine_seeds,
        "response_nest_commit": grid.NEST_COMMIT,
        "spatial_prior": (
            "Uniform active-TPC cylinder proxy; not the official 4.71-tonne FV "
            "or calibration-source geometry"
        ),
        "replica_interpretation": (
            "The two within-seed halves are diagnostic only. The three full "
            "productions per grid, each with a distinct seed, are the independent "
            "replication units for rate standard errors."
        ),
        "covariance_limit": (
            "This estimates between-seed uncertainty for integrated accepted rates "
            "and reports pairwise 2D-shape stability. Three seeds do not provide a "
            "complete high-dimensional cell-by-cell detector covariance matrix."
        ),
        "comparisons": comparisons,
        "per_seed": seed_details,
    }


def write_outputs(summary: dict, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "black_tail_independent_seed_summary.json"
    comparison_path = out_dir / "black_tail_independent_seed_comparison.csv"
    seed_path = out_dir / "black_tail_independent_seed_details.csv"
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    comparisons = summary["comparisons"]
    with comparison_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(comparisons[0]))
        writer.writeheader()
        writer.writerows(comparisons)
    details = summary["per_seed"]
    with seed_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(details[0]))
        writer.writeheader()
        writer.writerows(details)
    return {
        "summary_json": str(json_path),
        "comparison_csv": str(comparison_path),
        "seed_details_csv": str(seed_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coarse-response-dirs", type=Path, nargs=3, required=True)
    parser.add_argument("--fine-response-dirs", type=Path, nargs=3, required=True)
    parser.add_argument("--coarse-seeds", type=int, nargs=3, required=True)
    parser.add_argument("--fine-seeds", type=int, nargs=3, required=True)
    parser.add_argument("--events-per-stratum", type=int, default=10000)
    parser.add_argument("--nuclear-models", nargs="+", default=["GCN", "JJ55"])
    parser.add_argument("--spectrum-dir", type=Path, default=Path(
        "research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum"
    ))
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    summary = run_audit(args)
    outputs = write_outputs(summary, args.out_dir)
    print(json.dumps({
        "status": summary["status"],
        "comparisons": summary["comparisons"],
        **outputs,
    }, indent=2))


if __name__ == "__main__":
    main()
