#!/usr/bin/env python3
"""Compare 0.5- and 1-keV NEST NR response folding in the high-energy tail.

The interval is aligned to the 1-keV response strata (225.4--269.9 keV).
The calculation reuses the exact piecewise-linear three-body spectra and
compares 2D cell intensities, accepted rates, and disjoint-replica stability.
It is a response-grid diagnostic, not a full LZ selected likelihood.
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

import converge_lz_2026_three_body_energy_grid as grid

TAIL_MIN_KEV = 225.4
TAIL_MAX_KEV = 269.9
EXPOSURE_KG_DAY = 1_037_310.0
FAMILIES = ("eft2024", "tableS5", "ws2024", "generic")
BENCHMARKS = ("red_ms200_dm1", "green_ms300_dm1", "black_ms360_dm1", "blue_ms300_dm10")
NUCLEAR_MODELS = ("GCN", "JJ55")
MODES = ("nest", "ws_roi")


def interval_edges(lo: float, hi: float, width: float) -> list[float]:
    return grid.make_edges(lo, hi, width)


def fold_interval(stats: dict, xs: list[float], ys: list[float],
                  lo: float, hi: float, coarse_width: float,
                  replica: int | None) -> dict:
    """Fold one response sample over an exact sub-interval."""
    edges = interval_edges(lo, hi, coarse_width)
    bin_map = {}
    for (ibin, rep), rec in stats.items():
        if rep == 0:
            bin_map[ibin] = (rec["lo"], rec["hi"])

    selected = {
        ibin: (a, b) for ibin, (a, b) in bin_map.items()
        if a >= lo - 1e-8 and b <= hi + 1e-8
    }
    if not selected:
        raise ValueError("response has no strata in requested interval")
    if abs(min(a for a, _ in selected.values()) - lo) > 1e-8:
        raise ValueError("response strata do not begin at requested interval")
    if abs(max(b for _, b in selected.values()) - hi) > 1e-8:
        raise ValueError("response strata do not end at requested interval")

    intensity = {mode: defaultdict(float) for mode in MODES}
    bin_rows = []
    raw_rate = grid.integrate_linear(xs, ys, lo, hi)
    for a, b in zip(edges, edges[1:]):
        ids = [
            ibin for ibin, (flo, fhi) in selected.items()
            if flo >= a - 1e-8 and fhi <= b + 1e-8
        ]
        if not ids:
            raise ValueError(f"no response strata in coarse interval [{a},{b}]")
        merged = grid.merge_bin_stats(stats, ids, replica)
        if abs(merged["width"] - (b - a)) > 1e-7:
            raise ValueError(f"response strata do not cover [{a},{b}]")
        rate_bin = grid.integrate_linear(xs, ys, a, b)
        for mode in MODES:
            for cell, probability in merged["cell_probability"][mode].items():
                intensity[mode][cell] += rate_bin * probability
        bin_rows.append({
            "energy_low_keV": a,
            "energy_high_keV": b,
            "rate_integral_events_kg_day": rate_bin,
            "n_generated": merged["n_generated"],
            "s1_coin_acceptance": merged["acceptance"]["s1_coin"],
            "s2_threshold_acceptance": merged["acceptance"]["s2_threshold"],
            "nest_acceptance": merged["acceptance"]["nest"],
            "ws_roi_acceptance": merged["acceptance"]["ws_roi"],
        })

    result = {"raw_rate": raw_rate, "bin_rows": bin_rows, "intensity": {}}
    for mode in MODES:
        cells = dict(intensity[mode])
        accepted = math.fsum(cells.values())
        result["intensity"][mode] = cells
        result[mode] = {
            "accepted_rate_events_kg_day": accepted,
            "acceptance_fraction_of_raw_rate": accepted / raw_rate if raw_rate > 0 else 0.0,
            "number_of_cells": len(cells),
        }
    return result


def write_outputs(args: argparse.Namespace) -> dict:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    coarse_samples = {}
    fine_samples = {}
    for family in FAMILIES:
        coarse_path = args.coarse_response_dir / f"{family}.csv"
        fine_path = args.fine_response_dir / f"{family}.csv"
        coarse_samples[family] = grid.read_response(coarse_path)
        fine_samples[family] = grid.read_response(fine_path)

    summary = {
        "study": "0.5-keV versus 1-keV high-energy three-body NR response-grid comparison",
        "true_recoil_interval_keV": [TAIL_MIN_KEV, TAIL_MAX_KEV],
        "response_grids_keV": [1.0, 0.5],
        "events_per_1keV_or_0p5keV_stratum": 4000,
        "replicas": "two disjoint 2,000-event halves per stratum",
        "response_nest_commit": grid.NEST_COMMIT,
        "spatial_prior": "uniform active-TPC cylinder volume proxy; not the official 4.71-tonne FV or calibration-source geometry",
        "folding": "piecewise-linear three-body spectrum integrated exactly in each response bin; response cell probabilities retain all generated events in the denominator",
        "acceptance_modes": {
            "nest": "NEST Parametric S1 coincidence and configured NEST S2 threshold",
            "ws_roi": "NEST mode plus 3<=S1c<=600 phd, raw S2>645 phd, and 2.75<=log10(S2c)<=4.15",
        },
        "limitations": [
            "This is only a high-energy response-grid diagnostic, not the full 5.4-269.9 keV selected signal PDF.",
            "The WS ROI mode omits trigger, SS reconstruction, data-analysis cuts, fiducial-volume selection, Skin/OD veto, and live-time selections.",
            "The two replica halves are disjoint halves of each seeded response stream, not separately seeded full productions.",
            "No official calibration-source spatial prior, position-reconstruction smearing, or full detector nuisance covariance is included.",
        ],
        "comparisons": [],
        "replica_stability": [],
    }

    intensity_path = args.out_dir / "high_energy_signal_2d_intensity.csv"
    comparison_path = args.out_dir / "high_energy_grid_comparison.csv"
    replica_path = args.out_dir / "high_energy_replica_stability.csv"
    bin_path = args.out_dir / "high_energy_acceptance_by_bin.csv"

    with intensity_path.open("w", newline="", encoding="utf-8") as f_int, \
         comparison_path.open("w", newline="", encoding="utf-8") as f_cmp, \
         replica_path.open("w", newline="", encoding="utf-8") as f_rep, \
         bin_path.open("w", newline="", encoding="utf-8") as f_bin:
        wi = csv.writer(f_int)
        wi.writerow([
            "benchmark", "nuclear_model", "response_family", "acceptance_mode",
            "response_grid_keV", "s1c_bin_low_phd", "s1c_bin_high_phd",
            "log10s2c_bin_low", "log10s2c_bin_high", "rate_events_kg_day_cell",
        ])
        wc = csv.DictWriter(f_cmp, fieldnames=[
            "benchmark", "nuclear_model", "response_family", "acceptance_mode",
            "raw_rate_tail_events_kg_day", "rate_1keV_events_kg_day",
            "rate_0p5keV_events_kg_day", "relative_rate_difference_0p5_vs_1keV",
            "rate_1keV_events_2p84_tonne_year", "rate_0p5keV_events_2p84_tonne_year",
            "tv_distance_0p5_vs_1keV", "replica_rate_difference_1keV",
            "replica_tv_distance_1keV", "replica_rate_difference_0p5keV",
            "replica_tv_distance_0p5keV", "tv_vs_1keV_over_max_replica_tv",
            "rate_difference_over_max_replica_rate_difference",
        ])
        wc.writeheader()
        wr = csv.DictWriter(f_rep, fieldnames=[
            "benchmark", "nuclear_model", "response_family", "acceptance_mode",
            "response_grid_keV", "replica_rate_events_kg_day",
            "replica_vs_pooled_tv_distance",
        ])
        wr.writeheader()
        wb = csv.DictWriter(f_bin, fieldnames=[
            "benchmark", "nuclear_model", "response_family", "response_grid_keV",
            "replica", "energy_low_keV", "energy_high_keV",
            "rate_integral_events_kg_day", "n_generated", "s1_coin_acceptance",
            "s2_threshold_acceptance", "nest_acceptance", "ws_roi_acceptance",
        ])
        wb.writeheader()

        for benchmark in BENCHMARKS:
            spectrum_path = (
                args.spectrum_dir / benchmark / "natural_xenon_continuous_spectrum.csv"
            )
            for nuclear in NUCLEAR_MODELS:
                xs, ys = grid.read_spectrum(spectrum_path, nuclear)
                for family in FAMILIES:
                    samples = {
                        1.0: coarse_samples[family],
                        0.5: fine_samples[family],
                    }
                    folded = {}
                    for width, stats in samples.items():
                        for rep in (0, 1, None):
                            folded[(width, rep)] = fold_interval(
                                stats, xs, ys, TAIL_MIN_KEV, TAIL_MAX_KEV,
                                width, rep,
                            )
                            rep_label = "pooled" if rep is None else str(rep)
                            for br in folded[(width, rep)]["bin_rows"]:
                                wb.writerow({
                                    "benchmark": benchmark,
                                    "nuclear_model": nuclear,
                                    "response_family": family,
                                    "response_grid_keV": width,
                                    "replica": rep_label,
                                    **br,
                                })
                    for mode in MODES:
                        ref = folded[(1.0, None)]
                        fine = folded[(0.5, None)]
                        rep1 = (folded[(1.0, 0)], folded[(1.0, 1)])
                        rep05 = (folded[(0.5, 0)], folded[(0.5, 1)])
                        r1 = ref[mode]["accepted_rate_events_kg_day"]
                        r05 = fine[mode]["accepted_rate_events_kg_day"]
                        tv = grid.total_variation(ref["intensity"][mode], fine["intensity"][mode])
                        rate_rep1 = grid.relative_difference(
                            rep1[0][mode]["accepted_rate_events_kg_day"],
                            rep1[1][mode]["accepted_rate_events_kg_day"],
                        )
                        tv_rep1 = grid.total_variation(
                            rep1[0]["intensity"][mode], rep1[1]["intensity"][mode]
                        )
                        rate_rep05 = grid.relative_difference(
                            rep05[0][mode]["accepted_rate_events_kg_day"],
                            rep05[1][mode]["accepted_rate_events_kg_day"],
                        )
                        tv_rep05 = grid.total_variation(
                            rep05[0]["intensity"][mode], rep05[1]["intensity"][mode]
                        )
                        max_rep_rate = max(rate_rep1, rate_rep05)
                        max_rep_tv = max(tv_rep1, tv_rep05)
                        rate_diff = grid.relative_difference(r1, r05)
                        row = {
                            "benchmark": benchmark,
                            "nuclear_model": nuclear,
                            "response_family": family,
                            "acceptance_mode": mode,
                            "raw_rate_tail_events_kg_day": ref["raw_rate"],
                            "rate_1keV_events_kg_day": r1,
                            "rate_0p5keV_events_kg_day": r05,
                            "relative_rate_difference_0p5_vs_1keV": rate_diff,
                            "rate_1keV_events_2p84_tonne_year": r1 * EXPOSURE_KG_DAY,
                            "rate_0p5keV_events_2p84_tonne_year": r05 * EXPOSURE_KG_DAY,
                            "tv_distance_0p5_vs_1keV": tv,
                            "replica_rate_difference_1keV": rate_rep1,
                            "replica_tv_distance_1keV": tv_rep1,
                            "replica_rate_difference_0p5keV": rate_rep05,
                            "replica_tv_distance_0p5keV": tv_rep05,
                            "tv_vs_1keV_over_max_replica_tv": tv / max_rep_tv if max_rep_tv > 0 else None,
                            "rate_difference_over_max_replica_rate_difference": (
                                rate_diff / max_rep_rate if max_rep_rate > 0 else None
                            ),
                        }
                        summary["comparisons"].append(row)
                        wc.writerow(row)
                        for width, reps in ((1.0, rep1), (0.5, rep05)):
                            for i, rep_fold in enumerate(reps):
                                wr.writerow({
                                    "benchmark": benchmark,
                                    "nuclear_model": nuclear,
                                    "response_family": family,
                                    "acceptance_mode": mode,
                                    "response_grid_keV": width,
                                    "replica_rate_events_kg_day": rep_fold[mode]["accepted_rate_events_kg_day"],
                                    "replica_tv_distance": grid.total_variation(
                                        rep_fold["intensity"][mode],
                                        folded[(width, None)]["intensity"][mode],
                                    ),
                                })
                        for width in (1.0, 0.5):
                            for (s1_bin, log_bin), rate_cell in sorted(
                                folded[(width, None)]["intensity"][mode].items()
                            ):
                                wi.writerow([
                                    benchmark, nuclear, family, mode, width,
                                    s1_bin * grid.S1_BIN_WIDTH_PHD,
                                    (s1_bin + 1) * grid.S1_BIN_WIDTH_PHD,
                                    round(log_bin * grid.LOG10_S2_BIN_WIDTH, 2),
                                    round((log_bin + 1) * grid.LOG10_S2_BIN_WIDTH, 2),
                                    f"{rate_cell:.12g}",
                                ])

    summary["diagnostics"] = {
        "n_comparisons": len(summary["comparisons"]),
        "max_relative_rate_difference_0p5_vs_1keV": max(
            x["relative_rate_difference_0p5_vs_1keV"] for x in summary["comparisons"]
        ),
        "max_tv_distance_0p5_vs_1keV": max(
            x["tv_distance_0p5_vs_1keV"] for x in summary["comparisons"]
        ),
        "comparisons_where_grid_tv_exceeds_both_replica_tv_checks": sum(
            x["tv_distance_0p5_vs_1keV"] > max(
                x["replica_tv_distance_1keV"], x["replica_tv_distance_0p5keV"]
            ) for x in summary["comparisons"]
        ),
        "comparisons_where_grid_rate_difference_exceeds_both_replica_rate_checks": sum(
            x["relative_rate_difference_0p5_vs_1keV"] > max(
                x["replica_rate_difference_1keV"], x["replica_rate_difference_0p5keV"]
            ) for x in summary["comparisons"]
        ),
        "formal_pass": None,
        "status": "DIAGNOSTIC_ONLY_NO_PREDECLARED_TOLERANCE",
    }
    (args.out_dir / "high_energy_half_kev_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coarse-response-dir", type=Path, required=True)
    ap.add_argument("--fine-response-dir", type=Path, required=True)
    ap.add_argument("--spectrum-dir", type=Path, default=Path(
        "research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum"
    ))
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    summary = write_outputs(args)
    print(json.dumps(summary["diagnostics"], indent=2))


if __name__ == "__main__":
    main()
