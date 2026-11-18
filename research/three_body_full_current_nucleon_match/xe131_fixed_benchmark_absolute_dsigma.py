#!/usr/bin/env python3
"""Absolute fixed-benchmark Xe-131 d sigma/dER in the AFH charge sector.

The complete three-body DM phase space is integrated pointwise at fixed
Delta m=450 keV and zero-width prescription. Public flux, mediator, coupling
and target-mass prefactors are restored after the coherent AFH charge
contraction. Transverse nuclear multipoles are not included.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CALC_DIR = ROOT / "research" / "three_body_calculation_and_validation"
if str(CALC_DIR) not in sys.path:
    sys.path.insert(0, str(CALC_DIR))
import eq6_kernel  # noqa: E402
from nucleon_vector_form_factors import F1V0, charge_coefficients, isoscalar_zexp
from paper_plot_style import apply_paper_style, save_paper_figure
from three_body_phase_space_tensor import eq6, integrate_spin_resolved_tensor
from xe131_fixed_speed_charge_dsigma import (
    G2, MA_XE131_GEV, MCHI_GEV, MN_GEV, MS_GEV, MV_GEV, SPEED_KM_S,
    XE131_MASS_RECORD, exact_qA_GeV, load_native_xe131_responses,
    interpolate_responses,
)

DELTA_M_GEV = 450.0e-6
COUPLING_PRODUCT_SQUARED = 1.0
WIDTH_SCHEME = "zero"
MAPPING = "threshold_u2"
CURVE_ORDER = (20, 16, 12)
HIGH_ORDER = (40, 32, 16)
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
    denominator = (mV_GeV * mV_GeV + qA * qA) ** 2
    prefactor = mA_GeV * coupling_product_squared / (
        256.0 * math.pi**3 * pchi * pchi * denominator
    )
    return {
        "qA_GeV": qA,
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
        "quadrature_points": int(result["quadrature_points"]),
    }

def nuclear_charge_kernels(ER_keV: float, LC: float, responses: dict[str, float]) -> dict:
    qA = exact_qA_GeV(MA_XE131_GEV, ER_keV)
    F1, F2 = isoscalar_zexp(qA * qA)
    cM, cPhi = charge_coefficients(qA, F1=F1, F2=F2, mN_GeV=MN_GEV)
    WM, WPhi, WMPhi = (
        float(responses["M"]), float(responses["PhiPP"]), float(responses["MPhiPP"])
    )
    if min(WM, WPhi) < -1.0e-12:
        raise ArithmeticError("negative diagonal AFH charge response")
    terms = {
        "pointlike_M": F1V0**2 * LC * WM,
        "finite_t_M": cM**2 * LC * WM,
        "M_Phi_interference": 2.0 * cM * cPhi * LC * WMPhi,
        "PhiPP_diagonal": cPhi**2 * LC * WPhi,
    }
    terms["full_charge"] = (
        terms["finite_t_M"] + terms["M_Phi_interference"] + terms["PhiPP_diagonal"]
    )
    if terms["full_charge"] <= 0.0 or terms["pointlike_M"] <= 0.0:
        raise ArithmeticError("non-positive coherent charge kernel")
    return {
        "F1V": F1, "F2V": F2, "cM": cM, "cPhiPP": cPhi,
        **terms,
        "full_charge_over_pointlike_M": terms["full_charge"] / terms["pointlike_M"],
        "full_charge_over_finite_t_M": terms["full_charge"] / terms["finite_t_M"],
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
        "quadrature_points": phase["quadrature_points"],
        "nw": order[0], "nz": order[1], "nphi": order[2],
        "pchi_GeV": kin["pchi_GeV"],
        "mediator_denominator_GeV4": kin["mediator_denominator_GeV4"],
        "public_prefactor_GeVminus5": kin["public_prefactor_GeVminus5"],
        "phase_space_open": bool(phase["phase_space_open"]),
    }
    if not phase["phase_space_open"]:
        return {
            **base,
            "pointlike_M_GeVminus3": 0.0, "finite_t_M_GeVminus3": 0.0,
            "M_Phi_interference_GeVminus3": 0.0, "PhiPP_diagonal_GeVminus3": 0.0,
            "full_charge_GeVminus3": 0.0, "pointlike_M_cm2_per_keV": 0.0,
            "finite_t_M_cm2_per_keV": 0.0, "full_charge_cm2_per_keV": 0.0,
            "full_charge_over_pointlike_M": 0.0,
        }
    kernels = nuclear_charge_kernels(ER_keV, phase["L_C_GeV2"], responses)
    prefactor = kin["public_prefactor_GeVminus5"]
    values = {key: prefactor * kernels[key] for key in
              ("pointlike_M", "finite_t_M", "M_Phi_interference", "PhiPP_diagonal", "full_charge")}
    return {
        **base,
        "F1V": kernels["F1V"], "F2V": kernels["F2V"],
        "cM": kernels["cM"], "cPhiPP": kernels["cPhiPP"],
        "L_C_over_L00_minus_one": phase["L_C_over_L00_minus_one"],
        "pointlike_M_kernel_GeV2": kernels["pointlike_M"],
        "finite_t_M_kernel_GeV2": kernels["finite_t_M"],
        "M_Phi_interference_kernel_GeV2": kernels["M_Phi_interference"],
        "PhiPP_diagonal_kernel_GeV2": kernels["PhiPP_diagonal"],
        "full_charge_kernel_GeV2": kernels["full_charge"],
        "pointlike_M_GeVminus3": values["pointlike_M"],
        "finite_t_M_GeVminus3": values["finite_t_M"],
        "M_Phi_interference_GeVminus3": values["M_Phi_interference"],
        "PhiPP_diagonal_GeVminus3": values["PhiPP_diagonal"],
        "full_charge_GeVminus3": values["full_charge"],
        "pointlike_M_cm2_per_keV": values["pointlike_M"] * GEV_MINUS3_TO_CM2_PER_KEV,
        "finite_t_M_cm2_per_keV": values["finite_t_M"] * GEV_MINUS3_TO_CM2_PER_KEV,
        "full_charge_cm2_per_keV": values["full_charge"] * GEV_MINUS3_TO_CM2_PER_KEV,
        "full_charge_over_pointlike_M": kernels["full_charge_over_pointlike_M"],
        "full_charge_over_finite_t_M": kernels["full_charge_over_finite_t_M"],
    }

def plot_absolute(rows: list[dict], outdir: Path) -> None:
    apply_paper_style()
    opened = [row for row in rows if row["phase_space_open"]]
    er = np.asarray([row["ER_keV"] for row in opened])
    fig, ax = plt.subplots(figsize=(6.8, 4.45))
    ax.semilogy(er, [r["pointlike_M_cm2_per_keV"] for r in opened],
                linestyle="--", label=r"Pointlike $9W_M$")
    ax.semilogy(er, [r["finite_t_M_cm2_per_keV"] for r in opened],
                linestyle="-.", label=r"Finite-$Q^2$ $M$ only")
    ax.semilogy(er, [r["full_charge_cm2_per_keV"] for r in opened],
                linestyle="-", linewidth=1.9,
                label=r"Coherent $M+\Phi''$ charge sector")
    ax.axvline(200.0, color="0.45", linestyle="--", linewidth=0.85,
               label=r"$E_R=200~\mathrm{keV}$")
    ax.axvline(267.0, color="0.60", linestyle=":", linewidth=1.0,
               label=r"$E_R=267~\mathrm{keV}$")
    ax.set_xlim(float(er.min()), float(er.max()))
    ax.set_xlabel(r"Recoil energy, $E_R$ [keV]")
    ax.set_ylabel(r"$\mathrm{d}\sigma/\mathrm{d}E_R$ [cm$^2$ keV$^{-1}$]")
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
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def run(afh_csv: Path, outdir: Path) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    response_bundle, provenance = load_native_xe131_responses(afh_csv)
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
        relative = abs(high["full_charge_GeVminus3"] - medium["full_charge_GeVminus3"]) / max(abs(high["full_charge_GeVminus3"]), 1.0e-300)
        anchors.append({
            "ER_keV": ER, "medium_grid_nearest_ER_keV": medium["ER_keV"],
            "high_order": list(HIGH_ORDER), "medium_order": list(CURVE_ORDER),
            "high_full_charge_GeVminus3": high["full_charge_GeVminus3"],
            "medium_full_charge_GeVminus3": medium["full_charge_GeVminus3"],
            "relative_difference": relative,
        })
    max_anchor_difference = max(item["relative_difference"] for item in anchors)
    if max_anchor_difference > 1.0e-3:
        raise RuntimeError(f"medium/high absolute dSigma convergence failed: {max_anchor_difference:.6g}")

    legacy_checks = []
    for ER in (200.0, 267.0):
        new = phase_space_integral(ER, (12, 10, 8))
        old = eq6_kernel.reduced_kernel(
            MCHI_GEV, MS_GEV, DELTA_M_GEV, MA_XE131_GEV,
            ER * 1.0e-6, SPEED_KM_S,
            nw=12, nz=10, nphi=8, width_scheme="zero",
        )
        residual = abs(new["L00_GeV2"] - old) / max(abs(old), 1.0e-300)
        legacy_checks.append({
            "ER_keV": ER, "spin_resolved_L00_GeV2": new["L00_GeV2"],
            "independent_Eq6_I6_GeV2": old, "relative_residual": residual,
        })
    max_legacy_residual = max(item["relative_residual"] for item in legacy_checks)
    if max_legacy_residual > 2.0e-8:
        raise RuntimeError(f"spin-resolved L00 does not reproduce independent Eq. (6): {max_legacy_residual:.6g}")

    min_pole_clearance = min(row["pole_clearance_keV"] for row in rows if row["phase_space_open"])
    if min_pole_clearance <= 0.0:
        raise RuntimeError("fixed Delta m=450 keV scan crosses the chi2 pole")

    csv_path = outdir / "xe131_fixed_benchmark_absolute_dsigma_450keV.csv"
    metadata_path = outdir / "xe131_fixed_benchmark_absolute_dsigma_450keV_metadata.json"
    write_csv(csv_path, rows)
    summary = {
        "status": "PASS_XE131_FIXED_BENCHMARK_ABSOLUTE_CHARGE_SECTOR_DSIGMA",
        "scope": "absolute fixed-speed, single-isotope Xe-131 differential cross section in the coherent M+Phi''+M-Phi'' charge sector",
        "benchmark": {
            "mchi1_GeV": MCHI_GEV, "mchi2_GeV": MCHI_GEV + DELTA_M_GEV,
            "delta_m_keV": DELTA_M_GEV * 1.0e6, "ms_keV": MS_GEV * 1.0e6,
            "mV_GeV": MV_GEV, "speed_km_s": SPEED_KM_S, "g2_for_width": G2,
            "coupling_product_squared_(g1_g2_gVN)^2": COUPLING_PRODUCT_SQUARED,
            "width_scheme": WIDTH_SCHEME,
            "propagator": "1/(mV^2+Q_A^2), Q_A^2=2*mA*ER+ER^2",
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
            "finite_Q2_form_factors": "central isoscalar_zexp diagnostic; not final model-specific universal u+d+s form factors",
            "native_provenance": provenance,
        },
        "formula": "dSigma/dER = mA*(g1*g2*gVN)^2/[256*pi^3*pchi^2*(mV^2+Q_A^2)^2] * L_C^(3) * [cM^2*W_M + 2*cM*cPhiPP*W_MPhiPP + cPhiPP^2*W_PhiPP]",
        "definitions": {
            "Q_A_squared_GeV2": "2*mA*ER+ER^2",
            "L_C_GeV2": "L00-(ER/Q_A)*(L03+L30)+(ER/Q_A)^2*L33",
            "cM": "F1V-Q_A^2*(F1V+2*F2V)/(8*mN^2)",
            "cPhiPP": "Q_A^2*(F1V+2*F2V)/(4*mN^2)",
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
        "minimum_chi2_pole_clearance_keV": min_pole_clearance,
        "limitations": [
            "Charge-sector result only; native transverse Delta, SigmaPrime and SigmaPrime-Delta responses are not included in the central absolute curve.",
            "Continuity reduction is conditional on conservation of the complete nuclear one-body vector current.",
            "Finite-Q2 isoscalar_zexp F1/F2 is diagnostic, especially for F2V(Q2), not a final model-specific universal form-factor determination.",
            "Single isotope and fixed incident speed only; no halo average, isotope sum, detector response, exposure, event count or exclusion.",
            "Coupling-product-squared is the unit reference normalization; results scale linearly with this quantity.",
            "The six-channel spatial OBDME candidate remains provisional pending native-Wolfram spatial-response validation and P3-C amplitude-level matching.",
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
