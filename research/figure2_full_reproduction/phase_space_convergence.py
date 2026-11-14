"""Independent phase-space quadrature audits for the three-body Eq. (6) kernel.

The committed eq6_kernel.py remains the amplitude baseline. This module
independently changes the W^2 parameterization and phase-space measure:
  * threshold-regularized W^2 = W_min^2 + Delta*u^2;
  * linear-W with the explicit dW^2 = 2 W dW Jacobian;
  * raw, unaveraged dPhi_3 integration to reconstruct the Eq. (6) prefactor.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
from numpy.polynomial.legendre import leggauss

try:
    import eq6_kernel as eq6
except ImportError:  # pragma: no cover
    from . import eq6_kernel as eq6


def _legendre(order: int):
    if order < 1:
        raise ValueError("quadrature orders must be positive")
    return leggauss(int(order))


def _stable_build_point(
    mchi: float, ms: float, mA: float, ER: float, speed_kms: float,
    delta_W2: float, z: float, phi: float,
):
    """Build a phase-space point carrying delta=W^2-W_min^2 explicitly."""
    beta = speed_kms / eq6.C_KM_S
    gamma = 1.0 / math.sqrt(1.0 - beta * beta)
    Echi = mchi * gamma
    pchi = mchi * gamma * beta
    p = np.array([Echi, 0.0, 0.0, pchi])
    qmag = math.sqrt(2.0 * mA * ER + ER * ER)
    numerator = (
        2.0 * mchi * ms + ms * ms + delta_W2
        + 2.0 * (Echi + mA) * ER
    )
    cos_q = numerator / (2.0 * pchi * qmag)
    if abs(cos_q) > 1.0 + 2e-8:
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
    if lam_kallen < -1e-14:
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


def _trace(
    mchi: float, ms: float, delta_m: float, mA: float, ER: float,
    speed_kms: float, W2: float, delta_W2: float, z: float, phi: float,
    width_scheme: str, g2: float,
) -> float:
    point = _stable_build_point(mchi, ms, mA, ER, speed_kms, delta_W2, z, phi)
    mchi2 = mchi + delta_m
    if width_scheme == "zero":
        width, running_width = 0.0, None
    elif width_scheme == "pole":
        width = eq6.chi2_width_dirac_scalar(mchi, ms, delta_m, g2)
        running_width = None
    elif width_scheme == "running":
        width = 0.0
        running_width = eq6.chi2_width_dirac_scalar_at_mass(
            math.sqrt(W2), mchi, ms, g2
        )
    else:
        raise ValueError("width_scheme must be zero, pole, or running")
    return eq6.spin_trace(
        point, mchi, mchi2, width=width, running_width=running_width
    )["total"]


def _integrate(
    mchi: float, ms: float, delta_m: float, mA: float, ER: float,
    speed_kms: float, nW: int, nz: int, nphi: int,
    mapping: str, phi_measure: str = "average",
    width_scheme: str = "pole", g2: float = 1.0,
) -> float:
    """Integrate sqrt(lambda_dim)*L00 over dW2 dz and the selected phi measure."""
    if min(mchi, mA) <= 0.0 or min(ms, ER, speed_kms, delta_m) < 0.0:
        raise ValueError("invalid non-positive physical input")
    wmin2, wmax2 = eq6.limits(mchi, ms, mA, ER, speed_kms)
    if wmax2 <= wmin2:
        return 0.0

    xW, wW = _legendre(nW)
    xz, wz = _legendre(nz)
    xp, wp = _legendre(nphi)

    if mapping == "linear_w2":
        W2_values = 0.5 * (wmax2 + wmin2) + 0.5 * (wmax2 - wmin2) * xW
        W2_weights = 0.5 * (wmax2 - wmin2) * wW
        delta_values = W2_values - wmin2
    elif mapping == "linear_w":
        Wmin, Wmax = math.sqrt(wmin2), math.sqrt(wmax2)
        W_values = 0.5 * (Wmax + Wmin) + 0.5 * (Wmax - Wmin) * xW
        W_weights = 0.5 * (Wmax - Wmin) * wW
        W2_values = W_values * W_values
        W2_weights = W_weights * (2.0 * W_values)
        delta_values = (W_values - Wmin) * (W_values + Wmin)
    elif mapping == "threshold_u2":
        u_values = 0.5 * (xW + 1.0)
        u_weights = 0.5 * wW
        delta = wmax2 - wmin2
        delta_values = delta * u_values * u_values
        W2_values = wmin2 + delta_values
        W2_weights = u_weights * (2.0 * delta * u_values)
    else:
        raise ValueError("unknown W mapping")

    phi_values = math.pi * (xp + 1.0)
    if phi_measure == "average":
        phi_weights = 0.5 * wp
    elif phi_measure == "raw":
        phi_weights = math.pi * wp
    else:
        raise ValueError("phi_measure must be average or raw")

    total = 0.0
    for W2, delta_W2, weightW in zip(W2_values, delta_values, W2_weights):
        W2 = float(W2)
        delta_W2 = float(delta_W2)
        lam = delta_W2 * (4.0 * mchi * ms + delta_W2) / (W2 * W2)
        if lam < 0.0:
            if lam > -1e-14:
                lam = 0.0
            else:
                raise ArithmeticError(f"negative Kallen lambda: {lam}")
        angular = 0.0
        for z, weightz in zip(xz, wz):
            azimuth = 0.0
            for phi, weightphi in zip(phi_values, phi_weights):
                azimuth += float(weightphi) * _trace(
                    mchi, ms, delta_m, mA, ER, speed_kms,
                    W2, delta_W2, float(z), float(phi), width_scheme, g2,
                )
            angular += float(weightz) * azimuth
        total += float(weightW) * math.sqrt(lam) * angular
    return float(total)


def integrate_i6(
    mchi: float, ms: float, delta_m: float, mA: float, ER: float,
    speed_kms: float, nW: int = 16, nz: int = 16, nphi: int = 8,
    mapping: str = "threshold_u2", width_scheme: str = "pole", g2: float = 1.0,
) -> float:
    """Return I6 with the normalized azimuthal average."""
    return _integrate(
        mchi, ms, delta_m, mA, ER, speed_kms, nW, nz, nphi,
        mapping, "average", width_scheme, g2,
    )


def integrate_raw_li_phase_space(
    mchi: float, ms: float, delta_m: float, mA: float, ER: float,
    speed_kms: float, nW: int = 16, nz: int = 16, nphi: int = 8,
    mapping: str = "threshold_u2", width_scheme: str = "pole", g2: float = 1.0,
) -> float:
    """Return the raw dphi integral (without 1/(2*pi) normalization)."""
    return _integrate(
        mchi, ms, delta_m, mA, ER, speed_kms, nW, nz, nphi,
        mapping, "raw", width_scheme, g2,
    )


def cross_section_eq6(
    I6: float, mchi: float, mA: float, ER: float, speed_kms: float,
    mV: float = 10.0, coupling_product_squared: float = 1.0, RA: float = 1.0,
) -> float:
    beta = speed_kms / eq6.C_KM_S
    gamma = 1.0 / math.sqrt(1.0 - beta * beta)
    pchi = mchi * gamma * beta
    denominator = (mV * mV + 2.0 * mA * ER) ** 2
    return (
        mA * coupling_product_squared * RA * I6
        / (256.0 * math.pi**3 * pchi**2 * denominator)
    )


def cross_section_direct_li(
    raw_integral: float, mchi: float, mA: float, ER: float, speed_kms: float,
    mV: float = 10.0, coupling_product_squared: float = 1.0, RA: float = 1.0,
) -> float:
    beta = speed_kms / eq6.C_KM_S
    gamma = 1.0 / math.sqrt(1.0 - beta * beta)
    pchi = mchi * gamma * beta
    denominator = (mV * mV + 2.0 * mA * ER) ** 2
    return (
        mA * coupling_product_squared * RA * raw_integral
        / (512.0 * math.pi**4 * pchi**2 * denominator)
    )


def benchmark_cases():
    return [
        ("green_ER200_v776", 1000.0, 300e-6, 1e-3, 122.0, 200e-6, 776.0),
        ("green_ER267_v776", 1000.0, 300e-6, 1e-3, 122.0, 267e-6, 776.0),
        ("green_ER542_v776", 1000.0, 300e-6, 1e-3, 122.0, 542e-6, 776.0),
        ("red_ER101_v776", 1000.0, 200e-6, 1e-3, 122.0, 101e-6, 776.0),
    ]


def _write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _vmin_kms(mchi: float, ms: float, mA: float, ER: float) -> float:
    q = math.sqrt(2.0 * mA * ER + ER * ER)
    a = ms + (mA * ER + 0.5 * ms * ms) / mchi
    beta = (q * ER + a * math.sqrt(q * q - ER * ER + a * a)) / (q * q + a * a)
    return eq6.C_KM_S * beta


def run_mapping_scan(output_dir: Path, nref: int = 32):
    rows = []
    for name, mchi, ms, dm, mA, ER, speed in benchmark_cases():
        reference = integrate_i6(
            mchi, ms, dm, mA, ER, speed,
            nW=nref, nz=24, nphi=16, mapping="threshold_u2",
        )
        configs = (
            ("linear-W2", "linear_w2", 8, 8, 4),
            ("linear-W2", "linear_w2", 16, 16, 8),
            ("linear-W", "linear_w", 8, 8, 4),
            ("threshold-u2", "threshold_u2", 4, 4, 4),
            ("threshold-u2", "threshold_u2", 6, 6, 4),
            ("threshold-u2", "threshold_u2", 8, 8, 4),
            ("threshold-u2", "threshold_u2", 12, 12, 6),
            ("threshold-u2", "threshold_u2", 16, 16, 8),
            ("threshold-u2", "threshold_u2", 24, 24, 12),
        )
        for method, mapping, nW, nz, nphi in configs:
            value = integrate_i6(
                mchi, ms, dm, mA, ER, speed,
                nW=nW, nz=nz, nphi=nphi, mapping=mapping,
            )
            wmin2, wmax2 = eq6.limits(mchi, ms, mA, ER, speed)
            rows.append({
                "case": name, "mapping": method,
                "delta_W2_GeV2": f"{wmax2-wmin2:.14g}",
                "nW_or_nu": nW, "nz": nz, "nphi": nphi,
                "I6_GeV2": f"{value:.14g}",
                "reference_I6_GeV2": f"{reference:.14g}",
                "relative_difference_to_threshold_reference": f"{value/reference-1.0:.12e}",
            })
    _write_csv(output_dir / "phase_space_mapping_convergence.csv", rows)
    return rows


def run_angular_scan(output_dir: Path):
    _, mchi, ms, dm, mA, ER, speed = benchmark_cases()[0]
    zref = integrate_i6(
        mchi, ms, dm, mA, ER, speed, nW=8, nz=24, nphi=8,
    )
    phiref = integrate_i6(
        mchi, ms, dm, mA, ER, speed, nW=8, nz=8, nphi=16,
    )
    rows = []
    for nz in (2, 4, 6, 8, 12, 16, 24):
        value = integrate_i6(
            mchi, ms, dm, mA, ER, speed, nW=8, nz=nz, nphi=8,
        )
        rows.append({
            "dimension": "z", "order": nz, "fixed_nW": 8, "fixed_other_order": 8,
            "I6_GeV2": f"{value:.14g}",
            "relative_difference": f"{value/zref-1.0:.12e}",
        })
    for nphi in (2, 3, 4, 6, 8, 12, 16, 20):
        value = integrate_i6(
            mchi, ms, dm, mA, ER, speed, nW=8, nz=8, nphi=nphi,
        )
        rows.append({
            "dimension": "phi", "order": nphi, "fixed_nW": 8, "fixed_other_order": 8,
            "I6_GeV2": f"{value:.14g}",
            "relative_difference": f"{value/phiref-1.0:.12e}",
        })
    _write_csv(output_dir / "phase_space_angular_convergence.csv", rows)
    return rows


def run_threshold_scan(output_dir: Path):
    _, mchi, ms, dm, mA, ER, _ = benchmark_cases()[2]
    vmin = _vmin_kms(mchi, ms, mA, ER)
    rows = []
    for dv in (0.1, 0.5, 1.0, 2.0, 5.0):
        speed = vmin + dv
        reference = integrate_i6(
            mchi, ms, dm, mA, ER, speed, nW=24, nz=4, nphi=4,
        )
        configs = (
            ("linear_w2", "linear-W2", 8),
            ("linear_w2", "linear-W2", 16),
            ("threshold_u2", "threshold-u2", 4),
            ("threshold_u2", "threshold-u2", 6),
            ("threshold_u2", "threshold-u2", 8),
            ("threshold_u2", "threshold-u2", 12),
            ("threshold_u2", "threshold-u2", 16),
            ("threshold_u2", "threshold-u2", 24),
        )
        for mapping, label, nW in configs:
            value = integrate_i6(
                mchi, ms, dm, mA, ER, speed, nW=nW, nz=4, nphi=4,
                mapping=mapping,
            )
            wmin2, wmax2 = eq6.limits(mchi, ms, mA, ER, speed)
            rows.append({
                "delta_v_km_s": dv, "v_kms": f"{speed:.12g}",
                "delta_W2_GeV2": f"{wmax2-wmin2:.14g}",
                "mapping": label, "nW_or_nu": nW,
                "I6_GeV2": f"{value:.14g}",
                "reference_I6_GeV2": f"{reference:.14g}",
                "relative_difference": f"{value/reference-1.0:.12e}",
            })
    _write_csv(output_dir / "phase_space_threshold_convergence.csv", rows)
    return rows


def run_prefactor_check(output_dir: Path):
    name, mchi, ms, dm, mA, ER, speed = benchmark_cases()[0]
    raw = integrate_raw_li_phase_space(
        mchi, ms, dm, mA, ER, speed, nW=8, nz=8, nphi=4,
    )
    i6 = integrate_i6(
        mchi, ms, dm, mA, ER, speed, nW=8, nz=8, nphi=4,
    )
    ds_eq6 = cross_section_eq6(i6, mchi, mA, ER, speed)
    ds_li = cross_section_direct_li(raw, mchi, mA, ER, speed)
    rows = [{
        "case": name, "I6_GeV2": f"{i6:.14g}",
        "raw_phi_integral_GeV2": f"{raw:.14g}",
        "raw_over_2pi_I6": f"{raw/(2.0*math.pi*i6):.14g}",
        "dsigma_dER_eq6_GeV_minus3": f"{ds_eq6:.14g}",
        "dsigma_dER_direct_LI_GeV_minus3": f"{ds_li:.14g}",
        "direct_over_eq6": f"{ds_li/ds_eq6:.14g}",
    }]
    _write_csv(output_dir / "phase_space_li_prefactor_crosscheck.csv", rows)
    return rows



def run_historical_800_anchor(output_dir: Path):
    """Separate the historical A*u mass convention from W2 quadrature error."""
    mchi, ms, dm = 1000.0, 300e-6, 1e-3
    ER, speed = 200e-6, 800.0
    archived_i6 = 1433678.0722867665
    mass_schemes = (
        ("historical_A_times_u_approx", 122.0),
        ("NIST_Xe131_nuclear_mass", 131.0 * 0.93149410242),
    )
    rows = []
    summaries = []
    for mass_scheme, mA in mass_schemes:
        reference = integrate_i6(
            mchi, ms, dm, mA, ER, speed,
            nW=48, nz=40, nphi=24, mapping="threshold_u2",
        )
        legacy = eq6.reduced_kernel(
            mchi, ms, dm, mA, ER, speed,
            nw=16, nz=16, nphi=8, width_scheme="pole", g2=1.0,
        )
        configs = (
            ("legacy_eq6_linear_W2", "linear_w2", 16, 16, 8, legacy),
            ("independent_linear_W2", "linear_w2", 16, 16, 8, integrate_i6(
                mchi, ms, dm, mA, ER, speed,
                nW=16, nz=16, nphi=8, mapping="linear_w2",
            )),
            ("threshold_u2", "threshold_u2", 8, 8, 4, integrate_i6(
                mchi, ms, dm, mA, ER, speed,
                nW=8, nz=4, nphi=4, mapping="threshold_u2",
            )),
            ("threshold_u2", "threshold_u2", 16, 16, 8, integrate_i6(
                mchi, ms, dm, mA, ER, speed,
                nW=16, nz=16, nphi=8, mapping="threshold_u2",
            )),
            ("threshold_u2", "threshold_u2", 24, 24, 12, integrate_i6(
                mchi, ms, dm, mA, ER, speed,
                nW=24, nz=24, nphi=12, mapping="threshold_u2",
            )),
            ("threshold_u2_reference", "threshold_u2", 48, 40, 24, reference),
        )
        for label, mapping, nW, nz, nphi, value in configs:
            rows.append({
                "case": "green_ER200_v800",
                "mass_scheme": mass_scheme,
                "mchi_GeV": f"{mchi:.14g}",
                "ms_keV": f"{ms*1e6:.14g}",
                "Delta_m_MeV": f"{dm*1e3:.14g}",
                "mA_GeV": f"{mA:.14g}",
                "ER_keV": f"{ER*1e6:.14g}",
                "speed_km_s": f"{speed:.14g}",
                "implementation": label,
                "mapping": mapping,
                "nW": nW,
                "nz": nz,
                "nphi": nphi,
                "I6_GeV2": f"{value:.14g}",
                "archived_I6_GeV2": f"{archived_i6:.14g}",
                "relative_to_archived": f"{value/archived_i6-1.0:.12e}",
                "reference_I6_GeV2": f"{reference:.14g}",
                "relative_to_high_order_reference": f"{value/reference-1.0:.12e}",
            })
        summaries.append({
            "mass_scheme": mass_scheme,
            "mA_GeV": mA,
            "legacy_I6_GeV2": legacy,
            "threshold_u2_reference_I6_GeV2": reference,
            "legacy_relative_to_archive": legacy/archived_i6-1.0,
            "legacy_relative_to_high_order": legacy/reference-1.0,
        })
    _write_csv(output_dir / "phase_space_historical_800_anchor.csv", rows)
    print("historical 800-km/s anchor:", json.dumps({
        "archived_I6_GeV2": archived_i6,
        "mass_scheme_comparison": summaries,
        "interpretation": "A*u versus NIST nuclear-mass input and linear-W2 versus threshold-u2 quadrature are reported separately.",
    }))
    return rows


def run_scan(
    output_dir: Path, nref: int = 48,
    modes: Iterable[str] = ("mapping", "angular", "threshold", "prefactor"),
):
    results = {}
    for mode in modes:
        if mode == "mapping":
            results[mode] = run_mapping_scan(output_dir, nref)
        elif mode == "angular":
            results[mode] = run_angular_scan(output_dir)
        elif mode == "threshold":
            results[mode] = run_threshold_scan(output_dir)
        elif mode == "prefactor":
            results[mode] = run_prefactor_check(output_dir)
        elif mode == "historical_800":
            results[mode] = run_historical_800_anchor(output_dir)
        else:
            raise ValueError(f"unknown scan mode: {mode}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_names = [
        "phase_space_mapping_convergence.csv",
        "phase_space_angular_convergence.csv",
        "phase_space_threshold_convergence.csv",
        "phase_space_li_prefactor_crosscheck.csv",
        "phase_space_historical_800_anchor.csv",
    ]
    output_records = {}
    for name in output_names:
        path = output_dir / name
        if path.exists():
            output_records[name] = {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            }
    metadata = {
        "calculation": "P1 independent three-body phase-space quadrature convergence",
        "date": "2026-11-14",
        "units": {"mass_energy_momentum": "GeV", "speed": "km/s", "I6": "GeV^2"},
        "matrix_element": "reuses the committed Dirac spin_trace in eq6_kernel.py; independent part is phase-space mapping and measure",
        "width_scheme": "pole",
        "g2": 1.0,
        "reference_quadrature": {
            "mapping": "W2 = Wmin2 + (Wmax2-Wmin2)*u^2",
            "orders": {"u": nref, "z": 24, "phi": 16},
            "azimuth": "normalized average for I6; raw dphi for the direct LI prefactor check",
        },
        "stable_threshold_kinematics": "delta = W2-Wmin2 is carried explicitly; lambda_dim = delta*(4*mchi*ms+delta)/W2^2",
        "cross_section_prefactor_test": {
            "mV_GeV": 10.0, "coupling_product_squared": 1.0, "RA": 1.0,
            "comparison": "Eq. (6) normalized-phi result versus direct raw-dphi Lorentz-invariant dPhi3 measure",
        },
        "scope": "four selected fixed-speed 776-km/s benchmark points, five vmin-offset threshold checks, and one historical 800-km/s green benchmark anchor; not a halo fold, full model scan, resonance-boundary scan, or detector likelihood",
        "matrix_element_source": "eq6_kernel.py committed Dirac trace and spinor amplitude; unchanged by this audit",
        "audit_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "outputs": output_records,
    }
    metadata_path = output_dir / "phase_space_convergence_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    manifest_paths = [output_dir / name for name in output_names] + [metadata_path]
    manifest = "".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
        for path in manifest_paths
    )
    (output_dir / "SHA256SUMS.txt").write_text(manifest, encoding="utf-8")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path(__file__).resolve().parent / "results" / "phase_space_convergence_2026-11-14",
    )
    parser.add_argument("--reference-order", type=int, default=48)
    parser.add_argument(
        "--mode", choices=("all", "mapping", "angular", "threshold", "prefactor", "historical_800"),
        default="all",
    )
    args = parser.parse_args()
    modes = ("mapping", "angular", "threshold", "prefactor", "historical_800") if args.mode == "all" else (args.mode,)
    results = run_scan(args.output_dir, args.reference_order, modes)
    print("completed:", ", ".join(results))
    for mode, rows in results.items():
        print(f"{mode}: {len(rows)} rows")
    if "prefactor" in results:
        print(results["prefactor"][0])


if __name__ == "__main__":
    main()
