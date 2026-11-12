#!/usr/bin/env python3
"""Seven-isotope AFH v6.0 natural-xenon halo fold with AME2020 nuclear masses.

The adopted AFH central prediction contains the seven isotopes for which the
v6.0 package supplies default density matrices. Xe-124 and Xe-126 are not
silently set to zero or renormalized away: a separate coherent A^2 ceiling
quantifies their maximum possible contribution under the equal-p/n one-body
charge-response assumption.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE.parent / "figure2_full_reproduction"))

import eq6_kernel  # noqa: E402
from isotope_mass_schemes import (  # noqa: E402
    AME2020_XE_ATOMIC_MASS_U,
    NIST_XE_ATOMIC_MASS_U,
    isotope_mass_GeV,
)
from rate_kinematics import vmin_three_body_km_s  # noqa: E402

AFH_ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
MISSING_ISOTOPES = (124, 126)
MASS_SCHEMES = ("nist_nuclear", "ame2020_nuclear")

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
CASES = (
    ("red_ms200_dm1", 101.0),
    ("green_ms300_dm1", 101.0),
    ("black_ms360_dm1", 101.0),
    ("blue_ms300_dm10", 101.0),
    ("green_ms300_dm1", 200.0),
    ("green_ms300_dm1", 267.0),
    ("green_ms300_dm1", 542.0),
)
HALO_MODELS = ("shm_cutoff", "mb_untruncated")
KERNEL_CHECK_CASES = (
    ("red_ms200_dm1", 101.0, "shm_cutoff"),
    ("green_ms300_dm1", 267.0, "shm_cutoff"),
    ("green_ms300_dm1", 542.0, "mb_untruncated"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_abundances(path: Path) -> dict[int, float]:
    rows = read_csv(path)
    abundance = {int(row["A"]): float(row["natural_atom_fraction"]) for row in rows}
    if set(abundance) != set(range(124, 137, 1)) - {125, 127, 133, 135}:
        expected = {124, 126, 128, 129, 130, 131, 132, 134, 136}
        if set(abundance) != expected:
            raise ValueError(f"Unexpected xenon isotope set in {path}: {sorted(abundance)}")
    if not math.isclose(sum(abundance.values()), 1.0, rel_tol=0.0, abs_tol=2.0e-6):
        raise ValueError("Natural xenon atom fractions do not sum to unity")
    return abundance


def load_afh_responses(path: Path):
    rows = read_csv(path)
    required = {"A", "q_GeV", "R_equal_pn_normalized"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"AFH response grid must contain {sorted(required)}")
    grouped: dict[int, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(int(row["A"]), []).append(row)
    if set(grouped) != set(AFH_ISOTOPES):
        raise ValueError(
            f"AFH response grid isotope set mismatch: {sorted(grouped)}"
        )

    interpolators = {}
    metadata = {}
    for A in AFH_ISOTOPES:
        isotope_rows = grouped[A]
        q = np.asarray([float(row["q_GeV"]) for row in isotope_rows], dtype=float)
        response = np.asarray(
            [float(row["R_equal_pn_normalized"]) for row in isotope_rows],
            dtype=float,
        )
        if len(q) != 2401 or not np.all(np.diff(q) > 0.0):
            raise ValueError(f"Xe-{A} must have a monotonic 2401-node q grid")
        if not math.isclose(q[0], 0.0, abs_tol=1e-14):
            raise ValueError(f"Xe-{A} q grid does not start at zero")
        if not math.isclose(q[-1], 0.6, abs_tol=1e-12):
            raise ValueError(f"Xe-{A} q grid does not end at 0.6 GeV")
        if not math.isclose(response[0], A * A, rel_tol=0.0, abs_tol=1e-7):
            raise ValueError(f"Xe-{A} response does not satisfy R_A(0)=A^2")
        if np.any(~np.isfinite(response)) or np.any(response < 0.0):
            raise ValueError(f"Xe-{A} response has invalid values")
        max_ratio = float(np.max(response / (A * A)))
        if max_ratio > 1.0 + 1.0e-3:
            raise ValueError(
                f"Xe-{A} normalized coherent response exceeds A^2 by more than "
                f"the 0.1% numerical tolerance: max ratio={max_ratio:.8g}"
            )
        interpolators[A] = PchipInterpolator(q, response, extrapolate=False)
        metadata[A] = {
            "grid_points": len(q),
            "q_min_GeV": float(q[0]),
            "q_max_GeV": float(q[-1]),
            "q_step_GeV": float(q[1] - q[0]),
            "R_A_q0": float(response[0]),
            "max_R_over_A2": max_ratio,
        }
    return interpolators, metadata


def mean_atomic_weight_g_mol(abundances: dict[int, float], mass_scheme: str) -> float:
    if mass_scheme == "nist_nuclear":
        atomic_masses = NIST_XE_ATOMIC_MASS_U
    elif mass_scheme == "ame2020_nuclear":
        atomic_masses = AME2020_XE_ATOMIC_MASS_U
    else:
        raise ValueError(f"Unsupported mass scheme: {mass_scheme}")
    return sum(abundances[A] * atomic_masses[A] for A in abundances)


def target_rate_factor(rho_dm: float, mchi: float, mean_atomic_weight: float) -> float:
    """Convert integral dv f(v) beta dσ/dER to events/(kg day keV)."""
    target_atoms_per_kg = AVOGADRO * 1000.0 / mean_atomic_weight
    return (
        (rho_dm / mchi)
        * C_CM_S
        * target_atoms_per_kg
        * GEV2_TO_CM2
        * 1.0e-6
        * 86400.0
    )


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
    raise ValueError(f"Unknown halo model: {model}")


def speed_nodes(vmin: float, vmax: float, n: int):
    if vmax <= vmin:
        return np.empty(0), np.empty(0)
    nodes, weights = leggauss(n)
    return (
        0.5 * (vmax + vmin) + 0.5 * (vmax - vmin) * nodes,
        0.5 * (vmax - vmin) * weights,
    )


def relative_difference(a: float, b: float) -> float:
    if a == 0.0 and b == 0.0:
        return 0.0
    if a == 0.0:
        return math.inf
    return abs(b / a - 1.0)


def isotope_rate(
    *,
    A: int,
    abundance: float,
    mA: float,
    response_value: float,
    response_model: str,
    benchmark: str,
    er_keV: float,
    halo_model: str,
    mass_scheme: str,
    nv: int,
    nw: int,
    nz: int,
    nphi: int,
    rate_factor: float,
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
    ER = er_keV * 1.0e-6
    q_exact = math.sqrt(2.0 * mA * ER + ER * ER)
    if not math.isfinite(response_value) or response_value < 0.0:
        raise ArithmeticError(f"Invalid R_A for Xe-{A}: {response_value}")

    vmin = vmin_three_body_km_s(mchi, ms, mA, ER)
    vmax = vesc + ve if halo_model == "shm_cutoff" else untruncated_vmax
    integral = 0.0
    if vmin < vmax:
        velocities, weights = speed_nodes(vmin, vmax, nv)
        for velocity, weight in zip(velocities, weights):
            v = float(velocity)
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
            mediator_denominator = (mV * mV + 2.0 * mA * ER) ** 2
            dsigma_dER = (
                mA * coupling_product_sq * response_value * I6
                / (256.0 * math.pi**3 * pchi**2 * mediator_denominator)
            )
            integral += float(weight) * pdf * beta * dsigma_dER

    contribution = rate_factor * abundance * integral
    return {
        "benchmark": benchmark,
        "ER_keV": er_keV,
        "halo_model": halo_model,
        "mass_scheme": mass_scheme,
        "A": A,
        "isotope": f"Xe-{A}",
        "natural_atom_fraction": abundance,
        "AFH_response_model": response_model,
        "mA_GeV": mA,
        "q_exact_spatial_GeV": q_exact,
        "R_A": response_value,
        "vmin_km_s": vmin,
        "vmax_km_s": vmax,
        "open_support": vmin < vmax,
        "nv": nv,
        "kernel_quadrature": f"{nw}x{nz}x{nphi}",
        "speed_integral_dsigma_GeVminus3": integral,
        "rate_contribution_events_kg_day_keV": contribution,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--response-csv",
        type=Path,
        default=HERE / "output" / "afh_default_xenon_responses"
                / "afh_xe_isotope_responses.csv",
    )
    parser.add_argument(
        "--abundance-csv",
        type=Path,
        default=HERE / "input" / "natural_xenon_isotope_weights.csv",
    )
    parser.add_argument(
        "--nist-reference-csv",
        type=Path,
        default=HERE / "results" / "natural_xenon_halo_rates.csv",
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
    parser.add_argument("--nv-orders", type=int, nargs="+", default=[32, 64])
    parser.add_argument("--nw", type=int, default=8)
    parser.add_argument("--nz", type=int, default=8)
    parser.add_argument("--nphi", type=int, default=4)
    parser.add_argument("--max-relative-speed-convergence", type=float, default=5.0e-3)
    parser.add_argument("--max-relative-kernel-convergence", type=float, default=5.0e-3)
    parser.add_argument("--max-relative-nist-reproduction", type=float, default=5.0e-8)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    abundances = load_abundances(args.abundance_csv)
    response_interpolators, response_metadata = load_afh_responses(args.response_csv)
    nv_orders = sorted(set(args.nv_orders))
    if len(nv_orders) < 2:
        raise ValueError("At least two speed quadrature orders are required")
    low_nv, high_nv = nv_orders[-2], nv_orders[-1]

    mean_atomic_weights = {
        scheme: mean_atomic_weight_g_mol(abundances, scheme)
        for scheme in MASS_SCHEMES
    }
    rate_factors = {
        scheme: target_rate_factor(
            args.rhoDM_GeV_cm3, args.mchi_GeV, mean_atomic_weights[scheme]
        )
        for scheme in MASS_SCHEMES
    }

    contributions_high = []
    speed_checks = []
    summaries = []
    missing_ceiling_rows = []
    envelopes = []
    nist_reference = {
        (row["benchmark"], float(row["ER_keV"]), row["halo_model"]):
            float(row["rate_events_kg_day_keV"])
        for row in read_csv(args.nist_reference_csv)
    }

    for mass_scheme in MASS_SCHEMES:
        for benchmark, er_keV in CASES:
            for halo_model in HALO_MODELS:
                isotope_rows_by_nv = {}
                for nv in nv_orders:
                    rows_nv = []
                    for A in AFH_ISOTOPES:
                        mA = isotope_mass_GeV(A, mass_scheme)
                        ER = er_keV * 1.0e-6
                        q = math.sqrt(2.0 * mA * ER + ER * ER)
                        if q > 0.6:
                            raise ValueError(f"Xe-{A} q={q:.8g} GeV exceeds AFH grid")
                        response_value = float(response_interpolators[A](q))
                        row = isotope_rate(
                            A=A,
                            abundance=abundances[A],
                            mA=mA,
                            response_value=response_value,
                            response_model="AFH_v6_default",
                            benchmark=benchmark,
                            er_keV=er_keV,
                            halo_model=halo_model,
                            mass_scheme=mass_scheme,
                            nv=nv,
                            nw=args.nw,
                            nz=args.nz,
                            nphi=args.nphi,
                            rate_factor=rate_factors[mass_scheme],
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
                        rows_nv.append(row)
                    isotope_rows_by_nv[nv] = rows_nv

                low_total = sum(
                    row["rate_contribution_events_kg_day_keV"]
                    for row in isotope_rows_by_nv[low_nv]
                )
                high_total = sum(
                    row["rate_contribution_events_kg_day_keV"]
                    for row in isotope_rows_by_nv[high_nv]
                )
                rel_total = relative_difference(low_total, high_total)
                speed_checks.append({
                    "mass_scheme": mass_scheme,
                    "benchmark": benchmark,
                    "ER_keV": er_keV,
                    "halo_model": halo_model,
                    "nv_low": low_nv,
                    "nv_high": high_nv,
                    "rate_low": low_total,
                    "rate_high": high_total,
                    "relative_difference": rel_total,
                })
                for low, high in zip(isotope_rows_by_nv[low_nv], isotope_rows_by_nv[high_nv]):
                    speed_checks.append({
                        "mass_scheme": mass_scheme,
                        "benchmark": benchmark,
                        "ER_keV": er_keV,
                        "halo_model": halo_model,
                        "A": high["A"],
                        "nv_low": low_nv,
                        "nv_high": high_nv,
                        "rate_low": low["rate_contribution_events_kg_day_keV"],
                        "rate_high": high["rate_contribution_events_kg_day_keV"],
                        "relative_difference": relative_difference(
                            low["rate_contribution_events_kg_day_keV"],
                            high["rate_contribution_events_kg_day_keV"],
                        ),
                    })
                contributions_high.extend(isotope_rows_by_nv[high_nv])

                total_open_abundance = sum(
                    row["natural_atom_fraction"]
                    for row in isotope_rows_by_nv[high_nv]
                    if row["open_support"]
                )
                summary = {
                    "mass_scheme": mass_scheme,
                    "benchmark": benchmark,
                    "ER_keV": er_keV,
                    "halo_model": halo_model,
                    "mean_atomic_weight_g_mol": mean_atomic_weights[mass_scheme],
                    "available_AFH_abundance_coverage": sum(
                        abundances[A] for A in AFH_ISOTOPES
                    ),
                    "open_AFH_abundance_fraction": total_open_abundance,
                    "open_AFH_isotopes": ";".join(
                        str(row["A"]) for row in isotope_rows_by_nv[high_nv]
                        if row["open_support"]
                    ),
                    "AFH_7_isotope_rate_nv_low": low_total,
                    "AFH_7_isotope_rate_events_kg_day_keV": high_total,
                    "nv_low": low_nv,
                    "nv_high": high_nv,
                }

                # Xe-124 and Xe-126 have no AFH v6.0 default density matrices.
                # Use R_A=A^2 only as a coherent-charge ceiling, never as an
                # AFH central prediction or a replacement nuclear model.
                missing_rows = []
                for A in MISSING_ISOTOPES:
                    mA = isotope_mass_GeV(A, mass_scheme)
                    ceiling = float(A * A)
                    row = isotope_rate(
                        A=A,
                        abundance=abundances[A],
                        mA=mA,
                        response_value=ceiling,
                        response_model="coherent_A2_ceiling_not_AFH",
                        benchmark=benchmark,
                        er_keV=er_keV,
                        halo_model=halo_model,
                        mass_scheme=mass_scheme,
                        nv=high_nv,
                        nw=args.nw,
                        nz=args.nz,
                        nphi=args.nphi,
                        rate_factor=rate_factors[mass_scheme],
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
                    missing_rows.append(row)
                    missing_ceiling_rows.append(row)
                missing_ceiling_total = sum(
                    row["rate_contribution_events_kg_day_keV"]
                    for row in missing_rows
                )
                summary["missing_Xe124_Xe126_coherent_ceiling"] = missing_ceiling_total
                summary["nine_isotope_coherent_ceiling_total"] = (
                    high_total + missing_ceiling_total
                )
                summary["missing_ceiling_fraction_of_envelope"] = (
                    missing_ceiling_total / (high_total + missing_ceiling_total)
                    if high_total + missing_ceiling_total > 0.0 else 0.0
                )
                summaries.append(summary)
                envelopes.append({
                    "mass_scheme": mass_scheme,
                    "benchmark": benchmark,
                    "ER_keV": er_keV,
                    "halo_model": halo_model,
                    "AFH_7_isotope_central_rate": high_total,
                    "Xe124_Xe126_coherent_A2_ceiling": missing_ceiling_total,
                    "nine_isotope_upper_envelope_not_AFH_prediction":
                        high_total + missing_ceiling_total,
                    "AFH_abundance_coverage": sum(abundances[A] for A in AFH_ISOTOPES),
                    "missing_abundance": sum(abundances[A] for A in MISSING_ISOTOPES),
                })

    # The NIST-mass, 32-node fold must reproduce the already archived mainline
    # seven-isotope result before AME2020 is interpreted as a mass correction.
    nist_reproduction = []
    for row in summaries:
        if row["mass_scheme"] != "nist_nuclear":
            continue
        key = (row["benchmark"], row["ER_keV"], row["halo_model"])
        if key not in nist_reference:
            raise ValueError(f"Missing mainline NIST reference row: {key}")
        # The mainline reference used 32 speed nodes. Compare the matching
        # lower-order result, not the 64-node converged result.
        reference = nist_reference[key]
        low = row["AFH_7_isotope_rate_nv_low"]
        difference = relative_difference(reference, low)
        nist_reproduction.append({
            "benchmark": row["benchmark"],
            "ER_keV": row["ER_keV"],
            "halo_model": row["halo_model"],
            "reference_main_nist_rate_nv32": reference,
            "regenerated_nist_rate_nv32": low,
            "relative_difference": difference,
        })
    max_nist_difference = max(
        (row["relative_difference"] for row in nist_reproduction), default=0.0
    )
    if max_nist_difference > args.max_relative_nist_reproduction:
        raise ArithmeticError(
            "Regenerated NIST seven-isotope fold does not reproduce main: "
            f"maximum relative difference={max_nist_difference:.3e}"
        )

    # Kernel quadrature cross-check: all seven AFH isotopes at three
    # representative kinematic/halo anchors, using the AME2020 mass scheme.
    kernel_checks = []
    for benchmark, er_keV, halo_model in KERNEL_CHECK_CASES:
        for A in AFH_ISOTOPES:
            mA = isotope_mass_GeV(A, "ame2020_nuclear")
            q = math.sqrt(2.0 * mA * er_keV * 1.0e-6 + (er_keV * 1.0e-6) ** 2)
            response_value = float(response_interpolators[A](q))
            base = isotope_rate(
                A=A, abundance=abundances[A], mA=mA,
                response_value=response_value, response_model="AFH_v6_default",
                benchmark=benchmark, er_keV=er_keV, halo_model=halo_model,
                mass_scheme="ame2020_nuclear", nv=high_nv,
                nw=args.nw, nz=args.nz, nphi=args.nphi,
                rate_factor=rate_factors["ame2020_nuclear"],
                mchi=args.mchi_GeV, mV=args.mV_GeV,
                coupling_product_sq=args.coupling_product_sq, g2=args.g2,
                rho_dm=args.rhoDM_GeV_cm3, v0=args.v0_km_s,
                ve=args.ve_km_s, vesc=args.vesc_km_s,
                untruncated_vmax=args.untruncated_vmax_km_s,
            )
            high = isotope_rate(
                A=A, abundance=abundances[A], mA=mA,
                response_value=response_value, response_model="AFH_v6_default",
                benchmark=benchmark, er_keV=er_keV, halo_model=halo_model,
                mass_scheme="ame2020_nuclear", nv=high_nv,
                nw=16, nz=16, nphi=8,
                rate_factor=rate_factors["ame2020_nuclear"],
                mchi=args.mchi_GeV, mV=args.mV_GeV,
                coupling_product_sq=args.coupling_product_sq, g2=args.g2,
                rho_dm=args.rhoDM_GeV_cm3, v0=args.v0_km_s,
                ve=args.ve_km_s, vesc=args.vesc_km_s,
                untruncated_vmax=args.untruncated_vmax_km_s,
            )
            low_rate = base["rate_contribution_events_kg_day_keV"]
            high_rate = high["rate_contribution_events_kg_day_keV"]
            kernel_checks.append({
                "mass_scheme": "ame2020_nuclear",
                "benchmark": benchmark,
                "ER_keV": er_keV,
                "halo_model": halo_model,
                "A": A,
                "kernel_low": f"{args.nw}x{args.nz}x{args.nphi}",
                "kernel_high": "16x16x8",
                "rate_low": low_rate,
                "rate_high": high_rate,
                "relative_difference": relative_difference(low_rate, high_rate),
            })

    max_speed_difference = max(
        (row["relative_difference"] for row in speed_checks), default=0.0
    )
    max_kernel_difference = max(
        (row["relative_difference"] for row in kernel_checks), default=0.0
    )
    if max_speed_difference > args.max_relative_speed_convergence:
        raise ArithmeticError(
            f"Speed quadrature failed: max relative difference={max_speed_difference:.3e}"
        )
    if max_kernel_difference > args.max_relative_kernel_convergence:
        raise ArithmeticError(
            f"Kernel quadrature failed: max relative difference={max_kernel_difference:.3e}"
        )

    write_csv(args.out_dir / "afh_seven_isotope_contributions.csv", contributions_high)
    write_csv(args.out_dir / "afh_seven_isotope_halo_rates.csv", summaries)
    write_csv(args.out_dir / "missing_isotope_coherent_A2_ceiling.csv", missing_ceiling_rows)
    write_csv(args.out_dir / "natural_xenon_rate_envelopes.csv", envelopes)
    write_csv(args.out_dir / "speed_quadrature_convergence.csv", speed_checks)
    write_csv(args.out_dir / "kernel_quadrature_convergence.csv", kernel_checks)
    write_csv(args.out_dir / "nist_mainline_reproduction.csv", nist_reproduction)

    mass_metadata = {}
    for scheme in MASS_SCHEMES:
        mass_metadata[scheme] = {
            "mean_atomic_weight_g_mol": mean_atomic_weights[scheme],
            "mean_atomic_weight_uses_all_nine_isotopes": True,
            "mass_conversion": (
                "NIST atomic mass minus 54 electron masses, CODATA-2018 constants; "
                "electronic binding neglected"
                if scheme == "nist_nuclear"
                else "AME2020 unrounded atomic mass minus 54 CODATA-2022 electron masses "
                     "plus B_e(54)"
            ),
        }

    metadata = {
        "calculation": (
            "AME2020/CODATA-2022 natural-xenon three-body halo fold using all "
            "seven AFH v6.0 default-density xenon responses"
        ),
        "status": "exploratory only; 2401-node PCHIP interpolation is not accepted for precision rates; not a nine-isotope AFH result",
        "response_interpolation_status": "NOT_ACCEPTED_PENDING_DIRECT_EXACT_Q_OR_VALIDATED_REFINED_GRID",
        "AFH_source": "DMFormFactor v6.0 built-in sdgXeA default densities",
        "AFH_response_file": str(args.response_csv),
        "AFH_response_file_sha256": sha256(args.response_csv),
        "AFH_response_grid": response_metadata,
        "AFH_isotopes": list(AFH_ISOTOPES),
        "AFH_available_natural_atom_fraction": sum(abundances[A] for A in AFH_ISOTOPES),
        "missing_isotopes": list(MISSING_ISOTOPES),
        "missing_natural_atom_fraction": sum(abundances[A] for A in MISSING_ISOTOPES),
        "abundance_source": str(args.abundance_csv),
        "abundance_convention": "natural atom fractions; no renormalization",
        "mass_schemes": mass_metadata,
        "target_number_per_kg": (
            "N_A*1000/Mbar; Mbar is computed from all nine natural isotopes "
            "using the same atomic-mass scheme as the nuclear kinematics"
        ),
        "response_momentum": (
            "exact_spatial kinematic q=sqrt(2*m_A*E_R+E_R^2); the current "
            "response lookup is PCHIP on a 2401-node grid and has a documented "
            "off-grid interpolation residual up to 8.91e-3 at selected points; "
            "this response lookup is diagnostic only, not accepted for precision rates"
        ),
        "three_body_kinematics": (
            "exact target mass-shell q; isotope-specific W_max and v_min; "
            "mediator invariant denominator (m_V^2+2*m_A*E_R)^2"
        ),
        "response_normalization": "R_A(0)=A^2 for each AFH isotope",
        "dark_sector": {
            "mchi1_GeV": args.mchi_GeV,
            "mV_GeV": args.mV_GeV,
            "coupling_product_squared": args.coupling_product_sq,
            "g2": args.g2,
            "rho_chi_GeV_cm3": args.rhoDM_GeV_cm3,
            "benchmarks": {
                name: {"ms_keV": ms * 1.0e6, "Delta_m_MeV": dm * 1.0e3}
                for name, (ms, dm) in BENCHMARKS.items()
            },
            "width_scheme": (
                "pole chi2 -> chi1 s width; conditional on Dirac fermions, "
                "real scalar, pure scalar off-diagonal Yukawa, and no other open channels"
            ),
        },
        "halo": {
            "shm_cutoff": {
                "v0_km_s": args.v0_km_s,
                "vE_km_s": args.ve_km_s,
                "vesc_km_s": args.vesc_km_s,
                "vmax_lab_km_s": args.vesc_km_s + args.ve_km_s,
            },
            "mb_untruncated": {
                "v0_km_s": args.v0_km_s,
                "vE_km_s": args.ve_km_s,
                "numerical_vmax_km_s": args.untruncated_vmax_km_s,
                "status": "tail-sensitivity diagnostic, not adopted default",
            },
        },
        "quadrature": {
            "speed_orders": nv_orders,
            "kernel_baseline": [args.nw, args.nz, args.nphi],
            "kernel_crosscheck": [16, 16, 8],
            "max_relative_speed_difference": max_speed_difference,
            "max_relative_kernel_difference": max_kernel_difference,
            "max_relative_nist_mainline_reproduction": max_nist_difference,
        },
        "missing_isotope_ceiling": {
            "response_model": "R_A(q)=A^2 for Xe-124 and Xe-126",
            "interpretation": (
                "coherent-charge upper ceiling from |F_A(q)|<=A for a normalized "
                "nonnegative one-body charge density; this is not an AFH response "
                "and is never included in the seven-isotope central prediction"
            ),
            "not_a_nine_isotope_AFH_prediction": True,
        },
        "rate_units": "events/(kg day keV)",
        "detector_response": "not applied",
        "native_Mathematica_validation": (
            "pending; AFH default matrices were extracted from the official v6.0 "
            "source and response functions are evaluated with the independently "
            "validated Python finite-sum translation"
        ),
    }
    metadata_path = args.out_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "mass_schemes": MASS_SCHEMES,
        "AFH_isotopes": list(AFH_ISOTOPES),
        "AFH_abundance_coverage": metadata["AFH_available_natural_atom_fraction"],
        "missing_isotopes": list(MISSING_ISOTOPES),
        "missing_abundance": metadata["missing_natural_atom_fraction"],
        "max_speed_convergence": max_speed_difference,
        "max_kernel_convergence": max_kernel_difference,
        "max_NIST_mainline_reproduction": max_nist_difference,
        "rates": [
            {
                "mass_scheme": row["mass_scheme"],
                "benchmark": row["benchmark"],
                "ER_keV": row["ER_keV"],
                "halo": row["halo_model"],
                "AFH_7_rate_nv64": row["AFH_7_isotope_rate_events_kg_day_keV"],
                "missing_A2_ceiling": row["missing_Xe124_Xe126_coherent_ceiling"],
            }
            for row in summaries
        ],
        "status": "DIAGNOSTIC_ONLY_NOT_ACCEPTED",
    }, indent=2))


if __name__ == "__main__":
    main()
