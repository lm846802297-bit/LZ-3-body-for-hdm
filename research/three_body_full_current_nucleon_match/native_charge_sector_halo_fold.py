#!/usr/bin/env python3
"""Native-AFH Coulomb-sector halo fold (not a complete vector-current rate).

This module evaluates M + Phi'' + M-Phi'' using the continuity-reduced
Coulomb weight L_C = L00 - (omega/Q)(L03+L30) + (omega/Q)^2 L33,
conditional on conservation of the complete nuclear vector current.
It therefore eliminates the longitudinal multipole using the conserved-
current relation, but omits transverse nuclear-current multipoles such as
Delta and Sigma'. The algebraic point-nucleus identity does not establish
dynamical continuity of the truncated many-body one-body current. It is not the full
L_mu_nu W_A^{mu nu} contraction or the final three-body spectrum.
A native AFH input PASS validates the nuclear response archive only; it does
not validate the missing three-body transverse multipole projection.
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
    RAW_F1_UDS0,
    RAW_F2_UDS0,
    bishara_linear,
    isoscalar_zexp,
    charge_coefficients,
    effective_nucleon_form_factors,
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
    """Exact spatial recoil momentum from P'^2=P^2=m_A^2."""
    ER = float(ER_keV) * 1.0e-6
    if ER < 0.0 or mA_GeV <= 0.0:
        raise ValueError("invalid recoil or nuclear mass")
    return math.sqrt(2.0 * mA_GeV * ER + ER * ER)


def mediator_denominator_squared_GeV4(mV_GeV: float, mA_GeV: float, ER_keV: float) -> float:
    """Return (mV^2-t_A)^2 with t_A=-2*m_A*E_R, never spatial Q_A^2."""
    if min(mV_GeV, mA_GeV) <= 0.0 or ER_keV < 0.0:
        raise ValueError("invalid mediator or nuclear recoil kinematics")
    ER_GeV = ER_keV * 1.0e-6
    tA_GeV2 = -2.0 * mA_GeV * ER_GeV
    return (mV_GeV * mV_GeV - tA_GeV2) ** 2


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
        raw_values = {}
        for name, column in NATIVE_RESPONSE_W_COLUMNS.items():
            values = np.asarray([float(row[column]) for row in rows], dtype=float)
            imaginary = np.asarray(
                [float(row[f"Im_{column}"]) for row in rows], dtype=float
            )
            if not np.all(np.isfinite(values)) or not np.all(np.isfinite(imaginary)):
                raise ValueError(f"Xe-{A}: non-finite native {name} response")
            if np.max(np.abs(imaginary)) > 2.0e-12:
                raise ValueError(f"Xe-{A}: native {name} imaginary residual is too large")
            raw_values[name] = values

        # AFH v6.0 raw isoscalar W_M has R_raw(0)=A^2/4, where
        # R_raw=4*pi*W_M/(2J+1).  Correct the small OBDME rounding
        # mismatch with C0(A), then apply the independent isospin factor 4.
        # This makes R_phys(0)=A^2 exactly and applies neither factor twice.
        package_m_zero = conversion * float(raw_values["M"][0])
        if not math.isfinite(package_m_zero) or package_m_zero <= 0.0:
            raise ValueError(f"Xe-{A}: non-positive AFH raw M(q=0) normalization")
        c0 = (A * A) / (4.0 * package_m_zero)
        if not math.isfinite(c0) or c0 <= 0.0:
            raise ValueError(f"Xe-{A}: invalid AFH common OBDME normalization C0={c0}")
        for name, values in raw_values.items():
            physical[name] = 4.0 * c0 * conversion * values
        if not math.isclose(
            float(physical["M"][0]), float(A * A), rel_tol=2.0e-13, abs_tol=2.0e-12
        ):
            raise ArithmeticError(f"Xe-{A}: physical AFH M(q=0) does not equal A^2")
        bundle[A] = {
            "q": q,
            "physical": physical,
            "common_matrix_normalization_C0": c0,
            "raw_M_zero_package_response": package_m_zero,
        }
    gate["provenance"]["C0_by_isotope"] = {
        str(A): bundle[A]["common_matrix_normalization_C0"] for A in ISOTOPES
    }
    gate["provenance"]["physical_zero_momentum_M_anchor"] = "M(q_A=0)=A^2"
    return bundle, gate


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_provisional_response_bundle(
    charge_dir: Path, spatial_dir: Path
) -> tuple[dict, dict]:
    """Load the internally validated, explicitly provisional Python AFH-8 bundle.

    Charge responses are corrected by the common C0(A) factor from the
    spatial OBDME archive. Delta/SigmaPrime/SigmaPrimeDelta are taken from
    the independently rank-reconstructed P3-B archive, which already
    includes C0. This path never claims native Mathematica validation.
    """
    charge_meta_path = charge_dir / "metadata.json"
    charge_validation_path = charge_dir / "validation.json"
    charge_csv_path = charge_dir / "afh_v6_full_eight_response_7isotope.csv"
    charge_sums_path = charge_dir / "SHA256SUMS.txt"
    charge_commit_path = charge_dir / "source_commit.txt"
    spatial_meta_path = spatial_dir / "metadata.json"
    spatial_validation_path = spatial_dir / "multipole-validation.json"
    spatial_csv_path = spatial_dir / "afh_spatial_obdme_responses_7isotope_2401.csv"
    spatial_multipole_path = spatial_dir / "afh_spatial_obdme_multipoles_7isotope_2401.csv"

    required = (
        charge_meta_path, charge_validation_path, charge_csv_path,
        charge_sums_path, charge_commit_path, spatial_meta_path,
        spatial_validation_path, spatial_csv_path, spatial_multipole_path,
    )
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(f"provisional AFH input is missing: {path}")

    charge_meta = json.loads(charge_meta_path.read_text(encoding="utf-8-sig"))
    charge_validation = json.loads(charge_validation_path.read_text(encoding="utf-8-sig"))
    spatial_meta = json.loads(spatial_meta_path.read_text(encoding="utf-8-sig"))
    spatial_validation = json.loads(spatial_validation_path.read_text(encoding="utf-8-sig"))

    expected_source_sha = "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372"
    expected_source_commit = "dcefbeb7ad705b6c03f2b4689200eb1d9252e67b"
    expected_charge_sha = "59ea25093137a05b8ebcc158e2fe6a74fe5927599dbb16766b067aa1ad8e3caa"
    expected_spatial_response_sha = "4e0a23c18d29df3af04a2531e75b7bffeaa3251d0efe97674b2287cf3c25e7e3"
    expected_spatial_multipole_sha = "e83f7499cd0af4ec8f1974238f09daf4899ca1b87205ec837ae0964a2e8532c6"

    if charge_meta.get("status") != "PROVISIONAL_PYTHON" or charge_meta.get("native_afh_validated") is not False:
        raise ValueError("charge AFH-8 input is not explicitly provisional Python")
    if charge_validation.get("status") != "PASS" or charge_validation.get("native_afh_validated") is not False:
        raise ValueError("charge AFH-8 internal validation did not pass provisionally")
    if charge_validation.get("actual_total_rows") != NATIVE_EXPECTED_ROWS:
        raise ValueError("charge AFH-8 response row count is not 16,807")
    if charge_meta.get("normalization", {}).get("factor_four_applied_once_to_physical_columns") is not True:
        raise ValueError("charge AFH-8 equal-p/n factor-four convention is not verified")
    if charge_meta.get("isotopes") != list(ISOTOPES):
        raise ValueError("charge AFH-8 isotope set mismatch")
    if charge_commit_path.read_text(encoding="utf-8").strip() != expected_source_commit:
        raise ValueError("charge AFH-8 source commit mismatch")
    charge_sha = _sha256_file(charge_csv_path)
    if charge_sha != expected_charge_sha:
        raise ValueError(f"charge AFH-8 CSV SHA-256 mismatch: {charge_sha}")

    sums = {}
    for line in charge_sums_path.read_text(encoding="ascii").splitlines():
        parts = line.split()
        if len(parts) == 2:
            sums[parts[1]] = parts[0].lower()
    for name, path in (
        ("afh_v6_full_eight_response_7isotope.csv", charge_csv_path),
        ("metadata.json", charge_meta_path),
        ("validation.json", charge_validation_path),
        ("source_commit.txt", charge_commit_path),
    ):
        if sums.get(name) != _sha256_file(path):
            raise ValueError(f"charge AFH-8 checksum manifest mismatch: {name}")

    if spatial_meta.get("status") != "PROVISIONAL_SOURCE_TRANSLATED_AFH_SPATIAL_RESPONSES":
        raise ValueError("spatial AFH input is not explicitly provisional")
    if spatial_meta.get("source_file_sha256") != expected_source_sha:
        raise ValueError("charge/spatial AFH source hashes disagree")
    if spatial_meta.get("native_mathematica_spatial_crosscheck") is not False:
        raise ValueError("spatial AFH archive must remain explicitly non-native")
    if spatial_meta.get("rankwise_amplitudes_and_signed_interference_saved") is not True:
        raise ValueError("spatial AFH archive lacks rank-resolved amplitudes")
    if spatial_validation.get("status") != "PASS_AFH_SPATIAL_MULTIPOLE_ARCHIVE":
        raise ValueError("spatial AFH internal archive validation did not pass")
    if spatial_validation.get("native_afh_validated") is not False:
        raise ValueError("spatial AFH validation must not claim native validation")
    if spatial_meta.get("response_rows") != NATIVE_EXPECTED_ROWS:
        raise ValueError("spatial AFH response row count is not 16,807")
    if spatial_meta.get("multipole_rows") != 9604:
        raise ValueError("spatial AFH rank-resolved row count is not 9,604")
    spatial_response_sha = _sha256_file(spatial_csv_path)
    spatial_multipole_sha = _sha256_file(spatial_multipole_path)
    if spatial_response_sha != expected_spatial_response_sha:
        raise ValueError("spatial AFH response CSV SHA-256 mismatch")
    if spatial_multipole_sha != expected_spatial_multipole_sha:
        raise ValueError("spatial AFH multipole CSV SHA-256 mismatch")
    if spatial_meta.get("response_file_sha256") != spatial_response_sha:
        raise ValueError("spatial AFH response metadata hash mismatch")
    if spatial_meta.get("multipole_file_sha256") != spatial_multipole_sha:
        raise ValueError("spatial AFH multipole metadata hash mismatch")

    charge_rows = read_csv(charge_csv_path)
    spatial_rows = read_csv(spatial_csv_path)
    if len(charge_rows) != NATIVE_EXPECTED_ROWS or len(spatial_rows) != NATIVE_EXPECTED_ROWS:
        raise ValueError("provisional charge/spatial AFH archives must each have 16,807 rows")

    charge_index = {}
    for row in charge_rows:
        A = int(float(row["A"]))
        q = float(row["q_GeV"])
        charge_index[(A, round(q, 10))] = row
    spatial_index = {}
    for row in spatial_rows:
        A = int(float(row["A"]))
        q = float(row["q_GeV"])
        spatial_index[(A, round(q, 10))] = row
    expected_keys = {
        (A, round(i * 0.00025, 10))
        for A in ISOTOPES for i in range(2401)
    }
    if charge_index.keys() != expected_keys or spatial_index.keys() != expected_keys:
        raise ValueError("provisional AFH charge/spatial q grids are not the canonical 16,807-row grid")

    c0_by_A = {
        int(item["A"]): float(item["common_matrix_normalization"])
        for item in spatial_meta["isotope_metadata"]
    }
    if set(c0_by_A) != set(ISOTOPES):
        raise ValueError("spatial AFH C0 map is incomplete")

    charge_columns = {
        "M": "R_M_physical_equal_pn",
        "SigmaDoublePrime": "R_SigmaDoublePrime_physical_equal_pn",
        "PhiPP": "R_PhiPP_physical_equal_pn",
        "PhiTildePrime": "R_PhiTildePrime_physical_equal_pn",
        "MPhiPP": "R_MPhiPP_physical_equal_pn",
    }
    spatial_columns = {
        "Delta": "R_Delta_equal_pn",
        "SigmaPrime": "R_SigmaPrime_equal_pn",
        "SigmaPrimeDelta": "R_SigmaPrimeDelta_equal_pn",
    }
    bundle = {}
    max_charge_cauchy_excess = 0.0
    max_spatial_cauchy_excess = 0.0
    expected_q = np.arange(2401, dtype=float) * 0.00025
    for A in ISOTOPES:
        physical = {name: [] for name in FULL_VECTOR_RESPONSE_NAMES}
        for i, q in enumerate(expected_q):
            key = (A, round(float(q), 10))
            cr = charge_index[key]
            sr = spatial_index[key]
            if not math.isclose(float(cr["q_GeV"]), float(sr["q_GeV"]), rel_tol=0.0, abs_tol=1e-12):
                raise ValueError(f"charge/spatial q mismatch for Xe-{A}")
            for name, column in charge_columns.items():
                physical[name].append(c0_by_A[A] * float(cr[column]))
            for name, column in spatial_columns.items():
                physical[name].append(float(sr[column]))
            m = physical["M"][-1]
            phi = physical["PhiPP"][-1]
            mphi = physical["MPhiPP"][-1]
            delta = physical["Delta"][-1]
            sigma = physical["SigmaPrime"][-1]
            sigmadelta = physical["SigmaPrimeDelta"][-1]
            charge_excess = max(0.0, abs(mphi) - math.sqrt(max(0.0, m) * max(0.0, phi)))
            spatial_excess = max(0.0, abs(sigmadelta) - math.sqrt(max(0.0, delta) * max(0.0, sigma)))
            max_charge_cauchy_excess = max(max_charge_cauchy_excess, charge_excess)
            max_spatial_cauchy_excess = max(max_spatial_cauchy_excess, spatial_excess)
            scale_c = max(abs(mphi), math.sqrt(max(0.0, m) * max(0.0, phi)), 1e-300)
            scale_s = max(abs(sigmadelta), math.sqrt(max(0.0, delta) * max(0.0, sigma)), 1e-300)
            if charge_excess > 2e-10 * scale_c + 1e-12:
                raise ValueError(f"provisional M-Phi'' Cauchy bound fails for Xe-{A}, q={q}")
            if spatial_excess > 2e-10 * scale_s + 1e-12:
                raise ValueError(f"provisional Sigma'-Delta Cauchy bound fails for Xe-{A}, q={q}")
        q = expected_q.copy()
        bundle[A] = {
            "q": q,
            "physical": {name: np.asarray(values, dtype=float) for name, values in physical.items()},
            "interpolation_mode": "linear_psd_preserving",
        }

    comparison = {
        "status": "PROVISIONAL_INTERNAL_VALIDATION_PASS",
        "native_afh_validated": False,
        "rows_compared": NATIVE_EXPECTED_ROWS,
        "charge_rows": len(charge_rows),
        "spatial_rows": len(spatial_rows),
        "spatial_multipole_rows": int(spatial_meta["multipole_rows"]),
        "max_charge_cauchy_excess": max_charge_cauchy_excess,
        "max_spatial_cauchy_excess": max_spatial_cauchy_excess,
    }
    gate = {
        "comparison": comparison,
        "provenance": {
            "status": "PROVISIONAL_PYTHON_AFH_V6_TRANSLATION",
            "native_afh_validated": False,
            "source_commit": expected_source_commit,
            "source_file_sha256": expected_source_sha,
            "charge_csv_sha256": charge_sha,
            "spatial_response_sha256": spatial_response_sha,
            "spatial_multipole_sha256": spatial_multipole_sha,
            "charge_artifact_run_id": 44222087512,
            "charge_artifact_id": 14391456283,
            "spatial_artifact_run_id": 44432440600,
            "spatial_artifact_id": 14486014588,
            "C0_by_isotope": {str(A): c0_by_A[A] for A in ISOTOPES},
        },
        "sha256_verified_files": [
            "charge/afh_v6_full_eight_response_7isotope.csv",
            "charge/metadata.json",
            "charge/validation.json",
            "charge/source_commit.txt",
            "spatial/afh_spatial_obdme_responses_7isotope_2401.csv",
            "spatial/afh_spatial_obdme_multipoles_7isotope_2401.csv",
        ],
    }
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
    pchip_values = {}
    use_psd_preserving_linear = (
        bundle_entry.get("interpolation_mode") == "linear_psd_preserving"
    )
    for name in response_names:
        values = bundle_entry["physical"][name]
        pchip = PchipInterpolator(q, values, extrapolate=False)
        pchip_values[name] = float(pchip(q_GeV))
        linear[name] = float(np.interp(q_GeV, q, values))
        # A common linear interpolation of all response-matrix entries is a
        # convex combination of the endpoint response matrices and therefore
        # preserves their Cauchy-Schwarz/PSD constraints. Independent PCHIP
        # curves do not guarantee this near response zeros.
        out[name] = (
            linear[name] if use_psd_preserving_linear else pchip_values[name]
        )
    return {
        "physical_equal_pn": out,
        "linear_physical_equal_pn": linear,
        "pchip_physical_equal_pn": pchip_values,
        "pchip_linear_relative_difference": {
            name: abs(pchip_values[name] - linear[name]) / max(abs(pchip_values[name]), abs(linear[name]), 1.0e-300)
            for name in response_names
        },
        "interpolation_used": (
            "linear_psd_preserving" if use_psd_preserving_linear else "pchip"
        ),
    }


def form_factor_values(
    qA_GeV: float,
    prescription: str,
    *,
    tN_GeV2: float,
) -> tuple[float, float]:
    """Return effective-nucleon Fhat_1,Fhat_2 for the external gVN basis.

    Formal production uses t_N=t_A=-2*m_A*E_R. The AFH response uses the
    independent spatial Q_A^2. Raw universal u+d+s form factors are divided
    by three exactly once because the external prefactor contains g_VN=3*g_Vq.
    """
    QN2 = -float(tN_GeV2)
    if QN2 < 0.0 or not math.isfinite(QN2):
        raise ValueError("nucleon invariant Q_N^2 must be finite and non-negative")
    if prescription == "q0_anchor":
        raw = (RAW_F1_UDS0, RAW_F2_UDS0)
    elif prescription == "bishara_linear":
        raw = bishara_linear(QN2)
    elif prescription == "isoscalar_zexp":
        raw = isoscalar_zexp(QN2)
    else:
        raise ValueError(f"unknown form-factor prescription: {prescription}")
    return effective_nucleon_form_factors(*raw)


def charge_kernel_from_coulomb_weight(
    L_C: float,
    qA_GeV: float,
    responses: dict[str, float],
    form_factor_prescription: str,
    *,
    tN_GeV2: float,
) -> dict:
    """Return A reference, B finite-t_N M-only baseline, and C extension."""
    if not math.isfinite(L_C) or L_C < 0.0:
        raise ValueError(f"invalid continuity-adjusted Coulomb weight L_C={L_C}")
    F1hat, F2hat = form_factor_values(
        qA_GeV, form_factor_prescription, tN_GeV2=tN_GeV2
    )
    cM, cPhi = charge_coefficients(
        qA_GeV, F1=F1hat, F2=F2hat, tN_GeV2=tN_GeV2
    )
    WM = float(responses["M"])
    WPhi = float(responses["PhiPP"])
    WMPhi = float(responses["MPhiPP"])
    if WM <= 0.0 or WPhi < -1.0e-12:
        raise ValueError("invalid AFH M/Phi'' diagonal response")
    A_reference = L_C * WM
    B_baseline = cM * cM * L_C * WM
    terms = {
        "M": B_baseline,
        "PhiPP": cPhi * cPhi * L_C * WPhi,
        "MPhiPP": 2.0 * cM * cPhi * L_C * WMPhi,
    }
    C_extension = sum(terms.values())
    if min(A_reference, B_baseline, C_extension) <= 0.0:
        raise ValueError("non-positive A/B/C charge kernel")
    raw_F1, raw_F2 = (
        (RAW_F1_UDS0, RAW_F2_UDS0) if form_factor_prescription == "q0_anchor"
        else (bishara_linear(-tN_GeV2) if form_factor_prescription == "bishara_linear"
              else isoscalar_zexp(-tN_GeV2))
    )
    return {
        "form_factor_prescription": form_factor_prescription,
        "F1V_quark_sum": raw_F1,
        "F2V_quark_sum": raw_F2,
        "F1N_effective": F1hat,
        "F2N_effective": F2hat,
        "tN_GeV2": float(tN_GeV2),
        "Q_N2_GeV2": -float(tN_GeV2),
        "cM": cM,
        "cPhiPP": cPhi,
        "L_C": float(L_C),
        "terms": terms,
        "baseline_A_original_AFH_M": A_reference,
        "baseline_B_finite_tN_M": B_baseline,
        "extension_C_MplusPhiPP": C_extension,
        "relative_B_vs_A": B_baseline / A_reference - 1.0,
        "relative_C_vs_A": C_extension / A_reference - 1.0,
        "relative_C_vs_B": C_extension / B_baseline - 1.0,
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
    charge_residual = abs(charge - charge_check["extension_C_MplusPhiPP"]) / max(
        abs(charge), abs(charge_check["extension_C_MplusPhiPP"]), 1.0e-300
    )
    if charge_residual > 2.0e-12:
        raise AssertionError(
            f"charge-sector reconstruction mismatch: {charge_residual:.6g}"
        )
    return {
        "F1N_effective": F1,
        "F2N_effective": F2,
        "tN_GeV2": tN_GeV2,
        "L_C": coefficients["L_C_continuity_adjusted_charge_weight"],
        "L_T": float(np.real(L[1, 1] + L[2, 2])),
        "charge_sector": charge,
        "spatial_sector": spatial,
        "leading_static_vector_current_candidate": total,
        "baseline_A_original_AFH_M": charge_check["baseline_A_original_AFH_M"],
        "baseline_B_finite_tN_M": charge_check["baseline_B_finite_tN_M"],
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
    native_dir: Path | None = None,
    provisional_charge_dir: Path | None = None,
    provisional_spatial_dir: Path | None = None,
    mchi: float = MCHI_DEFAULT,
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
        raise ValueError("formal three-body halo production requires the asymmetric Pole width prescription")
    if native_dir is not None:
        if provisional_charge_dir is not None or provisional_spatial_dir is not None:
            raise ValueError("choose native AFH inputs or provisional Python AFH inputs, not both")
        native_bundle, afh_input_gate = load_native_response_bundle(native_dir)
    else:
        if provisional_charge_dir is None or provisional_spatial_dir is None:
            raise ValueError("provide --native-dir or both provisional charge and spatial directories")
        native_bundle, afh_input_gate = load_provisional_response_bundle(
            provisional_charge_dir, provisional_spatial_dir
        )
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
                    tA_GeV2 = ER * ER - qA * qA
                    tA_expected_GeV2 = -2.0 * mA * ER
                    if not math.isclose(tA_GeV2, tA_expected_GeV2, rel_tol=2.0e-12, abs_tol=2.0e-18):
                        raise ArithmeticError("q_A, E_R and m_A violate the exact nuclear mass-shell transfer")
                    tN_GeV2 = tA_GeV2
                    kernel = charge_kernel_from_coulomb_weight(
                        coulomb_result["L_C"], qA,
                        response["physical_equal_pn"],
                        form_factor_prescription,
                        tN_GeV2=tN_GeV2,
                    )
                    # The propagator uses invariant t_A, not spatial Q_A^2.
                    denominator = mediator_denominator_squared_GeV4(mV, mA, ER_keV)
                    common = (
                        mA * coupling_product_squared
                        / (256.0 * math.pi**3 * pchi * pchi * denominator)
                    )
                    halo_charge += float(w) * fv * beta * common * kernel["extension_C_MplusPhiPP"]
                    halo_A_reference += float(w) * fv * beta * common * kernel["baseline_A_original_AFH_M"]
                    halo_B_baseline += float(w) * fv * beta * common * kernel["baseline_B_finite_tN_M"]
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
                            candidate["leading_static_vector_current_candidate"],
                        )
                        halo_spatial_candidate += (
                            float(w) * fv * beta * common * candidate["spatial_sector"]
                        )
                        halo_full_candidate += (
                            float(w) * fv * beta * common
                            * candidate["leading_static_vector_current_candidate"]
                        )
                isotope_row = {
                    "A": A, "abundance": xA, "open": True,
                    "mA_GeV": mA, "qA_GeV": qA, "vmin_km_s": vmin,
                    "baseline_A_original_AFH_M_halo_integral": halo_A_reference,
                    "baseline_B_finite_tN_M_halo_integral": halo_B_baseline,
                    "extension_C_MplusPhiPP_halo_integral": halo_charge,
                    "relative_B_vs_A": halo_B_baseline / halo_A_reference - 1.0
                    if halo_A_reference else math.nan,
                    "relative_C_vs_A": halo_charge / halo_A_reference - 1.0
                    if halo_A_reference else math.nan,
                    "relative_C_vs_B": halo_charge / halo_B_baseline - 1.0
                    if halo_B_baseline else math.nan,
                    "max_pchip_linear_response_difference": max_interp_difference,
                    "max_abs_charge_continuity_relative_correction": max_abs_continuity_correction,
                    "max_continuity_identity_relative_residual": max_continuity_identity_residual,
                    "nv": nv, "nw": nw, "nz": nz, "nphi": nphi,
                }
                if include_leading_static_vector_candidate:
                    isotope_row.update({
                        "spatial_candidate_halo_integral": halo_spatial_candidate,
                        "leading_static_vector_candidate_halo_integral": halo_full_candidate,
                        "relative_spatial_candidate_vs_coulomb": (
                            halo_spatial_candidate / halo_charge if halo_charge else math.nan
                        ),
                        "relative_full_candidate_vs_A": (
                            halo_full_candidate / halo_A_reference - 1.0
                            if halo_A_reference else math.nan
                        ),
                        "relative_full_candidate_vs_B": (
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
                r.get("abundance", 0.0) * r.get("extension_C_MplusPhiPP_halo_integral", 0.0)
                for r in isotope_rows
            )
            total_A_reference = sum(
                r.get("abundance", 0.0) * r.get("baseline_A_original_AFH_M_halo_integral", 0.0)
                for r in isotope_rows
            )
            total_B_baseline = sum(
                r.get("abundance", 0.0) * r.get("baseline_B_finite_tN_M_halo_integral", 0.0)
                for r in isotope_rows
            )
            total_rate = rate_factor * total_charge
            A_reference_rate = rate_factor * total_A_reference
            B_baseline_rate = rate_factor * total_B_baseline
            row = {
                "ER_keV": ER_keV,
                "halo_model": halo_name,
                "rate_A_original_AFH_M_events_kg_day_keV": A_reference_rate,
                "rate_B_baseline_M_events_kg_day_keV": B_baseline_rate,
                "rate_C_charge_extension_events_kg_day_keV": total_rate,
                "relative_B_vs_A": B_baseline_rate / A_reference_rate - 1.0
                if A_reference_rate else math.nan,
                "relative_C_vs_A": total_rate / A_reference_rate - 1.0
                if A_reference_rate else math.nan,
                "relative_C_vs_B": total_rate / B_baseline_rate - 1.0
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
                    r.get("abundance", 0.0) * r.get("leading_static_vector_candidate_halo_integral", 0.0)
                    for r in isotope_rows
                )
                spatial_rate = rate_factor * total_spatial
                full_rate = rate_factor * total_full
                row.update({
                    "rate_spatial_candidate_events_kg_day_keV": spatial_rate,
                    "rate_leading_static_vector_candidate_events_kg_day_keV": full_rate,
                    "relative_spatial_candidate_vs_coulomb": (
                        total_spatial / total_charge if total_charge else math.nan
                    ),
                    "relative_full_candidate_vs_A": (
                        full_rate / A_reference_rate - 1.0 if A_reference_rate else math.nan
                    ),
                    "relative_full_candidate_vs_B": (
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
            "point-nucleus identity is an algebraic convention check, not proof "
            "of many-body current conservation"
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
        "AFH_input_validation": afh_input_gate["comparison"],
        "AFH_input_provenance": afh_input_gate["provenance"],
        "AFH_sha256_verified_files": afh_input_gate["sha256_verified_files"],
        "native_afh_validated": bool(afh_input_gate["comparison"].get("native_afh_validated", False)),
        "form_factor_prescription": form_factor_prescription,
        "width_scheme": width_scheme,
        "formal_width_prescription": (
            "Asymmetric Pole prescription: first p-k chi2 propagator zero-width (+i0+); "
            "second p'+k chi2 propagator uses constant Gamma_chi2(m_chi2)."
        ),
        "mediator_denominator": "(mV^2-t_A)^2=(mV^2+2*mA*ER)^2; t_A=-2*mA*ER",
        "nuclear_spatial_momentum": "Q_A^2=2*mA*ER+ER^2; used only in AFH y_A and spatial NR coefficients",
        "nucleon_transfer_scheme": "strict one-body impulse q_N^mu=q_A^mu; t_N=t_A=-2*mA*ER",
        "coupling_basis": "external (g1*g2*gVN)^2 with gVN=3*gVq; use Fhat_i=F_i^(u+d+s)/3",
        "primary_baseline": "B: finite-t_N effective nucleon current times finite-size AFH W_M(y_A) only",
        "A_reference": "q=0 effective nucleon current times the same finite-size AFH W_M(y_A)",
        "C_extension": "B plus Phi'' and signed M-Phi'' interference; diagnostic extension, not the primary baseline",
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
            "common linear interpolation on provisional Python AFH response matrices to preserve PSD/Cauchy bounds; PCHIP retained as a diagnostic"
            if afh_input_gate["comparison"].get("native_afh_validated") is False
            else "PCHIP on native 0.25 MeV absolute response values; linear interpolation retained as a diagnostic"
        ),
        "recoil_momentum": "q_A=sqrt(2 m_A E_R + E_R^2), exact nuclear mass-shell relation",
        "coulomb_weight": "L_C=L00-(E_R/q_A)(L03+L30)+(E_R/q_A)^2 L33, conditional on conservation of the complete nuclear vector current",
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
        default=None,
        help="extracted root of a provenance-validated native AFH eight-response artifact",
    )
    parser.add_argument("--provisional-charge-dir", type=Path, default=None,
                        help="AFH-8 provisional Python charge-response artifact directory")
    parser.add_argument("--provisional-spatial-dir", type=Path, default=None,
                        help="P3-B provisional Python spatial-response artifact directory")
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
        required=True,
    )
    parser.add_argument(
        "--width-scheme",
        choices=("zero", "pole", "running"),
        default="pole",
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
    if args.width_scheme != "pole":
        parser.error("formal production accepts only the asymmetric Pole width prescription")
    provisional_selected = args.provisional_charge_dir is not None or args.provisional_spatial_dir is not None
    if (args.native_dir is None) == (not provisional_selected):
        parser.error("provide either --native-dir or both provisional AFH directories")
    if provisional_selected and (args.provisional_charge_dir is None or args.provisional_spatial_dir is None):
        parser.error("both --provisional-charge-dir and --provisional-spatial-dir are required")
    result = fold(
        native_dir=args.native_dir,
        provisional_charge_dir=args.provisional_charge_dir,
        provisional_spatial_dir=args.provisional_spatial_dir,
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
