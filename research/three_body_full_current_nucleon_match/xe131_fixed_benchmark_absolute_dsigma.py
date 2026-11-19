#!/usr/bin/env python3
"""Absolute fixed-benchmark Xe-131 d sigma/dER in the AFH charge sector.

The complete three-body DM phase space is integrated pointwise at fixed
Delta m=450 keV with the formal asymmetric Eq. (19) prescription: the first
p-k propagator is zero-width (+i0+), while the second p'+k propagator carries
the constant pole width evaluated at m_chi2. Public flux, mediator, coupling
and target-mass prefactors are restored after the coherent native-AFH charge
contraction. Transverse nuclear multipoles are not included.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CALC_DIR = ROOT / "research" / "three_body_calculation_and_validation"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(CALC_DIR) not in sys.path:
    sys.path.insert(0, str(CALC_DIR))
import eq6_kernel  # noqa: E402
from nucleon_vector_form_factors import (
    DEFAULT_FORM_FACTOR_PRESCRIPTION,
    charge_coefficients,
    effective_nucleon_form_factors,
    bishara_linear,
    isoscalar_zexp,
)
from three_body_phase_space_tensor import eq6, integrate_spin_resolved_tensor
from xe131_fixed_speed_charge_dsigma import (
    G2, MA_XE131_GEV, MCHI_GEV, MN_GEV, MS_GEV, MV_GEV, SPEED_KM_S,
    XE131_MASS_RECORD, exact_qA_GeV, load_native_xe131_responses,
    interpolate_responses,
)

DELTA_M_GEV = 450.0e-6
COUPLING_PRODUCT_SQUARED = 1.0
WIDTH_SCHEME = "pole"
MAPPING = "threshold_u2"
CURVE_ORDER = (20, 16, 12)
HIGH_ORDER = (40, 32, 16)
LEGACY_ORDER = (48, 32, 16)
GEV_MINUS3_TO_CM2_PER_KEV = 3.893793721e-34

def incident_momentum_GeV(mchi_GeV: float, speed_km_s: float) -> float:
    beta = speed_km_s / eq6.C_KM_S
    if not 0.0 < beta < 1.0:
        raise ValueError("incident speed must lie between zero and c")
    return mchi_GeV * beta / math.sqrt(1.0 - beta * beta)

def kinematic_prefactor_GeVminus5(
    ER_keV: float, *, mA_GeV: float = MA_XE131_GEV,
    mchi_GeV: float = MCHI_GEV, speed_km_s: float = SPEED_KM_S,
    mV_GeV: float = MV_GEV,
    coupling_product_squared: float = COUPLING_PRODUCT_SQUARED,
) -> dict:
    qA = exact_qA_GeV(mA_GeV, ER_keV)
    pchi = incident_momentum_GeV(mchi_GeV, speed_km_s)
    ER_GeV = ER_keV * 1.0e-6
    Q_A_squared = qA * qA
    t_A = -2.0 * mA_GeV * ER_GeV
    # The propagator carries the invariant transfer t_A=q_A^2, not the
    # spatial three-momentum squared Q_A^2.
    minus_t_A = -t_A
    denominator = (mV_GeV * mV_GeV - t_A) ** 2
    prefactor = mA_GeV * coupling_product_squared / (
        256.0 * math.pi**3 * pchi * pchi * denominator
    )
    return {
        "qA_GeV": qA,
        "Q_A_squared_GeV2": Q_A_squared,
        "t_A_GeV2": t_A,
        "minus_t_A_GeV2": minus_t_A,
        "pchi_GeV": pchi,
        "mediator_denominator_GeV4": denominator,
        "public_prefactor_GeVminus5": prefactor,
    }

def phase_space_integral(ER_keV: float, order: tuple[int, int, int]) -> dict:
    nw, nz, nphi = order
    result = integrate_spin_resolved_tensor(
        mchi=MCHI_GEV, ms=MS_GEV, delta_m=DELTA_M_GEV,
        mA=MA_XE131_GEV, ER=ER_keV * 1.0e-6,
        speed_kms=SPEED_KM_S, g2=G2, width_scheme=WIDTH_SCHEME,
        mapping=MAPPING, nw=nw, nz=nz, nphi=nphi,
        crosscheck_dirac_trace=False,
    )
    if not result.get("phase_space_open", False):
        wmax = eq6.limits(MCHI_GEV, MS_GEV, MA_XE131_GEV,
                          ER_keV * 1.0e-6, SPEED_KM_S)[1]
        return {
            "phase_space_open": False, "L00_GeV2": 0.0, "L_C_GeV2": 0.0,
            "pole_clearance_keV": (MCHI_GEV + DELTA_M_GEV - math.sqrt(wmax))*1.0e6,
            "Gamma_pole_keV": eq6.chi2_width_dirac_scalar(
                MCHI_GEV, MS_GEV, DELTA_M_GEV, G2
            ) * 1.0e6,
            "quadrature_points": 0,
        }
    contractions = result["point_nucleus_contractions"]
    q_expected = exact_qA_GeV(MA_XE131_GEV, ER_keV)
    if not math.isclose(float(result["qA_magnitude_GeV"]), q_expected,
                        rel_tol=0.0, abs_tol=2.0e-12):
        raise ArithmeticError("phase-space q_A does not match exact nuclear mass shell")
    L00 = float(contractions["I00"])
    LC = float(contractions["L_C_continuity_adjusted"])
    residual = float(contractions["continuity_reduced_relative_residual"])
    if L00 <= 0.0 or LC <= 0.0 or not math.isfinite(LC):
        raise ArithmeticError(f"non-positive phase-space integral at ER={ER_keV}")
    if residual > 5.0e-12:
        raise ArithmeticError(f"point-nucleus continuity identity failed: {residual}")
    return {
        "phase_space_open": True, "L00_GeV2": L00, "L_C_GeV2": LC,
        "L_C_over_L00_minus_one": LC / L00 - 1.0,
        "pole_clearance_keV": float(result["pole_clearance_keV"]),
        "Gamma_pole_keV": float(result["Gamma_pole_keV"]),
        "quadrature_points": int(result["quadrature_points"]),
    }

def nuclear_charge_kernels(
    ER_keV: float,
    LC: float,
    responses: dict[str, float],
    form_factor_prescription: str = DEFAULT_FORM_FACTOR_PRESCRIPTION,
) -> dict:
    """Return A reference, B primary baseline, and C charge-response extension."""
    qA = exact_qA_GeV(MA_XE131_GEV, ER_keV)
    ER_GeV = ER_keV * 1.0e-6
    tN_GeV2 = ER_GeV * ER_GeV - qA * qA
    QN2_GeV2 = -tN_GeV2
    if form_factor_prescription == "bishara_linear":
        F1_quark, F2_quark = bishara_linear(QN2_GeV2)
    elif form_factor_prescription == "isoscalar_zexp":
        F1_quark, F2_quark = isoscalar_zexp(QN2_GeV2)
    else:
        raise ValueError(f"unknown form-factor prescription: {form_factor_prescription}")
    F1_effective, F2_effective = effective_nucleon_form_factors(
        F1_quark, F2_quark
    )
    cM, cPhi = charge_coefficients(
        qA, F1=F1_effective, F2=F2_effective, mN_GeV=MN_GEV,
        tN_GeV2=tN_GeV2,
    )
    WM, WPhi, WMPhi = (
        float(responses["M"]), float(responses["PhiPP"]), float(responses["MPhiPP"])
    )
    if WM <= 0.0 or WPhi < -1.0e-12:
        raise ArithmeticError("invalid diagonal AFH charge response")
    A_reference = LC * WM
    B_baseline = cM**2 * LC * WM
    C_terms = {
        "B_M_only": B_baseline,
        "M_Phi_interference": 2.0 * cM * cPhi * LC * WMPhi,
        "PhiPP_diagonal": cPhi**2 * LC * WPhi,
    }
    C_extension = sum(C_terms.values())
    if min(A_reference, B_baseline, C_extension) <= 0.0:
        raise ArithmeticError("non-positive A/B/C charge kernel")
    return {
        "form_factor_prescription": form_factor_prescription,
        "F1V_quark": F1_quark, "F2V_quark": F2_quark,
        "F1N_effective": F1_effective, "F2N_effective": F2_effective,
        "tN_GeV2": tN_GeV2, "Q_N2_GeV2": QN2_GeV2,
        "nucleon_transfer_scheme": "strict one-body impulse q_N^mu=q_A^mu",
        "cM_effective": cM, "cPhiPP_effective": cPhi,
        "A_original_AFH_M_reference": A_reference,
        "B_baseline_M_only": B_baseline,
        "C_charge_extension": C_extension,
        "M_Phi_interference": C_terms["M_Phi_interference"],
        "PhiPP_diagonal": C_terms["PhiPP_diagonal"],
        "B_over_A": B_baseline / A_reference,
        "C_over_A": C_extension / A_reference,
        "C_over_B": C_extension / B_baseline,
    }


def make_recoil_grid(ER_min: float, ER_max: float) -> np.ndarray:
    coarse = np.arange(math.ceil(ER_min), math.floor(ER_max) + 1.0e-9, 2.0)
    dip_one = np.arange(265.0, 273.0001, 0.5)
    dip_two = np.arange(542.0, 550.0001, 0.5)
    values = np.concatenate((np.asarray([ER_min, ER_max, 200.0, 267.0]),
                             coarse, dip_one, dip_two))
    values = np.unique(values)
    return values[(values >= ER_min) & (values <= ER_max)]

def find_open_interval() -> tuple[float, float]:
    threshold = (MCHI_GEV + MS_GEV) ** 2
    def margin(ER_keV: float) -> float:
        wmin, wmax = eq6.limits(MCHI_GEV, MS_GEV, MA_XE131_GEV,
                                ER_keV * 1.0e-6, SPEED_KM_S)
        return wmax - threshold
    return (
        brentq(margin, 0.0, 250.0, xtol=1.0e-12),
        brentq(margin, 500.0, 900.0, xtol=1.0e-12),
    )

def calculate_row(
    ER_keV: float,
    response_bundle: dict,
    order: tuple[int, int, int] = CURVE_ORDER,
    form_factor_prescription: str = DEFAULT_FORM_FACTOR_PRESCRIPTION,
) -> dict:
    qA = exact_qA_GeV(MA_XE131_GEV, ER_keV)
    responses = interpolate_responses(response_bundle, qA)["pchip"]
    phase = phase_space_integral(ER_keV, order)
    kin = kinematic_prefactor_GeVminus5(ER_keV)
    base = {
        "ER_keV": ER_keV, "qA_GeV": qA,
        "W_M": responses["M"], "W_PhiPP": responses["PhiPP"],
        "W_MPhiPP": responses["MPhiPP"],
        "L00_GeV2": phase["L00_GeV2"], "L_C_GeV2": phase["L_C_GeV2"],
        "pole_clearance_keV": phase["pole_clearance_keV"],
        "Gamma_pole_keV": phase["Gamma_pole_keV"],
        "quadrature_points": phase["quadrature_points"],
        "nw": order[0], "nz": order[1], "nphi": order[2],
        "pchi_GeV": kin["pchi_GeV"],
        "Q_A_squared_GeV2": kin["Q_A_squared_GeV2"],
        "t_A_GeV2": kin["t_A_GeV2"],
        "minus_t_A_GeV2": kin["minus_t_A_GeV2"],
        "mediator_denominator_GeV4": kin["mediator_denominator_GeV4"],
        "public_prefactor_GeVminus5": kin["public_prefactor_GeVminus5"],
        "phase_space_open": bool(phase["phase_space_open"]),
    }
    if not phase["phase_space_open"]:
        return {
            **base,
            "A_original_AFH_M_reference_GeVminus3": 0.0,
            "B_baseline_M_only_GeVminus3": 0.0,
            "C_charge_extension_GeVminus3": 0.0,
            "A_original_AFH_M_reference_cm2_per_keV": 0.0,
            "B_baseline_M_only_cm2_per_keV": 0.0,
            "C_charge_extension_cm2_per_keV": 0.0,
            "C_over_A": 0.0,
            "C_over_B": 0.0,
        }
    kernels = nuclear_charge_kernels(
        ER_keV, phase["L_C_GeV2"], responses, form_factor_prescription
    )
    prefactor = kin["public_prefactor_GeVminus5"]
    values = {
        "A_original_AFH_M_reference": prefactor * kernels["A_original_AFH_M_reference"],
        "B_baseline_M_only": prefactor * kernels["B_baseline_M_only"],
        "C_charge_extension": prefactor * kernels["C_charge_extension"],
        "M_Phi_interference": prefactor * kernels["M_Phi_interference"],
        "PhiPP_diagonal": prefactor * kernels["PhiPP_diagonal"],
    }
    return {
        **base,
        "form_factor_prescription": kernels["form_factor_prescription"],
        "F1V_quark": kernels["F1V_quark"],
        "F2V_quark": kernels["F2V_quark"],
        "F1N_effective": kernels["F1N_effective"],
        "F2N_effective": kernels["F2N_effective"],
        "tN_GeV2": kernels["tN_GeV2"],
        "Q_N2_GeV2": kernels["Q_N2_GeV2"],
        "nucleon_transfer_scheme": kernels["nucleon_transfer_scheme"],
        "cM_effective": kernels["cM_effective"],
        "cPhiPP_effective": kernels["cPhiPP_effective"],
        "L_C_over_L00_minus_one": phase["L_C_over_L00_minus_one"],
        "A_original_AFH_M_reference_kernel_GeV2": kernels["A_original_AFH_M_reference"],
        "B_baseline_M_only_kernel_GeV2": kernels["B_baseline_M_only"],
        "C_charge_extension_kernel_GeV2": kernels["C_charge_extension"],
        "M_Phi_interference_kernel_GeV2": kernels["M_Phi_interference"],
        "PhiPP_diagonal_kernel_GeV2": kernels["PhiPP_diagonal"],
        "A_original_AFH_M_reference_GeVminus3": values["A_original_AFH_M_reference"],
        "B_baseline_M_only_GeVminus3": values["B_baseline_M_only"],
        "C_charge_extension_GeVminus3": values["C_charge_extension"],
        "M_Phi_interference_GeVminus3": values["M_Phi_interference"],
        "PhiPP_diagonal_GeVminus3": values["PhiPP_diagonal"],
        "A_original_AFH_M_reference_cm2_per_keV": (
            values["A_original_AFH_M_reference"] * GEV_MINUS3_TO_CM2_PER_KEV
        ),
        "B_baseline_M_only_cm2_per_keV": (
            values["B_baseline_M_only"] * GEV_MINUS3_TO_CM2_PER_KEV
        ),
        "C_charge_extension_cm2_per_keV": (
            values["C_charge_extension"] * GEV_MINUS3_TO_CM2_PER_KEV
        ),
        "B_over_A": kernels["B_over_A"],
        "C_over_A": kernels["C_over_A"],
        "C_over_B": kernels["C_over_B"],
    }

def plot_absolute(rows: list[dict], outdir: Path) -> None:
    import matplotlib.pyplot as plt
    from paper_plot_style import apply_paper_style, save_paper_figure

    apply_paper_style()
    opened = [row for row in rows if row["phase_space_open"]]
    er = np.asarray([row["ER_keV"] for row in opened])
    fig, ax = plt.subplots(figsize=(6.8, 4.45))
    ax.semilogy(er, [r["A_original_AFH_M_reference_cm2_per_keV"] for r in opened],
                linestyle="--", label=r"A: finite-size AFH $W_M$")
    ax.semilogy(er, [r["B_baseline_M_only_cm2_per_keV"] for r in opened],
                linestyle="-.", linewidth=1.9,
                label=r"B: finite-$t_N$ nucleon current $\times W_M$")
    ax.semilogy(er, [r["C_charge_extension_cm2_per_keV"] for r in opened],
                linestyle="-", linewidth=1.6,
                label=r"C: $M+\Phi''$ charge-response extension")
    ax.axvline(200.0, color="0.45", linestyle="--", linewidth=0.85,
               label=r"$E_R=200~\mathrm{keV}$")
    ax.axvline(267.0, color="0.60", linestyle=":", linewidth=1.0,
               label=r"$E_R=267~\mathrm{keV}$")
    ax.set_xlim(float(er.min()), float(er.max()))
    ax.set_xlabel(r"Recoil energy, $E_R$ [keV]")
    ax.set_ylabel(r"$\mathrm{d}\sigma/\mathrm{d}E_R$ [cm$^2$ keV$^{-1}$]")
    ax.set_title(r"Xe-131 fixed-benchmark differential cross section")
    ax.legend(loc="best", ncol=1)
    ax.tick_params(which="both", direction="in", top=True, right=True)
    ax.text(0.985, 0.965,
            r"$m_{\chi_1}=1~\mathrm{TeV},\ \Delta m=450~\mathrm{keV}$" "\n"
            r"$m_s=300~\mathrm{keV},\ v=776~\mathrm{km\,s^{-1}}$",
            transform=ax.transAxes, ha="right", va="top", fontsize=8.0)
    fig.tight_layout(pad=0.6)
    save_paper_figure(fig, outdir / "xe131_fixed_benchmark_absolute_dsigma_450keV")

def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("refusing to write empty absolute dSigma/dER table")
    # Closed endpoint rows intentionally omit response/kernel quantities.
    # Build a stable union schema so mixed open/closed rows serialize safely.
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def run(
    afh_csv: Path,
    outdir: Path,
    form_factor_prescription: str = DEFAULT_FORM_FACTOR_PRESCRIPTION,
) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    response_bundle, provenance = load_native_xe131_responses(afh_csv)
    er_min, er_max = find_open_interval()
    energies = make_recoil_grid(er_min, er_max)
    rows = [
        calculate_row(float(ER), response_bundle, CURVE_ORDER, form_factor_prescription)
        for ER in energies
    ]
    if not rows or not any(row["phase_space_open"] for row in rows):
        raise RuntimeError("absolute fixed-benchmark curve contains no open recoil points")

    anchors = []
    for ER in (200.0, 267.0, 269.0, 546.0, 650.0):
        medium = min(rows, key=lambda row: abs(row["ER_keV"] - ER))
        high = calculate_row(ER, response_bundle, HIGH_ORDER, form_factor_prescription)
        if not high["phase_space_open"]:
            raise RuntimeError(f"high-order convergence anchor ER={ER} is closed")
        relative = abs(high["B_baseline_M_only_GeVminus3"] - medium["B_baseline_M_only_GeVminus3"]) / max(abs(high["B_baseline_M_only_GeVminus3"]), 1.0e-300)
        anchors.append({
            "ER_keV": ER, "medium_grid_nearest_ER_keV": medium["ER_keV"],
            "high_order": list(HIGH_ORDER), "medium_order": list(CURVE_ORDER),
            "high_B_baseline_M_only_GeVminus3": high["B_baseline_M_only_GeVminus3"],
            "medium_B_baseline_M_only_GeVminus3": medium["B_baseline_M_only_GeVminus3"],
            "relative_difference": relative,
        })
    max_anchor_difference = max(item["relative_difference"] for item in anchors)
    if max_anchor_difference > 1.0e-3:
        raise RuntimeError(f"medium/high absolute dSigma convergence failed: {max_anchor_difference:.6g}")

    legacy_checks = []
    for ER in (200.0, 267.0):
        # The legacy Eq. (6) implementation integrates W^2 linearly, while
        # the spin-resolved tensor uses the threshold_u2 map. Use a high
        # common order so the independent quadrature maps are both converged.
        new = phase_space_integral(ER, LEGACY_ORDER)
        old = eq6_kernel.reduced_kernel(
            MCHI_GEV, MS_GEV, DELTA_M_GEV, MA_XE131_GEV,
            ER * 1.0e-6, SPEED_KM_S,
            nw=LEGACY_ORDER[0], nz=LEGACY_ORDER[1],
            nphi=LEGACY_ORDER[2], width_scheme="pole", g2=G2,
        )
        residual = abs(new["L00_GeV2"] - old) / max(abs(old), 1.0e-300)
        legacy_checks.append({
            "ER_keV": ER, "spin_resolved_L00_GeV2": new["L00_GeV2"],
            "independent_Eq6_I6_GeV2": old, "relative_residual": residual,
        })
    max_legacy_residual = max(item["relative_residual"] for item in legacy_checks)
    if max_legacy_residual > 1.0e-5:
        raise RuntimeError(f"spin-resolved L00 does not reproduce high-order independent Eq. (6): {max_legacy_residual:.6g}")

    # The AFH/nucleon ratio is independent of the DM-side phase-space factor.
    # These anchors reproduce the previously validated fixed-speed ratio
    # calculation, although the full absolute curve keeps Delta m=450 keV
    # fixed at every recoil.
    expected_charge_ratios = {
        200.0: 0.737630,
        267.0: 0.605649,
    }
    ratio_checks = []
    for ER, expected in expected_charge_ratios.items():
        row = min(rows, key=lambda item: abs(item["ER_keV"] - ER))
        residual = abs(row["C_over_A"] - expected)
        ratio_checks.append({
            "ER_keV": ER,
            "fixed_Delta_m_keV": DELTA_M_GEV * 1.0e6,
            "C_over_A": row["C_over_A"],
            "previous_Bishara_linear_anchor": expected,
            "absolute_difference": residual,
        })
        if residual > 2.0e-5:
            raise RuntimeError(f"Bishara-linear C/A anchor mismatch at ER={ER}: {residual}")

    min_pole_clearance = min(row["pole_clearance_keV"] for row in rows if row["phase_space_open"])
    if min_pole_clearance <= 0.0:
        raise RuntimeError("fixed Delta m=450 keV scan crosses the chi2 pole")

    csv_path = outdir / "xe131_fixed_benchmark_absolute_dsigma_450keV.csv"
    metadata_path = outdir / "xe131_fixed_benchmark_absolute_dsigma_450keV_metadata.json"
    write_csv(csv_path, rows)
    summary = {
        "status": "PASS_XE131_FIXED_BENCHMARK_ABSOLUTE_B_BASELINE_AND_C_EXTENSION",
        "scope": "absolute fixed-speed Xe-131 spectrum with B as the primary finite-t_N M-only baseline and C as a separate Phi'' charge-response extension",
        "benchmark": {
            "mchi1_GeV": MCHI_GEV, "mchi2_GeV": MCHI_GEV + DELTA_M_GEV,
            "delta_m_keV": DELTA_M_GEV * 1.0e6, "ms_keV": MS_GEV * 1.0e6,
            "mV_GeV": MV_GEV, "speed_km_s": SPEED_KM_S, "g2_for_width": G2,
            "coupling_product_squared_(g1_g2_gVN)^2": COUPLING_PRODUCT_SQUARED,
            "coupling_basis": "effective nucleon g_VN; g_VN=3*g_Vq",
            "width_scheme": WIDTH_SCHEME,
            "Gamma_chi2_pole_keV": eq6.chi2_width_dirac_scalar(
                MCHI_GEV, MS_GEV, DELTA_M_GEV, G2
            ) * 1.0e6,
            "propagator_width_policy": (
                "Eq. (19): first p-k propagator is zero-width (+i0+); "
                "second p'+k propagator carries +i*m_chi2*Gamma_chi2_pole"
            ),
            "propagator": "1/(mV^2-t_A), t_A=q_A^2=-2*mA*ER; Q_A^2=2*mA*ER+ER^2 is not used in the mediator denominator",
            "incident_momentum": "p_chi=m_chi*gamma*v/c",
        },
        "target": {
            "isotope": "Xe-131", "A": 131, "Z": 54,
            "atomic_mass_u": XE131_MASS_RECORD["atomic_mass_u"],
            "mA_bare_nucleus_GeV": MA_XE131_GEV,
            "mass_scheme": "AME atomic mass minus Z electron masses, multiplied by u_GeV; no electronic binding correction",
        },
        "nuclear_response": {
            "source": "AFH DMFormFactor v6.0 native Wolfram 14.2.0",
            "responses": ["M", "PhiPP", "MPhiPP"],
            "normalization": "physical equal-proton/neutron; factor four applied exactly once",
            "interpolation": "PCHIP on provenance-pinned 2401-point q grid",
            "finite_Q2_form_factors": "Bishara linear flavor-resolved low-Q_N^2 prescription is the primary B baseline; isoscalar_zexp is an alternate sensitivity model; full universal u+d+s F1,F2 are divided by three before use with the external g_VN prefactor",
            "nuclear_response_baseline": "AFH finite-size W_M(y_A), physical equal-p=n response; no extra Helm factor",
            "AFH_response_normalization": "factor four applied exactly once in physical equal-p=n response",
            "nucleon_form_factor_normalization": "Fhat_i=F_i^(u+d+s)/3",
            "nucleon_transfer_scheme": "strict one-body impulse q_N^mu=q_A^mu, t_N=t_A=-2*m_A*E_R",
            "native_provenance": provenance,
        },
        "primary_B_formula": "dSigma_B/dER = mA*(g1*g2*gVN)^2/[256*pi^3*pchi^2*(mV^2-t_A)^2] * L_C^(3) * cMhat(t_N)^2 * W_M^phys(y_A); only AFH M response is included",
        "C_extension_formula": "dSigma_C/dER = dSigma_B/dER + prefactor*L_C*[2*cMhat*cPhihat*W_MPhiPP + cPhihat^2*W_PhiPP]",
        "form_factor_prescription": form_factor_prescription,
        "form_factor_status": "Bishara linear: F1^uds(t_N)=3+8.392*t_N+O(t_N^2), F2^uds(t_N)=-0.552+O(t_N); Fhat_i=F_i^uds/3 in the external g_VN basis",
        "transfer_convention": "t_N=t_A=-2*m_A*E_R for strict one-body impulse; Q_A^2=2*m_A*E_R+E_R^2 is used in AFH y_A and spatial NR coefficients",
        "definitions": {
            "Q_A_squared_GeV2": "2*mA*ER+ER^2; spatial momentum squared used in AFH response",
            "t_A_GeV2": "-2*mA*ER; Lorentz-invariant transfer used in the mediator propagator",
            "t_N_GeV2": "t_A=-2*mA*ER in the strict one-body impulse prescription",
            "L_C_GeV2": "L00-(ER/Q_A)*(L03+L30)+(ER/Q_A)^2*L33",
            "cMhat": "Fhat1+t_N*(Fhat1+2*Fhat2)/(8*mN^2)",
            "cPhihat": "Q_A^2*(Fhat1+2*Fhat2)/(4*mN^2)",
            "units": "kernel L_C*W has GeV^2; public prefactor GeV^-5; dSigma/dER GeV^-3",
            "conversion_GeVminus3_to_cm2_per_keV": GEV_MINUS3_TO_CM2_PER_KEV,
        },
        "recoil_interval_keV": [er_min, er_max],
        "recoil_grid": {
            "points": len(rows),
            "open_points": sum(bool(row["phase_space_open"]) for row in rows),
            "grid": "2-keV global grid, 0.5-keV refinement around AFH response minima, exact endpoints and 200/267-keV anchors",
            "curve_quadrature_order": list(CURVE_ORDER),
            "high_order_anchor_order": list(HIGH_ORDER),
            "high_order_anchor_checks": anchors,
            "maximum_high_order_relative_difference": max_anchor_difference,
        },
        "independent_Eq6_L00_crosschecks": legacy_checks,
        "maximum_independent_Eq6_relative_residual": max_legacy_residual,
        "independent_Eq6_crosscheck_order": list(LEGACY_ORDER),
        "nuclear_ratio_crosschecks_against_previous_validated_run": ratio_checks,
        "minimum_chi2_pole_clearance_keV": min_pole_clearance,
        "primary_baseline": "B: finite-t_N Dirac-Pauli nucleon current times the AFH finite-size W_M(y_A) response, with no additional AFH response channels",
        "A_reference": "q=0 effective nucleon current times the same finite-size AFH W_M(y_A)",
        "C_extension": "M+Phi''+M-Phi'' charge-sector extension, reported separately from B",
        "limitations": [
            "B is the primary baseline; C is a separate charge-multipole extension. Native transverse Delta, SigmaPrime and SigmaPrime-Delta responses are not included in this absolute curve.",
            "Continuity reduction is conditional on conservation of the complete nuclear one-body vector current.",
            "The primary B prescription is the first-order Bishara flavor-summed F1(t_N) expansion with F2(t_N)=F2(0)+O(t_N); isoscalar_zexp is a separate sensitivity model. Full quark-current values are normalized by three before entering the external g_VN-prefactor rate.",
            "Single isotope and fixed incident speed only; no halo average, isotope sum, detector response, exposure, event count or exclusion.",
            "Coupling-product-squared is the unit reference normalization; results scale linearly with this quantity.",
            "The six-channel spatial OBDME candidate remains provisional pending native-Wolfram spatial-response validation and P3-C amplitude-level matching.",
            "The pole width is conditional on Dirac chi2, a real scalar, a pure-scalar off-diagonal Yukawa coupling, and no additional open chi2 decay channels.",
        ],
        "output_files": [
            csv_path.name, metadata_path.name,
            "xe131_fixed_benchmark_absolute_dsigma_450keV.svg",
            "xe131_fixed_benchmark_absolute_dsigma_450keV.pdf",
        ],
    }
    metadata_path.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    plot_absolute(rows, outdir)
    return summary

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--afh-csv", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.afh_csv, args.outdir)
    print(json.dumps({
        "status": result["status"], "benchmark": result["benchmark"],
        "recoil_interval_keV": result["recoil_interval_keV"],
        "grid": result["recoil_grid"]["points"],
        "open_points": result["recoil_grid"]["open_points"],
        "max_high_order_difference": result["recoil_grid"]["maximum_high_order_relative_difference"],
        "max_Eq6_residual": result["maximum_independent_Eq6_relative_residual"],
        "minimum_pole_clearance_keV": result["minimum_chi2_pole_clearance_keV"],
        "output": str(args.outdir),
    }, indent=2))

if __name__ == "__main__":
    main()