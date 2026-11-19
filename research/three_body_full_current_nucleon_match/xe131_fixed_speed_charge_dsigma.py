#!/usr/bin/env python3
"""Fixed-speed Xe-131 differential cross-section ratio in the Coulomb sector.

The DM-side L_C is obtained from the full phase-space-integrated tensor using
the nuclear-current continuity relation, conditional on conservation of the
complete nuclear vector current. Native AFH M/Phi''/M-Phi'' responses are
contracted with finite-t_N charge coefficients and compared with the original
pointlike 9 W_M baseline using the formal constant pole-width prescription.
Transverse nuclear-current multipoles are not included in this restricted
Coulomb-sector ratio.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

from nucleon_vector_form_factors import F1V0, charge_coefficients, isoscalar_zexp
from native_charge_sector_halo_fold import load_isotope_inputs
from three_body_phase_space_tensor import integrate_spin_resolved_tensor

MCHI_GEV = 1000.0
MS_GEV = 300.0e-6
XE131_MASS_RECORD = load_isotope_inputs()[131]
MA_XE131_GEV = float(XE131_MASS_RECORD["mA_GeV"])
MN_GEV = 0.938918
SPEED_KM_S = 776.0
G2 = 1.0
MV_GEV = 10.0
NATIVE_CSV_SHA256 = "b1b65708cd103058c3bcaea50bf65550d5671a88e97000b94f2536fbc60a59ff"
NATIVE_ARCHIVE_COMMIT = "e6d9dee3527cab200ee6b21198d577b987282fac"
NATIVE_EXPORT_COMMIT = "54e1ff10bba0cbffe7acc6af428014415c708475"
EXPECTED_AFH_SOURCE_SHA256 = "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372"
EXPECTED_DENSITY_MATRIX_SHA256 = "f656145ba2fb9da741b77faed4c01d0dc457c955fa340928b5dbf9cee9bc5d45"


def canonical_sha256(raw: bytes) -> str:
    """Hash native text exports after canonicalizing Windows CRLF to LF."""
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()

# (delta_m [GeV], medium order, high order)
BENCHMARKS = {
    200.0: (450.0e-6, (32, 24, 12), (40, 32, 16)),
    267.0: (362.0e-6, (40, 24, 12), (48, 32, 16)),
}
WIDTH_SCHEMES = ("pole",)


def exact_qA_GeV(mA_GeV: float, ER_keV: float) -> float:
    ER = ER_keV * 1.0e-6
    return math.sqrt(2.0 * mA_GeV * ER + ER * ER)


def load_native_xe131_responses(path: Path) -> tuple[dict, dict]:
    raw = path.read_bytes()
    raw_digest = hashlib.sha256(raw).hexdigest()
    canonical_digest = canonical_sha256(raw)
    if canonical_digest != NATIVE_CSV_SHA256:
        raise ValueError(
            "Native Xe-131 CSV canonical SHA-256 mismatch: "
            f"expected {NATIVE_CSV_SHA256}, got {canonical_digest} "
            f"(raw checkout hash {raw_digest})"
        )

    metadata_path = path.with_name("afh_default_xe131_M_PhiPP_metadata.json")
    validation_path = path.with_name("afh_default_xe131_M_PhiPP_validation.json")
    manifest_path = path.with_name("sha256_manifest.json")
    for required in (metadata_path, validation_path, manifest_path):
        if not required.is_file():
            raise FileNotFoundError(f"native Xe-131 provenance file is missing: {required}")

    metadata_raw = metadata_path.read_bytes()
    validation_raw = validation_path.read_bytes()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    metadata = json.loads(metadata_raw.decode("utf-8-sig"))
    validation = json.loads(validation_raw.decode("utf-8-sig"))
    expected_files = manifest.get("files", {})
    actual_files = {
        path.name: canonical_digest,
        metadata_path.name: canonical_sha256(metadata_raw),
        validation_path.name: canonical_sha256(validation_raw),
    }
    if manifest.get("status") != "COMPLETED":
        raise ValueError("native Xe-131 SHA-256 manifest is not completed")
    for name, digest in actual_files.items():
        if expected_files.get(name) != digest:
            raise ValueError(
                f"native Xe-131 provenance SHA-256 mismatch for {name}: "
                f"manifest={expected_files.get(name)}, actual={digest}"
            )

    expected_indices = {"M": 1, "PhiPP": 4, "M_PhiPP": 7}
    if metadata.get("status") != "COMPLETED":
        raise ValueError("native Xe-131 metadata status is not COMPLETED")
    if metadata.get("source") != "AFH DMFormFactor v6.0 native Wolfram execution":
        raise ValueError("native Xe-131 metadata source is not AFH v6.0 Wolfram")
    if metadata.get("afh_source_sha256") != EXPECTED_AFH_SOURCE_SHA256:
        raise ValueError("native Xe-131 AFH source SHA-256 does not match the pinned source")
    if metadata.get("density_matrix_csv_sha256") != EXPECTED_DENSITY_MATRIX_SHA256:
        raise ValueError("native Xe-131 density-matrix SHA-256 does not match the pinned input")
    if metadata.get("isotope_A") != 131 or metadata.get("Z") != 54:
        raise ValueError("native Xe-131 metadata has the wrong isotope identity")
    if metadata.get("response_indices") != expected_indices:
        raise ValueError("native Xe-131 response-index map is not M/PhiPP/M-PhiPP")
    if metadata.get("grid_points") != 2401:
        raise ValueError("native Xe-131 metadata does not specify 2,401 q points")
    if not math.isclose(float(metadata.get("q_min_GeV", math.nan)), 0.0, abs_tol=1e-14):
        raise ValueError("native Xe-131 q_min is not zero")
    if not math.isclose(float(metadata.get("q_max_GeV", math.nan)), 0.6, abs_tol=1e-14):
        raise ValueError("native Xe-131 q_max is not 0.6 GeV")
    if not math.isclose(float(metadata.get("dq_GeV", math.nan)), 0.00025, abs_tol=1e-14):
        raise ValueError("native Xe-131 dq is not 0.00025 GeV")
    if metadata.get("factor_four_applied_once") is not True:
        raise ValueError("native Xe-131 equal-p/n factor-four bookkeeping is not certified")
    if "14.2.0" not in str(metadata.get("wolfram_version", "")):
        raise ValueError("native Xe-131 Wolfram version is not 14.2.0")
    if metadata.get("csv_sha256") != NATIVE_CSV_SHA256:
        raise ValueError("native Xe-131 metadata CSV SHA-256 disagrees with canonical hash")
    if validation.get("status") != "PASS" or validation.get("rows") != 2401:
        raise ValueError("native Xe-131 response-level validation did not PASS")
    if validation.get("metadata_sha256") != actual_files[metadata_path.name]:
        raise ValueError("native Xe-131 validation does not pin the canonical metadata hash")
    if validation.get("csv_sha256") != NATIVE_CSV_SHA256:
        raise ValueError("native Xe-131 validation CSV SHA-256 disagrees with canonical hash")
    if float(validation.get("max_imaginary_residual", math.inf)) > 2.0e-12:
        raise ValueError("native Xe-131 imaginary response residual is too large")
    if float(validation.get("maximum_Cauchy_excess", math.inf)) > 2.0e-12:
        raise ValueError("native Xe-131 M/Phi interference Cauchy check failed")

    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 2401:
        raise ValueError(f"expected 2401 native AFH rows, got {len(rows)}")
    q = np.asarray([float(row["q_GeV"]) for row in rows], dtype=float)
    expected_q = np.linspace(0.0, 0.6, 2401)
    if not np.allclose(q, expected_q, rtol=0.0, atol=2e-12):
        raise ValueError("native Xe-131 AFH q grid is not the canonical 2401-point grid")
    columns = {
        "M": "R_M_physical_equal_pn",
        "PhiPP": "R_PhiPP_physical_equal_pn",
        "MPhiPP": "R_MPhiPP_physical_equal_pn",
    }
    responses = {
        name: np.asarray([float(row[column]) for row in rows], dtype=float)
        for name, column in columns.items()
    }
    if not all(np.all(np.isfinite(values)) for values in responses.values()):
        raise ValueError("native AFH response archive contains non-finite values")
    return {"q": q, "responses": responses}, {
        "sha256_policy": "UTF-8 text normalized to LF before SHA-256",
        "sha256_canonical_lf": canonical_digest,
        "sha256_raw_checkout": raw_digest,
        "metadata_sha256_canonical_lf": actual_files[metadata_path.name],
        "validation_sha256_canonical_lf": actual_files[validation_path.name],
        "native_archive_commit": NATIVE_ARCHIVE_COMMIT,
        "original_export_commit": NATIVE_EXPORT_COMMIT,
        "rows": len(rows),
        "native_package": "AFH DMFormFactor v6.0 / Wolfram 14.2.0",
        "afh_source_sha256": metadata["afh_source_sha256"],
        "density_matrix_csv_sha256": metadata["density_matrix_csv_sha256"],
        "response_columns": columns,
        "normalization": "physical equal-p/n columns; factor four applied once",
        "mass_record": XE131_MASS_RECORD,
        "mass_convention": "bare nucleus: (atomic_mass_u - Z*m_e[u])*u_GeV",
    }
def interpolate_responses(bundle: dict, qA_GeV: float) -> dict:
    q = bundle["q"]
    if qA_GeV < q[0] or qA_GeV > q[-1]:
        raise ValueError("q_A lies outside the native AFH Xe-131 grid")
    pchip = {
        name: float(PchipInterpolator(q, values, extrapolate=False)(qA_GeV))
        for name, values in bundle["responses"].items()
    }
    linear = {
        name: float(np.interp(qA_GeV, q, values))
        for name, values in bundle["responses"].items()
    }
    return {"pchip": pchip, "linear": linear}


def charge_sector_kernels(
    L_C: float, qA_GeV: float, responses: dict[str, float]
) -> dict:
    """Return finite-t_N M+Phi'' and pointlike M-only Coulomb-sector kernels."""
    Q2 = qA_GeV * qA_GeV
    F1, F2 = isoscalar_zexp(Q2)
    cM, cPhi = charge_coefficients(qA_GeV, F1=F1, F2=F2, mN_GeV=MN_GEV)
    WM, WPhi, WMPhi = responses["M"], responses["PhiPP"], responses["MPhiPP"]
    if WM <= 0.0:
        raise ValueError(f"non-positive native W_M at q_A={qA_GeV:.12g} GeV")
    if not math.isfinite(L_C) or L_C <= 0.0:
        raise ValueError("invalid continuity-adjusted Coulomb weight L_C")

    finite_t_M_kernel = cM * cM * L_C * WM
    interference_kernel = 2.0 * cM * cPhi * L_C * WMPhi
    phi_kernel = cPhi * cPhi * L_C * WPhi
    full_charge_kernel = finite_t_M_kernel + interference_kernel + phi_kernel
    pointlike_M_kernel = F1V0 * F1V0 * L_C * WM
    if pointlike_M_kernel <= 0.0 or full_charge_kernel <= 0.0:
        raise ValueError("non-positive numerator or denominator kernel")

    eta = cPhi / cM
    Qphi = 1.0 + 2.0 * eta * (WMPhi / WM) + eta * eta * (WPhi / WM)
    ratio_direct = full_charge_kernel / pointlike_M_kernel
    ratio_finite_t_M = full_charge_kernel / finite_t_M_kernel
    ratio_factorized = (cM * cM / (F1V0 * F1V0)) * Qphi
    ratio_legacy_F1_squared = (F1 * F1 / (F1V0 * F1V0)) * Qphi
    if not math.isclose(ratio_direct, ratio_factorized, rel_tol=2e-13, abs_tol=2e-15):
        raise AssertionError("direct and factorized Coulomb-sector ratios disagree")

    return {
        "F1V_finite_t": F1,
        "F2V_finite_t": F2,
        "cM": cM,
        "cPhiPP": cPhi,
        "eta_cPhi_over_cM": eta,
        "W_PhiPP_over_W_M": WPhi / WM,
        "W_MPhiPP_over_W_M": WMPhi / WM,
        "Q_PhiPP_relative_to_finite_t_M": Qphi,
        "finite_t_M_only_over_q0_M_reference": (cM * cM) / 9.0,
        "full_charge_over_finite_t_M": ratio_finite_t_M,
        "relative_change_vs_finite_t_M_percent": 100.0 * (ratio_finite_t_M - 1.0),
        "full_charge_over_q0_M_reference": ratio_direct,
        "relative_change_vs_q0_M_reference_percent": 100.0 * (ratio_direct - 1.0),
        # Legacy aliases: the denominator is the q=0 nucleon-form-factor M reference.
        "finite_t_M_only_over_pointlike_M": (cM * cM) / 9.0,
        "full_charge_over_pointlike_M": ratio_direct,
        "relative_change_percent": 100.0 * (ratio_direct - 1.0),
        "legacy_F1_squared_ratio_for_normalization_audit": ratio_legacy_F1_squared,
        "legacy_F1_squared_relative_change_percent": 100.0 * (ratio_legacy_F1_squared - 1.0),
        "kernels_with_common_LC": {
            "pointlike_M_only": pointlike_M_kernel,
            "finite_t_M_only": finite_t_M_kernel,
            "M_Phi_interference": interference_kernel,
            "PhiPP_diagonal": phi_kernel,
            "finite_t_M_plus_PhiPP": full_charge_kernel,
        },
    }
def integrate_LC(
    ER_keV: float,
    delta_m_GeV: float,
    width_scheme: str,
    order: tuple[int, int, int],
) -> dict:
    nw, nz, nphi = order
    result = integrate_spin_resolved_tensor(
        mchi=MCHI_GEV,
        ms=MS_GEV,
        delta_m=delta_m_GeV,
        mA=MA_XE131_GEV,
        ER=ER_keV * 1.0e-6,
        speed_kms=SPEED_KM_S,
        g2=G2,
        width_scheme=width_scheme,
        mapping="threshold_u2",
        nw=nw,
        nz=nz,
        nphi=nphi,
        crosscheck_dirac_trace=False,
    )
    if not result.get("phase_space_open", False):
        raise RuntimeError(
            f"three-body phase space is closed for ER={ER_keV} keV, width={width_scheme}"
        )
    contractions = result["point_nucleus_contractions"]
    L00 = float(contractions["I00"])
    L_C = float(contractions["L_C_continuity_adjusted"])
    continuity_residual = float(contractions["continuity_reduced_relative_residual"])
    if not math.isfinite(L00) or L00 <= 0.0:
        raise ValueError("invalid phase-space-integrated L00")
    if not math.isfinite(L_C) or L_C <= 0.0:
        raise ValueError("invalid continuity-adjusted Coulomb weight L_C")
    if not math.isfinite(continuity_residual) or continuity_residual > 5.0e-12:
        raise ValueError("point-nucleus nuclear-continuity identity failed")
    q_exact = exact_qA_GeV(MA_XE131_GEV, ER_keV)
    q_phase = float(result["qA_magnitude_GeV"])
    if not math.isclose(q_phase, q_exact, rel_tol=0.0, abs_tol=2.0e-12):
        raise ValueError("phase-space q_A disagrees with canonical Xe-131 mass-shell q_A")
    return {
        "L00": L00,
        "L_C": L_C,
        "charge_continuity_relative_correction": L_C / L00 - 1.0,
        "continuity_identity_relative_residual": continuity_residual,
        "qA_from_phase_space_GeV": q_phase,
        "pole_clearance_keV": float(result["pole_clearance_keV"]),
        "quadrature_points": int(result["quadrature_points"]),
        "order": {"nw": nw, "nz": nz, "nphi": nphi},
    }
def run(afh_csv: Path) -> dict:
    bundle, provenance = load_native_xe131_responses(afh_csv)
    results = []
    for ER_keV, (delta_m, medium_order, high_order) in BENCHMARKS.items():
        qA = exact_qA_GeV(MA_XE131_GEV, ER_keV)
        response_interp = interpolate_responses(bundle, qA)
        high_response = response_interp["pchip"]
        linear_response = response_interp["linear"]
        width_rows = []
        for width in WIDTH_SCHEMES:
            medium = integrate_LC(ER_keV, delta_m, width, medium_order)
            high = integrate_LC(ER_keV, delta_m, width, high_order)
            convergence_LC = abs(high["L_C"] - medium["L_C"]) / abs(high["L_C"])
            convergence_L00 = abs(high["L00"] - medium["L00"]) / abs(high["L00"])
            if max(convergence_LC, convergence_L00) > 1.0e-3:
                raise RuntimeError(
                    f"phase-space medium/high convergence failed: ER={ER_keV}, "
                    f"width={width}, LC={convergence_LC:.6g}, L00={convergence_L00:.6g}"
                )
            kernels = charge_sector_kernels(high["L_C"], qA, high_response)
            linear_kernels = charge_sector_kernels(high["L_C"], qA, linear_response)
            width_rows.append({
                "width_scheme": width,
                "g2": G2,
                "delta_m_keV": delta_m * 1.0e6,
                "speed_kms": SPEED_KM_S,
                "phase_space": {
                    "medium": medium,
                    "high": high,
                    "L_C_medium_high_relative_difference": convergence_LC,
                    "L00_medium_high_relative_difference": convergence_L00,
                },
                "nuclear_kinematics": {
                    "mA_GeV": MA_XE131_GEV,
                    "atomic_mass_u": XE131_MASS_RECORD["atomic_mass_u"],
                    "ER_keV": ER_keV,
                    "qA_exact_GeV": qA,
                    "tN_GeV2_static": -(qA * qA),
                },
                "native_AFH_responses_pchip": high_response,
                "native_AFH_responses_linear_check": linear_response,
                "finite_tN_form_factors_and_charge_kernels": kernels,
                "linear_interpolation_cross_section_ratio": (
                    linear_kernels["full_charge_over_finite_t_M"]
                ),
                "pchip_minus_linear_ratio": (
                    kernels["full_charge_over_finite_t_M"]
                    - linear_kernels["full_charge_over_finite_t_M"]
                ),
                "linear_interpolation_ratio_vs_q0_reference": (
                    linear_kernels["full_charge_over_q0_M_reference"]
                ),
                "pchip_ratio_vs_q0_reference": (
                    kernels["full_charge_over_q0_M_reference"]
                ),
            })
        ratios = [
            row["finite_tN_form_factors_and_charge_kernels"]["full_charge_over_finite_t_M"]
            for row in width_rows
        ]
        if len(width_rows) != 1 or width_rows[0]["width_scheme"] != "pole":
            raise AssertionError("formal fixed-speed charge result must contain exactly one pole-width scenario")
        results.append({
            "ER_keV": ER_keV,
            "benchmark": {
                "mchi1_GeV": MCHI_GEV,
                "ms_keV": MS_GEV * 1.0e6,
                "delta_m_keV": delta_m * 1.0e6,
                "speed_kms": SPEED_KM_S,
                "g2": G2,
                "mV_GeV_common_prefactor_only": MV_GEV,
                "target": "Xe-131",
            },
            "fixed_speed_differential_cross_section_ratio": (
                width_rows[0]["finite_tN_form_factors_and_charge_kernels"][
                    "full_charge_over_finite_t_M"
                ]
            ),
            "relative_change_percent": (
                width_rows[0]["finite_tN_form_factors_and_charge_kernels"][
                    "relative_change_vs_finite_t_M_percent"
                ]
            ),
            "legacy_ratio_vs_q0_M_reference": (
                width_rows[0]["finite_tN_form_factors_and_charge_kernels"][
                    "full_charge_over_q0_M_reference"
                ]
            ),
            "width_scenarios": width_rows,
            "formal_width_scheme": "pole",
            "common_factorization_check": {
                "ratio_uses_same_LC_in_numerator_and_denominator": True,
                "interpretation": "the common pole-width phase-space factor L_C cancels from this normalized ratio",
            },
        })
    return {
        "status": "PASS_XE131_FIXED_SPEED_COULOMB_SECTOR_RATIO",
        "scope": (
            "fixed-speed Xe-131 differential cross-section ratio in the "
            "M+Phi''+M-Phi'' Coulomb sector; the complete 2->3 DM phase space "
            "is integrated with both scalar-radiation diagrams and finite chi2 "
            "widths, while native AFH transverse-current responses are not included"
        ),
        "ratio_definition": (
            "(dSigma/dER)_[finite-tN M+Phi'' Coulomb sector] / "
            "(dSigma/dER)_[same finite-tN M-only with identical F1,F2]"
        ),
        "secondary_reference_definition": (
            "(dSigma/dER)_[finite-tN M+Phi'' Coulomb sector] / "
            "(dSigma/dER)_[q=0 nucleon-form-factor M-only reference]"
        ),
        "factorization": (
            "The same continuity-adjusted L_C^(3), propagator, flux, and phase-space "
            "prefactor multiply numerator and denominator and cancel in the ratio."
        ),
        "DM_benchmark": {
            "mchi1_GeV": MCHI_GEV,
            "ms_keV": MS_GEV * 1.0e6,
            "speed_kms": SPEED_KM_S,
            "g2": G2,
            "width_schemes": list(WIDTH_SCHEMES),
            "formal_width_prescription": "Eq. (19) asymmetric: first p-k propagator remains zero-width (+i0+); second p'+k propagator uses constant pole width evaluated at m_chi2",
        },
        "nuclear_input": {
            "target": "Xe-131",
            "mA_bare_nucleus_GeV": MA_XE131_GEV,
            "mass_record": XE131_MASS_RECORD,
            "AFH_native_provenance": provenance,
            "recoil_momentum_convention": "q_A=sqrt(2*m_A*E_R+E_R^2)",
            "nucleon_invariant_convention": "t_N=-|q_A|^2 in the static impulse matching",
        },
        "form_factor_prescription": (
            "central isoscalar_zexp diagnostic from nucleon_vector_form_factors.py; "
            "not a final validated universal finite-Q^2 u+d+s input"
        ),
        "results": results,
        "limitations": [
            "This is not the complete L_mu_nu W_A^mu_nu result because native Delta/Sigma transverse responses are not included.",
            "The spatial-current sector was previously found negligible in provisional fixed-speed contractions, but that does not replace native spatial-response validation.",
            "The finite-Q2 form-factor prescription remains diagnostic, especially F2^V(Q2).",
            "No halo velocity average, isotope sum, detector response, or absolute coupling normalization is included.",
            "The common phase-space factor in this ratio is L_C, not L00 alone.",
        ],
    }
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--afh-csv", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.afh_csv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "rows": len(result["results"]),
        "results": [
            {
                "ER_keV": row["ER_keV"],
                "ratio": row["fixed_speed_differential_cross_section_ratio"],
                "relative_change_percent": row["relative_change_percent"],
            }
            for row in result["results"]
        ],
        "output": str(args.out),
    }, indent=2))


if __name__ == "__main__":
    main()
