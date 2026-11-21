#!/usr/bin/env python3
"""Fold AFH-7 and Hybrid-9 natural-xenon spectra with LZ 2026 NR efficiency.

Rate-level fold only: no nuclear response or three-body phase-space integral
is recomputed here.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

from fold_lz_2026_rate_level import (
    candidate_tail_bounds,
    integrate_piecewise_linear_product,
    integrate_weighted_rate,
    read_efficiency_curves,
    sha256,
)

DEFAULT_SPECTRUM = Path(
    "research/afh_default_density_natural_xenon_halo/results/"
    "afh7_hybrid9_continuous_2026-11-14/"
    "afh_hybrid9_natural_xenon_spectrum.csv"
)
DEFAULT_SPECTRUM_METADATA = DEFAULT_SPECTRUM.with_name("metadata.json")
DEFAULT_EFFICIENCY = Path(
    "research/lz_detector_response/lz_2026_extended_nr/"
    "lz_2026_nr_efficiency_digitized.csv"
)
SCENARIOS = ("AFH-7", "Hybrid-9 (AFH-7 + Helm-2)")
SCENARIO_DESCRIPTIONS = {
    "AFH-7": (
        "AFH v6.0 default-density responses for Xe-128, Xe-129, Xe-130, "
        "Xe-131, Xe-132, Xe-134 and Xe-136; Xe-124/Xe-126 omitted without "
        "renormalizing the remaining natural abundances."
    ),
    "Hybrid-9 (AFH-7 + Helm-2)": (
        "AFH v6.0 for the seven supported isotopes; Helm is used only as an "
        "explicitly labelled fallback for Xe-124 and Xe-126."
    ),
}
CONSTANT_NUMERIC_FIELDS = (
    "coupling_product_sq", "mchi_GeV", "mV_GeV", "g2_for_pole_width",
    "rhoDM_GeV_cm3", "vmax_km_s", "available_atom_fraction",
    "missing_atom_fraction", "A2_weighted_AFH_coverage_at_q0",
)
CONSTANT_TEXT_FIELDS = ("mass_scheme", "response_q_convention", "width_scheme")


def _as_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def read_selected_spectrum_groups(path: Path) -> dict[tuple[str, str], list[dict[str, str]]]:
    """Read AFH-7 and Hybrid-9 only, validating each spectrum group."""
    required = {
        "benchmark", "scenario", "ER_keV", "rate_events_kg_day_keV",
        "coupling_product_sq", "mchi_GeV", "mV_GeV", "g2_for_pole_width",
        "rhoDM_GeV_cm3", "vmax_km_s", "available_atom_fraction",
        "missing_atom_fraction", "A2_weighted_AFH_coverage_at_q0",
        "mass_scheme", "response_q_convention", "width_scheme",
        "detector_response_applied",
    }
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Spectrum CSV is missing columns: {sorted(missing)}")
        for row in reader:
            scenario = row["scenario"]
            if scenario not in SCENARIOS:
                continue
            benchmark = row["benchmark"]
            if not benchmark:
                raise ValueError("Empty benchmark label in spectrum CSV")
            if _as_bool(row["detector_response_applied"]):
                raise ValueError(
                    "Input spectrum already contains detector efficiency; refusing to fold it twice"
                )
            energy = float(row["ER_keV"])
            rate = float(row["rate_events_kg_day_keV"])
            if not (math.isfinite(energy) and math.isfinite(rate) and rate >= 0.0):
                raise ValueError(f"Invalid energy or rate in {benchmark}/{scenario}")
            groups[(benchmark, scenario)].append(row)

    if not groups:
        raise ValueError(f"No AFH-7 or Hybrid-9 spectra found in {path}")
    for key, rows in groups.items():
        rows.sort(key=lambda row: float(row["ER_keV"]))
        energies = [float(row["ER_keV"]) for row in rows]
        if len(energies) < 2 or any(b <= a for a, b in zip(energies, energies[1:])):
            raise ValueError(f"{key}: recoil energies must be unique and strictly increasing")
        for field in CONSTANT_NUMERIC_FIELDS:
            values = [float(row[field]) for row in rows]
            if any(not math.isfinite(value) for value in values):
                raise ValueError(f"{key}: non-finite metadata field {field}")
            if any(not math.isclose(value, values[0], rel_tol=1e-12, abs_tol=1e-15)
                   for value in values[1:]):
                raise ValueError(f"{key}: {field} changes across recoil energies")
        for field in CONSTANT_TEXT_FIELDS:
            values = [row[field] for row in rows]
            if any(value != values[0] for value in values[1:]):
                raise ValueError(f"{key}: {field} changes across recoil energies")
        if any(row["response_q_convention"] != "exact spatial q" for row in rows):
            raise ValueError(f"{key}: expected exact spatial-q response convention")
    return dict(groups)


def fold_one_group(
    benchmark: str,
    scenario: str,
    rows: list[dict[str, str]],
    efficiency_x: list[float],
    efficiency_central: list[float],
    efficiency_lower: list[float],
    efficiency_upper: list[float],
    benchmark_parameters: dict[str, float],
    roi_min_keV: float,
    roi_max_keV: float,
    exposure_tonne_year: float,
    integration_steps: int,
    candidate_interval: tuple[float, float] | None = None,
) -> tuple[dict[str, Any], float, float]:
    """Fold one pre-detector spectrum and return row plus quadrature diagnostics."""
    rows = sorted(rows, key=lambda row: float(row["ER_keV"]))
    rate_x = [float(row["ER_keV"]) for row in rows]
    rate_y = [float(row["rate_events_kg_day_keV"]) for row in rows]
    if len(rate_x) < 2 or any(b <= a for a, b in zip(rate_x, rate_x[1:])):
        raise ValueError(f"{benchmark}/{scenario}: invalid recoil grid")
    if rate_x[0] > roi_min_keV or rate_x[-1] < roi_max_keV:
        raise ValueError(f"{benchmark}/{scenario}: spectrum does not cover the full ROI")

    raw_integral, weighted = integrate_piecewise_linear_product(
        rate_x, rate_y, efficiency_x, efficiency_central, roi_min_keV, roi_max_keV
    )
    _, weighted_lower = integrate_piecewise_linear_product(
        rate_x, rate_y, efficiency_x, efficiency_lower, roi_min_keV, roi_max_keV
    )
    _, weighted_upper = integrate_piecewise_linear_product(
        rate_x, rate_y, efficiency_x, efficiency_upper, roi_min_keV, roi_max_keV
    )
    tail_min, tail_max = candidate_interval or candidate_tail_bounds(roi_min_keV, roi_max_keV)
    _, weighted_tail = integrate_piecewise_linear_product(
        rate_x, rate_y, efficiency_x, efficiency_central, tail_min, tail_max
    )
    _, weighted_dense = integrate_weighted_rate(
        rate_x, rate_y, efficiency_x, efficiency_central,
        roi_min_keV, roi_max_keV, integration_steps
    )
    _, weighted_dense_fine = integrate_weighted_rate(
        rate_x, rate_y, efficiency_x, efficiency_central,
        roi_min_keV, roi_max_keV, 2 * integration_steps
    )
    dense_vs_exact = abs(weighted_dense / weighted - 1.0) if weighted > 0.0 else 0.0
    refinement = (
        abs(weighted_dense_fine / weighted_dense - 1.0)
        if weighted_dense > 0.0 else 0.0
    )

    reference = rows[0]
    exposure_kg_day = exposure_tonne_year * 1000.0 * 365.25
    expected = exposure_kg_day * weighted
    expected_lower = exposure_kg_day * weighted_lower
    expected_upper = exposure_kg_day * weighted_upper
    coupling_sq = float(reference["coupling_product_sq"])
    raw_events = exposure_kg_day * raw_integral
    output = {
        "benchmark": benchmark,
        "scenario": scenario,
        "ms_MeV": float(benchmark_parameters["ms_MeV"]),
        "delta_m_MeV": float(benchmark_parameters["delta_m_MeV"]),
        "roi_min_keV": roi_min_keV,
        "roi_max_keV": roi_max_keV,
        "exposure_tonne_year": exposure_tonne_year,
        "exposure_kg_day": exposure_kg_day,
        "spectrum_point_count": len(rows),
        "raw_roi_integral_events_kg_day": raw_integral,
        "efficiency_weighted_integral_events_kg_day": weighted,
        "spectrum_weighted_mean_efficiency": weighted / raw_integral if raw_integral > 0 else 0.0,
        "spectrum_weighted_mean_efficiency_lower_envelope": weighted_lower / raw_integral if raw_integral > 0 else 0.0,
        "spectrum_weighted_mean_efficiency_upper_envelope": weighted_upper / raw_integral if raw_integral > 0 else 0.0,
        "efficiency_envelope_treatment": "gray detector-systematic range; no confidence level assigned by LZ",
        "integration_method": "exact analytic integral of piecewise-linear rate times piecewise-linear efficiency over the union of input knots",
        "dense_trapezoid_relative_difference_vs_exact": dense_vs_exact,
        "dense_trapezoid_refinement_relative_difference": refinement,
        "ideal_100pct_efficiency_events_in_window": raw_events,
        "expected_events_in_high_efficiency_window": expected,
        "expected_events_efficiency_lower_envelope": expected_lower,
        "expected_events_efficiency_upper_envelope": expected_upper,
        "candidate_tail_min_keV": tail_min,
        "candidate_tail_max_keV": tail_max,
        "expected_events_in_candidate_statistical_slice": exposure_kg_day * weighted_tail,
        "fraction_expected_events_in_candidate_statistical_slice": weighted_tail / weighted if weighted > 0 else 0.0,
        "coupling_product_sq_reference": coupling_sq,
        "coupling_product_sq_for_one_expected_event_at_fixed_g2": coupling_sq / expected if expected > 0 else None,
        "coupling_product_sq_for_one_event_lower_envelope": coupling_sq / expected_lower if expected_lower > 0 else None,
        "coupling_product_sq_for_one_event_upper_envelope": coupling_sq / expected_upper if expected_upper > 0 else None,
        "mchi_GeV": float(reference["mchi_GeV"]),
        "mV_GeV": float(reference["mV_GeV"]),
        "g2_for_conditional_pole_width": float(reference["g2_for_pole_width"]),
        "rhoDM_GeV_cm3": float(reference["rhoDM_GeV_cm3"]),
        "vmax_km_s": float(reference["vmax_km_s"]),
        "available_atom_fraction": float(reference["available_atom_fraction"]),
        "missing_atom_fraction": float(reference["missing_atom_fraction"]),
        "A2_weighted_AFH_coverage_at_q0": float(reference["A2_weighted_AFH_coverage_at_q0"]),
        "mass_scheme": reference["mass_scheme"],
        "response_q_convention": reference["response_q_convention"],
        "width_scheme": reference["width_scheme"],
        "detector_efficiency_applied": True,
        "energy_resolution_smearing_applied": False,
        "two_dimensional_signal_pdf_applied": False,
        "background_likelihood_applied": False,
        "is_exclusion_limit": False,
    }
    return output, dense_vs_exact, refinement


def run_fold(
    spectrum_csv: Path,
    spectrum_metadata_path: Path,
    efficiency_csv: Path,
    out_dir: Path,
    roi_min_keV: float = 5.4,
    roi_max_keV: float = 269.9,
    exposure_tonne_year: float = 2.84,
    integration_steps: int = 10000,
) -> dict[str, Any]:
    """Run, validate and archive the AFH-7/Hybrid-9 efficiency fold."""
    for path in (spectrum_csv, spectrum_metadata_path, efficiency_csv):
        if not path.is_file():
            raise FileNotFoundError(path)
    if not (roi_min_keV < roi_max_keV and exposure_tonne_year > 0.0):
        raise ValueError("Invalid ROI or exposure")
    if integration_steps < 2:
        raise ValueError("integration_steps must be at least 2")

    source_metadata = json.loads(spectrum_metadata_path.read_text(encoding="utf-8"))
    if source_metadata.get("status") != "PASS":
        raise ValueError("Source AFH-7/Hybrid-9 spectrum metadata is not PASS")
    if source_metadata.get("detector_response_applied") is not False:
        raise ValueError("Source spectrum must be pre-detector; refusing a second efficiency fold")
    benchmarks = source_metadata["particle_parameters"]["benchmarks"]
    groups = read_selected_spectrum_groups(spectrum_csv)
    expected_pairs = {(benchmark, scenario) for benchmark in benchmarks for scenario in SCENARIOS}
    if set(groups) != expected_pairs:
        raise ValueError(
            f"Unexpected spectrum groups; missing={sorted(expected_pairs-set(groups))}, "
            f"extra={sorted(set(groups)-expected_pairs)}"
        )
    expected_points = int(source_metadata["recoil_grid_keV"]["points"])
    for key, rows in groups.items():
        if len(rows) != expected_points:
            raise ValueError(f"{key}: expected {expected_points} points, found {len(rows)}")

    efficiency_x, efficiency_central, efficiency_lower, efficiency_upper = read_efficiency_curves(
        efficiency_csv
    )
    if efficiency_x[0] > roi_min_keV or efficiency_x[-1] < roi_max_keV:
        raise ValueError("LZ efficiency curve does not cover the requested ROI")
    tail_interval = candidate_tail_bounds(roi_min_keV, roi_max_keV)

    output_rows, dense_errors, refinement_errors = [], [], []
    for benchmark, parameters in benchmarks.items():
        benchmark_parameters = {
            "ms_MeV": float(parameters["ms_MeV"]),
            "delta_m_MeV": float(parameters["delta_m_MeV"]),
        }
        for scenario in SCENARIOS:
            row, dense_error, refinement_error = fold_one_group(
                benchmark, scenario, groups[(benchmark, scenario)],
                efficiency_x, efficiency_central, efficiency_lower, efficiency_upper,
                benchmark_parameters, roi_min_keV, roi_max_keV,
                exposure_tonne_year, integration_steps, tail_interval,
            )
            output_rows.append(row)
            dense_errors.append(dense_error)
            refinement_errors.append(refinement_error)

    out_dir.mkdir(parents=True, exist_ok=True)
    output_csv = out_dir / "lz_2026_afh7_hybrid9_rate_level_event_yields.csv"
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    efficiency_metadata_path = efficiency_csv.with_name("lz_2026_nr_efficiency_metadata.json")
    metadata: dict[str, Any] = {
        "status": "PASS",
        "calculation": "LZ 2026 final-WIMP-search-ROI efficiency fold of AFH-7 and Hybrid-9 natural-xenon spectra",
        "input_files": {
            "spectrum_csv": str(spectrum_csv),
            "spectrum_csv_sha256": sha256(spectrum_csv),
            "spectrum_metadata_json": str(spectrum_metadata_path),
            "spectrum_metadata_sha256": sha256(spectrum_metadata_path),
            "efficiency_csv": str(efficiency_csv),
            "efficiency_csv_sha256": sha256(efficiency_csv),
            "efficiency_metadata_json": str(efficiency_metadata_path) if efficiency_metadata_path.is_file() else None,
            "efficiency_metadata_sha256": sha256(efficiency_metadata_path) if efficiency_metadata_path.is_file() else None,
            "afh_source_file": source_metadata.get("afh_source_file"),
            "afh_source_sha256": source_metadata.get("afh_source_sha256"),
            "isotope_weights_sha256": source_metadata.get("isotope_weights_sha256"),
            "afh_response_grid_sha256": source_metadata.get("response_grid_files"),
        },
        "source_response_convention": source_metadata.get("response_convention"),
        "source_response_evaluation": source_metadata.get("AFH_evaluation"),
        "selected_scenarios": {key: SCENARIO_DESCRIPTIONS[key] for key in SCENARIOS},
        "benchmark_parameters": benchmarks,
        "recoil_grid_points_per_group": expected_points,
        "output_rows": len(output_rows),
        "roi_keV": [roi_min_keV, roi_max_keV],
        "candidate_tail_diagnostic": {
            "candidate_energy_keV": 248.0,
            "candidate_statistical_uncertainty_keV": 23.0,
            "integration_interval_keV": list(tail_interval),
            "upper_edge_clipped_by_search_roi": tail_interval[1] < 271.0,
            "systematic_energy_uncertainty_used": False,
            "energy_resolution_smearing_used": False,
            "interpretation": "spectral-shape diagnostic only; not an event likelihood",
        },
        "exposure_tonne_year": exposure_tonne_year,
        "exposure_kg_day": exposure_tonne_year * 1000.0 * 365.25,
        "efficiency_source": "LZ 2026 Fig. S2 digitized central final WIMP-search ROI NR efficiency and gray envelope",
        "efficiency_envelope_treatment": "gray detector-systematic range; no confidence level assigned by LZ",
        "integration_method": "exact analytic integral of piecewise-linear rate times piecewise-linear efficiency over the union of their knots",
        "dense_trapezoid_crosscheck_steps": integration_steps,
        "maximum_dense_trapezoid_relative_difference_vs_exact": max(dense_errors),
        "maximum_dense_trapezoid_refinement_relative_difference": max(refinement_errors),
        "abundance_renormalization": "none",
        "limitations": [
            "AFH-7 omits Xe-124 and Xe-126 because official AFH v6.0 default density matrices are unavailable; remaining natural abundances are not renormalized",
            "Hybrid-9 uses Helm only for Xe-124 and Xe-126; those two contributions are not AFH results",
            "source spectra reuse the archived three-body kernel and natural-xenon halo fold; this script recomputes neither",
            "the efficiency gray envelope has no confidence level assigned by LZ",
            "no NEST S1c/log10(S2c) PDFs or nuisance covariance",
            "no energy-resolution smearing or event-by-event reconstructed-energy response",
            "no background model, profile likelihood or confidence-level construction",
            "not a 90% confidence-level exclusion and not an official LZ likelihood",
        ],
        "detector_level_scope": {
            "efficiency_applied": True,
            "energy_resolution_smearing_applied": False,
            "two_dimensional_signal_pdf_applied": False,
            "background_likelihood_applied": False,
            "is_exclusion_limit": False,
        },
        "source_commit": os.environ.get("GITHUB_SHA"),
    }
    metadata_path = out_dir / "lz_2026_afh7_hybrid9_rate_level_metadata.json"
    metadata["output_csv"] = str(output_csv)
    metadata["output_csv_sha256"] = sha256(output_csv)
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (out_dir / "SHA256SUMS.txt").write_text(
        f"{sha256(output_csv)}  {output_csv.name}\n"
        f"{sha256(metadata_path)}  {metadata_path.name}\n",
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spectrum-csv", type=Path, default=DEFAULT_SPECTRUM)
    parser.add_argument("--spectrum-metadata", type=Path, default=DEFAULT_SPECTRUM_METADATA)
    parser.add_argument("--efficiency-csv", type=Path, default=DEFAULT_EFFICIENCY)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--roi-min-keV", type=float, default=5.4)
    parser.add_argument("--roi-max-keV", type=float, default=269.9)
    parser.add_argument("--exposure-tonne-year", type=float, default=2.84)
    parser.add_argument("--integration-steps", type=int, default=10000)
    args = parser.parse_args()
    metadata = run_fold(
        args.spectrum_csv, args.spectrum_metadata, args.efficiency_csv, args.out_dir,
        args.roi_min_keV, args.roi_max_keV, args.exposure_tonne_year, args.integration_steps
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
