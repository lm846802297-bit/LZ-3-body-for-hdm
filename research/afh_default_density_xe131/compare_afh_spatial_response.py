#!/usr/bin/env python3
"""Pointwise comparison of Python spatial responses with native AFH exports.

The native Wolfram reference is ResponseNuclear[y,{1,3,6,8},0,0] for
Xe-129 and Xe-131. All values remain in the raw AFH isoscalar convention;
the physical equal-p/n factor of four is deliberately not applied here.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Iterable, Mapping

RESPONSE_MAP = (
    ("M", "W_M00_AFH", "W_M00_AFH"),
    ("SigmaPrime", "W_SigmaPrime00_AFH", "W_SigmaPrime00_AFH"),
    ("Delta", "W_Delta00_AFH_literal", "W_Delta00_AFH"),
    ("SigmaPrimeDelta", "W_SigmaPrimeDelta00_AFH_literal", "W_SigmaPrimeDelta00_AFH"),
)


def _key(row: Mapping[str, object]) -> tuple[int, float]:
    return int(float(row["A"])), round(float(row["q_GeV"]), 10)


def _index(rows: Iterable[Mapping[str, object]], label: str):
    result = {}
    for row in rows:
        key = _key(row)
        if key in result:
            raise ValueError(f"duplicate {label} row for A={key[0]}, q={key[1]:.10g}")
        result[key] = row
    return result


def compare_records(
    python_rows: Iterable[Mapping[str, object]],
    native_rows: Iterable[Mapping[str, object]],
    *,
    rtol: float = 5e-7,
    atol: float = 2e-12,
) -> dict:
    """Compare all mapped responses and check positivity/Cauchy-Schwarz."""
    py = _index(python_rows, "Python")
    native = _index(native_rows, "native AFH")
    if not py:
        raise ValueError("Python response table is empty")
    if py.keys() != native.keys():
        missing_native = sorted(py.keys() - native.keys())
        missing_python = sorted(native.keys() - py.keys())
        raise ValueError(
            f"q-grid mismatch; missing native={missing_native}, missing Python={missing_python}"
        )

    maxima = {
        name: {"max_abs": 0.0, "max_rel": 0.0, "worst_key": None}
        for name, _, _ in RESPONSE_MAP
    }
    point_rows = []
    failures = []

    for key in sorted(py):
        prow, nrow = py[key], native[key]
        values = {}
        for name, py_column, native_column in RESPONSE_MAP:
            pv = float(prow[py_column])
            nv = float(nrow[native_column])
            if not (math.isfinite(pv) and math.isfinite(nv)):
                failures.append(f"{name} non-finite at A={key[0]}, q={key[1]:.10g}")
                continue
            diff = abs(pv - nv)
            scale = max(abs(pv), abs(nv))
            rel = diff / scale if scale else 0.0
            if diff > maxima[name]["max_abs"]:
                maxima[name]["max_abs"] = diff
                maxima[name]["worst_key"] = {"A": key[0], "q_GeV": key[1]}
            maxima[name]["max_rel"] = max(maxima[name]["max_rel"], rel)
            if not math.isclose(pv, nv, rel_tol=rtol, abs_tol=atol):
                failures.append(
                    f"{name} mismatch at A={key[0]}, q={key[1]:.10g}: "
                    f"Python={pv:.16g}, native={nv:.16g}, abs={diff:.4g}, rel={rel:.4g}"
                )
            values[f"python_{name}"] = pv
            values[f"native_{name}"] = nv
            values[f"absdiff_{name}"] = diff
            values[f"reldiff_{name}"] = rel

        # The diagonal spatial responses must be nonnegative. The signed
        # interference must obey the response-matrix Cauchy-Schwarz bound.
        for source, row, delta_column, mix_column in (
            ("Python", prow, "W_Delta00_AFH_literal", "W_SigmaPrimeDelta00_AFH_literal"),
            ("native AFH", nrow, "W_Delta00_AFH", "W_SigmaPrimeDelta00_AFH"),
        ):
            sigma = float(row["W_SigmaPrime00_AFH"])
            delta = float(row[delta_column])
            mix = float(row[mix_column])
            if sigma < -atol or delta < -atol:
                failures.append(
                    f"{source} negative diagonal spatial response at A={key[0]}, q={key[1]:.10g}"
                )
            lhs = mix * mix
            rhs = max(0.0, sigma) * max(0.0, delta)
            cs_tol = max(atol, rtol * max(lhs, rhs, 1.0))
            if lhs > rhs + cs_tol:
                failures.append(
                    f"{source} SigmaPrime-Delta Cauchy-Schwarz violation "
                    f"at A={key[0]}, q={key[1]:.10g}: lhs={lhs:.8g}, rhs={rhs:.8g}"
                )

        point_rows.append({"A": key[0], "q_GeV": key[1], **values})

    return {
        "status": "PASS" if not failures else "FAIL",
        "scope": "AFH raw isoscalar responses M, SigmaPrime, Delta, SigmaPrime-Delta",
        "rows": len(point_rows),
        "isotopes": sorted({key[0] for key in py}),
        "rtol": rtol,
        "atol": atol,
        "max_differences": maxima,
        "failures": failures,
        "point_rows": point_rows,
    }


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--python-csv", type=Path, required=True)
    parser.add_argument("--native-dir", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--rtol", type=float, default=5e-7)
    parser.add_argument("--atol", type=float, default=2e-12)
    args = parser.parse_args()

    native_rows = []
    for isotope in (129, 131):
        path = args.native_dir / f"afh_xe{isotope}_spatial_native.csv"
        if not path.is_file():
            raise FileNotFoundError(f"missing native AFH export: {path}")
        native_rows.extend(read_csv(path))
    result = compare_records(
        read_csv(args.python_csv), native_rows, rtol=args.rtol, atol=args.atol
    )
    args.outdir.mkdir(parents=True, exist_ok=True)
    json_path = args.outdir / "afh_spatial_python_native_comparison.json"
    csv_path = args.outdir / "afh_spatial_python_native_comparison.csv"
    json_path.write_text(
        json.dumps({k: v for k, v in result.items() if k != "point_rows"}, indent=2) + "\n",
        encoding="utf-8",
    )
    columns = ["A", "q_GeV"]
    for name, _, _ in RESPONSE_MAP:
        columns.extend(
            [f"python_{name}", f"native_{name}", f"absdiff_{name}", f"reldiff_{name}"]
        )
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(result["point_rows"])
    print(json.dumps({k: v for k, v in result.items() if k != "point_rows"}, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
