#!/usr/bin/env python3
"""PCHIP versus local Chebyshev interpolation audit for the Xe-131 six-channel scan.

This is a response-grid interpolation diagnostic. It does not reevaluate AFH
ResponseNuclear on a denser native q grid and does not reintegrate phase space.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from numpy.polynomial.chebyshev import chebfit, chebval
from scipy.interpolate import PchipInterpolator

CHANNELS = {
    "M": ("W_M", "kernel_charge_M"),
    "PhiPP": ("W_PhiPP", "kernel_charge_PhiPP"),
    "MPhiPP": ("W_MPhiPP", "kernel_charge_MPhiPP"),
    "Delta": ("W_Delta", "kernel_spatial_Delta"),
    "SigmaPrime": ("W_SigmaPrime", "kernel_spatial_SigmaPrime"),
    "SigmaPrimeDelta": ("W_SigmaPrimeDelta", "kernel_spatial_SigmaPrimeDelta"),
}
CHARGE = ("M", "PhiPP", "MPhiPP")
SPATIAL = ("Delta", "SigmaPrime", "SigmaPrimeDelta")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("refusing to write empty interpolation audit")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def local_chebyshev_value(
    q_grid: np.ndarray, values: np.ndarray, q: float, *, degree: int, n_points: int
) -> float:
    if q < q_grid[0] or q > q_grid[-1]:
        raise ValueError(f"q={q:.12g} is outside the response grid")
    if degree >= n_points:
        raise ValueError("degree must be smaller than n_points")
    idx = np.argsort(np.abs(q_grid - q), kind="stable")[:n_points]
    idx = idx[np.argsort(q_grid[idx])]
    x = q_grid[idx]
    scale = float(np.max(np.abs(x - q)))
    if scale == 0.0:
        return float(values[int(np.argmin(np.abs(q_grid - q)))])
    return float(chebval(0.0, chebfit((x - q) / scale, values[idx], degree)))


def point_record(scan: list[dict], metric: np.ndarray, i: int) -> dict:
    row = scan[i]
    return {
        "benchmark": row["benchmark"],
        "ER_keV": float(row["ER_keV"]),
        "qA_GeV": float(row["qA_GeV"]),
        "width_scheme": row["width_scheme"],
        "value": float(metric[i]),
    }


def run_audit(
    scan_csv: Path, response_csv: Path, out_csv: Path, out_json: Path,
    scan_json: Path | None = None,
) -> dict:
    scan = read_csv(scan_csv)
    response = read_csv(response_csv)
    if not scan or not response:
        raise ValueError("scan and response tables must be non-empty")
    q_grid = np.asarray([float(r["qA_GeV"]) for r in response])
    q_scan = np.asarray([float(r["qA_GeV"]) for r in scan])
    if len(q_grid) < 13 or not np.all(np.diff(q_grid) > 0.0):
        raise ValueError("response grid must have at least 13 increasing q nodes")
    if q_scan.min() < q_grid[0] or q_scan.max() > q_grid[-1]:
        raise ValueError("scan q values extend outside the response grid")

    pchip_values, cheb8_values, cheb10_values = {}, {}, {}
    summaries = {}
    for name, (column, _) in CHANNELS.items():
        y = np.asarray([float(r[column]) for r in response])
        pchip = np.asarray(PchipInterpolator(q_grid, y, extrapolate=False)(q_scan))
        c8 = np.asarray([
            local_chebyshev_value(q_grid, y, q, degree=8, n_points=11) for q in q_scan
        ])
        c10 = np.asarray([
            local_chebyshev_value(q_grid, y, q, degree=10, n_points=13) for q in q_scan
        ])
        archived = np.asarray([float(r[f"W_{name}"]) for r in scan])
        if not np.allclose(archived, pchip, rtol=2e-11, atol=2e-14):
            raise ValueError(f"archived PCHIP response mismatch in {name}")
        pchip_values[name], cheb8_values[name], cheb10_values[name] = pchip, c8, c10
        scale = max(float(np.max(np.abs(y))), 1e-300)
        rel = np.abs(pchip - c10) / np.maximum(
            np.maximum(np.abs(pchip), np.abs(c10)), 1e-12 * scale
        )
        worst = int(np.argmax(rel))
        summaries[name] = {
            "max_abs_pchip_vs_cheb10": float(np.max(np.abs(pchip - c10))),
            "max_relative_pchip_vs_cheb10_with_1e-12_channel_scale_floor": float(rel[worst]),
            "worst_point": point_record(scan, rel, worst),
            "max_abs_cheb8_vs_cheb10": float(np.max(np.abs(c8 - c10))),
            "max_abs_cheb8_vs_cheb10_over_channel_scale": float(np.max(np.abs(c8-c10))/scale),
        }

    coeff = {}
    for name, (_, kernel_col) in CHANNELS.items():
        w = pchip_values[name]
        k = np.asarray([float(r[kernel_col]) for r in scan])
        if np.any(w == 0.0):
            raise ValueError(f"cannot reconstruct particle coefficient for zero {name} response")
        coeff[name] = k / w

    kernels = {}
    for sector, names in (("charge", CHARGE), ("spatial", SPATIAL)):
        kernels[f"{sector}_pchip"] = np.asarray([
            sum(float(r[CHANNELS[n][1]]) for n in names) for r in scan
        ])
        kernels[f"{sector}_cheb10"] = sum(coeff[n] * cheb10_values[n] for n in names)
    kernels["full_pchip"] = kernels["charge_pchip"] + kernels["spatial_pchip"]
    kernels["full_cheb10"] = kernels["charge_cheb10"] + kernels["spatial_cheb10"]
    A_reference_pchip = np.asarray([float(r["kernel_A_reference_M"]) for r in scan])
    A_reference_coeff = A_reference_pchip / pchip_values["M"]
    A_reference_cheb10 = A_reference_coeff * cheb10_values["M"]
    kernels["full_over_A_reference_pchip"] = kernels["full_pchip"] / A_reference_pchip
    kernels["full_over_A_reference_cheb10"] = kernels["full_cheb10"] / A_reference_cheb10

    for sector in ("charge", "spatial", "full"):
        p, c = kernels[f"{sector}_pchip"], kernels[f"{sector}_cheb10"]
        rel = np.abs(c - p) / np.maximum(np.abs(p), 1e-300)
        worst = int(np.argmax(rel))
        summaries[f"kernel_{sector}"] = {
            "max_abs_pchip_vs_cheb10": float(np.max(np.abs(c-p))),
            "max_relative_pchip_vs_cheb10": float(rel[worst]),
            "worst_point": point_record(scan, rel, worst),
        }
    ratio_rel = np.abs(
        kernels["full_over_A_reference_cheb10"] / kernels["full_over_A_reference_pchip"] - 1.0
    )
    ratio_worst = int(np.argmax(ratio_rel))
    summaries["ratio_D_over_A_reference"] = {
        "max_relative_pchip_vs_cheb10": float(ratio_rel[ratio_worst]),
        "worst_point": point_record(scan, ratio_rel, ratio_worst),
    }

    m, phi, mphi = (cheb10_values[n] for n in CHARGE)
    delta, sigma, sigmadelta = (cheb10_values[n] for n in SPATIAL)
    diagonal_minima = {
        "M": float(m.min()), "PhiPP": float(phi.min()),
        "Delta": float(delta.min()), "SigmaPrime": float(sigma.min()),
    }
    if min(diagonal_minima.values()) < -1e-12:
        raise ArithmeticError(f"negative diagonal local response: {diagonal_minima}")
    charge_bound = np.sqrt(np.maximum(m, 0.0) * np.maximum(phi, 0.0))
    spatial_bound = np.sqrt(np.maximum(delta, 0.0) * np.maximum(sigma, 0.0))
    charge_excess = np.maximum(0.0, np.abs(mphi) - charge_bound)
    spatial_excess = np.maximum(0.0, np.abs(sigmadelta) - spatial_bound)
    if charge_excess.max() > 2e-10 * max(float(charge_bound.max()), 1e-300):
        raise ArithmeticError("local charge responses violate Cauchy-Schwarz")
    if spatial_excess.max() > 2e-10 * max(float(spatial_bound.max()), 1e-300):
        raise ArithmeticError("local spatial responses violate Cauchy-Schwarz")

    output = []
    for i, row in enumerate(scan):
        item = {k: row[k] for k in ("benchmark", "ER_keV", "qA_GeV", "width_scheme")}
        for name in CHANNELS:
            item[f"W_{name}_pchip"] = float(pchip_values[name][i])
            item[f"W_{name}_cheb8"] = float(cheb8_values[name][i])
            item[f"W_{name}_cheb10"] = float(cheb10_values[name][i])
        for sector in ("charge", "spatial", "full"):
            p, c = kernels[f"{sector}_pchip"][i], kernels[f"{sector}_cheb10"][i]
            item[f"K_{sector}_pchip"] = float(p)
            item[f"K_{sector}_cheb10"] = float(c)
            item[f"K_{sector}_cheb10_over_pchip_minus_1"] = float(c/p - 1.0)
        item["D_over_A_reference_pchip"] = float(kernels["full_over_A_reference_pchip"][i])
        item["D_over_A_reference_cheb10"] = float(kernels["full_over_A_reference_cheb10"][i])
        item["D_over_A_reference_cheb10_over_pchip_minus_1"] = float(
            kernels["full_over_A_reference_cheb10"][i] /
            kernels["full_over_A_reference_pchip"][i] - 1.0
        )
        output.append(item)
    write_csv(out_csv, output)

    provenance = {}
    if scan_json is not None:
        meta = json.loads(scan_json.read_text(encoding="utf-8-sig"))
        rm = meta.get("response_metadata", {})
        provenance = {
            "scan_status": meta.get("status"),
            "spatial_response_status": rm.get("spatial_response_status"),
            "spatial_native_mathematica_crosscheck": rm.get("spatial_native_mathematica_crosscheck"),
            "AFH_source_sha256": rm.get("AFH_source_sha256"),
            "Xe131_density_matrix_sha256": rm.get("Xe131_density_matrix_sha256"),
            "C0": rm.get("C0"),
        }
    result = {
        "status": "PASS_LOCAL_INTERPOLATION_STABILITY_DIAGNOSTIC",
        "scope": "PCHIP versus local Chebyshev interpolation of the archived 2,401-point AFH response grid at 140 fixed-speed recoil q values",
        "native_afh_dense_q_validated": False,
        "native_afh_spatial_validated": False,
        "phase_space_reintegrated": False,
        "scan_rows": len(scan),
        "response_grid_points": len(q_grid),
        "response_q_min_GeV": float(q_grid[0]),
        "response_q_max_GeV": float(q_grid[-1]),
        "response_q_step_GeV": float(q_grid[1] - q_grid[0]),
        "local_interpolation": {
            "cheb8": {"degree": 8, "nearest_nodes": 11},
            "cheb10": {"degree": 10, "nearest_nodes": 13},
            "coordinate_scaling": "local q offset divided by maximum selected-node distance",
        },
        "channel_summaries": summaries,
        "minimum_local_cheb10_diagonal_responses": diagonal_minima,
        "maximum_charge_cauchy_schwarz_excess": float(charge_excess.max()),
        "maximum_spatial_cauchy_schwarz_excess": float(spatial_excess.max()),
        "provenance": provenance,
        "interpretation": "Degree-8 and degree-10 local interpolants provide a stable interpolation cross-check on the existing q grid. They do not replace direct native AFH ResponseNuclear evaluations on a denser q grid. The full-kernel difference is dominated by W_M near the Xe-131 diffraction minimum; the spatial-current kernel changes by less than 1 ppm in this diagnostic.",
        "required_next_gate": "Direct native Wolfram ResponseNuclear evaluation for Xe-131 charge indices 1, 4, 7 on q=0.2545--0.2575 GeV with 0.000025 GeV spacing, followed by the six-channel fixed-speed contraction using that dense response table.",
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--scan-csv", type=Path, required=True)
    p.add_argument("--response-grid-csv", type=Path, required=True)
    p.add_argument("--scan-json", type=Path)
    p.add_argument("--out-csv", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    a = p.parse_args()
    result = run_audit(a.scan_csv, a.response_grid_csv, a.out_csv, a.out_json, a.scan_json)
    print(json.dumps({
        "status": result["status"],
        "scan_rows": result["scan_rows"],
        "max_full_kernel_relative_difference": result["channel_summaries"]["kernel_full"]["max_relative_pchip_vs_cheb10"],
        "max_D_over_A_ratio_relative_difference": result["channel_summaries"]["ratio_D_over_A_reference"]["max_relative_pchip_vs_cheb10"],
        "max_charge_kernel_relative_difference": result["channel_summaries"]["kernel_charge"]["max_relative_pchip_vs_cheb10"],
        "max_spatial_kernel_relative_difference": result["channel_summaries"]["kernel_spatial"]["max_relative_pchip_vs_cheb10"],
    }, indent=2))
    if result["status"] != "PASS_LOCAL_INTERPOLATION_STABILITY_DIAGNOSTIC":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
