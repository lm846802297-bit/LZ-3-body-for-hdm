#!/usr/bin/env python3
"""Reproduce AFH seven-isotope charge-response equivalence diagnostics."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "research" / "afh_default_density_natural_xenon_halo"
RESPONSE_DIR = STUDY / "results" / "full_afh_v6_default_7_isotope_response"
COMPARISON_FILE = (
    STUDY / "results" / "afh7_hybrid9_continuous_2026-11-14"
    / "afh_hybrid9_response_model_comparison.csv"
)
ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
NATURAL_FRACTIONS = {
    128: 0.019102, 129: 0.264006, 130: 0.040710,
    131: 0.212324, 132: 0.269086, 134: 0.104357, 136: 0.088573,
}
SELECTED_ER_KEV = (5, 10, 50, 100, 150, 200, 250, 300, 400, 500, 600, 800)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_response_grids() -> dict[int, list[dict[str, str]]]:
    grids = {}
    for isotope in ISOTOPES:
        path = RESPONSE_DIR / f"afh_default_xe{isotope}_response_2401.csv"
        rows = read_csv(path)
        if len(rows) != 2401:
            raise ValueError(f"Xe-{isotope}: expected 2401 nodes, got {len(rows)}")
        grids[isotope] = rows
    return grids


def zero_momentum_rows(grids: dict[int, list[dict[str, str]]]) -> list[dict]:
    result = []
    for isotope, rows in grids.items():
        row = rows[0]
        A = int(row["A"])
        raw = float(row["R_AFH_package_4pi_over_2Jplus1"])
        expected = A * A / 4.0
        physical = float(row["R_equal_pn_normalized"])
        result.append({
            "A": A, "isotope": f"Xe-{A}", "J_A": float(row["J_A"]),
            "raw_AFH_R0": f"{raw:.15g}",
            "expected_A2_over_4": f"{expected:.15g}",
            "raw_relative_error": f"{raw / expected - 1.0:.12g}",
            "raw_error_ppm": f"{(raw / expected - 1.0) * 1e6:.8f}",
            "physical_R0": f"{physical:.15g}", "expected_A2": A * A,
            "physical_relative_error": f"{physical / (A * A) - 1.0:.12g}",
        })
    return result


def multipole_reconstruction_rows(
    grids: dict[int, list[dict[str, str]]]
) -> list[dict]:
    result = []
    for isotope, rows in grids.items():
        max_rel = 0.0
        max_abs = 0.0
        max_q = 0.0
        for row in rows:
            J = float(row["J_A"])
            a0 = float(row["rank0_amplitude"])
            a2 = float(row["rank2_amplitude"])
            norm = float(row["A0_normalization_factor"])
            rebuilt = norm * (4.0 * math.pi / (2.0 * J + 1.0)) * (a0*a0 + a2*a2)
            stored = float(row["R_equal_pn_normalized"])
            absolute = abs(rebuilt - stored)
            relative = absolute / max(abs(stored), 1e-300)
            if relative > max_rel:
                max_rel, max_q = relative, float(row["q_GeV"])
            max_abs = max(max_abs, absolute)
        result.append({
            "A": isotope, "points": len(rows),
            "max_relative_reconstruction_residual": f"{max_rel:.12g}",
            "max_absolute_reconstruction_residual": f"{max_abs:.12g}",
            "q_at_max_relative_residual_GeV": f"{max_q:.8g}",
            "status": "PASS" if max_rel < 1e-12 else "FAIL",
        })
    return result


def first_local_minima_rows(
    grids: dict[int, list[dict[str, str]]],
    q_min: float = 0.080,
    q_max: float = 0.220,
) -> list[dict]:
    result = []
    for isotope, rows in grids.items():
        found = None
        for i in range(1, len(rows) - 1):
            q = float(rows[i]["q_GeV"])
            if not q_min <= q <= q_max:
                continue
            value = float(rows[i]["R_over_A2"])
            if (value <= float(rows[i-1]["R_over_A2"])
                    and value <= float(rows[i+1]["R_over_A2"])):
                found = rows[i]
                break
        if found is None:
            raise ValueError(f"no local minimum found for Xe-{isotope}")
        result.append({
            "A": isotope, "q_min_GeV": found["q_GeV"],
            "F2_min_grid": found["R_over_A2"],
            "ER_keV": found["ER_keV"],
            "definition": "first grid-local minimum in 0.080 <= q/GeV <= 0.220",
        })
    return result


def xe131_rank2_rows(grids: dict[int, list[dict[str, str]]]) -> list[dict]:
    result = []
    for row in grids[131]:
        a0 = float(row["rank0_amplitude"])
        a2 = float(row["rank2_amplitude"])
        denominator = a0*a0 + a2*a2
        fraction = a2*a2 / denominator if denominator else 0.0
        result.append({
            "q_GeV": row["q_GeV"], "ER_keV": row["ER_keV"],
            "F2_total": row["R_over_A2"],
            "rank2_fraction_of_M_response": f"{fraction:.12g}",
        })
    return result


def selected_shape_rows() -> list[dict]:
    rows = read_csv(COMPARISON_FILE)
    result = []
    for energy in SELECTED_ER_KEV:
        selected = {
            int(row["A"]): row for row in rows
            if abs(float(row["ER_keV"]) - energy) < 1e-9
            and int(row["A"]) in ISOTOPES
        }
        if set(selected) != set(ISOTOPES):
            raise ValueError(f"ER={energy} keV: incomplete seven-isotope row set")
        values = {A: float(selected[A]["R_AFH_over_A2"]) for A in ISOTOPES}
        minimum_A = min(ISOTOPES, key=lambda A: values[A])
        maximum_A = max(ISOTOPES, key=lambda A: values[A])
        xe131 = values[131]
        denom = sum(NATURAL_FRACTIONS[A] * A*A for A in ISOTOPES)
        weighted = sum(
            NATURAL_FRACTIONS[A] * A*A * values[A] for A in ISOTOPES
        ) / denom
        out = {
            "ER_keV": energy,
            "AFH7_A2_weighted_F2": f"{weighted:.12g}",
            "Xe131_F2": f"{xe131:.12g}",
            "AFH7_vs_Xe131_relative_difference": f"{weighted / xe131 - 1.0:.12g}",
            "minimum_isotope": f"Xe-{minimum_A}",
            "minimum_F2": f"{values[minimum_A]:.12g}",
            "maximum_isotope": f"Xe-{maximum_A}",
            "maximum_F2": f"{values[maximum_A]:.12g}",
            "max_over_min_minus_one": f"{values[maximum_A] / values[minimum_A] - 1.0:.12g}",
        }
        for A in ISOTOPES:
            out[f"Xe{A}_F2"] = f"{values[A]:.12g}"
        result.append(out)
    return result


def main() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path(__file__).resolve().parent / "results",
    )
    args = parser.parse_args()
    grids = load_response_grids()
    q0 = zero_momentum_rows(grids)
    reconstruction = multipole_reconstruction_rows(grids)
    minima = first_local_minima_rows(grids)
    rank2 = xe131_rank2_rows(grids)
    shapes = selected_shape_rows()
    outputs = {
        "zero_momentum_normalization.csv": q0,
        "multipole_reconstruction.csv": reconstruction,
        "selected_recoil_shape_comparison.csv": shapes,
        "first_local_minima_grid.csv": minima,
        "xe131_rank2_fraction.csv": rank2,
    }
    for filename, data in outputs.items():
        write_csv(args.outdir / filename, data)
    summary = {
        "status": "PASS" if all(r["status"] == "PASS" for r in reconstruction) else "FAIL",
        "isotopes": list(ISOTOPES),
        "response_grid_points": sum(len(v) for v in grids.values()),
        "natural_atom_fraction_covered": sum(NATURAL_FRACTIONS.values()),
        "zero_momentum_max_abs_raw_error_ppm": max(abs(float(r["raw_error_ppm"])) for r in q0),
        "multipole_reconstruction_max_relative_residual": max(
            float(r["max_relative_reconstruction_residual"]) for r in reconstruction
        ),
        "first_minimum_search_interval_GeV": [0.080, 0.220],
        "outputs": list(outputs),
        "scope": "nuclear-response audit only; no new three-body or detector calculation",
    }
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    main()
