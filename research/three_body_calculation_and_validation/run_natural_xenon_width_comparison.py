#!/usr/bin/env python3
"""Halo-folded natural-xenon rate comparison for zero/pole/running chi2 widths.

This reproduces the existing pre-detector GCN/JJ55 W_M rate construction at
selected recoil energies while varying only the chi2 width prescription.
It is a width-impact crosscheck, not the full AFH spatial-current result.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from run_natural_xenon_halo_fold import (
    C_KM_S,
    RHO_DM_GEV_CM3_DEFAULT,
    V0_KM_S_DEFAULT,
    VE_KM_S_DEFAULT,
    VESC_KM_S_DEFAULT,
    compute_isotope_halo_integrals,
    mean_target_number_per_kg,
    rate_conversion_factor,
    write_csv,
)
from run_natural_xenon_joint import AVAILABLE, MODELS, NATURAL_ABUNDANCE

MCHI_GEV = 1000.0
MS_MEV = 0.300
DELTA_M_MEV = 1.0
MV_GEV = 10.0
COUPLING_PRODUCT_SQ = 1.0e-8
ER_POINTS_KEV = (101.0, 200.0, 267.0, 542.0)
WIDTH_SCHEMES = ("zero", "pole", "running")


def calculate(args: argparse.Namespace) -> dict:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    response_cache: dict = {}
    isotope_rows: list[dict] = []
    rate_rows: list[dict] = []
    lookup: dict[tuple[str, float, int, str], dict] = {}

    rate_factor = rate_conversion_factor(args.rho_dm, args.mchi)
    for er_keV in args.energies_keV:
        for width_scheme in WIDTH_SCHEMES:
            for A in AVAILABLE:
                rows = compute_isotope_halo_integrals(
                    A=A,
                    ER_keV=er_keV,
                    halo_model="shm_cutoff",
                    mass_scheme=args.mass_scheme,
                    nv=args.nv,
                    mchi=args.mchi,
                    ms=args.ms_MeV * 1.0e-3,
                    delta_m=args.delta_m_MeV * 1.0e-3,
                    speed_v0=args.v0,
                    speed_ve=args.ve,
                    speed_vesc=args.vesc,
                    untruncated_vmax=1600.0,
                    coupling_product_sq=args.coupling_product_sq,
                    response_dir=args.response_dir,
                    nw=args.nw,
                    nz=args.nz,
                    nphi=args.nphi,
                    width_scheme=width_scheme,
                    g2=args.g2,
                    response_cache=response_cache,
                )
                for row in rows:
                    row.update({
                        "width_scheme": width_scheme,
                        "g2": args.g2,
                        "benchmark": "green_ms300_dm1",
                        "mchi_GeV": args.mchi,
                        "ms_MeV": args.ms_MeV,
                        "delta_m_MeV": args.delta_m_MeV,
                        "mV_GeV": args.mV,
                        "coupling_product_sq": args.coupling_product_sq,
                    })
                    isotope_rows.append(row)
                    lookup[(width_scheme, er_keV, A, row["model"])] = row

            for model in MODELS:
                weighted_integral = 0.0
                for A in AVAILABLE:
                    row = lookup[(width_scheme, er_keV, A, model.upper())]
                    denominator = (
                        args.mV**2 + 2.0 * float(row["mA_GeV"]) * er_keV * 1.0e-6
                    ) ** 2
                    weighted_integral += (
                        NATURAL_ABUNDANCE[A] * float(row["J_A_GeV"]) / denominator
                    )
                rate_rows.append({
                    "benchmark": "green_ms300_dm1",
                    "model": model.upper(),
                    "halo_model": "shm_cutoff",
                    "mass_scheme": args.mass_scheme,
                    "ER_keV": er_keV,
                    "width_scheme": width_scheme,
                    "g2": args.g2,
                    "mchi_GeV": args.mchi,
                    "ms_MeV": args.ms_MeV,
                    "delta_m_MeV": args.delta_m_MeV,
                    "mV_GeV": args.mV,
                    "coupling_product_sq": args.coupling_product_sq,
                    "rho_dm_GeV_cm3": args.rho_dm,
                    "available_abundance_fraction": sum(
                        NATURAL_ABUNDANCE[A] for A in AVAILABLE
                    ),
                    "sum_xA_halo_integral_dsigma_GeVminus3": weighted_integral,
                    "rate_events_kg_day_keV": rate_factor * weighted_integral,
                    "detector_response_applied": False,
                })

    for row in rate_rows:
        key = (row["model"], row["ER_keV"])
        zero = next(
            item for item in rate_rows
            if item["model"] == key[0] and item["ER_keV"] == key[1]
            and item["width_scheme"] == "zero"
        )
        row["rate_over_zero_width"] = (
            row["rate_events_kg_day_keV"] / zero["rate_events_kg_day_keV"]
            if zero["rate_events_kg_day_keV"] > 0 else None
        )
        anchor = next(
            item for item in rate_rows
            if item["model"] == row["model"] and item["ER_keV"] == 200.0
            and item["width_scheme"] == row["width_scheme"]
        )
        row["spectrum_shape_over_200keV"] = (
            row["rate_events_kg_day_keV"] / anchor["rate_events_kg_day_keV"]
            if anchor["rate_events_kg_day_keV"] > 0 else None
        )

    isotope_path = args.out_dir / "natural_xenon_isotope_width_comparison.csv"
    rate_path = args.out_dir / "natural_xenon_halo_width_comparison.csv"
    write_csv(isotope_path, isotope_rows)
    write_csv(rate_path, rate_rows)

    summary_rows = []
    for model in MODELS:
        for er_keV in args.energies_keV:
            by_width = {
                row["width_scheme"]: row
                for row in rate_rows
                if row["model"] == model.upper() and row["ER_keV"] == er_keV
            }
            summary_rows.append({
                "model": model.upper(),
                "ER_keV": er_keV,
                "zero_width_rate_events_kg_day_keV":
                    by_width["zero"]["rate_events_kg_day_keV"],
                "pole_width_rate_events_kg_day_keV":
                    by_width["pole"]["rate_events_kg_day_keV"],
                "running_width_rate_events_kg_day_keV":
                    by_width["running"]["rate_events_kg_day_keV"],
                "pole_over_zero": by_width["pole"]["rate_over_zero_width"],
                "running_over_zero": by_width["running"]["rate_over_zero_width"],
            })

    summary = {
        "status": "natural_xenon_halo_folded_width_comparison",
        "benchmark": {
            "name": "green_ms300_dm1",
            "mchi_GeV": args.mchi,
            "ms_MeV": args.ms_MeV,
            "delta_m_MeV": args.delta_m_MeV,
            "mV_GeV": args.mV,
            "coupling_product_sq": args.coupling_product_sq,
            "g2_for_conditional_width": args.g2,
            "rho_dm_GeV_cm3": args.rho_dm,
        },
        "halo": {
            "model": "truncated SHM",
            "v0_km_s": args.v0,
            "ve_km_s": args.ve,
            "vesc_km_s": args.vesc,
            "maximum_lab_speed_km_s": args.ve + args.vesc,
        },
        "nuclear_response": {
            "models": [x.upper() for x in MODELS],
            "available_isotopes": list(AVAILABLE),
            "omitted_isotopes": [124, 126],
            "available_abundance_fraction": sum(NATURAL_ABUNDANCE[A] for A in AVAILABLE),
            "response": "existing GCN/JJ55 W_M isotope grids",
            "AFH_default": False,
        },
        "quadrature": {
            "speed_nodes": args.nv,
            "eq6_orders": {"nw": args.nw, "nz": args.nz, "nphi": args.nphi},
        },
        "width_schemes": {
            "zero": "diagnostic baseline only",
            "pole": "current manuscript conditional pole-width prescription",
            "running": "scalar-channel absorptive running-width comparison",
        },
        "results": summary_rows,
        "limitations": [
            "Pre-detector halo-folded rate; no detector efficiency, resolution, cuts, exposure, or likelihood.",
            "Uses GCN/JJ55 W_M responses, not AFH full spatial nuclear responses.",
            "The scalar-only conditional width assumes Dirac chi, a real scalar, a pure scalar Yukawa vertex, and no other open chi2 decay channels.",
            "This comparison changes only the chi2 width prescription; it does not yet include Sigma', Sigma'', or Delta.",
        ],
    }
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--response-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--energies-keV", type=float, nargs="+", default=list(ER_POINTS_KEV))
    parser.add_argument("--mchi", type=float, default=MCHI_GEV)
    parser.add_argument("--ms-MeV", type=float, default=MS_MEV)
    parser.add_argument("--delta-m-MeV", type=float, default=DELTA_M_MEV)
    parser.add_argument("--mV", type=float, default=MV_GEV)
    parser.add_argument("--coupling-product-sq", type=float, default=COUPLING_PRODUCT_SQ)
    parser.add_argument("--g2", type=float, default=1.0)
    parser.add_argument("--rho-dm", type=float, default=0.3)
    parser.add_argument("--mass-scheme", choices=("A_u", "nist_nuclear"), default="nist_nuclear")
    parser.add_argument("--v0", type=float, default=V0_KM_S_DEFAULT)
    parser.add_argument("--ve", type=float, default=VE_KM_S_DEFAULT)
    parser.add_argument("--vesc", type=float, default=VESC_KM_S_DEFAULT)
    parser.add_argument("--nv", type=int, default=32)
    parser.add_argument("--nw", type=int, default=8)
    parser.add_argument("--nz", type=int, default=8)
    parser.add_argument("--nphi", type=int, default=4)
    args = parser.parse_args()
    calculate(args)


if __name__ == "__main__":
    main()
