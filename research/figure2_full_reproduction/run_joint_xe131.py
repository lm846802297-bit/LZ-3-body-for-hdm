#!/usr/bin/env python3
"""Run a Xe-131 single-speed joint AFH-response / three-body-kernel diagnostic."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from joint_xe131 import (  # noqa: E402
    differential_cross_section,
    isotope_mass_GeV,
    load_nuclear_response,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--response-dir",
        type=Path,
        default=HERE / "results" / "anand_wm_response",
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--A", type=int, default=131)
    parser.add_argument("--mchi-GeV", type=float, default=1000.0)
    parser.add_argument("--ms-MeV", type=float, default=0.3)
    parser.add_argument("--delta-m-MeV", type=float, default=1.0)
    parser.add_argument("--speed-km-s", type=float, default=776.0)
    parser.add_argument("--coupling-product-sq", type=float, default=1.0e-8)
    parser.add_argument(
        "--ER-keV", type=float, nargs="+",
        default=[101.0, 200.0, 267.0, 542.0],
    )
    parser.add_argument("--mV-GeV", type=float, default=None)
    parser.add_argument(
        "--width-scheme", choices=("zero", "pole", "running"), default="zero"
    )
    parser.add_argument("--g2", type=float, default=None)
    parser.add_argument("--nw", type=int, default=16)
    parser.add_argument("--nz", type=int, default=16)
    parser.add_argument("--nphi", type=int, default=8)
    args = parser.parse_args()

    if args.width_scheme in ("pole", "running") and args.g2 is None:
        parser.error("--g2 is required for pole/running width schemes")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    mA = isotope_mass_GeV(args.A)
    ms = args.ms_MeV * 1.0e-3
    delta_m = args.delta_m_MeV * 1.0e-3

    all_rows: list[dict] = []
    for model in ("gcn", "jj55"):
        response_path = args.response_dir / f"xe{args.A}_{model.upper()}_WM.csv"
        if not response_path.exists():
            # The archived filenames use lower-case model names.
            response_path = args.response_dir / f"xe{args.A}_{model}_WM.csv"
        response = load_nuclear_response(response_path, args.A, model)

        rows = []
        for ER_keV in args.ER_keV:
            result = differential_cross_section(
                response,
                mchi_GeV=args.mchi_GeV,
                ms_GeV=ms,
                delta_m_GeV=delta_m,
                ER_GeV=ER_keV * 1.0e-6,
                speed_km_s=args.speed_km_s,
                coupling_product_sq=args.coupling_product_sq,
                mV_GeV=args.mV_GeV,
                width_scheme=args.width_scheme,
                g2=args.g2,
                nw=args.nw,
                nz=args.nz,
                nphi=args.nphi,
            )
            result["ER_keV"] = ER_keV
            result["chi2_pole_gap_keV"] = (
                1000.0 * float(result["chi2_pole_gap_GeV"])
                if result["chi2_pole_gap_GeV"] == result["chi2_pole_gap_GeV"]
                else None
            )
            result["chi2_on_shell_closed"] = (
                result["chi2_pole_gap_GeV"] > 0.0
            )
            rows.append(result)
            all_rows.append(result)

        out_csv = args.out_dir / f"xe{args.A}_{model}_joint_single_speed.csv"
        with out_csv.open("w", newline="", encoding="utf-8") as handle:
            fields = list(rows[0].keys())
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    metadata = {
        "calculation": "Xe-131 AFH W_M response x manuscript Eq. (6)",
        "target_A": args.A,
        "target_mass_GeV": mA,
        "target_mass_prescription": "A * 0.93149410242 GeV",
        "mchi_GeV": args.mchi_GeV,
        "ms_MeV": args.ms_MeV,
        "delta_m_MeV": args.delta_m_MeV,
        "speed_km_s": args.speed_km_s,
        "speed_treatment": "fixed incident speed; not a halo velocity integral",
        "coupling_product_sq": args.coupling_product_sq,
        "coupling_product_definition": "(g1*g2*gVN)^2",
        "mV_GeV": args.mV_GeV,
        "mV_status": "not supplied by the Figure 2 caption; left explicit",
        "width_scheme": args.width_scheme,
        "g2": args.g2,
        "width_caveat": (
            "Pole/running widths are conditional on the Dirac pure-scalar "
            "two-body width helper; the manuscript does not state the "
            "Dirac/Majorana realization or a separate g2 benchmark."
        ),
        "response_y_convention": "y=(b_A*q/2)^2 with q the exact spatial momentum transfer",
        "response_momentum": "q_response=q_kinematics=sqrt(2*m_A*E_R+E_R^2)",
        "small_recoil_approximation": "q_NR=sqrt(2*m_A*E_R)",
        "three_body_kinematic_momentum": "q_exact=sqrt(2*m_A*E_R+E_R^2)",
        "nuclear_models": ["GCN", "JJ55"],
        "quadrature": {"nw": args.nw, "nz": args.nz, "nphi": args.nphi},
        "ER_keV": args.ER_keV,
        "interpretation": (
            "Differential cross section only when mV_GeV is supplied. "
            "Otherwise C_A_GeV is archived as the coefficient before the "
            "vector-propagator denominator. This is not an event rate."
        ),
    }
    (args.out_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Xe-{args.A}: mA={mA:.9f} GeV")
    print(f"width scheme={args.width_scheme}; mV={args.mV_GeV}")
    for row in all_rows:
        print(
            f"{row['model']:4s} ER={row['ER_keV']:7.2f} keV "
            f"R_A={row['R_A']:.8g} I6={row['I6_GeV2']:.8g} GeV^2 "
            f"C_A={row['C_A_GeV']:.8g} GeV "
            f"open={row['phase_space_open']} "
            f"chi2_on_shell_closed={row['chi2_on_shell_closed']}"
        )


if __name__ == "__main__":
    main()
