#!/usr/bin/env python3
"""Pointwise comparison of the Python AFH-8 database with native Wolfram exports."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from run_afh_full_response_database import (
    ISOTOPES, RESPONSE_COLUMNS,
)


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def _index(rows, label):
    result = {}
    for row in rows:
        key = (int(float(row["A"])), round(float(row["q_GeV"]), 10))
        if key in result:
            raise ValueError(f"duplicate {label} row at {key}")
        result[key] = row
    return result


def compare_records(
    python_rows,
    native_rows,
    *,
    expected_isotopes=ISOTOPES,
    expected_points=2401,
    rtol=5e-7,
    atol=2e-12,
    imag_atol=2e-12,
):
    py = _index(python_rows, "Python")
    native = _index(native_rows, "native AFH")
    expected_keys = {
        (A, round(i * 0.00025, 10))
        for A in expected_isotopes
        for i in range(expected_points)
    }
    failures = []
    if py.keys() != expected_keys:
        failures.append(
            f"Python key set mismatch: missing={len(expected_keys - py.keys())}, "
            f"unexpected={len(py.keys() - expected_keys)}"
        )
    if native.keys() != expected_keys:
        failures.append(
            f"native AFH key set mismatch: missing={len(expected_keys - native.keys())}, "
            f"unexpected={len(native.keys() - expected_keys)}"
        )

    maxima = {
        name: {"max_abs": 0.0, "max_rel": 0.0, "worst_key": None}
        for name in RESPONSE_COLUMNS
    }
    rows_checked = 0
    for key in sorted(py.keys() & native.keys()):
        prow = py[key]
        nrow = native[key]
        rows_checked += 1
        try:
            py_y = float(prow["y"])
            native_y = float(nrow["y"])
            if not math.isclose(py_y, native_y, rel_tol=2e-12, abs_tol=2e-14):
                failures.append(f"y mismatch at {key}: Python={py_y}, native={native_y}")
        except (KeyError, TypeError, ValueError) as exc:
            failures.append(f"missing/invalid y at {key}: {exc}")

        for name, column in RESPONSE_COLUMNS.items():
            try:
                pv = float(prow[column])
                nv = float(nrow[column])
                imag = float(nrow[f"Im_{column}"])
            except (KeyError, TypeError, ValueError) as exc:
                failures.append(f"missing/invalid {column} at {key}: {exc}")
                continue
            if not all(math.isfinite(v) for v in (pv, nv, imag)):
                failures.append(f"non-finite {column} at {key}")
                continue
            diff = abs(pv - nv)
            scale = max(abs(pv), abs(nv))
            rel = diff / scale if scale else 0.0
            record = maxima[name]
            if diff > record["max_abs"]:
                record["max_abs"] = diff
                record["worst_key"] = {"A": key[0], "q_GeV": key[1]}
            record["max_rel"] = max(record["max_rel"], rel)
            if not math.isclose(pv, nv, rel_tol=rtol, abs_tol=atol):
                failures.append(
                    f"{column} mismatch at {key}: Python={pv:.16g}, "
                    f"native={nv:.16g}, abs={diff:.4g}, rel={rel:.4g}"
                )
            if abs(imag) > imag_atol:
                failures.append(
                    f"native imaginary residual for {column} at {key}: {imag:.4g}"
                )

    return {
        "status": "PASS" if not failures else "FAIL",
        "scope": "pointwise Python versus native AFH v6.0 ResponseNuclear comparison",
        "native_afh_validated": not failures and rows_checked == len(expected_keys),
        "isotopes": list(expected_isotopes),
        "expected_points_per_isotope": expected_points,
        "expected_rows": len(expected_keys),
        "python_rows": len(py),
        "native_rows": len(native),
        "rows_compared": rows_checked,
        "rtol": rtol,
        "atol": atol,
        "imaginary_atol": imag_atol,
        "max_differences": maxima,
        "failures": failures,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--python-csv", type=Path, required=True)
    parser.add_argument("--native-dir", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--rtol", type=float, default=5e-7)
    parser.add_argument("--atol", type=float, default=2e-12)
    parser.add_argument("--imag-atol", type=float, default=2e-12)
    args = parser.parse_args()

    native_rows = []
    for A in ISOTOPES:
        path = args.native_dir / f"afh_v6_xe{A}_eight_response_native.csv"
        if not path.is_file():
            raise FileNotFoundError(f"missing native AFH export: {path}")
        native_rows.extend(read_csv(path))

    result = compare_records(
        read_csv(args.python_csv),
        native_rows,
        rtol=args.rtol,
        atol=args.atol,
        imag_atol=args.imag_atol,
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
