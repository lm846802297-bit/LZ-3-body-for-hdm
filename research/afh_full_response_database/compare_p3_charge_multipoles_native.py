#!/usr/bin/env python3
"""Validate native AFH M_J/PhiPP_J rank amplitudes against native responses."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

EXPECTED_SOURCE_SHA256 = "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372"
EXPECTED_RANKS = {129: (0, 1), 131: (0, 1, 2, 3)}
NQ = 2401
ATOL = 2.0e-12
RTOL = 5.0e-7
IMAG_ATOL = 2.0e-12


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def close(a: float, b: float) -> bool:
    return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= ATOL + RTOL * max(abs(a), abs(b))


def key(row: dict) -> tuple[int, float]:
    return int(row["A"]), round(float(row["q_GeV"]), 10)


def run(native_dir: Path) -> dict:
    meta_path = native_dir / "charge_multipole_metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
    if meta.get("status") != "PASS_NATIVE_AFH_CHARGE_MULTIPOLE_RANK_SUM":
        raise ValueError("native charge-multipole exporter did not report PASS")
    if meta.get("AFH_source_sha256") != EXPECTED_SOURCE_SHA256:
        raise ValueError("AFH source SHA-256 mismatch")
    if meta.get("native_afh_charge_multipoles_validated") is not True:
        raise ValueError("native charge multipole validation flag is not true")
    if meta.get("rank_map") != ["129=0,1", "131=0,1,2,3"]:
        raise ValueError(f"unexpected charge multipole rank map: {meta.get('rank_map')}")

    multipole_path = native_dir / meta["multipole_file"]
    validation_path = native_dir / meta["validation_file"]
    if sha256(multipole_path) != meta.get("multipole_file_sha256"):
        raise ValueError("native charge multipole CSV SHA-256 mismatch")
    if sha256(validation_path) != meta.get("validation_file_sha256"):
        raise ValueError("native charge rank-sum validation CSV SHA-256 mismatch")

    multipoles = read_csv(multipole_path)
    validations = read_csv(validation_path)
    expected_multipole_rows = NQ * sum(len(v) for v in EXPECTED_RANKS.values())
    expected_validation_rows = NQ * len(EXPECTED_RANKS)
    if len(multipoles) != expected_multipole_rows:
        raise ValueError(f"charge multipole row count {len(multipoles)} != {expected_multipole_rows}")
    if len(validations) != expected_validation_rows:
        raise ValueError(f"rank-sum validation row count {len(validations)} != {expected_validation_rows}")

    grouped = defaultdict(list)
    max_imag = 0.0
    for row in multipoles:
        A = int(row["A"])
        J = int(row["multipole_J"])
        if A not in EXPECTED_RANKS or J not in EXPECTED_RANKS[A]:
            raise ValueError(f"unexpected isotope/rank in charge multipole table: A={A}, J={J}")
        max_imag = max(
            max_imag, abs(float(row["Im_M_J_native"])),
            abs(float(row["Im_PhiPP_J_native"]))
        )
        grouped[key(row)].append(row)
    if max_imag > IMAG_ATOL:
        raise ValueError(f"native charge multipole imaginary residual {max_imag} > {IMAG_ATOL}")

    validation_index = {}
    maxima = {"M": 0.0, "PhiPP": 0.0, "M_PhiPP": 0.0}
    max_abs = 0.0
    for row in validations:
        k = key(row)
        if k in validation_index:
            raise ValueError(f"duplicate rank-sum validation row {k}")
        validation_index[k] = row
    if set(validation_index) != set(grouped):
        raise ValueError("native charge multipole and validation q grids differ")

    for k, rows in grouped.items():
        rows.sort(key=lambda r: int(r["multipole_J"]))
        A = k[0]
        got_ranks = tuple(int(r["multipole_J"]) for r in rows)
        if got_ranks != EXPECTED_RANKS[A]:
            raise ValueError(f"rank list mismatch at {k}: {got_ranks}")
        M = [complex(float(r["M_J_native"]), float(r["Im_M_J_native"])) for r in rows]
        P = [complex(float(r["PhiPP_J_native"]), float(r["Im_PhiPP_J_native"])) for r in rows]
        rank_sums = {
            "M": 0.25 * sum(abs(x) ** 2 for x in M),
            "PhiPP": 0.25 * sum(abs(x) ** 2 for x in P),
            "M_PhiPP": 0.25 * sum((x * y.conjugate()).real for x, y in zip(M, P)),
        }
        vr = validation_index[k]
        native_values = {
            "M": float(vr["W_M_native"]),
            "PhiPP": float(vr["W_PhiPP_native"]),
            "M_PhiPP": float(vr["W_MPhiPP_native"]),
        }
        stored_sums = {
            "M": float(vr["W_M_rank_sum"]),
            "PhiPP": float(vr["W_PhiPP_rank_sum"]),
            "M_PhiPP": float(vr["W_MPhiPP_rank_sum"]),
        }
        for channel in rank_sums:
            if not close(rank_sums[channel], stored_sums[channel]):
                raise ValueError(f"multipole-to-validation CSV mismatch {channel} at {k}")
            difference = abs(rank_sums[channel] - native_values[channel])
            max_abs = max(max_abs, difference)
            maxima[channel] = max(
                maxima[channel],
                difference / max(abs(rank_sums[channel]), abs(native_values[channel]), 1.0e-8)
            )
            if not close(rank_sums[channel], native_values[channel]):
                raise ValueError(f"native AFH response rank-sum mismatch {channel} at {k}")

    return {
        "status": "PASS_NATIVE_AFH_CHARGE_MULTIPOLE_RANK_SUM",
        "native_afh_charge_multipoles_validated": True,
        "AFH_source_sha256": EXPECTED_SOURCE_SHA256,
        "isotopes": [129, 131],
        "rank_map": {"129": [0, 1], "131": [0, 1, 2, 3]},
        "multipole_rows": len(multipoles),
        "validation_rows": len(validations),
        "max_native_imaginary_residual": max_imag,
        "max_rank_sum_absolute_residual": max_abs,
        "max_rank_sum_scaled_relative_residual_by_channel": maxima,
        "acceptance": {"atol": ATOL, "rtol": RTOL, "imaginary_atol": IMAG_ATOL},
        "multipole_file_sha256": meta["multipole_file_sha256"],
        "validation_file_sha256": meta["validation_file_sha256"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-dir", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.native_dir)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
