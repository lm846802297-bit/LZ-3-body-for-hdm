#!/usr/bin/env python3
"""Continuous pre-detector natural-xenon recoil spectra for GCN/JJ55 responses.

This is a nuclear-response-model comparison, not an AFH-default result.
It uses the full isotope-specific GCN/JJ55 response grids, exact spatial q,
NIST-derived nuclear masses, the truncated SHM, and the same conditional
chi2 pole-width benchmark assumptions used by the AFH selected-point fold.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from run_natural_xenon_halo_fold import (
    C_KM_S,
    NIST_XE_STANDARD_ATOMIC_WEIGHT_G_MOL,
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


BENCHMARKS = {
    "red_ms200_dm1": {"ms_MeV": 0.200, "delta_m_MeV": 1.0},
    "green_ms300_dm1": {"ms_MeV": 0.300, "delta_m_MeV": 1.0},
    "black_ms360_dm1": {"ms_MeV": 0.360, "delta_m_MeV": 1.0},
    "blue_ms300_dm10": {"ms_MeV": 0.300, "delta_m_MeV": 10.0},
}
SELECTED_CHECK_ENERGIES_KEV = (101.0, 200.0, 267.0, 542.0)


def recoil_grid(er_min: float, er_max: float, er_step: float) -> list[float]:
    if not (0.0 < er_min <= er_max and er_step > 0.0):
        raise ValueError("require 0 < ER-min <= ER-max and ER-step > 0")
    count = int(round((er_max - er_min) / er_step))
    values = [er_min + i * er_step for i in range(count + 1)]
    if not math.isclose(values[-1], er_max, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError("ER range must be an integer number of ER steps")
    return sorted(set(values).union(SELECTED_CHECK_ENERGIES_KEV))


def relative_difference(a: float, b: float) -> float:
    if a == 0.0 and b == 0.0:
        return 0.0
    if a == 0.0:
        return math.inf
    return abs(b / a - 1.0)


def run(args: argparse.Namespace) -> dict:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    response_dir = args.response_dir
    energies = recoil_grid(args.er_min_keV, args.er_max_keV, args.er_step_keV)
    rate_factor = rate_conversion_factor(args.rhoDM_GeV_cm3, args.mchi_GeV)
    response_cache: dict = {}

    isotope_rows: list[dict] = []
    isotope_index: dict[tuple[str, float, int, str], dict] = {}
    natural_rows: list[dict] = []

    for benchmark in args.benchmarks:
        spec = BENCHMARKS[benchmark]
        ms = spec["ms_MeV"] * 1.0e-3
        delta_m = spec["delta_m_MeV"] * 1.0e-3
        for er_keV in energies:
            for A in AVAILABLE:
                rows = compute_isotope_halo_integrals(
                    A=A,
                    ER_keV=er_keV,
                    halo_model="shm_cutoff",
                    mass_scheme=args.mass_scheme,
                    nv=args.nv,
                    mchi=args.mchi_GeV,
                    ms=ms,
                    delta_m=delta_m,
                    speed_v0=args.v0_km_s,
                    speed_ve=args.ve_km_s,
                    speed_vesc=args.vesc_km_s,
                    untruncated_vmax=1600.0,
                    coupling_product_sq=args.coupling_product_sq,
                    response_dir=response_dir,
                    nw=args.nw,
                    nz=args.nz,
                    nphi=args.nphi,
                    width_scheme="pole",
                    g2=args.g2,
                    response_cache=response_cache,
                )
                for row in rows:
                    row.update({
                        "benchmark": benchmark,
                        "mchi_GeV": args.mchi_GeV,
                        "ms_MeV": spec["ms_MeV"],
                        "delta_m_MeV": spec["delta_m_MeV"],
                        "mV_GeV": args.mV_GeV,
                        "g2": args.g2,
                        "coupling_product_sq": args.coupling_product_sq,
                        "rhoDM_GeV_cm3": args.rhoDM_GeV_cm3,
                        "response_q_convention": "exact_spatial",
                    })
                    isotope_rows.append(row)
                    isotope_index[(benchmark, er_keV, A, row["model"])] = row

            for model in MODELS:
                weighted_integral = 0.0
                for A in AVAILABLE:
                    row = isotope_index[(benchmark, er_keV, A, model.upper())]
                    er_GeV = er_keV * 1.0e-6
                    denominator = (
                        args.mV_GeV**2 + 2.0 * float(row["mA_GeV"]) * er_GeV
                    ) ** 2
                    weighted_integral += (
                        NATURAL_ABUNDANCE[A] * float(row["J_A_GeV"]) / denominator
                    )
                natural_rows.append({
                    "benchmark": benchmark,
                    "model": model.upper(),
                    "halo_model": "shm_cutoff",
                    "mass_scheme": args.mass_scheme,
                    "ER_keV": er_keV,
                    "mchi_GeV": args.mchi_GeV,
                    "ms_MeV": spec["ms_MeV"],
                    "delta_m_MeV": spec["delta_m_MeV"],
                    "mV_GeV": args.mV_GeV,
                    "width_scheme": "pole",
                    "g2": args.g2,
                    "coupling_product_sq": args.coupling_product_sq,
                    "rhoDM_GeV_cm3": args.rhoDM_GeV_cm3,
                    "available_abundance_fraction": sum(
                        NATURAL_ABUNDANCE[A] for A in AVAILABLE
                    ),
                    "sum_xA_halo_integral_dsigma_GeVminus3": weighted_integral,
                    "rate_events_kg_day_keV": rate_factor * weighted_integral,
                    "detector_response_applied": False,
                })

    # Independent spot checks at the recoil points used by the AFH selected-point fold.
    check_rows: list[dict] = []
    for benchmark in args.benchmarks:
        spec = BENCHMARKS[benchmark]
        ms = spec["ms_MeV"] * 1.0e-3
        delta_m = spec["delta_m_MeV"] * 1.0e-3
        for er_keV in SELECTED_CHECK_ENERGIES_KEV:
            for A in AVAILABLE:
                low_speed = compute_isotope_halo_integrals(
                    A=A, ER_keV=er_keV, halo_model="shm_cutoff",
                    mass_scheme=args.mass_scheme, nv=args.nv_low,
                    mchi=args.mchi_GeV, ms=ms, delta_m=delta_m,
                    speed_v0=args.v0_km_s, speed_ve=args.ve_km_s,
                    speed_vesc=args.vesc_km_s, untruncated_vmax=1600.0,
                    coupling_product_sq=args.coupling_product_sq,
                    response_dir=response_dir, nw=args.nw, nz=args.nz,
                    nphi=args.nphi, width_scheme="pole", g2=args.g2,
                    response_cache=response_cache,
                )
                high_speed = compute_isotope_halo_integrals(
                    A=A, ER_keV=er_keV, halo_model="shm_cutoff",
                    mass_scheme=args.mass_scheme, nv=args.nv,
                    mchi=args.mchi_GeV, ms=ms, delta_m=delta_m,
                    speed_v0=args.v0_km_s, speed_ve=args.ve_km_s,
                    speed_vesc=args.vesc_km_s, untruncated_vmax=1600.0,
                    coupling_product_sq=args.coupling_product_sq,
                    response_dir=response_dir, nw=args.nw, nz=args.nz,
                    nphi=args.nphi, width_scheme="pole", g2=args.g2,
                    response_cache=response_cache,
                )
                high_kernel = compute_isotope_halo_integrals(
                    A=A, ER_keV=er_keV, halo_model="shm_cutoff",
                    mass_scheme=args.mass_scheme, nv=args.nv,
                    mchi=args.mchi_GeV, ms=ms, delta_m=delta_m,
                    speed_v0=args.v0_km_s, speed_ve=args.ve_km_s,
                    speed_vesc=args.vesc_km_s, untruncated_vmax=1600.0,
                    coupling_product_sq=args.coupling_product_sq,
                    response_dir=response_dir, nw=args.nw_high,
                    nz=args.nz_high, nphi=args.nphi_high,
                    width_scheme="pole", g2=args.g2,
                    response_cache=response_cache,
                )
                for low, mid, high in zip(low_speed, high_speed, high_kernel):
                    check_rows.append({
                        "benchmark": benchmark,
                        "A": A,
                        "model": mid["model"],
                        "ER_keV": er_keV,
                        "nv_low": args.nv_low,
                        "nv_final": args.nv,
                        "speed_quadrature_relative_difference": relative_difference(
                            float(low["J_A_GeV"]), float(mid["J_A_GeV"])
                        ),
                        "kernel_order_low": f"{args.nw}x{args.nz}x{args.nphi}",
                        "kernel_order_high": f"{args.nw_high}x{args.nz_high}x{args.nphi_high}",
                        "kernel_order_relative_difference": relative_difference(
                            float(mid["J_A_GeV"]), float(high["J_A_GeV"])
                        ),
                    })

    max_speed = max(
        (float(r["speed_quadrature_relative_difference"]) for r in check_rows),
        default=0.0,
    )
    max_kernel = max(
        (float(r["kernel_order_relative_difference"]) for r in check_rows),
        default=0.0,
    )
    if max_speed > args.max_relative_check or max_kernel > args.max_relative_check:
        raise ArithmeticError(
            f"quadrature check failed: speed={max_speed:.4g}, kernel={max_kernel:.4g}, "
            f"tolerance={args.max_relative_check:.4g}"
        )

    write_csv(args.out_dir / "isotope_continuous_spectrum.csv", isotope_rows)
    write_csv(args.out_dir / "natural_xenon_continuous_spectrum.csv", natural_rows)
    write_csv(args.out_dir / "quadrature_crosschecks.csv", check_rows)

    metadata = {
        "calculation": "continuous pre-detector natural-xenon three-body recoil spectrum",
        "nuclear_response_models": ["GCN", "JJ55"],
        "afh_default_response_used": False,
        "afh_comparison": (
            "AFH v6.0 is retained separately at 28 selected isotope/recoil samples; "
            "this continuous calculation uses the complete GCN/JJ55 isotope response grids."
        ),
        "available_isotopes": list(AVAILABLE),
        "omitted_isotopes": [124, 126],
        "available_natural_amount_fraction": sum(NATURAL_ABUNDANCE[A] for A in AVAILABLE),
        "abundance_renormalization": "none",
        "abundance_source": "NIST xenon isotopic amount fractions",
        "mean_target_molar_mass_g_mol": NIST_XE_STANDARD_ATOMIC_WEIGHT_G_MOL,
        "mean_target_number_per_kg": mean_target_number_per_kg(),
        "mass_scheme": args.mass_scheme,
        "isotope_nuclear_mass_prescription": (
            "NIST atomic isotope mass minus 54 electron rest masses, multiplied by u; "
            "atomic electron binding energy neglected"
            if args.mass_scheme == "nist_nuclear" else "A*u"
        ),
        "response_q_convention": "exact spatial q=sqrt(2*m_A*E_R+E_R^2)",
        "kinematic_q_convention": "exact spatial q=sqrt(2*m_A*E_R+E_R^2)",
        "halo_model": "truncated SHM",
        "halo_parameters_km_s": {
            "v0": args.v0_km_s,
            "vE": args.ve_km_s,
            "vesc": args.vesc_km_s,
            "maximum_lab_speed": args.vesc_km_s + args.ve_km_s,
        },
        "particle_parameters": {
            "mchi_GeV": args.mchi_GeV,
            "mV_GeV": args.mV_GeV,
            "coupling_product_sq_(g1_g2_gVN)^2": args.coupling_product_sq,
            "g2_for_width": args.g2,
            "rhoDM_GeV_cm3": args.rhoDM_GeV_cm3,
        },
        "benchmarks": BENCHMARKS,
        "recoil_grid_keV": {
            "min": args.er_min_keV,
            "max": args.er_max_keV,
            "step": args.er_step_keV,
            "additional_exact_comparison_points": list(SELECTED_CHECK_ENERGIES_KEV),
            "unique_point_count": len(energies),
        },
        "width_scheme": "conditional pole width for chi2 -> chi1 s",
        "width_assumptions": (
            "Dirac fermions, real scalar, pure scalar off-diagonal Yukawa, "
            "and no other open chi2 decay channels"
        ),
        "quadrature": {
            "speed_nodes": args.nv,
            "eq6": {"nw": args.nw, "nz": args.nz, "nphi": args.nphi},
            "spot_check_speed_nodes": args.nv_low,
            "spot_check_eq6": {
                "nw": args.nw_high,
                "nz": args.nz_high,
                "nphi": args.nphi_high,
            },
            "maximum_speed_quadrature_relative_difference": max_speed,
            "maximum_kernel_order_relative_difference": max_kernel,
            "relative_tolerance": args.max_relative_check,
        },
        "rate_units": "events / kg / day / keV",
        "detector_response_applied": False,
        "not_included": [
            "detector efficiency, S1/S2 response, energy resolution, exposure, cuts and likelihood",
            "Xe-124 and Xe-126 nuclear response contributions",
            "full seven-isotope AFH v6.0 response grid",
            "annual modulation and time-dependent Earth velocity",
            "uncertainty propagation for halo and nuclear response inputs",
        ],
    }
    (args.out_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))
    print(
        f"Saved {len(natural_rows)} natural-xenon spectrum rows and "
        f"{len(isotope_rows)} isotope-resolved rows."
    )
    print(
        f"Quadrature checks: max speed difference={max_speed:.3e}, "
        f"max kernel-order difference={max_kernel:.3e}."
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--response-dir", type=Path,
                        default=Path(__file__).resolve().parent / "results" / "anand_wm_response")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--benchmarks", nargs="+", choices=tuple(BENCHMARKS),
                        default=list(BENCHMARKS))
    parser.add_argument("--mass-scheme", choices=("A_u", "nist_nuclear"), default="nist_nuclear")
    parser.add_argument("--er-min-keV", type=float, default=5.0)
    parser.add_argument("--er-max-keV", type=float, default=800.0)
    parser.add_argument("--er-step-keV", type=float, default=5.0)
    parser.add_argument("--mchi-GeV", type=float, default=1000.0)
    parser.add_argument("--mV-GeV", type=float, default=10.0)
    parser.add_argument("--coupling-product-sq", type=float, default=1.0e-8)
    parser.add_argument("--rhoDM-GeV-cm3", type=float, default=RHO_DM_GEV_CM3_DEFAULT)
    parser.add_argument("--g2", type=float, default=1.0)
    parser.add_argument("--v0-km-s", type=float, default=V0_KM_S_DEFAULT)
    parser.add_argument("--ve-km-s", type=float, default=VE_KM_S_DEFAULT)
    parser.add_argument("--vesc-km-s", type=float, default=VESC_KM_S_DEFAULT)
    parser.add_argument("--nv", type=int, default=32)
    parser.add_argument("--nw", type=int, default=8)
    parser.add_argument("--nz", type=int, default=8)
    parser.add_argument("--nphi", type=int, default=4)
    parser.add_argument("--nv-low", type=int, default=16)
    parser.add_argument("--nw-high", type=int, default=16)
    parser.add_argument("--nz-high", type=int, default=16)
    parser.add_argument("--nphi-high", type=int, default=8)
    parser.add_argument("--max-relative-check", type=float, default=5.0e-3)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
