#!/usr/bin/env python3
"""Validate the dense native Xe-131 AFH charge-response export near the M dip."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

AFH_SHA256 = "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372"
CHANNELS = {
    "M": ("W_M00_AFH", "Im_W_M00_AFH"),
    "PhiPP": ("W_PhiPP00_AFH", "Im_W_PhiPP00_AFH"),
    "MPhiPP": ("W_MPhiPP00_AFH", "Im_W_MPhiPP00_AFH"),
}
N_DENSE = 121
Q_MIN = 0.2545
Q_MAX = 0.2575
DQ_DENSE = 0.000025
DQ_COARSE = 0.00025
RTOL = 5e-7
ATOL = 2e-12
IMAG_ATOL = 2e-12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def parse_metadata(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def parse_wolfram_float(value: str) -> float:
    return float(value.strip().replace("*^", "e"))


def resolve_coarse_column(row: dict[str, str], column: str) -> str:
    """Resolve the canonical or legacy native coarse-header spelling.

    The 2,401-node ``phi_response_native`` export labels the three imaginary
    components ``Im_W_M00``, ``Im_W_PhiPP00`` and ``Im_W_MPhiPP00``. The dense
    export uses the suffixed AFH names. Both label the same native entries.
    """
    if column in row:
        return column
    legacy = column[:-4] if column.endswith("_AFH") else column
    if legacy in row:
        return legacy
    raise ValueError(f"missing native response column {column!r}")


def close(a: float, b: float) -> bool:
    return abs(a - b) <= ATOL + RTOL * max(abs(a), abs(b))


def validate(dense_csv: Path, dense_metadata: Path, coarse_csv: Path) -> dict:
    dense_meta = parse_metadata(dense_metadata)
    required_meta = {
        "source": "AFH DMFormFactor v6.0 native Wolfram execution",
        "isotope": "Xe-131",
        "Z": "54",
        "responses": "ResponseNuclear[y,index,0,0], indices=1,4,7",
        "response_map": "M=1;PhiPP=4;MPhiPP=7",
        "q_grid": "121 uniform nodes from 0.2545 to 0.2575 GeV, step 0.000025 GeV",
        "isospin": "tau1=tau2=0; raw AFH isoscalar package convention",
        "normalization": "raw AFH package response; no physical equal-p/n factor-four rescaling",
        "AFH_source_sha256": AFH_SHA256,
        "rows": str(N_DENSE),
    }
    for key, expected in required_meta.items():
        if dense_meta.get(key) != expected:
            raise ValueError(f"dense native metadata mismatch for {key}: {dense_meta.get(key)!r}")

    wolfram_version = dense_meta.get("wolfram_version", "")
    if "14.2.0" not in wolfram_version:
        raise ValueError(f"expected Wolfram 14.2.0, got {wolfram_version!r}")
    reported_imag = parse_wolfram_float(dense_meta.get("max_imaginary_residual", "inf"))
    if not math.isfinite(reported_imag) or reported_imag > IMAG_ATOL:
        raise ValueError(f"reported native imaginary residual too large: {reported_imag}")

    dense = read_csv(dense_csv)
    coarse = read_csv(coarse_csv)
    if len(dense) != N_DENSE:
        raise ValueError(f"expected {N_DENSE} dense rows, got {len(dense)}")
    if len(coarse) != 2401:
        raise ValueError(f"expected 2,401 coarse native rows, got {len(coarse)}")

    coarse_index = {}
    for row in coarse:
        q = parse_wolfram_float(row["q_GeV"])
        key = round(q, 10)
        if key in coarse_index:
            raise ValueError(f"duplicate coarse q node {q}")
        coarse_index[key] = row

    max_imag = 0.0
    max_common_abs = {name: 0.0 for name in CHANNELS}
    max_common_rel = {name: 0.0 for name in CHANNELS}
    common_points = 0
    q_values = []
    for i, row in enumerate(dense):
        if int(row["A"]) != 131:
            raise ValueError(f"dense row {i} has A={row['A']}, expected 131")
        q = parse_wolfram_float(row["q_GeV"])
        expected_q = Q_MIN + i * DQ_DENSE
        if not math.isclose(q, expected_q, rel_tol=0.0, abs_tol=2e-12):
            raise ValueError(f"dense q grid mismatch at row {i}: {q} != {expected_q}")
        q_values.append(q)
        if not math.isfinite(parse_wolfram_float(row["y"])):
            raise ValueError(f"non-finite y at dense row {i}")
        for name, (real_col, imag_col) in CHANNELS.items():
            real = parse_wolfram_float(row[real_col])
            imag = parse_wolfram_float(row[imag_col])
            if not math.isfinite(real) or not math.isfinite(imag):
                raise ValueError(f"non-finite {name} response at dense row {i}")
            max_imag = max(max_imag, abs(imag))

        if i % 10 == 0:
            key = round(q, 10)
            if key not in coarse_index:
                raise ValueError(f"missing common coarse node at q={q:.12g}")
            coarse_row = coarse_index[key]
            if abs(parse_wolfram_float(coarse_row["q_GeV"]) - q) > 2e-12:
                raise ValueError(f"coarse q mismatch at common node q={q}")
            for name, (real_col, imag_col) in CHANNELS.items():
                for column in (real_col, imag_col):
                    a = parse_wolfram_float(row[column])
                    b = parse_wolfram_float(
                        coarse_row[resolve_coarse_column(coarse_row, column)]
                    )
                    diff = abs(a - b)
                    rel = diff / max(abs(a), abs(b), 1e-300)
                    if not close(a, b):
                        raise ValueError(
                            f"native dense/coarse {name} mismatch at q={q:.12g}, "
                            f"column={column}: dense={a:.16g}, coarse={b:.16g}"
                        )
                    if column == real_col:
                        max_common_abs[name] = max(max_common_abs[name], diff)
                        max_common_rel[name] = max(max_common_rel[name], rel)
            common_points += 1

    if max_imag > IMAG_ATOL:
        raise ValueError(f"native imaginary residual too large: {max_imag}")
    if common_points != 13:
        raise ValueError(f"expected 13 common coarse-grid points, got {common_points}")
    if not math.isclose(q_values[0], Q_MIN, abs_tol=2e-12):
        raise ValueError("dense q minimum mismatch")
    if not math.isclose(q_values[-1], Q_MAX, abs_tol=2e-12):
        raise ValueError("dense q maximum mismatch")

    return {
        "status": "PASS_NATIVE_XE131_DENSE_CHARGE_DIP",
        "scope": "native Wolfram AFH v6.0 Xe-131 M/PhiPP/M-PhiPP response export and overlap consistency",
        "native_afh_dense_q_validated": True,
        "native_afh_full_seven_isotope_gate": "separate gate; this result does not replace it",
        "isotope": "Xe-131",
        "response_indices": {"M": 1, "PhiPP": 4, "MPhiPP": 7},
        "rows": len(dense),
        "q_min_GeV": q_values[0],
        "q_max_GeV": q_values[-1],
        "q_step_GeV": DQ_DENSE,
        "coarse_rows": len(coarse),
        "common_nodes_compared": common_points,
        "max_imaginary_residual": max_imag,
        "imaginary_tolerance": IMAG_ATOL,
        "common_node_max_absolute_difference": max_common_abs,
        "common_node_max_relative_difference": max_common_rel,
        "rtol": RTOL,
        "atol": ATOL,
        "AFH_source_sha256": AFH_SHA256,
        "source_commit": dense_meta.get("source_commit"),
        "wolfram_version": wolfram_version,
        "dense_csv_sha256": sha256(dense_csv),
        "dense_metadata_sha256": sha256(dense_metadata),
        "coarse_native_csv_sha256": sha256(coarse_csv),
        "normalization": "raw AFH isoscalar package response; no equal-p/n factor-four conversion in exported columns",
        "acceptance_note": "This validates the dense Xe-131 charge-response export and its 13 overlapping coarse-grid nodes. It does not validate the spatial AFH multipoles or the three-body tensor contraction.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dense-csv", type=Path, required=True)
    parser.add_argument("--dense-metadata", type=Path, required=True)
    parser.add_argument("--coarse-csv", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.dense_csv, args.dense_metadata, args.coarse_csv)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
