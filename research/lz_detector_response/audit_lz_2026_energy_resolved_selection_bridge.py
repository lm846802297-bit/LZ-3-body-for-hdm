#!/usr/bin/env python3
"""Energy-resolved Fig. S2 residual-selection bridge using archived NEST events.

This is a rate-level diagnostic. It does not construct the missing conditional
2D SS/data-analysis migration kernel and must not be used as a scalar 2D
selection correction.
"""
from __future__ import annotations

import argparse
import bisect
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
from summarize_lz_2026_selection_stage_rates import (
    CURVE_COLUMNS,
    integrate_piecewise_linear_product,
    validate_cumulative_curves,
)

RESPONSE_FAMILIES = ("eft2024", "tableS5")
BENCHMARKS = (
    "red_ms200_dm1",
    "green_ms300_dm1",
    "black_ms360_dm1",
    "blue_ms300_dm10",
)
NUCLEAR_MODELS = ("GCN", "JJ55")
ORANGE = "trigger_plus_s1_threshold_cumulative"
GREEN = "trigger_plus_s1_ss_analysis_cumulative"
FINAL = "final_plus_roi_cumulative"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_efficiency_curves(path: Path) -> tuple[list[float], dict[str, list[float]]]:
    rows = read_csv(path)
    validate_cumulative_curves(rows)
    x = [float(row["ER_keV"]) for row in rows]
    if any(b <= a for a, b in zip(x, x[1:])):
        raise ValueError("Fig. S2 recoil-energy knots must be strictly increasing")
    curves = {
        name: [float(row[name]) for row in rows]
        for name in CURVE_COLUMNS
    }
    return x, curves


def pooled_acceptance(raw_replica: list[float], passed_replica: list[float]) -> float:
    if len(raw_replica) != 2 or len(passed_replica) != 2:
        raise ValueError("exactly two event replicas are required")
    denominator = math.fsum(raw_replica)
    numerator = math.fsum(passed_replica)
    if denominator <= 0.0:
        if numerator > 0.0:
            raise ValueError("positive accepted weight with zero total response weight")
        return 0.0
    if numerator < -1e-12 or numerator > denominator * (1.0 + 1e-10):
        raise ValueError("accepted response weight is outside the total weight")
    return min(1.0, max(0.0, numerator / denominator))


def conditional_efficiency(numerator_rate: float, denominator_rate: float) -> float:
    if denominator_rate <= 0.0:
        return 0.0
    value = numerator_rate / denominator_rate
    if not math.isfinite(value) or value < -1e-9 or value > 1.0 + 1e-8:
        raise ValueError("conditional efficiency is outside [0,1]")
    return min(1.0, max(0.0, value))


def load_spectra(
    spectrum_dir: Path, benchmarks: list[str], nuclear_models: list[str]
) -> dict[tuple[str, str], tuple[list[float], list[float]]]:
    spectra = {}
    for benchmark in benchmarks:
        path = spectrum_dir / benchmark / "natural_xenon_continuous_spectrum.csv"
        for nuclear in nuclear_models:
            spectra[(benchmark, nuclear)] = grid.read_spectrum(path, nuclear)
    return spectra


def accumulate_weighted_response(
    response_csv: Path,
    spectra: dict[tuple[str, str], tuple[list[float], list[float]]],
) -> tuple[dict, dict, dict]:
    """Stream one NEST response family and accumulate per-bin rate-density sums."""
    sums = defaultdict(lambda: {
        "raw": [0.0, 0.0],
        "nest": [0.0, 0.0],
        "ws_roi": [0.0, 0.0],
        "n": [0, 0],
    })
    edges = {}
    with response_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {
            "replica", "energy_bin_index", "energy_bin_low_keV",
            "energy_bin_high_keV", "energy_keV", "s1c_abs_phd",
            "s2c_abs_phd", "s2r_abs_phd", "s1_coincidence_pass",
            "s2_threshold_pass",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{response_csv} missing columns: {sorted(missing)}")

        for row in reader:
            ibin = int(row["energy_bin_index"])
            replica = int(row["replica"])
            if replica not in (0, 1):
                raise ValueError(f"invalid replica label {replica}")
            lo = float(row["energy_bin_low_keV"])
            hi = float(row["energy_bin_high_keV"])
            edge = edges.setdefault(ibin, (lo, hi))
            if abs(edge[0] - lo) > 1e-10 or abs(edge[1] - hi) > 1e-10:
                raise ValueError(f"inconsistent energy edges in bin {ibin}")

            energy = float(row["energy_keV"])
            s1c = float(row["s1c_abs_phd"])
            s2c = float(row["s2c_abs_phd"])
            s2r = float(row["s2r_abs_phd"])
            nest_pass = (
                int(row["s1_coincidence_pass"]) == 1
                and int(row["s2_threshold_pass"]) == 1
                and s1c > 0.0
                and s2c > 0.0
            )
            roi_pass = nest_pass and grid.ws_roi_pass(s1c, s2r, s2c)

            for key, (xs, ys) in spectra.items():
                weight = grid.interpolate(energy, xs, ys)
                bucket = sums[(key, ibin)]
                bucket["raw"][replica] += weight
                bucket["n"][replica] += 1
                if nest_pass:
                    bucket["nest"][replica] += weight
                if roi_pass:
                    bucket["ws_roi"][replica] += weight

    if not edges:
        raise ValueError(f"empty response sample: {response_csv}")
    expected_edges = grid.make_edges(grid.ROI_MIN_KEV, grid.ROI_MAX_KEV, 1.0)
    if sorted(edges) != list(range(len(expected_edges) - 1)):
        raise ValueError("response sample does not cover the full 1-keV recoil grid")
    for ibin, (lo, hi) in enumerate(zip(expected_edges, expected_edges[1:])):
        observed = edges[ibin]
        if abs(observed[0] - lo) > 1e-9 or abs(observed[1] - hi) > 1e-9:
            raise ValueError(f"response sample has incorrect energy edges in bin {ibin}")
        for key in spectra:
            bucket = sums[(key, ibin)]
            if bucket["n"] != [2000, 2000]:
                raise ValueError(
                    f"{key}/{ibin}: expected 2,000 events per replica, got {bucket['n']}"
                )
    return sums, edges, expected_edges


def read_reference_bridge(path: Path | None) -> dict:
    if path is None:
        return {}
    rows = read_csv(path)
    return {
        (row["benchmark"], row["nuclear_model"], row["response_family"]): row
        for row in rows
    }


def build_energy_resolved_rows(
    family: str,
    spectra: dict[tuple[str, str], tuple[list[float], list[float]]],
    sums: dict,
    edges: dict,
    energy_edges: list[float],
    efficiency_x: list[float],
    efficiency_curves: dict[str, list[float]],
) -> tuple[list[dict], list[dict]]:
    per_bin = []
    summaries = []
    for key, (spectrum_x, spectrum_y) in spectra.items():
        benchmark, nuclear = key
        for ibin, (lo, hi) in enumerate(zip(energy_edges, energy_edges[1:])):
            bucket = sums[(key, ibin)]
            exact_raw = grid.integrate_linear(spectrum_x, spectrum_y, lo, hi)
            nest_acceptance = pooled_acceptance(bucket["raw"], bucket["nest"])
            ws_roi_acceptance = pooled_acceptance(bucket["raw"], bucket["ws_roi"])
            nest_rate = exact_raw * nest_acceptance
            ws_roi_rate = exact_raw * ws_roi_acceptance

            orange_rate = integrate_piecewise_linear_product(
                spectrum_x, spectrum_y, efficiency_x,
                efficiency_curves[ORANGE], lo, hi,
            )
            green_rate = integrate_piecewise_linear_product(
                spectrum_x, spectrum_y, efficiency_x,
                efficiency_curves[GREEN], lo, hi,
            )
            final_rate = integrate_piecewise_linear_product(
                spectrum_x, spectrum_y, efficiency_x,
                efficiency_curves[FINAL], lo, hi,
            )
            ss_da_conditional = conditional_efficiency(green_rate, orange_rate)
            energy_factorized_rate = ws_roi_rate * ss_da_conditional
            bin_ratio = (
                energy_factorized_rate / final_rate - 1.0
                if final_rate > 0.0 else None
            )

            per_bin.append({
                "benchmark": benchmark,
                "nuclear_model": nuclear,
                "response_family": family,
                "energy_bin_index": ibin,
                "energy_low_keV": lo,
                "energy_high_keV": hi,
                "generated_events_replica0": bucket["n"][0],
                "generated_events_replica1": bucket["n"][1],
                "exact_raw_rate_events_kg_day": exact_raw,
                "nest_acceptance_weighted_replica0": (
                    bucket["nest"][0] / bucket["raw"][0]
                    if bucket["raw"][0] > 0.0 else 0.0
                ),
                "nest_acceptance_weighted_replica1": (
                    bucket["nest"][1] / bucket["raw"][1]
                    if bucket["raw"][1] > 0.0 else 0.0
                ),
                "ws_roi_acceptance_weighted_replica0": (
                    bucket["ws_roi"][0] / bucket["raw"][0]
                    if bucket["raw"][0] > 0.0 else 0.0
                ),
                "ws_roi_acceptance_weighted_replica1": (
                    bucket["ws_roi"][1] / bucket["raw"][1]
                    if bucket["raw"][1] > 0.0 else 0.0
                ),
                "nest_acceptance_weighted_pooled": nest_acceptance,
                "ws_roi_acceptance_weighted_pooled": ws_roi_acceptance,
                "nest_accepted_rate_events_kg_day": nest_rate,
                "ws_roi_accepted_rate_events_kg_day": ws_roi_rate,
                "figs2_trigger_plus_s1_rate_events_kg_day": orange_rate,
                "figs2_trigger_plus_s1_ss_da_rate_events_kg_day": green_rate,
                "figs2_final_plus_roi_rate_events_kg_day": final_rate,
                "figs2_ss_da_given_trigger_plus_s1": ss_da_conditional,
                "energy_resolved_factorized_rate_events_kg_day": energy_factorized_rate,
                "energy_resolved_factorized_vs_figs2_final_relative_difference": bin_ratio,
            })

        selected = [
            row for row in per_bin
            if row["benchmark"] == benchmark
            and row["nuclear_model"] == nuclear
            and row["response_family"] == family
        ]
        total = lambda field: math.fsum(row[field] for row in selected)
        raw_total = total("exact_raw_rate_events_kg_day")
        nest_total = total("nest_accepted_rate_events_kg_day")
        ws_roi_total = total("ws_roi_accepted_rate_events_kg_day")
        orange_total = total("figs2_trigger_plus_s1_rate_events_kg_day")
        green_total = total("figs2_trigger_plus_s1_ss_da_rate_events_kg_day")
        final_total = total("figs2_final_plus_roi_rate_events_kg_day")
        energy_factorized_total = total("energy_resolved_factorized_rate_events_kg_day")
        global_ss_da = conditional_efficiency(green_total, orange_total)
        global_factorized = ws_roi_total * global_ss_da
        global_ratio = (
            global_factorized / final_total - 1.0 if final_total > 0.0 else None
        )
        energy_ratio = (
            energy_factorized_total / final_total - 1.0 if final_total > 0.0 else None
        )
        valid_bins = [
            row for row in selected
            if row["energy_resolved_factorized_vs_figs2_final_relative_difference"] is not None
        ]
        worst_bin = max(
            valid_bins,
            key=lambda row: abs(
                row["energy_resolved_factorized_vs_figs2_final_relative_difference"]
            ),
            default=None,
        )
        summaries.append({
            "benchmark": benchmark,
            "nuclear_model": nuclear,
            "response_family": family,
            "n_energy_bins": len(selected),
            "raw_rate_events_kg_day": raw_total,
            "nest_rate_events_kg_day": nest_total,
            "ws_roi_rate_events_kg_day": ws_roi_total,
            "figs2_trigger_plus_s1_rate_events_kg_day": orange_total,
            "figs2_trigger_plus_s1_ss_da_rate_events_kg_day": green_total,
            "figs2_final_plus_roi_rate_events_kg_day": final_total,
            "figs2_ss_da_given_trigger_plus_s1_global": global_ss_da,
            "global_factorized_rate_events_kg_day": global_factorized,
            "global_factorized_vs_figs2_final_relative_difference": global_ratio,
            "energy_resolved_factorized_rate_events_kg_day": energy_factorized_total,
            "energy_resolved_factorized_vs_figs2_final_relative_difference": energy_ratio,
            "max_abs_energy_binwise_factorization_difference": (
                abs(worst_bin["energy_resolved_factorized_vs_figs2_final_relative_difference"])
                if worst_bin else None
            ),
            "worst_energy_bin_low_keV": worst_bin["energy_low_keV"] if worst_bin else None,
            "worst_energy_bin_high_keV": worst_bin["energy_high_keV"] if worst_bin else None,
        })
    return per_bin, summaries


def run_audit(args: argparse.Namespace) -> dict:
    efficiency_x, efficiency_curves = read_efficiency_curves(args.efficiency_csv)
    spectra = load_spectra(args.spectrum_dir, args.benchmarks, args.nuclear_models)
    reference_rows = {}
    for family in args.response_families:
        if args.reference_bridge_dir is not None:
            reference_rows[family] = read_reference_bridge(
                args.reference_bridge_dir / family / "conditional_selection_bridge.csv"
            )
        else:
            reference_rows[family] = {}

    all_bins = []
    all_summaries = []
    reproduction_differences = []
    for family in args.response_families:
        sums, edges, energy_edges = accumulate_weighted_response(
            args.response_dir / f"{family}.csv", spectra
        )
        bin_rows, summaries = build_energy_resolved_rows(
            family, spectra, sums, edges, energy_edges,
            efficiency_x, efficiency_curves,
        )
        for row in summaries:
            ref = reference_rows[family].get((
                row["benchmark"], row["nuclear_model"], family
            ))
            if ref is not None:
                reference_difference = float(
                    ref["relative_difference_factorized_vs_figs2"]
                )
                row["reference_integrated_bridge_relative_difference"] = reference_difference
                row["integrated_bridge_reproduction_abs_difference"] = abs(
                    row["global_factorized_vs_figs2_final_relative_difference"]
                    - reference_difference
                )
                reproduction_differences.append(
                    row["integrated_bridge_reproduction_abs_difference"]
                )
            else:
                row["reference_integrated_bridge_relative_difference"] = None
                row["integrated_bridge_reproduction_abs_difference"] = None
        all_bins.extend(bin_rows)
        all_summaries.extend(summaries)

    max_reproduction = max(reproduction_differences, default=None)
    if max_reproduction is not None and max_reproduction > 1e-8:
        raise AssertionError(
            f"energy-resolved bridge does not reproduce integrated bridge: {max_reproduction}"
        )
    return {
        "study": "energy-resolved Fig. S2 residual-selection bridge",
        "status": "ENERGY_RESOLVED_RATE_LEVEL_DIAGNOSTIC_ONLY",
        "source_run_id": args.source_run_id,
        "source_artifact_id": args.source_artifact_id,
        "nest_source_commit": grid.NEST_COMMIT,
        "response_families": args.response_families,
        "benchmarks": args.benchmarks,
        "nuclear_models": args.nuclear_models,
        "true_recoil_interval_keV": [grid.ROI_MIN_KEV, grid.ROI_MAX_KEV],
        "energy_bin_width_keV": 1.0,
        "n_energy_bins": len(grid.make_edges(grid.ROI_MIN_KEV, grid.ROI_MAX_KEV, 1.0)) - 1,
        "efficiency_curve_source": "LZ Collaboration arXiv:2609.02823v1 Supplemental Fig. S2 vector extraction",
        "factorization": (
            "per-bin NEST+WS-ROI accepted rate multiplied by the spectrum-integrated "
            "Fig. S2 SS+data-analysis conditional efficiency (green/orange) in that bin"
        ),
        "roi_overlap_policy": (
            "Do not multiply Fig. S2 ROI conditional efficiency again: the WS ROI is already applied."
        ),
        "integrated_bridge_reproduction_max_abs_difference": max_reproduction,
        "per_key_summaries": all_summaries,
        "per_energy_bin_rows": all_bins,
        "limitations": [
            "This is a rate-level factorization diagnostic, not a conditional 2D selection or migration kernel.",
            "The Fig. S2 SS+data-analysis conditional efficiency is not guaranteed to factorize from NEST/WS-ROI at event level.",
            "No waveform trigger, SS reconstruction, official FV, Skin/OD veto, or live-time response is applied.",
            "The raw response sample uses one seeded NEST production with two within-stream halves; this is not an independent-seed uncertainty estimate.",
            "Do not multiply the full Fig. S2 cumulative efficiency or the residual factor into the existing 2D intensity as a scalar correction.",
        ],
    }


def write_outputs(summary: dict, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "energy_resolved_selection_bridge_summary.json"
    summary_csv = out_dir / "energy_resolved_selection_bridge_summary.csv"
    bins_csv = out_dir / "energy_resolved_selection_bridge_by_energy_bin.csv"
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for path, rows in (
        (summary_csv, summary["per_key_summaries"]),
        (bins_csv, summary["per_energy_bin_rows"]),
    ):
        with path.open("w", newline="", encoding="utf-8") as handle:
            if rows:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
    return {
        "summary_json": str(json_path),
        "summary_csv": str(summary_csv),
        "per_energy_bin_csv": str(bins_csv),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response-dir", type=Path, required=True)
    parser.add_argument("--efficiency-csv", type=Path, required=True)
    parser.add_argument("--reference-bridge-dir", type=Path)
    parser.add_argument("--spectrum-dir", type=Path, default=Path(
        "research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum"
    ))
    parser.add_argument("--response-families", nargs="+", choices=RESPONSE_FAMILIES, default=list(RESPONSE_FAMILIES))
    parser.add_argument("--benchmarks", nargs="+", choices=BENCHMARKS, default=list(BENCHMARKS))
    parser.add_argument("--nuclear-models", nargs="+", choices=NUCLEAR_MODELS, default=list(NUCLEAR_MODELS))
    parser.add_argument("--source-run-id", type=int, default=43697104437)
    parser.add_argument("--source-artifact-id", type=int, default=14155360851)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    summary = run_audit(args)
    outputs = write_outputs(summary, args.out_dir)
    print(json.dumps({
        "status": summary["status"],
        "integrated_bridge_reproduction_max_abs_difference": summary["integrated_bridge_reproduction_max_abs_difference"],
        "n_summary_rows": len(summary["per_key_summaries"]),
        "n_energy_bin_rows": len(summary["per_energy_bin_rows"]),
        "outputs": outputs,
    }, indent=2))


if __name__ == "__main__":
    main()
