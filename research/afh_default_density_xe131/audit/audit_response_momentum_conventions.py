#!/usr/bin/env python3
"""Audit exact AFH spatial recoil momentum against the NR recoil approximation."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parents[1]
NATURAL_INPUT = HERE.parent / "afh_default_density_natural_xenon_halo" / "input"
U_GEV = 0.93149410242
ME_U = 0.000548579909065
Z_XE = 54
RECOIL_POINTS_KEV = (101.0, 200.0, 267.0, 542.0)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def q_response_nr_approx(mA_GeV: float, ER_GeV: float) -> float:
    """Small-recoil approximation q^2=2*m_A*E_R."""
    return math.sqrt(2.0 * mA_GeV * ER_GeV)


def q_response_exact_spatial(mA_GeV: float, ER_GeV: float) -> float:
    """Exact spatial recoil momentum from the nuclear mass shell."""
    return math.sqrt(2.0 * mA_GeV * ER_GeV + ER_GeV * ER_GeV)


def write_rows(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--response-samples", type=Path,
                        default=NATURAL_INPUT / "afh_response_samples.csv")
    parser.add_argument("--isotope-weights", type=Path,
                        default=NATURAL_INPUT / "natural_xenon_isotope_weights.csv")
    parser.add_argument("--xe131-response-csv", type=Path, required=True,
                        help="Fresh AFH Xe-131 response grid from run_afh_default_xe131.py")
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    weights = read_csv(args.isotope_weights)
    samples = read_csv(args.response_samples)
    by_A = {int(r["A"]): r for r in weights}
    if len(samples) != 28:
        raise ValueError(f"expected 28 selected AFH samples, got {len(samples)}")

    q_rows = []
    max_delta_q_keV = 0.0
    max_relative_ppm = 0.0
    for sample in samples:
        A = int(sample["A"])
        ER_keV = float(sample["ER_keV"])
        ER = ER_keV * 1.0e-6
        atom_mass_u = float(by_A[A]["atomic_mass_u"])
        mA = (atom_mass_u - Z_XE * ME_U) * U_GEV
        q_nr = q_response_nr_approx(mA, ER)
        q_exact = q_response_exact_spatial(mA, ER)
        q_sample = float(sample["q_response_GeV"])
        if not math.isclose(q_sample, q_exact, rel_tol=0.0, abs_tol=2e-10):
            raise ValueError(
                f"stored Xe-{A} {ER_keV:g} keV response q does not match "
                f"the exact spatial-q convention: sample={q_sample:.12g}, "
                f"q_exact={q_exact:.12g}"
            )
        if math.isclose(q_sample, q_nr, rel_tol=0.0, abs_tol=2e-10):
            raise ValueError(
                f"Xe-{A} {ER_keV:g} keV sample unexpectedly matches the NR approximation"
            )
        delta_keV = (q_exact - q_nr) * 1.0e6
        relative_ppm = (q_exact / q_nr - 1.0) * 1.0e6
        max_delta_q_keV = max(max_delta_q_keV, delta_keV)
        max_relative_ppm = max(max_relative_ppm, relative_ppm)
        q_rows.append({
            "A": A,
            "ER_keV": ER_keV,
            "mA_NIST_nuclear_GeV": mA,
            "q_response_exact_spatial_GeV": q_exact,
            "q_response_NR_approx_GeV": q_nr,
            "q_sample_archived_GeV": q_sample,
            "delta_q_exact_minus_NR_keV": delta_keV,
            "relative_q_shift_ppm": relative_ppm,
            "sample_matches_exact_spatial_convention": True,
            "sample_matches_NR_approximation": False,
        })
    write_rows(args.outdir / "natural_xenon_q_convention_audit.csv", q_rows)

    response_rows = read_csv(args.xe131_response_csv)
    q_grid = np.asarray([float(r["q_GeV"]) for r in response_rows], dtype=float)
    R_grid = np.asarray([float(r["R_equal_pn_normalized"]) for r in response_rows], dtype=float)
    if len(q_grid) != 2401 or np.any(np.diff(q_grid) <= 0):
        raise ValueError("AFH Xe-131 response grid is not the expected 2401-point monotonic grid")
    interp = PchipInterpolator(q_grid, R_grid, extrapolate=False)

    xe131_weight = by_A[131]
    m131_nist = (float(xe131_weight["atomic_mass_u"]) - Z_XE * ME_U) * U_GEV
    xe131_rows = []
    for ER_keV in RECOIL_POINTS_KEV:
        ER = ER_keV * 1.0e-6
        q_nr = q_response_nr_approx(m131_nist, ER)
        q_exact = q_response_exact_spatial(m131_nist, ER)
        R_nr = float(interp(q_nr))
        R_exact = float(interp(q_exact))
        xe131_rows.append({
            "A": 131,
            "mass_convention": "NIST atomic mass minus 54 electron masses",
            "ER_keV": ER_keV,
            "mA_GeV": m131_nist,
            "q_response_exact_spatial_MeV": q_exact * 1000.0,
            "q_response_NR_approx_MeV": q_nr * 1000.0,
            "delta_q_exact_minus_NR_keV": (q_exact - q_nr) * 1.0e6,
            "R_A_exact_spatial": R_exact,
            "R_A_NR_approx": R_nr,
            "relative_response_shift_NR_approx_vs_exact_ppm": (R_nr / R_exact - 1.0) * 1.0e6,
        })
    write_rows(args.outdir / "xe131_afh_response_shift_NR_vs_exact.csv", xe131_rows)

    # The fixed-speed Figure-2 benchmark historically uses M_A=131*u.
    m131_benchmark = 131.0 * U_GEV
    benchmark_rows = []
    for ER_keV in RECOIL_POINTS_KEV:
        ER = ER_keV * 1.0e-6
        q_nr = q_response_nr_approx(m131_benchmark, ER)
        q_exact = q_response_exact_spatial(m131_benchmark, ER)
        R_nr = float(interp(q_nr))
        R_exact = float(interp(q_exact))
        benchmark_rows.append({
            "A": 131,
            "mass_convention": "M_A=131*u",
            "mA_GeV": m131_benchmark,
            "ER_keV": ER_keV,
            "q_response_exact_spatial_MeV": q_exact * 1000.0,
            "q_response_NR_approx_MeV": q_nr * 1000.0,
            "delta_q_exact_minus_NR_keV": (q_exact - q_nr) * 1.0e6,
            "R_A_exact_spatial": R_exact,
            "R_A_NR_approx": R_nr,
            "relative_response_shift_NR_approx_vs_exact_ppm": (R_nr / R_exact - 1.0) * 1.0e6,
        })
    write_rows(args.outdir / "xe131_fixed_benchmark_q_comparison.csv", benchmark_rows)

    summary = {
        "status": "pass",
        "stored_natural_xenon_response_samples": len(q_rows),
        "stored_sample_convention": "q_response=sqrt(2*m_A*E_R+E_R^2), exact spatial recoil momentum",
        "AFH_response_definition": "y=(q*b_A/2)^2, with q the spatial momentum transfer",
        "exact_spatial_response_convention": "q_response=sqrt(2*m_A*E_R+E_R^2), from the exact nuclear mass shell",
        "NR_approximation_convention": "q_response=sqrt(2*m_A*E_R), valid for E_R much smaller than m_A",
        "three_body_kinematic_convention": "q_kinematic=sqrt(2*m_A*E_R+E_R^2)",
        "mass_scheme": "(NIST atomic isotope mass - 54 electron masses)*u; electronic binding neglected",
        "max_delta_q_keV_across_28_samples": max_delta_q_keV,
        "max_relative_q_shift_ppm_across_28_samples": max_relative_ppm,
        "xe131_response_comparison": "PCHIP interpolation of the freshly regenerated 2401-point AFH default Xe-131 response grid at exact spatial q and q_NR approximation, using NIST nuclear mass",
        "xe131_max_absolute_relative_NR_approx_response_shift_ppm": max(
            abs(r["relative_response_shift_NR_approx_vs_exact_ppm"]) for r in xe131_rows
        ),
        "xe131_fixed_benchmark_mass_comparison": "PCHIP interpolation of the same response grid using the Figure-2 benchmark mass M_A=131*u",
        "interpretation": [
            "AFH defines y=(q*b_A/2)^2 with q the spatial momentum transfer; exact mass-shell kinematics gives q=sqrt(2*m_A*E_R+E_R^2).",
            "The archived 28 natural-xenon response samples use exact spatial q and are the physically consistent choice for the exact three-body kinematics.",
            "q_NR=sqrt(2*m_A*E_R) is a small-recoil approximation; its response impact is quantified but it does not invalidate the exact-q samples.",
            "The archived natural-xenon halo rates therefore remain the exact-spatial-q baseline; no seven-isotope response regeneration is required to preserve this convention."
        ]
    }
    (args.outdir / "q_convention_audit_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
