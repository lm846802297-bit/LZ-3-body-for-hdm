#!/usr/bin/env python3
"""Compare AFH-native Mathematica output with the source-translated Python result.

Run after executing run_afh_default_xe131.wls with the official DMFormFactor
v6.0 package. This deliberately refuses to interpolate mismatched q grids.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import numpy as np


def read_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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

    q_py = np.array([float(r["q_GeV"]) for r in py])
    q_wl = np.array([float(r["q_GeV"]) for r in wl])
    if not np.array_equal(q_py, q_wl):
        raise SystemExit("q grids are not exactly equal; no interpolation is allowed")

    # Compare the physical equal-pn response after each implementation applies
    # the same q=0 normalization. This avoids confusing rounded density-matrix
    # coefficients with a shape disagreement.
    r_py = np.array([float(r["R_equal_pn_normalized"]) for r in py])
    r_wl = np.array([float(r["R_equal_pn_normalized"]) for r in wl])
    absdiff = np.abs(r_py-r_wl)
    scale = np.maximum(np.maximum(np.abs(r_py), np.abs(r_wl)), args.atol)
    reldiff = absdiff/scale
    passed = bool(np.allclose(r_py, r_wl, rtol=args.rtol, atol=args.atol))
    result = {
        "passed": passed,
        "points": len(py),
        "rtol": args.rtol,
        "atol": args.atol,
        "max_abs_difference": float(absdiff.max()),
        "max_relative_difference": float(reldiff.max()),
        "max_relative_difference_index": int(np.argmax(reldiff)),
        "max_relative_difference_q_GeV": float(q_py[int(np.argmax(reldiff))]),
        "python_R0": float(r_py[0]),
        "mathematica_R0": float(r_wl[0]),
        "expected_R0": 131**2,
        "q_grid_identical": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
