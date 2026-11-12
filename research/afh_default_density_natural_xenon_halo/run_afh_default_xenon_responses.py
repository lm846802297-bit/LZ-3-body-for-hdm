#!/usr/bin/env python3
"""Generate complete AFH v6.0 default-density response grids for natural xenon.

The finite-sum implementation is the same source-translated kernel already
validated for Xe-131. This wrapper supplies isotope-specific J_A, T_iso and
b_A, and regenerates all seven built-in AFH default xenon responses.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "afh_default_density_xe131"))
sys.path.insert(0, str(HERE.parent / "figure2_full_reproduction"))

from run_afh_default_xe131 import (  # noqa: E402
    angular_mj,
    bessel_element,
    compute_amplitude,
    orbital_n_l,
)
from isotope_mass_schemes import isotope_mass_GeV  # noqa: E402

Z = 54
ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
GROUND_STATE_SPIN = {
    128: 0.0,
    129: 0.5,
    130: 0.0,
    131: 1.5,
    132: 0.0,
    134: 0.0,
    136: 0.0,
}
FM_TO_GEV_INV_AFH = 5.0677
Q_MAX_GEV = 0.60
Q_STEP_GEV = 0.00025
EXPECTED_GRID_POINTS = 2401
FIELDS = (
    "A", "isotope", "J_A", "T_iso", "b_A_fm", "q_GeV", "y",
    "W_M00_AFH_package", "R_AFH_isoscalar_4pi_over_2Jplus1",
    "R_equal_pn_normalized", "R_over_A2",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_matrix(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = []
        for row in csv.DictReader(handle):
            rows.append({
                "index": int(row["index"]),
                "coefficient": float(row["coefficient"]),
                "rank": int(row["rank"]),
                "isospin": int(row["isospin"]),
                "Nprime": int(row["Nprime"]),
                "two_jprime": int(row["two_jprime"]),
                "N": int(row["N"]),
                "two_j": int(row["two_j"]),
            })
    if not rows or [r["index"] for r in rows] != list(range(1, len(rows) + 1)):
        raise ValueError(f"Invalid or non-contiguous AFH matrix: {path}")
    return rows


def oscillator_length_fm(A: int) -> float:
    return math.sqrt(41.467 / (45.0 * A ** (-1.0 / 3.0)
                               - 25.0 * A ** (-2.0 / 3.0)))


def package_response(q_GeV: float, A: int, rows: list[dict],
                     b_GeV_inv: float, T_iso: float, J_A: float) -> tuple[float, dict]:
    """Return AFH W_M^00 and the allowed even-multipole amplitudes."""
    ranks = tuple(range(0, int(round(2.0 * J_A)) + 1, 2))
    amplitudes = {
        rank: compute_amplitude(q_GeV, rank, rows, b_GeV_inv, T_iso)
        for rank in ranks
    }
    W00 = 0.25 * sum(value * value for value in amplitudes.values())
    response = 4.0 * math.pi / (2.0 * J_A + 1.0) * W00
    return response, amplitudes


def write_csv(path: Path, rows: list[dict], fields=None) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--xe131-reference",
                        type=Path,
                        default=HERE.parent / "afh_default_density_xe131"
                                / "output" / "afh_default_xe131_WM00.csv")
    parser.add_argument("--selected-samples",
                        type=Path,
                        default=HERE / "input" / "afh_response_samples.csv")
    parser.add_argument("--max-relative-xe131-grid-difference", type=float,
                        default=5.0e-12)
    parser.add_argument("--max-relative-selected-sample-difference", type=float,
                        default=5.0e-7)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    q_grid = np.arange(EXPECTED_GRID_POINTS, dtype=float) * Q_STEP_GEV
    if not math.isclose(float(q_grid[-1]), Q_MAX_GEV, rel_tol=0.0, abs_tol=1e-14):
        raise ArithmeticError("AFH q-grid construction failed")

    response_rows = []
    per_isotope = {}
    direct_response_cache = {}

    for A in ISOTOPES:
        matrix_path = args.matrix_dir / f"afh_default_xe{A}_density_matrix.csv"
        rows = read_matrix(matrix_path)
        J_A = GROUND_STATE_SPIN[A]
        T_iso = abs(A / 2.0 - Z)
        b_fm = oscillator_length_fm(A)
        b_GeV_inv = b_fm * FM_TO_GEV_INV_AFH

        package_values = np.empty(len(q_grid), dtype=float)
        W_values = np.empty(len(q_grid), dtype=float)
        for index, q in enumerate(q_grid):
            package_R, _ = package_response(
                float(q), A, rows, b_GeV_inv, T_iso, J_A
            )
            package_values[index] = package_R
            W_values[index] = package_R * (2.0 * J_A + 1.0) / (4.0 * math.pi)

        package_zero = float(package_values[0])
        expected_zero = A * A / 4.0
        zero_relative_error = abs(package_zero / expected_zero - 1.0)
        if zero_relative_error > 5.0e-4:
            raise ArithmeticError(
                f"Xe-{A} AFH q=0 normalization mismatch: "
                f"got {package_zero:.12g}, expected {expected_zero:.12g}, "
                f"relative error={zero_relative_error:.3e}"
            )

        R_equal = A * A * package_values / package_zero
        if np.any(~np.isfinite(R_equal)) or np.any(R_equal < 0.0):
            raise ArithmeticError(f"Invalid normalized AFH response for Xe-{A}")

        for i, q in enumerate(q_grid):
            response_rows.append({
                "A": A,
                "isotope": f"Xe-{A}",
                "J_A": J_A,
                "T_iso": T_iso,
                "b_A_fm": b_fm,
                "q_GeV": float(q),
                "y": (float(q) * b_GeV_inv / 2.0) ** 2,
                "W_M00_AFH_package": float(W_values[i]),
                "R_AFH_isoscalar_4pi_over_2Jplus1": float(package_values[i]),
                "R_equal_pn_normalized": float(R_equal[i]),
                "R_over_A2": float(R_equal[i] / (A * A)),
            })

        per_isotope[A] = {
            "rows": len(rows),
            "J_A": J_A,
            "T_iso": T_iso,
            "b_A_fm": b_fm,
            "q_grid_points": len(q_grid),
            "q_min_GeV": float(q_grid[0]),
            "q_max_GeV": float(q_grid[-1]),
            "q_step_GeV": Q_STEP_GEV,
            "package_R0": package_zero,
            "expected_package_R0_A2_over_4": expected_zero,
            "package_R0_relative_error": zero_relative_error,
            "physical_equal_pn_normalization_factor": (A * A) / package_zero,
            "max_R_over_A2": float(np.max(R_equal / (A * A))),
            "matrix_file": matrix_path.name,
            "matrix_sha256": sha256(matrix_path),
        }
        direct_response_cache[A] = (rows, b_GeV_inv, T_iso, J_A, package_zero)

    response_path = args.out_dir / "afh_xe_isotope_responses.csv"
    write_csv(response_path, response_rows, FIELDS)

    # Independent regression 1: the new generic implementation must reproduce
    # the already archived Xe-131 2401-node response curve.
    xe131_reference_rows = []
    with args.xe131_reference.open("r", newline="", encoding="utf-8") as handle:
        xe131_reference_rows = list(csv.DictReader(handle))
    new131 = [r for r in response_rows if int(r["A"]) == 131]
    if len(xe131_reference_rows) != EXPECTED_GRID_POINTS:
        raise RuntimeError("Archived Xe-131 reference is not a 2401-node grid")
    grid_differences = []
    for new, old in zip(new131, xe131_reference_rows):
        if abs(float(new["q_GeV"]) - float(old["q_GeV"])) > 1e-14:
            raise RuntimeError("Xe-131 q grids do not match")
        a = float(old["R_equal_pn_normalized"])
        b = float(new["R_equal_pn_normalized"])
        if a == 0.0:
            grid_differences.append(abs(b - a))
        else:
            grid_differences.append(abs(b / a - 1.0))
    max_xe131_grid_difference = max(grid_differences)
    if max_xe131_grid_difference > args.max_relative_xe131_grid_difference:
        raise RuntimeError(
            "Generic response generator does not reproduce the archived "
            f"Xe-131 curve: max relative difference={max_xe131_grid_difference:.3e}"
        )

    # Independent regression 2: directly evaluate all 28 old selected samples
    # at their recorded NIST-mass exact-spatial q, rather than interpolating.
    sample_rows = []
    max_sample_difference = 0.0
    max_pchip_difference = 0.0
    max_pchip_archive_difference = 0.0
    with args.selected_samples.open("r", newline="", encoding="utf-8") as handle:
        samples = list(csv.DictReader(handle))
    if len(samples) != 28:
        raise RuntimeError(f"Expected 28 selected AFH samples, found {len(samples)}")

    response_by_A = {}
    for A in ISOTOPES:
        isotope_rows = [r for r in response_rows if int(r["A"]) == A]
        q = np.asarray([float(r["q_GeV"]) for r in isotope_rows])
        RA = np.asarray([float(r["R_equal_pn_normalized"]) for r in isotope_rows])
        response_by_A[A] = PchipInterpolator(q, RA, extrapolate=False)

    for sample in samples:
        A = int(sample["A"])
        ER = float(sample["ER_keV"]) * 1.0e-6
        q_sample = float(sample["q_response_GeV"])
        mA_nist = isotope_mass_GeV(A, "nist_nuclear")
        q_expected = math.sqrt(2.0 * mA_nist * ER + ER * ER)
        if abs(q_sample - q_expected) > 2.0e-10:
            raise RuntimeError(
                f"Selected sample q does not match NIST exact-spatial q for Xe-{A}: "
                f"{q_sample:.12g} vs {q_expected:.12g}"
            )

        matrix, b_inv, T_iso, J_A, package_zero = direct_response_cache[A]
        package_R, _ = package_response(q_sample, A, matrix, b_inv, T_iso, J_A)
        direct_RA = A * A * package_R / package_zero
        pchip_RA = float(response_by_A[A](q_sample))
        reference_RA = float(sample["R_A"])
        direct_rel = abs(direct_RA / reference_RA - 1.0) if reference_RA else abs(direct_RA)
        pchip_rel = abs(pchip_RA / direct_RA - 1.0) if direct_RA else abs(pchip_RA)
        pchip_archive_rel = (
            abs(pchip_RA / reference_RA - 1.0) if reference_RA else abs(pchip_RA)
        )
        max_sample_difference = max(max_sample_difference, direct_rel)
        max_pchip_difference = max(max_pchip_difference, pchip_rel)
        max_pchip_archive_difference = max(
            max_pchip_archive_difference, pchip_archive_rel
        )
        sample_rows.append({
            "A": A,
            "ER_keV": float(sample["ER_keV"]),
            "J_A": J_A,
            "T_iso": T_iso,
            "b_A_fm_archived": float(sample["b_A_fm"]),
            "b_A_fm_recomputed": oscillator_length_fm(A),
            "q_NIST_exact_spatial_GeV": q_sample,
            "q_recomputed_GeV": q_expected,
            "q_abs_difference_GeV": abs(q_sample - q_expected),
            "y_AFH": (q_sample * b_inv / 2.0) ** 2,
            "package_R0": package_zero,
            "package_R_at_q": package_R,
            "normalization_factor_to_A2": (A * A) / package_zero,
            "R_A_archived_28_sample": reference_RA,
            "R_A_direct_AFH": direct_RA,
            "R_A_PCHIP_from_2401_grid": pchip_RA,
            "direct_vs_archived_relative_difference": direct_rel,
            "PCHIP_vs_direct_relative_difference": pchip_rel,
            "PCHIP_vs_archived_relative_difference": pchip_archive_rel,
        })

    # Persist the complete point-by-point audit before enforcing the acceptance
    # threshold. A failed regression must still leave a downloadable diagnostic.
    regression_path = args.out_dir / "afh_response_selected_sample_regression.csv"
    write_csv(regression_path, sample_rows)
    diagnostic = {
        "status": (
            "PASS" if max_pchip_archive_difference <= args.max_relative_selected_sample_difference
            else "FAIL"
        ),
        "acceptance_comparison": "PCHIP from regenerated 2401-node grid vs archived 28 PCHIP samples",
        "acceptance_tolerance_relative": args.max_relative_selected_sample_difference,
        "max_direct_vs_archived_relative_difference": max_sample_difference,
        "max_pchip_vs_archived_relative_difference": max_pchip_archive_difference,
        "max_pchip_vs_direct_relative_difference": max_pchip_difference,
        "fold_interpolation_status": (
            "REQUIRES_EXACT_Q_OR_GRID_REFINEMENT"
            if max_pchip_difference > 5.0e-4 else "WITHIN_5E-4_DIAGNOSTIC"
        ),
        "sample_count": len(sample_rows),
        "source_response_grid_points": len(response_rows),
        "top_discrepancies": sorted(
            sample_rows,
            key=lambda row: row["direct_vs_archived_relative_difference"],
            reverse=True,
        )[:10],
        "interpretation": (
            "Diagnostic only. No tolerance is relaxed and no response is rescaled "
            "to force agreement."
        ),
    }
    diagnostic_path = args.out_dir / "afh_response_selected_sample_regression_diagnostic.json"
    diagnostic_path.write_text(
        json.dumps(diagnostic, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(diagnostic, indent=2))

    if max_pchip_archive_difference > args.max_relative_selected_sample_difference:
        raise RuntimeError(
            "Regenerated AFH PCHIP grid does not reproduce the 28 archived PCHIP samples: "
            f"max relative difference={max_pchip_archive_difference:.3e}"
        )
    metadata = {
        "calculation": "AFH v6.0 default-density W_M^00 response for natural xenon",
        "source": "Official AFH DMFormFactor v6.0 built-in default density matrices",
        "source_package_file": "dmformfactor-V6.m",
        "source_package_sha256": "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372",
        "source_archive_sha256": "4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727",
        "source_selection": 'SetIsotope[54,A,"default","default"]',
        "response_function": "ResponseNuclear[y,1,0,0]",
        "isotopes": list(ISOTOPES),
        "omitted_natural_isotopes": [124, 126],
        "grid": {
            "points_per_isotope": EXPECTED_GRID_POINTS,
            "total_rows": len(response_rows),
            "q_min_GeV": 0.0,
            "q_max_GeV": Q_MAX_GEV,
            "q_step_GeV": Q_STEP_GEV,
            "y": "(q*b_A/2)^2",
        },
        "response_normalization": (
            "R_equal_pn(q)=A^2*R_AFH_isoscalar(q)/R_AFH_isoscalar(0); "
            "R_equal_pn(0)=A^2"
        ),
        "q0_package_normalization_acceptance_tolerance_relative": 5.0e-4,
        "q0_normalization_note": (
            "Built-in OBDME coefficients are rounded in the AFH source. "
            "The raw q=0 offset is retained in metadata and removed only by "
            "the isotope-specific multiplicative normalization to A^2."
        ),
        "oscillator_length": "sqrt(41.467/(45*A^(-1/3)-25*A^(-2/3))) fm",
        "spatial_momentum": "q=sqrt(2*m_A*E_R+E_R^2); no NR substitution",
        "isotope_metadata": per_isotope,
        "regression": {
            "xe131_full_grid_points": EXPECTED_GRID_POINTS,
            "xe131_max_relative_grid_difference": max_xe131_grid_difference,
            "selected_sample_points": len(samples),
            "selected_sample_max_relative_direct_vs_archived_difference": max_sample_difference,
            "selected_sample_max_relative_pchip_vs_archived_difference": max_pchip_archive_difference,
            "selected_sample_max_relative_pchip_vs_direct_difference": max_pchip_difference,
            "status": "PASS",
            "fold_interpolation_status": (
                "REQUIRES_EXACT_Q_OR_GRID_REFINEMENT"
                if max_pchip_difference > 5.0e-4 else "WITHIN_5E-4_DIAGNOSTIC"
            ),
        },
        "response_file": response_path.name,
        "response_file_sha256": sha256(response_path),
        "selected_sample_regression_file": regression_path.name,
        "selected_sample_regression_sha256": sha256(regression_path),
        "native_mathematica_reexecution": "pending; Python source translation only",
    }
    metadata_path = args.out_dir / "afh_xe_isotope_response_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "isotopes": list(ISOTOPES),
        "total_response_rows": len(response_rows),
        "xe131_grid_max_relative_difference": max_xe131_grid_difference,
        "selected_samples": len(samples),
        "selected_samples_max_relative_direct_vs_archived_difference": max_sample_difference,
        "selected_samples_max_relative_pchip_vs_archived_difference": max_pchip_archive_difference,
        "pchip_vs_direct_max_relative_difference": max_pchip_difference,
        "response_sha256": sha256(response_path),
        "status": "PASS",
    }, indent=2))


if __name__ == "__main__":
    main()
