#!/usr/bin/env python3
"""Validate the rank-resolved P3-B AFH spatial multipole archive."""
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
RAW = {
    "W_Delta": ("W_Delta_AFH_package", "W_Delta_J_AFH_package"),
    "W_SigmaPrime": ("W_SigmaPrime_AFH_package", "W_SigmaPrime_J_AFH_package"),
    "W_SigmaPrimeDelta": ("W_SigmaPrimeDelta_AFH_package", "W_SigmaPrimeDelta_J_AFH_package"),
}
PHYSICAL = {
    "R_Delta": ("R_Delta_equal_pn", "R_Delta_J_equal_pn"),
    "R_SigmaPrime": ("R_SigmaPrime_equal_pn", "R_SigmaPrime_J_equal_pn"),
    "R_SigmaPrimeDelta": ("R_SigmaPrimeDelta_equal_pn", "R_SigmaPrimeDelta_J_equal_pn"),
}
ATOL, RTOL = 2e-14, 2e-12

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def qkey(row):
    return (int(float(row["A"])), round(float(row["q_GeV"]), 10))

def close(a, b):
    return abs(a-b) <= ATOL + RTOL*max(abs(a), abs(b))

def validate(out_dir: Path):
    meta_path = out_dir / "metadata.json"
    response_path = out_dir / "afh_spatial_obdme_responses_7isotope_2401.csv"
    multipole_path = out_dir / "afh_spatial_obdme_multipoles_7isotope_2401.csv"
    for p in (meta_path, response_path, multipole_path):
        if not p.is_file():
            raise FileNotFoundError(p)
    meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
    if meta.get("source_file_sha256") != "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372":
        raise ValueError("AFH source SHA-256 mismatch")
    if tuple(meta.get("isotopes", ())) != ISOTOPES or meta.get("response_rows") != 16807:
        raise ValueError("response isotope set or row count mismatch")
    if meta.get("rankwise_amplitudes_and_signed_interference_saved") is not True:
        raise ValueError("rank-resolved multipole archive is not marked complete")
    if meta.get("response_file_sha256") != sha256(response_path):
        raise ValueError("response CSV SHA-256 mismatch")
    if meta.get("multipole_file_sha256") != sha256(multipole_path):
        raise ValueError("multipole CSV SHA-256 mismatch")

    ranks_by_A = {str(k): [int(x) for x in v] for k, v in meta.get("multipole_ranks_by_isotope", {}).items()}
    if set(map(int, ranks_by_A)) != set(ISOTOPES):
        raise ValueError("multipole rank map does not contain all seven isotopes")
    for A in SPIN_ZERO:
        if ranks_by_A[str(A)]:
            raise ValueError(f"spin-zero Xe-{A} unexpectedly has abnormal multipole ranks")

    response_rows = read_csv(response_path)
    multipole_rows = read_csv(multipole_path)
    expected_response_keys = {(A, round(i*0.00025, 10)) for A in ISOTOPES for i in range(NQ)}
    response_index = {}
    for row in response_rows:
        k = qkey(row)
        if k in response_index:
            raise ValueError(f"duplicate total-response row {k}")
        response_index[k] = row
    if response_index.keys() != expected_response_keys:
        raise ValueError("total response grid is incomplete or contains extra rows")

    expected_multipole_keys = {
        (A, round(i*0.00025, 10), J)
        for A in ISOTOPES for i in range(NQ) for J in ranks_by_A[str(A)]
    }
    multipole_index = {}
    grouped = {}
    max_identity_residual = {k: 0.0 for k in (
        "W_Delta", "W_SigmaPrime", "W_SigmaPrimeDelta",
        "R_Delta", "R_SigmaPrime", "R_SigmaPrimeDelta",
    )}
    max_cs_excess = 0.0
    for row in multipole_rows:
        A, q = qkey(row)
        J = int(float(row["multipole_J"]))
        key = (A, q, J)
        if key in multipole_index:
            raise ValueError(f"duplicate multipole row {key}")
        multipole_index[key] = row
        grouped.setdefault((A, q), []).append(row)
        md, ms = float(row["M_Delta_J"]), float(row["M_SigmaPrime_J"])
        expected_values = {
            "W_Delta_J_AFH_package": 0.25*md*md,
            "W_SigmaPrime_J_AFH_package": 0.25*ms*ms,
            "W_SigmaPrimeDelta_J_AFH_package": 0.25*ms*md,
        }
        for col, value in expected_values.items():
            if not close(float(row[col]), value):
                raise ValueError(f"{col} does not match amplitudes at {key}")
        wd, ws, wx = (expected_values[x] for x in (
            "W_Delta_J_AFH_package", "W_SigmaPrime_J_AFH_package",
            "W_SigmaPrimeDelta_J_AFH_package"
        ))
        max_cs_excess = max(max_cs_excess, max(0.0, abs(wx)-math.sqrt(wd*ws)))
        c0 = float(row["common_matrix_normalization"])
        J_A = float(row["J_A"])
        conv = 4.0*c0*4.0*math.pi/(2.0*J_A+1.0)
        for col, wcol in (
            ("R_Delta_J_equal_pn", "W_Delta_J_AFH_package"),
            ("R_SigmaPrime_J_equal_pn", "W_SigmaPrime_J_AFH_package"),
            ("R_SigmaPrimeDelta_J_equal_pn", "W_SigmaPrimeDelta_J_AFH_package"),
        ):
            if not close(float(row[col]), conv*float(row[wcol])):
                raise ValueError(f"{col} normalization mismatch at {key}")
    if multipole_index.keys() != expected_multipole_keys:
        raise ValueError(
            f"multipole grid mismatch: missing={len(expected_multipole_keys-multipole_index.keys())}, "
            f"extra={len(multipole_index.keys()-expected_multipole_keys)}"
        )

    for A, q in expected_response_keys:
        total = response_index[(A, q)]
        rank_rows = grouped.get((A, q), [])
        for label, (total_col, rank_col) in {**RAW, **PHYSICAL}.items():
            value = math.fsum(float(row[rank_col]) for row in rank_rows)
            expected = float(total[total_col])
            residual = abs(value-expected)
            max_identity_residual[label] = max(max_identity_residual[label], residual)
            if not close(value, expected):
                raise ValueError(
                    f"{label} rank sum mismatch at Xe-{A}, q={q}: "
                    f"rank sum={value:.16g}, total={expected:.16g}"
                )
        if A in SPIN_ZERO and rank_rows:
            raise ValueError(f"spin-zero Xe-{A} has multipole rows")

    expected_multipole_count = NQ*sum(len(ranks_by_A[str(A)]) for A in ISOTOPES)
    if len(multipole_rows) != expected_multipole_count:
        raise ValueError("multipole row count does not match isotope rank map")
    if meta.get("multipole_rows") != len(multipole_rows):
        raise ValueError("metadata multipole row count mismatch")
    stored = meta.get("multipole_reconstruction_max_absolute_residual", {})
    for name, value in max_identity_residual.items():
        if name not in stored or not math.isfinite(float(stored[name])):
            raise ValueError(f"missing/non-finite stored reconstruction residual for {name}")
        if float(stored[name]) > ATOL + RTOL*max(abs(value), 1e-300):
            raise ValueError(f"stored reconstruction residual inconsistent for {name}")

    return {
        "status": "PASS_AFH_SPATIAL_MULTIPOLE_ARCHIVE",
        "rows_total_responses": len(response_rows),
        "rows_rank_resolved_multipoles": len(multipole_rows),
        "multipole_ranks_by_isotope": ranks_by_A,
        "response_csv_sha256": sha256(response_path),
        "multipole_csv_sha256": sha256(multipole_path),
        "max_rank_sum_reconstruction_absolute_residual": max_identity_residual,
        "max_rankwise_cauchy_excess": max_cs_excess,
        "native_afh_validated": False,
        "scope": "rank-resolved Python AFH archive integrity only; native Wolfram comparison remains a separate gate",
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    a = p.parse_args()
    result = validate(a.out_dir)
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS_AFH_SPATIAL_MULTIPOLE_ARCHIVE":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
