#!/usr/bin/env python3
"""Isotope-by-isotope natural-xenon three-body cross-section diagnostic.

This computes each isotope's own AFH response and Eq. (6) kernel before
abundance weighting. It is a fixed-speed, zero-width calculation. The vector
mediator mass is not known from the Figure 2 caption, so a clearly labelled
exploratory mV scan is used rather than selecting one value as the original.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import eq6_kernel  # noqa: E402
from joint_xe131 import (  # noqa: E402
    isotope_mass_GeV,
    load_nuclear_response,
)

NATURAL_ABUNDANCE = {
    124: 0.000952,
    126: 0.000890,
    128: 0.019102,
    129: 0.264006,
    130: 0.040710,
    131: 0.212324,
    132: 0.269086,
    134: 0.104357,
    136: 0.088573,
}
AVAILABLE = (128, 129, 130, 131, 132, 134, 136)
MODELS = ("gcn", "jj55")


def pchi_GeV(mchi: float, speed_kms: float) -> float:
    beta = speed_kms / eq6_kernel.C_KM_S
    gamma = 1.0 / math.sqrt(1.0 - beta * beta)
    return mchi * gamma * beta


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows to write: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--response-dir",
        type=Path,
        default=HERE / "results" / "anand_wm_response",
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--mchi-GeV", type=float, default=1000.0)
    parser.add_argument("--ms-MeV", type=float, default=0.3)
    parser.add_argument("--delta-m-MeV", type=float, default=1.0)
    parser.add_argument("--speed-km-s", type=float, default=776.0)
    parser.add_argument("--coupling-product-sq", type=float, default=1.0e-8)
    parser.add_argument("--ER-keV", type=float, nargs="+",
                        default=[101.0, 200.0, 267.0, 542.0])
    parser.add_argument("--mV-scan-GeV", type=float, nargs="+",
                        default=[0.05, 0.1, 0.2, 0.5, 1.0])
    parser.add_argument("--nw", type=int, default=40)
    parser.add_argument("--nz", type=int, default=32)
    parser.add_argument("--nphi", type=int, default=20)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ms = args.ms_MeV * 1.0e-3
    delta_m = args.delta_m_MeV * 1.0e-3
    pchi = pchi_GeV(args.mchi_GeV, args.speed_km_s)

    isotope_rows: list[dict] = []
    isotope_dsigma_rows: list[dict] = []
    response_cache: dict[tuple[int, str], object] = {}
    abundance_coverage = sum(NATURAL_ABUNDANCE[A] for A in AVAILABLE)

    for A in AVAILABLE:
        mA = isotope_mass_GeV(A)
        for model in MODELS:
            response_path = args.response_dir / f"xe{A}_{model.upper()}_WM.csv"
            response_cache[(A, model)] = load_nuclear_response(
                response_path, A, model
            )

        for ER_keV in args.ER_keV:
            ER = ER_keV * 1.0e-6
            q_response = math.sqrt(2.0 * mA * ER)
            q_exact = math.sqrt(2.0 * mA * ER + ER * ER)
            wmin2, wmax2 = eq6_kernel.limits(
                args.mchi_GeV, ms, mA, ER, args.speed_km_s
            )
            phase_open = wmax2 > wmin2
            I6 = eq6_kernel.reduced_kernel(
                args.mchi_GeV, ms, delta_m, mA, ER, args.speed_km_s,
                nw=args.nw, nz=args.nz, nphi=args.nphi,
                width_scheme="zero",
            )
            pole_gap_keV = (
                1000.0 * (args.mchi_GeV + delta_m - math.sqrt(wmax2))
                if wmax2 > 0.0 else None
            )

            for model in MODELS:
                response = response_cache[(A, model)]
                R_A, _ = response.at_recoil(ER, mA)
                C_A = (
                    mA * args.coupling_product_sq
                    / (256.0 * math.pi**3 * pchi**2)
                    * R_A * I6
                )
                abundance = NATURAL_ABUNDANCE[A]
                isotope_rows.append({
                    "A": A,
                    "model": model.upper(),
                    "natural_amount_fraction": abundance,
                    "mA_GeV": mA,
                    "ER_keV": ER_keV,
                    "q_response_NR_GeV": q_response,
                    "q_kinematics_exact_GeV": q_exact,
                    "R_A": R_A,
                    "R_A_over_A2": R_A / (A * A),
                    "phase_space_open": phase_open,
                    "I6_GeV2": I6,
                    "chi2_pole_gap_keV": pole_gap_keV,
                    "C_A_GeV": C_A,
                })

                for mV in args.mV_scan_GeV:
                    denominator = (mV * mV + 2.0 * mA * ER) ** 2
                    dsigma = C_A / denominator if denominator > 0.0 else float("inf")
                    isotope_dsigma_rows.append({
                        "A": A,
                        "model": model.upper(),
                        "natural_amount_fraction": abundance,
                        "ER_keV": ER_keV,
                        "mV_GeV": mV,
                        "dsigma_dER_GeVminus3": dsigma,
                        "abundance_weighted_dsigma_GeVminus3": abundance * dsigma,
                        "phase_space_open": phase_open,
                    })

    natural_rows: list[dict] = []
    for model in ("GCN", "JJ55"):
        for ER_keV in args.ER_keV:
            for mV in args.mV_scan_GeV:
                selected = [
                    r for r in isotope_dsigma_rows
                    if r["model"] == model
                    and r["ER_keV"] == ER_keV
                    and r["mV_GeV"] == mV
                ]
                weighted_sum = sum(
                    float(r["abundance_weighted_dsigma_GeVminus3"])
                    for r in selected
                )
                natural_rows.append({
                    "model": model,
                    "ER_keV": ER_keV,
                    "mV_GeV": mV,
                    "available_abundance_fraction": abundance_coverage,
                    "sum_xA_dsigma_dER_GeVminus3": weighted_sum,
                    "common_per_detector_mass_factor_omitted": "1/mean_xenon_nuclear_mass",
                    "interpretation": "fixed-speed isotope sum; not halo folded",
                })

    write_csv(args.out_dir / "isotope_contributions.csv", isotope_rows)
    write_csv(args.out_dir / "isotope_dsigma_mV_scan.csv", isotope_dsigma_rows)
    write_csv(args.out_dir / "natural_xenon_mV_scan.csv", natural_rows)

    metadata = {
        "calculation": "isotope-specific natural-xenon AFH response x Eq. (6)",
        "available_isotopes": list(AVAILABLE),
        "omitted_isotopes": [124, 126],
        "available_natural_amount_fraction": abundance_coverage,
        "omitted_natural_amount_fraction": 1.0 - abundance_coverage,
        "abundance_source": "NIST xenon isotopic compositions as recorded in run_anand_wm_response.py",
        "abundance_convention": "atomic amount fractions; not mass fractions",
        "abundance_renormalization": "none; missing 124/126 fraction is left missing",
        "mA_prescription": "A * 0.93149410242 GeV",
        "mchi_GeV": args.mchi_GeV,
        "ms_MeV": args.ms_MeV,
        "delta_m_MeV": args.delta_m_MeV,
        "speed_km_s": args.speed_km_s,
        "speed_treatment": "single fixed incident speed; no halo integral",
        "coupling_product_sq": args.coupling_product_sq,
        "width_scheme": "zero",
        "mV_scan_GeV": args.mV_scan_GeV,
        "mV_status": "exploratory parameter scan; no mV benchmark is specified in the Figure 2 caption",
        "quadrature": {"nw": args.nw, "nz": args.nz, "nphi": args.nphi},
        "response_y_convention": "y=b_A^2*m_A*E_R/2; q_response=sqrt(2*m_A*E_R)",
        "three_body_kinematics": "q_exact=sqrt(2*m_A*E_R+E_R^2)",
        "models": ["GCN", "JJ55"],
        "natural_sum": "sum_A x_A * d sigma_A/dE_R; common 1/mean xenon mass omitted",
        "not_included": [
            "Xe-124 and Xe-126 nuclear density matrices",
            "halo velocity integral",
            "detector efficiency and exposure",
            "finite-width uncertainty from the unspecified separate g2",
        ],
    }
    (args.out_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Natural xenon isotope coverage: {abundance_coverage:.8f}")
    print(f"Missing isotope abundance: {1.0 - abundance_coverage:.8f}")
    print(f"Computed {len(isotope_rows)} isotope/model/recoil contributions.")
    print(f"Computed {len(natural_rows)} abundance-weighted mV-scan points.")
    for row in natural_rows:
        print(
            f"{row['model']} ER={row['ER_keV']:.0f} keV "
            f"mV={row['mV_GeV']:.3g} GeV "
            f"sum_xA_dsigma/dER={row['sum_xA_dsigma_dER_GeVminus3']:.8g} GeV^-3"
        )


if __name__ == "__main__":
    main()
