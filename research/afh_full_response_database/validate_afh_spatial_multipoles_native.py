#!/usr/bin/env python3
"""Structural and numerical checks for the native AFH rank-resolved multipoles."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ISOTOPES = (129, 131)
RANKS = {129: (1,), 131: (1, 2, 3)}
Q_MIN = 0.0
Q_MAX = 0.6
Q_STEP = 0.00025
EXPECTED_PER_ISOTOPE = 2401
COLS = (
    "A",
    "q_GeV",
    "y",
    "multipole_J",
    "M_Delta_J_native",
    "M_SigmaPrime_J_native",
    "Im_M_Delta_J_native",
    "Im_M_SigmaPrime_J_native",
)


def _base_radius(A: int) -> float:
    return math.sqrt(41.467 / (45.0 * A ** (-1.0 / 3.0) - 25.0 * A ** (-2.0 / 3.0)))


def _expected_y(A: int, q: float) -> float:
    b_gev_inv = _base_radius(A) * 5.0677
    return (q * b_gev_inv / 2.0) ** 2


def validate_records(rows, *, imag_atol: float = 2e-12, metadata: dict | None = None):
    failures = []
    grouped = defaultdict(dict)
    for index, row in enumerate(rows):
        try:
            A = int(float(row["A"]))
            q = float(row["q_GeV"])
            J = int(float(row["multipole_J"]))
            y = float(row["y"])
            m_delta = float(row["M_Delta_J_native"])
            m_sigma = float(row["M_SigmaPrime_J_native"])
            im_delta = float(row["Im_M_Delta_J_native"])
            im_sigma = float(row["Im_M_SigmaPrime_J_native"])
        except (KeyError, TypeError, ValueError) as exc:
            failures.append(f"row {index}: invalid numeric field: {exc}")
            continue

        if A not in RANKS:
            failures.append(f"row {index}: unexpected isotope {A}")
            continue
        if J not in RANKS[A]:
            failures.append(f"row {index}: unexpected rank J={J} for Xe-{A}")
            continue
        key = (A, round(q, 10), J)
        if key in grouped[A].get("keys", set()):
            failures.append(f"Xe-{A}: duplicate row at q={q:.10g}, J={J}")
        grouped[A].setdefault("keys", set()).add(key)
        grouped[A].setdefault("rows", []).append(row)

        if not all(math.isfinite(v) for v in (q, y, m_delta, m_sigma, im_delta, im_sigma)):
            failures.append(f"Xe-{A} q={q:.10g} J={J}: non-finite value")
        if abs(y - _expected_y(A, q)) > max(2e-12, 2e-10 * abs(y)):
            failures.append(f"Xe-{A} q={q:.10g} J={J}: y mismatch")
        if abs(im_delta) > imag_atol or abs(im_sigma) > imag_atol:
            failures.append(
                f"Xe-{A} q={q:.10g} J={J}: imaginary residual "
                f"{max(abs(im_delta), abs(im_sigma)):.4g} > {imag_atol:.4g}"
            )

    if set(grouped) != set(ISOTOPES):
        failures.append(f"isotope set {sorted(grouped)} != {list(ISOTOPES)}")

    summaries = {}
    for A in ISOTOPES:
        entries = grouped.get(A, {}).get("rows", [])
        if len(entries) != EXPECTED_PER_ISOTOPE * len(RANKS[A]):
            failures.append(
                f"Xe-{A}: {len(entries)} rows != "
                f"{EXPECTED_PER_ISOTOPE * len(RANKS[A])}"
            )
        qs = sorted({round(float(r["q_GeV"]), 10) for r in entries})
        if qs != sorted({round(Q_MIN + i * Q_STEP, 10) for i in range(EXPECTED_PER_ISOTOPE)}):
            failures.append(f"Xe-{A}: q grid does not match the 2400-node grid")
        ranks_present = sorted({int(float(r["multipole_J"])) for r in entries})
        if tuple(ranks_present) != RANKS[A]:
            failures.append(f"Xe-{A}: ranks {ranks_present} != {list(RANKS[A])}")
        summaries[str(A)] = {
            "rows": len(entries),
            "ranks": ranks_present,
            "q_points": len(qs),
            "q_min_GeV": min(qs) if qs else None,
            "q_max_GeV": max(qs) if qs else None,
            "max_abs_imaginary": max(
                (max(abs(float(r["Im_M_Delta_J_native"])),
                     abs(float(r["Im_M_SigmaPrime_J_native"]))) for r in entries),
                default=None,
            ),
        }

    if metadata is not None:
        if metadata.get("rows") != EXPECTED_PER_ISOTOPE * sum(map(len, RANKS.values())):
            failures.append("metadata row count mismatch")
        if metadata.get("isotopes") != "129,131":
            failures.append("metadata isotope label mismatch")
        if "q=0 value is the analytic y=0 limit" not in metadata.get("q_grid", ""):
            failures.append("metadata does not document the q=0 analytic limit")
        if metadata.get("max_imaginary_residual") is None:
            failures.append("metadata lacks max_imaginary_residual")

    return {
        "status": "PASS_NATIVE_AFH_SPATIAL_MULTIPOLES" if not failures else "FAIL",
        "scope": "native AFH v6.0 rank-resolved DeltaJ and SigmaPJ amplitudes",
        "isotopes": list(ISOTOPES),
        "rows": len(rows),
        "expected_rows": EXPECTED_PER_ISOTOPE * sum(map(len, RANKS.values())),
        "isotope_summaries": summaries,
        "failures": failures,
    }


def _parse_metadata(path: Path) -> dict:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--imag-atol", type=float, default=2e-12)
    args = parser.parse_args()

    with args.csv.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))

    metadata = _parse_metadata(args.metadata)
    metadata_rows = metadata.get("rows")
    if metadata_rows is not None:
        metadata["rows"] = int(metadata_rows)
    metadata["max_imaginary_residual"] = metadata.get("max_imaginary_residual")
    if metadata["max_imaginary_residual"] is not None:
        metadata["max_imaginary_residual"] = float(metadata["max_imaginary_residual"])

    result = validate_records(rows, imag_atol=args.imag_atol, metadata=metadata)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS_NATIVE_AFH_SPATIAL_MULTIPOLES":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
