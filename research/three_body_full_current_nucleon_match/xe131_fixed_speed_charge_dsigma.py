#!/usr/bin/env python3
"""Fixed-speed Xe-131 differential cross-section ratio in the charge sector.

The DM-side L00 is obtained by integrating the complete 2->3 phase space,
including both scalar-emission diagrams and their coherent interference,
with finite chi2 widths. The AFH charge response is contracted as
M + Phi'' + M-Phi'' and compared with the original pointlike 9 W_M baseline.

This is a charge-density-sector result: native Xe-131 M/Phi''/M-Phi''
responses are available, while the complete native spatial-current response
set is not yet available.
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
from three_body_phase_space_tensor import integrate_spin_resolved_tensor

MCHI_GEV = 1000.0
MS_GEV = 300.0e-6
MA_XE131_GEV = 121.9099224472
MN_GEV = 0.938918
SPEED_KM_S = 776.0
G2 = 1.0
MV_GEV = 10.0
NATIVE_CSV_SHA256 = "b1b65708cd103058c3bcaea50bf65550d5671a88e97000b94f2536fbc60a59ff"
NATIVE_SOURCE_COMMIT = "54e1ff10bba0cbffe7acc6af428014415c708475"

# (delta_m [GeV], medium order, high order)
BENCHMARKS = {
    200.0: (450.0e-6, (32, 24, 12), (40, 32, 16)),
    267.0: (362.0e-6, (40, 24, 12), (48, 32, 16)),
}
WIDTH_SCHEMES = ("pole", "running")


def exact_qA_GeV(mA_GeV: float, ER_keV: float) -> float:
    ER = ER_keV * 1.0e-6
    return math.sqrt(2.0 * mA_GeV * ER + ER * ER)


def load_native_xe131_responses(path: Path) -> tuple[dict, dict]:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != NATIVE_CSV_SHA256:
        raise ValueError(
            "Native Xe-131 CSV SHA-256 mismatch: "
            f"expected {NATIVE_CSV_SHA256}, got {digest}"
        )
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
        "sha256": digest,
        "source_commit": NATIVE_SOURCE_COMMIT,
        "rows": len(rows),
        "native_package": "AFH DMFormFactor v6.0 / Wolfram 14.2.0",
        "response_columns": columns,
        "normalization": "physical equal-p/n columns; factor four applied once",
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


def charge_sector_kernels(L00: float, qA_GeV: float, responses: dict[str, float]) -> dict:
    """Return finite-t_N M+Phi'' and pointlike M-only kernels."""
    Q2 = qA_GeV * qA_GeV
    F1, F2 = isoscalar_zexp(Q2)
    cM, cPhi = charge_coefficients(qA_GeV, F1=F1, F2=F2, mN_GeV=MN_GEV)
    WM, WPhi, WMPhi = responses["M"], responses["PhiPP"], responses["MPhiPP"]
    if WM <= 0.0:
        raise ValueError(f"non-positive native W_M at q_A={qA_GeV:.12g} GeV")

    finite_t_M_kernel = cM * cM * L00 * WM
    interference_kernel = 2.0 * cM * cPhi * L00 * WMPhi
    phi_kernel = cPhi * cPhi * L00 * WPhi
    full_charge_kernel = finite_t_M_kernel + interference_kernel + phi_kernel
    pointlike_M_kernel = F1V0 * F1V0 * L00 * WM
    if pointlike_M_kernel <= 0.0 or full_charge_kernel <= 0.0:
        raise ValueError("non-positive numerator or denominator kernel")

    eta = cPhi / cM
    Qphi = 1.0 + 2.0 * eta * (WMPhi / WM) + eta * eta * (WPhi / WM)
    ratio_direct = full_charge_kernel / pointlike_M_kernel
    ratio_factorized = (cM * cM / (F1V0 * F1V0)) * Qphi
    ratio_legacy_F1_squared = (F1 * F1 / (F1V0 * F1V0)) * Qphi
    if not math.isclose(ratio_direct, ratio_factorized, rel_tol=2e-13, abs_tol=2e-15):
        raise AssertionError("direct and factorized charge-sector ratios disagree")

    return {
        "F1V_finite_t": F1,
        "F2V_finite_t": F2,
        "cM": cM,
        "cPhiPP": cPhi,
        "eta_cPhi_over_cM": eta,
        "W_PhiPP_over_W_M": WPhi / WM,
        "W_MPhiPP_over_W_M": WMPhi / WM,
        "Q_PhiPP_relative_to_finite_t_M": Qphi,
        "finite_t_M_only_over_pointlike_M": (cM * cM) / 9.0,
        "full_charge_over_pointlike_M": ratio_direct,
        "relative_change_percent": 100.0 * (ratio_direct - 1.0),
        "legacy_F1_squared_ratio_for_normalization_audit": ratio_legacy_F1_squared,
        "legacy_F1_squared_relative_change_percent": 100.0 * (ratio_legacy_F1_squared - 1.0),
        "kernels_with_common_L00": {
            "pointlike_M_only": pointlike_M_kernel,
            "finite_t_M_only": finite_t_M_kernel,
            "M_Phi_interference": interference_kernel,
            "PhiPP_diagonal": phi_kernel,
            "finite_t_M_plus_PhiPP": full_charge_kernel,
        },
    }


def integrate_L00(
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
    L00 = float(result["point_nucleus_contractions"]["I00"])
    if not math.isfinite(L00) or L00 <= 0.0:
        raise ValueError("invalid phase-space-integrated L00")
    return {
        "L00": L00,
        "qA_from_phase_space_GeV": float(result["qA_magnitude_GeV"]),
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
            medium = integrate_L00(ER_keV, delta_m, width, medium_order)
            high = integrate_L00(ER_keV, delta_m, width, high_order)
            convergence = abs(high["L00"] - medium["L00"]) / abs(high["L00"])
            if convergence > 1.0e-3:
                raise RuntimeError(
                    f"L00 medium/high convergence failed: ER={ER_keV}, "
                    f"width={width}, rel={convergence:.6g}"
                )
            kernels = charge_sector_kernels(high["L00"], qA, high_response)
            linear_kernels = charge_sector_kernels(high["L00"], qA, linear_response)
            width_rows.append({
                "width_scheme": width,
                "g2": G2,
                "delta_m_keV": delta_m * 1.0e6,
                "speed_kms": SPEED_KM_S,
                "phase_space": {
                    "medium": medium,
                    "high": high,
                    "L00_medium_high_relative_difference": convergence,
                },
                "nuclear_kinematics": {
                    "mA_GeV": MA_XE131_GEV,
                    "ER_keV": ER_keV,
                    "qA_exact_GeV": qA,
                    "tN_GeV2_static": -(qA * qA),
                },
                "native_AFH_responses_pchip": high_response,
                "native_AFH_responses_linear_check": linear_response,
                "finite_tN_form_factors_and_charge_kernels": kernels,
                "linear_interpolation_cross_section_ratio": (
                    linear_kernels["full_charge_over_pointlike_M"]
                ),
                "pchip_minus_linear_ratio": (
                    kernels["full_charge_over_pointlike_M"]
                    - linear_kernels["full_charge_over_pointlike_M"]
                ),
            })
        ratios = [
            row["finite_tN_form_factors_and_charge_kernels"]["full_charge_over_pointlike_M"]
            for row in width_rows
        ]
        if max(ratios) - min(ratios) > 2.0e-13:
            raise AssertionError(
                "charge-sector ratio should be independent of pole/running width "
                "because the common integrated L00 cancels"
            )
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
                    "full_charge_over_pointlike_M"
                ]
            ),
            "relative_change_percent": (
                width_rows[0]["finite_tN_form_factors_and_charge_kernels"][
                    "relative_change_percent"
                ]
            ),
            "width_scenarios": width_rows,
            "width_independence_check": {
                "ratio_max_minus_min": max(ratios) - min(ratios),
                "interpretation": "finite widths change the absolute dSigma/dER, but cancel in this factorized charge-sector ratio",
            },
        })
    return {
        "status": "PASS_XE131_FIXED_SPEED_CHARGE_SECTOR_RATIO",
        "scope": (
            "fixed-speed Xe-131 differential cross-section ratio in the "
            "M+Phi''+M-Phi'' charge-density sector; the complete 2->3 DM "
            "phase space is integrated with both scalar-radiation diagrams "
            "and finite chi2 widths, while native AFH spatial-current "
            "responses are not included"
        ),
        "ratio_definition": (
            "(dSigma/dER)_[finite-tN M+Phi'' charge sector] / "
            "(dSigma/dER)_[original pointlike 9 W_M-only]"
        ),
        "factorization": (
            "The same integrated L00^(3), propagator, flux, and phase-space "
            "prefactor multiply numerator and denominator and cancel in the ratio."
        ),
        "DM_benchmark": {
            "mchi1_GeV": MCHI_GEV,
            "ms_keV": MS_GEV * 1.0e6,
            "speed_kms": SPEED_KM_S,
            "g2": G2,
            "width_schemes": list(WIDTH_SCHEMES),
        },
        "nuclear_input": {
            "target": "Xe-131",
            "mA_bare_nucleus_GeV": MA_XE131_GEV,
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
            "This is not the complete L_mu_nu W_A^mu_nu result because native Delta/Sigma responses are not included.",
            "The spatial-current sector was previously found negligible in provisional fixed-speed contractions, but that does not replace native spatial-response validation.",
            "The finite-Q2 form-factor prescription remains diagnostic, especially F2^V(Q2).",
            "No halo velocity average, isotope sum, detector response, or absolute coupling normalization is included.",
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
