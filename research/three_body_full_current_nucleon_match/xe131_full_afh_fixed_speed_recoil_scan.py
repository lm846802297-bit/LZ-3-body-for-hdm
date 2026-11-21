#!/usr/bin/env python3
"""Xe-131 fixed-speed A/B/C/D recoil scan with the leading-static six-channel AFH current.

A is the q=0 effective-nucleon-current reference; B is the adopted
finite-t_N M-only baseline; C adds the matched Phi'' charge terms; D adds
the provisional Delta/Sigma'/Sigma'-Delta spatial candidate. The native
AFH M/Phi''/M-Phi'' responses are combined with source-translated P3-B
spatial OBDME responses. The spatial sector remains provisional until
native-Wolfram and P3-C amplitude-level gates pass.
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

import afh_spatial_obdme_responses as spatial
from nucleon_vector_form_factors import (
    bishara_linear, charge_coefficients,
    effective_nucleon_form_factors,
)
from three_body_multipole_leptonic_weights import (
    DEFAULT_MN_GEV,
    complex_from_pairs,
    extract_afh_vector_coefficients,
)
from three_body_phase_space_tensor import eq6, integrate_spin_resolved_tensor
from xe131_fixed_speed_charge_dsigma import (
    MA_XE131_GEV,
    load_native_xe131_responses,
)

MCHI_GEV = 1000.0
MS_GEV = 300.0e-6
SPEED_KM_S = 776.0
G2 = 1.0
FORMAL_WIDTH_SCHEMES = ("pole",)
EXPECTED_CHARGE_RATIOS = {
    ("off_pole_dm450", 200.0): 0.7376302304925361,
    ("near_pole_dm362", 267.0): 0.6056496631467666,
}
RESPONSE_NAMES = ("M", "PhiPP", "MPhiPP", "Delta", "SigmaPrime", "SigmaPrimeDelta")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write an empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def recoil_cases() -> tuple[dict, ...]:
    near_grid = np.unique(np.concatenate((
        np.linspace(200.0, 260.0, 13),
        np.linspace(260.0, 274.5, 30),
        np.asarray([267.0]),
    )))
    return (
        {
            "name": "off_pole_dm450",
            "delta_m_GeV": 450.0e-6,
            "mapping": "threshold_u2",
            "orders": (32, 24, 12),
            "energies_keV": np.arange(130.0, 400.0 + 0.1, 10.0),
        },
        {
            "name": "near_pole_dm362",
            "delta_m_GeV": 362.0e-6,
            "mapping": "sine2",
            "orders": (48, 32, 16),
            "energies_keV": near_grid,
        },
    )


def load_response_interpolators(native_charge_csv: Path) -> tuple[dict, dict]:
    """Build one consistently normalized Xe-131 six-response grid on q=0..0.6 GeV."""
    native, native_provenance = load_native_xe131_responses(native_charge_csv)

    input_metadata = json.loads(spatial.META_PATH.read_text(encoding="utf-8"))
    isotope = next(item for item in input_metadata["isotopes"] if int(item["A"]) == 131)
    J_A = float(isotope["J_A"])
    T_iso = float(isotope["T_iso"])
    b_GeV_inv = float(isotope["b_A_GeV_inverse"])
    density_path = spatial.MATRIX_ROOT / "afh_default_xe131_density_matrix.csv"
    density_rows = spatial.read_density_matrix(density_path)

    # The common finite-decimal OBDME correction is calibrated only by M(q=0)=A^2.
    c0_anchor = spatial.isotope_spatial_response(
        0.0, 131, density_rows, J_A, T_iso, b_GeV_inv
    )
    C0_spatial = float(c0_anchor["common_matrix_normalization"])
    C0_native = float(native_provenance["common_matrix_normalization_C0"])
    if not math.isclose(C0_native, C0_spatial, rel_tol=0.0, abs_tol=2.0e-12):
        raise ValueError(
            "native charge and P3-B spatial OBDME C0 normalizations disagree: "
            f"native={C0_native:.16g}, spatial={C0_spatial:.16g}"
        )
    C0 = C0_spatial
    q_grid = np.asarray(native["q"], dtype=float)

    # load_native_xe131_responses already applies C0 to the three native
    # physical equal-p/n charge channels. Do not multiply them a second time.
    charge = {
        name: np.asarray(native["responses"][name], dtype=float)
        for name in ("M", "PhiPP", "MPhiPP")
    }
    spatial_rows = [
        spatial.isotope_spatial_response(
            float(q), 131, density_rows, J_A, T_iso, b_GeV_inv,
            common_matrix_normalization=C0,
        )
        for q in q_grid
    ]
    spatial_values = {
        "Delta": np.asarray([row["R_Delta_equal_pn"] for row in spatial_rows]),
        "SigmaPrime": np.asarray([row["R_SigmaPrime_equal_pn"] for row in spatial_rows]),
        "SigmaPrimeDelta": np.asarray([
            row["R_SigmaPrimeDelta_equal_pn"] for row in spatial_rows
        ]),
    }
    values = {**charge, **spatial_values}

    pchip = {
        name: PchipInterpolator(q_grid, array, extrapolate=False)
        for name, array in values.items()
    }
    linear = {
        name: array.copy()
        for name, array in values.items()
    }

    response_grid_rows = []
    max_c0 = 0.0
    for i, q in enumerate(q_grid):
        row = {
            "A": 131,
            "qA_GeV": float(q),
            "y": float((q * b_GeV_inv / 2.0) ** 2),
            "C0_common_OBDME_normalization": C0,
        }
        for name in RESPONSE_NAMES:
            row[f"W_{name}"] = float(values[name][i])
        wm = float(values["M"][i])
        wp = float(values["PhiPP"][i])
        wmp = float(values["MPhiPP"][i])
        wd = float(values["Delta"][i])
        ws = float(values["SigmaPrime"][i])
        wsd = float(values["SigmaPrimeDelta"][i])
        row["W_PhiPP_over_W_M"] = wp / wm if wm != 0.0 else None
        row["W_MPhiPP_over_W_M"] = wmp / wm if wm != 0.0 else None
        row["W_SigmaPrime_over_W_Delta"] = ws / wd if wd != 0.0 else None
        row["W_SigmaPrimeDelta_over_sqrt_WDeltaWSigmaPrime"] = (
            wsd / math.sqrt(wd * ws) if wd > 0.0 and ws > 0.0 else None
        )
        response_grid_rows.append(row)
        max_c0 = max(max_c0, abs(C0 - 1.0))

    metadata = {
        "native_charge_response": native_provenance,
        "spatial_response_status": "PROVISIONAL_SOURCE_TRANSLATED_AFH_SPATIAL_RESPONSES",
        "spatial_native_mathematica_crosscheck": False,
        "AFH_source_sha256": input_metadata["source_file_sha256"],
        "Xe131_density_matrix_sha256": spatial.sha256_file(density_path),
        "isotope": 131,
        "J_A": J_A,
        "T_iso": T_iso,
        "b_A_GeV_inverse": b_GeV_inv,
        "C0": C0,
        "normalization": (
            "factor four is included once by the native AFH charge export; "
            "one common C0 is applied once to charge and spatial channels"
        ),
        "q_grid_points": len(q_grid),
        "q_grid_min_GeV": float(q_grid[0]),
        "q_grid_max_GeV": float(q_grid[-1]),
        "q_grid_step_GeV": float(q_grid[1] - q_grid[0]),
        "max_abs_C0_minus_one": max_c0,
        "interpolation": "PCHIP for all six response channels; linear interpolation retained as diagnostic",
    }
    return {
        "q": q_grid,
        "values": values,
        "pchip": pchip,
        "linear": linear,
        "metadata": metadata,
        "response_grid_rows": response_grid_rows,
    }


def responses_at(bundle: dict, qA_GeV: float) -> tuple[dict, dict]:
    q = bundle["q"]
    if qA_GeV < q[0] or qA_GeV > q[-1]:
        raise ValueError(f"q_A={qA_GeV:.12g} GeV lies outside the AFH response grid")
    values = {name: float(bundle["pchip"][name](qA_GeV)) for name in RESPONSE_NAMES}
    linear = {
        name: float(np.interp(qA_GeV, q, bundle["values"][name]))
        for name in RESPONSE_NAMES
    }
    interpolation = {
        name: abs(values[name] - linear[name]) /
        max(abs(values[name]), abs(linear[name]), 1.0e-300)
        for name in RESPONSE_NAMES
    }
    if values["M"] < -1.0e-12 or values["PhiPP"] < -1.0e-12:
        raise ArithmeticError("negative diagonal charge response")
    if values["Delta"] < -1.0e-12 or values["SigmaPrime"] < -1.0e-12:
        raise ArithmeticError("negative diagonal spatial response")
    charge_bound = math.sqrt(max(0.0, values["M"]) * max(0.0, values["PhiPP"]))
    spatial_bound = math.sqrt(
        max(0.0, values["Delta"]) * max(0.0, values["SigmaPrime"])
    )
    if abs(values["MPhiPP"]) > charge_bound + 2.0e-10 * max(charge_bound, 1.0e-300):
        raise ArithmeticError("M-Phi'' response violates Cauchy-Schwarz")
    if abs(values["SigmaPrimeDelta"]) > spatial_bound + 2.0e-10 * max(spatial_bound, 1.0e-300):
        raise ArithmeticError("Sigma'-Delta response violates Cauchy-Schwarz")
    return values, interpolation


def contract_six_channels(
    L: np.ndarray,
    qA_GeV: float,
    ER_GeV: float,
    responses: dict,
    F1: float,
    F2: float,
) -> dict:
    coefficients = extract_afh_vector_coefficients(
        L, qA_GeV, f1=F1, f2=F2,
        mN_GeV=DEFAULT_MN_GEV, omega_GeV=ER_GeV,
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
    }
    charge = float(sum(charge_terms.values()))
    spatial = float(sum(spatial_terms.values()))
    full = charge + spatial
    LC = float(coefficients["L_C_continuity_adjusted_charge_weight"])
    A_reference = LC * responses["M"]
    B_baseline = coefficients["C_M"] * responses["M"]
    if min(A_reference, B_baseline, charge, full) <= 0.0:
        raise ArithmeticError(
            "non-positive A/B/C/D comparison kernel: "
            f"A={A_reference}, B={B_baseline}, C={charge}, D={full}"
        )
    if spatial < -2.0e-10 * max(abs(charge), 1.0e-300):
        raise ArithmeticError(f"negative combined spatial kernel: {spatial}")

    return {
        "coefficients": coefficients,
        "charge_terms": charge_terms,
        "spatial_terms": spatial_terms,
        "A_reference_M": A_reference,
        "B_finite_tN_M": B_baseline,
        "C_charge_only": charge,
        "spatial_candidate": spatial,
        "D_full_six_channel_candidate": full,
        "B_over_A_reference": B_baseline / A_reference,
        "C_over_B_baseline": charge / B_baseline,
        "C_over_A_reference": charge / A_reference,
        "D_over_C_charge_only": full / charge,
        "spatial_over_C_charge_only": spatial / charge,
        "D_over_A_reference": full / A_reference,
        "PhiPP_over_B_correction": charge / B_baseline - 1.0,
    }


def integrate_point(
    case: dict,
    ER_keV: float,
    width_scheme: str,
    orders: tuple[int, int, int],
    response_bundle: dict,
) -> dict:
    ER_GeV = ER_keV * 1.0e-6
    delta_m = float(case["delta_m_GeV"])
    wmin, wmax = eq6.limits(
        MCHI_GEV, MS_GEV, MA_XE131_GEV, ER_GeV, SPEED_KM_S
    )
    if wmax <= wmin:
        return {
            "benchmark": case["name"], "delta_m_keV": delta_m * 1.0e6,
            "ER_keV": ER_keV, "width_scheme": width_scheme,
            "status": "closed_phase_space",
        }
    pole_clearance_keV = (
        MCHI_GEV + delta_m - math.sqrt(wmax)
    ) * 1.0e6
    if pole_clearance_keV <= 0.0:
        return {
            "benchmark": case["name"], "delta_m_keV": delta_m * 1.0e6,
            "ER_keV": ER_keV, "width_scheme": width_scheme,
            "pole_clearance_keV": pole_clearance_keV,
            "status": "on_shell_chi2_accessible_not_in_offshell_scan",
        }

    result = integrate_spin_resolved_tensor(
        mchi=MCHI_GEV,
        ms=MS_GEV,
        delta_m=delta_m,
        mA=MA_XE131_GEV,
        ER=ER_GeV,
        speed_kms=SPEED_KM_S,
        g2=G2,
        width_scheme=width_scheme,
        mapping=case["mapping"],
        nw=orders[0], nz=orders[1], nphi=orders[2],
        crosscheck_dirac_trace=False,
    )
    if not result.get("phase_space_open", False):
        raise RuntimeError(f"phase-space status changed during ER={ER_keV} keV integration")
    qA = math.sqrt(2.0 * MA_XE131_GEV * ER_GeV + ER_GeV * ER_GeV)
    if not math.isclose(float(result["qA_magnitude_GeV"]), qA, rel_tol=0.0, abs_tol=2.0e-12):
        raise ArithmeticError("phase-space tensor q_A does not match exact Xe-131 mass-shell momentum")
    L = complex_from_pairs(np.asarray(result["L_q_aligned_real_imag"], dtype=float))
    responses, interpolation = responses_at(response_bundle, qA)
    tN_GeV2 = ER_GeV * ER_GeV - qA * qA
    F1_raw, F2_raw = bishara_linear(-tN_GeV2)
    F1, F2 = effective_nucleon_form_factors(F1_raw, F2_raw)
    contracted = contract_six_channels(L, qA, ER_GeV, responses, F1, F2)
    coeff = contracted["coefficients"]
    cM, cPhiPP = charge_coefficients(
        qA, F1=F1, F2=F2, tN_GeV2=tN_GeV2, mN_GeV=DEFAULT_MN_GEV
    )
    return {
        "benchmark": case["name"],
        "delta_m_keV": delta_m * 1.0e6,
        "mchi1_GeV": MCHI_GEV,
        "ms_keV": MS_GEV * 1.0e6,
        "speed_km_s": SPEED_KM_S,
        "g2": G2,
        "ER_keV": ER_keV,
        "qA_GeV": qA,
        "pole_clearance_keV": pole_clearance_keV,
        "Gamma_pole_keV": float(result["Gamma_pole_keV"]),
        "width_scheme": width_scheme,
        "mapping": case["mapping"],
        "nw": orders[0], "nz": orders[1], "nphi": orders[2],
        "quadrature_points": int(result["quadrature_points"]),
        "L_C": float(coeff["L_C_continuity_adjusted_charge_weight"]),
        "L_T": float(np.real(L[1, 1] + L[2, 2])),
        "F1V_quark_sum": F1_raw,
        "F2V_quark_sum": F2_raw,
        "F1N_effective": F1,
        "F2N_effective": F2,
        "tN_GeV2": tN_GeV2,
        "cM": float(cM),
        "cPhiPP": float(cPhiPP),
        "eta_cPhi_over_cM": float(cPhiPP / cM),
        **{f"W_{name}": float(responses[name]) for name in RESPONSE_NAMES},
        **{f"pchip_linear_rel_{name}": float(interpolation[name]) for name in RESPONSE_NAMES},
        **{f"kernel_charge_{name}": float(value) for name, value in contracted["charge_terms"].items()},
        **{f"kernel_spatial_{name}": float(value) for name, value in contracted["spatial_terms"].items()},
        "kernel_A_reference_M": float(contracted["A_reference_M"]),
        "kernel_B_finite_tN_M": float(contracted["B_finite_tN_M"]),
        "kernel_C_charge_only": float(contracted["C_charge_only"]),
        "kernel_spatial_candidate": float(contracted["spatial_candidate"]),
        "kernel_D_full_six_channel_candidate": float(contracted["D_full_six_channel_candidate"]),
        "B_over_A_reference": float(contracted["B_over_A_reference"]),
        "C_over_B_baseline": float(contracted["C_over_B_baseline"]),
        "C_over_A_reference": float(contracted["C_over_A_reference"]),
        "PhiPP_relative_to_B": float(contracted["PhiPP_over_B_correction"]),
        "D_over_C_charge_only": float(contracted["D_over_C_charge_only"]),
        "spatial_over_C_charge_only": float(contracted["spatial_over_C_charge_only"]),
        "D_over_A_reference": float(contracted["D_over_A_reference"]),
        "status": "PROVISIONAL_SIX_CHANNEL_FIXED_SPEED_POINT",
    }


def run(native_charge_csv: Path, outdir: Path) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    response_bundle = load_response_interpolators(native_charge_csv)
    rows = []
    for case in recoil_cases():
        for ER_keV in case["energies_keV"]:
            for width_scheme in FORMAL_WIDTH_SCHEMES:
                orders = tuple(case["orders"])
                if case["name"] == "off_pole_dm450" and math.isclose(float(ER_keV), 200.0):
                    orders = (40, 32, 16)
                if case["name"] == "near_pole_dm362" and math.isclose(float(ER_keV), 267.0):
                    orders = (48, 32, 16)
                rows.append(integrate_point(
                    case, float(ER_keV), width_scheme, orders, response_bundle
                ))

    accepted = [row for row in rows if row["status"] == "PROVISIONAL_SIX_CHANNEL_FIXED_SPEED_POINT"]
    if not accepted:
        raise RuntimeError("no open off-shell recoil points were integrated")

    anchor_checks = []
    for (case_name, ER_keV), expected in EXPECTED_CHARGE_RATIOS.items():
        match = [
            row for row in accepted
            if row["benchmark"] == case_name
            and math.isclose(float(row["ER_keV"]), ER_keV)
            and row["width_scheme"] == "pole"
        ]
        if len(match) != 1:
            raise RuntimeError(f"missing unique anchor point {(case_name, ER_keV)}")
        actual = float(match[0]["C_over_A_reference"])
        residual = abs(actual - expected)
        anchor_checks.append({
            "benchmark": case_name, "ER_keV": ER_keV,
            "expected_previous_charge_ratio": expected,
            "recomputed_charge_ratio": actual,
            "absolute_residual": residual,
            "status": "PASS" if residual < 2.0e-8 else "FAIL",
        })
        if residual >= 2.0e-8:
            raise AssertionError(
                f"charge-only anchor mismatch at {case_name}, ER={ER_keV}: {residual}"
            )

    max_spatial_fraction = max(abs(float(row["spatial_over_C_charge_only"])) for row in accepted)
    max_interp = max(
        float(row[f"pchip_linear_rel_{name}"])
        for row in accepted for name in RESPONSE_NAMES
    )
    summary = {
        "status": "PASS_XE131_FIXED_SPEED_SIX_CHANNEL_DIAGNOSTIC",
        "scope": (
            "fixed-speed Xe-131 differential-kernel comparison; native AFH M/Phi''/M-Phi'' "
            "responses plus source-translated P3-B Delta/Sigma'/Sigma'-Delta responses; "
            "leading-static one-body vector-current candidate only"
        ),
        "benchmark_parameters": {
            "mchi1_GeV": MCHI_GEV, "ms_keV": MS_GEV * 1.0e6,
            "speed_km_s": SPEED_KM_S, "g2": G2,
            "mA_bare_nucleus_GeV": MA_XE131_GEV,
            "form_factor_prescription": "adopted B: Bishara-linear raw u+d+s F1 slope and constant F2 anchor, divided by three for the external-gVN basis",
            "nucleon_transfer_convention": "q_N^mu=q_A^mu; t_N=t_A=omega^2-Q_A^2=-2*m_A*E_R",
        },
        "fixed_benchmarks": [
            {
                "name": "off_pole_dm450",
                "delta_m_keV": 450.0,
                "ER_grid_keV": [130.0, 400.0, 10.0],
                "mapping": "threshold_u2",
            },
            {
                "name": "near_pole_dm362",
                "delta_m_keV": 362.0,
                "ER_grid_keV": "13 points from 200 to 260 keV at 5 keV spacing plus 30 points from 260 to 274.5 keV and the exact 267 keV anchor",
                "mapping": "sine2",
            },
        ],
        "width_schemes": list(FORMAL_WIDTH_SCHEMES),
        "formal_width_prescription": "Eq. (19) asymmetric: first p-k propagator remains zero-width (+i0+); second p'+k propagator uses the constant pole width evaluated at m_chi2. Running width is not a production input.",
        "response_metadata": response_bundle["metadata"],
        "anchor_checks_against_previous_finite_tN_charge_only": anchor_checks,
        "accepted_recoil_rows": len(accepted),
        "all_rows_including_closed_or_on_shell": len(rows),
        "maximum_absolute_spatial_over_charge_candidate": max_spatial_fraction,
        "maximum_PCHIP_vs_linear_response_difference": max_interp,
        "spatial_phase_status": (
            "P3-A particle-side/frame checks passed; P3-B spatial responses are "
            "independently Python-cross-checked but not native-Wolfram validated; "
            "P3-C bound-nucleus covariant-versus-AFH contraction remains open"
        ),
        "limitations": [
            "B uses the adopted low-momentum Bishara F1 slope and constant F2 anchor; no unsupported F2 slope is assumed.",
            "Spatial Delta/Sigma'/Sigma'-Delta nuclear responses are source-translated Python AFH data, not native-Wolfram validated.",
            "The signed Sigma'-Delta particle-side phase remains a candidate pending P3-C amplitude-level validation.",
            "The one-body impulse matching uses q_N^mu=q_A^mu; bound-nucleon off-shell and interaction-current effects are not included.",
            "This is fixed-speed and isotope-specific; no halo average, natural-xenon isotope sum, detector response, or absolute event rate is included.",
            "The common mediator, flux, and coupling prefactors cancel in the reported response ratios.",
        ],
        "results": rows,
    }

    response_path = outdir / "xe131_six_response_grid.csv"
    results_path = outdir / "xe131_six_channel_fixed_speed_recoil_scan.csv"
    summary_path = outdir / "xe131_six_channel_fixed_speed_recoil_scan.json"
    write_csv(response_path, response_bundle["response_grid_rows"])
    write_csv(results_path, rows)
    summary_path.write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    manifest_path = outdir / "SHA256SUMS.txt"
    manifest_path.write_text(
        f"{sha256(response_path)}  {response_path.name}\n"
        f"{sha256(results_path)}  {results_path.name}\n"
        f"{sha256(summary_path)}  {summary_path.name}\n",
        encoding="ascii",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-charge-csv", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.native_charge_csv, args.outdir)
    print(json.dumps({
        "status": result["status"],
        "accepted_recoil_rows": result["accepted_recoil_rows"],
        "all_rows": result["all_rows_including_closed_or_on_shell"],
        "max_abs_spatial_over_charge_candidate": result["maximum_absolute_spatial_over_charge_candidate"],
        "max_pchip_linear_difference": result["maximum_PCHIP_vs_linear_response_difference"],
        "anchor_checks": result["anchor_checks_against_previous_finite_tN_charge_only"],
        "output": str(args.outdir),
    }, indent=2))


if __name__ == "__main__":
    main()
