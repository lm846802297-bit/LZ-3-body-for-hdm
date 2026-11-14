#!/usr/bin/env python3
"""Compare 5-keV and 1-keV Xe-131 AFH full dSigma/dER grids.

This is an ER-sampling convergence check, not a W2/z/phi* quadrature audit.
Both inputs must already have passed compare_full_dsigma_mathematica.py.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

BENCHMARKS = (
    "red_ms200_dm1",
    "green_ms300_dm1",
    "black_ms360_dm1",
    "blue_ms300_dm10",
)
REQUIRED = {
    "benchmark", "ER_keV", "phase_space_open", "R_A_physical_normalized",
    "C0", "I6_GeV2", "width_scheme", "W2_mapping", "g2", "nW", "nz",
    "nphi", "dsigma_dER_GeVminus3", "dsigma_without_factor4_GeVminus3",
    "dsigma_factor4_ratio", "dsigma_cm2_per_keV",
}
RESPONSE_WINDOWS = ((85.0, 120.0), (250.0, 290.0), (525.0, 565.0))


def rel(a: float, b: float) -> float:
    return abs(a - b) / max(abs(b), 1e-300)


def load_grid(path: Path, step_keV: int) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")
    if frame.duplicated(["benchmark", "ER_keV"]).any():
        raise ValueError(f"{path}: duplicate benchmark/ER rows")
    if set(frame["benchmark"].astype(str)) != set(BENCHMARKS):
        raise ValueError(f"{path}: benchmark set does not match the four fixed benchmarks")
    expected = np.arange(5.0, 800.0 + 0.5 * step_keV, float(step_keV))
    for name in BENCHMARKS:
        sub = frame.loc[frame["benchmark"].astype(str) == name].sort_values("ER_keV")
        got = sub["ER_keV"].to_numpy(dtype=float)
        if len(got) != len(expected) or not np.array_equal(got, expected):
            raise ValueError(
                f"{path}: {name} does not have the required {step_keV}-keV grid 5--800 keV"
            )
    frame["phase_space_open"] = pd.to_numeric(frame["phase_space_open"]).astype(int).astype(bool)
    numeric = [
        "ER_keV", "R_A_physical_normalized", "C0", "I6_GeV2",
        "g2", "nW", "nz", "nphi", "dsigma_dER_GeVminus3",
        "dsigma_without_factor4_GeVminus3", "dsigma_factor4_ratio",
        "dsigma_cm2_per_keV",
    ]
    for col in numeric:
        frame[col] = pd.to_numeric(frame[col], errors="raise")
        if not np.all(np.isfinite(frame[col].to_numpy(dtype=float))):
            raise ValueError(f"{path}: non-finite values in {col}")
    return frame.sort_values(["benchmark", "ER_keV"]).reset_index(drop=True)


def response_minimum(frame: pd.DataFrame, benchmark: str, window: tuple[float, float]):
    sub = frame.loc[
        (frame["benchmark"] == benchmark)
        & frame["ER_keV"].between(window[0], window[1])
    ]
    if sub.empty:
        raise ValueError(f"No response points in window {window} for {benchmark}")
    row = sub.loc[sub["R_A_physical_normalized"].idxmin()]
    return float(row["ER_keV"]), float(row["R_A_physical_normalized"])


def summarize_benchmark(coarse: pd.DataFrame, fine: pd.DataFrame, name: str):
    c = coarse.loc[coarse["benchmark"] == name].sort_values("ER_keV")
    f = fine.loc[fine["benchmark"] == name].sort_values("ER_keV")
    common = c.merge(
        f, on=["benchmark", "ER_keV"], suffixes=("_5keV", "_1keV"),
        validate="one_to_one",
    )
    if len(common) != len(c):
        raise ValueError(f"{name}: 1-keV grid does not contain every 5-keV node")

    mask_match = bool(np.array_equal(
        common["phase_space_open_5keV"].to_numpy(),
        common["phase_space_open_1keV"].to_numpy(),
    ))
    open_mask = common["phase_space_open_5keV"].to_numpy(dtype=bool)
    if not mask_match:
        raise AssertionError(f"{name}: phase-space masks differ at common ER nodes")

    max_i6 = max(
        (rel(float(a), float(b)) for a, b in zip(
            common.loc[open_mask, "I6_GeV2_5keV"],
            common.loc[open_mask, "I6_GeV2_1keV"],
        )),
        default=0.0,
    )
    max_dsigma = max(
        (rel(float(a), float(b)) for a, b in zip(
            common.loc[open_mask, "dsigma_dER_GeVminus3_5keV"],
            common.loc[open_mask, "dsigma_dER_GeVminus3_1keV"],
        )),
        default=0.0,
    )
    max_response = max(
        rel(float(a), float(b)) for a, b in zip(
            common["R_A_physical_normalized_5keV"],
            common["R_A_physical_normalized_1keV"],
        )
    )
    max_c0 = max(
        rel(float(a), float(b)) for a, b in zip(common["C0_5keV"], common["C0_1keV"])
    )

    for field in ("width_scheme", "W2_mapping", "g2", "nW", "nz", "nphi"):
        if not np.all(common[f"{field}_5keV"].astype(str).to_numpy()
                      == common[f"{field}_1keV"].astype(str).to_numpy()):
            raise AssertionError(f"{name}: calculation setting {field} differs between grids")
    if not np.all(common["width_scheme_5keV"].astype(str).to_numpy() == "pole"):
        raise AssertionError(f"{name}: expected pole-width prescription")
    if not np.all(common["W2_mapping_5keV"].astype(str).to_numpy() == "threshold_u2"):
        raise AssertionError(f"{name}: expected threshold_u2 mapping")
    if not np.all(common["nW_5keV"].to_numpy(dtype=int) == 16):
        raise AssertionError(f"{name}: expected nW=16")
    if not np.all(common["nz_5keV"].to_numpy(dtype=int) == 16):
        raise AssertionError(f"{name}: expected nz=16")
    if not np.all(common["nphi_5keV"].to_numpy(dtype=int) == 8):
        raise AssertionError(f"{name}: expected nphi=8")

    ratio5 = c.loc[c["phase_space_open"], "dsigma_factor4_ratio"].to_numpy(dtype=float)
    ratio1 = f.loc[f["phase_space_open"], "dsigma_factor4_ratio"].to_numpy(dtype=float)
    factor4_residual = max(
        float(np.max(np.abs(ratio5 - 4.0) / 4.0)) if len(ratio5) else 0.0,
        float(np.max(np.abs(ratio1 - 4.0) / 4.0)) if len(ratio1) else 0.0,
    )

    area5 = float(np.trapezoid(c["dsigma_cm2_per_keV"], c["ER_keV"]))
    area1 = float(np.trapezoid(f["dsigma_cm2_per_keV"], f["ER_keV"]))
    area_rel = rel(area5, area1)

    c_open = c.loc[c["phase_space_open"]]
    f_open = f.loc[f["phase_space_open"]]
    peak5 = c_open.loc[c_open["dsigma_cm2_per_keV"].idxmax()]
    peak1 = f_open.loc[f_open["dsigma_cm2_per_keV"].idxmax()]
    peak_height_rel = rel(
        float(peak5["dsigma_cm2_per_keV"]), float(peak1["dsigma_cm2_per_keV"])
    )
    peak_energy_shift = abs(float(peak5["ER_keV"]) - float(peak1["ER_keV"]))

    row = {
        "benchmark": name,
        "rows_5keV": int(len(c)),
        "rows_1keV": int(len(f)),
        "open_rows_5keV": int(c["phase_space_open"].sum()),
        "open_rows_1keV": int(f["phase_space_open"].sum()),
        "common_node_max_rel_I6": max_i6,
        "common_node_max_rel_dsigma": max_dsigma,
        "common_node_max_rel_response": max_response,
        "common_node_max_rel_C0": max_c0,
        "max_factor4_ratio_relative_residual": factor4_residual,
        "integral_5keV_cm2": area5,
        "integral_1keV_cm2": area1,
        "integral_relative_difference": area_rel,
        "peak_ER_5keV": float(peak5["ER_keV"]),
        "peak_ER_1keV": float(peak1["ER_keV"]),
        "peak_energy_shift_keV": peak_energy_shift,
        "peak_height_relative_difference": peak_height_rel,
    }
    for i, window in enumerate(RESPONSE_WINDOWS, start=1):
        e5, r5 = response_minimum(c, name, window)
        e1, r1 = response_minimum(f, name, window)
        row[f"response_min{i}_ER_5keV"] = e5
        row[f"response_min{i}_ER_1keV"] = e1
        row[f"response_min{i}_shift_keV"] = abs(e5 - e1)
        row[f"response_min{i}_R_over_A2_1keV"] = r1 / (131.0 ** 2)

    row["status"] = (
        "PASS"
        if mask_match
        and max_i6 <= 2e-7
        and max_dsigma <= 2e-7
        and max_response <= 2e-10
        and max_c0 <= 2e-12
        and factor4_residual <= 2e-12
        and area_rel <= 1e-3
        and peak_height_rel <= 5e-3
        else "FAIL"
    )
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--five-kev-csv", type=Path, required=True)
    parser.add_argument("--one-kev-csv", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    coarse = load_grid(args.five_kev_csv, 5)
    fine = load_grid(args.one_kev_csv, 1)
    rows = [summarize_benchmark(coarse, fine, name) for name in BENCHMARKS]
    summary = {
        "status": "PASS" if all(r["status"] == "PASS" for r in rows) else "FAIL",
        "scope": "fixed-speed Xe-131 AFH full dSigma/dER; no halo or detector fold",
        "coarse_grid_keV": "5 to 800 in 5-keV steps",
        "fine_grid_keV": "5 to 800 in 1-keV steps",
        "fixed_quadrature": "16x16x8 (W2,z,phi*)",
        "W2_mapping": "threshold_u2",
        "width_scheme": "pole",
        "acceptance": {
            "common_node_I6_and_dsigma_relative": 2e-7,
            "PCHIP_response_relative": 2e-10,
            "C0_and_factor4_relative": 2e-12,
            "integrated_dsigma_area_relative": 1e-3,
            "peak_height_relative": 5e-3,
        },
        "benchmarks": rows,
        "interpretation": (
            "Common-node comparisons check grid-independent reproducibility; "
            "the integrated area and peak-height comparisons assess recoil-grid sampling. "
            "Response-minimum and peak positions are reported as diagnostics."
        ),
    }
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output_csv, index=False, float_format="%.14g")
    args.output_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
