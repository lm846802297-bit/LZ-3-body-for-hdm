#!/usr/bin/env python3
"""Compare AFH-native Mathematica output with the source-translated Python result.

The comparison is deliberately performed before and after the finite-precision
q=0 normalization.  It checks the raw AFH W_M response, the package-normalized
isoscalar response, the physical equal-p/n response (factor four included once),
and the final q=0-normalized physical response.  Mismatched q grids are rejected;
no interpolation is allowed.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np


def read_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def column(rows, name):
    try:
        return np.array([float(row[name]) for row in rows], dtype=float)
    except KeyError as exc:
        raise SystemExit(f"Missing required CSV column: {name}") from exc
    except ValueError as exc:
        raise SystemExit(f"Non-numeric value in CSV column {name}") from exc


def compare(a, b, *, rtol, atol):
    delta = np.abs(a - b)
    scale = np.maximum(np.abs(b), atol)
    rel = delta / scale
    passed = bool(np.allclose(a, b, rtol=rtol, atol=atol))
    i = int(np.argmax(rel))
    return {
        "passed": passed,
        "max_absolute_difference": float(delta.max()),
        "max_relative_difference": float(rel[i]),
        "worst_index": i,
        "worst_q_GeV": None,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--python-csv", type=Path, required=True)
    p.add_argument("--mathematica-csv", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--rtol", type=float, default=2e-8)
    p.add_argument("--atol", type=float, default=2e-10)
    args = p.parse_args()

    py = read_rows(args.python_csv)
    wl = read_rows(args.mathematica_csv)
    if len(py) != len(wl):
        raise SystemExit(f"Grid length mismatch: Python={len(py)}, Mathematica={len(wl)}")

    q_py = column(py, "q_GeV")
    q_wl = column(wl, "q_GeV")
    q_grid_max_abs_difference = float(np.max(np.abs(q_py - q_wl)))
    q_grid_atol = 1e-14  # allow only CSV floating-point serialization roundoff
    if not np.allclose(q_py, q_wl, rtol=0.0, atol=q_grid_atol):
        raise SystemExit(
            f"q grids differ by {q_grid_max_abs_difference:.3e} GeV; "
            "no interpolation is allowed"
        )

    # The same physical response is represented by 4 times the AFH package
    # isoscalar response when the cross-section prefactor contains g_VN^2.
    py_w = column(py, "W_M00_AFH_package")
    wl_w = column(wl, "W_M00_AFH_package")
    py_afh = column(py, "R_AFH_package_4pi_over_2Jplus1")
    wl_afh = column(wl, "R_AFH_4Pi_over_2Jplus1")
    py_phys_raw = column(py, "R_equal_pn_raw")
    wl_phys_raw = column(wl, "R_equal_pn_raw")
    py_phys_norm = column(py, "R_equal_pn_normalized")
    wl_phys_norm = column(wl, "R_equal_pn_normalized")

    factor4_py = bool(np.allclose(py_phys_raw, 4.0 * py_afh, rtol=2e-12, atol=2e-10))
    factor4_wl = bool(np.allclose(wl_phys_raw, 4.0 * wl_afh, rtol=2e-12, atol=2e-10))
    expected_zero = 131**2
    q0_normalization_py = bool(np.isclose(py_phys_norm[0], expected_zero, rtol=0, atol=2e-8))
    q0_normalization_wl = bool(np.isclose(wl_phys_norm[0], expected_zero, rtol=0, atol=2e-8))

    quantities = {
        "raw_AFH_W_M00": compare(py_w, wl_w, rtol=args.rtol, atol=args.atol),
        "AFH_package_R_4piW_over_2Jplus1": compare(py_afh, wl_afh, rtol=args.rtol, atol=args.atol),
        "physical_equal_pn_R_raw_factor4_once": compare(py_phys_raw, wl_phys_raw, rtol=args.rtol, atol=args.atol),
        "physical_equal_pn_R_q0_normalized": compare(py_phys_norm, wl_phys_norm, rtol=args.rtol, atol=args.atol),
    }
    for result in quantities.values():
        result["worst_q_GeV"] = float(q_py[result["worst_index"]])

    passed = (
        all(x["passed"] for x in quantities.values())
        and factor4_py and factor4_wl
        and q0_normalization_py and q0_normalization_wl
    )
    result = {
        "passed": passed,
        "points": len(py),
        "python_csv_sha256": sha256_file(args.python_csv),
        "mathematica_csv_sha256": sha256_file(args.mathematica_csv),
        "rtol": args.rtol,
        "atol": args.atol,
        "q_grid_identical_within_export_precision": True,
        "q_grid_max_abs_difference_GeV": q_grid_max_abs_difference,
        "q_grid_export_atol_GeV": q_grid_atol,
        "q_grid_start_GeV": float(q_py[0]),
        "q_grid_end_GeV": float(q_py[-1]),
        "q_grid_step_GeV": float(q_py[1] - q_py[0]),
        "expected_R_A_zero": expected_zero,
        "factor4_contract": {
            "python_R_equal_raw_equals_4_R_AFH": factor4_py,
            "mathematica_R_equal_raw_equals_4_R_AFH": factor4_wl,
        },
        "q0_normalization_contract": {
            "python_R_A_0": float(py_phys_norm[0]),
            "mathematica_R_A_0": float(wl_phys_norm[0]),
            "python_passed": q0_normalization_py,
            "mathematica_passed": q0_normalization_wl,
        },
        "comparisons": quantities,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
