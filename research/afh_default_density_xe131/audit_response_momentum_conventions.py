#!/usr/bin/env python3
"""Audit q_response versus exact q_kinematics for the AFH xenon workflow."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
NATURAL_INPUT = HERE.parent / "afh_default_density_natural_xenon_halo" / "input"
U_GEV = 0.93149410242
ME_U = 0.000548579909065
Z_XE = 54
RECOIL_POINTS_KEV = (101.0, 200.0, 267.0, 542.0)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def q_response_nr(mA_GeV: float, ER_GeV: float) -> float:
    """The manuscript's y=b_A^2*m_A*E_R/2 response convention."""
    return math.sqrt(2.0 * mA_GeV * ER_GeV)


def q_kinematic_exact(mA_GeV: float, ER_GeV: float) -> float:
    """Exact spatial recoil momentum from the nuclear mass shell."""
    return math.sqrt(2.0 * mA_GeV * ER_GeV + ER_GeV * ER_GeV)


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
        q_nr = q_response_nr(mA, ER)
        q_exact = q_kinematic_exact(mA, ER)
        q_sample = float(sample["q_response_GeV"])
        if not math.isclose(q_sample, q_exact, rel_tol=0.0, abs_tol=2e-10):
            raise ValueError(
                f"stored Xe-{A} {ER_keV:g} keV response q does not match "
                f"the archived exact-q convention: sample={q_sample:.12g}, "
                f"q_exact={q_exact:.12g}"
            )
        if math.isclose(q_sample, q_nr, rel_tol=0.0, abs_tol=2e-10):
            raise ValueError(
                f"Xe-{A} {ER_keV:g} keV sample unexpectedly matches both conventions"
            )
        delta_keV = (q_exact - q_nr) * 1.0e6
        relative_ppm = (q_exact / q_nr - 1.0) * 1.0e6
        max_delta_q_keV = max(max_delta_q_keV, delta_keV)
        max_relative_ppm = max(max_relative_ppm, relative_ppm)
        q_rows.append({
            "A": A,
            "ER_keV": ER_keV,
            "mA_NIST_nuclear_GeV": mA,
            "q_response_manuscript_NR_GeV": q_nr,
            "q_kinematic_exact_GeV": q_exact,
            "q_sample_archived_GeV": q_sample,
            "delta_q_exact_minus_NR_keV": delta_keV,
            "relative_q_shift_ppm": relative_ppm,
            "sample_matches_exact_convention": True,
            "sample_matches_manuscript_NR_convention": False,
        })

    with (args.outdir / "natural_xenon_q_convention_audit.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=list(q_rows[0]))
        writer.writeheader()
        writer.writerows(q_rows)

    response_rows = read_csv(args.xe131_response_csv)
    q_grid = np.asarray([float(r["q_GeV"]) for r in response_rows], dtype=float)
    R_grid = np.asarray([float(r["R_equal_pn_normalized"]) for r in response_rows], dtype=float)
    if len(q_grid) != 2401 or np.any(np.diff(q_grid) <= 0):
        raise ValueError("AFH Xe-131 response grid is not the expected 2401-point monotonic grid")
    interp = PchipInterpolator(q_grid, R_grid, extrapolate=False)
    xe131_weight = by_A[131]
    m131 = (float(xe131_weight["atomic_mass_u"]) - Z_XE * ME_U) * U_GEV
    xe131_rows = []
    for ER_keV in RECOIL_POINTS_KEV:
        ER = ER_keV * 1.0e-6
        q_nr = q_response_nr(m131, ER)
        q_exact = q_kinematic_exact(m131, ER)
        R_nr = float(interp(q_nr))
        R_exact = float(interp(q_exact))
        xe131_rows.append({
            "A": 131,
            "ER_keV": ER_keV,
            "mA_NIST_nuclear_GeV": m131,
            "q_response_manuscript_NR_MeV": q_nr * 1000.0,
            "q_kinematic_exact_MeV": q_exact * 1000.0,
            "delta_q_keV": (q_exact - q_nr) * 1.0e6,
            "R_A_at_manuscript_NR_q": R_nr,
            "R_A_at_exact_q": R_exact,
            "relative_response_shift_exact_vs_NR_ppm": (R_exact / R_nr - 1.0) * 1.0e6,
        })
    with (args.outdir / "xe131_afh_response_shift_NR_vs_exact.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=list(xe131_rows[0]))
        writer.writeheader()
        writer.writerows(xe131_rows)

    summary = {
        "status": "pass",
        "stored_natural_xenon_response_samples": len(q_rows),
        "stored_sample_convention": "q_response=sqrt(2*m_A*E_R+E_R^2), exact spatial recoil momentum",
        "manuscript_response_convention": "q_response=sqrt(2*m_A*E_R), from y=b_A^2*m_A*E_R/2",
        "three_body_kinematic_convention": "q_kinematic=sqrt(2*m_A*E_R+E_R^2)",
        "mass_scheme": "(NIST atomic isotope mass - 54 electron masses)*u; electronic binding neglected",
        "max_delta_q_keV_across_28_samples": max_delta_q_keV,
        "max_relative_q_shift_ppm_across_28_samples": max_relative_ppm,
        "xe131_response_comparison": "PCHIP interpolation of the freshly regenerated 2401-point AFH default Xe-131 response grid at q_NR and q_exact, using NIST nuclear mass",
        "xe131_max_absolute_relative_response_shift_ppm": max(
            abs(r["relative_response_shift_exact_vs_NR_ppm"]) for r in xe131_rows
        ),
        "interpretation": [
            "The archived 28 natural-xenon AFH samples were evaluated at q_exact, not at the manuscript's q_response_NR.",
            "The exact q remains the correct momentum in the three-body kinematic boundary and v_min calculation.",
            "The archived halo rates are preserved as legacy exact-q-response results; they are not silently relabeled as manuscript-NR results.",
            "A corrected natural-xenon AFH rate requires regenerating the seven isotope response samples at q_response_NR from the full AFH isotope response table.",
        ],
    }
    (args.outdir / "q_convention_audit_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
