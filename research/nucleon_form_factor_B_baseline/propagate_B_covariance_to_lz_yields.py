#!/usr/bin/env python3
"""Propagate the Borah electromagnetic coefficient covariance to LZ event yields.

The same correlated F_M(-t_N) draws used in the formal B recoil spectra are
applied isotope by isotope to the archived leading-order P0 reference rate,
then folded through the LZ 2026 NR efficiency.
The formal impulse prescription is t_N=t_A=-2*m_A*E_R; AFH continues to use
the exact spatial Q_A^2 separately. Cross-recoil and cross-isotope
correlations induced by the shared fit coefficients are retained.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "research/three_body_calculation_and_validation"))

from apply_B_to_afh_hybrid9_continuous_spectrum import (  # noqa: E402
    SCENARIOS,
    number,
    rate_prefactor,
    read_csv,
    response_for_scenario,
)
from borah2020_lowq2 import sample_cM_draws  # noqa: E402
from fold_lz_2026_rate_level import (  # noqa: E402
    integrate_piecewise_linear_product,
    read_efficiency_curves,
    sha256,
)

DEFAULT_SOURCE_DIR = (
    ROOT / "research/afh_default_density_natural_xenon_halo/results/"
    "afh7_hybrid9_continuous_2026-11-14"
)
DEFAULT_EFFICIENCY = (
    ROOT / "research/lz_detector_response/lz_2026_extended_nr/"
    "lz_2026_nr_efficiency_digitized.csv"
)
TONNE_YEAR_TO_KG_DAY = 1000.0 * 365.25


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_keyed_csv(path: Path, key_fields: tuple[str, ...]) -> dict[tuple, dict[str, str]]:
    rows = read_csv(path)
    result = {}
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        if key in result:
            raise ValueError(f"duplicate key in {path}: {key}")
        result[key] = row
    return result


def integrate_draw_matrix(
    rate_x: list[float],
    rate_draws: np.ndarray,
    efficiency_x: list[float],
    efficiency_y: list[float],
    lo: float,
    hi: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Integrate every draw exactly for piecewise-linear rate and efficiency."""
    rates = np.asarray(rate_draws, dtype=float)
    if rates.ndim != 2 or rates.shape[1] != len(rate_x):
        raise ValueError("rate_draws must have shape (n_draws, len(rate_x))")
    if not lo < hi or rate_x[0] > lo or rate_x[-1] < hi:
        raise ValueError("rate grid does not cover the requested ROI")
    if efficiency_x[0] > lo or efficiency_x[-1] < hi:
        raise ValueError("efficiency grid does not cover the requested ROI")
    if np.any(~np.isfinite(rates)) or np.any(rates < 0.0):
        raise ValueError("rate draws must be finite and non-negative")

    raw = np.zeros(rates.shape[0], dtype=float)
    weighted = np.zeros(rates.shape[0], dtype=float)
    knots = sorted(
        {lo, hi}
        | {x for x in rate_x if lo < x < hi}
        | {x for x in efficiency_x if lo < x < hi}
    )

    def evaluate(x: float) -> np.ndarray:
        if x <= rate_x[0]:
            return rates[:, 0]
        if x >= rate_x[-1]:
            return rates[:, -1]
        right = int(np.searchsorted(rate_x, x, side="right"))
        left = right - 1
        fraction = (x - rate_x[left]) / (rate_x[right] - rate_x[left])
        return rates[:, left] + fraction * (rates[:, right] - rates[:, left])

    def efficiency(x: float) -> float:
        return float(np.interp(x, efficiency_x, efficiency_y))

    for a, b in zip(knots, knots[1:]):
        width = b - a
        r0 = evaluate(a)
        r1 = evaluate(b)
        e0 = efficiency(a)
        e1 = efficiency(b)
        dr = r1 - r0
        de = e1 - e0
        raw += 0.5 * width * (r0 + r1)
        weighted += width * (
            r0 * e0 + 0.5 * (r0 * de + e0 * dr) + (dr * de) / 3.0
        )
    return raw, weighted


def run(
    source_dir: Path,
    b_spectrum_dir: Path,
    detector_yield_csv: Path,
    efficiency_csv: Path,
    out_dir: Path,
    strange_model: str,
    n_draws: int = 3000,
    seed: int = 20261119,
    roi_min_keV: float = 5.4,
    roi_max_keV: float = 269.9,
    exposure_tonne_year: float = 2.84,
    closure_tolerance: float = 2.0e-10,
) -> dict:
    source_spectrum_path = source_dir / "afh_hybrid9_natural_xenon_spectrum.csv"
    isotope_path = source_dir / "afh_hybrid9_isotope_kernel_integrals.csv"
    source_metadata_path = source_dir / "metadata.json"
    b_spectrum_path = b_spectrum_dir / "afh_hybrid9_B_natural_xenon_spectrum.csv"
    b_isotope_path = b_spectrum_dir / "afh_hybrid9_B_isotope_contributions.csv"
    b_metadata_path = b_spectrum_dir / "metadata.json"
    for path in (
        source_spectrum_path, isotope_path, source_metadata_path,
        b_spectrum_path, b_isotope_path, b_metadata_path, detector_yield_csv, efficiency_csv,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)
    if n_draws < 2 or not roi_min_keV < roi_max_keV or exposure_tonne_year <= 0.0:
        raise ValueError("invalid draw count, ROI or exposure")

    source_metadata = json.loads(source_metadata_path.read_text(encoding="utf-8"))
    b_metadata = json.loads(b_metadata_path.read_text(encoding="utf-8"))
    if source_metadata.get("status") != "PASS" or b_metadata.get("status") != "PASS":
        raise ValueError("source or B spectrum metadata is not PASS")
    if b_metadata.get("strange_form_factor_model") != strange_model:
        raise ValueError("B spectrum strange-current model does not match requested model")
    if b_metadata.get("detector_response_applied") is not False:
        raise ValueError("B spectrum must be pre-detector")

    particle = source_metadata["particle_parameters"]
    mV = float(particle["mV_GeV"])
    coupling_sq = float(particle["coupling_product_squared"])
    prefactor = rate_prefactor(source_metadata)
    source_spectrum = read_csv(source_spectrum_path)
    isotope_rows = read_csv(isotope_path)
    b_rows = read_csv(b_spectrum_path)
    b_isotope_rows = read_csv(b_isotope_path)
    detector_rows = read_csv(detector_yield_csv)
    if not source_spectrum or not isotope_rows or not b_rows or not b_isotope_rows or not detector_rows:
        raise ValueError("one or more required rate tables are empty")

    b_groups = defaultdict(list)
    for row in b_rows:
        b_groups[(row["benchmark"], row["scenario"])].append(row)
    for rows in b_groups.values():
        rows.sort(key=lambda row: number(row, "ER_keV"))

    detector_lookup = {
        (row["benchmark"], row["scenario"]): row for row in detector_rows
    }
    source_spectrum_lookup = {
        (row["benchmark"], row["scenario"], number(row, "ER_keV")): row
        for row in source_spectrum
    }
    b_isotope_lookup = {
        (
            row["benchmark"], row["scenario"],
            number(row, "ER_keV"), int(row["A"]),
        ): row
        for row in b_isotope_rows
    }

    energies_by_benchmark = {
        benchmark: sorted({
            number(row, "ER_keV") for row in source_spectrum
            if row["benchmark"] == benchmark and row["scenario"] == "AFH-7"
        })
        for benchmark in particle["benchmarks"]
    }
    isotope_groups = defaultdict(list)
    q2_values_set = set()
    for row in isotope_rows:
        benchmark = row["benchmark"]
        ER = number(row, "ER_keV")
        A = int(row["A"])
        mA = number(row, "mA_GeV")
        q2 = 2.0*mA*ER*1.0e-6
        q2_values_set.add(q2)
        isotope_groups[(benchmark, ER)].append(row)

    q2_values = sorted(q2_values_set)
    q2_index = {format(q2, ".17g"): i for i, q2 in enumerate(q2_values)}
    q2_index_for_row = {
        (row["benchmark"], number(row, "ER_keV"), int(row["A"])):
            q2_index[format(
                2.0*number(row, "mA_GeV")*number(row, "ER_keV")*1.0e-6,
                ".17g",
            )]
        for row in isotope_rows
    }

    fm_draws = sample_cM_draws(
        np.asarray(q2_values), n_draws=n_draws, seed=seed,
        strange_model=strange_model,
    )
    multiplier_draws = fm_draws * fm_draws
    efficiency_x, efficiency_central, efficiency_lower, efficiency_upper = (
        read_efficiency_curves(efficiency_csv)
    )
    if efficiency_x[0] > roi_min_keV or efficiency_x[-1] < roi_max_keV:
        raise ValueError("efficiency curve does not cover the ROI")
    exposure_kg_day = exposure_tonne_year * TONNE_YEAR_TO_KG_DAY

    output_rows = []
    max_central_closure = 0.0
    max_P0_spectrum_closure = 0.0
    max_isotope_P0_contribution_closure = 0.0
    max_draw_nonfinite = 0
    for benchmark, energies in energies_by_benchmark.items():
        if len(energies) < 2:
            raise ValueError(f"{benchmark}: insufficient recoil grid")
        for scenario in SCENARIOS:
            draw_rates = np.zeros((n_draws, len(energies)), dtype=float)
            energy_index = {energy: i for i, energy in enumerate(energies)}
            for ER in energies:
                reconstructed_P0_rate = 0.0
                for row in isotope_groups[(benchmark, ER)]:
                    R_A = response_for_scenario(row, scenario)
                    base_kernel = number(row, "kernel_halo_integral_GeV")
                    if R_A == 0.0 or base_kernel == 0.0:
                        continue
                    A = int(row["A"])
                    atom_fraction = number(row, "natural_atom_fraction")
                    mA = number(row, "mA_GeV")
                    tA = -2.0*mA*ER*1.0e-6
                    denominator = (mV*mV - tA)**2
                    p0_contribution = (
                        prefactor * atom_fraction * base_kernel * R_A / denominator
                    )
                    reconstructed_P0_rate += p0_contribution
                    stored_key = (benchmark, scenario, ER, A)
                    stored_isotope = b_isotope_lookup[stored_key]
                    stored_P0_contribution = number(
                        stored_isotope, "rate_P0_contribution_events_kg_day_keV"
                    )
                    isotope_closure = (
                        abs(p0_contribution/stored_P0_contribution-1.0)
                        if stored_P0_contribution > 0.0 else (
                            0.0 if p0_contribution == 0.0 else math.inf
                        )
                    )
                    max_isotope_P0_contribution_closure = max(
                        max_isotope_P0_contribution_closure, isotope_closure
                    )
                    if isotope_closure > closure_tolerance:
                        raise ArithmeticError(
                            f"{benchmark}/{scenario}/{ER}/Xe-{A}: isotope P0 contribution "
                            f"does not close ({isotope_closure:.6e})"
                        )
                    q2 = 2.0*mA*ER*1.0e-6
                    idx = q2_index_for_row[(benchmark, ER, A)]
                    draw_rates[:, energy_index[ER]] += (
                        p0_contribution * multiplier_draws[:, idx]
                    )

                source_P0_rate = number(
                    source_spectrum_lookup[(benchmark, scenario, ER)],
                    "rate_events_kg_day_keV",
                )
                spectrum_closure = (
                    abs(reconstructed_P0_rate/source_P0_rate-1.0)
                    if source_P0_rate > 0.0 else (
                        0.0 if reconstructed_P0_rate == 0.0 else math.inf
                    )
                )
                max_P0_spectrum_closure = max(max_P0_spectrum_closure, spectrum_closure)
                if spectrum_closure > closure_tolerance:
                    raise ArithmeticError(
                        f"{benchmark}/{scenario}/{ER}: reconstructed P0 spectrum "
                        f"does not close ({spectrum_closure:.6e})"
                    )

            rows = b_groups[(benchmark, scenario)]
            b_energies = [number(row, "ER_keV") for row in rows]
            if b_energies != energies:
                raise ValueError(f"{benchmark}/{scenario}: B spectrum energy grid mismatch")
            central_rates = np.asarray(
                [number(row, "rate_events_kg_day_keV") for row in rows],
                dtype=float,
            )
            central_raw, central_weighted = integrate_piecewise_linear_product(
                b_energies, central_rates.tolist(),
                efficiency_x, efficiency_central, roi_min_keV, roi_max_keV,
            )
            central_events = central_weighted * exposure_kg_day
            detector_row = detector_lookup[(benchmark, scenario)]
            detector_events = number(detector_row, "expected_events_in_high_efficiency_window")
            closure = abs(central_events/detector_events - 1.0) if detector_events > 0 else (
                0.0 if central_events == 0.0 else math.inf
            )
            max_central_closure = max(max_central_closure, closure)
            if closure > closure_tolerance:
                raise ArithmeticError(
                    f"{benchmark}/{scenario}: central detector-yield closure "
                    f"{closure:.6e} > {closure_tolerance:.6e}"
                )

            raw_draws, weighted_draws = integrate_draw_matrix(
                energies, draw_rates, efficiency_x, efficiency_central,
                roi_min_keV, roi_max_keV,
            )
            max_draw_nonfinite += int(np.count_nonzero(~np.isfinite(weighted_draws)))
            if np.any(~np.isfinite(weighted_draws)) or np.any(weighted_draws < 0.0):
                raise ArithmeticError(f"{benchmark}/{scenario}: invalid detector-yield draws")
            event_draws = weighted_draws * exposure_kg_day
            p16, p50, p84 = np.percentile(event_draws, [16, 50, 84])
            output_rows.append({
                "benchmark": benchmark,
                "scenario": scenario,
                "strange_form_factor_model": strange_model,
                "n_draws": n_draws,
                "seed": seed,
                "roi_min_keV": roi_min_keV,
                "roi_max_keV": roi_max_keV,
                "exposure_tonne_year": exposure_tonne_year,
                "expected_events_central": central_events,
                "expected_events_EM_cov_p16": float(p16),
                "expected_events_EM_cov_p50": float(p50),
                "expected_events_EM_cov_p84": float(p84),
                "EM_covariance_half_width_pct": (
                    50.0*(p84-p16)/p50 if p50 > 0.0 else 0.0
                ),
                "central_vs_EM_cov_median_pct": (
                    100.0*(central_events/p50-1.0) if p50 > 0.0 else 0.0
                ),
                "coupling_product_sq_reference": coupling_sq,
                "coupling_product_sq_for_one_event_at_EM_cov_median": (
                    coupling_sq/p50 if p50 > 0.0 else None
                ),
                "detector_central_yield_closure_relative": closure,
                "detector_efficiency_uncertainty_sampled": False,
                "strange_lattice_uncertainty_sampled": False,
            })

    out_dir.mkdir(parents=True, exist_ok=True)
    output_csv = out_dir / "lz_2026_B_detector_yield_EM_covariance.csv"
    write_csv(output_csv, output_rows)
    metadata = {
        "status": "PASS",
        "calculation": "correlated Borah electromagnetic form-factor covariance propagated through isotope-resolved B recoil spectra and LZ 2026 NR efficiency",
        "reference_baseline": "P0: archived leading-order charge-only spectrum; legacy source rate_events_kg_day_keV column is interpreted as P0",
        "strange_form_factor_model": strange_model,
        "n_draws": n_draws,
        "seed": seed,
        "roi_keV": [roi_min_keV, roi_max_keV],
        "exposure_tonne_year": exposure_tonne_year,
        "exposure_kg_day": exposure_kg_day,
        "uncertainty_scope": {
            "Borah2020_EM_coefficient_covariance": True,
            "cross_recoil_and_cross_isotope_correlations_preserved": True,
            "strange_lattice_uncertainties_sampled": False,
            "LZ_efficiency_gray_envelope_sampled": False,
            "energy_resolution_smearing": False,
            "two_dimensional_signal_pdf": False,
            "background_likelihood": False,
        },
        "validation": {
            "maximum_central_detector_yield_closure_relative_difference": max_central_closure,
            "maximum_P0_spectrum_reconstruction_relative_difference": max_P0_spectrum_closure,
            "maximum_isotope_P0_contribution_relative_difference": max_isotope_P0_contribution_closure,
            "central_detector_yield_closure_tolerance": closure_tolerance,
            "nonfinite_draw_count": max_draw_nonfinite,
        },
        "source_files": {
            "isotope_kernel_csv": str(isotope_path),
            "isotope_kernel_sha256": sha256(isotope_path),
            "source_metadata_json": str(source_metadata_path),
            "source_metadata_sha256": sha256(source_metadata_path),
            "B_spectrum_csv": str(b_spectrum_path),
            "B_spectrum_sha256": sha256(b_spectrum_path),
            "B_isotope_contributions_csv": str(b_isotope_path),
            "B_isotope_contributions_sha256": sha256(b_isotope_path),
            "B_metadata_json": str(b_metadata_path),
            "B_metadata_sha256": sha256(b_metadata_path),
            "efficiency_csv": str(efficiency_csv),
            "efficiency_sha256": sha256(efficiency_csv),
            "detector_yield_csv": str(detector_yield_csv),
            "detector_yield_sha256": sha256(detector_yield_csv),
        },
        "output_csv": output_csv.name,
        "output_csv_sha256": sha256(output_csv),
    }
    metadata_path = out_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    (out_dir / "SHA256SUMS.txt").write_text(
        f"{sha256(output_csv)}  {output_csv.name}\n"
        f"{sha256(metadata_path)}  {metadata_path.name}\n",
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--b-spectrum-dir", type=Path, required=True)
    parser.add_argument("--detector-yield-csv", type=Path, required=True)
    parser.add_argument("--efficiency-csv", type=Path, default=DEFAULT_EFFICIENCY)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--strange-model", required=True)
    parser.add_argument("--draws", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=20261119)
    parser.add_argument("--roi-min-keV", type=float, default=5.4)
    parser.add_argument("--roi-max-keV", type=float, default=269.9)
    parser.add_argument("--exposure-tonne-year", type=float, default=2.84)
    parser.add_argument("--closure-tolerance", type=float, default=2.0e-10)
    args = parser.parse_args()
    result = run(
        args.source_dir, args.b_spectrum_dir, args.detector_yield_csv,
        args.efficiency_csv, args.out_dir, args.strange_model,
        args.draws, args.seed, args.roi_min_keV, args.roi_max_keV,
        args.exposure_tonne_year, args.closure_tolerance,
    )
    print(json.dumps(result["validation"], indent=2))


if __name__ == "__main__":
    main()
