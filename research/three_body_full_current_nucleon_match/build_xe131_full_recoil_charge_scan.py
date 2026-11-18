#!/usr/bin/env python3
"""Publication-style plots from the committed 943-point Xe-131 charge scan.

This script only plots the committed CSV. It does not alter or recompute the
underlying AFH response data.
"""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from paper_plot_style import apply_paper_style, save_paper_figure

HERE = Path(__file__).resolve().parent
DEFAULT_CSV = HERE / "results" / "2026-11-18" / "xe131_charge_kernel_full_recoil_scan.csv"
DEFAULT_OUT = HERE / "results" / "2026-11-18"

def load_rows(path: Path) -> dict[str, np.ndarray]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 943:
        raise ValueError(f"expected 943 native-grid rows, found {len(rows)}")
    keys = rows[0].keys()
    return {key: np.asarray([float(row[key]) for row in rows]) for key in keys}

def reference_lines(ax) -> None:
    ax.axvline(200.0, color="0.45", linestyle="--", linewidth=0.85,
               label=r"$E_R=200~\mathrm{keV}$")
    ax.axvline(267.0, color="0.60", linestyle=":", linewidth=1.0,
               label=r"$E_R=267~\mathrm{keV}$")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    data = load_rows(args.csv)
    args.outdir.mkdir(parents=True, exist_ok=True)
    apply_paper_style()

    er = data["ER_keV"]
    km = data["K_M_only"]
    kmi = data["K_M_plus_interference"]
    kfull = data["K_full_charge"]
    scale = float(np.max(km))

    fig, ax = plt.subplots(figsize=(6.8, 4.45))
    ax.semilogy(er, km / scale, label=r"$K_M=c_M^2W_M$")
    ax.semilogy(er, kmi / scale,
                label=r"$K_M+2c_Mc_{\Phi''}W_{M\Phi''}$")
    ax.semilogy(er, kfull / scale,
                label=r"$K_{\mathrm{ch}}=K_M+2c_Mc_{\Phi''}W_{M\Phi''}+c_{\Phi''}^2W_{\Phi''}$")
    reference_lines(ax)
    ax.set_xlim(float(er.min()), float(er.max()))
    ax.set_xlabel(r"Recoil energy, $E_R$ [keV]")
    ax.set_ylabel(r"Normalized charge-sector kernel, $K/K_{M,\max}$")
    ax.set_title(r"Xe-131 charge-sector response kernels")
    ax.legend(loc="best", ncol=1)
    ax.tick_params(which="both", direction="in", top=True, right=True)
    fig.tight_layout(pad=0.6)
    save_paper_figure(fig, args.outdir / "xe131_charge_kernel_full_recoil_curves")

    fig, ax = plt.subplots(figsize=(6.8, 4.45))
    ax.plot(er, data["ratio_M_plus_int_over_M"],
            label=r"$(K_M+2c_Mc_{\Phi''}W_{M\Phi''})/K_M$")
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
    save_paper_figure(fig, args.outdir / "xe131_charge_kernel_full_recoil_ratios")

    print({
        "rows": len(er),
        "ER_min_keV": float(er.min()),
        "ER_max_keV": float(er.max()),
        "ratio_min": float(np.min(data["ratio_full_over_M"])),
        "ratio_max": float(np.max(data["ratio_full_over_M"])),
        "outputs": [
            "xe131_charge_kernel_full_recoil_curves.svg/.pdf",
            "xe131_charge_kernel_full_recoil_ratios.svg/.pdf",
        ],
    })

if __name__ == "__main__":
    main()
