#!/usr/bin/env python3
"""Shared, provenance-checked overlay for the 121-point native Xe-131 AFH dip grid."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def overlay_dense_native_charge_grid(
    native: dict, native_provenance: dict, dense_csv: Path,
    dense_metadata: Path, dense_validation: Path,
) -> tuple[dict, dict]:
    """Replace the coarse Xe-131 charge grid locally with the validated 121-point native grid.

    Dense AFH columns are raw isoscalar package W responses. Convert them using
    the same 4*pi/(2J+1), equal-p/n factor four, and C0 convention as the
    canonical native archive; never apply the factor four twice.
    """
    meta = {}
    for line in dense_metadata.read_text(encoding="utf-8-sig").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            meta[key.strip()] = value.strip()
    validation = json.loads(dense_validation.read_text(encoding="utf-8-sig"))
    expected_meta = {
        "source": "AFH DMFormFactor v6.0 native Wolfram execution",
        "isotope": "Xe-131",
        "Z": "54",
        "response_map": "M=1;PhiPP=4;MPhiPP=7",
        "q_grid": "121 uniform nodes from 0.2545 to 0.2575 GeV, step 0.000025 GeV",
        "normalization": "raw AFH package response; no physical equal-p/n factor-four rescaling",
        "AFH_source_sha256": "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372",
        "rows": "121",
    }
    for key, value in expected_meta.items():
        if meta.get(key) != value:
            raise ValueError(f"dense native AFH metadata mismatch for {key}")
    if validation.get("status") != "PASS_NATIVE_XE131_DENSE_CHARGE_DIP":
        raise ValueError("dense native AFH validation JSON is not PASS")
    if validation.get("rows") != 121 or validation.get("common_nodes_compared") != 13:
        raise ValueError("dense native AFH validation has wrong grid/overlap counts")
    if float(validation.get("max_imaginary_residual", math.inf)) > 2.0e-12:
        raise ValueError("dense native AFH imaginary residual exceeds tolerance")
    if validation.get("AFH_source_sha256") != meta["AFH_source_sha256"]:
        raise ValueError("dense native AFH source hash mismatch")
    if validation.get("dense_csv_sha256") != hashlib.sha256(dense_csv.read_bytes()).hexdigest():
        raise ValueError("dense native AFH CSV SHA-256 mismatch")
    if validation.get("dense_metadata_sha256") != hashlib.sha256(dense_metadata.read_bytes()).hexdigest():
        raise ValueError("dense native AFH metadata SHA-256 mismatch")

    with dense_csv.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 121:
        raise ValueError(f"expected 121 dense native AFH rows, got {len(rows)}")
    q_dense = np.asarray([float(row["q_GeV"]) for row in rows], dtype=float)
    q_expected = 0.2545 + np.arange(121, dtype=float) * 0.000025
    if not np.allclose(q_dense, q_expected, rtol=0.0, atol=2.0e-12):
        raise ValueError("dense native AFH q grid does not match its declared 121 nodes")
    if np.max(np.abs(np.asarray([
        float(row["Im_W_M00_AFH"]) for row in rows
    ] + [
        float(row["Im_W_PhiPP00_AFH"]) for row in rows
    ] + [
        float(row["Im_W_MPhiPP00_AFH"]) for row in rows
    ]))) > 2.0e-12:
        raise ValueError("dense native AFH CSV contains a non-negligible imaginary response")

    C0 = float(native_provenance["common_matrix_normalization_C0"])
    response_factor = 4.0 * math.pi / (2.0 * 1.5 + 1.0) * 4.0 * C0
    dense_values = {
        "M": response_factor * np.asarray([float(row["W_M00_AFH"]) for row in rows]),
        "PhiPP": response_factor * np.asarray([float(row["W_PhiPP00_AFH"]) for row in rows]),
        "MPhiPP": response_factor * np.asarray([float(row["W_MPhiPP00_AFH"]) for row in rows]),
    }
    if np.min(dense_values["M"]) < 0.0 or np.min(dense_values["PhiPP"]) < 0.0:
        raise ValueError("dense native AFH diagonal charge response is negative")
    bound = np.sqrt(dense_values["M"] * dense_values["PhiPP"])
    if np.any(np.abs(dense_values["MPhiPP"]) > bound + 2.0e-10 * np.maximum(bound, 1.0e-300)):
        raise ValueError("dense native AFH M-PhiPP violates Cauchy-Schwarz")

    q_coarse = np.asarray(native["q"], dtype=float)
    if len(q_coarse) != 2401:
        raise ValueError("canonical native Xe-131 coarse grid must contain 2401 points")
    keep_left = q_coarse < q_dense[0] - 1.0e-12
    keep_right = q_coarse > q_dense[-1] + 1.0e-12
    q_merged = np.concatenate((q_coarse[keep_left], q_dense, q_coarse[keep_right]))
    if np.any(np.diff(q_merged) <= 0.0):
        raise ValueError("merged native/dense Xe-131 q grid is not strictly increasing")
    merged = {}
    for name in ("M", "PhiPP", "MPhiPP"):
        coarse_values = np.asarray(native["responses"][name], dtype=float)
        merged[name] = np.concatenate((
            coarse_values[keep_left], dense_values[name], coarse_values[keep_right]
        ))
    native = {"q": q_merged, "responses": merged}
    native_provenance = {
        **native_provenance,
        "dense_native_overlay": True,
        "dense_native_csv_sha256": hashlib.sha256(dense_csv.read_bytes()).hexdigest(),
        "dense_native_metadata_sha256": hashlib.sha256(dense_metadata.read_bytes()).hexdigest(),
        "dense_native_validation_sha256": hashlib.sha256(dense_validation.read_bytes()).hexdigest(),
        "dense_native_validation_status": validation["status"],
        "dense_native_points": len(q_dense),
        "dense_native_q_min_GeV": float(q_dense[0]),
        "dense_native_q_max_GeV": float(q_dense[-1]),
        "dense_native_q_step_GeV": 0.000025,
        "dense_native_common_nodes_compared": validation["common_nodes_compared"],
        "dense_native_common_node_max_relative_difference": validation["common_node_max_relative_difference"],
        "dense_native_normalization": "raw AFH W converted to physical equal-p/n R with 4*4pi/(2J+1), then same C0 applied once",
        "merged_response_grid_points": len(q_merged),
    }
    return native, native_provenance
