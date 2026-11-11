#!/usr/bin/env python3
"""Halo-fold the isotope-specific natural-xenon three-body rate.

Two explicitly separated halo prescriptions are evaluated:
  * mb_untruncated: the untruncated Maxwell-Boltzmann DMFormFactor default;
  * shm_cutoff: the standard truncated Maxwellian with v_esc=544 km/s.

The nuclear response, three-body kernel, mediator mass and width assumptions
remain explicit. This is a theory rate before detector efficiencies/resolution.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import eq6_kernel  # noqa: E402
from joint_xe131 import load_nuclear_response  # noqa: E402
from isotope_mass_schemes import isotope_mass_GeV as isotope_mass_with_scheme  # noqa: E402
from rate_kinematics import vmin_three_body_km_s  # noqa: E402
from run_natural_xenon_joint import AVAILABLE, MODELS, NATURAL_ABUNDANCE  # noqa: E402

C_KM_S = 299_792.458
C_CM_S = 2.99792458e10
RHO_DM_GEV_CM3_DEFAULT = 0.3
V0_KM_S_DEFAULT = 220.0
VE_KM_S_DEFAULT = 232.0
VESC_KM_S_DEFAULT = 544.0
UNTRUNCATED_VMAX_KM_S_DEFAULT = 1600.0
NIST_XE_STANDARD_ATOMIC_WEIGHT_G_MOL = 131.293
AVOGADRO = 6.02214076e23
GEV2_TO_CM2 = 0.3893793721e-27


def mb_untruncated_pdf(v: float, v0: float, ve: float) -> float:
    """Normalized untruncated lab-frame Maxwell-Boltzmann speed PDF, per km/s."""
    if v < 0.0:
        return 0.0
    return (
        v / (math.sqrt(math.pi) * v0 * ve)
        * (
            math.exp(-((v - ve) / v0) ** 2)
            - math.exp(-((v + ve) / v0) ** 2)
        )
    )


def shm_truncated_pdf(v: float, v0: float, ve: float, vesc: float) -> float:
    """Normalized lab-frame speed PDF for a Galactic-frame truncated SHM."""
    vmax = vesc + ve
    if v < 0.0 or v > vmax:
        return 0.0
    z = vesc / v0
    normalization = math.erf(z) - 2.0 * z / math.sqrt(math.pi) * math.exp(-z * z)
    if normalization <= 0.0:
        raise ValueError("invalid truncated-halo normalization")
    if v < vesc - ve:
        bracket = (
            math.exp(-((v - ve) / v0) ** 2)
            - math.exp(-((v + ve) / v0) ** 2)
        )
    else:
        bracket = math.exp(-((v - ve) / v0) ** 2) - math.exp(-z * z)
    return v * bracket / (math.sqrt(math.pi) * v0 * ve * normalization)


def halo_pdf(v: float, model: str, v0: float, ve: float, vesc: float) -> float:
    if model == "mb_untruncated":
        return mb_untruncated_pdf(v, v0, ve)
    if model == "shm_cutoff":
        return shm_truncated_pdf(v, v0, ve, vesc)
    raise ValueError(f"unknown halo model: {model}")


def speed_nodes(vmin: float, vmax: float, n: int) -> tuple[np.ndarray, np.ndarray]:
    if n < 2:
        raise ValueError("speed quadrature order must be >=2")
    if vmax <= vmin:
        return np.empty(0), np.empty(0)
    x, w = leggauss(n)
    return (
        0.5 * (vmax + vmin) + 0.5 * (vmax - vmin) * x,
        0.5 * (vmax - vmin) * w,
    )


def mean_target_number_per_kg() -> float:
    """Number of natural-xenon atoms per kg using the NIST standard atomic weight."""
    return AVOGADRO * 1000.0 / NIST_XE_STANDARD_ATOMIC_WEIGHT_G_MOL


def rate_conversion_factor(rho_dm: float, mchi: float) -> float:
    """Multiply a halo-folded GeV^-3 spectrum by this for events/(kg day keV)."""
    n_chi_cm3 = rho_dm / mchi
    return (
        n_chi_cm3
        * C_CM_S
        * mean_target_number_per_kg()
        * GEV2_TO_CM2
        * 1.0e-6
        * 86400.0
    )


def compute_isotope_halo_integrals(
    *,
    A: int,
    ER_keV: float,
    halo_model: str,
    mass_scheme: str,
    nv: int,
    mchi: float,
    ms: float,
    delta_m: float,
    speed_v0: float,
    speed_ve: float,
    speed_vesc: float,
    untruncated_vmax: float,
    coupling_product_sq: float,
    response_dir: Path,
    nw: int,
    nz: int,
    nphi: int,
    width_scheme: str = "zero",
    g2: float | None = None,
    response_cache: dict | None = None,
) -> list[dict]:
    """Compute both nuclear models while evaluating the shared I6 only once.

    J_A = integral dv f_lab(v) beta C_A(v), with units GeV.
    """
    mA = isotope_mass_with_scheme(A, mass_scheme)
    ER = ER_keV * 1.0e-6
    vmin = vmin_three_body_km_s(mchi, ms, mA, ER)
    vmax = (
        speed_vesc + speed_ve
        if halo_model == "shm_cutoff"
        else untruncated_vmax
    )
    responses = {}
    if response_cache is None:
        response_cache = {}
    for model in MODELS:
        cache_key = (str(response_dir.resolve()), int(A), model)
        if cache_key not in response_cache:
            response_path = response_dir / f"xe{A}_{model.upper()}_WM.csv"
            response_cache[cache_key] = load_nuclear_response(response_path, A, model)
        response = response_cache[cache_key]
        R_A, q_response = response.at_recoil(ER, mA)
        responses[model] = (R_A, q_response)

    if vmin >= vmax:
        return [{
            "A": A,
            "mass_scheme": mass_scheme,
            "model": model.upper(),
            "halo_model": halo_model,
            "ER_keV": ER_keV,
            "abundance": NATURAL_ABUNDANCE[A],
            "mA_GeV": mA,
            "R_A": responses[model][0],
            "q_response_GeV": responses[model][1],
            "vmin_km_s": vmin,
            "vmax_km_s": vmax,
            "speed_phase_space_open": False,
            "nv": nv,
            "J_A_GeV": 0.0,
            "width_scheme": width_scheme,
            "g2": g2,
        } for model in MODELS]

    velocities, weights = speed_nodes(vmin, vmax, nv)
    common_integral = 0.0
    for v, weight in zip(velocities, weights):
        pdf = halo_pdf(float(v), halo_model, speed_v0, speed_ve, speed_vesc)
        if pdf == 0.0:
            continue
        beta = float(v) / C_KM_S
        pchi = mchi * beta / math.sqrt(1.0 - beta * beta)
        I6 = eq6_kernel.reduced_kernel(
            mchi,
            ms,
            delta_m,
            mA,
            ER,
            float(v),
            nw=nw,
            nz=nz,
            nphi=nphi,
            width_scheme=width_scheme,
            g2=g2,
        )
        common_prefactor = (
            mA * coupling_product_sq
            / (256.0 * math.pi**3 * pchi**2)
            * I6
        )
        common_integral += float(weight) * pdf * beta * common_prefactor

    rows = []
    for model in MODELS:
        R_A, q_response = responses[model]
        rows.append({
            "A": A,
            "model": model.upper(),
            "halo_model": halo_model,
            "ER_keV": ER_keV,
            "abundance": NATURAL_ABUNDANCE[A],
            "mA_GeV": mA,
            "R_A": R_A,
            "q_response_GeV": q_response,
            "vmin_km_s": vmin,
            "vmax_km_s": vmax,
            "speed_phase_space_open": True,
            "nv": nv,
            "J_A_GeV": common_integral * R_A,
            "width_scheme": width_scheme,
            "g2": g2,
        })
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows to write: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--response-dir", type=Path,
                        default=HERE / "results" / "anand_wm_response")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--mass-scheme", choices=("A_u", "nist_nuclear"), default="A_u")
    parser.add_argument("--mchi-GeV", type=float, default=1000.0)
    parser.add_argument("--ms-MeV", type=float, default=0.3)
    parser.add_argument("--delta-m-MeV", type=float, default=1.0)
    parser.add_argument("--coupling-product-sq", type=float, default=1.0e-8)
    parser.add_argument("--rhoDM-GeV-cm3", type=float, default=RHO_DM_GEV_CM3_DEFAULT)
    parser.add_argument("--ER-keV", type=float, nargs="+",
                        default=[101.0, 200.0, 267.0, 542.0])
    parser.add_argument("--mV-scan-GeV", type=float, nargs="+",
                        default=[0.05, 0.1, 0.2, 0.5, 1.0])
    parser.add_argument("--halo-models", nargs="+",
                        choices=("mb_untruncated", "shm_cutoff"),
                        default=["mb_untruncated", "shm_cutoff"])
    parser.add_argument("--v0-km-s", type=float, default=V0_KM_S_DEFAULT)
    parser.add_argument("--ve-km-s", type=float, default=VE_KM_S_DEFAULT)
    parser.add_argument("--vesc-km-s", type=float, default=VESC_KM_S_DEFAULT)
    parser.add_argument("--untruncated-vmax-km-s", type=float,
                        default=UNTRUNCATED_VMAX_KM_S_DEFAULT)
    parser.add_argument("--nv-orders", type=int, nargs="+", default=[16, 32])
    parser.add_argument("--nw", type=int, default=16)
    parser.add_argument("--nz", type=int, default=16)
    parser.add_argument("--nphi", type=int, default=8)
    parser.add_argument("--width-scheme", choices=("zero", "pole", "running"), default="zero")
    parser.add_argument("--g2", type=float, default=None,
                        help="Separate chi2-chi1-s coupling for conditional pole/running width")
    parser.add_argument("--max-relative-convergence", type=float, default=5.0e-3)
    parser.add_argument("--response-q-convention", choices=("exact_spatial",), default="exact_spatial",
                        help="The AFH/GCN/JJ55 response uses the exact spatial momentum q=sqrt(2*m_A*E_R+E_R^2).")
    args = parser.parse_args()

    if args.width_scheme in ("pole", "running") and args.g2 is None:
        parser.error("--g2 is required when --width-scheme is pole or running")
    if args.g2 is not None and (not math.isfinite(args.g2) or args.g2 < 0.0):
        parser.error("--g2 must be finite and non-negative")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    response_cache: dict = {}
    ms = args.ms_MeV * 1.0e-3
    delta_m = args.delta_m_MeV * 1.0e-3
    abundance_coverage = sum(NATURAL_ABUNDANCE[A] for A in AVAILABLE)
    rate_factor = rate_conversion_factor(args.rhoDM_GeV_cm3, args.mchi_GeV)

    isotope_rows: list[dict] = []
    natural_rows: list[dict] = []
    intermediate: dict[tuple, dict] = {}

    for halo_model in args.halo_models:
        for nv in args.nv_orders:
            for A in AVAILABLE:
                for ER_keV in args.ER_keV:
                    rows = compute_isotope_halo_integrals(
                        A=A,
                        ER_keV=ER_keV,
                        halo_model=halo_model,
                        mass_scheme=args.mass_scheme,
                        nv=nv,
                        mchi=args.mchi_GeV,
                        ms=ms,
                        delta_m=delta_m,
                        speed_v0=args.v0_km_s,
                        speed_ve=args.ve_km_s,
                        speed_vesc=args.vesc_km_s,
                        untruncated_vmax=args.untruncated_vmax_km_s,
                        coupling_product_sq=args.coupling_product_sq,
                        response_dir=args.response_dir,
                        nw=args.nw,
                        nz=args.nz,
                        nphi=args.nphi,
                        width_scheme=args.width_scheme,
                        g2=args.g2,
                        response_cache=response_cache,
                    )
                    for row in rows:
                        isotope_rows.append(row)
                        intermediate[(halo_model, nv, A, ER_keV, row["model"])] = row

            for model in MODELS:
                for ER_keV in args.ER_keV:
                    for mV in args.mV_scan_GeV:
                        weighted_sigma_integral = 0.0
                        for A in AVAILABLE:
                            row = intermediate[(halo_model, nv, A, ER_keV, model.upper())]
                            denominator = (
                                mV * mV
                                + 2.0 * float(row["mA_GeV"]) * ER_keV * 1.0e-6
                            ) ** 2
                            weighted_sigma_integral += (
                                NATURAL_ABUNDANCE[A]
                                * float(row["J_A_GeV"])
                                / denominator
                            )
                        rate = rate_factor * weighted_sigma_integral
                        natural_rows.append({
                            "halo_model": halo_model,
                            "mass_scheme": args.mass_scheme,
                            "model": model.upper(),
                            "ER_keV": ER_keV,
                            "mV_GeV": mV,
                            "nv": nv,
                            "available_abundance_fraction": abundance_coverage,
                            "mean_xenon_atomic_weight_g_mol": NIST_XE_STANDARD_ATOMIC_WEIGHT_G_MOL,
                            "sum_xA_halo_integral_dsigma_GeVminus3": weighted_sigma_integral,
                            "rate_events_kg_day_keV": rate,
                            "rhoDM_GeV_cm3": args.rhoDM_GeV_cm3,
                            "detector_efficiency_resolution": "not applied",
                        })

    convergence_rows: list[dict] = []
    ordered_nv = sorted(set(args.nv_orders))
    if len(ordered_nv) >= 2:
        low_nv, high_nv = ordered_nv[-2], ordered_nv[-1]
        for halo_model in args.halo_models:
            for model in MODELS:
                for ER_keV in args.ER_keV:
                    for mV in args.mV_scan_GeV:
                        low = next(r for r in natural_rows if
                                   r["halo_model"] == halo_model and
                                   r["model"] == model.upper() and
                                   r["ER_keV"] == ER_keV and
                                   r["mV_GeV"] == mV and r["nv"] == low_nv)
                        high = next(r for r in natural_rows if
                                    r["halo_model"] == halo_model and
                                    r["model"] == model.upper() and
                                    r["ER_keV"] == ER_keV and
                                    r["mV_GeV"] == mV and r["nv"] == high_nv)
                        low_rate = float(low["rate_events_kg_day_keV"])
                        high_rate = float(high["rate_events_kg_day_keV"])
                        rel = (
                            abs(high_rate / low_rate - 1.0)
                            if low_rate > 0.0 else (0.0 if high_rate == 0.0 else math.inf)
                        )
                        convergence_rows.append({
                            "halo_model": halo_model,
                            "model": model.upper(),
                            "ER_keV": ER_keV,
                            "mV_GeV": mV,
                            "nv_low": low_nv,
                            "nv_high": high_nv,
                            "rate_low": low_rate,
                            "rate_high": high_rate,
                            "relative_difference": rel,
                        })
                        if rel > args.max_relative_convergence:
                            raise ArithmeticError(
                                f"speed quadrature not converged: {halo_model}, "
                                f"{model}, ER={ER_keV}, mV={mV}, rel={rel:.4g}"
                            )

    write_csv(args.out_dir / "isotope_halo_integrals.csv", isotope_rows)
    write_csv(args.out_dir / "natural_xenon_halo_rates.csv", natural_rows)
    if convergence_rows:
        write_csv(args.out_dir / "speed_quadrature_convergence.csv", convergence_rows)

    metadata = {
        "calculation": "natural-xenon isotope-specific halo-folded three-body rate",
        "available_isotopes": list(AVAILABLE),
        "omitted_isotopes": [124, 126],
        "available_natural_amount_fraction": abundance_coverage,
        "omitted_natural_amount_fraction": 1.0 - abundance_coverage,
        "abundance_source": "NIST isotopic amount fractions",
        "mean_target_mass_for_per_kg_normalization": "NIST standard atomic weight 131.293 g/mol",
        "mass_scheme": args.mass_scheme,
        "isotope_kinematic_mass": (
            "A * 0.93149410242 GeV" if args.mass_scheme == "A_u" else
            "(NIST relative atomic mass - 54 electron masses)*u; electronic binding energy neglected"
        ),
        "mchi_GeV": args.mchi_GeV,
        "ms_MeV": args.ms_MeV,
        "delta_m_MeV": args.delta_m_MeV,
        "coupling_product_sq": args.coupling_product_sq,
        "rhoDM_GeV_cm3": args.rhoDM_GeV_cm3,
        "v0_km_s": args.v0_km_s,
        "vE_km_s": args.ve_km_s,
        "vesc_km_s": args.vesc_km_s,
        "halo_models": {
            "mb_untruncated": {
                "definition": "DMFormFactor untruncated lab-frame Maxwell-Boltzmann speed PDF",
                "vmax_km_s": args.untruncated_vmax_km_s,
            },
            "shm_cutoff": {
                "definition": "Galactic Maxwellian truncated at vesc, boosted by vE",
                "vmax_lab_km_s": args.vesc_km_s + args.ve_km_s,
            },
        },
        "mV_scan_GeV": args.mV_scan_GeV,
        "mV_status": "exploratory scan; not specified by direct-detection figure captions",
        "width_scheme": args.width_scheme,
        "g2": args.g2,
        "width_interpretation": (
            "conditional Dirac pole/running width for chi2 -> chi1 s; assumes Dirac fermions, real scalar, pure scalar off-diagonal Yukawa, and no other open channels"
            if args.width_scheme in ("pole", "running") else "zero-width diagnostic"
        ),
        "response_q_convention": "exact spatial q=sqrt(2*m_A*E_R+E_R^2); same exact q used by the three-body nuclear recoil kinematics",
        "eq6_quadrature": {"nw": args.nw, "nz": args.nz, "nphi": args.nphi},
        "speed_quadrature_orders": args.nv_orders,
        "speed_convergence_tolerance": args.max_relative_convergence,
        "rate_units": "events / kg / day / keV",
        "rate_formula": (
            "(rhoDM/mchi)*c*(N_A*1000/131.293)*"
            "(0.3893793721e-27 cm2/GeV^-2)*(1e-6 GeV/keV)*86400 "
            "times sum_A x_A integral dv f_lab(v) beta d sigma_A/dER"
        ),
        "not_included": [
            "Xe-124 and Xe-126 response functions and their rate contributions",
            "detector efficiency, energy resolution, exposure and analysis cuts",
            "annual modulation and time-dependent Earth speed",
            "finite-width uncertainty and unspecified separate g2",
            "uncertainty propagation of halo parameters",
        ],
    }
    (args.out_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Natural xenon abundance coverage: {abundance_coverage:.8f}")
    print(f"Mean molar mass for per-kg normalization: {NIST_XE_STANDARD_ATOMIC_WEIGHT_G_MOL} g/mol")
    print(f"Rate conversion factor: {rate_factor:.8e}")
    for row in natural_rows:
        if row["nv"] == max(args.nv_orders):
            print(
                f"{row['halo_model']:14s} {row['model']:4s} "
                f"ER={row['ER_keV']:6.1f} keV mV={row['mV_GeV']:4.2f} GeV "
                f"rate={row['rate_events_kg_day_keV']:.8e} events/kg/day/keV"
            )
    if convergence_rows:
        worst = max(convergence_rows, key=lambda r: r["relative_difference"])
        print(
            "Worst speed quadrature difference: "
            f"{worst['relative_difference']:.3e} "
            f"({worst['halo_model']}, {worst['model']}, "
            f"ER={worst['ER_keV']} keV, mV={worst['mV_GeV']} GeV)"
        )


if __name__ == "__main__":
    main()
