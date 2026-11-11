#!/usr/bin/env python3
"""Compare coarse and high-order Xe-131 joint Eq. (6) diagnostics."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--results-dir", type=Path, default=ROOT / "results" / "joint_xe131")
ARGS = parser.parse_args()
RESULTS = ARGS.results_dir


def read_rows(path: Path) -> dict[float, dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return {float(row["ER_keV"]): row for row in csv.DictReader(handle)}


def main() -> None:
    coarse_gcn = read_rows(RESULTS / "coarse" / "xe131_gcn_joint_single_speed.csv")
    fine_gcn = read_rows(RESULTS / "fine" / "xe131_gcn_joint_single_speed.csv")
    fine_jj55 = read_rows(RESULTS / "fine" / "xe131_jj55_joint_single_speed.csv")

    rows = []
    for ER in sorted(coarse_gcn):
        c = coarse_gcn[ER]
        f = fine_gcn[ER]
        j = fine_jj55[ER]
        Ic = float(c["I6_GeV2"])
        If = float(f["I6_GeV2"])
        Ij = float(j["I6_GeV2"])
        if not math.isclose(If, Ij, rel_tol=2e-13, abs_tol=1e-10):
            raise ArithmeticError(f"GCN/JJ55 three-body kernel mismatch at ER={ER} keV")
        rel = (If / Ic - 1.0) if Ic > 0.0 else 0.0
        if Ic > 0.0 and abs(rel) > 5.0e-5:
            raise ArithmeticError(
                f"Eq. (6) quadrature not converged at ER={ER} keV: rel={rel:.4g}"
            )
        rows.append({
            "ER_keV": ER,
            "phase_space_open": f["phase_space_open"],
            "I6_coarse_16_16_8_GeV2": Ic,
            "I6_fine_40_32_20_GeV2": If,
            "relative_fine_minus_coarse": rel,
            "R_A_GCN": float(f["R_A"]),
            "R_A_JJ55": float(j["R_A"]),
            "C_A_GCN_GeV": float(f["C_A_GeV"]),
            "C_A_JJ55_GeV": float(j["C_A_GeV"]),
            "chi2_pole_gap_keV": float(f["chi2_pole_gap_keV"]),
        })

    out = RESULTS / "quadrature_convergence.csv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Xe-131 joint-kernel quadrature convergence",
        "",
        "The comparison uses the same AFH response data and physical inputs.",
        "Only the Eq. (6) quadrature order changes: coarse (16,16,8), fine (40,32,20).",
        "The response model does not enter I6; GCN and JJ55 must therefore share I6.",
        "",
        "| ER [keV] | phase space | I6 coarse [GeV²] | I6 fine [GeV²] | fine/coarse - 1 |",
        "|---:|:---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['ER_keV']:.0f} | {row['phase_space_open']} | "
            f"{row['I6_coarse_16_16_8_GeV2']:.8g} | "
            f"{row['I6_fine_40_32_20_GeV2']:.8g} | "
            f"{row['relative_fine_minus_coarse']:.3e} |"
        )
    lines.extend([
        "",
        "Acceptance: all open-channel points must agree within 5e-5 relative; "
        "GCN/JJ55 must give the same I6 to numerical precision.",
        "",
        "This is a fixed-speed differential-cross-section diagnostic, not a halo-folded event rate.",
    ])
    (RESULTS / "CONVERGENCE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out.read_text(encoding="utf-8"))
    print((RESULTS / "CONVERGENCE.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
