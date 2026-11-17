#!/usr/bin/env python3
"""Quantify isotope-mass prescription sensitivity in xenon response and kinematics."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from isotope_mass_schemes import NIST_XE_ATOMIC_MASS_U, isotope_mass_GeV
from joint_xe131 import load_nuclear_response
from rate_kinematics import vmin_three_body_km_s
from run_natural_xenon_joint import AVAILABLE, NATURAL_ABUNDANCE, MODELS

ALL_NIST_ISOTOPES = tuple(sorted(NIST_XE_ATOMIC_MASS_U))
ER_POINTS_KEV = (101.0, 200.0, 267.0, 542.0)
SCHEMES = ("A_u", "nist_nuclear")
VESC_LAB_KM_S = 776.0


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--response-dir", type=Path,
                        default=HERE / "results" / "anand_wm_response")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--mchi-GeV", type=float, default=1000.0)
    parser.add_argument("--ms-MeV", type=float, default=0.3)
    parser.add_argument("--vesc-lab-km-s", type=float, default=VESC_LAB_KM_S)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ms = args.ms_MeV * 1.0e-3
    rows: list[dict] = []

    for A in ALL_NIST_ISOTOPES:
        abundance = NATURAL_ABUNDANCE[A]
        for ER_keV in ER_POINTS_KEV:
            ER = ER_keV * 1.0e-6
            masses = {
                scheme: isotope_mass_GeV(A, scheme)
                for scheme in SCHEMES
            }
            vmins = {
                scheme: vmin_three_body_km_s(
                    args.mchi_GeV, ms, masses[scheme], ER
                )
                for scheme in SCHEMES
            }
            qresponses = {
                scheme: (2.0 * masses[scheme] * ER) ** 0.5
                for scheme in SCHEMES
            }
            qkin = {
                scheme: (2.0 * masses[scheme] * ER + ER * ER) ** 0.5
                for scheme in SCHEMES
            }

            response_values = {}
            if A in AVAILABLE:
                for model in MODELS:
                    response = load_nuclear_response(
                        args.response_dir / f"xe{A}_{model.upper()}_WM.csv",
                        A,
                        model,
                    )
                    response_values[model] = {
                        scheme: response.at_recoil(ER, masses[scheme])[0]
                        for scheme in SCHEMES
                    }
            else:
                response_values = {model: {s: None for s in SCHEMES} for model in MODELS}

            for scheme in SCHEMES:
                other = "nist_nuclear" if scheme == "A_u" else "A_u"
                row = {
                    "A": A,
                    "natural_amount_fraction": abundance,
                    "ER_keV": ER_keV,
                    "mass_scheme": scheme,
                    "mA_GeV": masses[scheme],
                    "relative_mass_difference_vs_Au": masses[scheme] / masses["A_u"] - 1.0,
                    "q_response_GeV": qresponses[scheme],
                    "q_kin_exact_GeV": qkin[scheme],
                    "vmin_km_s": vmins[scheme],
                    "vmin_difference_vs_Au_km_s": vmins[scheme] - vmins["A_u"],
                    "cutoff_phase_space_open_at_776": vmins[scheme] < args.vesc_lab_km_s,
                    "comparison_mass_scheme": other,
                }
                for model in MODELS:
                    row[f"R_A_{model.upper()}"] = response_values[model][scheme]
                    base = response_values[model]["A_u"]
                    current = response_values[model][scheme]
                    row[f"R_A_{model.upper()}_ratio_vs_Au"] = (
                        current / base if base not in (None, 0.0) and current is not None
                        else None
                    )
                rows.append(row)

    out_csv = args.out_dir / "isotope_mass_scheme_sensitivity.csv"
    write_csv(out_csv, rows)

    metadata = {
        "calculation": "xenon isotope mass-scheme sensitivity for q response and three-body vmin",
        "mass_schemes": {
            "A_u": "m_A=A*0.93149410242 GeV; retained previous calculation baseline",
            "nist_nuclear": (
                "m_A=(NIST relative atomic mass - 54 electron masses)*u; "
                "atomic electron binding energy neglected"
            ),
        },
        "nist_atomic_mass_source": "https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ascii=ascii&ele=Xe",
        "mchi_GeV": args.mchi_GeV,
        "ms_MeV": args.ms_MeV,
        "ER_keV": list(ER_POINTS_KEV),
        "lab_speed_cutoff_km_s": args.vesc_lab_km_s,
        "available_response_isotopes": list(AVAILABLE),
        "missing_response_isotopes": [A for A in ALL_NIST_ISOTOPES if A not in AVAILABLE],
        "abundance_coverage": sum(NATURAL_ABUNDANCE[A] for A in AVAILABLE),
        "purpose": (
            "Quantify how a small nuclear-mass shift changes vmin and the "
            "AFH response interpolation, especially near the 776 km/s endpoint."
        ),
    }
    (args.out_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    print("A  ER[keV]  vmin(Au)  vmin(NIST nuc)  delta-vmin  open@776 (Au/NIST)")
    for A in ALL_NIST_ISOTOPES:
        for ER in (101.0, 200.0, 267.0, 542.0):
            a = next(r for r in rows if r["A"] == A and r["ER_keV"] == ER and r["mass_scheme"] == "A_u")
            n = next(r for r in rows if r["A"] == A and r["ER_keV"] == ER and r["mass_scheme"] == "nist_nuclear")
            print(
                f"{A:3d} {ER:7.1f} {a['vmin_km_s']:10.3f} "
                f"{n['vmin_km_s']:14.3f} "
                f"{n['vmin_difference_vs_Au_km_s']:11.3f} "
                f"{a['cutoff_phase_space_open_at_776']}/{n['cutoff_phase_space_open_at_776']}"
            )


if __name__ == "__main__":
    main()
