#!/usr/bin/env python3
"""Rebuild Xe-131 full-recoil charge-sector kernels and figures from native AFH.

Run from the repository root:
  python research/three_body_full_current_nucleon_match/build_xe131_full_recoil_charge_scan.py

The kernels omit the common three-body DM-side factor; they are proportional
to, but are not absolute, differential cross sections.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results" / "2026-11-18"
NATIVE = (
    ROOT
    / "research"
    / "afh_default_density_xe131"
    / "output"
    / "phi_response_native"
    / "afh_default_xe131_M_PhiPP_native.csv"
)
M_A_GEV = 121.90971983538435
M_N_GEV = 0.938918
ER_MIN_KEV = 109.382231766
ER_MAX_KEV = 653.701913810

sys.path.insert(0, str(HERE))
from nucleon_vector_form_factors import charge_coefficients, isoscalar_zexp
from paper_plot_style import apply_paper_style, save_paper_figure


def build_scan(native_path: Path) -> pd.DataFrame:
    native = pd.read_csv(native_path)
    q_all = native["q_GeV"].to_numpy()
    er_all = (np.sqrt(M_A_GEV**2 + q_all**2) - M_A_GEV) * 1.0e6
    mask = (er_all >= ER_MIN_KEV) & (er_all <= ER_MAX_KEV)
    q, er = q_all[mask], er_all[mask]
    wm = native.loc[mask, "R_M_physical_equal_pn"].to_numpy()
    wp = native.loc[mask, "R_PhiPP_physical_equal_pn"].to_numpy()
    wmp = native.loc[mask, "R_MPhiPP_physical_equal_pn"].to_numpy()

    f1, f2, cm, cp = [], [], [], []
    for qi in q:
        fi1, fi2 = isoscalar_zexp(float(qi**2))
        ci_m, ci_p = charge_coefficients(
            float(qi), F1=fi1, F2=fi2, mN_GeV=M_N_GEV
        )
        f1.append(fi1)
        f2.append(fi2)
        cm.append(ci_m)
        cp.append(ci_p)
    f1, f2, cm, cp = map(np.asarray, (f1, f2, cm, cp))

    km = cm**2 * wm
    kmi = km + 2 * cm * cp * wmp
    kfull = kmi + cp**2 * wp
    result = pd.DataFrame(
        {
            "ER_keV": er,
            "q_GeV": q,
            "W_M": wm,
            "W_PhiPP": wp,
            "W_MPhiPP": wmp,
            "F1V": f1,
            "F2V": f2,
            "cM": cm,
            "cPhiPP": cp,
            "K_M_only": km,
            "K_M_plus_interference": kmi,
            "K_full_charge": kfull,
            "ratio_M_plus_int_over_M": kmi / km,
            "ratio_full_over_M": kfull / km,
        }
    )
    if len(result) != 943:
        raise ValueError(f"expected 943 native-grid rows, found {len(result)}")
    return result


def reference_lines(ax) -> None:
    ax.axvline(
        200.0,
        color="0.45",
        linestyle="--",
        linewidth=0.85,
        label=r"$E_R=200~\mathrm{keV}$",
    )
    ax.axvline(
        267.0,
        color="0.60",
        linestyle=":",
        linewidth=1.0,
        label=r"$E_R=267~\mathrm{keV}$",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, default=NATIVE)
    parser.add_argument("--outdir", type=Path, default=RESULTS)
    args = parser.parse_args()

    data = build_scan(args.native)
    args.outdir.mkdir(parents=True, exist_ok=True)
    data.to_csv(
        args.outdir / "xe131_charge_kernel_full_recoil_scan.csv",
        index=False,
        float_format="%.12g",
    )
    apply_paper_style()

    er = data["ER_keV"].to_numpy()
    km = data["K_M_only"].to_numpy()
    kmi = data["K_M_plus_interference"].to_numpy()
    kfull = data["K_full_charge"].to_numpy()
    scale = float(np.max(km))

    fig, ax = plt.subplots(figsize=(6.8, 4.45))
    ax.semilogy(er, km / scale, label=r"$K_M=c_M^2W_M$")
    ax.semilogy(
        er,
        kmi / scale,
        label=r"$K_M+2c_Mc_{\Phi''}W_{M\Phi''}$",
    )
    ax.semilogy(
        er,
        kfull / scale,
        label=(
            r"$K_{\mathrm{ch}}=K_M+2c_Mc_{\Phi''}W_{M\Phi''}"
            r"+c_{\Phi''}^2W_{\Phi''}$"
        ),
    )
    reference_lines(ax)
    ax.set_xlim(float(er.min()), float(er.max()))
    ax.set_xlabel(r"Recoil energy, $E_R$ [keV]")
    ax.set_ylabel(r"Normalized charge-sector kernel, $K/K_{M,\max}$")
    ax.set_title(r"Xe-131 charge-sector response kernels")
    ax.legend(loc="best", ncol=1)
    ax.tick_params(which="both", direction="in", top=True, right=True)
    fig.tight_layout(pad=0.6)
    save_paper_figure(
        fig, args.outdir / "xe131_charge_kernel_full_recoil_curves"
    )

    fig, ax = plt.subplots(figsize=(6.8, 4.45))
    ax.plot(
        er,
        data["ratio_M_plus_int_over_M"],
        label=r"$(K_M+2c_Mc_{\Phi''}W_{M\Phi''})/K_M$",
    )
    ax.plot(er, data["ratio_full_over_M"], label=r"$K_{\mathrm{ch}}/K_M$")
    ax.axhline(1.0, color="0.25", linestyle="-", linewidth=0.8)
    reference_lines(ax)
    ax.set_xlim(float(er.min()), float(er.max()))
    ax.set_xlabel(r"Recoil energy, $E_R$ [keV]")
    ax.set_ylabel(r"Ratio to finite-$Q^2$ $M$-only kernel")
    ax.set_title(r"Xe-131 charge-sector response correction")
    ax.legend(loc="best", ncol=1)
    ax.tick_params(which="both", direction="in", top=True, right=True)
    fig.tight_layout(pad=0.6)
    save_paper_figure(
        fig, args.outdir / "xe131_charge_kernel_full_recoil_ratios"
    )

    print(
        {
            "rows": len(er),
            "ER_min_keV": float(er.min()),
            "ER_max_keV": float(er.max()),
            "ratio_min": float(data["ratio_full_over_M"].min()),
            "ratio_max": float(data["ratio_full_over_M"].max()),
            "outputs": [
                "xe131_charge_kernel_full_recoil_curves.svg/.pdf",
                "xe131_charge_kernel_full_recoil_ratios.svg/.pdf",
            ],
        }
    )


if __name__ == "__main__":
    main()