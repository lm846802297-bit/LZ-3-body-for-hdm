#!/usr/bin/env python3
"""Natural-xenon halo fold with the B finite-t_N AFH M-only baseline.

The primary reported rate is B = c_M(Fhat_1(t_N),Fhat_2(t_N))^2
L_C W_M(y_A), with the finite-size AFH M response retained and no additional
AFH responses. The module also computes the separate C charge-sector
extension (Phi'', M-Phi''), and optionally a provisional leading-static
spatial-current candidate. L_C uses nuclear-current continuity and is
conditional on conservation of the complete nuclear vector current; the
algebraic point-nucleus identity is not a dynamical proof of that condition.
The result is not the complete L_mu_nu W_A^{mu nu} contraction until P3 passes.
The public rate prefactor uses (g1*g2*gVN)^2, so the current coefficients
must use Fhat_i=F_i^(u+d+s)/3.
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
from scipy.interpolate import PchipInterpolator
from numpy.polynomial.legendre import leggauss

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HALO_INPUT = ROOT / "research" / "afh_default_density_natural_xenon_halo" / "input"
sys_path = ROOT / "research" / "three_body_full_current_nucleon_match"
import sys
if str(sys_path) not in sys.path:
    sys.path.insert(0, str(sys_path))

from nucleon_vector_form_factors import (  # noqa: E402
    F1V0,
    F2V0,
    F1N0,
    F2N0,
    bishara_linear,
    isoscalar_zexp,
    effective_nucleon_form_factors,
    charge_coefficients,
)
from three_body_phase_space_tensor import integrate_spin_resolved_tensor  # noqa: E402
from three_body_multipole_leptonic_weights import (  # noqa: E402
    DEFAULT_MN_GEV,
    extract_afh_vector_coefficients,
)

C_KM_S = 299792.458
C_CM_S = 2.99792458e10
GEV2_TO_CM2 = 0.3893793721e-27
AVOGADRO = 6.02214076e23
U_GEV = 0.93149410242
ME_U = 0.000548579909065
Z_XE = 54
MCHI_DEFAULT = 1000.0
MV_DEFAULT = 10.0
RHO_DEFAULT = 0.3
G2_DEFAULT = 1.0
COUPLING_PRODUCT_SQUARED_DEFAULT = 1.0e-8

ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
J_BY_A = {128: 0.0, 129: 0.5, 130: 0.0, 131: 1.5, 132: 0.0, 134: 0.0, 136: 0.0}
RESPONSE_NAMES = ("M", "PhiPP", "MPhiPP")
RESPONSE_W_COLUMNS = {
    "M": "W_M00_AFH",
    "PhiPP": "W_PhiPP00_AFH",
    "MPhiPP": "W_MPhiPP00_AFH",
}
NATIVE_AFH_SOURCE_COMMIT = "dcefbeb7ad705b6c03f2b4689200eb1d9252e67b"
NATIVE_AFH_REPOSITORY = "lm846802297-bit/LZ-3-body-for-hdm"
NATIVE_RESPONSE_INDEX_MAP = {
    "M": 1,
    "SigmaDoublePrime": 2,
    "SigmaPrime": 3,
    "PhiPP": 4,
    "PhiTildePrime": 5,
    "Delta": 6,
    "MPhiPP": 7,
    "SigmaPrimeDelta": 8,
}
NATIVE_RESPONSE_W_COLUMNS = {
    "M": "W_M00_AFH",
    "SigmaDoublePrime": "W_SigmaDoublePrime00_AFH",
    "SigmaPrime": "W_SigmaPrime00_AFH",
    "PhiPP": "W_PhiPP00_AFH",
    "PhiTildePrime": "W_PhiTildePrime00_AFH",
    "Delta": "W_Delta00_AFH",
    "MPhiPP": "W_MPhiPP00_AFH",
    "SigmaPrimeDelta": "W_SigmaPrimeDelta00_AFH",
}
FULL_VECTOR_RESPONSE_NAMES = tuple(NATIVE_RESPONSE_W_COLUMNS)
NATIVE_EXPECTED_ROWS = len(ISOTOPES) * 2401

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def load_isotope_inputs(path: Path = HALO_INPUT / "natural_xenon_isotope_weights.csv") -> dict[int, dict]:
    rows = read_csv(path)
    data = {}
    for row in rows:
        A = int(row["A"])
        if row["AFH_default_density_available"].lower() != "true":
            continue
        data[A] = {
            "abundance": float(row["natural_atom_fraction"]),
            "atomic_mass_u": float(row["atomic_mass_u"]),
            "mA_GeV": (float(row["atomic_mass_u"]) - Z_XE * ME_U) * U_GEV,
        }
    if tuple(sorted(data)) != ISOTOPES:
        raise ValueError(f"expected AFH isotope set {ISOTOPES}, got {tuple(sorted(data))}")
    return data


def exact_qA_GeV(mA_GeV: float, ER_keV: float) -> float:
    """Exact spatial recoil momentum |q_A| from P_A'^2=P_A^2=m_A^2."""
    ER = float(ER_keV) * 1.0e-6
    if ER < 0.0 or mA_GeV <= 0.0:
        raise ValueError("invalid recoil or nuclear mass")
    return math.sqrt(2.0 * mA_GeV * ER + ER * ER)


def nuclear_transfer_invariant_tA_GeV2(mA_GeV: float, ER_keV: float) -> float:
    """Exact Lorentz invariant t_A=q_A^mu q_{A,mu} for a target initially at rest."""
    ER = float(ER_keV) * 1.0e-6
    if ER < 0.0 or mA_GeV <= 0.0:
        raise ValueError("invalid recoil or nuclear mass")
    return -2.0 * mA_GeV * ER


def mediator_denominator_squared_GeV4(
    mV_GeV: float, mA_GeV: float, ER_keV: float
) -> float:
    """Return (m_V^2-t_A)^2; do not substitute spatial |q_A|^2 for t_A."""
    if mV_GeV <= 0.0:
        raise ValueError("mediator mass must be positive")
    tA = nuclear_transfer_invariant_tA_GeV2(mA_GeV, ER_keV)
    return (mV_GeV * mV_GeV - tA) ** 2


def vmin_three_body_km_s(mchi: float, ms: float, mA: float, ER_keV: float) -> float:
    ER = ER_keV * 1.0e-6
    q = exact_qA_GeV(mA, ER_keV)
    a = ms + (mA * ER + 0.5 * ms * ms) / mchi
    beta = (q * ER + a * math.sqrt(q * q - ER * ER + a * a)) / (q * q + a * a)
    return C_KM_S * beta


def mb_untruncated_pdf(v: float, v0: float = 220.0, ve: float = 232.0) -> float:
    if v < 0.0:
        return 0.0
    return v / (math.sqrt(math.pi) * v0 * ve) * (
        math.exp(-((v - ve) / v0) ** 2)
        - math.exp(-((v + ve) / v0) ** 2)
    )


def shm_truncated_pdf(
    v: float, v0: float = 220.0, ve: float = 232.0, vesc: float = 544.0
) -> float:
    if v < 0.0 or v > vesc + ve:
        return 0.0
    z = vesc / v0
    norm = math.erf(z) - 2.0 * z / math.sqrt(math.pi) * math.exp(-z * z)
    if v < vesc - ve:
        bracket = math.exp(-((v - ve) / v0) ** 2) - math.exp(-((v + ve) / v0) ** 2)
    else:
        bracket = math.exp(-((v - ve) / v0) ** 2) - math.exp(-z * z)
    return v * bracket / (math.sqrt(math.pi) * v0 * ve * norm)


def _verify_native_archive_hashes(
    artifact_root: Path, required_relative_paths: list[str]
) -> list[str]:
    checksum_path = artifact_root / "SHA256SUMS.txt"
    if not checksum_path.is_file():
        raise RuntimeError("native AFH artifact is missing SHA256SUMS.txt")
    recorded = {}
    for line_number, line in enumerate(
        checksum_path.read_text(encoding="ascii").splitlines(), start=1
    ):
        if not line.strip():
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            raise RuntimeError(
                f"malformed native AFH checksum line {line_number}"
            )
        digest, relative = parts
        relative = relative.replace("\\", "/")
        if relative in recorded:
            raise RuntimeError(f"duplicate native AFH checksum path: {relative}")
        recorded[relative] = digest.lower()

    verified = []
    for relative in required_relative_paths:
        path = artifact_root / Path(relative)
        if not path.is_file():
            raise RuntimeError(f"native AFH artifact is missing required file: {relative}")
        expected = recorded.get(relative.replace("\\", "/"))
        if expected is None:
            raise RuntimeError(f"native AFH checksum manifest omits: {relative}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(
                f"native AFH SHA-256 mismatch for {relative}: "
                f"expected {expected}, got {actual}"
            )
        verified.append(relative.replace("\\", "/"))
    return verified


def _native_validation_gate(artifact_root: Path) -> dict:
    """Require the complete, provenance-pinned native AFH-8 artifact.

    The private runner artifact has this layout:
      native/afh_v6_xe*_eight_response_native.csv
      native/native_metadata.txt
      native-comparison.json
      run_manifest.json
      SHA256SUMS.txt
    """
    comparison_path = artifact_root / "native-comparison.json"
    run_manifest_path = artifact_root / "run_manifest.json"
    native_data_dir = (
        artifact_root / "native"
        if (artifact_root / "native").is_dir()
        else artifact_root
    )
    metadata_path = native_data_dir / "native_metadata.txt"
    if not comparison_path.is_file():
        raise RuntimeError(
            "native AFH comparison manifest is missing; do not use raw native CSVs "
            "before the 16,807-row pointwise comparison passes"
        )
    if not run_manifest_path.is_file():
        raise RuntimeError("native AFH run_manifest.json is missing")
    if not metadata_path.is_file():
        raise RuntimeError("native AFH native_metadata.txt is missing")

    comparison = json.loads(comparison_path.read_text(encoding="utf-8-sig"))
    manifest = json.loads(run_manifest_path.read_text(encoding="utf-8-sig"))
    expected_isotopes = list(ISOTOPES)
    expected_response_names = set(NATIVE_RESPONSE_INDEX_MAP)
    failures = []

    if comparison.get("status") != "PASS":
        failures.append(f"comparison status={comparison.get('status')}")
    if comparison.get("native_afh_validated") is not True:
        failures.append("native_afh_validated is not true")
    if comparison.get("rows_compared") != NATIVE_EXPECTED_ROWS:
        failures.append(f"rows_compared={comparison.get('rows_compared')}")
    if comparison.get("expected_rows") != NATIVE_EXPECTED_ROWS:
        failures.append(f"expected_rows={comparison.get('expected_rows')}")
    if comparison.get("python_rows") != NATIVE_EXPECTED_ROWS:
        failures.append(f"python_rows={comparison.get('python_rows')}")
    if comparison.get("native_rows") != NATIVE_EXPECTED_ROWS:
        failures.append(f"native_rows={comparison.get('native_rows')}")
    if comparison.get("isotopes") != expected_isotopes:
        failures.append(f"isotopes={comparison.get('isotopes')}")
    if comparison.get("expected_points_per_isotope") != 2401:
        failures.append(
            f"expected_points_per_isotope="
            f"{comparison.get('expected_points_per_isotope')}"
        )
    if comparison.get("failures") != []:
        failures.append("comparison failures list is not empty")

    max_differences = comparison.get("max_differences")
    if not isinstance(max_differences, dict) or set(max_differences) != expected_response_names:
        failures.append("comparison does not contain all eight AFH response channels")
    else:
        for name, metrics in max_differences.items():
            try:
                max_abs = float(metrics["max_abs"])
                max_rel = float(metrics["max_rel"])
            except (KeyError, TypeError, ValueError):
                failures.append(f"invalid comparison maxima for {name}")
                continue
            if not math.isfinite(max_abs) or not math.isfinite(max_rel):
                failures.append(f"non-finite comparison maxima for {name}")
            elif max_abs < 0.0 or max_rel < 0.0:
                failures.append(f"negative comparison maxima for {name}")

    for field, maximum in (
        ("rtol", 5.0e-7),
        ("atol", 2.0e-12),
        ("imaginary_atol", 2.0e-12),
    ):
        try:
            value = float(comparison[field])
        except (KeyError, TypeError, ValueError):
            failures.append(f"missing/invalid comparison tolerance {field}")
            continue
        if not math.isfinite(value) or value > maximum:
            failures.append(f"comparison tolerance {field}={value} exceeds {maximum}")

    expected_q_grid = {
        "points": 2401,
        "q_min_GeV": 0.0,
        "q_max_GeV": 0.6,
        "step_GeV": 0.00025,
    }
    expected_manifest = {
        "repository": NATIVE_AFH_REPOSITORY,
        "source_commit": NATIVE_AFH_SOURCE_COMMIT,
        "native_package": "AFH DMFormFactor v6.0",
        "isotopes": expected_isotopes,
        "response_indices": NATIVE_RESPONSE_INDEX_MAP,
    }
    for field, expected in expected_manifest.items():
        if manifest.get(field) != expected:
            failures.append(f"run manifest {field} mismatch")
    q_grid = manifest.get("q_grid")
    if not isinstance(q_grid, dict):
        failures.append("run manifest q_grid is missing")
    else:
        for field, expected in expected_q_grid.items():
            try:
                actual = float(q_grid[field])
            except (KeyError, TypeError, ValueError):
                failures.append(f"run manifest q_grid.{field} is missing/invalid")
                continue
            if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1.0e-14):
                failures.append(
                    f"run manifest q_grid.{field}={actual} != {expected}"
                )

    for field in ("wolfram_version", "python_version"):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            failures.append(f"run manifest {field} is missing")
    try:
        if int(manifest.get("control_run_id", 0)) <= 0:
            failures.append("run manifest control_run_id is invalid")
        if int(manifest.get("control_run_attempt", 0)) < 1:
            failures.append("run manifest control_run_attempt is invalid")
    except (TypeError, ValueError):
        failures.append("run manifest control run identity is invalid")

    manifest_comparison = manifest.get("comparison")
    if not isinstance(manifest_comparison, dict):
        failures.append("run manifest comparison record is missing")
    else:
        for field in ("status", "native_afh_validated", "rows_compared"):
            if manifest_comparison.get(field) != comparison.get(field):
                failures.append(
                    f"run manifest comparison.{field} disagrees with comparison file"
                )

    if failures:
        raise RuntimeError(
            "native AFH provenance gate is not closed: " + "; ".join(failures)
        )

    metadata = metadata_path.read_text(encoding="utf-8-sig")
    if not metadata.strip():
        raise RuntimeError("native AFH native_metadata.txt is empty")

    prefix = "native/" if native_data_dir != artifact_root else ""
    required_paths = [
        "native-comparison.json",
        "run_manifest.json",
        f"{prefix}native_metadata.txt",
    ] + [
        f"{prefix}afh_v6_xe{A}_eight_response_native.csv"
        for A in ISOTOPES
    ]
    verified_files = _verify_native_archive_hashes(
        artifact_root, required_paths
    )
    return {
        "comparison": comparison,
        "native_metadata": metadata,
        "native_csv_directory": str(native_data_dir),
        "provenance": {
            "repository": manifest["repository"],
            "source_commit": manifest["source_commit"],
            "control_run_id": int(manifest["control_run_id"]),
            "control_run_attempt": int(manifest["control_run_attempt"]),
            "native_package": manifest["native_package"],
            "wolfram_version": manifest["wolfram_version"],
            "python_version": manifest["python_version"],
            "response_indices": manifest["response_indices"],
            "q_grid": manifest["q_grid"],
        },
        "sha256_verified_files": verified_files,
    }


def load_native_response_bundle(artifact_root: Path) -> tuple[dict, dict]:
    gate = _native_validation_gate(artifact_root)
    native_data_dir = Path(gate["native_csv_directory"])
    bundle = {}
    expected_q = np.linspace(0.0, 0.6, 2401)
    for A in ISOTOPES:
        path = native_data_dir / f"afh_v6_xe{A}_eight_response_native.csv"
        if not path.is_file():
            raise FileNotFoundError(f"missing native AFH export: {path}")
        rows = read_csv(path)
        if len(rows) != 2401:
            raise ValueError(f"Xe-{A}: expected 2401 native rows, got {len(rows)}")
        row_isotopes = np.asarray([int(float(row["A"])) for row in rows], dtype=int)
        if not np.all(row_isotopes == A):
            raise ValueError(f"Xe-{A}: native CSV contains rows from another isotope")
        q = np.asarray([float(row["q_GeV"]) for row in rows], dtype=float)
        if not np.all(np.isfinite(q)) or not np.allclose(
            q, expected_q, rtol=0.0, atol=2.0e-12
        ):
            raise ValueError(
                f"Xe-{A}: native q grid is not the canonical 2401-point [0,0.6] GeV grid"
            )
        physical = {}
        conversion = 4.0 * math.pi / (2.0 * J_BY_A[A] + 1.0)
        for name, column in NATIVE_RESPONSE_W_COLUMNS.items():
            values = np.asarray([float(row[column]) for row in rows], dtype=float)
            imaginary = np.asarray(
                [float(row[f"Im_{column}"]) for row in rows], dtype=float
            )
            if not np.all(np.isfinite(values)) or not np.all(np.isfinite(imaginary)):
                raise ValueError(f"Xe-{A}: non-finite native {name} response")
            if np.max(np.abs(imaginary)) > 2.0e-12:
                raise ValueError(f"Xe-{A}: native {name} imaginary residual is too large")
            physical[name] = 4.0 * conversion * values
        bundle[A] = {"q": q, "physical": physical}
    return bundle, gate

def interpolate_native_response(
    bundle_entry: dict,
    q_GeV: float,
    response_names: tuple[str, ...] = RESPONSE_NAMES,
) -> dict:
    q = bundle_entry["q"]
    if q_GeV < q[0] or q_GeV > q[-1]:
        raise ValueError(f"q_A={q_GeV:.12g} GeV lies outside native AFH grid")
    out = {}
    linear = {}
    for name in response_names:
        values = bundle_entry["physical"][name]
        pchip = PchipInterpolator(q, values, extrapolate=False)
        out[name] = float(pchip(q_GeV))
        linear[name] = float(np.interp(q_GeV, q, values))
    return {
        "physical_equal_pn": out,
        "linear_physical_equal_pn": linear,
        "pchip_linear_relative_difference": {
            name: abs(out[name] - linear[name]) / max(abs(out[name]), abs(linear[name]), 1.0e-300)
            for name in response_names
        },
    }


def quark_form_factor_values(
    qA_GeV: float,
    prescription: str,
    *,
    tN_GeV2: float | None = None,
) -> tuple[float, float]:
    """Return raw flavor-summed F1,F2 for the universal u+d+s current."""
    Q2 = qA_GeV * qA_GeV if tN_GeV2 is None else -float(tN_GeV2)
    if Q2 < 0.0 or not math.isfinite(Q2):
        raise ValueError("nucleon form-factor Q_N^2 must be finite and non-negative")
    if prescription == "q0_anchor":
        return F1V0, F2V0
    if prescription == "bishara_linear":
        return bishara_linear(Q2)
    if prescription == "isoscalar_zexp":
        return isoscalar_zexp(Q2)
    raise ValueError(f"unknown form-factor prescription: {prescription}")


def form_factor_values(
    qA_GeV: float,
    prescription: str,
    *,
    tN_GeV2: float | None = None,
) -> tuple[float, float]:
    """Return effective Fhat_i=F_i^{uds}/3 for the external g_VN basis."""
    raw = quark_form_factor_values(
        qA_GeV, prescription, tN_GeV2=tN_GeV2
    )
    return effective_nucleon_form_factors(*raw)


def charge_kernel_from_coulomb_weight(
    L_C: float,
    qA_GeV: float,
    responses: dict[str, float],
    form_factor_prescription: str,
    *,
    tN_GeV2: float | None = None,
) -> dict:
    """Build the B baseline and the separate C charge-multipole extension.

    B = c_M(Fhat_1,Fhat_2;t_N)^2 L_C W_M(y_A), with only the AFH M response.
    C adds Phi'' and signed M-Phi'' terms at the same nucleon form factors.
    The public prefactor is expressed with g_VN=3*g_Vq, so Fhat_i=F_i^{uds}/3.
    """
    if not math.isfinite(L_C) or L_C < 0.0:
        raise ValueError(f"invalid continuity-adjusted Coulomb weight L_C={L_C}")
    tN_used = -qA_GeV * qA_GeV if tN_GeV2 is None else float(tN_GeV2)
    F1_quark, F2_quark = quark_form_factor_values(
        qA_GeV, form_factor_prescription, tN_GeV2=tN_used
    )
    F1, F2 = effective_nucleon_form_factors(F1_quark, F2_quark)
    cM, cPhi = charge_coefficients(
        qA_GeV, F1=F1, F2=F2, tN_GeV2=tN_GeV2
    )
    WM = float(responses["M"])
    WPhi = float(responses["PhiPP"])
    WMPhi = float(responses["MPhiPP"])
    if WM <= 0.0:
        raise ValueError(f"non-positive native W_M at q_A={qA_GeV:.12g} GeV")
    if not math.isfinite(L_C) or L_C < 0.0:
        raise ValueError("invalid continuity-adjusted Coulomb weight L_C")

    A_reference_M = F1N0 * F1N0 * L_C * WM
    B_baseline_M = cM * cM * L_C * WM
    C_M = B_baseline_M
    C_PhiPP = cPhi * cPhi * L_C * WPhi
    C_MPhiPP = 2.0 * cM * cPhi * L_C * WMPhi
    terms = {"M": C_M, "PhiPP": C_PhiPP, "MPhiPP": C_MPhiPP}
    C_charge_extension = sum(terms.values())
    relative_C_vs_A = C_charge_extension / A_reference_M - 1.0
    relative_B_vs_A = B_baseline_M / A_reference_M - 1.0
    relative_C_vs_B = C_charge_extension / B_baseline_M - 1.0

    return {
        "form_factor_prescription": form_factor_prescription,
        "F1V_quark_sum": F1_quark,
        "F2V_quark_sum": F2_quark,
        "F1N_effective": F1,
        "F2N_effective": F2,
        "tN_GeV2": tN_used,
        "Q_N2_GeV2": -tN_used,
        "nucleon_transfer_scheme": (
            "strict one-body impulse q_N^mu=q_A^mu"
            if tN_GeV2 is not None else "static q_N^0=0 diagnostic"
        ),
        "cM": cM,
        "cPhiPP": cPhi,
        "L_C": float(L_C),
        "terms": terms,
        "AFH_finite_size_M_baseline": A_reference_M,
        "nucleon_q0_M_only": A_reference_M,
        "nucleon_finite_t_M_only": B_baseline_M,
        "charge_M_PhiPP": C_charge_extension,
        "relative_nucleon_finite_t_M_only_vs_AFH_finite_size_M_baseline": relative_B_vs_A,
        "relative_charge_vs_AFH_finite_size_M_baseline": relative_C_vs_A,
        "relative_charge_vs_nucleon_finite_t_M_only": relative_C_vs_B,
    }


def leading_static_vector_current_kernel_from_tensor(
    L_q_aligned_real_imag: list,
    qA_GeV: float,
    omega_GeV: float,
    responses: dict[str, float],
    form_factor_prescription: str,
) -> dict:
    """Evaluate the six-channel leading-static AFH vector-current candidate.

    This is deliberately labelled a candidate until the direct covariant
    one-nucleon contraction and AFH multipole contraction pass P3.
    """
    required = set(FULL_VECTOR_RESPONSE_NAMES)
    missing = required.difference(responses)
    if missing:
        raise ValueError(f"missing native AFH response channels: {sorted(missing)}")
    pairs = np.asarray(L_q_aligned_real_imag, dtype=float)
    if pairs.shape != (4, 4, 2) or not np.all(np.isfinite(pairs)):
        raise ValueError("integrated q-aligned Lorentz tensor must have shape (4,4,2)")
    L = pairs[:, :, 0] + 1j * pairs[:, :, 1]
    tN_GeV2 = omega_GeV * omega_GeV - qA_GeV * qA_GeV
    F1, F2 = form_factor_values(
        qA_GeV, form_factor_prescription, tN_GeV2=tN_GeV2
    )
    coefficients = extract_afh_vector_coefficients(
        L,
        qA_GeV,
        f1=F1,
        f2=F2,
        mN_GeV=DEFAULT_MN_GEV,
        omega_GeV=omega_GeV,
    )
    charge_terms = {
        "M": coefficients["C_M"] * responses["M"],
        "PhiPP": coefficients["C_PhiPP"] * responses["PhiPP"],
        "MPhiPP": coefficients["C_MPhiPP"] * responses["MPhiPP"],
    }
    spatial_terms = {
        "Delta": coefficients["C_Delta"] * responses["Delta"],
        "SigmaPrime": coefficients["C_SigmaPrime"] * responses["SigmaPrime"],
        "SigmaPrimeDelta": (
            coefficients["C_SigmaPrimeDelta"] * responses["SigmaPrimeDelta"]
        ),
        "SigmaDoublePrime": coefficients["C_SigmaDoublePrime"] * responses["SigmaDoublePrime"],
        "PhiTildePrime": coefficients["C_PhiTildePrime"] * responses["PhiTildePrime"],
    }
    charge = float(sum(charge_terms.values()))
    spatial = float(sum(spatial_terms.values()))
    total = charge + spatial
    response_m = float(responses["M"])
    response_phi = float(responses["PhiPP"])
    response_mphi = float(responses["MPhiPP"])
    if response_m < -1.0e-12 or response_phi < -1.0e-12:
        raise ValueError("negative native AFH M/Phi'' diagonal response")
    charge_response_bound = math.sqrt(
        max(0.0, response_m) * max(0.0, response_phi)
    )
    charge_response_cauchy_excess = max(
        0.0, abs(response_mphi) - charge_response_bound
    )
    charge_response_cauchy_scale = max(
        abs(response_mphi), charge_response_bound, 1.0e-300
    )
    if charge_response_cauchy_excess > max(
        1.0e-12, 2.0e-10 * charge_response_cauchy_scale
    ):
        raise ValueError(
            "native AFH M-Phi'' response violates Cauchy-Schwarz: "
            f"excess={charge_response_cauchy_excess:.6g}"
        )

    response_delta = float(responses["Delta"])
    response_sigma = float(responses["SigmaPrime"])
    response_cross = float(responses["SigmaPrimeDelta"])
    if response_delta < -1.0e-12 or response_sigma < -1.0e-12:
        raise ValueError("negative native AFH spatial diagonal response")
    response_bound = math.sqrt(
        max(0.0, response_delta) * max(0.0, response_sigma)
    )
    spatial_response_cauchy_excess = max(
        0.0, abs(response_cross) - response_bound
    )
    response_cauchy_scale = max(abs(response_cross), response_bound, 1.0e-300)
    if spatial_response_cauchy_excess > max(
        1.0e-12, 2.0e-10 * response_cauchy_scale
    ):
        raise ValueError(
            "native AFH SigmaPrime-Delta response violates Cauchy-Schwarz: "
            f"excess={spatial_response_cauchy_excess:.6g}"
        )
    response_cauchy_excess = max(
        charge_response_cauchy_excess, spatial_response_cauchy_excess
    )
    if coefficients["C_SigmaPrimeDelta_cauchy_identity_relative_residual"] > 2.0e-12:
        raise ValueError("particle-side SigmaPrime-Delta coefficient identity failed")
    spatial_scale = max(
        *(abs(value) for value in spatial_terms.values()),
        1.0e-300,
    )
    if spatial < -2.0e-10 * spatial_scale:
        raise ValueError(
            f"negative combined leading-static spatial kernel: {spatial:.6g}"
        )
    total_scale = max(abs(charge), abs(spatial), 1.0e-300)
    if total < -2.0e-10 * total_scale:
        raise ValueError(f"negative total leading-static vector kernel: {total:.6g}")

    charge_check = charge_kernel_from_coulomb_weight(
        coefficients["L_C_continuity_adjusted_charge_weight"],
        qA_GeV,
        responses,
        form_factor_prescription,
        tN_GeV2=tN_GeV2,
    )
    charge_residual = abs(charge - charge_check["charge_M_PhiPP"]) / max(
        abs(charge), abs(charge_check["charge_M_PhiPP"]), 1.0e-300
    )
    if charge_residual > 2.0e-12:
        raise AssertionError(
            f"charge-sector reconstruction mismatch: {charge_residual:.6g}"
        )
    return {
        "F1N_effective": F1,
        "F2N_effective": F2,
        "tN_GeV2": tN_GeV2,
        "Q_N2_GeV2": -tN_GeV2,
        "nucleon_transfer_scheme": "strict one-body impulse q_N^mu=q_A^mu",
        "coupling_basis": "external (g1*g2*gVN)^2 with Fhat_i=F_i^(u+d+s)/3",
        "L_C": coefficients["L_C_continuity_adjusted_charge_weight"],
        "L_T": float(np.real(L[1, 1] + L[2, 2])),
        "charge_M_PhiPP": charge,
        "spatial_sector": spatial,
        "full_six_channel_candidate": total,
        "AFH_finite_size_M_baseline": charge_check["AFH_finite_size_M_baseline"],
        "nucleon_q0_M_only": charge_check["nucleon_q0_M_only"],
        "nucleon_finite_t_M_only": charge_check["nucleon_finite_t_M_only"],
        "charge_terms": charge_terms,
        "spatial_terms": spatial_terms,
        "particle_coefficients": {
            key: coefficients[key]
            for key in (
                "C_M", "C_PhiPP", "C_MPhiPP", "C_Delta",
                "C_SigmaPrime", "C_SigmaPrimeDelta",
                "C_SigmaDoublePrime", "C_PhiTildePrime",
            )
        },
        "charge_response_Cauchy_excess": charge_response_cauchy_excess,
        "spatial_response_Cauchy_excess": spatial_response_cauchy_excess,
        "response_Cauchy_excess": response_cauchy_excess,
        "particle_Cauchy_identity_relative_residual": (
            coefficients["C_SigmaPrimeDelta_cauchy_identity_relative_residual"]
        ),
        "charge_reconstruction_relative_residual": charge_residual,
        "scope": (
            "leading-static one-body vector-current candidate; not promoted "
            "until P3 direct covariant-versus-AFH tensor validation passes"
        ),
    }


def _coulomb_weights_from_result(result: dict) -> dict:
    contractions = result["point_nucleus_contractions"]
    L00 = float(contractions["I00"])
    L_C = float(contractions["L_C_continuity_adjusted"])
    residual = float(contractions["continuity_reduced_relative_residual"])
    if not math.isfinite(L00) or L00 < 0.0:
        raise ValueError(f"invalid integrated L00={L00}")
    if not math.isfinite(L_C) or L_C < 0.0:
        raise ValueError(f"invalid continuity-adjusted Coulomb weight L_C={L_C}")
    if not math.isfinite(residual) or residual > 5.0e-12:
        raise ValueError(
            f"nuclear-continuity reduction fails point-nucleus identity: {residual}"
        )
    correction = (
        L_C / L00 - 1.0
        if L00 > 0.0
        else (0.0 if L_C == 0.0 else math.inf)
    )
    if not math.isfinite(correction):
        raise ValueError("non-finite continuity correction at vanishing L00")
    return {
        "L00": L00,
        "L_C": L_C,
        "charge_continuity_relative_correction": correction,
        "continuity_reduced_relative_residual": residual,
    }


def integrate_coulomb_weight(
    *,
    mchi: float,
    ms: float,
    delta_m: float,
    mA: float,
    ER_keV: float,
    speed_kms: float,
    g2: float,
    width_scheme: str,
    nw: int,
    nz: int,
    nphi: int,
) -> dict:
    result = integrate_spin_resolved_tensor(
        mchi=mchi,
        ms=ms,
        delta_m=delta_m,
        mA=mA,
        ER=ER_keV * 1.0e-6,
        speed_kms=speed_kms,
        g2=g2,
        width_scheme=width_scheme,
        mapping="threshold_u2",
        nw=nw,
        nz=nz,
        nphi=nphi,
        crosscheck_dirac_trace=False,
    )
    if not result.get("phase_space_open", False):
        return {"phase_space_open": False}
    weights = _coulomb_weights_from_result(result)
    return {
        "phase_space_open": True,
        **weights,
        "qA_GeV": float(result["qA_magnitude_GeV"]),
        "quadrature_points": int(result["quadrature_points"]),
        "pole_clearance_keV": float(result["pole_clearance_keV"]),
        "L_q_aligned_real_imag": result["L_q_aligned_real_imag"],
    }


def _rate_factor(mchi: float, rho: float, mean_atomic_weight: float) -> float:
    target_nuclei_per_kg = AVOGADRO * 1000.0 / mean_atomic_weight
    return (
        (rho / mchi)
        * C_CM_S
        * target_nuclei_per_kg
        * GEV2_TO_CM2
        * 1.0e-6
        * 86400.0
    )


def mean_atomic_weight_from_input(path: Path) -> float:
    rows = read_csv(path)
    return sum(float(row["atomic_mass_u"]) * float(row["natural_atom_fraction"]) for row in rows)


def fold(
    *,
    native_dir: Path,
    mchi: float,
    ms: float,
    delta_m: float,
    mV: float,
    g2: float,
    coupling_product_squared: float,
    rho: float,
    ER_values_keV: Iterable[float],
    nv: int,
    nw: int,
    nz: int,
    nphi: int,
    form_factor_prescription: str,
    width_scheme: str,
    include_leading_static_vector_candidate: bool = False,
    response_input: Path = HALO_INPUT / "natural_xenon_isotope_weights.csv",
) -> dict:
    if width_scheme != "pole":
        raise ValueError(
            "formal natural-xenon production is pole-only: the first propagator "
            "is zero-width and the second carries the constant pole width"
        )
    native_bundle, native_gate = load_native_response_bundle(native_dir)
    isotope_data = load_isotope_inputs(response_input)
    mean_atomic_weight = mean_atomic_weight_from_input(response_input)
    rate_factor = _rate_factor(mchi, rho, mean_atomic_weight)
    response_names = (
        FULL_VECTOR_RESPONSE_NAMES
        if include_leading_static_vector_candidate else RESPONSE_NAMES
    )

    speed_nodes, speed_weights = leggauss(nv)
    rows = []
    for ER_keV in ER_values_keV:
        ER = ER_keV * 1.0e-6
        for halo_name, pdf, vmax in (
            ("shm_cutoff", shm_truncated_pdf, 776.0),
            ("mb_untruncated", mb_untruncated_pdf, 1600.0),
        ):
            isotope_rows = []
            for A in ISOTOPES:
                xA = isotope_data[A]["abundance"]
                mA = isotope_data[A]["mA_GeV"]
                qA = exact_qA_GeV(mA, ER_keV)
                vmin = vmin_three_body_km_s(mchi, ms, mA, ER_keV)
                if vmin >= vmax:
                    isotope_rows.append({
                        "A": A, "abundance": xA, "open": False,
                        "vmin_km_s": vmin, "qA_GeV": qA,
                    })
                    continue
                vs = 0.5 * (vmax + vmin) + 0.5 * (vmax - vmin) * speed_nodes
                ws = 0.5 * (vmax - vmin) * speed_weights
                halo_charge = 0.0
                halo_A_reference = 0.0
                halo_B_baseline = 0.0
                halo_spatial_candidate = 0.0
                halo_full_candidate = 0.0
                max_interp_difference = 0.0
                max_abs_continuity_correction = 0.0
                max_continuity_identity_residual = 0.0
                max_response_cauchy_excess = 0.0
                max_charge_response_cauchy_excess = 0.0
                max_spatial_response_cauchy_excess = 0.0
                max_particle_cauchy_residual = 0.0
                max_charge_reconstruction_residual = 0.0
                min_spatial_candidate_kernel = math.inf
                min_full_candidate_kernel = math.inf
                for v, w in zip(vs, ws):
                    fv = pdf(float(v))
                    if fv == 0.0:
                        continue
                    beta = float(v) / C_KM_S
                    pchi = mchi * beta / math.sqrt(1.0 - beta * beta)
                    coulomb_result = integrate_coulomb_weight(
                        mchi=mchi, ms=ms, delta_m=delta_m, mA=mA,
                        ER_keV=ER_keV, speed_kms=float(v), g2=g2,
                        width_scheme=width_scheme, nw=nw, nz=nz, nphi=nphi,
                    )
                    if not coulomb_result["phase_space_open"]:
                        continue
                    max_abs_continuity_correction = max(
                        max_abs_continuity_correction,
                        abs(coulomb_result["charge_continuity_relative_correction"]),
                    )
                    max_continuity_identity_residual = max(
                        max_continuity_identity_residual,
                        coulomb_result["continuity_reduced_relative_residual"],
                    )
                    response = interpolate_native_response(
                        native_bundle[A], qA, response_names=response_names
                    )
                    max_interp_difference = max(
                        max_interp_difference,
                        max(response["pchip_linear_relative_difference"].values()),
                    )
                    ER_GeV = float(ER_keV) * 1.0e-6
                    tN_GeV2 = ER_GeV * ER_GeV - qA * qA
                    kernel = charge_kernel_from_coulomb_weight(
                        coulomb_result["L_C"], qA,
                        response["physical_equal_pn"],
                        form_factor_prescription,
                        tN_GeV2=tN_GeV2,
                    )
                    # The mediator and the strict one-body nucleon impulse current
                    # carry q_A^mu: t_A=t_N=E_R^2-|q_A|^2=-2 m_A E_R.
                    # The AFH response still uses spatial Q_A^2=|q_A|^2.
                    denominator = mediator_denominator_squared_GeV4(mV, mA, ER_keV)
                    common = (
                        mA * coupling_product_squared
                        / (256.0 * math.pi**3 * pchi * pchi * denominator)
                    )
                    halo_charge += float(w) * fv * beta * common * kernel["charge_M_PhiPP"]
                    halo_A_reference += float(w) * fv * beta * common * kernel["AFH_finite_size_M_baseline"]
                    halo_B_baseline += float(w) * fv * beta * common * kernel["nucleon_finite_t_M_only"]
                    if include_leading_static_vector_candidate:
                        candidate = leading_static_vector_current_kernel_from_tensor(
                            coulomb_result["L_q_aligned_real_imag"],
                            qA,
                            ER,
                            response["physical_equal_pn"],
                            form_factor_prescription,
                        )
                        max_response_cauchy_excess = max(
                            max_response_cauchy_excess,
                            candidate["response_Cauchy_excess"],
                        )
                        max_charge_response_cauchy_excess = max(
                            max_charge_response_cauchy_excess,
                            candidate["charge_response_Cauchy_excess"],
                        )
                        max_spatial_response_cauchy_excess = max(
                            max_spatial_response_cauchy_excess,
                            candidate["spatial_response_Cauchy_excess"],
                        )
                        max_particle_cauchy_residual = max(
                            max_particle_cauchy_residual,
                            candidate["particle_Cauchy_identity_relative_residual"],
                        )
                        max_charge_reconstruction_residual = max(
                            max_charge_reconstruction_residual,
                            candidate["charge_reconstruction_relative_residual"],
                        )
                        min_spatial_candidate_kernel = min(
                            min_spatial_candidate_kernel, candidate["spatial_sector"]
                        )
                        min_full_candidate_kernel = min(
                            min_full_candidate_kernel,
                            candidate["full_six_channel_candidate"],
                        )
                        halo_spatial_candidate += (
                            float(w) * fv * beta * common * candidate["spatial_sector"]
                        )
                        halo_full_candidate += (
                            float(w) * fv * beta * common
                            * candidate["full_six_channel_candidate"]
                        )
                isotope_row = {
                    "A": A, "abundance": xA, "open": True,
                    "mA_GeV": mA, "qA_GeV": qA, "vmin_km_s": vmin,
                    "AFH_finite_size_M_baseline_halo_integral": halo_A_reference,
                    "nucleon_finite_t_M_only_halo_integral": halo_B_baseline,
                    "charge_M_PhiPP_halo_integral": halo_charge,
                    "relative_nucleon_FF_vs_AFH_finite_size_baseline": halo_B_baseline / halo_A_reference - 1.0
                    if halo_A_reference else math.nan,
                    "relative_charge_M_PhiPP_vs_AFH_finite_size_baseline": halo_charge / halo_A_reference - 1.0
                    if halo_A_reference else math.nan,
                    "relative_charge_M_PhiPP_vs_nucleon_finite_t_M_only": halo_charge / halo_B_baseline - 1.0
                    if halo_B_baseline else math.nan,
                    "max_pchip_linear_response_difference": max_interp_difference,
                    "max_abs_charge_continuity_relative_correction": max_abs_continuity_correction,
                    "max_continuity_identity_relative_residual": max_continuity_identity_residual,
                    "nv": nv, "nw": nw, "nz": nz, "nphi": nphi,
                }
                if include_leading_static_vector_candidate:
                    isotope_row.update({
                        "spatial_candidate_halo_integral": halo_spatial_candidate,
                        "full_six_channel_candidate_halo_integral": halo_full_candidate,
                        "relative_spatial_candidate_vs_C_extension": (
                            halo_spatial_candidate / halo_charge if halo_charge else math.nan
                        ),
                        "relative_full_candidate_vs_AFH_finite_size_M_baseline": (
                            halo_full_candidate / halo_A_reference - 1.0
                            if halo_A_reference else math.nan
                        ),
                        "relative_full_candidate_vs_nucleon_finite_t_M_only": (
                            halo_full_candidate / halo_B_baseline - 1.0
                            if halo_B_baseline else math.nan
                        ),
                        "max_native_response_Cauchy_excess": max_response_cauchy_excess,
                        "max_native_charge_response_Cauchy_excess": max_charge_response_cauchy_excess,
                        "max_native_spatial_response_Cauchy_excess": max_spatial_response_cauchy_excess,
                        "max_particle_Cauchy_identity_residual": max_particle_cauchy_residual,
                        "max_charge_reconstruction_residual": max_charge_reconstruction_residual,
                        "minimum_spatial_candidate_kernel": (
                            min_spatial_candidate_kernel
                            if math.isfinite(min_spatial_candidate_kernel) else None
                        ),
                        "minimum_full_candidate_kernel": (
                            min_full_candidate_kernel
                            if math.isfinite(min_full_candidate_kernel) else None
                        ),
                    })

                isotope_rows.append(isotope_row)
            total_charge = sum(
                r.get("abundance", 0.0) * r.get("charge_M_PhiPP_halo_integral", 0.0)
                for r in isotope_rows
            )
            total_A_reference = sum(
                r.get("abundance", 0.0) * r.get("AFH_finite_size_M_baseline_halo_integral", 0.0)
                for r in isotope_rows
            )
            total_B_baseline = sum(
                r.get("abundance", 0.0) * r.get("nucleon_finite_t_M_only_halo_integral", 0.0)
                for r in isotope_rows
            )
            total_rate = rate_factor * total_charge
            A_reference_rate = rate_factor * total_A_reference
            B_baseline_rate = rate_factor * total_B_baseline
            row = {
                "ER_keV": ER_keV,
                "halo_model": halo_name,
                "rate_nucleon_finite_t_M_only_events_kg_day_keV": B_baseline_rate,
                "rate_AFH_finite_size_M_baseline_events_kg_day_keV": A_reference_rate,
                "rate_charge_M_PhiPP_events_kg_day_keV": total_rate,
                "relative_nucleon_FF_vs_AFH_finite_size_baseline": B_baseline_rate / A_reference_rate - 1.0
                if A_reference_rate else math.nan,
                "relative_charge_M_PhiPP_vs_AFH_finite_size_baseline": total_rate / A_reference_rate - 1.0
                if A_reference_rate else math.nan,
                "relative_charge_M_PhiPP_vs_nucleon_finite_t_M_only": total_rate / B_baseline_rate - 1.0
                if B_baseline_rate else math.nan,
                "open_abundance_fraction": sum(
                    r["abundance"] for r in isotope_rows if r.get("open")
                ),
                "isotope_rows": isotope_rows,
            }
            if include_leading_static_vector_candidate:
                total_spatial = sum(
                    r.get("abundance", 0.0) * r.get("spatial_candidate_halo_integral", 0.0)
                    for r in isotope_rows
                )
                total_full = sum(
                    r.get("abundance", 0.0) * r.get("full_six_channel_candidate_halo_integral", 0.0)
                    for r in isotope_rows
                )
                spatial_rate = rate_factor * total_spatial
                full_rate = rate_factor * total_full
                row.update({
                    "rate_spatial_candidate_events_kg_day_keV": spatial_rate,
                    "rate_full_six_channel_candidate_events_kg_day_keV": full_rate,
                    "relative_spatial_candidate_vs_C_extension": (
                        total_spatial / total_charge if total_charge else math.nan
                    ),
                    "relative_full_candidate_vs_AFH_finite_size_M_baseline": (
                        full_rate / A_reference_rate - 1.0 if A_reference_rate else math.nan
                    ),
                    "relative_full_candidate_vs_nucleon_finite_t_M_only": (
                        full_rate / B_baseline_rate - 1.0 if B_baseline_rate else math.nan
                    ),
                    "minimum_spatial_candidate_kernel": min(
                        (r["minimum_spatial_candidate_kernel"] for r in isotope_rows
                         if r.get("minimum_spatial_candidate_kernel") is not None),
                        default=None,
                    ),
                    "minimum_full_candidate_kernel": min(
                        (r["minimum_full_candidate_kernel"] for r in isotope_rows
                         if r.get("minimum_full_candidate_kernel") is not None),
                        default=None,
                    ),
                    "max_native_response_Cauchy_excess": max(
                        (r.get("max_native_response_Cauchy_excess", 0.0) for r in isotope_rows),
                        default=0.0,
                    ),
                    "max_native_charge_response_Cauchy_excess": max(
                        (r.get("max_native_charge_response_Cauchy_excess", 0.0) for r in isotope_rows),
                        default=0.0,
                    ),
                    "max_native_spatial_response_Cauchy_excess": max(
                        (r.get("max_native_spatial_response_Cauchy_excess", 0.0) for r in isotope_rows),
                        default=0.0,
                    ),
                    "max_particle_Cauchy_identity_residual": max(
                        (r.get("max_particle_Cauchy_identity_residual", 0.0) for r in isotope_rows),
                        default=0.0,
                    ),
                    "max_charge_reconstruction_residual": max(
                        (r.get("max_charge_reconstruction_residual", 0.0) for r in isotope_rows),
                        default=0.0,
                    ),
                })

            rows.append(row)

    return {
        "reference_baseline": "A: external gVN coupling times physical equal-p=n AFH finite-size W_M(y_A)",
        "nucleon_q0_M_only": "same finite-size AFH W_M(y_A) with Fhat_1(0)=1",
        "charge_M_PhiPP": "nucleon_finite_t_M_only plus Phi'' and signed M-Phi'' charge responses at the same AFH W_M(y_A)",
        "coupling_normalization": "coupling_product_squared=(g1*g2*gVN)^2; use Fhat_i=F_i^(u+d+s)/3 in all nucleon-current coefficients",
        "coupling_basis": "effective nucleon g_VN with g_VN=3*g_Vq",
        "nuclear_response_baseline": "finite-size native AFH W_M(y_A) at each recoil; no point-nucleus substitution",
        "AFH_response_normalization": "physical equal-p=n; raw-to-physical factor four applied exactly once",
        "no_additional_nuclear_form_factor": "do not multiply a Helm or other whole-nucleus form factor on top of AFH W_M",
        "status": (
            "COMPUTED_WITHIN_LEADING_STATIC_VECTOR_CURRENT_CANDIDATE"
            if include_leading_static_vector_candidate
            else "COMPUTED_WITHIN_COULOMB_SECTOR_APPROXIMATION"
        ),
        "full_current_complete": False,
        "leading_static_vector_current_candidate_included": (
            include_leading_static_vector_candidate
        ),
        "P3_tensor_validation_complete": False,
        "continuity_reduction_status": (
            "CONDITIONAL_ON_CONSERVED_NUCLEAR_VECTOR_CURRENT; "
            "the point-target longitudinal identity is an algebraic convention check, "
            "not proof of many-body current conservation or a point-nucleus AFH baseline"
        ),
        "included_tensor_components": (
            [
                "L00", "L03", "L30", "L33 reduced using nuclear-current continuity",
                "L11", "L22 transverse-even AFH weights"
            ]
            if include_leading_static_vector_candidate
            else ["L00", "L03", "L30", "L33 reduced using nuclear-current continuity"]
        ),
        "omitted_tensor_components": (
            [
                "mixed longitudinal/transverse components excluded by the unpolarized parity-even target-tensor symmetry",
                "transverse antisymmetric/helicity-odd combination not used by the leading AFH SigmaPrime-Delta coefficient",
                "higher-order and two-body nuclear-current operators"
            ]
            if include_leading_static_vector_candidate
            else [
                "transverse nuclear-current multipoles (Delta, Sigma', and any additional allowed channels)"
            ]
        ),
        "approximation": (
            "leading-static one-body vector-current candidate with M, Phi'', M-Phi'', Delta, Sigma', and Sigma'-Delta; P3 tensor validation pending"
            if include_leading_static_vector_candidate
            else "M + Phi'' + M-Phi'' Coulomb sector using continuity-reduced L_C; transverse nuclear-current multipoles are not included"
        ),
        "scope": (
            "seven-isotope natural-xenon leading-static vector-current candidate; "
            "not promoted to a complete full-current prediction until P3 passes"
            if include_leading_static_vector_candidate
            else "seven-isotope natural-xenon Coulomb-sector diagnostic using native AFH M/Phi''/M-Phi'' responses, nuclear-current continuity, and finite-t_N diagnostics; not the full L_mu_nu W_A^mu_nu contraction"
        ),
        "native_gate": native_gate["comparison"],
        "native_provenance": native_gate["provenance"],
        "native_sha256_verified_files": native_gate["sha256_verified_files"],
        "form_factor_prescription": form_factor_prescription,
        "width_scheme": width_scheme,
        "mchi_GeV": mchi,
        "ms_GeV": ms,
        "delta_m_GeV": delta_m,
        "mV_GeV": mV,
        "g2": g2,
        "coupling_product_squared": coupling_product_squared,
        "rho_GeV_cm3": rho,
        "isotopes": list(ISOTOPES),
        "natural_atom_fraction_coverage": sum(
            isotope_data[A]["abundance"] for A in ISOTOPES
        ),
        "response_interpolation": (
            "PCHIP on native 0.25 MeV absolute response values; linear interpolation retained as diagnostic"
        ),
        "recoil_momentum": "Q_A=|bold(q_A)|=sqrt(2 m_A E_R + E_R^2), exact spatial nuclear recoil momentum",
        "nuclear_transfer_invariant": "t_A=q_A^mu q_{A,mu}=-2 m_A E_R exactly for an initially resting on-shell target",
        "mediator_propagator_denominator": "(m_V^2-t_A)^2=(m_V^2+2 m_A E_R)^2; uses t_A, not spatial Q_A^2",
        "nucleon_form_factor_argument": "Q_N^2=-t_N with strict one-body impulse q_N^mu=q_A^mu, so t_N=t_A=-2 m_A E_R and Q_N^2=2 m_A E_R; static q_N^0=0 is a separate diagnostic",
        "nucleon_transfer_scheme": "full external four-momentum transfer q_N^mu=q_A^mu in formal P4; static q_N^0=0 retained only as optional diagnostic",
        "nucleon_finite_t_M_only_definition": "c_M(Fhat_1(t_N),Fhat_2(t_N))^2 * L_C * W_M(y_A); this is the nucleon-current correction to the reference baseline",
        "AFH_finite_size_M_baseline_definition": "L_C * W_M(y_A), using Fhat_1(0)=1; retains the physical finite-size AFH nuclear response",
        "C_extension_definition": "B plus Phi'' diagonal and signed M-Phi'' interference",
        "form_factor_normalization": "Fhat_i=F_i^(u+d+s)/3 because coupling_product_squared uses external g_VN=3*g_Vq",
        "response_comparison": (
            "A is the mandatory original finite-size AFH M-only reference; B/A isolates "
            "the single-nucleon finite-t_N correction at fixed W_M(Q_A); C/B isolates "
            "the additional Phi'' and signed M-Phi'' nuclear-response correction."
        ),
        "leading_static_label_meaning": (
            "leading nonrelativistic one-body nuclear-current expansion; it does not mean q_N^0=0"
        ),
        "coulomb_weight": "L_C=L00-(E_R/Q_A)(L03+L30)+(E_R/Q_A)^2 L33, conditional on conservation of the complete nuclear vector current",
        "transverse_weight": (
            "L_T=L11+L22 for the leading-static AFH Delta/SigmaPrime/SigmaPrimeDelta coefficients"
            if include_leading_static_vector_candidate else None
        ),
        "results": rows,
    }
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--native-dir",
        type=Path,
        required=True,
        help="extracted root of the private native AFH eight-response artifact",
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mchi-GeV", type=float, default=MCHI_DEFAULT)
    parser.add_argument("--ms-keV", type=float, required=True)
    parser.add_argument("--delta-m-keV", type=float, required=True)
    parser.add_argument("--mV-GeV", type=float, default=MV_DEFAULT)
    parser.add_argument("--g2", type=float, default=G2_DEFAULT)
    parser.add_argument("--coupling-product-squared", type=float, default=COUPLING_PRODUCT_SQUARED_DEFAULT)
    parser.add_argument("--rho-GeV-cm3", type=float, default=RHO_DEFAULT)
    parser.add_argument("--ER-keV", type=float, nargs="+", required=True)
    parser.add_argument("--nv", type=int, default=8)
    parser.add_argument("--nw", type=int, default=16)
    parser.add_argument("--nz", type=int, default=12)
    parser.add_argument("--nphi", type=int, default=6)
    parser.add_argument(
        "--form-factor",
        choices=("q0_anchor", "bishara_linear", "isoscalar_zexp"),
        default="bishara_linear",
    )
    parser.add_argument(
        "--width-scheme",
        choices=("pole",),
        default="pole",
        help="formal production is fixed to the asymmetric pole-width prescription",
    )
    parser.add_argument(
        "--include-leading-static-vector-candidate",
        action="store_true",
        help=(
            "also contract native Delta/Sigma'/Sigma'-Delta responses with "
            "the leading-static AFH coefficients; result remains unpromoted "
            "until P3 tensor validation passes"
        ),
    )
    parser.add_argument(
        "--response-input",
        type=Path,
        default=HALO_INPUT / "natural_xenon_isotope_weights.csv",
    )
    args = parser.parse_args()
    if min(args.nv, args.nw, args.nz, args.nphi) < 2:
        parser.error("all quadrature orders must be >= 2")
    result = fold(
        native_dir=args.native_dir,
        mchi=args.mchi_GeV,
        ms=args.ms_keV * 1.0e-6,
        delta_m=args.delta_m_keV * 1.0e-6,
        mV=args.mV_GeV,
        g2=args.g2,
        coupling_product_squared=args.coupling_product_squared,
        rho=args.rho_GeV_cm3,
        ER_values_keV=args.ER_keV,
        nv=args.nv,
        nw=args.nw,
        nz=args.nz,
        nphi=args.nphi,
        form_factor_prescription=args.form_factor,
        width_scheme=args.width_scheme,
        include_leading_static_vector_candidate=args.include_leading_static_vector_candidate,
        response_input=args.response_input,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "full_current_complete": result["full_current_complete"],
        "leading_static_vector_current_candidate_included": (
            result["leading_static_vector_current_candidate_included"]
        ),
        "P3_tensor_validation_complete": result["P3_tensor_validation_complete"],
        "form_factor_prescription": result["form_factor_prescription"],
        "n_recoil_points": len(args.ER_keV),
        "output": str(args.out),
    }, indent=2))


if __name__ == "__main__":
    main()
