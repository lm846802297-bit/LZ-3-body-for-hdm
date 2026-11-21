#!/usr/bin/env python3
"""Charge-sector M + Phi'' matching for the Xe-131 AFH response grid.

The default F1/F2 inputs are zero-momentum anchors only. The output is a
controlled diagnostic until finite-t flavour-separated form factors are
provided. The script evaluates the charge-current sector; it does not claim
to include spatial-current Sigma/Delta responses.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

M_N_GEV_DEFAULT = 0.938918
F1_ZERO_DEFAULT = 3.0
F2_ZERO_DEFAULT = -0.552


def charge_coefficients(
    q_gev: float,
    *,
    f1: float = F1_ZERO_DEFAULT,
    f2: float = F2_ZERO_DEFAULT,
    m_n: float = M_N_GEV_DEFAULT,
) -> tuple[float, float]:
    """Return AFH M and Phi'' charge coefficients.

    Conventions:
      q_N = p_N' - p_N is the one-nucleon current transfer;
      in the static one-body impulse approximation, q_N^0=0 and
      q_N spatial = q_A spatial;
      t_N^static = -|q_A|^2, whereas the nuclear four-transfer is
      t_A = -|q_A|^2 + E_R^2.

    The coefficients follow the nonrelativistically normalized vector-charge
    expansion in Hoferichter, Menendez & Schwenk, PRD 102, 074018 (2020),
    Eq. (41), mapped to the AFH Phi'' operator definition, Anand et al.,
    PRC 89, 065501 (2014), Eq. (51).
    """
    if q_gev < 0 or m_n <= 0:
        raise ValueError("q must be nonnegative and m_n must be positive")
    t_n_static = -(q_gev * q_gev)
    f1_plus_2f2 = f1 + 2.0 * f2
    c_m = f1 + f1_plus_2f2 * t_n_static / (8.0 * m_n * m_n)
    c_phi = f1_plus_2f2 * q_gev * q_gev / (4.0 * m_n * m_n)
    return c_m, c_phi


def matched_charge_response(
    q_gev: float,
    w_m: float,
    w_phi: float,
    w_mphi: float,
    *,
    f1: float = F1_ZERO_DEFAULT,
    f2: float = F2_ZERO_DEFAULT,
    m_n: float = M_N_GEV_DEFAULT,
) -> dict[str, float]:
    """Combine AFH M, Phi'', and M-Phi'' responses at one momentum."""
    if min(w_m, w_phi) < -1.0e-13:
        raise ValueError("diagonal AFH responses must be nonnegative")
    c_m, c_phi = charge_coefficients(q_gev, f1=f1, f2=f2, m_n=m_n)
    scale = max(abs(w_m * w_phi), abs(w_mphi * w_mphi), 1.0e-300)
    cs_margin = w_m * w_phi - w_mphi * w_mphi
    if cs_margin < -2.0e-9 * scale:
        raise ValueError(
            f"Cauchy-Schwarz violation: W_M W_Phi - W_MPhi^2={cs_margin}"
        )

    m_piece = c_m * c_m * w_m
    interference_piece = 2.0 * c_m * c_phi * w_mphi
    phi_piece = c_phi * c_phi * w_phi
    matched = m_piece + interference_piece + phi_piece
    tolerance = 2.0e-10 * max(abs(m_piece), abs(interference_piece),
                              abs(phi_piece), 1.0e-300)
    if matched < -tolerance:
        raise ValueError(f"negative matched response: {matched}")

    eta = c_phi / c_m if c_m else math.nan
    q_phi_over_m = matched / m_piece if m_piece else math.nan
    leading_point_charge = f1 * f1 * w_m
    q_total_over_leading = (
        matched / leading_point_charge if leading_point_charge else math.nan
    )
    return {
        "c_M": c_m,
        "c_PhiPP": c_phi,
        "eta_Phi_over_M": eta,
        "M_piece": m_piece,
        "M_Phi_interference_piece": interference_piece,
        "PhiPP_squared_piece": phi_piece,
        "matched_charge_response": matched,
        "Q_Phi_over_Monly": q_phi_over_m,
        "delta_Phi_over_Monly_percent": 100.0 * (q_phi_over_m - 1.0),
        "Q_full_over_F1zero2_WM": q_total_over_leading,
        "delta_full_over_F1zero2_WM_percent": (
            100.0 * (q_total_over_leading - 1.0)
        ),
        "cauchy_schwarz_margin": cs_margin,
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"empty input CSV: {path}")
    return rows


def grid_record(row: dict[str, str], **form_factors: float) -> dict[str, float]:
    q = float(row["q_GeV"])
    wm = float(row["W_M00_AFH"])
    wphi = float(row["W_PhiPP_AFH"])
    wmp = float(row["W_MPhiPP_AFH"])
    result = matched_charge_response(q, wm, wphi, wmp, **form_factors)
    er_gev = float(row["ER_keV"]) * 1.0e-6
    result.update({
        "q_GeV": q,
        "q_MeV": 1000.0 * q,
        "ER_keV": float(row["ER_keV"]),
        "t_N_static_GeV2": -q * q,
        "t_A_nuclear_GeV2": -q * q + er_gev * er_gev,
        "W_M": wm,
        "W_PhiPP": wphi,
        "W_MPhiPP": wmp,
        "W_PhiPP_over_W_M": wphi / wm if wm else math.nan,
        "W_MPhiPP_over_W_M": wmp / wm if wm else math.nan,
    })
    return result


def selected_record(row: dict[str, str], **form_factors: float) -> dict[str, float]:
    q = float(row["q_min_MeV"]) / 1000.0
    wm = float(row["W_M00_AFH"])
    wphi = float(row["W_PhiPP_AFH"])
    wmp = float(row["W_MPhiPP_AFH"])
    result = matched_charge_response(q, wm, wphi, wmp, **form_factors)
    er_gev = float(row["ER_min_keV"]) * 1.0e-6
    result.update({
        "q_GeV": q,
        "q_MeV": 1000.0 * q,
        "ER_keV": float(row["ER_min_keV"]),
        "t_N_static_GeV2": -q * q,
        "t_A_nuclear_GeV2": -q * q + er_gev * er_gev,
        "W_M": wm,
        "W_PhiPP": wphi,
        "W_MPhiPP": wmp,
        "W_PhiPP_over_W_M": wphi / wm if wm else math.nan,
        "W_MPhiPP_over_W_M": wmp / wm if wm else math.nan,
    })
    return result


def write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, float]]) -> dict:
    min_row = min(rows, key=lambda row: row["delta_Phi_over_Monly_percent"])
    max_row = max(rows, key=lambda row: row["delta_Phi_over_Monly_percent"])
    return {
        "status": "zero_momentum_form_factor_diagnostic_only",
        "form_factor_model": (
            "constant F1^V(0)=3 and F2^V(0)=-0.552; not a finite-t model"
        ),
        "nucleon_mass_GeV": M_N_GEV_DEFAULT,
        "F1_zero": F1_ZERO_DEFAULT,
        "F2_zero": F2_ZERO_DEFAULT,
        "F1_plus_2F2_zero": F1_ZERO_DEFAULT + 2.0 * F2_ZERO_DEFAULT,
        "grid_points": len(rows),
        "minimum_relative_Phi_correction": min_row,
        "maximum_relative_Phi_correction": max_row,
        "transfer_prescription": (
            "Static one-body impulse approximation: q_N^0=0, "
            "t_N=-|q_A|^2; t_A=-|q_A|^2+E_R^2 is recorded separately."
        ),
        "interpretation": (
            "Q_Phi_over_Monly compares M+Phi'' with the same nonrelativistically "
            "normalized M-only charge response. Q_full_over_F1zero2_WM also "
            "includes the t_N/(8 m_N^2) Darwin-Foldy correction to the M "
            "coefficient. Neither ratio includes spatial-current Sigma/Delta "
            "responses."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid", type=Path, required=True)
    parser.add_argument("--selected", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--m-n", type=float, default=M_N_GEV_DEFAULT)
    parser.add_argument("--f1-zero", type=float, default=F1_ZERO_DEFAULT)
    parser.add_argument("--f2-zero", type=float, default=F2_ZERO_DEFAULT)
    args = parser.parse_args()
    ff = {"m_n": args.m_n, "f1": args.f1_zero, "f2": args.f2_zero}

    grid = [grid_record(row, **ff) for row in read_csv(args.grid)]
    selected = [selected_record(row, **ff) for row in read_csv(args.selected)]
    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(args.outdir / "phi_charge_match_full_grid.csv", grid)
    write_csv(args.outdir / "phi_charge_match_selected_points.csv", selected)

    summary = summarize(grid)
    summary["nucleon_mass_GeV"] = args.m_n
    summary["F1_zero"] = args.f1_zero
    summary["F2_zero"] = args.f2_zero
    summary["selected_points"] = selected
    summary_path = args.outdir / "phi_charge_match_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": summary["status"],
        "grid_points": len(grid),
        "minimum_relative_Phi_correction": {
            k: summary["minimum_relative_Phi_correction"][k]
            for k in ("q_MeV", "ER_keV", "delta_Phi_over_Monly_percent")
        },
        "maximum_relative_Phi_correction": {
            k: summary["maximum_relative_Phi_correction"][k]
            for k in ("q_MeV", "ER_keV", "delta_Phi_over_Monly_percent")
        },
        "selected_points": [
            {
                "q_MeV": row["q_MeV"],
                "ER_keV": row["ER_keV"],
                "delta_Phi_over_Monly_percent":
                    row["delta_Phi_over_Monly_percent"],
                "delta_full_over_F1zero2_WM_percent":
                    row["delta_full_over_F1zero2_WM_percent"],
            }
            for row in selected
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
