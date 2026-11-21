#!/usr/bin/env python3
"""Validate native AFH v6.0 Xe-131 exports of M, Phi'', and M-Phi''.

Checks response bookkeeping, normalization, positivity, Cauchy-Schwarz
consistency, grid identity, and provenance. It does not recompute AFH matrix
elements or the three-body tensor contraction.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

EXPECTED_SOURCE_SHA256 = "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372"
EXPECTED_MATRIX_SHA256 = "f656145ba2fb9da741b77faed4c01d0dc457c955fa340928b5dbf9cee9bc5d45"
EXPECTED_ROWS = 2401
EXPECTED_Q_MIN = 0.0
EXPECTED_Q_MAX = 0.6
EXPECTED_DQ = 0.00025

REQUIRED_COLUMNS = (
    "q_GeV", "y",
    "W_M00_AFH", "W_PhiPP00_AFH", "W_MPhiPP00_AFH",
    "R_M_raw", "R_PhiPP_raw", "R_MPhiPP_raw",
    "R_M_physical_equal_pn", "R_PhiPP_physical_equal_pn",
    "R_MPhiPP_physical_equal_pn",
    "Im_W_M00", "Im_W_PhiPP00", "Im_W_MPhiPP00",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _number(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f"{key} is not finite")
    return value


def validate_rows(
    rows: list[dict[str, str]],
    metadata: dict,
    *,
    require_full_grid: bool = True,
) -> dict:
    """Validate parsed CSV rows. Disabling full-grid checks is for unit tests."""
    if metadata.get("status") != "COMPLETED":
        raise ValueError("native execution metadata does not report COMPLETED")
    if metadata.get("source") != "AFH DMFormFactor v6.0 native Wolfram execution":
        raise ValueError("unexpected AFH source/runtime provenance")
    if metadata.get("afh_source_sha256") != EXPECTED_SOURCE_SHA256:
        raise ValueError("AFH source SHA-256 mismatch")
    if metadata.get("density_matrix_csv_sha256") != EXPECTED_MATRIX_SHA256:
        raise ValueError("Xe-131 density-matrix SHA-256 mismatch")
    if metadata.get("isotope_A") != 131 or metadata.get("Z") != 54:
        raise ValueError("isotope identity is not Xe-131")
    if float(metadata.get("J_A", -1)) != 1.5:
        raise ValueError("Xe-131 nuclear spin metadata must be J_A=3/2")
    if metadata.get("response_indices") != {"M": 1, "PhiPP": 4, "M_PhiPP": 7}:
        raise ValueError("AFH response-index mapping is inconsistent")
    if metadata.get("isospin") != "tau1=tau2=0; raw AFH isoscalar package convention":
        raise ValueError("unexpected AFH isospin convention")
    if metadata.get("factor_four_applied_once") is not True:
        raise ValueError("physical factor-four mapping is not explicitly recorded")
    if metadata.get("shape_renormalization_applied") is not False:
        raise ValueError("raw export must not apply a q=0 shape renormalization")

    q_min = float(metadata["q_min_GeV"])
    q_max = float(metadata["q_max_GeV"])
    dq = float(metadata["dq_GeV"])
    b = float(metadata["b_A_GeV_inverse"])
    expected_n = int(metadata["grid_points"])
    if expected_n != len(rows):
        raise ValueError(f"metadata says {expected_n} rows, CSV has {len(rows)}")
    if require_full_grid:
        if expected_n != EXPECTED_ROWS:
            raise ValueError(f"expected {EXPECTED_ROWS} q nodes, got {expected_n}")
        if not math.isclose(q_min, EXPECTED_Q_MIN, abs_tol=1e-14):
            raise ValueError("unexpected q minimum")
        if not math.isclose(q_max, EXPECTED_Q_MAX, abs_tol=1e-14):
            raise ValueError("unexpected q maximum")
        if not math.isclose(dq, EXPECTED_DQ, abs_tol=1e-14):
            raise ValueError("unexpected q step")

    if not rows:
        raise ValueError("CSV contains no data rows")
    for key in REQUIRED_COLUMNS:
        if key not in rows[0]:
            raise ValueError(f"missing CSV column: {key}")

    response_factor = 4.0 * math.pi / (2.0 * 1.5 + 1.0)
    max_factor_residual = 0.0
    max_four_residual = 0.0
    max_imaginary = 0.0
    min_phi_diagonal = math.inf
    max_cauchy_excess = 0.0
    max_y_residual = 0.0

    for index, row in enumerate(rows):
        q = _number(row, "q_GeV")
        y = _number(row, "y")
        expected_q = q_min + index * dq
        if not math.isclose(q, expected_q, rel_tol=0.0, abs_tol=2e-12):
            raise ValueError(f"q grid mismatch at row {index}: {q} vs {expected_q}")
        expected_y = (q * b / 2.0) ** 2
        y_residual = abs(y - expected_y)
        max_y_residual = max(max_y_residual, y_residual)
        if y_residual > 2e-11 * max(1.0, abs(expected_y)):
            raise ValueError(f"AFH y=(q_A b_A/2)^2 mismatch at row {index}")

        wm = _number(row, "W_M00_AFH")
        wphi = _number(row, "W_PhiPP00_AFH")
        wmix = _number(row, "W_MPhiPP00_AFH")
        rm = _number(row, "R_M_raw")
        rphi = _number(row, "R_PhiPP_raw")
        rmix = _number(row, "R_MPhiPP_raw")
        rm_phys = _number(row, "R_M_physical_equal_pn")
        rphi_phys = _number(row, "R_PhiPP_physical_equal_pn")
        rmix_phys = _number(row, "R_MPhiPP_physical_equal_pn")

        for w, r, label in (
            (wm, rm, "M"), (wphi, rphi, "PhiPP"), (wmix, rmix, "M_PhiPP")
        ):
            residual = abs(r - response_factor * w) / max(1.0, abs(r), abs(response_factor * w))
            max_factor_residual = max(max_factor_residual, residual)
            if residual > 2e-12:
                raise ValueError(f"4pi/(2J+1) mapping failed for {label} at row {index}")

        for raw, physical, label in (
            (rm, rm_phys, "M"), (rphi, rphi_phys, "PhiPP"), (rmix, rmix_phys, "M_PhiPP")
        ):
            residual = abs(physical - 4.0 * raw) / max(1.0, abs(physical), abs(4.0 * raw))
            max_four_residual = max(max_four_residual, residual)
            if residual > 2e-12:
                raise ValueError(f"factor-four mapping failed for {label} at row {index}")

        if rm < -1e-10:
            raise ValueError(f"negative diagonal M response at row {index}")
        if rphi < -1e-10:
            raise ValueError(f"negative diagonal Phi'' response at row {index}")
        min_phi_diagonal = min(min_phi_diagonal, rphi)

        # M-Phi'' is signed. Its square must obey the Cauchy-Schwarz bound
        # implied by the positive-semidefinite nuclear response matrix.
        rhs = max(0.0, rm * rphi)
        excess = rmix * rmix - rhs
        max_cauchy_excess = max(max_cauchy_excess, excess)
        if excess > 2e-9 * max(1.0, rhs):
            raise ValueError(f"M-Phi'' violates Cauchy-Schwarz at row {index}")

        for key, scale_key in (
            ("Im_W_M00", "W_M00_AFH"),
            ("Im_W_PhiPP00", "W_PhiPP00_AFH"),
            ("Im_W_MPhiPP00", "W_MPhiPP00_AFH"),
        ):
            imag = abs(_number(row, key))
            scale = max(1.0, abs(_number(row, scale_key)))
            if imag > 1e-12 * scale:
                raise ValueError(f"unexpected imaginary residual in {key} at row {index}")
            max_imaginary = max(max_imaginary, imag)

    first = rows[0]
    r_m0 = _number(first, "R_M_raw")
    expected_m0 = 131.0**2 / 4.0
    m0_relative_error = abs(r_m0 / expected_m0 - 1.0)
    if m0_relative_error > 2e-4:
        raise ValueError(f"AFH raw q=0 M normalization failed: {r_m0} vs A^2/4={expected_m0}")
    if not math.isclose(
        _number(first, "R_M_physical_equal_pn"),
        131.0**2,
        rel_tol=2e-4,
        abs_tol=2e-4,
    ):
        raise ValueError("physical equal-p/n q=0 M response does not approach A^2")

    return {
        "status": "PASS",
        "scope": "native AFH Xe-131 M, Phi'', and M-Phi'' nuclear responses only",
        "rows": len(rows),
        "q_min_GeV": q_min,
        "q_max_GeV": q_max,
        "dq_GeV": dq,
        "max_y_absolute_residual": max_y_residual,
        "max_response_factor_residual": max_factor_residual,
        "max_factor_four_residual": max_four_residual,
        "max_imaginary_residual": max_imaginary,
        "minimum_R_PhiPP_raw": min_phi_diagonal,
        "maximum_Cauchy_excess": max_cauchy_excess,
        "R_M_raw_q0": r_m0,
        "expected_A2_over_4": expected_m0,
        "R_M_raw_q0_relative_error": m0_relative_error,
        "R_M_physical_q0": _number(first, "R_M_physical_equal_pn"),
        "expected_A2": 131.0**2,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    with args.csv.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    result = validate_rows(rows, metadata, require_full_grid=True)

    actual_csv_sha = sha256_file(args.csv)
    if metadata.get("csv_sha256") != actual_csv_sha:
        raise ValueError("native CSV SHA-256 does not match execution metadata")
    result["csv_sha256"] = actual_csv_sha
    result["metadata_sha256"] = sha256_file(args.metadata)
    result["afh_source_sha256"] = metadata["afh_source_sha256"]
    result["density_matrix_csv_sha256"] = metadata["density_matrix_csv_sha256"]
    result["wolfram_version"] = metadata.get("wolfram_version")
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
