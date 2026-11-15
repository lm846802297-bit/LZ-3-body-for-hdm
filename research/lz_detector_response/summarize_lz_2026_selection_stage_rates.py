#!/usr/bin/env python3
"""Integrate LZ Fig. S2 cumulative selection efficiencies against three-body spectra.

The product of the piecewise-linear recoil spectrum and piecewise-linear
cumulative efficiency is quadratic on each interval. This script integrates
that product analytically on the union of both knot sets and cross-checks the
final result against the archived rate-level event-yield table.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import json
import math
from pathlib import Path
from typing import Iterable

CURVE_COLUMNS = (
    "trigger_cumulative",
    "trigger_plus_s1_threshold_cumulative",
    "trigger_plus_s1_ss_analysis_cumulative",
    "final_plus_roi_cumulative",
)
CURVE_LABELS = (
    "trigger",
    "trigger_plus_s1",
    "trigger_plus_s1_ss_analysis",
    "final_plus_roi",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def interp_piecewise_linear(xs: list[float], ys: list[float], x: float) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("piecewise-linear interpolation requires matching arrays with >=2 points")
    if x < xs[0] - 1e-12 or x > xs[-1] + 1e-12:
        raise ValueError(f"interpolation point {x} is outside [{xs[0]}, {xs[-1]}]")
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    i = bisect.bisect_right(xs, x) - 1
    dx = xs[i + 1] - xs[i]
    if dx <= 0:
        raise ValueError("x knots must be strictly increasing")
    t = (x - xs[i]) / dx
    return ys[i] + t * (ys[i + 1] - ys[i])


def integrate_piecewise_linear_product(
    spectrum_x: list[float],
    spectrum_y: list[float],
    efficiency_x: list[float],
    efficiency_y: list[float],
    lo: float,
    hi: float,
) -> float:
    """Exact integral of two piecewise-linear functions over [lo, hi]."""
    if not (math.isfinite(lo) and math.isfinite(hi) and hi > lo):
        raise ValueError("integration interval must be finite and increasing")
    if len(spectrum_x) != len(spectrum_y) or len(efficiency_x) != len(efficiency_y):
        raise ValueError("x/y knot lengths differ")
    if len(spectrum_x) < 2 or len(efficiency_x) < 2:
        raise ValueError("both interpolants need at least two knots")
    if any(b <= a for a, b in zip(spectrum_x, spectrum_x[1:])):
        raise ValueError("spectrum knots must be strictly increasing")
    if any(b <= a for a, b in zip(efficiency_x, efficiency_x[1:])):
        raise ValueError("efficiency knots must be strictly increasing")
    if lo < spectrum_x[0] or hi > spectrum_x[-1]:
        raise ValueError("integration interval exceeds the spectrum knot range")
    if lo < efficiency_x[0] or hi > efficiency_x[-1]:
        raise ValueError("integration interval exceeds the efficiency knot range")

    knots = sorted({
        lo,
        hi,
        *(x for x in spectrum_x if lo < x < hi),
        *(x for x in efficiency_x if lo < x < hi),
    })
    total = 0.0
    for left, right in zip(knots, knots[1:]):
        width = right - left
        r0 = interp_piecewise_linear(spectrum_x, spectrum_y, left)
        r1 = interp_piecewise_linear(spectrum_x, spectrum_y, right)
        e0 = interp_piecewise_linear(efficiency_x, efficiency_y, left)
        e1 = interp_piecewise_linear(efficiency_x, efficiency_y, right)
        dr = (r1 - r0) / width
        de = (e1 - e0) / width
        total += (
            r0 * e0 * width
            + 0.5 * (r0 * de + e0 * dr) * width**2
            + (dr * de / 3.0) * width**3
        )
    return total


def validate_cumulative_curves(rows: list[dict[str, str]]) -> None:
    for row in rows:
        values = [float(row[key]) for key in CURVE_COLUMNS]
        if any(not math.isfinite(v) or v < -1e-8 or v > 1.0 + 1e-8 for v in values):
            raise ValueError(f"invalid cumulative efficiency at ER={row['ER_keV']}")
        trigger, s1, ss, final = values
        if not (final <= ss + 1e-7 and ss <= s1 + 1e-7 and s1 <= trigger + 1e-7):
            raise ValueError(f"cumulative curves are not nested at ER={row['ER_keV']}")


def summarize(
    spectrum_dir: Path,
    efficiency_csv: Path,
    rate_level_csv: Path,
    relative_tolerance: float,
) -> dict:
    efficiency_rows = read_csv(efficiency_csv)
    validate_cumulative_curves(efficiency_rows)
    efficiency_rows.sort(key=lambda row: float(row["ER_keV"]))
    efficiency_x = [float(row["ER_keV"]) for row in efficiency_rows]
    efficiency = {
        label: [float(row[column]) for row in efficiency_rows]
        for label, column in zip(CURVE_LABELS, CURVE_COLUMNS)
    }

    rate_rows = read_csv(rate_level_csv)
    reference = {
        (row["benchmark"], row["model"], row["halo_model"]): row
        for row in rate_rows
    }
    if len(reference) != len(rate_rows):
        raise ValueError("duplicate benchmark/model/halo_model rows in rate-level reference")

    results: list[dict] = []
    for benchmark_dir in sorted(p for p in spectrum_dir.iterdir() if p.is_dir()):
        spectrum_path = benchmark_dir / "natural_xenon_continuous_spectrum.csv"
        if not spectrum_path.exists():
            continue
        rows = read_csv(spectrum_path)
        for model in ("GCN", "JJ55"):
            selected = [
                row for row in rows
                if row["model"] == model and row["halo_model"] == "shm_cutoff"
            ]
            if len(selected) < 2:
                raise ValueError(f"missing spectrum rows for {benchmark_dir.name}/{model}")
            selected.sort(key=lambda row: float(row["ER_keV"]))
            spectrum_x = [float(row["ER_keV"]) for row in selected]
            spectrum_y = [float(row["rate_events_kg_day_keV"]) for row in selected]
            key = (benchmark_dir.name, model, "shm_cutoff")
            if key not in reference:
                raise ValueError(f"no rate-level reference row for {key}")
            ref = reference[key]
            lo = float(ref["roi_min_keV"])
            hi = float(ref["roi_max_keV"])
            exposure = float(ref["exposure_kg_day"])

            raw_rate = integrate_piecewise_linear_product(
                spectrum_x, spectrum_y, efficiency_x,
                [1.0] * len(efficiency_x), lo, hi
            )
            stage_rates = {
                label: integrate_piecewise_linear_product(
                    spectrum_x, spectrum_y, efficiency_x, efficiency[label], lo, hi
                )
                for label in CURVE_LABELS
            }
            expected_raw = float(ref["raw_roi_integral_events_kg_day"])
            expected_final_events = float(ref["expected_events_in_high_efficiency_window"])
            raw_rel_diff = abs(raw_rate - expected_raw) / max(abs(expected_raw), 1e-300)
            final_events = stage_rates["final_plus_roi"] * exposure
            final_rel_diff = abs(final_events - expected_final_events) / max(abs(expected_final_events), 1e-300)
            if raw_rel_diff > relative_tolerance:
                raise ValueError(f"raw-rate closure failed for {key}: {raw_rel_diff}")
            if final_rel_diff > relative_tolerance:
                raise ValueError(f"Fig. S2 final-yield closure failed for {key}: {final_rel_diff}")

            cumulative_events = {
                label: stage_rates[label] * exposure for label in CURVE_LABELS
            }
            conditional = {
                "trigger": stage_rates["trigger"] / raw_rate if raw_rate else 0.0,
                "s1_given_trigger": (
                    stage_rates["trigger_plus_s1"] / stage_rates["trigger"]
                    if stage_rates["trigger"] else 0.0
                ),
                "ss_analysis_given_s1": (
                    stage_rates["trigger_plus_s1_ss_analysis"]
                    / stage_rates["trigger_plus_s1"]
                    if stage_rates["trigger_plus_s1"] else 0.0
                ),
                "roi_given_ss_analysis": (
                    stage_rates["final_plus_roi"]
                    / stage_rates["trigger_plus_s1_ss_analysis"]
                    if stage_rates["trigger_plus_s1_ss_analysis"] else 0.0
                ),
                "total_final": stage_rates["final_plus_roi"] / raw_rate if raw_rate else 0.0,
            }
            results.append({
                "benchmark": benchmark_dir.name,
                "model": model,
                "halo_model": "shm_cutoff",
                "roi_min_keV": lo,
                "roi_max_keV": hi,
                "exposure_kg_day": exposure,
                "raw_rate_events_kg_day": raw_rate,
                "stage_rate_events_kg_day": stage_rates,
                "raw_expected_events": raw_rate * exposure,
                "stage_expected_events": cumulative_events,
                "conditional_stage_efficiencies": conditional,
                "reference_final_expected_events": expected_final_events,
                "raw_rate_relative_closure": raw_rel_diff,
                "final_expected_events_relative_closure": final_rel_diff,
            })

    if len(results) != len(rate_rows):
        raise ValueError(f"processed {len(results)} spectra but found {len(rate_rows)} reference rows")
    return {
        "study": "LZ 2026 rate-level Fig. S2 selection-stage closure",
        "method": "exact analytic integration of the product of piecewise-linear spectrum and efficiency on the union of knots",
        "efficiency_points": len(efficiency_rows),
        "relative_closure_tolerance": relative_tolerance,
        "max_raw_rate_relative_closure": max(r["raw_rate_relative_closure"] for r in results),
        "max_final_expected_events_relative_closure": max(
            r["final_expected_events_relative_closure"] for r in results
        ),
        "n_results": len(results),
        "results": results,
        "interpretation": (
            "This is a one-dimensional rate-level efficiency closure. It does not "
            "supply the two-dimensional (S1c, log10 S2c) migration kernel or the "
            "full BACCARAT/GEANT4 event-selection response."
        ),
    }


def write_csv(path: Path, results: Iterable[dict]) -> None:
    fields = [
        "benchmark", "model", "raw_expected_events",
        "trigger_expected_events", "trigger_plus_s1_expected_events",
        "trigger_plus_s1_ss_analysis_expected_events", "final_plus_roi_expected_events",
        "trigger_efficiency", "s1_given_trigger_efficiency",
        "ss_analysis_given_s1_efficiency", "roi_given_ss_analysis_efficiency",
        "total_final_efficiency", "raw_rate_relative_closure",
        "final_expected_events_relative_closure",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in results:
            stage = row["stage_expected_events"]
            cond = row["conditional_stage_efficiencies"]
            writer.writerow({
                "benchmark": row["benchmark"],
                "model": row["model"],
                "raw_expected_events": row["raw_expected_events"],
                "trigger_expected_events": stage["trigger"],
                "trigger_plus_s1_expected_events": stage["trigger_plus_s1"],
                "trigger_plus_s1_ss_analysis_expected_events": stage["trigger_plus_s1_ss_analysis"],
                "final_plus_roi_expected_events": stage["final_plus_roi"],
                "trigger_efficiency": cond["trigger"],
                "s1_given_trigger_efficiency": cond["s1_given_trigger"],
                "ss_analysis_given_s1_efficiency": cond["ss_analysis_given_s1"],
                "roi_given_ss_analysis_efficiency": cond["roi_given_ss_analysis"],
                "total_final_efficiency": cond["total_final"],
                "raw_rate_relative_closure": row["raw_rate_relative_closure"],
                "final_expected_events_relative_closure": row["final_expected_events_relative_closure"],
            })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spectrum-dir", type=Path, required=True)
    parser.add_argument("--efficiency-components", type=Path, required=True)
    parser.add_argument("--rate-level-counts", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--relative-tolerance", type=float, default=1e-8)
    args = parser.parse_args()

    result = summarize(
        args.spectrum_dir,
        args.efficiency_components,
        args.rate_level_counts,
        args.relative_tolerance,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "selection_stage_rate_level_summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    write_csv(args.output_dir / "selection_stage_rate_level_summary.csv", result["results"])
    print(json.dumps({
        "n_results": result["n_results"],
        "max_raw_rate_relative_closure": result["max_raw_rate_relative_closure"],
        "max_final_expected_events_relative_closure": result["max_final_expected_events_relative_closure"],
        "output_dir": str(args.output_dir),
    }, indent=2))


if __name__ == "__main__":
    main()
