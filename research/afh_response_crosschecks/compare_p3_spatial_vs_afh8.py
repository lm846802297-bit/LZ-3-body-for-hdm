#!/usr/bin/env python3
"""P3-B vs independent AFH-8 Python grid; this is not native AFH validation.

Use the standard-library csv parser for round-trip-safe decimal conversion.
Do not use pandas' default fast float parser for this precision comparison.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
NQ = 2401
SPIN_ZERO = {128, 130, 132, 134, 136}
RTOL, ATOL = 5e-12, 2e-14
RAW = {
    "W_Delta": ("W_Delta_AFH_package", "W_Delta00_AFH"),
    "W_SigmaPrime": ("W_SigmaPrime_AFH_package", "W_SigmaPrime00_AFH"),
    "W_SigmaPrimeDelta": ("W_SigmaPrimeDelta_AFH_package", "W_SigmaPrimeDelta00_AFH"),
}
PHYSICAL = {
    "R_Delta": ("R_Delta_equal_pn", "R_Delta_physical_equal_pn"),
    "R_SigmaPrime": ("R_SigmaPrime_equal_pn", "R_SigmaPrime_physical_equal_pn"),
    "R_SigmaPrimeDelta": ("R_SigmaPrimeDelta_equal_pn", "R_SigmaPrimeDelta_physical_equal_pn"),
}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def read(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def index(rows, label):
    out = {}
    for row in rows:
        key = (int(float(row["A"])), round(float(row["q_GeV"]), 10))
        if key in out:
            raise ValueError(f"duplicate {label} row {key}")
        out[key] = row
    return out

def compare(joined, left_col, right_col, scale_c0=False):
    max_abs = max_rel = 0.0
    worst = None
    failed = 0
    for key, left, right in joined:
        a, b = float(left[left_col]), float(right[right_col])
        if scale_c0:
            b *= float(left["common_matrix_normalization"])
        if not math.isfinite(a) or not math.isfinite(b):
            raise ValueError(f"non-finite {left_col}/{right_col} at {key}")
        d = abs(a-b)
        rel = d / max(abs(a), abs(b), 1e-300)
        max_abs = max(max_abs, d)
        if rel > max_rel:
            max_rel = rel
            worst = {"A": key[0], "q_GeV": key[1], "left": a, "right_scaled": b}
        if d > ATOL + RTOL * max(abs(a), abs(b)):
            failed += 1
    return {"passed": failed == 0, "failed_points": failed,
            "max_absolute_difference": max_abs, "max_relative_difference": max_rel,
            "worst_point": worst, "rtol": RTOL, "atol": ATOL}

def run(p3_path: Path, afh8_path: Path):
    p3, afh8 = index(read(p3_path), "P3-B"), index(read(afh8_path), "AFH-8")
    expected = {(A, round(i*0.00025, 10)) for A in ISOTOPES for i in range(NQ)}
    if p3.keys() != expected or afh8.keys() != expected:
        raise ValueError(
            f"grid mismatch: P3 missing/extra={len(expected-p3.keys())}/{len(p3.keys()-expected)}, "
            f"AFH-8 missing/extra={len(expected-afh8.keys())}/{len(afh8.keys()-expected)}"
        )
    joined, c0, c0_spread = [], {}, 0.0
    y_diff = cauchy_excess = 0.0
    norm_failures, spin_zero_nonzero = 0, []
    for key in sorted(expected):
        a, b = p3[key], afh8[key]
        if float(a["J_A"]) != float(b["J_A"]):
            raise ValueError(f"J_A mismatch at {key}")
        y_diff = max(y_diff, abs(float(a["y"])-float(b["y"])))
        A, c = key[0], float(a["common_matrix_normalization"])
        if not 0.999 <= c <= 1.001:
            raise ValueError(f"unexpected C0={c} for Xe-{A}")
        if A in c0:
            c0_spread = max(c0_spread, abs(c-c0[A]))
        else:
            c0[A] = c
        wd, ws, wx = (float(a[x]) for x in (
            "W_Delta_AFH_package", "W_SigmaPrime_AFH_package",
            "W_SigmaPrimeDelta_AFH_package"))
        cauchy_excess = max(cauchy_excess,
            max(0.0, abs(wx)-math.sqrt(max(0.0, wd*ws))))
        if A in SPIN_ZERO and (wd != 0.0 or ws != 0.0 or wx != 0.0):
            spin_zero_nonzero.append({"A": A, "q_GeV": key[1]})
        factor = 4.0 * math.pi / (2.0*float(a["J_A"])+1.0)
        for rc, wc in (
            ("R_Delta_equal_pn", "W_Delta_AFH_package"),
            ("R_SigmaPrime_equal_pn", "W_SigmaPrime_AFH_package"),
            ("R_SigmaPrimeDelta_equal_pn", "W_SigmaPrimeDelta_AFH_package"),
        ):
            if abs(float(a[rc])-4.0*c*factor*float(a[wc])) > 2e-14 + 2e-12*abs(float(a[rc])):
                norm_failures += 1
        for rc, wc in (
            ("R_Delta_physical_equal_pn", "W_Delta00_AFH"),
            ("R_SigmaPrime_physical_equal_pn", "W_SigmaPrime00_AFH"),
            ("R_SigmaPrimeDelta_physical_equal_pn", "W_SigmaPrimeDelta00_AFH"),
        ):
            if abs(float(b[rc])-4.0*factor*float(b[wc])) > 2e-14 + 2e-12*abs(float(b[rc])):
                norm_failures += 1
        joined.append((key, a, b))
    if y_diff != 0.0 or c0_spread > 2e-14 or spin_zero_nonzero:
        raise ValueError("y/C0/spin-zero structural check failed")
    raw = {k: compare(joined, *v) for k, v in RAW.items()}
    physical = {k: compare(joined, *v, scale_c0=True) for k, v in PHYSICAL.items()}
    passed = (all(x["passed"] for x in raw.values())
              and all(x["passed"] for x in physical.values())
              and norm_failures == 0 and cauchy_excess <= 2e-14)
    return {
        "status": "PASS_INDEPENDENT_PYTHON_CROSSCHECK" if passed else "FAIL",
        "scope": "Python-to-Python consistency only; not native Mathematica validation",
        "comparison_parser": "Python standard-library csv.DictReader",
        "native_afh_validated": False,
        "isotopes": list(ISOTOPES), "points_per_isotope": NQ,
        "rows_compared": len(joined),
        "q_grid": {"minimum_GeV": 0.0, "maximum_GeV": 0.6, "step_GeV": 0.00025},
        "max_y_absolute_difference": y_diff,
        "max_C0_spread_within_isotope": c0_spread,
        "C0_by_isotope": {str(k): v for k, v in c0.items()},
        "max_Cauchy_Schwarz_excess": cauchy_excess,
        "normalization_identity_failures": norm_failures,
        "spin_zero_isotope_spatial_responses_exactly_zero": True,
        "P3_B_csv_sha256": sha256(p3_path), "AFH_8_csv_sha256": sha256(afh8_path),
        "raw_AFH_package_comparisons": raw,
        "physical_equal_pn_comparisons_after_C0": physical,
        "acceptance_note": "Native AFH acceptance requires pointwise Wolfram ResponseNuclear comparison and negligible imaginary residuals."
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--p3-csv", type=Path, required=True)
    p.add_argument("--afh8-csv", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    args = p.parse_args()
    result = run(args.p3_csv, args.afh8_csv)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS_INDEPENDENT_PYTHON_CROSSCHECK":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
