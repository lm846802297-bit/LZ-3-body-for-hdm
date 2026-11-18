#!/usr/bin/env python3
"""Structural, normalization, positivity, and Cauchy checks for AFH-8 output."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

from run_afh_full_response_database import (
    ISOTOPES, J_BY_A, RESPONSE_COLUMNS, DIAGONAL_FAMILIES,
)

CROSS_PAIRS = (
    ("W_M00_AFH", "W_PhiPP00_AFH", "W_MPhiPP00_AFH", "M-PhiPP"),
    (
        "W_SigmaPrime00_AFH",
        "W_Delta00_AFH",
        "W_SigmaPrimeDelta00_AFH",
        "SigmaPrime-Delta",
    ),
)


def validate_records(
    rows,
    *,
    expected_isotopes=ISOTOPES,
    expected_points=2401,
    q_min=0.0,
    q_max=0.6,
    atol=2e-12,
    rtol=1e-9,
    zero_momentum_rtol=3e-4,
):
    failures = []
    grouped = defaultdict(list)
    for row in rows:
        try:
            A = int(float(row["A"]))
            q = float(row["q_GeV"])
        except (KeyError, TypeError, ValueError) as exc:
            failures.append(f"invalid isotope/q row: {exc}")
            continue
        grouped[A].append((q, row))

    if set(grouped) != set(expected_isotopes):
        failures.append(
            f"isotope set {sorted(grouped)} != expected {list(expected_isotopes)}"
        )

    expected_step = (
        (q_max - q_min) / (expected_points - 1)
        if expected_points > 1 else None
    )
    summaries = {}
    response_columns = list(RESPONSE_COLUMNS.values())
    raw_columns = [f"R_{name}_raw" for name in RESPONSE_COLUMNS]
    physical_columns = [
        f"R_{name}_physical_equal_pn" for name in RESPONSE_COLUMNS
    ]

    for A in expected_isotopes:
        entries = sorted(grouped.get(A, []), key=lambda item: item[0])
        if len(entries) != expected_points:
            failures.append(
                f"Xe-{A}: {len(entries)} rows != {expected_points}"
            )
            continue
        qs = [q for q, _ in entries]
        if len({round(q, 12) for q in qs}) != expected_points:
            failures.append(f"Xe-{A}: duplicate q_A values")
        if expected_step is not None:
            for i, q in enumerate(qs):
                expected_q = q_min + i * expected_step
                if not math.isclose(q, expected_q, rel_tol=0.0, abs_tol=atol):
                    failures.append(
                        f"Xe-{A}: q-grid mismatch at row {i}: "
                        f"{q:.16g} != {expected_q:.16g}"
                    )
                    break

        J_A = J_BY_A[A]
        conversion = 4.0 * math.pi / (2.0 * J_A + 1.0)
        ranges = {column: [] for column in response_columns}
        max_cs_excess = {label: 0.0 for *_, label in CROSS_PAIRS}
        zero_row = None

        for q, row in entries:
            numeric = {}
            for column in response_columns + raw_columns + physical_columns:
                try:
                    value = float(row[column])
                except (KeyError, TypeError, ValueError) as exc:
                    failures.append(
                        f"Xe-{A} q={q:.10g}: invalid/missing {column}: {exc}"
                    )
                    value = math.nan
                numeric[column] = value
                if not math.isfinite(value):
                    failures.append(
                        f"Xe-{A} q={q:.10g}: non-finite {column}"
                    )

            for name, column in RESPONSE_COLUMNS.items():
                value = numeric[column]
                ranges[column].append(value)
                if name in DIAGONAL_FAMILIES and math.isfinite(value) and value < -atol:
                    failures.append(
                        f"Xe-{A} q={q:.10g}: negative diagonal {column}"
                    )

            for name, column in RESPONSE_COLUMNS.items():
                w_value = numeric[column]
                r_raw = numeric[f"R_{name}_raw"]
                r_physical = numeric[f"R_{name}_physical_equal_pn"]
                if all(math.isfinite(v) for v in (w_value, r_raw, r_physical)):
                    expected_raw = conversion * w_value
                    if not math.isclose(
                        r_raw, expected_raw, rel_tol=rtol, abs_tol=atol
                    ):
                        failures.append(
                            f"Xe-{A} q={q:.10g}: {name} raw normalization mismatch"
                        )
                    if not math.isclose(
                        r_physical, 4.0 * r_raw,
                        rel_tol=rtol, abs_tol=atol,
                    ):
                        failures.append(
                            f"Xe-{A} q={q:.10g}: {name} physical factor-four mismatch"
                        )

            for left, right, cross, label in CROSS_PAIRS:
                a = numeric[left]
                b = numeric[right]
                c = numeric[cross]
                if all(math.isfinite(v) for v in (a, b, c)):
                    lhs = c * c
                    rhs = max(0.0, a) * max(0.0, b)
                    excess = lhs - rhs
                    max_cs_excess[label] = max(
                        max_cs_excess[label], excess
                    )
                    tolerance = max(1e-28, rtol * max(lhs, rhs, 1e-300))
                    if lhs > rhs + tolerance:
                        failures.append(
                            f"Xe-{A} q={q:.10g}: {label} Cauchy-Schwarz violation "
                            f"(lhs={lhs:.8g}, rhs={rhs:.8g})"
                        )
            if abs(q - q_min) <= atol:
                zero_row = numeric

        zero_momentum = None
        if zero_row is not None:
            r_m_raw = zero_row["R_M_raw"]
            expected = A * A / 4.0
            relative_error = abs(r_m_raw - expected) / expected
            zero_momentum = {
                "R_M_raw_q0": r_m_raw,
                "expected_A2_over_4": expected,
                "relative_error": relative_error,
                "tolerance": zero_momentum_rtol,
            }
            if relative_error > zero_momentum_rtol:
                failures.append(
                    f"Xe-{A}: zero-momentum M normalization error "
                    f"{relative_error:.6g} exceeds {zero_momentum_rtol:.6g}"
                )

        summaries[str(A)] = {
            "rows": len(entries),
            "J_A": J_A,
            "q_min_GeV": qs[0],
            "q_max_GeV": qs[-1],
            "zero_momentum_M_normalization": zero_momentum,
            "max_cauchy_schwarz_excess": max_cs_excess,
            "response_ranges": {
                column: {
                    "min": min(values),
                    "max": max(values),
                }
                for column, values in ranges.items()
            },
        }

    return {
        "status": "PASS" if not failures else "FAIL",
        "scope": (
            "Python internal consistency only; native AFH comparison is a "
            "separate acceptance gate"
        ),
        "native_afh_validated": False,
        "isotopes": list(expected_isotopes),
        "expected_points_per_isotope": expected_points,
        "expected_total_rows": expected_points * len(expected_isotopes),
        "actual_total_rows": len(rows),
        "q_min_GeV": q_min,
        "q_max_GeV": q_max,
        "step_GeV": expected_step,
        "normalization": (
            "R_raw=4*pi/(2J_A+1)*W_AFH; "
            "R_physical_equal_pn=4*R_raw"
        ),
        "isotope_summaries": summaries,
        "failures": failures,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--expected-points", type=int, default=2401)
    parser.add_argument("--q-min", type=float, default=0.0)
    parser.add_argument("--q-max", type=float, default=0.6)
    parser.add_argument("--zero-momentum-rtol", type=float, default=3e-4)
    args = parser.parse_args()

    with args.csv.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    result = validate_records(
        rows,
        expected_points=args.expected_points,
        q_min=args.q_min,
        q_max=args.q_max,
        zero_momentum_rtol=args.zero_momentum_rtol,
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
