#!/usr/bin/env python3
"""Recompute the AFH-default Xe-131 response substitution for four benchmarks.

The existing Eq. (6) I6 grid is kept fixed. Only the physical nuclear response
is replaced, so this script is a controlled nuclear-model comparison rather
than a fresh three-body phase-space integration.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

A = 131
M_A_GEV = A * 0.93149410242
BENCHMARKS = {
    "red_ms200_dm1": {"m_s_keV": 200, "Delta_m_MeV": 1},
    "green_ms300_dm1": {"m_s_keV": 300, "Delta_m_MeV": 1},
    "black_ms360_dm1": {"m_s_keV": 360, "Delta_m_MeV": 1},
    "blue_ms300_dm10": {"m_s_keV": 300, "Delta_m_MeV": 10},
}


def _response_interpolator(afh_csv: Path) -> tuple[PchipInterpolator, np.ndarray]:
    response = pd.read_csv(afh_csv)
    required = {"q_GeV", "R_equal_pn_normalized"}
    missing = required - set(response.columns)
    if missing:
        raise ValueError(f"AFH response CSV is missing columns: {sorted(missing)}")
    q = response["q_GeV"].to_numpy(dtype=float)
    r = response["R_equal_pn_normalized"].to_numpy(dtype=float)
    if len(q) != 2401 or not np.all(np.diff(q) > 0):
        raise ValueError("Expected the monotonic 2401-point AFH q grid")
    if not np.isclose(q[0], 0.0, atol=1e-14) or not np.isclose(q[-1], 0.6, atol=1e-12):
        raise ValueError("Unexpected AFH q-grid endpoints")
    if not np.isclose(r[0], A**2, rtol=0, atol=1e-7):
        raise ValueError("AFH physical response is not normalized to A^2 at q=0")
    return PchipInterpolator(q, r, extrapolate=False), q


def recompute(base_csv: Path, afh_csv: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = pd.read_csv(base_csv)
    required = {
        "benchmark", "model", "ER_keV", "R_A", "I6_GeV2",
        "dsigma_GeVminus3", "rate_tonne_year_keV", "phase_space_open",
    }
    missing = required - set(base.columns)
    if missing:
        raise ValueError(f"Base CSV is missing columns: {sorted(missing)}")
    if set(base["model"].unique()) != {"GCN", "JJ55"}:
        raise ValueError("Base CSV must contain exactly the GCN and JJ55 rows")
    if set(base["benchmark"].unique()) != set(BENCHMARKS):
        raise ValueError("Base CSV benchmark labels do not match the four fixed benchmarks")

    interp, q_grid = _response_interpolator(afh_csv)
    gcn = base[base["model"] == "GCN"].copy()
    jj55 = base[base["model"] == "JJ55"].copy()
    keys = ["benchmark", "ER_keV"]
    gcn = gcn.sort_values(keys).reset_index(drop=True)
    jj55 = jj55.sort_values(keys).reset_index(drop=True)
    if len(gcn) != 640 or len(jj55) != 640:
        raise ValueError("Expected 4 benchmarks x 160 recoil points for each base model")
    if not gcn[keys].equals(jj55[keys]):
        raise ValueError("GCN and JJ55 recoil grids do not match")
    if not np.allclose(gcn["I6_GeV2"], jj55["I6_GeV2"], rtol=1e-12, atol=1e-12):
        raise ValueError("I6 differs between GCN and JJ55; cannot treat it as a shared kernel")
    if not np.array_equal(gcn["phase_space_open"].to_numpy(), jj55["phase_space_open"].to_numpy()):
        raise ValueError("Phase-space masks differ between GCN and JJ55")

    ER_GeV = gcn["ER_keV"].to_numpy(dtype=float) * 1e-6
    q_response = np.sqrt(2.0 * M_A_GEV * ER_GeV + ER_GeV**2)
    if q_response.min() < q_grid.min() or q_response.max() > q_grid.max():
        raise ValueError("AFH response interpolation would require extrapolation")
    r_afh = np.asarray(interp(q_response), dtype=float)
    r_gcn = gcn["R_A"].to_numpy(dtype=float)
    if np.any(r_gcn <= 0):
        raise ValueError("Non-positive GCN response encountered on the recoil grid")
    ratio = r_afh / r_gcn

    afh = gcn.copy()
    afh["model"] = "AFH_default"
    afh["q_response_GeV"] = q_response
    afh["R_A"] = r_afh
    afh["response_ratio_AFH_to_GCN"] = ratio
    afh["dsigma_GeVminus3"] = gcn["dsigma_GeVminus3"].to_numpy(dtype=float) * ratio
    afh["rate_tonne_year_keV"] = gcn["rate_tonne_year_keV"].to_numpy(dtype=float) * ratio

    gcn["q_response_GeV"] = q_response
    jj55["q_response_GeV"] = q_response
    gcn["response_ratio_AFH_to_GCN"] = np.nan
    jj55["response_ratio_AFH_to_GCN"] = np.nan

    combined = pd.concat([afh, gcn, jj55], ignore_index=True)
    combined["model"] = pd.Categorical(
        combined["model"], ["AFH_default", "GCN", "JJ55"], ordered=True
    )
    combined = combined.sort_values(["benchmark", "model", "ER_keV"]).reset_index(drop=True)
    combined["model"] = combined["model"].astype(str)

    wide = afh[
        ["benchmark", "ER_keV", "q_response_GeV", "R_A", "I6_GeV2",
         "dsigma_GeVminus3", "rate_tonne_year_keV", "phase_space_open",
         "response_ratio_AFH_to_GCN"]
    ].rename(columns={
        "R_A": "R_A_AFH",
        "dsigma_GeVminus3": "dsigma_AFH_GeVminus3",
        "rate_tonne_year_keV": "rate_AFH_tonne_year_keV",
    })
    wide = wide.merge(
        gcn[["benchmark", "ER_keV", "R_A", "dsigma_GeVminus3", "rate_tonne_year_keV"]].rename(
            columns={"R_A": "R_A_GCN", "dsigma_GeVminus3": "dsigma_GCN_GeVminus3",
                     "rate_tonne_year_keV": "rate_GCN_tonne_year_keV"}
        ), on=keys, validate="one_to_one"
    )
    wide = wide.merge(
        jj55[["benchmark", "ER_keV", "R_A", "dsigma_GeVminus3", "rate_tonne_year_keV"]].rename(
            columns={"R_A": "R_A_JJ55", "dsigma_GeVminus3": "dsigma_JJ55_GeVminus3",
                     "rate_tonne_year_keV": "rate_JJ55_tonne_year_keV"}
        ), on=keys, validate="one_to_one"
    )

    validate(combined, wide)
    return combined, wide


def validate(combined: pd.DataFrame, wide: pd.DataFrame) -> None:
    if len(combined) != 1920 or len(wide) != 640:
        raise AssertionError("Unexpected row count")
    for benchmark, group in combined.groupby("benchmark"):
        g = group[group["model"] == "GCN"].sort_values("ER_keV")
        j = group[group["model"] == "JJ55"].sort_values("ER_keV")
        a = group[group["model"] == "AFH_default"].sort_values("ER_keV")
        if not np.allclose(g["I6_GeV2"], j["I6_GeV2"], rtol=1e-12, atol=1e-12):
            raise AssertionError(f"I6 mismatch between GCN/JJ55 for {benchmark}")
        if not np.allclose(g["I6_GeV2"], a["I6_GeV2"], rtol=1e-12, atol=1e-12):
            raise AssertionError(f"I6 mismatch between GCN/AFH for {benchmark}")
        if not np.array_equal(g["phase_space_open"].to_numpy(), a["phase_space_open"].to_numpy()):
            raise AssertionError(f"Phase-space mask mismatch for {benchmark}")
        mask = g["phase_space_open"].astype(bool).to_numpy()
        lhs = a.loc[mask, "dsigma_GeVminus3"].to_numpy() / g.loc[mask, "dsigma_GeVminus3"].to_numpy()
        rhs = a.loc[mask, "R_A"].to_numpy() / g.loc[mask, "R_A"].to_numpy()
        if not np.allclose(lhs, rhs, rtol=2e-12, atol=2e-12):
            raise AssertionError(f"AFH cross-section/response ratio mismatch for {benchmark}")


def make_plots(combined: pd.DataFrame, outdir: Path) -> None:
    import matplotlib.pyplot as plt

    for benchmark, spec in BENCHMARKS.items():
        group = combined[combined["benchmark"] == benchmark]
        fig, ax = plt.subplots(figsize=(8.6, 5.6))
        for model in ["AFH_default", "GCN", "JJ55"]:
            rows = group[group["model"] == model].sort_values("ER_keV")
            mask = (
                (rows["dsigma_GeVminus3"].to_numpy(dtype=float) > 0)
                & rows["phase_space_open"].astype(bool).to_numpy()
            )
            ax.plot(rows.loc[mask, "ER_keV"], rows.loc[mask, "dsigma_GeVminus3"],
                    label=model, linewidth=1.8)
        ax.set_yscale("log")
        ax.set_xlim(0, 800)
        ax.set_xlabel(r"$E_R$ [keV]")
        ax.set_ylabel(r"$d\sigma_A/dE_R$ [GeV$^{-3}$]")
        ax.set_title(
            rf"Xe-131: $m_s={spec['m_s_keV']}$ keV, "
            rf"$\Delta m={spec['Delta_m_MeV']}$ MeV"
        )
        ax.grid(True, which="both", alpha=0.25)
        ax.legend()
        fig.tight_layout()
        fig.savefig(outdir / f"{benchmark}.png", dpi=220)
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-csv", type=Path, required=True)
    parser.add_argument("--afh-response-csv", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--plots", action="store_true")
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    combined, wide = recompute(args.base_csv, args.afh_response_csv)
    combined.to_csv(args.outdir / "figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv",
                    index=False, float_format="%.12g")
    wide.to_csv(args.outdir / "figure2_four_benchmarks_AFH_GCN_JJ55_wide_audit.csv",
                index=False, float_format="%.12g")
    selected = wide[wide["ER_keV"].isin([200, 265, 270, 540, 545, 800])].copy()
    selected["AFH_over_JJ55"] = selected["R_A_AFH"] / selected["R_A_JJ55"]
    selected.to_csv(args.outdir / "selected_response_ratios.csv", index=False, float_format="%.10g")
    if args.plots:
        make_plots(combined, args.outdir)

    thresholds = {}
    for benchmark, group in combined[combined["model"] == "GCN"].groupby("benchmark"):
        opened = group[group["phase_space_open"].astype(bool)]
        thresholds[benchmark] = float(opened["ER_keV"].min()) if len(opened) else None
    metadata = {
        "target": "Xe-131",
        "A": A,
        "mA_GeV": M_A_GEV,
        "AFH_response": "DMFormFactor v6.0 built-in sdgXe131",
        "physical_normalization": "R_A=16*pi*W_M00_AFH_v6/(2J_A+1), R_A(0)=A^2",
        "interpolation": "PCHIP in exact spatial q_response=sqrt(2*mA*ER+ER^2); no extrapolation",
        "I6_recomputed": False,
        "benchmarks": BENCHMARKS,
        "first_open_grid_point_keV": thresholds,
        "rows": {"long": len(combined), "wide": len(wide)},
        "limitations": [
            "Fixed mono-speed v=800 km/s; no halo velocity integration.",
            "Reuses the archived I6 grid; not a fresh three-body integral calculation.",
            "Conditional pole width, not a full self-energy calculation.",
            "No detector efficiency, resolution, cuts, or likelihood.",
            "Native Mathematica execution of AFH v6.0 remains pending.",
        ],
    }
    (args.outdir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
