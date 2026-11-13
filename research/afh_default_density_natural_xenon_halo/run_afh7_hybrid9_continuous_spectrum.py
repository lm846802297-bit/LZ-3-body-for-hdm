#!/usr/bin/env python3
"""AFH-7, Hybrid-9, Helm-9 and coherent-ceiling natural-xenon spectra.

AFH is evaluated from the official v6.0 default density matrices at each exact
spatial-q recoil point. PCHIP is used only as an independent grid-interpolation
diagnostic. Xe-124/Xe-126 are never assigned invented AFH matrices: they enter
only the separately labelled Helm-2 hybrid and A^2 ceiling diagnostics.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIG_DIR = ROOT / "research" / "figure2_full_reproduction"
sys.path.insert(0, str(FIG_DIR))
sys.path.insert(0, str(HERE))

import eq6_kernel as eq6  # noqa: E402
from generate_afh_default_xenon_response_grid import (  # noqa: E402
    ISOTOPES as AFH_ISOTOPES,
    compute_isotope_grid,
    parse_density_matrix,
    parse_isotopic_spins,
    read_natural_xenon_masses,
)
from rate_kinematics import momentum_transfer, vmin_three_body_km_s  # noqa: E402

C_KM_S = 299_792.458
C_CM_S = 2.99792458e10
GEV2_TO_CM2 = 0.3893793721e-27
AVOGADRO = 6.02214076e23
NIST_XE_STANDARD_ATOMIC_WEIGHT_G_MOL = 131.29276144779053
HBARC_GEV_FM = 0.1973269804
V0_KM_S_DEFAULT = 220.0
VE_KM_S_DEFAULT = 232.0
VESC_KM_S_DEFAULT = 544.0

ALL_ISOTOPES = (124, 126, 128, 129, 130, 131, 132, 134, 136)
SELECTED_CHECK_ENERGIES_KEV = (101.0, 200.0, 267.0, 542.0)
SCENARIOS = (
    "AFH-7",
    "Hybrid-9 (AFH-7 + Helm-2)",
    "AFH-7 + A2-2 ceiling",
    "Helm-9",
)
BENCHMARKS = {
    "red_ms200_dm1": {"ms_MeV": 0.200, "delta_m_MeV": 1.0},
    "green_ms300_dm1": {"ms_MeV": 0.300, "delta_m_MeV": 1.0},
    "black_ms360_dm1": {"ms_MeV": 0.360, "delta_m_MeV": 1.0},
    "blue_ms300_dm10": {"ms_MeV": 0.300, "delta_m_MeV": 10.0},
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def recoil_grid(
    er_min: float = 5.0,
    er_max: float = 800.0,
    er_step: float = 5.0,
    fine_max: float = 270.0,
    high_er_step: float = 20.0,
) -> list[float]:
    if not (0.0 < er_min <= er_max and er_step > 0.0 and high_er_step > 0.0):
        raise ValueError("require positive recoil bounds and step sizes")
    fine_end = min(fine_max, er_max)
    if fine_end < er_min:
        raise ValueError("fine-grid endpoint must not be below ER-min")
    fine_count = int(round((fine_end - er_min) / er_step))
    fine = [er_min + i * er_step for i in range(fine_count + 1)]
    if not math.isclose(fine[-1], fine_end, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError("fine recoil interval must be an integer number of steps")
    coarse = []
    if er_max > fine_end:
        coarse_start = fine_end + 0.5 * high_er_step
        n_coarse = int(math.floor((er_max - coarse_start) / high_er_step + 1e-12))
        coarse = [coarse_start + i * high_er_step for i in range(n_coarse + 1)]
        if not math.isclose(coarse[-1], er_max, rel_tol=0.0, abs_tol=1e-9):
            coarse.append(er_max)
    selected = [e for e in SELECTED_CHECK_ENERGIES_KEV if er_min <= e <= er_max]
    return sorted(set(fine).union(coarse).union(selected))


def helm_form_factor(q_GeV: float, A: int) -> float:
    """Standard Helm amplitude with q converted to fm^{-1}."""
    if q_GeV < 0.0 or A <= 0:
        raise ValueError("require q>=0 and A>0")
    q_fm = q_GeV / HBARC_GEV_FM
    c = 1.23 * A ** (1.0 / 3.0) - 0.60
    a = 0.52
    s = 1.0
    r_n_sq = c * c + (7.0 / 3.0) * math.pi**2 * a * a - 5.0 * s * s
    if r_n_sq <= 0.0:
        raise ArithmeticError(f"non-positive Helm radius for A={A}")
    r_n = math.sqrt(r_n_sq)
    x = q_fm * r_n
    if abs(x) < 1.0e-5:
        x2 = x * x
        spherical = 1.0 - x2 / 10.0 + x2 * x2 / 280.0 - x2**3 / 15120.0
    else:
        j1 = (math.sin(x) - x * math.cos(x)) / (x * x)
        spherical = 3.0 * j1 / x
    return spherical * math.exp(-0.5 * (q_fm * s) ** 2)


def helm_response(q_GeV: float, A: int) -> float:
    form = helm_form_factor(q_GeV, A)
    return float(A * A * form * form)


def scenario_response(scenario: str, A: int, R_AFH: float | None, R_Helm: float) -> float:
    supported = A in AFH_ISOTOPES
    if scenario == "AFH-7":
        return float(R_AFH) if supported and R_AFH is not None else 0.0
    if scenario == "Hybrid-9 (AFH-7 + Helm-2)":
        return float(R_AFH) if supported and R_AFH is not None else R_Helm
    if scenario == "AFH-7 + A2-2 ceiling":
        return float(R_AFH) if supported and R_AFH is not None else float(A * A)
    if scenario == "Helm-9":
        return R_Helm
    raise ValueError(f"unknown response scenario: {scenario}")


def shm_truncated_pdf(v: float, v0: float, ve: float, vesc: float) -> float:
    vmax = vesc + ve
    if v < 0.0 or v > vmax:
        return 0.0
    z = vesc / v0
    normalization = math.erf(z) - 2.0 * z / math.sqrt(math.pi) * math.exp(-z * z)
    if normalization <= 0.0:
        raise ValueError("invalid truncated-SHM normalization")
    if v < vesc - ve:
        bracket = math.exp(-((v - ve) / v0) ** 2) - math.exp(-((v + ve) / v0) ** 2)
    else:
        bracket = math.exp(-((v - ve) / v0) ** 2) - math.exp(-z * z)
    return v * bracket / (math.sqrt(math.pi) * v0 * ve * normalization)


def speed_nodes(vmin: float, vmax: float, n: int) -> tuple[np.ndarray, np.ndarray]:
    if n < 2:
        raise ValueError("speed quadrature order must be >=2")
    if vmax <= vmin:
        return np.empty(0), np.empty(0)
    x, w = leggauss(int(n))
    return 0.5 * (vmax + vmin) + 0.5 * (vmax - vmin) * x, 0.5 * (vmax - vmin) * w


def global_wmax2(mchi: float, mA: float, speed_kms: float) -> tuple[float, float]:
    """Analytic max_ER W_max^2 and the recoil energy where it occurs."""
    beta = speed_kms / C_KM_S
    gamma = 1.0 / math.sqrt(1.0 - beta * beta)
    Echi = mchi * gamma
    pchi = mchi * gamma * beta
    discriminant = math.sqrt(mchi * mchi + 2.0 * Echi * mA + mA * mA)
    er_star = mA * ((Echi + mA) / discriminant - 1.0)
    wmax2 = mchi * mchi + 2.0 * mA * (Echi + mA - discriminant)
    return wmax2, er_star


def _legendre(order: int) -> tuple[np.ndarray, np.ndarray]:
    return leggauss(int(order))


def stable_build_point(
    mchi: float, ms: float, mA: float, ER: float, speed_kms: float,
    delta_W2: float, z: float, phi: float,
):
    """Construct the phase-space point using delta=W^2-W_min^2 explicitly."""
    beta = speed_kms / C_KM_S
    gamma = 1.0 / math.sqrt(1.0 - beta * beta)
    Echi = mchi * gamma
    pchi = mchi * gamma * beta
    p = np.array([Echi, 0.0, 0.0, pchi])
    qmag = momentum_transfer(mA, ER)
    numerator = (
        2.0 * mchi * ms + ms * ms + delta_W2
        + 2.0 * (Echi + mA) * ER
    )
    cos_q = numerator / (2.0 * pchi * qmag)
    if abs(cos_q) > 1.0 + 2.0e-8:
        raise ValueError(f"unphysical cos(theta_q)={cos_q}")
    cos_q = min(1.0, max(-1.0, cos_q))
    sin_q = math.sqrt(max(0.0, 1.0 - cos_q * cos_q))
    q = np.array([ER, qmag * sin_q, 0.0, qmag * cos_q])
    K = p - q
    W2 = (mchi + ms) ** 2 + delta_W2
    W = math.sqrt(W2)
    betaK = K[1:] / K[0]
    pstar = eq6.boost(p, -betaK)
    e3 = pstar[1:] / np.linalg.norm(pstar[1:])
    ref = np.array([1.0, 0.0, 0.0])
    if abs(float(np.dot(ref, e3))) > 0.9:
        ref = np.array([0.0, 1.0, 0.0])
    e1 = np.cross(ref, e3)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(e3, e1)
    lam_kallen = delta_W2 * (4.0 * mchi * ms + delta_W2)
    if lam_kallen < -1.0e-14:
        raise ValueError("closed chi1-s phase space")
    kabs = math.sqrt(max(0.0, lam_kallen)) / (2.0 * W)
    Ek = (2.0 * ms * (mchi + ms) + delta_W2) / (2.0 * W)
    Ep = (2.0 * mchi * (mchi + ms) + delta_W2) / (2.0 * W)
    direction = (
        z * e3
        + math.sqrt(max(0.0, 1.0 - z * z))
        * (math.cos(phi) * e1 + math.sin(phi) * e2)
    )
    k = eq6.boost(np.r_[Ek, kabs * direction], betaK)
    p_prime = eq6.boost(np.r_[Ep, -kabs * direction], betaK)
    return eq6.Point(p, p_prime, k, K, q, W2)


def integrate_i6_threshold_u2(
    mchi: float, ms: float, delta_m: float, mA: float, ER: float,
    speed_kms: float, nW: int, nz: int, nphi: int, g2: float,
) -> float:
    """Threshold-regularized I6 with the manuscript's constant pole width."""
    wmin2, wmax2 = eq6.limits(mchi, ms, mA, ER, speed_kms)
    if wmax2 <= wmin2:
        return 0.0
    xW, wW = _legendre(nW)
    xz, wz = _legendre(nz)
    xp, wp = _legendre(nphi)
    u = 0.5 * (xW + 1.0)
    wu = 0.5 * wW
    delta_range = wmax2 - wmin2
    delta_values = delta_range * u * u
    W2_values = wmin2 + delta_values
    W2_weights = wu * (2.0 * delta_range * u)
    phi_values = math.pi * (xp + 1.0)
    phi_weights = 0.5 * wp
    mchi2 = mchi + delta_m
    pole_width = eq6.chi2_width_dirac_scalar(mchi, ms, delta_m, g2)
    total = 0.0
    for W2, delta_W2, weightW in zip(W2_values, delta_values, W2_weights):
        W2 = float(W2)
        delta_W2 = float(delta_W2)
        lam = delta_W2 * (4.0 * mchi * ms + delta_W2) / (W2 * W2)
        if lam < 0.0:
            if lam > -1.0e-14:
                lam = 0.0
            else:
                raise ArithmeticError(f"negative Kallen lambda: {lam}")
        angular = 0.0
        for z, weightz in zip(xz, wz):
            azimuth = 0.0
            for phi, weightphi in zip(phi_values, phi_weights):
                point = stable_build_point(
                    mchi, ms, mA, ER, speed_kms,
                    delta_W2, float(z), float(phi),
                )
                value = eq6.spin_trace(
                    point, mchi, mchi2, width=pole_width
                )["total"]
                if not math.isfinite(value):
                    raise ArithmeticError("non-finite Dirac spin trace")
                azimuth += float(weightphi) * value
            angular += float(weightz) * azimuth
        total += float(weightW) * math.sqrt(lam) * angular
    if not math.isfinite(total) or total < -1.0e-12:
        raise ArithmeticError(f"invalid I6 value: {total}")
    return max(0.0, float(total))


def compute_kernel_halo_integral(
    *, A: int, ER_keV: float, mA: float, mchi: float, ms: float,
    delta_m: float, g2: float, coupling_product_sq: float,
    nv: int, nw: int, nz: int, nphi: int,
    v0: float, ve: float, vesc: float,
) -> dict:
    ER = ER_keV * 1.0e-6
    vmax = vesc + ve
    vmin = vmin_three_body_km_s(mchi, ms, mA, ER)
    if vmin >= vmax:
        return {
            "A": A, "ER_keV": ER_keV, "mA_GeV": mA,
            "vmin_km_s": vmin, "vmax_km_s": vmax,
            "speed_phase_space_open": False,
            "kernel_halo_integral_GeV": 0.0,
        }
    velocities, weights = speed_nodes(vmin, vmax, nv)
    total = 0.0
    for v, weight in zip(velocities, weights):
        v = float(v)
        pdf = shm_truncated_pdf(v, v0, ve, vesc)
        if pdf == 0.0:
            continue
        beta = v / C_KM_S
        gamma = 1.0 / math.sqrt(1.0 - beta * beta)
        pchi = mchi * gamma * beta
        I6 = integrate_i6_threshold_u2(
            mchi, ms, delta_m, mA, ER, v, nw, nz, nphi, g2
        )
        total += (
            float(weight) * pdf * beta
            * (mA * coupling_product_sq / (256.0 * math.pi**3 * pchi * pchi))
            * I6
        )
    if not math.isfinite(total) or total < -1.0e-12:
        raise ArithmeticError(f"invalid isotope halo integral for A={A}: {total}")
    return {
        "A": A, "ER_keV": ER_keV, "mA_GeV": mA,
        "vmin_km_s": vmin, "vmax_km_s": vmax,
        "speed_phase_space_open": True,
        "kernel_halo_integral_GeV": max(0.0, total),
    }


def relative_difference(reference: float, value: float) -> float:
    if reference == 0.0 and value == 0.0:
        return 0.0
    if reference == 0.0:
        return math.inf
    return abs(value / reference - 1.0)


def build_response_tables(
    *, energies: list[float], masses: dict[int, dict], source_path: Path,
    weights_path: Path, response_dir: Path,
) -> tuple[dict, list[dict], dict]:
    source_text = source_path.read_text(encoding="utf-8")
    spins = parse_isotopic_spins(source_text)
    matrices = {A: parse_density_matrix(source_text, A) for A in AFH_ISOTOPES}
    response_lookup: dict[tuple[int, float], dict] = {}
    response_rows: list[dict] = []
    response_summaries: dict[str, dict] = {}
    q_by_A: dict[int, list[float]] = {}
    pchip_by_A: dict[int, PchipInterpolator] = {}

    for A in AFH_ISOTOPES:
        mA = masses[A]["nuclear_mass_GeV"]
        q_values = [
            momentum_transfer(mA, ER_keV * 1.0e-6)
            for ER_keV in energies
        ]
        q_by_A[A] = q_values
        if max(q_values) > 0.6 + 1.0e-12:
            raise ValueError(f"Xe-{A}: recoil grid exceeds archived AFH q support")
        grid_path = response_dir / f"afh_default_xe{A}_response_2401.csv"
        grid = read_csv(grid_path)
        q_grid = np.asarray([float(row["q_GeV"]) for row in grid])
        r_grid = np.asarray([float(row["R_equal_pn_normalized"]) for row in grid])
        if len(q_grid) != 2401 or not np.all(np.diff(q_grid) > 0.0):
            raise ArithmeticError(f"Xe-{A}: invalid archived AFH q grid")
        pchip = PchipInterpolator(q_grid, r_grid, extrapolate=False)
        pchip_by_A[A] = pchip

        q_eval = np.asarray([0.0] + q_values, dtype=float)
        direct_records, direct_summary = compute_isotope_grid(
            A=A,
            rows=matrices[A],
            J_A=spins[A],
            mass_GeV=mA,
            q_grid=q_eval,
        )
        response_summaries[str(A)] = direct_summary
        for index, ER_keV in enumerate(energies):
            q = q_values[index]
            direct = float(direct_records[index + 1]["R_equal_pn_normalized"])
            interpolated = float(pchip(q))
            helm = helm_response(q, A)
            response_lookup[(A, ER_keV)] = {
                "q_GeV": q, "R_AFH": direct, "R_AFH_PCHIP": interpolated,
                "R_Helm": helm,
            }
            response_rows.append({
                "A": A, "isotope": masses[A]["isotope"], "ER_keV": ER_keV,
                "q_exact_spatial_GeV": q, "natural_atom_fraction": masses[A]["natural_atom_fraction"],
                "AFH_default_available": True,
                "R_AFH_direct_exact_q": direct,
                "R_AFH_PCHIP_grid": interpolated,
                "direct_minus_PCHIP_over_A2": (direct - interpolated) / (A * A),
                "relative_direct_vs_PCHIP": (
                    abs(interpolated / direct - 1.0)
                    if direct > 1.0e-10 * A * A else ""
                ),
                "R_Helm": helm,
                "R_AFH_over_A2": direct / (A * A),
                "R_Helm_over_A2": helm / (A * A),
                "AFH_minus_Helm_over_A2": (direct - helm) / (A * A),
            })

    for A in (124, 126):
        mA = masses[A]["nuclear_mass_GeV"]
        for ER_keV in energies:
            q = momentum_transfer(mA, ER_keV * 1.0e-6)
            response_lookup[(A, ER_keV)] = {
                "q_GeV": q, "R_AFH": None, "R_AFH_PCHIP": None,
                "R_Helm": helm_response(q, A),
            }
            response_rows.append({
                "A": A, "isotope": masses[A]["isotope"], "ER_keV": ER_keV,
                "q_exact_spatial_GeV": q, "natural_atom_fraction": masses[A]["natural_atom_fraction"],
                "AFH_default_available": False,
                "R_AFH_direct_exact_q": "",
                "R_AFH_PCHIP_grid": "",
                "direct_minus_PCHIP_over_A2": "",
                "relative_direct_vs_PCHIP": "",
                "R_Helm": response_lookup[(A, ER_keV)]["R_Helm"],
                "R_AFH_over_A2": "",
                "R_Helm_over_A2": response_lookup[(A, ER_keV)]["R_Helm"] / (A * A),
                "AFH_minus_Helm_over_A2": "",
            })
    return response_lookup, response_rows, response_summaries


def run(args: argparse.Namespace) -> dict:
    args.outdir.mkdir(parents=True, exist_ok=True)
    energies = recoil_grid(
        args.er_min_keV, args.er_max_keV, args.er_step_keV,
        args.fine_er_max_keV, args.high_er_step_keV,
    )
    masses = read_natural_xenon_masses(args.weights)
    abundance_sum = sum(masses[A]["natural_atom_fraction"] for A in ALL_ISOTOPES)
    if not math.isclose(abundance_sum, 1.0, rel_tol=0.0, abs_tol=2.0e-6):
        raise ArithmeticError(f"natural isotope fractions sum to {abundance_sum}")
    response_lookup, response_rows, response_summaries = build_response_tables(
        energies=energies, masses=masses, source_path=args.afh_source,
        weights_path=args.weights, response_dir=args.response_dir,
    )

    af_h_fraction = sum(masses[A]["natural_atom_fraction"] for A in AFH_ISOTOPES)
    missing_fraction = sum(masses[A]["natural_atom_fraction"] for A in (124, 126))
    total_a2 = sum(
        masses[A]["natural_atom_fraction"] * A * A for A in ALL_ISOTOPES
    )
    af_h_a2_fraction = sum(
        masses[A]["natural_atom_fraction"] * A * A for A in AFH_ISOTOPES
    ) / total_a2

    rate_factor = (
        (args.rhoDM_GeV_cm3 / args.mchi_GeV)
        * C_CM_S
        * (AVOGADRO * 1000.0 / NIST_XE_STANDARD_ATOMIC_WEIGHT_G_MOL)
        * GEV2_TO_CM2 * 1.0e-6 * 86400.0
    )
    vmax = args.vesc_km_s + args.ve_km_s
    kernel_cache: dict[tuple[str, float, int], dict] = {}
    kernel_rows: list[dict] = []
    spectrum_rows: list[dict] = []
    quadrature_rows: list[dict] = []

    for benchmark in args.benchmarks:
        spec = BENCHMARKS[benchmark]
        ms = spec["ms_MeV"] * 1.0e-3
        delta_m = spec["delta_m_MeV"] * 1.0e-3
        if delta_m <= ms:
            raise ValueError(f"{benchmark}: chi2 -> chi1 s is not open")
        mchi2 = args.mchi_GeV + delta_m
        pole_width = eq6.chi2_width_dirac_scalar(
            args.mchi_GeV, ms, delta_m, args.g2
        )
        wmax2_global = max(
            global_wmax2(args.mchi_GeV, masses[A]["nuclear_mass_GeV"], vmax)[0]
            for A in ALL_ISOTOPES
        )
        pole_gap_GeV = mchi2 - math.sqrt(wmax2_global)
        if pole_gap_GeV <= 0.0:
            raise ArithmeticError(
                f"{benchmark}: on-shell chi2 becomes kinematically accessible "
                f"at v_max={vmax} km/s"
            )

        for ER_keV in energies:
            for A in ALL_ISOTOPES:
                mA = masses[A]["nuclear_mass_GeV"]
                result = compute_kernel_halo_integral(
                    A=A, ER_keV=ER_keV, mA=mA, mchi=args.mchi_GeV,
                    ms=ms, delta_m=delta_m, g2=args.g2,
                    coupling_product_sq=args.coupling_product_sq,
                    nv=args.nv, nw=args.nw, nz=args.nz, nphi=args.nphi,
                    v0=args.v0_km_s, ve=args.ve_km_s, vesc=args.vesc_km_s,
                )
                key = (benchmark, ER_keV, A)
                kernel_cache[key] = result
                response = response_lookup[(A, ER_keV)]
                kernel_rows.append({
                    **result,
                    "benchmark": benchmark,
                    "ms_MeV": spec["ms_MeV"],
                    "delta_m_MeV": spec["delta_m_MeV"],
                    "q_exact_spatial_GeV": response["q_GeV"],
                    "natural_atom_fraction": masses[A]["natural_atom_fraction"],
                    "R_AFH_direct_exact_q": (
                        response["R_AFH"] if response["R_AFH"] is not None else ""
                    ),
                    "R_Helm": response["R_Helm"],
                    "width_scheme": "constant pole width",
                    "Gamma_chi2_pole_MeV": pole_width * 1.0e3,
                    "mchi2_minus_global_Wmax_keV": pole_gap_GeV * 1.0e6,
                })

            for scenario in SCENARIOS:
                weighted_integral = 0.0
                for A in ALL_ISOTOPES:
                    mA = masses[A]["nuclear_mass_GeV"]
                    response = response_lookup[(A, ER_keV)]
                    R_A = scenario_response(
                        scenario, A, response["R_AFH"], response["R_Helm"]
                    )
                    if R_A == 0.0:
                        continue
                    base = kernel_cache[(benchmark, ER_keV, A)]["kernel_halo_integral_GeV"]
                    denominator = (
                        args.mV_GeV**2 + 2.0 * mA * ER_keV * 1.0e-6
                    ) ** 2
                    weighted_integral += (
                        masses[A]["natural_atom_fraction"] * base * R_A / denominator
                    )
                spectrum_rows.append({
                    "benchmark": benchmark,
                    "scenario": scenario,
                    "ER_keV": ER_keV,
                    "rate_events_kg_day_keV": rate_factor * weighted_integral,
                    "weighted_cross_section_integral_GeVminus3": weighted_integral,
                    "available_atom_fraction": af_h_fraction,
                    "missing_atom_fraction": missing_fraction,
                    "A2_weighted_AFH_coverage_at_q0": af_h_a2_fraction,
                    "mchi_GeV": args.mchi_GeV,
                    "mV_GeV": args.mV_GeV,
                    "coupling_product_sq": args.coupling_product_sq,
                    "g2_for_pole_width": args.g2,
                    "rhoDM_GeV_cm3": args.rhoDM_GeV_cm3,
                    "halo_model": "truncated SHM",
                    "vmax_km_s": vmax,
                    "mass_scheme": "NIST nuclear masses",
                    "response_q_convention": "exact spatial q",
                    "width_scheme": "conditional Dirac pure-scalar pole width",
                    "detector_response_applied": False,
                })

    # Relative scenario shifts are attached after all spectra are available.
    reference = {
        (r["benchmark"], r["ER_keV"]): float(r["rate_events_kg_day_keV"])
        for r in spectrum_rows if r["scenario"] == "AFH-7"
    }
    for row in spectrum_rows:
        ref = reference[(row["benchmark"], row["ER_keV"])]
        row["relative_shift_vs_AFH7"] = (
            row["rate_events_kg_day_keV"] / ref - 1.0 if ref > 0.0
            else (0.0 if row["rate_events_kg_day_keV"] == 0.0 else "")
        )

    if not args.skip_crosschecks:
        check_energies = [
            e for e in SELECTED_CHECK_ENERGIES_KEV
            if args.er_min_keV <= e <= args.er_max_keV
        ]
        for benchmark in args.benchmarks:
            spec = BENCHMARKS[benchmark]
            ms = spec["ms_MeV"] * 1.0e-3
            delta_m = spec["delta_m_MeV"] * 1.0e-3
            for ER_keV in check_energies:
                for A in ALL_ISOTOPES:
                    mA = masses[A]["nuclear_mass_GeV"]
                    mid = kernel_cache[(benchmark, ER_keV, A)]["kernel_halo_integral_GeV"]
                    low = compute_kernel_halo_integral(
                        A=A, ER_keV=ER_keV, mA=mA, mchi=args.mchi_GeV,
                        ms=ms, delta_m=delta_m, g2=args.g2,
                        coupling_product_sq=args.coupling_product_sq,
                        nv=args.nv_low, nw=args.nw, nz=args.nz, nphi=args.nphi,
                        v0=args.v0_km_s, ve=args.ve_km_s, vesc=args.vesc_km_s,
                    )["kernel_halo_integral_GeV"]
                    high = compute_kernel_halo_integral(
                        A=A, ER_keV=ER_keV, mA=mA, mchi=args.mchi_GeV,
                        ms=ms, delta_m=delta_m, g2=args.g2,
                        coupling_product_sq=args.coupling_product_sq,
                        nv=args.nv, nw=args.nw_high, nz=args.nz_high,
                        nphi=args.nphi_high, v0=args.v0_km_s,
                        ve=args.ve_km_s, vesc=args.vesc_km_s,
                    )["kernel_halo_integral_GeV"]
                    speed_diff = relative_difference(low, mid)
                    kernel_diff = relative_difference(mid, high)
                    quadrature_rows.append({
                        "benchmark": benchmark, "A": A, "ER_keV": ER_keV,
                        "nv_low": args.nv_low, "nv_final": args.nv,
                        "speed_quadrature_relative_difference": speed_diff,
                        "kernel_order_low": f"{args.nw}x{args.nz}x{args.nphi}",
                        "kernel_order_high": (
                            f"{args.nw_high}x{args.nz_high}x{args.nphi_high}"
                        ),
                        "kernel_order_relative_difference": kernel_diff,
                    })
        max_speed_diff = max(
            (float(r["speed_quadrature_relative_difference"]) for r in quadrature_rows),
            default=0.0,
        )
        max_kernel_diff = max(
            (float(r["kernel_order_relative_difference"]) for r in quadrature_rows),
            default=0.0,
        )
        if max_speed_diff > args.max_relative_check or max_kernel_diff > args.max_relative_check:
            raise ArithmeticError(
                f"quadrature check failed: speed={max_speed_diff:.4g}, "
                f"kernel={max_kernel_diff:.4g}, tolerance={args.max_relative_check:.4g}"
            )
    else:
        max_speed_diff = None
        max_kernel_diff = None

    response_path = args.outdir / "afh_hybrid9_response_model_comparison.csv"
    kernel_path = args.outdir / "afh_hybrid9_isotope_kernel_integrals.csv"
    spectrum_path = args.outdir / "afh_hybrid9_natural_xenon_spectrum.csv"
    check_path = args.outdir / "afh_hybrid9_quadrature_crosschecks.csv"
    write_csv(response_path, response_rows)
    write_csv(kernel_path, kernel_rows)
    write_csv(spectrum_path, spectrum_rows)
    if quadrature_rows:
        write_csv(check_path, quadrature_rows)
    elif args.skip_crosschecks:
        write_csv(check_path, [{
            "status": "SKIPPED",
            "reason": "smoke run requested --skip-crosschecks",
        }])
    else:
        raise ArithmeticError("quadrature checks unexpectedly produced no rows")

    direct_pchip_diffs = [
        abs(float(row["direct_minus_PCHIP_over_A2"]))
        for row in response_rows
        if row["AFH_default_available"]
    ]
    model_diffs = [
        abs(float(row["AFH_minus_Helm_over_A2"]))
        for row in response_rows
        if row["AFH_default_available"]
    ]
    metadata = {
        "status": "PASS",
        "calculation": "continuous natural-xenon three-body rate with AFH-7 and explicitly labelled Helm diagnostics",
        "response_convention": "AFH direct finite-sum at exact spatial q; PCHIP grid is diagnostic only; Helm fallback is separate",
        "response_grid_source": str(args.response_dir.relative_to(ROOT)),
        "response_grid_files": {
            str(A): sha256_file(args.response_dir / f"afh_default_xe{A}_response_2401.csv")
            for A in AFH_ISOTOPES
        },
        "afh_source_file": str(args.afh_source.relative_to(ROOT)),
        "afh_source_sha256": sha256_file(args.afh_source),
        "isotope_weights_file": str(args.weights.relative_to(ROOT)),
        "isotope_weights_sha256": sha256_file(args.weights),
        "supported_AFH_isotopes": list(AFH_ISOTOPES),
        "missing_AFH_default_isotopes": [124, 126],
        "natural_atom_fraction_AFH7": af_h_fraction,
        "natural_atom_fraction_missing": missing_fraction,
        "A2_weighted_AFH_coverage_at_q0": af_h_a2_fraction,
        "abundance_renormalization": "none",
        "nuclear_mass_scheme": "NIST atomic isotope mass minus 54 electron masses, converted to GeV; electron binding energy neglected",
        "spatial_momentum": "q=sqrt(2*m_A*E_R+E_R^2) for each isotope",
        "AFH_evaluation": "official v6.0 density matrices parsed from source and direct finite-sum evaluation at every recoil q",
        "AFH_PCHIP_comparison": {
            "max_absolute_direct_minus_PCHIP_over_A2": max(direct_pchip_diffs, default=0.0),
            "interpretation": "interpolation diagnostic only; direct exact-q values are used in the rate",
        },
        "Helm_model_comparison": {
            "max_absolute_AFH_minus_Helm_over_A2_on_supported_isotopes": max(model_diffs, default=0.0),
            "formula": "R=A^2 F_Helm(q)^2; F=3 j1(q r_n)/(q r_n) exp[-(q s)^2/2]",
            "parameters_fm": {"c": "1.23*A^(1/3)-0.60", "a": 0.52, "s": 1.0},
            "role": "phenomenological fallback for Xe-124/Xe-126 and separate Helm-9 model comparison; not AFH data",
        },
        "scenarios": {
            "AFH-7": "AFH v6.0 for seven supported isotopes; Xe-124/Xe-126 omitted; natural abundances not renormalized",
            "Hybrid-9 (AFH-7 + Helm-2)": "AFH v6.0 for seven supported isotopes and Helm for Xe-124/Xe-126",
            "AFH-7 + A2-2 ceiling": "AFH v6.0 for seven supported isotopes and R=A^2 for Xe-124/Xe-126; diagnostic ceiling, not a nuclear model",
            "Helm-9": "Helm response for all nine naturally occurring isotopes; separate model comparison",
        },
        "particle_parameters": {
            "mchi_GeV": args.mchi_GeV, "mV_GeV": args.mV_GeV,
            "coupling_product_squared": args.coupling_product_sq,
            "g2_for_width": args.g2, "rhoDM_GeV_cm3": args.rhoDM_GeV_cm3,
            "benchmarks": {k: BENCHMARKS[k] for k in args.benchmarks},
        },
        "width": {
            "scheme": "constant pole width",
            "assumptions": "Dirac fermions, real scalar, pure scalar off-diagonal Yukawa, only chi2 -> chi1 s open",
            "max_speed_on_shell_exclusion": {
                "vmax_km_s": vmax,
                "minimum_pole_gap_over_isotopes_keV": min(
                    (args.mchi_GeV + BENCHMARKS[k]["delta_m_MeV"] * 1e-3)
                    - math.sqrt(max(
                        global_wmax2(
                            args.mchi_GeV, masses[A]["nuclear_mass_GeV"], vmax
                        )[0] for A in ALL_ISOTOPES
                    ))
                    for k in args.benchmarks
                ) * 1e6,
                "check": "global analytic max over all recoil energies at the SHM maximum lab speed",
            },
        },
        "halo": {
            "model": "truncated Standard Halo Model",
            "v0_km_s": args.v0_km_s, "vE_km_s": args.ve_km_s,
            "vesc_km_s": args.vesc_km_s, "vmax_lab_km_s": vmax,
        },
        "recoil_grid_keV": {
            "minimum": args.er_min_keV, "maximum": args.er_max_keV,
            "fine_step": args.er_step_keV, "fine_max": args.fine_er_max_keV,
            "high_energy_step": args.high_er_step_keV, "points": len(energies),
            "selected_check_points": list(SELECTED_CHECK_ENERGIES_KEV),
        },
        "quadrature": {
            "speed_nodes": args.nv, "kernel_order": [args.nw, args.nz, args.nphi],
            "speed_check_nodes": args.nv_low,
            "kernel_check_order": [args.nw_high, args.nz_high, args.nphi_high],
            "max_speed_relative_difference": max_speed_diff,
            "max_kernel_relative_difference": max_kernel_diff,
            "relative_tolerance": args.max_relative_check,
        },
        "rate_units": "events / kg / day / keV",
        "detector_response_applied": False,
        "not_included": [
            "AFH v6.0 Xe-124/Xe-126 density matrices; these are absent from the official default dispatch",
            "NEST S1/S2 response, efficiency, energy resolution, exposure and LZ likelihood",
            "halo and nuclear-structure uncertainty propagation",
            "annual modulation and time-dependent Earth velocity",
        ],
        "row_counts": {
            "response_model_comparison": len(response_rows),
            "isotope_kernel_integrals": len(kernel_rows),
            "natural_xenon_spectra": len(spectrum_rows),
            "quadrature_crosschecks": len(quadrature_rows),
        },
    }
    metadata_path = args.outdir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    output_files = [response_path, kernel_path, spectrum_path, check_path, metadata_path]
    manifest = "".join(
        f"{sha256_file(path)}  {path.name}\n" for path in output_files
    )
    (args.outdir / "SHA256SUMS.txt").write_text(manifest, encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--afh-source", type=Path,
        default=ROOT / "v6" / "dmformfactor-V6.m",
    )
    parser.add_argument(
        "--weights", type=Path,
        default=HERE / "input" / "natural_xenon_isotope_weights.csv",
    )
    parser.add_argument(
        "--response-dir", type=Path,
        default=HERE / "results" / "full_afh_v6_default_7_isotope_response",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--benchmarks", nargs="+", choices=tuple(BENCHMARKS),
                        default=list(BENCHMARKS))
    parser.add_argument("--er-min-keV", type=float, default=5.0)
    parser.add_argument("--er-max-keV", type=float, default=800.0)
    parser.add_argument("--er-step-keV", type=float, default=5.0)
    parser.add_argument("--fine-er-max-keV", type=float, default=270.0)
    parser.add_argument("--high-er-step-keV", type=float, default=20.0)
    parser.add_argument("--mchi-GeV", type=float, default=1000.0)
    parser.add_argument("--mV-GeV", type=float, default=10.0)
    parser.add_argument("--coupling-product-sq", type=float, default=1.0e-8)
    parser.add_argument("--rhoDM-GeV-cm3", type=float, default=0.3)
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
    parser.add_argument("--skip-crosschecks", action="store_true")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
