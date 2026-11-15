#!/usr/bin/env python3
"""Independent-seed full-range 1-keV versus 5-keV three-body NR response audit.

The two grids are produced independently with disjoint seeds. Events per
energy stratum scale with stratum width (4,000 per 1-keV bin and 20,000 per
5-keV bin by default), keeping the generated event density per keV equal.
This is a numerical response-grid study, not a full LZ selected-event PDF.
"""
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

ROI_MIN_KEV = grid.ROI_MIN_KEV
ROI_MAX_KEV = grid.ROI_MAX_KEV
FAMILIES = ("eft2024", "tableS5")
BENCHMARKS = (
    "red_ms200_dm1",
    "green_ms300_dm1",
    "black_ms360_dm1",
    "blue_ms300_dm10",
)
NUCLEAR_MODELS = ("GCN", "JJ55")
MODES = ("nest", "ws_roi")
REFERENCE_GRID_KEV = 1.0
CANDIDATE_GRID_KEV = 5.0
RATE_TOLERANCE = 0.01
TV_TOLERANCE = 0.01


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


def symmetric_relative_difference(a: float, b: float) -> float:
    scale = max(abs(a), abs(b))
    if scale == 0.0:
        return 0.0
    return abs(a - b) / scale


def max_pairwise_rate_difference(values: list[float]) -> float:
    if len(values) < 2:
        raise ValueError("at least two independent seeds are required")
    return max(
        symmetric_relative_difference(a, b)
        for a, b in itertools.combinations(values, 2)
    )


def pairwise_tv_distances(intensities: list[dict]) -> list[float]:
    if len(intensities) < 2:
        raise ValueError("at least two independent seeds are required")
    return [
        grid.total_variation(a, b)
        for a, b in itertools.combinations(intensities, 2)
    ]


def validate_response_sample(
    stats: dict, width_keV: float, events_per_bin: int, sample_label: str
) -> None:
    """Check exact ROI coverage, energy edges, two replicas, and per-bin counts."""
    edges = grid.make_edges(ROI_MIN_KEV, ROI_MAX_KEV, width_keV)
    expected_bins = len(edges) - 1
    bins = sorted({ibin for ibin, _ in stats})
    if bins != list(range(expected_bins)):
        raise ValueError(
            f"{sample_label}: expected energy-bin indices 0..{expected_bins - 1}, "
            f"got {bins[:3]}...{bins[-3:] if bins else []}"
        )
    if events_per_bin < 2 or events_per_bin % 2:
        raise ValueError("events per energy bin must be a positive even integer")
    expected_per_replica = events_per_bin // 2
    for ibin, (lo, hi) in enumerate(zip(edges, edges[1:])):
        for replica in (0, 1):
            rec = stats.get((ibin, replica))
            if rec is None:
                raise ValueError(
                    f"{sample_label}: missing bin {ibin}, replica {replica}"
                )
            if not math.isclose(rec["lo"], lo, rel_tol=0.0, abs_tol=1e-9):
                raise ValueError(f"{sample_label}: wrong low edge in bin {ibin}")
            if not math.isclose(rec["hi"], hi, rel_tol=0.0, abs_tol=1e-9):
                raise ValueError(f"{sample_label}: wrong high edge in bin {ibin}")
            if rec["n"] != expected_per_replica:
                raise ValueError(
                    f"{sample_label}: bin {ibin}, replica {replica} has "
                    f"{rec['n']} events, expected {expected_per_replica}"
                )


def load_seed_fold(
    response_dir: Path,
    seed: int,
    width_keV: float,
    events_per_bin: int,
    response_family: str,
    spectra: dict[tuple[str, str], tuple[list[float], list[float]]],
) -> dict:
    path = response_dir / f"{response_family}.csv"
    stats = grid.read_response(path)
    validate_response_sample(
        stats, width_keV, events_per_bin, f"{response_family}/seed-{seed}/{width_keV:g}keV"
    )
    folded = {}
    for (benchmark, nuclear), (xs, ys) in spectra.items():
        pooled = high.fold_interval(
            stats, xs, ys, ROI_MIN_KEV, ROI_MAX_KEV, width_keV, None
        )
        split = [
            high.fold_interval(
                stats, xs, ys, ROI_MIN_KEV, ROI_MAX_KEV, width_keV, replica
            )
            for replica in (0, 1)
        ]
        folded[(benchmark, nuclear)] = {
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
    return {"seed": seed, "width_keV": width_keV, "folds": folded}


def summarize_comparison(
    one_kev: list[dict],
    five_kev: list[dict],
    benchmark: str,
    nuclear_model: str,
    mode: str,
    response_family: str,
) -> dict:
    key = (benchmark, nuclear_model)
    one_rates = [
        item["folds"][key]["pooled"][mode]["accepted_rate_events_kg_day"]
        for item in one_kev
    ]
    five_rates = [
        item["folds"][key]["pooled"][mode]["accepted_rate_events_kg_day"]
        for item in five_kev
    ]
    one_mean, one_sd, one_se = mean_sd_se(one_rates)
    five_mean, five_sd, five_se = mean_sd_se(five_rates)
    combined_se = math.sqrt(one_se * one_se + five_se * five_se)
    rate_difference = grid.relative_difference(one_mean, five_mean)
    rate_over_sem = (
        abs(five_mean - one_mean) / combined_se
        if combined_se > 0.0
        else (0.0 if five_mean == one_mean else math.inf)
    )

    one_maps = [item["folds"][key]["pooled"]["intensity"][mode] for item in one_kev]
    five_maps = [item["folds"][key]["pooled"]["intensity"][mode] for item in five_kev]
    one_mean_map = mean_intensity(one_maps)
    five_mean_map = mean_intensity(five_maps)
    mean_map_tv = grid.total_variation(one_mean_map, five_mean_map)

    one_pair_tv = pairwise_tv_distances(one_maps)
    five_pair_tv = pairwise_tv_distances(five_maps)
    return {
        "benchmark": benchmark,
        "nuclear_model": nuclear_model,
        "response_family": response_family,
        "acceptance_mode": mode,
        "n_independent_seeds_per_grid": len(one_kev),
        "reference_grid_keV": REFERENCE_GRID_KEV,
        "candidate_grid_keV": CANDIDATE_GRID_KEV,
        "reference_mean_accepted_rate_events_kg_day": one_mean,
        "reference_seed_sd_events_kg_day": one_sd,
        "reference_seed_sem_events_kg_day": one_se,
        "candidate_mean_accepted_rate_events_kg_day": five_mean,
        "candidate_seed_sd_events_kg_day": five_sd,
        "candidate_seed_sem_events_kg_day": five_se,
        "relative_rate_difference_5_vs_1keV": rate_difference,
        "combined_seed_sem_events_kg_day": combined_se,
        "rate_difference_over_combined_seed_sem": rate_over_sem,
        "reference_max_pairwise_seed_rate_difference": max_pairwise_rate_difference(one_rates),
        "candidate_max_pairwise_seed_rate_difference": max_pairwise_rate_difference(five_rates),
        "reference_max_pairwise_seed_tv_distance": max(one_pair_tv),
        "candidate_max_pairwise_seed_tv_distance": max(five_pair_tv),
        "tv_distance_between_mean_2d_maps": mean_map_tv,
        "reference_max_within_seed_split_rate_difference": max(
            item["folds"][key]["split_rate_difference"][mode] for item in one_kev
        ),
        "candidate_max_within_seed_split_rate_difference": max(
            item["folds"][key]["split_rate_difference"][mode] for item in five_kev
        ),
        "reference_max_within_seed_split_tv_distance": max(
            item["folds"][key]["split_tv_distance"][mode] for item in one_kev
        ),
        "candidate_max_within_seed_split_tv_distance": max(
            item["folds"][key]["split_tv_distance"][mode] for item in five_kev
        ),
        "reference_seeds": [item["seed"] for item in one_kev],
        "candidate_seeds": [item["seed"] for item in five_kev],
    }


def evaluate_full_range_grid_gate(comparisons: list[dict]) -> dict:
    if not comparisons:
        raise ValueError("no full-range independent-seed comparisons")
    finite = [
        row for row in comparisons
        if math.isfinite(row["relative_rate_difference_5_vs_1keV"])
        and math.isfinite(row["tv_distance_between_mean_2d_maps"])
    ]
    if len(finite) != len(comparisons):
        raise ValueError("non-finite rate or 2D-TV comparison in full-range audit")
    max_rate = max(row["relative_rate_difference_5_vs_1keV"] for row in finite)
    max_tv = max(row["tv_distance_between_mean_2d_maps"] for row in finite)
    return {
        "scope": "full 5.4--269.9 keV ROI; both NR mean-yield families; all four benchmarks; GCN/JJ55; NEST and NEST+WS-ROI modes",
        "reference_grid_keV": REFERENCE_GRID_KEV,
        "candidate_grid_keV": CANDIDATE_GRID_KEV,
        "max_accepted_rate_relative_difference": max_rate,
        "max_2d_tv_distance_between_mean_maps": max_tv,
        "accepted_rate_threshold": RATE_TOLERANCE,
        "2d_tv_threshold": TV_TOLERANCE,
        "n_comparisons": len(finite),
        "point_estimate_pass": max_rate <= RATE_TOLERANCE and max_tv <= TV_TOLERANCE,
        "covariance_note": (
            "Three independent full productions estimate seed-to-seed rate and mean-map stability. "
            "They do not provide a cell-by-cell covariance matrix or validate official LZ selection."
        ),
    }


def run_audit(args: argparse.Namespace) -> dict:
    if len(args.one_kev_response_dirs) != 3 or len(args.five_kev_response_dirs) != 3:
        raise ValueError("exactly three independent productions are required per grid")
    if len(args.one_kev_seeds) != 3 or len(args.five_kev_seeds) != 3:
        raise ValueError("exactly three seed labels are required per grid")
    if len(set(args.one_kev_seeds)) != 3 or len(set(args.five_kev_seeds)) != 3:
        raise ValueError("seed labels must be unique within each grid")
    if set(args.one_kev_seeds) & set(args.five_kev_seeds):
        raise ValueError("1-keV and 5-keV productions must use disjoint seeds")
    if args.response_family not in FAMILIES:
        raise ValueError(f"response-family must be one of {FAMILIES}")
    if args.one_kev_events_per_bin < 2 or args.one_kev_events_per_bin % 2:
        raise ValueError("1-keV events per bin must be positive and even")
    if args.five_kev_events_per_bin < 2 or args.five_kev_events_per_bin % 2:
        raise ValueError("5-keV events per bin must be positive and even")
    if not math.isclose(
        args.one_kev_events_per_bin / REFERENCE_GRID_KEV,
        args.five_kev_events_per_bin / CANDIDATE_GRID_KEV,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise ValueError("the two grids must have equal generated events per keV")

    spectra = {}
    for benchmark in BENCHMARKS:
        path = (
            args.spectrum_dir / benchmark / "natural_xenon_continuous_spectrum.csv"
        )
        for nuclear in args.nuclear_models:
            spectra[(benchmark, nuclear)] = grid.read_spectrum(path, nuclear)

    one_kev = [
        load_seed_fold(
            directory, seed, REFERENCE_GRID_KEV,
            args.one_kev_events_per_bin, args.response_family, spectra,
        )
        for seed, directory in zip(args.one_kev_seeds, args.one_kev_response_dirs)
    ]
    five_kev = [
        load_seed_fold(
            directory, seed, CANDIDATE_GRID_KEV,
            args.five_kev_events_per_bin, args.response_family, spectra,
        )
        for seed, directory in zip(args.five_kev_seeds, args.five_kev_response_dirs)
    ]

    comparisons = [
        summarize_comparison(one_kev, five_kev, benchmark, nuclear, mode, args.response_family)
        for benchmark in BENCHMARKS
        for nuclear in args.nuclear_models
        for mode in MODES
    ]
    gate = evaluate_full_range_grid_gate(comparisons)
    per_seed = []
    for grid_label, samples in (("1keV", one_kev), ("5keV", five_kev)):
        for sample in samples:
            for (benchmark, nuclear), result in sample["folds"].items():
                for mode in MODES:
                    pooled = result["pooled"]
                    per_seed.append({
                        "response_family": args.response_family,
                        "grid": grid_label,
                        "grid_width_keV": sample["width_keV"],
                        "seed": sample["seed"],
                        "benchmark": benchmark,
                        "nuclear_model": nuclear,
                        "acceptance_mode": mode,
                        "raw_rate_events_kg_day": pooled["raw_rate"],
                        "accepted_rate_events_kg_day": pooled[mode]["accepted_rate_events_kg_day"],
                        "acceptance_fraction_of_raw_rate": pooled[mode]["acceptance_fraction_of_raw_rate"],
                        "within_seed_split_rate_difference": result["split_rate_difference"][mode],
                        "within_seed_split_tv_distance": result["split_tv_distance"][mode],
                    })
    return {
        "study": f"independent-seed full-range 1-keV versus 5-keV {args.response_family} NR response-grid audit",
        "response_family": args.response_family,
        "true_recoil_interval_keV": [ROI_MIN_KEV, ROI_MAX_KEV],
        "reference_grid_keV": REFERENCE_GRID_KEV,
        "candidate_grid_keV": CANDIDATE_GRID_KEV,
        "one_kev_events_per_energy_bin_per_seed": args.one_kev_events_per_bin,
        "five_kev_events_per_energy_bin_per_seed": args.five_kev_events_per_bin,
        "events_per_keV_per_seed": args.one_kev_events_per_bin / REFERENCE_GRID_KEV,
        "one_kev_independent_seeds": args.one_kev_seeds,
        "five_kev_independent_seeds": args.five_kev_seeds,
        "independent_seed_count_per_grid": 3,
        "replicas_per_seed": 2,
        "response_nest_commit": grid.NEST_COMMIT,
        "spatial_prior": "uniform active-TPC cylinder volume proxy; not the official 4.71-tonne FV or calibration-source geometry",
        "folding": "event-level response probabilities folded with exact piecewise-linear three-body spectrum integrals in each independently generated energy stratum",
        "acceptance_modes": {
            "nest": "NEST Parametric S1 coincidence and configured NEST S2 threshold",
            "ws_roi": "NEST mode plus published S1c/raw-S2/S2c WS-ROI bounds",
        },
        "gate": gate,
        "comparisons": comparisons,
        "per_seed": per_seed,
        "limitations": [
            "The 1-keV and 5-keV response samples are independently generated with disjoint seeds.",
            "Equal event density per keV is used: 4,000 events per 1-keV bin and 20,000 events per 5-keV bin by default.",
            "Three seeds support a descriptive between-seed stability estimate, not a complete cell-by-cell covariance matrix.",
            "This remains an intermediate NEST-level / WS-ROI response, not the official LZ selected signal PDF.",
            "No waveform-level trigger, SS reconstruction, data-analysis cuts, official FV, Skin/OD veto, or live-time model is included.",
        ],
    }


def write_outputs(summary: dict, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "full_range_grid_independent_seed_summary.json"
    csv_path = out_dir / "full_range_grid_independent_seed_comparison.csv"
    seed_path = out_dir / "full_range_grid_independent_seed_details.csv"
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    rows = summary["comparisons"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        if rows:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    seed_rows = summary["per_seed"]
    with seed_path.open("w", newline="", encoding="utf-8") as handle:
        if seed_rows:
            writer = csv.DictWriter(handle, fieldnames=list(seed_rows[0]))
            writer.writeheader()
            writer.writerows(seed_rows)
    return {
        "summary_json": str(json_path),
        "comparison_csv": str(csv_path),
        "seed_details_csv": str(seed_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response-family", choices=FAMILIES, required=True)
    parser.add_argument("--one-kev-response-dirs", type=Path, nargs=3, required=True)
    parser.add_argument("--five-kev-response-dirs", type=Path, nargs=3, required=True)
    parser.add_argument("--one-kev-seeds", type=int, nargs=3, required=True)
    parser.add_argument("--five-kev-seeds", type=int, nargs=3, required=True)
    parser.add_argument("--one-kev-events-per-bin", type=int, default=4000)
    parser.add_argument("--five-kev-events-per-bin", type=int, default=20000)
    parser.add_argument("--spectrum-dir", type=Path, default=Path(
        "research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum"
    ))
    parser.add_argument("--nuclear-models", nargs="+", choices=NUCLEAR_MODELS, default=list(NUCLEAR_MODELS))
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    summary = run_audit(args)
    outputs = write_outputs(summary, args.out_dir)
    print(json.dumps({
        "response_family": summary["response_family"],
        "gate": summary["gate"],
        "outputs": outputs,
    }, indent=2))


if __name__ == "__main__":
    main()
