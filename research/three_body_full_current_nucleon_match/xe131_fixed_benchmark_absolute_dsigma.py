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
    RAW_F1_UDS0, RAW_F2_UDS0, bishara_linear, charge_coefficients,
    effective_nucleon_form_factors,
)
from three_body_phase_space_tensor import eq6, integrate_spin_resolved_tensor
from xe131_fixed_speed_charge_dsigma import (
    G2, MA_XE131_GEV, MCHI_GEV, MN_GEV, MS_GEV, MV_GEV, SPEED_KM_S,
    XE131_MASS_RECORD, exact_qA_GeV, load_native_xe131_responses,
    interpolate_responses,
)
from xe131_dense_native_afh_overlay import overlay_dense_native_charge_grid

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

def nuclear_charge_kernels(ER_keV: float, LC: float, responses: dict[str, float]) -> dict:
    qA = exact_qA_GeV(MA_XE131_GEV, ER_keV)
    ER_GeV = ER_keV * 1.0e-6
    tN_GeV2 = -2.0 * MA_XE131_GEV * ER_GeV
    Q_A2_GeV2 = qA * qA

    # Raw universal u+d+s form factors are divided by three because the
    # public prefactor is already expressed with g_VN=3*g_Vq.
    F1_raw, F2_raw = bishara_linear(-tN_GeV2)
    F1, F2 = effective_nucleon_form_factors(F1_raw, F2_raw)
    F1hat0, _ = effective_nucleon_form_factors(RAW_F1_UDS0, RAW_F2_UDS0)
    cM, cPhi = charge_coefficients(
        qA, F1=F1, F2=F2, tN_GeV2=tN_GeV2, mN_GeV=MN_GEV
    )
    WM, WPhi, WMPhi = (
        float(responses["M"]), float(responses["PhiPP"]), float(responses["MPhiPP"])
    )
    if WM <= 0.0 or WPhi < -1.0e-12:
        raise ArithmeticError("invalid diagonal AFH charge response")
    if not math.isfinite(LC) or LC <= 0.0:
        raise ArithmeticError("invalid continuity-adjusted Coulomb weight")

    A_reference = F1hat0**2 * LC * WM
    B_baseline = cM**2 * LC * WM
    M_Phi_interference = 2.0 * cM * cPhi * LC * WMPhi
    PhiPP_diagonal = cPhi**2 * LC * WPhi
    C_extension = B_baseline + M_Phi_interference + PhiPP_diagonal
    if min(A_reference, B_baseline, C_extension) <= 0.0:
        raise ArithmeticError("non-positive A/B/C coherent charge kernel")

    C_over_B = C_extension / B_baseline
    B_over_A = B_baseline / A_reference
    C_over_A = C_extension / A_reference
    if not math.isclose(C_over_A, B_over_A * C_over_B, rel_tol=2.0e-13, abs_tol=2.0e-15):
        raise ArithmeticError("A/B/C charge ratios do not factorize")

    return {
        "F1V_quark_sum": F1_raw,
        "F2V_quark_sum": F2_raw,
        "F1N_effective": F1,
        "F2N_effective": F2,
        "tN_GeV2": tN_GeV2,
        "Q_A2_GeV2": Q_A2_GeV2,
        "cM": cM,
        "cPhiPP": cPhi,
        "A_reference_M": A_reference,
        "B_finite_tN_M": B_baseline,
        "M_Phi_interference": M_Phi_interference,
        "PhiPP_diagonal": PhiPP_diagonal,
        "C_MplusPhiPP": C_extension,
        "B_over_A_reference": B_over_A,
        "C_over_B_baseline": C_over_B,
        "C_over_A_reference": C_over_A,
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

def calculate_row(ER_keV: float, response_bundle: dict,
                  order: tuple[int, int, int] = CURVE_ORDER) -> dict:
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
            "A_reference_M_GeVminus3": 0.0, "B_finite_tN_M_GeVminus3": 0.0,
            "M_Phi_interference_GeVminus3": 0.0, "PhiPP_diagonal_GeVminus3": 0.0,
            "C_MplusPhiPP_GeVminus3": 0.0, "A_reference_M_cm2_per_keV": 0.0,
            "B_finite_tN_M_cm2_per_keV": 0.0, "C_MplusPhiPP_cm2_per_keV": 0.0,
            "B_over_A_reference": 0.0, "C_over_B_baseline": 0.0,
            "C_over_A_reference": 0.0,
        }
    kernels = nuclear_charge_kernels(ER_keV, phase["L_C_GeV2"], responses)
    prefactor = kin["public_prefactor_GeVminus5"]
    values = {
        key: prefactor * kernels[key]
        for key in (
            "A_reference_M", "B_finite_tN_M", "M_Phi_interference",
            "PhiPP_diagonal", "C_MplusPhiPP",
        )
    }
    return {
        **base,
        "F1V_quark_sum": kernels["F1V_quark_sum"],
        "F2V_quark_sum": kernels["F2V_quark_sum"],
        "F1N_effective": kernels["F1N_effective"],
        "F2N_effective": kernels["F2N_effective"],
        "tN_GeV2": kernels["tN_GeV2"],
        "cM": kernels["cM"],
        "cPhiPP": kernels["cPhiPP"],
        "L_C_over_L00_minus_one": phase["L_C_over_L00_minus_one"],
        "A_reference_M_kernel_GeV2": kernels["A_reference_M"],
        "B_finite_tN_M_kernel_GeV2": kernels["B_finite_tN_M"],
        "M_Phi_interference_kernel_GeV2": kernels["M_Phi_interference"],
        "PhiPP_diagonal_kernel_GeV2": kernels["PhiPP_diagonal"],
        "C_MplusPhiPP_kernel_GeV2": kernels["C_MplusPhiPP"],
        "A_reference_M_GeVminus3": values["A_reference_M"],
        "B_finite_tN_M_GeVminus3": values["B_finite_tN_M"],
        "M_Phi_interference_GeVminus3": values["M_Phi_interference"],
        "PhiPP_diagonal_GeVminus3": values["PhiPP_diagonal"],
        "C_MplusPhiPP_GeVminus3": values["C_MplusPhiPP"],
        "A_reference_M_cm2_per_keV": values["A_reference_M"] * GEV_MINUS3_TO_CM2_PER_KEV,
        "B_finite_tN_M_cm2_per_keV": values["B_finite_tN_M"] * GEV_MINUS3_TO_CM2_PER_KEV,
        "C_MplusPhiPP_cm2_per_keV": values["C_MplusPhiPP"] * GEV_MINUS3_TO_CM2_PER_KEV,
        "B_over_A_reference": kernels["B_over_A_reference"],
        "C_over_B_baseline": kernels["C_over_B_baseline"],
        "C_over_A_reference": kernels["C_over_A_reference"],
    }

def plot_absolute(rows: list[dict], outdir: Path) -> None:
    import matplotlib.pyplot as plt
    from paper_plot_style import apply_paper_style, save_paper_figure

    apply_paper_style()
    opened = [row for row in rows if row["phase_space_open"]]
    er = np.asarray([row["ER_keV"] for row in opened])
    fig, ax = plt.subplots(figsize=(6.8, 4.45))
    ax.semilogy(er, [r["A_reference_M_cm2_per_keV"] for r in opened],
                linestyle="--", label=r"A: finite-size AFH $W_M$ reference")
    ax.semilogy(er, [r["B_finite_tN_M_cm2_per_keV"] for r in opened],
                linestyle="-", linewidth=2.0,
                label=r"B: finite-$t_N$ $M$-only baseline")
    ax.semilogy(er, [r["C_MplusPhiPP_cm2_per_keV"] for r in opened],
                linestyle="-.", linewidth=1.5,
                label=r"$\mathrm{C:}\ M+\Phi''\ \mathrm{charge\ extension}$")
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
    afh_csv: Path, outdir: Path,
    dense_native_csv: Path | None = None,
    dense_native_metadata: Path | None = None,
    dense_native_validation: Path | None = None,
) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    response_bundle, provenance = load_native_xe131_responses(afh_csv)
    dense_args = (dense_native_csv, dense_native_metadata, dense_native_validation)
    if any(item is not None for item in dense_args):
        if not all(item is not None for item in dense_args):
            raise ValueError("dense native overlay requires CSV, metadata, and validation JSON together")
        response_bundle, provenance = overlay_dense_native_charge_grid(
            response_bundle, provenance, dense_native_csv,
            dense_native_metadata, dense_native_validation,
        )
    er_min, er_max = find_open_interval()
    energies = make_recoil_grid(er_min, er_max)
    rows = [calculate_row(float(ER), response_bundle, CURVE_ORDER) for ER in energies]
    if not rows or not any(row["phase_space_open"] for row in rows):
        raise RuntimeError("absolute fixed-benchmark curve contains no open recoil points")

    anchors = []
    for ER in (200.0, 267.0, 269.0, 546.0, 650.0):
        medium = min(rows, key=lambda row: abs(row["ER_keV"] - ER))
        high = calculate_row(ER, response_bundle, HIGH_ORDER)
        if not high["phase_space_open"]:
            raise RuntimeError(f"high-order convergence anchor ER={ER} is closed")
        relative = abs(high["C_MplusPhiPP_GeVminus3"] - medium["C_MplusPhiPP_GeVminus3"]) / max(abs(high["C_MplusPhiPP_GeVminus3"]), 1.0e-300)
        anchors.append({
            "ER_keV": ER, "medium_grid_nearest_ER_keV": medium["ER_keV"],
            "high_order": list(HIGH_ORDER), "medium_order": list(CURVE_ORDER),
            "high_full_charge_GeVminus3": high["C_MplusPhiPP_GeVminus3"],
            "medium_full_charge_GeVminus3": medium["C_MplusPhiPP_GeVminus3"],
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
    # The 267 keV anchor is evaluated on the merged 2,509-point grid with the
    # 121-point native Xe-131 dip overlay. Direct native AFH at
    # q(267 keV)=0.255146745 GeV gives 0.6056676141; the 0.000025 GeV dense
    # PCHIP gives 0.6056675913. The previous 0.6056496631 anchor was the
    # coarse-grid interpolation value.
    expected_charge_ratios = {
        200.0: 0.7376302305280606,
        267.0: 0.605667591295857,
    }
    ratio_checks = []
    for ER, expected in expected_charge_ratios.items():
        row = min(rows, key=lambda item: abs(item["ER_keV"] - ER))
        residual = abs(row["C_over_A_reference"] - expected)
        ratio_checks.append({
            "ER_keV": ER,
            "fixed_Delta_m_keV": DELTA_M_GEV * 1.0e6,
            "ratio": row["C_over_A_reference"],
            "previous_validated_ratio": expected,
            "absolute_difference": residual,
        })
        if residual > 2.0e-8:
            raise RuntimeError(f"native AFH charge ratio mismatch at ER={ER}: {residual}")

    min_pole_clearance = min(row["pole_clearance_keV"] for row in rows if row["phase_space_open"])
    if min_pole_clearance <= 0.0:
        raise RuntimeError("fixed Delta m=450 keV scan crosses the chi2 pole")

    csv_path = outdir / "xe131_fixed_benchmark_absolute_dsigma_450keV.csv"
    metadata_path = outdir / "xe131_fixed_benchmark_absolute_dsigma_450keV_metadata.json"
    write_csv(csv_path, rows)
    summary = {
        "status": "PASS_XE131_FIXED_BENCHMARK_ABSOLUTE_ABC_CHARGE_SECTOR",
        "scope": "absolute fixed-speed, single-isotope Xe-131 A/B/C differential cross sections in the coherent charge sector; B is the adopted M-only production baseline and C is a separate Phi'' extension",
        "benchmark": {
            "mchi1_GeV": MCHI_GEV, "mchi2_GeV": MCHI_GEV + DELTA_M_GEV,
            "delta_m_keV": DELTA_M_GEV * 1.0e6, "ms_keV": MS_GEV * 1.0e6,
            "mV_GeV": MV_GEV, "speed_km_s": SPEED_KM_S, "g2_for_width": G2,
            "coupling_product_squared_(g1_g2_gVN)^2": COUPLING_PRODUCT_SQUARED,
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
            "normalization": (
                "native physical equal-proton/neutron columns include factor four once; "
                "loader applies common OBDME C0 once to all three charge responses"
            ),
            "interpolation": (
                "PCHIP on merged 2,509-point native grid: 2,401-point coarse archive "
                "with the 121-point native Xe-131 dense dip grid replacing 13 overlap nodes"
                if provenance.get("dense_native_overlay")
                else "PCHIP on provenance-pinned 2401-point q grid"
            ),
            "finite_tN_form_factors": "adopted Bishara-linear raw u+d+s F1 slope plus constant raw F2 anchor; both divided by three in the external-gVN effective nucleon basis",
            "native_provenance": provenance,
        },
        "formula": "B: dSigma_B/dER = mA*(g1*g2*gVN)^2/[256*pi^3*pchi^2*(mV^2-t_A)^2] * L_C^(3) * cMhat(tN)^2 * W_M_phys(yA); C adds 2*cMhat*cPhihat*W_MPhiPP_phys + cPhihat^2*W_PhiPP_phys. A is the q=0 effective-nucleon-current reference. tN=tA=-2*mA*ER; Q_A^2=2*mA*ER+ER^2 enters AFH yA and cPhihat only.",
        "definitions": {
            "Q_A_squared_GeV2": "2*mA*ER+ER^2; exact spatial momentum squared used in AFH yA and cPhiPP",
            "t_A_GeV2": "-2*mA*ER; Lorentz-invariant transfer used in the mediator propagator",
            "L_C_GeV2": "L00-(ER/Q_A)*(L03+L30)+(ER/Q_A)^2*L33",
            "t_N_GeV2": "-2*mA*ER; formal one-body impulse invariant used in finite nucleon form factors and cM",
            "cM": "F1hat+t_N*(F1hat+2*F2hat)/(8*mN^2)",
            "cPhiPP": "Q_A^2*(F1hat+2*F2hat)/(4*mN^2)",
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
        "limitations": [
            "Charge-sector result only; native transverse Delta, SigmaPrime and SigmaPrime-Delta responses are not included in the central absolute curve.",
            "Continuity reduction is conditional on conservation of the complete nuclear one-body vector current.",
            "B uses the available low-momentum F1 slope and constant F2 anchor; no unsupported F2 slope is assumed.",
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
    parser.add_argument("--dense-native-csv", type=Path)
    parser.add_argument("--dense-native-metadata", type=Path)
    parser.add_argument("--dense-native-validation", type=Path)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    result = run(
        args.afh_csv, args.outdir, args.dense_native_csv,
        args.dense_native_metadata, args.dense_native_validation,
    )
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