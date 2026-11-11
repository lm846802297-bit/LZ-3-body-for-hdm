#!/usr/bin/env python3
"""AME2020/CODATA-2022 Xe-131 partial halo fold using the full AFH v6 response.

This computes only the Xe-131 isotope contribution to a natural-xenon target.
It is not the all-isotope natural-xenon rate: AFH response curves for the
other xenon isotopes are not archived with this branch.
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
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "figure2_full_reproduction"))

import eq6_kernel  # noqa: E402
from isotope_mass_schemes import (  # noqa: E402
    NIST_XE_ATOMIC_MASS_U,
    electron_binding_energy_eV,
    isotope_mass_GeV,
)
from rate_kinematics import vmin_three_body_km_s  # noqa: E402

A = 131
NATURAL_XE_ABUNDANCE_XE131 = 0.212324
NATURAL_XE_MEAN_ATOMIC_WEIGHT_G_MOL = 131.29276144787175
NATURAL_XE_ABUNDANCES = {
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
AVOGADRO = 6.02214076e23
C_KM_S = 299_792.458
C_CM_S = 2.99792458e10
GEV2_TO_CM2 = 0.3893793721e-27

BENCHMARKS = {
    "red_ms200_dm1": (200.0e-6, 1.0e-3),
    "green_ms300_dm1": (300.0e-6, 1.0e-3),
    "black_ms360_dm1": (360.0e-6, 1.0e-3),
    "blue_ms300_dm10": (300.0e-6, 10.0e-3),
}
CASES = [
    ("red_ms200_dm1", 101.0),
    ("green_ms300_dm1", 101.0),
    ("black_ms360_dm1", 101.0),
    ("blue_ms300_dm10", 101.0),
    ("green_ms300_dm1", 200.0),
    ("green_ms300_dm1", 267.0),
    ("green_ms300_dm1", 542.0),
]
HALO_MODELS = ("shm_cutoff", "mb_untruncated")
KERNEL_CHECK_CASES = (
    ("red_ms200_dm1", 101.0, "shm_cutoff"),
    ("green_ms300_dm1", 267.0, "shm_cutoff"),
    ("green_ms300_dm1", 542.0, "mb_untruncated"),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows to write: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_afh_response(path: Path):
    rows = read_csv(path)
    required = {"q_GeV", "R_equal_pn_normalized"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"AFH response table must contain {sorted(required)}")
    q = np.asarray([float(row["q_GeV"]) for row in rows], dtype=float)
    response = np.asarray(
        [float(row["R_equal_pn_normalized"]) for row in rows], dtype=float
    )
    if len(q) != 2401 or not np.all(np.diff(q) > 0.0):
        raise ValueError("Expected the complete monotonic 2401-point AFH q grid")
    if not np.isclose(q[0], 0.0, atol=1e-14) or not np.isclose(q[-1], 0.6, atol=1e-12):
        raise ValueError("Unexpected AFH response q-grid endpoints")
    if not np.isclose(response[0], A * A, rtol=0.0, atol=1e-7):
        raise ValueError("AFH physical equal-p/n response must satisfy R_A(0)=A^2")
    if np.any(response < 0.0) or not np.all(np.isfinite(response)):
        raise ValueError("AFH response contains invalid values")
    return PchipInterpolator(q, response, extrapolate=False), q, response


def mb_untruncated_pdf(v: float, v0: float, ve: float) -> float:
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
    vmax = vesc + ve
    if v < 0.0 or v >= vmax:
        return 0.0
    z = vesc / v0
    norm = math.erf(z) - 2.0 * z / math.sqrt(math.pi) * math.exp(-z * z)
    if v < vesc - ve:
        bracket = (
            math.exp(-((v - ve) / v0) ** 2)
            - math.exp(-((v + ve) / v0) ** 2)
        )
    else:
        bracket = math.exp(-((v - ve) / v0) ** 2) - math.exp(-z * z)
    return v * bracket / (math.sqrt(math.pi) * v0 * ve * norm)


def halo_pdf(v: float, model: str, v0: float, ve: float, vesc: float) -> float:
    if model == "shm_cutoff":
        return shm_truncated_pdf(v, v0, ve, vesc)
    if model == "mb_untruncated":
        return mb_untruncated_pdf(v, v0, ve)
    raise ValueError(f"unknown halo model: {model}")


def speed_nodes(vmin: float, vmax: float, n: int):
    if n < 2:
        raise ValueError("speed quadrature order must be >=2")
    if vmax <= vmin:
        return np.empty(0), np.empty(0)
    x, w = leggauss(n)
    return (
        0.5 * (vmax + vmin) + 0.5 * (vmax - vmin) * x,
        0.5 * (vmax - vmin) * w,
    )


def rate_factor(rho_dm: float, mchi: float) -> float:
    """Convert integral dv f(v) beta dσ/dER to events/(kg day keV)."""
    target_atoms_per_kg = (
        AVOGADRO * 1000.0 / NATURAL_XE_MEAN_ATOMIC_WEIGHT_G_MOL
    )
    return (
        (rho_dm / mchi)
        * C_CM_S
        * target_atoms_per_kg
        * GEV2_TO_CM2
        * 1.0e-6
        * 86400.0
    )


def compute_partial_rate(
    *,
    benchmark: str,
    er_keV: float,
    halo_model: str,
    nv: int,
    nw: int,
    nz: int,
    nphi: int,
    response_interp,
    mchi: float,
    mV: float,
    coupling_product_sq: float,
    g2: float,
    rho_dm: float,
    v0: float,
    ve: float,
    vesc: float,
    untruncated_vmax: float,
) -> dict:
    ms, delta_m = BENCHMARKS[benchmark]
    mA = isotope_mass_GeV(A, "ame2020_nuclear")
    ER = er_keV * 1.0e-6

    # Keep the manuscript's AFH response momentum and exact kinematic q distinct.
    q_response_NR = math.sqrt(2.0 * mA * ER)
    q_kin_exact = math.sqrt(2.0 * mA * ER + ER * ER)
    # The AFH response is a function of the physical three-momentum transfer.
    # Use the exact elastic target mass shell, consistently with Eq. (6) limits
    # and the natural-xenon halo-fold convention; retain q_NR as a diagnostic.
    q_response = q_kin_exact
    if q_response < 0.0 or q_response > 0.6:
        raise ValueError(f"AFH q={q_response} GeV is outside the archived grid")
    R_A = float(response_interp(q_response))
    if not math.isfinite(R_A) or R_A < 0.0:
        raise ArithmeticError(f"invalid AFH response at q={q_response}")

    vmin = vmin_three_body_km_s(mchi, ms, mA, ER)
    vmax = vesc + ve if halo_model == "shm_cutoff" else untruncated_vmax
    if vmin >= vmax:
        integral = 0.0
        open_support = False
    else:
        velocities, weights = speed_nodes(vmin, vmax, nv)
        integral = 0.0
        for v, weight in zip(velocities, weights):
            v = float(v)
            pdf = halo_pdf(v, halo_model, v0, ve, vesc)
            if pdf == 0.0:
                continue
            beta = v / C_KM_S
            pchi = mchi * beta / math.sqrt(1.0 - beta * beta)
            I6 = eq6_kernel.reduced_kernel(
                mchi,
                ms,
                delta_m,
                mA,
                ER,
                v,
                nw=nw,
                nz=nz,
                nphi=nphi,
                width_scheme="pole",
                g2=g2,
            )
            denominator = (mV * mV + 2.0 * mA * ER) ** 2
            dsigma = (
                mA * coupling_product_sq * R_A * I6
                / (256.0 * math.pi**3 * pchi**2 * denominator)
            )
            integral += float(weight) * pdf * beta * dsigma
        open_support = True

    # This is the Xe-131 term in a natural-xenon target, not the total rate.
    partial_rate = (
        rate_factor(rho_dm, mchi)
        * NATURAL_XE_ABUNDANCE_XE131
        * integral
    )
    return {
        "benchmark": benchmark,
        "ER_keV": er_keV,
        "halo_model": halo_model,
        "mass_scheme": "NIST atomic masses + AME2020 electron binding + CODATA2022",
        "A": A,
        "natural_atom_fraction_Xe131": NATURAL_XE_ABUNDANCE_XE131,
        "mA_GeV": mA,
        "q_response_used_GeV": q_response_NR,
        "q_response_NR_GeV": q_response_NR,
        "q_kinematics_exact_GeV": q_kin_exact,
        "R_A_AFH_equal_pn": R_A,
        "vmin_km_s": vmin,
        "vmax_km_s": vmax,
        "speed_support_open": open_support,
        "nv": nv,
        "kernel_quadrature": f"{nw}x{nz}x{nphi}",
        "width_scheme": "pole",
        "g2": g2,
        "speed_integral_dsigma_GeVminus3": integral,
        "Xe131_partial_rate_events_kg_day_keV": partial_rate,
    }


def relative_difference(a: float, b: float) -> float:
    if a == 0.0 and b == 0.0:
        return 0.0
    if a == 0.0:
        return math.inf
    return abs(b / a - 1.0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--response-csv",
        type=Path,
        default=HERE / "output" / "afh_default_xe131_WM00.csv",
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--mchi-GeV", type=float, default=1000.0)
    parser.add_argument("--mV-GeV", type=float, default=10.0)
    parser.add_argument("--coupling-product-sq", type=float, default=1.0e-8)
    parser.add_argument("--g2", type=float, default=1.0)
    parser.add_argument("--rhoDM-GeV-cm3", type=float, default=0.3)
    parser.add_argument("--v0-km-s", type=float, default=220.0)
    parser.add_argument("--ve-km-s", type=float, default=232.0)
    parser.add_argument("--vesc-km-s", type=float, default=544.0)
    parser.add_argument("--untruncated-vmax-km-s", type=float, default=1600.0)
    parser.add_argument("--nv-orders", type=int, nargs="+", default=[16, 32])
    parser.add_argument("--nw", type=int, default=8)
    parser.add_argument("--nz", type=int, default=8)
    parser.add_argument("--nphi", type=int, default=4)
    parser.add_argument("--max-relative-speed-convergence", type=float, default=5.0e-3)
    parser.add_argument("--max-relative-kernel-convergence", type=float, default=5.0e-3)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    response_interp, q_grid, response_grid = load_afh_response(args.response_csv)

    # Archive the full NIST -> nuclear-mass conversion table, including isotopes
    # for which an AFH response curve is not currently available.
    binding_eV = electron_binding_energy_eV(54)
    mass_rows = []
    for isotope_A, abundance in NATURAL_XE_ABUNDANCES.items():
        m_A_u = NIST_XE_ATOMIC_MASS_U[isotope_A]
        m_A_au = isotope_A * 0.93149410242
        m_A_nist = isotope_mass_GeV(isotope_A, "nist_nuclear")
        m_A_ame = isotope_mass_GeV(isotope_A, "ame2020_nuclear")
        vmin_101 = vmin_three_body_km_s(
            args.mchi_GeV, 300.0e-6, m_A_ame, 101.0e-6
        )
        mass_rows.append({
            "A": isotope_A,
            "isotope": f"Xe-{isotope_A}",
            "natural_atom_fraction": abundance,
            "atomic_mass_u_NIST": m_A_u,
            "electron_binding_energy_keV": binding_eV * 1.0e-3,
            "mA_Au_GeV_legacy": m_A_au,
            "mA_NIST_nuclear_GeV": m_A_nist,
            "mA_AME2020_CODATA2022_GeV": m_A_ame,
            "delta_AME2020_vs_NIST_keV": (m_A_ame - m_A_nist) * 1.0e6,
            "delta_AME2020_vs_Au_keV": (m_A_ame - m_A_au) * 1.0e6,
            "vmin_at_ER101keV_ms300_km_s": vmin_101,
            "AFH_default_response_available": isotope_A == A,
        })
    write_csv(args.out_dir / "xenon_isotope_ame2020_masses.csv", mass_rows)

    all_rows = []
    by_key = {}
    for nv in sorted(set(args.nv_orders)):
        for benchmark, er_keV in CASES:
            for halo_model in HALO_MODELS:
                row = compute_partial_rate(
                    benchmark=benchmark,
                    er_keV=er_keV,
                    halo_model=halo_model,
                    nv=nv,
                    nw=args.nw,
                    nz=args.nz,
                    nphi=args.nphi,
                    response_interp=response_interp,
                    mchi=args.mchi_GeV,
                    mV=args.mV_GeV,
                    coupling_product_sq=args.coupling_product_sq,
                    g2=args.g2,
                    rho_dm=args.rhoDM_GeV_cm3,
                    v0=args.v0_km_s,
                    ve=args.ve_km_s,
                    vesc=args.vesc_km_s,
                    untruncated_vmax=args.untruncated_vmax_km_s,
                )
                all_rows.append(row)
                by_key[(benchmark, er_keV, halo_model, nv)] = row

    speed_checks = []
    nv_orders = sorted(set(args.nv_orders))
    if len(nv_orders) >= 2:
        low_nv, high_nv = nv_orders[-2], nv_orders[-1]
        for benchmark, er_keV in CASES:
            for halo_model in HALO_MODELS:
                low = by_key[(benchmark, er_keV, halo_model, low_nv)]
                high = by_key[(benchmark, er_keV, halo_model, high_nv)]
                rel = relative_difference(
                    low["Xe131_partial_rate_events_kg_day_keV"],
                    high["Xe131_partial_rate_events_kg_day_keV"],
                )
                speed_checks.append({
                    "benchmark": benchmark,
                    "ER_keV": er_keV,
                    "halo_model": halo_model,
                    "nv_low": low_nv,
                    "nv_high": high_nv,
                    "rate_low": low["Xe131_partial_rate_events_kg_day_keV"],
                    "rate_high": high["Xe131_partial_rate_events_kg_day_keV"],
                    "relative_difference": rel,
                })
                if rel > args.max_relative_speed_convergence:
                    raise ArithmeticError(
                        f"speed quadrature failed: {benchmark}, ER={er_keV}, "
                        f"{halo_model}, rel={rel:.4g}"
                    )

    kernel_checks = []
    high_nv = max(nv_orders)
    for benchmark, er_keV, halo_model in KERNEL_CHECK_CASES:
        base = by_key[(benchmark, er_keV, halo_model, high_nv)]
        high_order = compute_partial_rate(
            benchmark=benchmark,
            er_keV=er_keV,
            halo_model=halo_model,
            nv=high_nv,
            nw=16,
            nz=16,
            nphi=8,
            response_interp=response_interp,
            mchi=args.mchi_GeV,
            mV=args.mV_GeV,
            coupling_product_sq=args.coupling_product_sq,
            g2=args.g2,
            rho_dm=args.rhoDM_GeV_cm3,
            v0=args.v0_km_s,
            ve=args.ve_km_s,
            vesc=args.vesc_km_s,
            untruncated_vmax=args.untruncated_vmax_km_s,
        )
        rel = relative_difference(
            base["Xe131_partial_rate_events_kg_day_keV"],
            high_order["Xe131_partial_rate_events_kg_day_keV"],
        )
        kernel_checks.append({
            "benchmark": benchmark,
            "ER_keV": er_keV,
            "halo_model": halo_model,
            "low_kernel": base["kernel_quadrature"],
            "high_kernel": "16x16x8",
            "rate_low": base["Xe131_partial_rate_events_kg_day_keV"],
            "rate_high": high_order["Xe131_partial_rate_events_kg_day_keV"],
            "relative_difference": rel,
        })
        if rel > args.max_relative_kernel_convergence:
            raise ArithmeticError(
                f"kernel quadrature failed: {benchmark}, ER={er_keV}, "
                f"{halo_model}, rel={rel:.4g}"
            )

    write_csv(args.out_dir / "xe131_partial_halo_rates.csv", all_rows)
    if speed_checks:
        write_csv(args.out_dir / "speed_quadrature_convergence.csv", speed_checks)
    if kernel_checks:
        write_csv(args.out_dir / "kernel_quadrature_convergence.csv", kernel_checks)

    mass = isotope_mass_GeV(A, "ame2020_nuclear")
    metadata = {
        "calculation": "AME2020/CODATA2022 Xe-131 partial contribution to natural-xenon halo-folded three-body rate",
        "scope": "Xe-131 isotope term only; not the total natural-xenon rate",
        "mass_scheme": {
            "atomic_mass_source": "NIST Atomic Weights and Isotopic Compositions for Xenon",
            "nuclear_conversion": "M_nucleus = M_neutral_atom - Z*m_e + B_e(Z)",
            "electron_binding_energy_source": "AME2020 atomic mass evaluation, Eq. (2)",
            "electron_binding_energy_formula_eV": "14.4381*Z^2.39 + 1.55468e-6*Z^5.35",
            "electron_binding_energy_Xe_keV": binding_eV * 1.0e-3,
            "isotope_mass_table": "xenon_isotope_ame2020_masses.csv",
            "natural_isotope_abundance_sum": sum(NATURAL_XE_ABUNDANCES.values()),
            "constants": "CODATA 2022",
            "u_c2_MeV": 931.49410372,
            "electron_mass_c2_MeV": 0.51099895069,
            "mA_Xe131_GeV": mass,
        },
        "AFH": {
            "source": "DMFormFactor v6.0 built-in sdgXe131, 67 density-matrix entries",
            "response_file": str(args.response_csv),
            "response_grid_points": int(len(q_grid)),
            "q_grid_GeV": [float(q_grid[0]), float(q_grid[-1]), float(q_grid[1]-q_grid[0])],
            "response_normalization": "R_equal_pn(q)=A^2*R_AFH_raw(q)/R_AFH_raw(0); R_equal_pn(0)=A^2",
            "oscillator_length": "AFH default b_A prescription; unchanged",
            "response_momentum": "q_response=sqrt(2*mA*ER), as defined by y=b_A^2*mA*ER/2 in the manuscript",
            "kinematic_momentum": "q_kin=sqrt(2*mA*ER+ER^2), exact target mass shell in three-body limits",
            "extrapolation": False,
        },
        "dark_sector": {
            "mchi1_GeV": args.mchi_GeV,
            "mV_GeV": args.mV_GeV,
            "ms_Delta_m_by_benchmark": {
                name: {"ms_keV": vals[0]*1.0e6, "Delta_m_MeV": vals[1]*1.0e3}
                for name, vals in BENCHMARKS.items()
            },
            "coupling_product_squared": args.coupling_product_sq,
            "g2": args.g2,
            "width": "pole width for chi2 -> chi1 s; conditional on Dirac chi2, real scalar, pure scalar off-diagonal Yukawa, and no other open channels",
        },
        "halo": {
            "baseline": "truncated SHM",
            "v0_km_s": args.v0_km_s,
            "vE_km_s": args.ve_km_s,
            "vesc_km_s": args.vesc_km_s,
            "vmax_lab_km_s": args.vesc_km_s + args.ve_km_s,
            "alternative": "untruncated boosted Maxwell-Boltzmann tail diagnostic",
            "untruncated_numerical_vmax_km_s": args.untruncated_vmax_km_s,
        },
        "natural_xenon_weighting": {
            "Xe131_natural_atom_fraction": NATURAL_XE_ABUNDANCE_XE131,
            "mean_atomic_weight_g_mol": NATURAL_XE_MEAN_ATOMIC_WEIGHT_G_MOL,
            "interpretation": "Xe-131 term per kg of natural xenon; all other isotope terms omitted",
        },
        "quadrature": {
            "speed_orders": sorted(set(args.nv_orders)),
            "kernel_baseline": [args.nw, args.nz, args.nphi],
            "kernel_crosscheck": [16, 16, 8],
            "max_relative_speed_difference": max(
                [row["relative_difference"] for row in speed_checks], default=0.0
            ),
            "max_relative_kernel_difference": max(
                [row["relative_difference"] for row in kernel_checks], default=0.0
            ),
        },
        "rate_units": "events/(kg day keV)",
        "not_included": [
            "Xe-124, Xe-126, Xe-128, Xe-129, Xe-130, Xe-132, Xe-134, Xe-136 rate terms",
            "detector efficiency, resolution, exposure, cuts, backgrounds, and likelihood",
            "native Mathematica re-execution of AFH v6.0",
        ],
    }
    (args.out_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Xe-131 AME2020/CODATA2022 nuclear mass: {mass:.12f} GeV")
    for row in all_rows:
        if row["nv"] == high_nv:
            print(
                f"{row['benchmark']:18s} ER={row['ER_keV']:6.1f} "
                f"{row['halo_model']:14s} "
                f"rate={row['Xe131_partial_rate_events_kg_day_keV']:.8e} "
                f"vmin={row['vmin_km_s']:.3f} km/s"
            )
    print(
        "Max speed-grid difference: "
        f"{metadata['quadrature']['max_relative_speed_difference']:.3e}"
    )
    print(
        "Max kernel-grid difference: "
        f"{metadata['quadrature']['max_relative_kernel_difference']:.3e}"
    )


if __name__ == "__main__":
    main()
