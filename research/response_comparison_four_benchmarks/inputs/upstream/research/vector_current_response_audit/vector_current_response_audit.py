#!/usr/bin/env python3
"""Exact four-component dark-matter current audit for the three-body Eq. (6) amplitude.

This extends the committed temporal-current kernel without modifying it.  It
computes L^{mu nu} for mu,nu=0..3, contracts it with a coherent point-charge
current representative J_A^mu=(P+P')^mu, and reports separately
the temporal, spatial, and interference pieces.

It does NOT calculate AFH Sigma'/Sigma''/Delta nuclear matrix elements.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
from pathlib import Path
from typing import Any

import numpy as np
from numpy.polynomial.legendre import leggauss

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KERNEL_DIR = ROOT / "research" / "three_body_calculation_and_validation"
if str(KERNEL_DIR) not in sys.path:
    sys.path.insert(0, str(KERNEL_DIR))

import eq6_kernel as eq6  # noqa: E402

M_N_REFERENCE_GEV = 0.939
MCHI_REFERENCE_GEV = 1000.0
MASS_U_GEV = 0.93149410242
C_KM_S = eq6.C_KM_S


def stable_build_point(
    mchi: float, ms: float, mA: float, ER: float, speed_kms: float,
    delta_W2: float, z: float, phi: float,
) -> eq6.Point:
    """Build a phase-space point using the threshold-stable Kallen variable.

    delta_W2 = W^2 - (mchi + ms)^2.  This is algebraically equivalent to
    eq6_kernel.build_point but avoids subtracting two O(mchi^2) quantities
    near the chi1+s threshold.
    """
    beta = speed_kms / C_KM_S
    gamma = 1.0 / math.sqrt(1.0 - beta * beta)
    Echi = mchi * gamma
    pchi = mchi * gamma * beta
    p = np.array([Echi, 0.0, 0.0, pchi])

    Q_A = math.sqrt(2.0 * mA * ER + ER * ER)
    numerator = (
        2.0 * mchi * ms + ms * ms + delta_W2
        + 2.0 * (Echi + mA) * ER
    )
    cos_theta_q = numerator / (2.0 * pchi * Q_A)
    if abs(cos_theta_q) > 1.0 + 2.0e-8:
        raise ValueError(f"unphysical cos(theta_qA)={cos_theta_q}")
    cos_theta_q = min(1.0, max(-1.0, cos_theta_q))
    sin_theta_q = math.sqrt(max(0.0, 1.0 - cos_theta_q * cos_theta_q))
    q_A = np.array([ER, Q_A * sin_theta_q, 0.0, Q_A * cos_theta_q])
    K = p - q_A

    W2 = (mchi + ms) ** 2 + delta_W2
    W = math.sqrt(W2)
    beta_K = K[1:] / K[0]
    pstar = eq6.boost(p, -beta_K)
    e3 = pstar[1:] / np.linalg.norm(pstar[1:])
    ref = np.array([1.0, 0.0, 0.0])
    if abs(float(np.dot(ref, e3))) > 0.9:
        ref = np.array([0.0, 1.0, 0.0])
    e1 = np.cross(ref, e3)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(e3, e1)

    lam = delta_W2 * (4.0 * mchi * ms + delta_W2)
    k_abs = math.sqrt(max(0.0, lam)) / (2.0 * W)
    E_k = (2.0 * ms * (mchi + ms) + delta_W2) / (2.0 * W)
    E_prime = (2.0 * mchi * (mchi + ms) + delta_W2) / (2.0 * W)
    direction = (
        z * e3
        + math.sqrt(max(0.0, 1.0 - z * z))
        * (math.cos(phi) * e1 + math.sin(phi) * e2)
    )
    k = eq6.boost(np.r_[E_k, k_abs * direction], beta_K)
    p_prime = eq6.boost(np.r_[E_prime, -k_abs * direction], beta_K)
    return eq6.Point(p, p_prime, k, K, q_A, W2)


def vector_current_vertices(
    point: eq6.Point, mchi2: float, denominator_imaginary_part: float = 0.0,
) -> tuple[tuple[np.ndarray, ...], tuple[np.ndarray, ...], tuple[np.ndarray, ...]]:
    """Return before, after, and coherent total Gamma^mu for all four indices.

    The same two scalar-emission orderings as eq6_kernel.vertices are kept.
    The imaginary part is inserted only in the K=p'+k_s chi2 propagator,
    matching the existing Eq. (6) convention.
    """
    r_before, r_after = eq6.chi2_internal_momenta(point)
    d_before = eq6.dot(r_before, r_before) - mchi2 * mchi2
    d_after = (
        point.W2 - mchi2 * mchi2
        + 1j * denominator_imaginary_part
    )
    if abs(d_before) < 1.0e-30 or abs(d_after) < 1.0e-30:
        raise ZeroDivisionError("chi2 propagator pole")
    before = []
    after = []
    total = []
    for mu in range(4):
        g_before = (
            eq6.GAMMA[mu]
            @ (eq6.slash(r_before) + mchi2 * eq6.ID4)
            / d_before
        )
        g_after = (
            (eq6.slash(r_after) + mchi2 * eq6.ID4)
            @ eq6.GAMMA[mu]
            / d_after
        )
        before.append(g_before)
        after.append(g_after)
        total.append(g_before + g_after)
    return tuple(before), tuple(after), tuple(total)


def dm_current_tensor(
    point: eq6.Point, mchi: float, mchi2: float,
    denominator_imaginary_part: float = 0.0,
) -> np.ndarray:
    r"""Compute L^{mu nu}=1/2 Tr[(p'+m) Gamma^mu (p+m) barGamma^nu]."""
    _, _, vertices = vector_current_vertices(
        point, mchi2, denominator_imaginary_part
    )
    p_in = eq6.slash(point.p) + mchi * eq6.ID4
    p_out = eq6.slash(point.p_prime) + mchi * eq6.ID4
    adjoints = tuple(
        eq6.GAMMA[0] @ vertex.conj().T @ eq6.GAMMA[0]
        for vertex in vertices
    )
    tensor = np.empty((4, 4), dtype=complex)
    for mu in range(4):
        for nu in range(4):
            tensor[mu, nu] = (
                np.trace(p_out @ vertices[mu] @ p_in @ adjoints[nu]) / 2.0
            )
    return tensor


def width_imaginary_part(
    point: eq6.Point, mchi: float, ms: float, delta_m: float,
    g2: float, width_scheme: str,
) -> float:
    """Imaginary part of the second chi2 denominator, in GeV^2."""
    mchi2 = mchi + delta_m
    if width_scheme == "zero":
        return 0.0
    if width_scheme == "pole":
        gamma_pole = eq6.chi2_width_dirac_scalar(mchi, ms, delta_m, g2)
        return mchi2 * gamma_pole
    if width_scheme == "running":
        gamma_W = eq6.chi2_width_dirac_scalar_at_mass(
            math.sqrt(point.W2), mchi, ms, g2
        )
        return math.sqrt(point.W2) * gamma_W
    raise ValueError(f"unknown width scheme: {width_scheme}")


def pointlike_coherent_charge_current(point: eq6.Point, mA: float) -> np.ndarray:
    r"""Coherent point-charge current representative; F_A(q_A^2) is factored out."""
    return np.r_[2.0 * mA + point.E_R, point.q_A[1:]]


def contract_nuclear_current(
    tensor: np.ndarray, nuclear_current_upper: np.ndarray,
) -> complex:
    """Contract L^{mu nu} with J_mu J_nu using (+---)."""
    nuclear_current_lower = np.asarray(nuclear_current_upper, dtype=float).copy()
    nuclear_current_lower[1:] *= -1.0
    return np.einsum(
        "m,n,mn->", nuclear_current_lower, nuclear_current_lower, tensor
    )


def decompose_current(
    tensor: np.ndarray, point: eq6.Point, mA: float,
) -> dict[str, float]:
    """Separate coherent charge, nuclear-CM convection, and interference."""
    J = pointlike_coherent_charge_current(point, mA)
    qvec = point.q_A[1:]
    Q_A = float(np.linalg.norm(qvec))
    qhat = qvec / Q_A
    J0 = float(J[0])

    charge = J0 * J0 * tensor[0, 0]
    spatial = np.einsum("i,j,ij->", qvec, qvec, tensor[1:, 1:])
    interference = -J0 * np.dot(
        qvec, tensor[0, 1:] + tensor[1:, 0]
    )
    full = contract_nuclear_current(tensor, J)

    spatial_norm = np.trace(tensor[1:, 1:])
    longitudinal_norm = np.einsum(
        "i,j,ij->", qhat, qhat, tensor[1:, 1:]
    )
    transverse_norm = spatial_norm - longitudinal_norm
    qdotJ = point.E_R * J0 - float(np.dot(qvec, J[1:]))

    return {
        "L00": float(np.real(tensor[0, 0])),
        "Lspatial_trace": float(np.real(spatial_norm)),
        "Llongitudinal": float(np.real(longitudinal_norm)),
        "Ltransverse": float(np.real(transverse_norm)),
        "charge_piece": float(np.real(charge)),
        "spatial_nuclear_piece": float(np.real(spatial)),
        "charge_spatial_interference": float(np.real(interference)),
        "full_point_nucleus": float(np.real(full)),
        "point_nucleus_current_conservation_residual_GeV2": float(qdotJ),
    }


def integrate_current_components(
    *,
    mchi: float, ms: float, delta_m: float, mA: float,
    ER: float, speed_kms: float, g2: float,
    width_scheme: str = "pole", mapping: str = "threshold_u2",
    nw: int = 24, nz: int = 16, nphi: int = 8,
) -> dict[str, Any]:
    """Integrate the full L^{mu nu} and coherent point-charge-current pieces.

    The common Eq. (6) phase-space weight sqrt(lambda_K)/W^2 is included.
    Overall couplings, mediator propagator, and the common external prefactor
    are omitted because they cancel in the reported current ratios.
    """
    if width_scheme not in {"zero", "pole", "running"}:
        raise ValueError("width_scheme must be zero, pole, or running")
    if mapping not in {"threshold_u2", "sine2"}:
        raise ValueError("mapping must be threshold_u2 or sine2")
    if nw < 2 or nz < 2 or nphi < 2:
        raise ValueError("quadrature orders must be at least 2")

    wmin, wmax = eq6.limits(mchi, ms, mA, ER, speed_kms)
    if wmax <= wmin:
        return {
            "phase_space_open": False,
            "mchi_GeV": mchi, "ms_GeV": ms, "delta_m_GeV": delta_m,
            "mA_GeV": mA, "ER_GeV": ER, "speed_kms": speed_kms,
            "width_scheme": width_scheme, "mapping": mapping,
            "nw": nw, "nz": nz, "nphi": nphi,
        }

    xw, ww = leggauss(nw)
    xz, wz = leggauss(nz)
    xp, wp = leggauss(nphi)
    u = 0.5 * (xw + 1.0)
    wu = 0.5 * ww
    z_values = xz
    z_weights = wz
    phi_values = math.pi * (xp + 1.0)
    phi_weights = 0.5 * wp

    delta_W2_max = wmax - wmin
    if mapping == "threshold_u2":
        delta_W2_values = delta_W2_max * u * u
        jacobians = 2.0 * delta_W2_max * u
    else:
        angle = 0.5 * math.pi * u
        delta_W2_values = delta_W2_max * np.sin(angle) ** 2
        jacobians = (
            0.5 * math.pi * delta_W2_max * np.sin(math.pi * u)
        )

    mchi2 = mchi + delta_m
    integrals = {
        "I00": 0.0, "Ispatial_trace": 0.0,
        "Ilongitudinal": 0.0, "Itransverse": 0.0,
        "Icharge": 0.0, "Ispatial_nuclear": 0.0,
        "Iinterference": 0.0, "Ifull": 0.0,
    }
    max_hermiticity_residual = 0.0
    max_current_conservation_residual = 0.0

    for delta_W2, jac, w_weight in zip(
        delta_W2_values, jacobians, wu
    ):
        delta_W2 = float(delta_W2)
        W2 = wmin + delta_W2
        lambda_dimensionless = (
            delta_W2 * (4.0 * mchi * ms + delta_W2) / (W2 * W2)
        )
        phase_weight = float(jac * w_weight) * math.sqrt(
            max(0.0, lambda_dimensionless)
        )
        for z, z_weight in zip(z_values, z_weights):
            for phi, phi_weight in zip(phi_values, phi_weights):
                point = stable_build_point(
                    mchi, ms, mA, ER, speed_kms,
                    delta_W2, float(z), float(phi),
                )
                imag = width_imaginary_part(
                    point, mchi, ms, delta_m, g2, width_scheme
                )
                tensor = dm_current_tensor(
                    point, mchi, mchi2, imag
                )
                decomp = decompose_current(tensor, point, mA)
                scale = max(float(np.max(np.abs(tensor))), 1.0)
                hermiticity = float(
                    np.max(np.abs(tensor - tensor.conj().T)) / scale
                )
                max_hermiticity_residual = max(
                    max_hermiticity_residual, hermiticity
                )
                max_current_conservation_residual = max(
                    max_current_conservation_residual,
                    abs(decomp["point_nucleus_current_conservation_residual_GeV2"]),
                )
                common = phase_weight * float(z_weight) * float(phi_weight)
                integrals["I00"] += common * decomp["L00"]
                integrals["Ispatial_trace"] += (
                    common * decomp["Lspatial_trace"]
                )
                integrals["Ilongitudinal"] += (
                    common * decomp["Llongitudinal"]
                )
                integrals["Itransverse"] += (
                    common * decomp["Ltransverse"]
                )
                integrals["Icharge"] += common * decomp["charge_piece"]
                integrals["Ispatial_nuclear"] += (
                    common * decomp["spatial_nuclear_piece"]
                )
                integrals["Iinterference"] += (
                    common * decomp["charge_spatial_interference"]
                )
                integrals["Ifull"] += common * decomp["full_point_nucleus"]

    Q_A = math.sqrt(2.0 * mA * ER + ER * ER)
    gamma_pole = eq6.chi2_width_dirac_scalar(
        mchi, ms, delta_m, g2
    )
    pole_clearance = mchi2 - math.sqrt(wmax)
    I00 = integrals["I00"]
    Isp = integrals["Ispatial_trace"]
    return {
        "phase_space_open": True,
        "mchi_GeV": mchi, "ms_GeV": ms, "delta_m_GeV": delta_m,
        "mchi2_GeV": mchi2, "mA_GeV": mA, "ER_GeV": ER,
        "ER_keV": ER * 1.0e6, "speed_kms": speed_kms,
        "qA_GeV": Q_A, "qA_over_2mN_reference": Q_A / (2.0 * M_N_REFERENCE_GEV),
        "g2": g2, "width_scheme": width_scheme, "mapping": mapping,
        "nw": nw, "nz": nz, "nphi": nphi,
        "Wmin_minus_mchi_keV": (math.sqrt(wmin) - mchi) * 1.0e6,
        "Wmax_minus_mchi_keV": (math.sqrt(wmax) - mchi) * 1.0e6,
        "pole_clearance_keV": pole_clearance * 1.0e6,
        "Gamma_chi2_keV": gamma_pole * 1.0e6,
        "I00": I00,
        "Ispatial_over_I00": Isp / I00,
        "rchi_spatial_over_temporal": math.sqrt(max(0.0, Isp / I00)),
        "Ilongitudinal_over_I00": integrals["Ilongitudinal"] / I00,
        "Itransverse_over_I00": integrals["Itransverse"] / I00,
        "point_nucleus_full_over_charge": (
            integrals["Ifull"] / integrals["Icharge"]
        ),
        "point_nucleus_spatial_over_charge": (
            integrals["Ispatial_nuclear"] / integrals["Icharge"]
        ),
        "point_nucleus_interference_over_charge": (
            integrals["Iinterference"] / integrals["Icharge"]
        ),
        "orbital_amp_ratio_vN_0p1": (
            math.sqrt(max(0.0, Isp / I00)) * 0.1
        ),
        "orbital_amp_ratio_vN_0p3": (
            math.sqrt(max(0.0, Isp / I00)) * 0.3
        ),
        "minimal_Dirac_magnetization_amp_ratio_per_nucleon": (
            math.sqrt(max(0.0, Isp / I00))
            * Q_A / (2.0 * M_N_REFERENCE_GEV)
        ),
        "max_tensor_hermiticity_relative_residual": max_hermiticity_residual,
        "max_point_nucleus_current_conservation_residual_GeV2": (
            max_current_conservation_residual
        ),
        **{key: float(value) for key, value in integrals.items()},
    }


DEFAULT_CASES = (
    {
        "benchmark": "green_450keV",
        "ms": 300.0e-6, "delta_m": 450.0e-6, "ER": 200.0e-6,
        "speed_kms": 776.0, "g2": 1.0,
        "mapping": "threshold_u2", "nw": 24, "nz": 16, "nphi": 8,
    },
    {
        "benchmark": "green_1MeV",
        "ms": 300.0e-6, "delta_m": 1.0e-3, "ER": 200.0e-6,
        "speed_kms": 776.0, "g2": 1.0,
        "mapping": "threshold_u2", "nw": 24, "nz": 16, "nphi": 8,
    },
    {
        "benchmark": "near_pole_362keV_g2_0p1",
        "ms": 300.0e-6, "delta_m": 362.0e-6, "ER": 267.0e-6,
        "speed_kms": 776.0, "g2": 0.1,
        "mapping": "sine2", "nw": 32, "nz": 16, "nphi": 8,
    },
    {
        "benchmark": "near_pole_362keV_g2_1",
        "ms": 300.0e-6, "delta_m": 362.0e-6, "ER": 267.0e-6,
        "speed_kms": 776.0, "g2": 1.0,
        "mapping": "sine2", "nw": 32, "nz": 16, "nphi": 8,
    },
)


def run_default_audit() -> list[dict[str, Any]]:
    rows = []
    mA = 131.0 * MASS_U_GEV
    for case in DEFAULT_CASES:
        for scheme in ("zero", "pole", "running"):
            result = integrate_current_components(
                mchi=MCHI_REFERENCE_GEV,
                ms=case["ms"], delta_m=case["delta_m"],
                mA=mA, ER=case["ER"], speed_kms=case["speed_kms"],
                g2=case["g2"], width_scheme=scheme,
                mapping=case["mapping"], nw=case["nw"],
                nz=case["nz"], nphi=case["nphi"],
            )
            result["benchmark"] = case["benchmark"]
            rows.append(result)
    return rows


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("refusing to write an empty result table")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    rows = run_default_audit()
    outdir = args.outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "vector_current_response_audit.csv"
    write_csv(csv_path, rows)
    metadata = {
        "status": "reproducible_diagnostic_pending_AFH_nuclear_response_contraction",
        "source_kernel": "research/three_body_calculation_and_validation/eq6_kernel.py",
        "source_commit": "c0cd9a566b570a8f317abfdd20fc7fcdfdde298e",
        "natural_units": "GeV, (+---)",
        "target_mass_convention": "mA=131*u with u=0.93149410242 GeV (matching fixed-speed Xe-131 archive)",
        "amplitude": (
            "Gamma^mu = gamma^mu (slash(p-k_s)+mchi2)/D_before "
            "+ (slash(p'+k_s)+mchi2) gamma^mu/D_after"
        ),
        "tensor": "L^{mu nu}=1/2 Tr[(slash(p')+mchi) Gamma^mu (slash(p)+mchi) barGamma^nu]",
        "nuclear_current": "coherent point-charge current representative J_A^mu=(P+P')^mu; F_A factored out",
        "width_assumptions": (
            "zero/pole/running widths use the existing conditional Dirac, real-scalar, "
            "pure-scalar, single-open-channel chi2->chi1+s prescription; running is diagnostic"
        ),
        "phase_space_mappings": {
            "threshold_u2": "W2=Wmin2+DeltaW2*u^2",
            "sine2": "W2=Wmin2+DeltaW2*sin(pi*u/2)^2",
        },
        "benchmarks": list(DEFAULT_CASES),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "result_file": csv_path.name,
        "result_sha256": sha256_file(csv_path),
        "scope_limitations": [
            "The coherent point-charge current includes only elastic centre-of-mass convection; it does not include internal nuclear orbital or magnetization matrix elements.",
            "The vN=0.1..0.3 and q/(2mN) columns are per-nucleon kinematic amplitude estimates, not AFH nuclear-response ratios.",
            "No AFH Sigma-prime, Sigma-double-prime, or Delta response has been contracted with the three-body tensor.",
            "No mediator propagator, halo integral, isotope abundance sum, detector response, or likelihood is included.",
            "The scalar-only chi2 width omits the unspecified vector-sector self-energy contribution.",
        ],
    }
    metadata_path = outdir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    sums_path = outdir / "SHA256SUMS.txt"
    sums_path.write_text(
        f"{sha256_file(csv_path)}  {csv_path.name}\n"
        f"{sha256_file(metadata_path)}  {metadata_path.name}\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": metadata["status"],
        "rows": len(rows),
        "result": str(csv_path),
        "sha256": metadata["result_sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
