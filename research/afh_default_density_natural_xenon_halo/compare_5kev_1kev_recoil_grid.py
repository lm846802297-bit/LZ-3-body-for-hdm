#!/usr/bin/env python3
"""Compare 5-keV and 1-keV natural-xenon three-body recoil spectra.

The comparison is performed before detector response, and again after folding
with the published one-dimensional LZ 2026 final-ROI efficiency.  It does not
construct a 2D likelihood or apply any additional event-selection efficiency.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any
import sys

HERE = Path(__file__).resolve().parent
FIG_DIR = HERE.parents[1] / "figure2_full_reproduction"
sys.path.insert(0, str(FIG_DIR))

from fold_lz_2026_rate_level import (
    candidate_tail_bounds,
    integrate_piecewise_linear_product,
    read_efficiency_curves,
)

DEFAULT_EFFICIENCY = (
    HERE.parents[1]
    / "lz_detector_response"
    / "lz_2026_extended_nr"
    / "lz_2026_nr_efficiency_digitized.csv"
)
SCENARIOS = ("AFH-7", "Hybrid-9 (AFH-7 + Helm-2)")
SELECTED_CHECK_ENERGIES_KEV = (101.0, 200.0, 267.0, 542.0)
ROI_KEV = (5.4, 269.9)
EXPOSURE_TONNE_YEAR = 2.84
KG_DAY_PER_TONNE_YEAR = 1000.0 * 365.25

# Numerical acceptance is intentionally applied to integrated quantities,
# not to the pointwise difference between non-common interpolation nodes.
TOLERANCES = {
    "common_node_rate_relative": 1.0e-10,
    "roi_raw_integral_relative": 5.0e-3,
    "roi_efficiency_weighted_relative": 5.0e-3,
    "tail_efficiency_weighted_relative": 1.0e-2,
    "peak_height_relative": 1.0e-2,
    "peak_position_shift_keV": 1.0,
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def expected_recoil_grid(step_keV: int) -> list[float]:
    if step_keV not in (1, 5):
        raise ValueError("only 1-keV and 5-keV fine grids are supported")
    fine_count = int(round((270.0 - 5.0) / step_keV))
    fine = [5.0 + i * step_keV for i in range(fine_count + 1)]
    high = [280.0 + 20.0 * i for i in range(27)]
    return sorted(set(fine + high + list(SELECTED_CHECK_ENERGIES_KEV)))


def read_metadata(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("status") != "PASS":
        raise ValueError(f"{path}: source spectrum metadata is not PASS")
    if obj.get("detector_response_applied") is not False:
        raise ValueError(f"{path}: expected a pre-detector spectrum")
    return obj


def read_spectrum(path: Path) -> dict[tuple[str, str], list[dict[str, float]]]:
    required = {
        "benchmark", "scenario", "ER_keV", "rate_events_kg_day_keV",
        "weighted_cross_section_integral_GeVminus3", "detector_response_applied",
    }
    groups: dict[tuple[str, str], list[dict[str, float]]] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        for row in reader:
            scenario = row["scenario"]
            if scenario not in SCENARIOS:
                continue
            if row["detector_response_applied"].strip().lower() not in {"false", "0"}:
                raise ValueError(f"{path}: input already has detector response")
            key = (row["benchmark"], scenario)
            item = {
                "ER_keV": float(row["ER_keV"]),
                "rate": float(row["rate_events_kg_day_keV"]),
                "kernel": float(row["weighted_cross_section_integral_GeVminus3"]),
            }
            if not all(math.isfinite(v) for v in item.values()):
                raise ValueError(f"{path}: non-finite spectrum value in {key}")
            if item["rate"] < 0.0 or item["kernel"] < 0.0:
                raise ValueError(f"{path}: negative rate/kernel in {key}")
            groups.setdefault(key, []).append(item)

    if not groups:
        raise ValueError(f"{path}: no AFH-7 or Hybrid-9 groups found")
    for key, rows in groups.items():
        rows.sort(key=lambda r: r["ER_keV"])
        energies = [r["ER_keV"] for r in rows]
        if any(b <= a for a, b in zip(energies, energies[1:])):
            raise ValueError(f"{path}: duplicate or unordered energies in {key}")
    return groups


def relative_difference(a: float, b: float) -> float:
    return abs(a - b) / max(abs(b), 1.0e-300)


def _integral(
    rows: list[dict[str, float]],
    efficiency_x: list[float],
    efficiency_y: list[float],
    lo: float,
    hi: float,
) -> tuple[float, float]:
    xs = [r["ER_keV"] for r in rows]
    ys = [r["rate"] for r in rows]
    return integrate_piecewise_linear_product(xs, ys, efficiency_x, efficiency_y, lo, hi)


def compare_group(
    coarse: list[dict[str, float]],
    fine: list[dict[str, float]],
    efficiency_x: list[float],
    efficiency_central: list[float],
    efficiency_lower: list[float],
    efficiency_upper: list[float],
    roi: tuple[float, float] = ROI_KEV,
) -> dict[str, Any]:
    coarse = sorted(coarse, key=lambda r: r["ER_keV"])
    fine = sorted(fine, key=lambda r: r["ER_keV"])
    c_by_e = {r["ER_keV"]: r for r in coarse}
    f_by_e = {r["ER_keV"]: r for r in fine}
    common = sorted(set(c_by_e).intersection(f_by_e))
    if len(common) != len(coarse):
        raise ValueError("the 1-keV grid must contain every 5-keV grid node")
    common_max = max(
        relative_difference(c_by_e[e]["rate"], f_by_e[e]["rate"])
        for e in common
    )
    common_kernel_max = max(
        relative_difference(c_by_e[e]["kernel"], f_by_e[e]["kernel"])
        for e in common
    )

    raw5, weighted5 = _integral(coarse, efficiency_x, efficiency_central, *roi)
    raw1, weighted1 = _integral(fine, efficiency_x, efficiency_central, *roi)
    _, lower5 = _integral(coarse, efficiency_x, efficiency_lower, *roi)
    _, lower1 = _integral(fine, efficiency_x, efficiency_lower, *roi)
    _, upper5 = _integral(coarse, efficiency_x, efficiency_upper, *roi)
    _, upper1 = _integral(fine, efficiency_x, efficiency_upper, *roi)

    tail = candidate_tail_bounds(*roi)
    _, tail5 = _integral(coarse, efficiency_x, efficiency_central, *tail)
    _, tail1 = _integral(fine, efficiency_x, efficiency_central, *tail)

    roi_coarse = [r for r in coarse if roi[0] <= r["ER_keV"] <= roi[1]]
    roi_fine = [r for r in fine if roi[0] <= r["ER_keV"] <= roi[1]]
    peak5 = max(roi_coarse, key=lambda r: r["rate"])
    peak1 = max(roi_fine, key=lambda r: r["rate"])
    peak_height_rel = relative_difference(peak5["rate"], peak1["rate"])
    peak_shift = abs(peak5["ER_keV"] - peak1["ER_keV"])

    exposure = EXPOSURE_TONNE_YEAR * KG_DAY_PER_TONNE_YEAR
    metrics = {
        "common_node_count": len(common),
        "common_node_max_relative_rate_difference": common_max,
        "common_node_max_relative_kernel_difference": common_kernel_max,
        "roi_raw_integral_5keV_events_kg_day": raw5,
        "roi_raw_integral_1keV_events_kg_day": raw1,
        "roi_raw_integral_relative_difference": relative_difference(raw5, raw1),
        "roi_efficiency_weighted_5keV_events_kg_day": weighted5,
        "roi_efficiency_weighted_1keV_events_kg_day": weighted1,
        "roi_efficiency_weighted_relative_difference": relative_difference(weighted5, weighted1),
        "roi_lower_envelope_relative_difference": relative_difference(lower5, lower1),
        "roi_upper_envelope_relative_difference": relative_difference(upper5, upper1),
        "tail_interval_keV": list(tail),
        "tail_weighted_5keV_events_kg_day": tail5,
        "tail_weighted_1keV_events_kg_day": tail1,
        "tail_weighted_relative_difference": relative_difference(tail5, tail1),
        "mean_efficiency_5keV": weighted5 / raw5 if raw5 > 0.0 else 0.0,
        "mean_efficiency_1keV": weighted1 / raw1 if raw1 > 0.0 else 0.0,
        "expected_events_5keV_at_2p84_tonne_year": exposure * weighted5,
        "expected_events_1keV_at_2p84_tonne_year": exposure * weighted1,
        "peak_ER_5keV_keV": peak5["ER_keV"],
        "peak_ER_1keV_keV": peak1["ER_keV"],
        "peak_position_shift_keV": peak_shift,
        "peak_height_relative_difference": peak_height_rel,
    }
    passed = (
        common_max <= TOLERANCES["common_node_rate_relative"]
        and metrics["roi_raw_integral_relative_difference"] <= TOLERANCES["roi_raw_integral_relative"]
        and metrics["roi_efficiency_weighted_relative_difference"] <= TOLERANCES["roi_efficiency_weighted_relative"]
        and metrics["tail_weighted_relative_difference"] <= TOLERANCES["tail_efficiency_weighted_relative"]
        and peak_height_rel <= TOLERANCES["peak_height_relative"]
        and peak_shift <= TOLERANCES["peak_position_shift_keV"]
    )
    metrics["status"] = "PASS" if passed else "FAIL"
    return metrics


def compare_runs(
    coarse_csv: Path,
    coarse_metadata: Path,
    fine_csv: Path,
    fine_metadata: Path,
    efficiency_csv: Path,
) -> dict[str, Any]:
    m5 = read_metadata(coarse_metadata)
    m1 = read_metadata(fine_metadata)
    g5 = read_spectrum(coarse_csv)
    g1 = read_spectrum(fine_csv)

    grid5 = expected_recoil_grid(5)
    grid1 = expected_recoil_grid(1)
    if m5["recoil_grid_keV"]["points"] != len(grid5):
        raise ValueError("5-keV metadata point count does not match the declared grid")
    if m1["recoil_grid_keV"]["points"] != len(grid1):
        raise ValueError("1-keV metadata point count does not match the declared grid")
    if not math.isclose(float(m5["recoil_grid_keV"]["fine_step"]), 5.0):
        raise ValueError("coarse metadata does not declare a 5-keV step")
    if not math.isclose(float(m1["recoil_grid_keV"]["fine_step"]), 1.0):
        raise ValueError("fine metadata does not declare a 1-keV step")
    if m5["recoil_grid_keV"]["fine_max"] != m1["recoil_grid_keV"]["fine_max"]:
        raise ValueError("fine-grid upper energy differs between runs")
    if m5["recoil_grid_keV"]["high_energy_step"] != m1["recoil_grid_keV"]["high_energy_step"]:
        raise ValueError("high-energy coarse step differs between runs")
    for key in ("particle_parameters", "halo", "quadrature", "response_convention"):
        if m5.get(key) != m1.get(key):
            raise ValueError(f"run settings differ between 5-keV and 1-keV runs: {key}")

    expected_keys = {
        (benchmark, scenario)
        for benchmark in m5["particle_parameters"]["benchmarks"]
        for scenario in SCENARIOS
    }
    if set(g5) != expected_keys or set(g1) != expected_keys:
        raise ValueError(
            f"unexpected spectrum groups: 5-keV missing={sorted(expected_keys-set(g5))}; "
            f"1-keV missing={sorted(expected_keys-set(g1))}"
        )
    for key, expected in ((key, grid5) for key in expected_keys):
        got = [r["ER_keV"] for r in g5[key]]
        if got != expected:
            raise ValueError(f"5-keV energy grid mismatch in {key}")
    for key, expected in ((key, grid1) for key in expected_keys):
        got = [r["ER_keV"] for r in g1[key]]
        if got != expected:
            raise ValueError(f"1-keV energy grid mismatch in {key}")

    ex, ec, elo, ehi = read_efficiency_curves(efficiency_csv)
    roi = ROI_KEV
    if ex[0] > roi[0] or ex[-1] < roi[1]:
        raise ValueError("published efficiency curve does not cover the LZ WS ROI")

    results = []
    for benchmark in m5["particle_parameters"]["benchmarks"]:
        for scenario in SCENARIOS:
            results.append({
                "benchmark": benchmark,
                "scenario": scenario,
                **compare_group(g5[(benchmark, scenario)], g1[(benchmark, scenario)], ex, ec, elo, ehi, roi),
            })
    summary = {
        "status": "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL",
        "calculation": "natural-xenon halo-folded three-body recoil spectrum",
        "coarse_grid": {
            "fine_ER_keV": "5, 10, ..., 270",
            "high_ER_keV": "280, 300, ..., 800",
            "selected_extra_points_keV": list(SELECTED_CHECK_ENERGIES_KEV),
            "point_count_per_group": len(grid5),
        },
        "fine_grid": {
            "fine_ER_keV": "5, 6, ..., 270",
            "high_ER_keV": "280, 300, ..., 800",
            "selected_extra_points_keV": list(SELECTED_CHECK_ENERGIES_KEV),
            "point_count_per_group": len(grid1),
        },
        "common_grid_point_count": len(set(grid5).intersection(grid1)),
        "roi_keV": list(roi),
        "exposure_tonne_year": EXPOSURE_TONNE_YEAR,
        "efficiency_source": str(efficiency_csv),
        "efficiency_source_sha256": sha256_file(efficiency_csv),
        "tolerances": TOLERANCES,
        "scope": [
            "natural-xenon AFH-7 and Hybrid-9 spectra",
            "same particle, halo, nuclear response, and phase-space quadrature settings",
            "common-node comparison before detector efficiency",
            "exact piecewise-linear integration against the published one-dimensional LZ final-ROI efficiency",
            "no 2D detector PDF, background model, profile likelihood, or exclusion limit",
        ],
        "benchmarks": results,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--five-kev-csv", type=Path, required=True)
    parser.add_argument("--five-kev-metadata", type=Path, required=True)
    parser.add_argument("--one-kev-csv", type=Path, required=True)
    parser.add_argument("--one-kev-metadata", type=Path, required=True)
    parser.add_argument("--efficiency-csv", type=Path, default=DEFAULT_EFFICIENCY)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    result = compare_runs(
        args.five_kev_csv, args.five_kev_metadata,
        args.one_kev_csv, args.one_kev_metadata,
        args.efficiency_csv,
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.out_dir / "recoil_grid_5keV_vs_1keV_summary.csv"
    json_path = args.out_dir / "recoil_grid_5keV_vs_1keV_summary.json"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        fields = ["benchmark", "scenario"] + sorted(
            key for key in result["benchmarks"][0] if key not in {"benchmark", "scenario"}
        )
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["benchmarks"])
    result["output"] = {
        "summary_csv": str(csv_path),
        "summary_csv_sha256": sha256_file(csv_path),
    }
    json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    result["output"]["summary_json"] = str(json_path)
    result["output"]["summary_json_sha256"] = sha256_file(json_path)
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
