#!/usr/bin/env python3
"""Audit the binning dependence of the independent-seed paired-S1 2D TV.

This is an exact aggregation of the archived 10-phd x 0.02-dex maps. It does
not generate new detector events or interpolate between cells. Both axes are
coarsened by factors 1, 2, and 4, corresponding to (10 phd, 0.02 dex),
(20 phd, 0.04 dex), and (40 phd, 0.08 dex).

The report compares the Parametric/Full TV of the equal-weight ensemble-mean
rate maps with the within-mode pairwise TV between independent seed maps.
All comparisons are descriptive Monte Carlo diagnostics, not confidence
intervals, significance tests, or detector-systematic uncertainties.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from aggregate_lz_2026_paired_s1_2d_independent_seeds import (
    BENCHMARKS,
    MODES,
    NUCLEAR_MODELS,
    STAGES,
    _read_maps,
    ensemble_mean_map,
    pairwise_tv_values,
    total_variation,
)

BASE_S1_BIN_WIDTH_PHD = 10.0
BASE_LOG10_S2_BIN_WIDTH = 0.02
REBIN_FACTORS = (1, 2, 4)


def rebin_map(cells: dict, factor: int) -> dict:
    """Aggregate both integer cell axes by an exact integer factor."""
    if factor not in REBIN_FACTORS:
        raise ValueError(f"factor must be one of {REBIN_FACTORS}")
    output = defaultdict(float)
    for cell, value in cells.items():
        if len(cell) != 2:
            raise ValueError(f"expected 2D cell key, got {cell}")
        if not math.isfinite(value) or value < 0.0:
            raise ValueError(f"invalid cell weight: {cell} -> {value}")
        output[(cell[0] // factor, cell[1] // factor)] += value
    return dict(output)


def marginalize_map(cells: dict, axis: int) -> dict:
    """Project (S1-bin, log10-S2-bin) cells onto one observable."""
    if axis not in (0, 1):
        raise ValueError("axis must be 0 (S1c) or 1 (log10 S2c)")
    output = defaultdict(float)
    for cell, value in cells.items():
        output[cell[axis]] += value
    return dict(output)


def _assert_rebin_preserves_rate(original: dict, rebinned: dict, context: str) -> None:
    before = math.fsum(original.values())
    after = math.fsum(rebinned.values())
    relative = abs(after - before) / max(abs(before), 1e-300)
    if relative > 1e-12:
        raise ValueError(
            f"rebinning changed integrated rate for {context}: "
            f"before={before}, after={after}, rel={relative}"
        )


def audit(seed_root: Path, seeds: list[int]) -> tuple[list[dict], list[dict], dict]:
    if len(seeds) < 3 or len(set(seeds)) != len(seeds):
        raise ValueError("provide at least three distinct independent seeds")

    expected_map_keys = {
        (benchmark, nuclear, "eft2024", mode, stage)
        for benchmark in BENCHMARKS
        for nuclear in NUCLEAR_MODELS
        for mode in MODES
        for stage in STAGES
    }
    maps_by_seed = {}
    for seed in seeds:
        path = seed_root / f"seed-{seed}" / "fold/paired_s1_mode_2d_signal_intensity.csv"
        maps_by_seed[seed] = _read_maps(path)
        observed = {key for key, _cell in maps_by_seed[seed]}
        if observed != expected_map_keys:
            raise ValueError(f"seed {seed} does not contain all 32 expected 2D maps")

    summary_rows = []
    per_seed_rows = []
    for benchmark in BENCHMARKS:
        for nuclear in NUCLEAR_MODELS:
            for stage in STAGES:
                seed_mode_maps = {
                    seed: {
                        mode: {
                            cell: value
                            for (key, cell), value in maps_by_seed[seed].items()
                            if key == (benchmark, nuclear, "eft2024", mode, stage)
                        }
                        for mode in MODES
                    }
                    for seed in seeds
                }
                if any(
                    not seed_mode_maps[seed][mode]
                    for seed in seeds for mode in MODES
                ):
                    raise ValueError(
                        f"empty map for {benchmark}/{nuclear}/{stage}"
                    )

                mean_maps = {
                    mode: ensemble_mean_map([
                        seed_mode_maps[seed][mode] for seed in seeds
                    ])
                    for mode in MODES
                }
                previous_mean_tv = None
                previous_seed_tvs = {seed: None for seed in seeds}
                previous_seed_spread = None

                for factor in REBIN_FACTORS:
                    rebinned_mean = {
                        mode: rebin_map(mean_maps[mode], factor)
                        for mode in MODES
                    }
                    for mode in MODES:
                        _assert_rebin_preserves_rate(
                            mean_maps[mode], rebinned_mean[mode],
                            f"{benchmark}/{nuclear}/{stage}/{mode}/factor={factor}",
                        )

                    mean_map_tv = total_variation(
                        rebinned_mean["parametric"], rebinned_mean["full"]
                    )
                    s1_marginal_tv = total_variation(
                        marginalize_map(rebinned_mean["parametric"], 0),
                        marginalize_map(rebinned_mean["full"], 0),
                    )
                    s2_marginal_tv = total_variation(
                        marginalize_map(rebinned_mean["parametric"], 1),
                        marginalize_map(rebinned_mean["full"], 1),
                    )

                    seed_mode_tvs = {}
                    rebinned_seed_maps = {}
                    for seed in seeds:
                        rebinned_seed_maps[seed] = {
                            mode: rebin_map(seed_mode_maps[seed][mode], factor)
                            for mode in MODES
                        }
                        for mode in MODES:
                            _assert_rebin_preserves_rate(
                                seed_mode_maps[seed][mode],
                                rebinned_seed_maps[seed][mode],
                                f"seed={seed}/{benchmark}/{nuclear}/{stage}/{mode}/factor={factor}",
                            )
                        seed_mode_tvs[seed] = total_variation(
                            rebinned_seed_maps[seed]["parametric"],
                            rebinned_seed_maps[seed]["full"],
                        )

                    pairwise_values = []
                    for mode in MODES:
                        pairwise_values.extend(pairwise_tv_values([
                            rebinned_seed_maps[seed][mode] for seed in seeds
                        ]))
                    if not pairwise_values:
                        raise ValueError(
                            f"no independent-seed map pairs for {benchmark}/{nuclear}/{stage}"
                        )
                    seed_spread = statistics.fmean(pairwise_values)
                    mean_seed_tv = statistics.fmean(seed_mode_tvs.values())
                    std_seed_tv = (
                        statistics.stdev(seed_mode_tvs.values())
                        if len(seed_mode_tvs) > 1 else 0.0
                    )

                    # Exact deterministic coarsening cannot increase TV.
                    if previous_mean_tv is not None and mean_map_tv > previous_mean_tv + 1e-12:
                        raise ValueError(
                            f"ensemble-map TV increased after coarsening for "
                            f"{benchmark}/{nuclear}/{stage}: {previous_mean_tv} -> {mean_map_tv}"
                        )
                    if previous_seed_spread is not None and seed_spread > previous_seed_spread + 1e-12:
                        raise ValueError(
                            f"seed-pairwise TV increased after coarsening for "
                            f"{benchmark}/{nuclear}/{stage}: {previous_seed_spread} -> {seed_spread}"
                        )
                    for seed in seeds:
                        previous = previous_seed_tvs[seed]
                        current = seed_mode_tvs[seed]
                        if previous is not None and current > previous + 1e-12:
                            raise ValueError(
                                f"per-seed mode TV increased after coarsening for seed {seed}: "
                                f"{previous} -> {current}"
                            )
                        previous_seed_tvs[seed] = current

                    s1_width = BASE_S1_BIN_WIDTH_PHD * factor
                    s2_width = BASE_LOG10_S2_BIN_WIDTH * factor
                    summary_rows.append({
                        "benchmark": benchmark,
                        "nuclear_model": nuclear,
                        "response_model": "eft2024",
                        "stage": stage,
                        "rebin_factor": factor,
                        "s1_bin_width_phd": s1_width,
                        "log10s2_bin_width": s2_width,
                        "ensemble_mean_map_2d_tv": mean_map_tv,
                        "ensemble_mean_map_s1_marginal_tv": s1_marginal_tv,
                        "ensemble_mean_map_log10s2_marginal_tv": s2_marginal_tv,
                        "mean_seed_parametric_vs_full_2d_tv": mean_seed_tv,
                        "std_seed_parametric_vs_full_2d_tv": std_seed_tv,
                        "min_seed_parametric_vs_full_2d_tv": min(seed_mode_tvs.values()),
                        "max_seed_parametric_vs_full_2d_tv": max(seed_mode_tvs.values()),
                        "mean_within_mode_seed_pairwise_2d_tv": seed_spread,
                        "ensemble_mode_tv_over_within_mode_seed_pairwise_tv": (
                            mean_map_tv / seed_spread if seed_spread > 0.0 else None
                        ),
                    })
                    for seed in seeds:
                        per_seed_rows.append({
                            "seed": seed,
                            "benchmark": benchmark,
                            "nuclear_model": nuclear,
                            "stage": stage,
                            "rebin_factor": factor,
                            "s1_bin_width_phd": s1_width,
                            "log10s2_bin_width": s2_width,
                            "parametric_vs_full_2d_tv": seed_mode_tvs[seed],
                        })

                    previous_mean_tv = mean_map_tv
                    previous_seed_spread = seed_spread

    expected_summary_rows = (
        len(BENCHMARKS) * len(NUCLEAR_MODELS) * len(STAGES) * len(REBIN_FACTORS)
    )
    expected_per_seed_rows = expected_summary_rows * len(seeds)
    if len(summary_rows) != expected_summary_rows:
        raise AssertionError(f"expected {expected_summary_rows} summary rows, got {len(summary_rows)}")
    if len(per_seed_rows) != expected_per_seed_rows:
        raise AssertionError(f"expected {expected_per_seed_rows} per-seed rows, got {len(per_seed_rows)}")

    metadata = {
        "study": "independent-seed paired S1 2D histogram-binning stability",
        "status": "INDEPENDENT_SEED_2D_BINNING_STABILITY_DIAGNOSTIC_ONLY",
        "seeds": seeds,
        "n_seeds": len(seeds),
        "benchmarks": list(BENCHMARKS),
        "nuclear_models": list(NUCLEAR_MODELS),
        "response_model": "eft2024",
        "stages": list(STAGES),
        "base_map_binning": {
            "s1_bin_width_phd": BASE_S1_BIN_WIDTH_PHD,
            "log10s2_bin_width": BASE_LOG10_S2_BIN_WIDTH,
        },
        "rebin_factors": list(REBIN_FACTORS),
        "rebinning_definition": (
            "Exact aggregation of integer cell indices on both axes; factor 2 "
            "maps 10-phd/0.02-dex cells to 20-phd/0.04-dex cells, and factor 4 "
            "maps to 40-phd/0.08-dex cells. No interpolation or new event generation."
        ),
        "seed_spread_definition": (
            "Mean pairwise TV between independent seed maps within each S1 mode, "
            "averaged over Parametric and Full modes; descriptive only, not the "
            "standard error or confidence interval of ensemble-mean TV."
        ),
        "ensemble_tv_to_seed_spread_ratio_definition": (
            "Descriptive scale comparison only; not an uncertainty estimate or "
            "a model-equivalence test."
        ),
        "limitations": [
            f"Uses {len(seeds)} independent pseudorandom seeds; no bootstrap confidence interval is included.",
            "Binning stability is an exact aggregation of the same events, not a new Monte Carlo.",
            "TV is binning-dependent and is not a stand-alone model-equivalence or significance test.",
            "NEST EFT2024 response is not official waveform-level LZ reconstruction.",
            "DAQ, SS/data-analysis, official FV, Skin/OD, and live-time migration remain absent."
        ],
        "n_summary_rows": len(summary_rows),
        "n_per_seed_rows": len(per_seed_rows),
    }
    return summary_rows, per_seed_rows, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-root", type=Path, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    summary_rows, per_seed_rows, metadata = audit(args.seed_root, args.seeds)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.out_dir / "paired_s1_independent_seed_binning_stability_summary.csv"
    per_seed_path = args.out_dir / "paired_s1_independent_seed_binning_stability_per_seed.csv"
    metadata_path = args.out_dir / "paired_s1_independent_seed_binning_stability_metadata.json"
    for path, rows in ((summary_path, summary_rows), (per_seed_path, per_seed_rows)):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": metadata["status"],
        "n_seeds": metadata["n_seeds"],
        "n_summary_rows": len(summary_rows),
        "n_per_seed_rows": len(per_seed_rows),
        "outputs": [str(summary_path), str(per_seed_path), str(metadata_path)],
    }, indent=2))


if __name__ == "__main__":
    main()
