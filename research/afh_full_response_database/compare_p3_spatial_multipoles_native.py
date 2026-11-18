#!/usr/bin/env python3
"""Pointwise P3-B versus native AFH v6.0 spatial response/multipole check.

This compares:
  (1) all 16,807 total-response grid rows for Delta, SigmaPrime and the
      signed SigmaPrime-Delta response;
  (2) all 9,604 rank-resolved Xe-129/Xe-131 DeltaJ and SigmaPJ amplitudes,
      their raw AFH bilinears, and their physical equal-p/n C0-corrected rows.

The native full eight-response comparison must already have passed. A PASS
validates the P3-B spatial OBDME/multipole implementation against native
Wolfram AFH; it does not by itself validate the three-body particle tensor
or a detector-level rate.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
SPIN = {128: 0.0, 129: 0.5, 130: 0.0, 131: 1.5, 132: 0.0, 134: 0.0, 136: 0.0}
NQ = 2401
RANKS = {129: (1,), 131: (1, 2, 3)}
EXPECTED_MULTIPOLE_ROWS = NQ * sum(len(v) for v in RANKS.values())
SOURCE_SHA256 = "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372"
RTOL = 5e-7
ATOL = 2e-12
IMAG_ATOL = 2e-12

TOTAL_CHANNELS = {
    "Delta": ("W_Delta_AFH_package", "W_Delta00_AFH", "R_Delta_equal_pn"),
    "SigmaPrime": ("W_SigmaPrime_AFH_package", "W_SigmaPrime00_AFH", "R_SigmaPrime_equal_pn"),
    "SigmaPrimeDelta": ("W_SigmaPrimeDelta_AFH_package", "W_SigmaPrimeDelta00_AFH", "R_SigmaPrimeDelta_equal_pn"),
}
RANK_CHANNELS = {
    "Delta": ("M_Delta_J", "M_Delta_J_native",
              "W_Delta_J_AFH_package", "R_Delta_J_equal_pn"),
    "SigmaPrime": ("M_SigmaPrime_J", "M_SigmaPrime_J_native",
                   "W_SigmaPrime_J_AFH_package", "R_SigmaPrime_J_equal_pn"),
    "SigmaPrimeDelta": (None, None,
                        "W_SigmaPrimeDelta_J_AFH_package",
                        "R_SigmaPrimeDelta_J_equal_pn"),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_kv(path: Path) -> dict:
    result = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def _response_key(row: dict) -> tuple[int, float]:
    return int(float(row["A"])), round(float(row["q_GeV"]), 10)


def _rank_key(row: dict) -> tuple[int, float, int]:
    A, q = _response_key(row)
    return A, q, int(float(row["multipole_J"]))


def _close(a: float, b: float, *, rtol=RTOL, atol=ATOL) -> bool:
    return math.isfinite(a) and math.isfinite(b) and abs(a-b) <= atol + rtol*max(abs(a), abs(b))


def _index(rows: list[dict], key_fn, label: str) -> dict:
    result = {}
    for row in rows:
        key = key_fn(row)
        if key in result:
            raise ValueError(f"duplicate {label} row {key}")
        result[key] = row
    return result


def compare_total_response_rows(p3_rows: list[dict], native_rows: list[dict]) -> dict:
    p3 = _index(p3_rows, _response_key, "P3 total-response")
    native = _index(native_rows, _response_key, "native total-response")
    expected = {
        (A, round(i*0.00025, 10))
        for A in ISOTOPES for i in range(NQ)
    }
    if p3.keys() != expected or native.keys() != expected:
        raise ValueError(
            "total-response grid mismatch: "
            f"P3 missing/extra={len(expected-p3.keys())}/{len(p3.keys()-expected)}, "
            f"native missing/extra={len(expected-native.keys())}/{len(native.keys()-expected)}"
        )

    metrics = {}
    for label, (p3_raw, native_raw, p3_physical) in TOTAL_CHANNELS.items():
        raw_abs = raw_rel = phys_abs = phys_rel = 0.0
        raw_worst = phys_worst = None
        raw_fail = phys_fail = 0
        for key in sorted(expected):
            prow, nrow = p3[key], native[key]
            a, b = float(prow[p3_raw]), float(nrow[native_raw])
            d = abs(a-b)
            rel = d/max(abs(a), abs(b), 1e-300)
            if d > raw_abs:
                raw_abs, raw_worst = d, {"A": key[0], "q_GeV": key[1], "P3": a, "native": b}
            raw_rel = max(raw_rel, rel)
            if not _close(a, b):
                raw_fail += 1

            J_A = float(prow["J_A"])
            C0 = float(prow["common_matrix_normalization"])
            factor = 4.0*C0*4.0*math.pi/(2.0*J_A+1.0)
            physical_native = factor*b
            physical_p3 = float(prow[p3_physical])
            dp = abs(physical_p3-physical_native)
            rp = dp/max(abs(physical_p3), abs(physical_native), 1e-300)
            if dp > phys_abs:
                phys_abs, phys_worst = dp, {
                    "A": key[0], "q_GeV": key[1],
                    "P3": physical_p3, "native_scaled": physical_native
                }
            phys_rel = max(phys_rel, rp)
            if not _close(physical_p3, physical_native):
                phys_fail += 1
        metrics[label] = {
            "raw_package": {
                "passed": raw_fail == 0, "failed_points": raw_fail,
                "max_absolute_difference": raw_abs,
                "max_relative_difference": raw_rel, "worst_point": raw_worst,
            },
            "physical_equal_pn_C0_corrected": {
                "passed": phys_fail == 0, "failed_points": phys_fail,
                "max_absolute_difference": phys_abs,
                "max_relative_difference": phys_rel, "worst_point": phys_worst,
            },
        }
    return {
        "passed": all(
            m[k]["passed"] for m in metrics.values()
            for k in ("raw_package", "physical_equal_pn_C0_corrected")
        ),
        "rows_compared": len(p3),
        "channels": metrics,
    }


def compare_rankwise_multipole_rows(
    p3_rows: list[dict],
    native_rows: list[dict],
    c0_by_A: dict[int, float],
    *,
    rtol: float = RTOL,
    atol: float = ATOL,
    imag_atol: float = IMAG_ATOL,
) -> dict:
    p3 = _index(p3_rows, _rank_key, "P3 rank-resolved")
    native = _index(native_rows, _rank_key, "native rank-resolved")
    expected = {
        (A, round(i*0.00025, 10), J)
        for A, ranks in RANKS.items()
        for i in range(NQ)
        for J in ranks
    }
    if p3.keys() != expected or native.keys() != expected:
        raise ValueError(
            "rank-resolved grid mismatch: "
            f"P3 missing/extra={len(expected-p3.keys())}/{len(p3.keys()-expected)}, "
            f"native missing/extra={len(expected-native.keys())}/{len(native.keys()-expected)}"
        )

    names = (
        "M_Delta_J", "M_SigmaPrime_J",
        "W_Delta_J_AFH_package", "W_SigmaPrime_J_AFH_package",
        "W_SigmaPrimeDelta_J_AFH_package",
        "R_Delta_J_equal_pn", "R_SigmaPrime_J_equal_pn",
        "R_SigmaPrimeDelta_J_equal_pn",
    )
    maxima = {name: {"max_abs": 0.0, "max_rel": 0.0, "worst": None, "failed": 0}
              for name in names}
    max_imag = max_y = 0.0
    for key in sorted(expected):
        prow, nrow = p3[key], native[key]
        A, q, J = key
        if float(prow["J_A"]) != SPIN[A]:
            raise ValueError(f"P3 nuclear spin mismatch at {key}")
        max_y = max(max_y, abs(float(prow["y"])-float(nrow["y"])))
        amp_d = float(nrow["M_Delta_J_native"])
        amp_s = float(nrow["M_SigmaPrime_J_native"])
        im_d = abs(float(nrow["Im_M_Delta_J_native"]))
        im_s = abs(float(nrow["Im_M_SigmaPrime_J_native"]))
        max_imag = max(max_imag, im_d, im_s)
        if max(im_d, im_s) > imag_atol:
            raise ValueError(f"native multipole imaginary residual exceeds tolerance at {key}")

        raw_values = {
            "M_Delta_J": (float(prow["M_Delta_J"]), amp_d),
            "M_SigmaPrime_J": (float(prow["M_SigmaPrime_J"]), amp_s),
            "W_Delta_J_AFH_package": (
                float(prow["W_Delta_J_AFH_package"]), 0.25*amp_d*amp_d
            ),
            "W_SigmaPrime_J_AFH_package": (
                float(prow["W_SigmaPrime_J_AFH_package"]), 0.25*amp_s*amp_s
            ),
            "W_SigmaPrimeDelta_J_AFH_package": (
                float(prow["W_SigmaPrimeDelta_J_AFH_package"]), 0.25*amp_s*amp_d
            ),
        }
        C0 = float(c0_by_A[A])
        factor = 4.0*C0*4.0*math.pi/(2.0*SPIN[A]+1.0)
        raw_values.update({
            "R_Delta_J_equal_pn": (
                float(prow["R_Delta_J_equal_pn"]),
                factor*0.25*amp_d*amp_d
            ),
            "R_SigmaPrime_J_equal_pn": (
                float(prow["R_SigmaPrime_J_equal_pn"]),
                factor*0.25*amp_s*amp_s
            ),
            "R_SigmaPrimeDelta_J_equal_pn": (
                float(prow["R_SigmaPrimeDelta_J_equal_pn"]),
                factor*0.25*amp_s*amp_d
            ),
        })
        for name, (a, b) in raw_values.items():
            m = maxima[name]
            d = abs(a-b)
            rel = d/max(abs(a), abs(b), 1e-300)
            if d > m["max_abs"]:
                m["max_abs"] = d
                m["worst"] = {
                    "A": A, "q_GeV": q, "J": J,
                    "P3": a, "native_reconstructed": b
                }
            m["max_rel"] = max(m["max_rel"], rel)
            if not _close(a, b, rtol=rtol, atol=atol):
                m["failed"] += 1

    if max_y > 2e-14:
        raise ValueError(f"native/P3 rankwise y mismatch: {max_y}")
    return {
        "passed": all(x["failed"] == 0 for x in maxima.values()),
        "rows_compared": len(p3),
        "rank_map": {"129": [1], "131": [1, 2, 3]},
        "max_y_absolute_difference": max_y,
        "max_native_imaginary_residual": max_imag,
        "imaginary_tolerance": imag_atol,
        "comparisons": maxima,
    }


def run(
    p3_dir: Path,
    native_dir: Path,
    native_spatial_dir: Path,
    native_manifest_path: Path,
    expected_source_commit: str,
) -> dict:
    p3meta_path = p3_dir/"metadata.json"
    p3meta = json.loads(p3meta_path.read_text(encoding="utf-8-sig"))
    p3_validation = json.loads((p3_dir/"multipole-validation.json").read_text(encoding="utf-8-sig"))
    native_meta_path = native_dir/"native_metadata.txt"
    native_meta = parse_kv(native_meta_path)
    native_spatial_meta_path = native_spatial_dir/"native_spatial_multipole_metadata.txt"
    native_spatial_meta = parse_kv(native_spatial_meta_path)
    manifest = json.loads(native_manifest_path.read_text(encoding="utf-8-sig"))

    if manifest.get("repository") != "lm846802297-bit/LZ-3-body-for-hdm":
        raise ValueError("native manifest repository mismatch")
    if manifest.get("source_commit") != expected_source_commit:
        raise ValueError("native manifest source commit does not match the pinned workflow input")
    if manifest.get("native_package") != "AFH DMFormFactor v6.0":
        raise ValueError("native AFH package identity mismatch")
    if manifest.get("isotopes") != list(ISOTOPES):
        raise ValueError("native manifest isotope set mismatch")
    if manifest.get("q_grid") != {
        "points": NQ, "q_min_GeV": 0.0, "q_max_GeV": 0.6, "step_GeV": 0.00025
    }:
        raise ValueError("native manifest q grid mismatch")
    gate = manifest.get("comparison") or {}
    if gate.get("status") != "PASS" or gate.get("native_afh_validated") is not True or gate.get("rows_compared") != 16807:
        raise ValueError("the native seven-isotope/eight-response gate has not passed")
    if p3meta.get("source_file_sha256") != SOURCE_SHA256:
        raise ValueError("P3 AFH source SHA-256 is not the reviewed AFH v6.0 source")
    if native_meta.get("AFH_source_sha256") != SOURCE_SHA256 or native_spatial_meta.get("AFH_source_sha256") != SOURCE_SHA256:
        raise ValueError("native AFH source SHA-256 mismatch")
    if p3meta.get("source_file_sha256") != native_meta.get("AFH_source_sha256"):
        raise ValueError("P3/native AFH source SHA-256 mismatch")
    if manifest.get("native_spatial_multipoles", {}).get("rows") != EXPECTED_MULTIPOLE_ROWS:
        raise ValueError("native manifest spatial multipole row count mismatch")
    if int(native_spatial_meta.get("rows", "-1")) != EXPECTED_MULTIPOLE_ROWS:
        raise ValueError("native spatial multipole metadata row count mismatch")
    if native_spatial_meta.get("isotopes") != "129,131":
        raise ValueError("native spatial multipole isotope set mismatch")
    if native_spatial_meta.get("rank_map") != "129=1;131=1,2,3":
        raise ValueError("native spatial multipole rank map mismatch")
    if p3_validation.get("status") != "PASS_AFH_SPATIAL_MULTIPOLE_ARCHIVE":
        raise ValueError("P3 rank-resolved archive has not passed its integrity validator")

    response_path = p3_dir/p3meta["response_file"]
    multipole_path = p3_dir/p3meta["multipole_file"]
    native_spatial_csv = native_spatial_dir/"afh_v6_xe129_xe131_spatial_multipoles_native.csv"
    for path in (response_path, multipole_path, native_spatial_csv):
        if not path.is_file():
            raise FileNotFoundError(path)
    if sha256(response_path) != p3meta.get("response_file_sha256"):
        raise ValueError("P3 total-response CSV hash mismatch")
    if sha256(multipole_path) != p3meta.get("multipole_file_sha256"):
        raise ValueError("P3 multipole CSV hash mismatch")
    if sha256(native_spatial_csv) != manifest.get("native_spatial_multipoles", {}).get("csv_sha256"):
        raise ValueError("native spatial multipole CSV hash mismatch")
    if sha256(native_spatial_meta_path) != manifest.get("native_spatial_multipoles", {}).get("metadata_sha256"):
        raise ValueError("native spatial multipole metadata hash mismatch")

    p3_response = read_csv(response_path)
    p3_multipoles = read_csv(multipole_path)
    native_response = []
    for A in ISOTOPES:
        f = native_dir/f"afh_v6_xe{A}_eight_response_native.csv"
        if not f.is_file():
            raise FileNotFoundError(f)
        native_response.extend(read_csv(f))
    native_multipoles = read_csv(native_spatial_csv)

    total = compare_total_response_rows(p3_response, native_response)
    c0_by_A = {
        int(item["A"]): float(item["common_matrix_normalization"])
        for item in p3meta["isotope_metadata"]
    }
    if set(c0_by_A) != set(ISOTOPES):
        raise ValueError("P3 C0 metadata is incomplete")
    ranks = {int(A): tuple(int(x) for x in values)
             for A, values in p3meta["multipole_ranks_by_isotope"].items()}
    if ranks.get(129) != (1,) or ranks.get(131) != (1, 2, 3):
        raise ValueError("P3 isotope rank map does not match Xe-129/Xe-131")
    rankwise = compare_rankwise_multipole_rows(
        p3_multipoles, native_multipoles, c0_by_A
    )
    passed = total["passed"] and rankwise["passed"]
    return {
        "status": "PASS_NATIVE_AFH_SPATIAL_MULTIPOLE_CROSSCHECK" if passed else "FAIL",
        "scope": "native Wolfram AFH total responses plus rank-resolved DeltaJ/SigmaPJ amplitudes",
        "native_afh_validated": bool(passed),
        "native_source_commit": expected_source_commit,
        "native_wolfram_version": native_meta.get("wolfram_version"),
        "afh_source_sha256": SOURCE_SHA256,
        "native_control_run_id": manifest.get("control_run_id"),
        "native_control_run_attempt": manifest.get("control_run_attempt"),
        "total_response_comparison": total,
        "rank_resolved_multipole_comparison": rankwise,
        "C0_by_isotope": {str(A): c0_by_A[A] for A in ISOTOPES},
        "acceptance_note": (
            "PASS validates P3-B spatial response totals and signed rankwise "
            "AFH OBDME multipole amplitudes against native Wolfram AFH v6.0. "
            "It does not alone validate the complete three-body covariant "
            "many-body amplitude or a halo/detector rate."
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--p3-dir", type=Path, required=True)
    p.add_argument("--native-dir", type=Path, required=True)
    p.add_argument("--native-spatial-dir", type=Path, required=True)
    p.add_argument("--native-manifest", type=Path, required=True)
    p.add_argument("--expected-source-commit", required=True)
    p.add_argument("--out-json", type=Path, required=True)
    a = p.parse_args()
    result = run(
        a.p3_dir, a.native_dir, a.native_spatial_dir,
        a.native_manifest, a.expected_source_commit
    )
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS_NATIVE_AFH_SPATIAL_MULTIPOLE_CROSSCHECK":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
