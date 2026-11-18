#!/usr/bin/env python3
"""Compare P3-B Python OBDME multipole amplitudes with native Wolfram AFH."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ISOTOPES = (129, 131)
RANKS = {129: (1,), 131: (1, 2, 3)}
NQ = 2401
EXPECTED_NATIVE_SOURCE_COMMIT = "e1e9c85530a7d609561b34e2c2df5ab36e5c5b89"
EXPECTED_AFH_SOURCE_SHA256 = "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372"
RTOL, ATOL, IMAG_ATOL = 5e-7, 2e-12, 2e-12

CHANNELS = {
    "Delta": ("M_Delta_J", "M_Delta_J_native", "Im_M_Delta_J_native"),
    "SigmaPrime": ("M_SigmaPrime_J", "M_SigmaPrime_J_native", "Im_M_SigmaPrime_J_native"),
}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def parse_kv(path: Path):
    out = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out

def key(row):
    return (
        int(float(row["A"])),
        round(float(row["q_GeV"]), 10),
        int(float(row["multipole_J"])),
    )

def compare_rows(p3_rows, native_rows, p3_metadata, native_metadata, native_manifest):
    if p3_metadata.get("source_file_sha256") != EXPECTED_AFH_SOURCE_SHA256:
        raise ValueError("P3-B AFH source SHA-256 mismatch")
    if p3_metadata.get("rankwise_amplitudes_and_signed_interference_saved") is not True:
        raise ValueError("P3-B rank-resolved amplitude archive is not complete")
    if p3_metadata.get("multipole_file_sha256") is None:
        raise ValueError("P3-B multipole artifact hash is missing")
    if native_metadata.get("AFH_source_sha256") != EXPECTED_AFH_SOURCE_SHA256:
        raise ValueError("native Wolfram AFH source SHA-256 mismatch")
    if native_metadata.get("source_commit") != EXPECTED_NATIVE_SOURCE_COMMIT:
        raise ValueError("native Wolfram source commit does not match the reviewed WLS export revision")
    if native_metadata.get("rows") != str(NQ * sum(len(RANKS[A]) for A in ISOTOPES)):
        raise ValueError("native multipole metadata row count mismatch")
    if native_metadata.get("isotopes") != "129,131":
        raise ValueError("native multipole isotope set mismatch")
    if native_metadata.get("q_grid") != "2401 uniform nodes from 0 to 0.6 GeV, step 0.00025 GeV":
        raise ValueError("native multipole q-grid metadata mismatch")
    if native_metadata.get("normalization") != "raw AFH package amplitudes; no equal-p/n factor-four conversion":
        raise ValueError("native multipole normalization convention mismatch")
    if native_metadata.get("imaginary_parts") != "exported separately for both amplitude channels":
        raise ValueError("native imaginary-amplitude provenance missing")

    gate = native_manifest.get("comparison") or {}
    if gate.get("status") != "PASS" or gate.get("native_afh_validated") is not True or gate.get("rows_compared") != 16807:
        raise ValueError("full seven-isotope native AFH ResponseNuclear gate has not passed")
    if native_manifest.get("source_commit") != EXPECTED_NATIVE_SOURCE_COMMIT:
        raise ValueError("native run manifest source commit mismatch")
    native_gate = native_manifest.get("native_spatial_multipoles") or {}
    if native_gate.get("rows") != len(native_rows):
        raise ValueError("native run manifest multipole row count mismatch")

    p3_index = {}
    for row in p3_rows:
        k = key(row)
        if k in p3_index:
            raise ValueError(f"duplicate P3-B multipole row {k}")
        p3_index[k] = row
    native_index = {}
    for row in native_rows:
        k = key(row)
        if k in native_index:
            raise ValueError(f"duplicate native multipole row {k}")
        native_index[k] = row

    expected = {
        (A, round(i*0.00025, 10), J)
        for A in ISOTOPES for i in range(NQ) for J in RANKS[A]
    }
    if p3_index.keys() != expected:
        raise ValueError(
            f"P3-B multipole key mismatch: missing={len(expected-p3_index.keys())}, "
            f"extra={len(p3_index.keys()-expected)}"
        )
    if native_index.keys() != expected:
        raise ValueError(
            f"native multipole key mismatch: missing={len(expected-native_index.keys())}, "
            f"extra={len(native_index.keys()-expected)}"
        )

    maxima = {
        name: {"max_absolute_difference": 0.0, "max_relative_difference": 0.0,
               "failed_points": 0, "worst_point": None}
        for name in CHANNELS
    }
    max_imag = 0.0
    max_y_diff = 0.0
    for k in sorted(expected):
        p, n = p3_index[k], native_index[k]
        max_y_diff = max(max_y_diff, abs(float(p["y"])-float(n["y"])))
        for name, (p3_col, native_col, imag_col) in CHANNELS.items():
            a = float(p[p3_col])
            b = float(n[native_col])
            im = abs(float(n[imag_col]))
            max_imag = max(max_imag, im)
            d = abs(a-b)
            rel = d / max(abs(a), abs(b), 1e-300)
            rec = maxima[name]
            rec["max_absolute_difference"] = max(rec["max_absolute_difference"], d)
            if rel > rec["max_relative_difference"]:
                rec["max_relative_difference"] = rel
                rec["worst_point"] = {
                    "A": k[0], "q_GeV": k[1], "J": k[2],
                    "p3_python": a, "native_wolfram": b
                }
            if d > ATOL + RTOL*max(abs(a), abs(b)):
                rec["failed_points"] += 1

    if max_imag > IMAG_ATOL:
        raise ValueError(f"native multipole imaginary residual exceeds tolerance: {max_imag}")
    if max_y_diff > 2e-14:
        raise ValueError(f"native/P3 y mismatch: {max_y_diff}")
    passed = all(x["failed_points"] == 0 for x in maxima.values())
    return {
        "status": "PASS_NATIVE_AFH_MULTIPOLE_AMPLITUDE_CROSSCHECK" if passed else "FAIL",
        "scope": "direct P3-B versus native Wolfram AFH DeltaJ and SigmaPJ amplitudes for Xe-129 and Xe-131",
        "native_afh_multipole_amplitudes_validated": bool(passed),
        "native_afh_validated": True,
        "isotopes": list(ISOTOPES),
        "rank_map": {str(A): list(RANKS[A]) for A in ISOTOPES},
        "q_points_per_isotope": NQ,
        "rows_compared": len(expected),
        "max_y_absolute_difference": max_y_diff,
        "max_native_imaginary_residual": max_imag,
        "native_imaginary_tolerance": IMAG_ATOL,
        "rtol": RTOL,
        "atol": ATOL,
        "P3_B_multipole_sha256": p3_metadata.get("multipole_file_sha256"),
        "native_multipole_csv_sha256": native_gate.get("csv_sha256"),
        "native_multipole_metadata_sha256": native_gate.get("metadata_sha256"),
        "native_source_commit": native_metadata.get("source_commit"),
        "native_wolfram_version": native_metadata.get("wolfram_version"),
        "amplitude_comparisons": maxima,
        "acceptance_note": "The raw AFH package multipole amplitudes are compared before the physical equal-p/n factor-four and common C0 response conversion. This validates the two spatial amplitude channels, not the full three-body tensor contraction or event rate."
    }

def run(p3_multipole_csv: Path, p3_metadata_path: Path,
        native_multipole_csv: Path, native_metadata_path: Path,
        native_manifest_path: Path, out_json: Path):
    p3meta = json.loads(p3_metadata_path.read_text(encoding="utf-8-sig"))
    native_meta = parse_kv(native_metadata_path)
    native_manifest = json.loads(native_manifest_path.read_text(encoding="utf-8-sig"))
    p3sha = sha256(p3_multipole_csv)
    if p3meta.get("multipole_file_sha256") != p3sha:
        raise ValueError("P3-B multipole CSV hash does not match P3-B metadata")
    native_sha = sha256(native_multipole_csv)
    native_meta_sha = sha256(native_metadata_path)
    native_gate = native_manifest.get("native_spatial_multipoles") or {}
    if native_gate.get("csv_sha256") != native_sha:
        raise ValueError("native multipole CSV hash does not match native run manifest")
    if native_gate.get("metadata_sha256") != native_meta_sha:
        raise ValueError("native multipole metadata hash does not match native run manifest")
    rows = compare_rows(
        read_csv(p3_multipole_csv), read_csv(native_multipole_csv),
        p3meta, native_meta, native_manifest
    )
    rows["P3_B_multipole_sha256"] = p3sha
    rows["native_multipole_csv_sha256"] = native_sha
    rows["native_run_id"] = native_manifest.get("control_run_id")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(rows, indent=2)+"\n", encoding="utf-8")
    return rows

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--p3-multipole-csv", type=Path, required=True)
    p.add_argument("--p3-metadata", type=Path, required=True)
    p.add_argument("--native-multipole-csv", type=Path, required=True)
    p.add_argument("--native-metadata", type=Path, required=True)
    p.add_argument("--native-manifest", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    a = p.parse_args()
    result = run(a.p3_multipole_csv, a.p3_metadata, a.native_multipole_csv,
                 a.native_metadata, a.native_manifest, a.out_json)
    print(json.dumps({"status": result["status"], "rows_compared": result["rows_compared"],
                      "max_native_imaginary_residual": result["max_native_imaginary_residual"]}, indent=2))
    if result["status"] != "PASS_NATIVE_AFH_MULTIPOLE_AMPLITUDE_CROSSCHECK":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
