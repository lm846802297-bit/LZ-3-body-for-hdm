#!/usr/bin/env python3
"""Direct P3-B spatial-response comparison with native AFH Wolfram exports.

A PASS is emitted only when the pinned AFH source hash matches, all 16,807
isotope/q rows and the three spatial channels agree, and native imaginary
residuals are below tolerance.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
J_BY_A = {128: 0.0, 129: 0.5, 130: 0.0, 131: 1.5, 132: 0.0, 134: 0.0, 136: 0.0}
NQ = 2401
CHANNELS = {
    "Delta": ("W_Delta_AFH_package", "W_Delta00_AFH"),
    "SigmaPrime": ("W_SigmaPrime_AFH_package", "W_SigmaPrime00_AFH"),
    "SigmaPrimeDelta": ("W_SigmaPrimeDelta_AFH_package", "W_SigmaPrimeDelta00_AFH"),
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

def index(rows, label):
    out = {}
    for row in rows:
        key = (int(float(row["A"])), round(float(row["q_GeV"]), 10))
        if key in out:
            raise ValueError(f"duplicate {label} row {key}")
        out[key] = row
    return out

def parse_kv(path: Path):
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out

def compare(joined, p3_col, native_col, *, scale_native=False):
    max_abs = max_rel = 0.0
    worst = None
    failed = 0
    for key, p3, native in joined:
        a, b = float(p3[p3_col]), float(native[native_col])
        if scale_native:
            J = float(p3["J_A"])
            c0 = float(p3["common_matrix_normalization"])
            b *= 4.0 * c0 * 4.0 * math.pi / (2.0 * J + 1.0)
            a = float(p3[p3_col])
        d = abs(a-b)
        rel = d / max(abs(a), abs(b), 1e-300)
        max_abs = max(max_abs, d)
        if rel > max_rel:
            max_rel = rel
            worst = {"A": key[0], "q_GeV": key[1], "p3": a, "native_scaled": b}
        if d > 2e-12 + 5e-7 * max(abs(a), abs(b)):
            failed += 1
    return {"passed": failed == 0, "failed_points": failed,
            "max_absolute_difference": max_abs, "max_relative_difference": max_rel,
            "worst_point": worst, "rtol": 5e-7, "atol": 2e-12}

def run(p3_csv: Path, p3_metadata: Path, native_dir: Path, native_metadata: Path, native_manifest: Path):
    p3meta = json.loads(p3_metadata.read_text(encoding="utf-8-sig"))
    nmeta = parse_kv(native_metadata)
    manifest = json.loads(native_manifest.read_text(encoding="utf-8-sig"))
    expected_commit = "dcefbeb7ad705b6c03f2b4689200eb1d9252e67b"
    if manifest.get("repository") != "lm846802297-bit/LZ-3-body-for-hdm":
        raise ValueError("native manifest repository mismatch")
    if manifest.get("source_commit") != expected_commit:
        raise ValueError(f"native source commit mismatch: {manifest.get('source_commit')}")
    if manifest.get("native_package") != "AFH DMFormFactor v6.0":
        raise ValueError("native package identity mismatch")
    if manifest.get("isotopes") != list(ISOTOPES):
        raise ValueError("native manifest isotope set mismatch")
    if manifest.get("q_grid") != {"points": 2401, "q_min_GeV": 0.0, "q_max_GeV": 0.6, "step_GeV": 0.00025}:
        raise ValueError("native manifest q grid mismatch")
    indices = manifest.get("response_indices", {})
    if (indices.get("SigmaPrime"), indices.get("Delta"), indices.get("SigmaPrimeDelta")) != (3, 6, 8):
        raise ValueError("native manifest AFH response-index mapping mismatch")
    full_gate = manifest.get("comparison") or {}
    if full_gate.get("status") != "PASS" or full_gate.get("native_afh_validated") is not True or full_gate.get("rows_compared") != 16807:
        raise ValueError("full native eight-response AFH gate has not passed")
    source_match = p3meta["source_file_sha256"] == nmeta.get("AFH_source_sha256")
    if not source_match:
        raise ValueError("AFH source SHA-256 mismatch between P3 metadata and native export")
    p3_csv_sha = sha256(p3_csv)
    if p3meta.get("response_file_sha256") != p3_csv_sha:
        raise ValueError("P3-B CSV SHA-256 does not match its artifact metadata")
    if int(nmeta.get("rows", "-1")) != 16807:
        raise ValueError(f"native metadata row count is not 16807: {nmeta.get('rows')}")
    if tuple(p3meta["isotopes"]) != ISOTOPES or int(p3meta["response_rows"]) != 16807:
        raise ValueError("P3 metadata isotope set or row count mismatch")

    p3 = index(read_csv(p3_csv), "P3-B")
    native_rows = []
    for A in ISOTOPES:
        path = native_dir / f"afh_v6_xe{A}_eight_response_native.csv"
        if not path.is_file():
            raise FileNotFoundError(f"missing native export: {path}")
        native_rows.extend(read_csv(path))
    native = index(native_rows, "native AFH")
    expected = {(A, round(i*0.00025, 10)) for A in ISOTOPES for i in range(NQ)}
    if p3.keys() != expected or native.keys() != expected:
        raise ValueError(
            f"key mismatch: P3 missing/extra={len(expected-p3.keys())}/{len(p3.keys()-expected)}, "
            f"native missing/extra={len(expected-native.keys())}/{len(native.keys()-expected)}"
        )

    joined = []
    max_y_diff = max_imag = 0.0
    for key in sorted(expected):
        p, n = p3[key], native[key]
        if float(p["J_A"]) != J_BY_A[key[0]]:
            raise ValueError(f"unexpected nuclear spin for Xe-{key[0]} at {key}")
        max_y_diff = max(max_y_diff, abs(float(p["y"])-float(n["y"])))
        for label, (_, native_col) in CHANNELS.items():
            im = abs(float(n[f"Im_{native_col}"]))
            max_imag = max(max_imag, im)
        joined.append((key, p, n))
    if max_y_diff > 2e-14:
        raise ValueError(f"native/P3 y mismatch: {max_y_diff}")
    if max_imag > 2e-12:
        raise ValueError(f"native imaginary residual too large: {max_imag}")

    raw = {
        label: compare(joined, p3_col, native_col)
        for label, (p3_col, native_col) in CHANNELS.items()
    }
    physical_columns = {
        "Delta": "R_Delta_equal_pn",
        "SigmaPrime": "R_SigmaPrime_equal_pn",
        "SigmaPrimeDelta": "R_SigmaPrimeDelta_equal_pn",
    }
    physical = {}
    for label, (_, native_col) in CHANNELS.items():
        # Compare physical equal-p/n P3 response to the raw native W converted
        # with the same AFH factor four and P3's common OBDME correction C0.
        physical[label] = compare(
            joined, physical_columns[label], native_col, scale_native=True
        )
    passed = (all(x["passed"] for x in raw.values())
              and all(x["passed"] for x in physical.values())
              and max_imag <= 2e-12 and max_y_diff <= 2e-14)
    return {
        "status": "PASS_NATIVE_AFH_SPATIAL_CROSSCHECK" if passed else "FAIL",
        "scope": "Direct P3-B versus native Wolfram AFH indices 3, 6 and 8",
        "native_afh_validated": bool(passed),
        "afh_source_sha256_match": source_match,
        "wolfram_version": nmeta.get("wolfram_version"),
        "isotopes": list(ISOTOPES), "points_per_isotope": NQ,
        "rows_compared": len(joined),
        "max_y_absolute_difference": max_y_diff,
        "max_native_imaginary_residual": max_imag,
        "native_imaginary_tolerance": 2e-12,
        "P3_B_csv_sha256": p3_csv_sha,
        "P3_B_metadata_sha256": sha256(p3_metadata),
        "native_metadata": nmeta,
        "native_source_commit": manifest.get("source_commit"),
        "native_control_run_id": manifest.get("control_run_id"),
        "native_control_run_attempt": manifest.get("control_run_attempt"),
        "raw_package_response_comparisons": raw,
        "physical_equal_pn_comparisons": physical,
        "acceptance_note": "A PASS validates these three P3-B spatial channels against the pinned AFH v6.0 Wolfram source. It does not by itself validate the full three-body tensor contraction or event rate."
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--p3-csv", type=Path, required=True)
    p.add_argument("--p3-metadata", type=Path, required=True)
    p.add_argument("--native-dir", type=Path, required=True)
    p.add_argument("--native-metadata", type=Path, required=True)
    p.add_argument("--native-manifest", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    a = p.parse_args()
    result = run(a.p3_csv, a.p3_metadata, a.native_dir, a.native_metadata, a.native_manifest)
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS_NATIVE_AFH_SPATIAL_CROSSCHECK":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
