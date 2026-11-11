#!/usr/bin/env python3
"""Reproduce the Anand et al. isoscalar coherent-charge response for xenon.

The dmscatter implementation is pinned in the accompanying workflow.  We ask
it for proton/neutron nuclear-response components (pnresponse=1), then form
the equal-coupling coherent combination by summing pp, pn, np, nn.

The response convention tested here is
    R_A(E_R) = 4*pi/(2*J_A+1) * W_M^00(y),
    y = (q*b/2)^2,
with R_A(0)=A^2.

This script computes only the nuclear factor.  It does not evaluate the
three-body matrix-element integral or halo integral.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import minimize_scalar
from scipy.signal import find_peaks

Z_XE = 54
FM_TO_GEV_INV = 5.0677
Q_MIN_GEV = 0.0
Q_MAX_GEV = 0.60
Q_STEP_GEV = 0.00025
ER_MAX_KEV = 800.0
ER_STEP_KEV = 0.5

# NIST isotopic compositions: amount fractions, not mass fractions.
# Xe-124 and Xe-126 are omitted from the dmscatter target library.
NATURAL_ABUNDANCE = {
    124: 0.000952,
    126: 0.000890,
    128: 0.019102,
    129: 0.264006,
    130: 0.040710,
    131: 0.212324,
    132: 0.269086,
    134: 0.104357,
    136: 0.088573,
}
AVAILABLE_ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
MODELS = ("gcn", "jj55")
DMSC_VERSION = "d5c4046b4d4cd715af12f1251fac40b6e25b85d5"
NIST_SOURCE = "https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ascii=ascii&ele=Xe"


def oscillator_length_fm(A: int) -> float:
    """AFH default oscillator length, documented in arXiv:1308.6288, Sec. 7.2.

    AFH's SetIsotope[..., bFM="default", ...] uses
    b[fm] = sqrt(41.467 / (45 A^(-1/3) - 25 A^(-2/3))).
    dmscatter implements the same prescription.
    """
    return math.sqrt(41.467 / (45.0 * A ** (-1.0 / 3.0) - 25.0 * A ** (-2.0 / 3.0)))


def read_ground_state_spin(dres_path: Path) -> float:
    lines = dres_path.read_text(encoding="utf-8").splitlines()
    state_idx = next(i for i, line in enumerate(lines) if "State" in line and "Ex" in line)
    for line in lines[state_idx + 1:]:
        fields = line.split()
        if len(fields) >= 5 and fields[0] == "1":
            return float(fields[3])
    raise RuntimeError("Could not read ground-state J from " + str(dres_path))


def run_dmscatter_response(
    dmscatter_root: Path,
    A: int,
    model: str,
    output_root: Path,
) -> dict:
    dres = dmscatter_root / "targets" / "Xe" / ("xe" + str(A) + model + ".dres")
    if not dres.exists():
        raise FileNotFoundError(dres)

    J = read_ground_state_spin(dres)
    b_fm = oscillator_length_fm(A)
    b_gev_inv = b_fm * FM_TO_GEV_INV
    # dmscatter includes both endpoints: N = (q_max-q_min)/dq + 1.
    n_q = int(round((Q_MAX_GEV - Q_MIN_GEV) / Q_STEP_GEV)) + 1
    q_expected = Q_MIN_GEV + np.arange(n_q, dtype=float) * Q_STEP_GEV

    workdir = output_root / "raw_runs" / ("xe" + str(A) + "_" + model)
    workdir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(dmscatter_root / "python"))
    import dmscatter as dm  # imported after the pinned repository is built

    old_cwd = Path.cwd()
    try:
        os.chdir(workdir)
        # Explicitly set the AFH Sec. 7.2 default b(A) prescription, so the
        # run is fully specified in its control file rather than relying on
        # an implicit executable default.
        Wfunc = dm.NucFormFactor(
            Z=Z_XE,
            N=A - Z_XE,
            # dmscatter's Python wrapper expects the density-matrix stem
            # without the trailing ".dres" extension.
            dres=str(dres.with_suffix("")),
            controlwords={
                "usemomentum": 1,
                "pnresponse": 1,
                "fillnuclearcore": 1,
                "hoparameter": b_fm,
            },
            epmin=Q_MIN_GEV,
            epmax=Q_MAX_GEV,
            epstep=Q_STEP_GEV,
            exec_path=str(dmscatter_root / "bin" / "dmscatter"),
            name=".anand_wm_" + str(A) + "_" + model,
            debug=True,
        )
        raw_file = workdir / "nucresponse_spectra.dat.old"
        if not raw_file.exists():
            raise RuntimeError("dmscatter did not leave the raw response file")
        raw = np.loadtxt(raw_file, comments="#")
        # Output columns: q, then 4 p/n channels for M, then 4 for each
        # subsequent nuclear response. Fortran ordering is (tau,tau').
        if raw.ndim != 2 or raw.shape[1] != 33:
            raise RuntimeError("Unexpected dmscatter response shape: " + str(raw.shape))
        q = raw[:, 0]
        if len(q) != n_q or not np.allclose(q, q_expected, rtol=0, atol=2e-10):
            raise RuntimeError("Unexpected q grid returned by dmscatter")
        wm_pn = raw[:, 1:5]
        wm_coherent = wm_pn.sum(axis=1)
        R = (4.0 * math.pi / (2.0 * J + 1.0)) * wm_coherent

        # Cross-check the Python wrapper's indexing against the raw Fortran
        # output at q=0.  Wfunc returns [operator,tau,tau_prime].
        wrapper_zero = np.asarray(Wfunc(0.0))[0].reshape(4, order="F")
        if not np.allclose(wrapper_zero, wm_pn[0], rtol=2e-7, atol=2e-8):
            raise RuntimeError("NucFormFactor wrapper/raw output ordering mismatch")
    finally:
        os.chdir(old_cwd)

    expected_zero = float(A * A)
    zero_relerr = abs(float(R[0]) / expected_zero - 1.0)
    cross_sym_relerr = abs(float(wm_pn[0, 1] - wm_pn[0, 2])) / max(
        1.0, abs(float(wm_pn[0, 1])), abs(float(wm_pn[0, 2]))
    )

    result = {
        "A": A,
        "model": model,
        "J": J,
        "b_fm": b_fm,
        "b_GeV_inv": b_gev_inv,
        "q_GeV": q,
        "W_M_pn_channels": wm_pn,
        "W_M_coherent_pn_sum": wm_coherent,
        "R_A": R,
        "R0": float(R[0]),
        "A2": expected_zero,
        "R0_relative_error": zero_relerr,
        "pn_np_symmetry_relative_error_at_q0": cross_sym_relerr,
        "raw_file": raw_file,
    }
    return result


def recoil_keV_from_q(q_GeV: np.ndarray | float, mA_GeV: float) -> np.ndarray:
    q = np.asarray(q_GeV, dtype=float)
    return (np.sqrt(mA_GeV * mA_GeV + q * q) - mA_GeV) * 1.0e6


def q_from_recoil_keV(ER_keV: np.ndarray | float, mA_GeV: float) -> np.ndarray:
    ER = np.asarray(ER_keV, dtype=float) * 1.0e-6
    return np.sqrt(2.0 * mA_GeV * ER + ER * ER)


def find_response_minima(result: dict) -> list[dict]:
    q = result["q_GeV"]
    R = result["R_A"]
    R0 = result["R0"]
    peaks, _ = find_peaks(-R, prominence=max(R0 * 1e-6, 1e-12), distance=12)
    spline = PchipInterpolator(q, R)
    minima = []
    for idx in peaks:
        if not (0.08 <= q[idx] <= 0.50):
            continue
        lo, hi = q[idx - 1], q[idx + 1]
        opt = minimize_scalar(lambda x: float(spline(x)), bounds=(lo, hi), method="bounded")
        qmin = float(opt.x)
        rmin = float(spline(qmin))
        A = result["A"]
        mA = A * 0.93149410242
        minima.append({
            "A": A,
            "model": result["model"],
            "q_min_MeV": qmin * 1000.0,
            "ER_min_keV": float(recoil_keV_from_q(qmin, mA)),
            "R_min_over_R0": rmin / R0,
        })
    return minima


def write_response_csv(path: Path, result: dict) -> None:
    A = result["A"]
    mA = A * 0.93149410242
    q = result["q_GeV"]
    ER = recoil_keV_from_q(q, mA)
    y = (q * result["b_GeV_inv"] / 2.0) ** 2
    ratio = result["R_A"] / result["R0"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "q_GeV", "ER_keV_using_A_u", "y=(q*b/2)^2",
            "W_M_pp", "W_M_np", "W_M_pn", "W_M_nn",
            "W_M_coherent_sum", "R_A=4pi/(2J+1)*W_M00", "R_A_over_R_A0",
        ])
        for i in range(len(q)):
            writer.writerow([
                f"{q[i]:.10g}", f"{ER[i]:.10g}", f"{y[i]:.10g}",
                *[f"{v:.12g}" for v in result["W_M_pn_channels"][i]],
                f"{result['W_M_coherent_pn_sum'][i]:.12g}",
                f"{result['R_A'][i]:.12g}", f"{ratio[i]:.12g}",
            ])


def write_summary_csv(path: Path, rows: list[dict]) -> None:
    fields = ["A", "model", "J", "b_fm", "R0", "A2", "R0_relative_error",
              "pn_np_symmetry_relative_error_at_q0"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in fields})


def write_minima_csv(path: Path, minima: list[dict]) -> None:
    fields = ["A", "model", "q_min_MeV", "ER_min_keV", "R_min_over_R0"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(minima)


def make_plots(results: dict, natural: dict, output_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8.2, 5.4))
    for model in MODELS:
        r = results[(131, model)]
        ER = recoil_keV_from_q(r["q_GeV"], 131 * 0.93149410242)
        ax.plot(ER, r["R_A"] / r["R0"], label="Xe-131 " + model.upper())
    for x in (101.0, 267.0, 542.0):
        ax.axvline(x, linestyle=":", linewidth=0.9)
    ax.set_xlim(0, 800)
    ax.set_ylim(1e-7, 2)
    ax.set_yscale("log")
    ax.set_xlabel(r"$E_R$ [keV]")
    ax.set_ylabel(r"$\mathcal{R}_{131}(E_R)/\mathcal{R}_{131}(0)$")
    ax.legend()
    ax.grid(True, which="both", alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_dir / "xe131_GCN_vs_JJ55_WM.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.2, 5.4))
    ER = natural["ER_keV"]
    for model in MODELS:
        ax.plot(ER, natural[model]["R_norm"], label="Natural Xe " + model.upper())
    for x in (101.0, 267.0, 542.0):
        ax.axvline(x, linestyle=":", linewidth=0.9)
    ax.set_xlim(0, 800)
    ax.set_ylim(1e-7, 2)
    ax.set_yscale("log")
    ax.set_xlabel(r"$E_R$ [keV]")
    ax.set_ylabel(r"$\mathcal{R}_{\rm mix}(E_R)/\mathcal{R}_{\rm mix}(0)$")
    ax.legend()
    ax.grid(True, which="both", alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_dir / "natural_xenon_GCN_vs_JJ55_WM.png", dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dmscatter-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    dmscatter_root = args.dmscatter_root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    q_grid = Q_MIN_GEV + np.arange(
        int(round((Q_MAX_GEV - Q_MIN_GEV) / Q_STEP_GEV)) + 1, dtype=float
    ) * Q_STEP_GEV

    results = {}
    summary_rows = []
    all_minima = []
    dip_rows = []
    for A in AVAILABLE_ISOTOPES:
        for model in MODELS:
            print("Computing Xe-" + str(A) + " " + model.upper(), flush=True)
            result = run_dmscatter_response(dmscatter_root, A, model, output)
            results[(A, model)] = result
            write_response_csv(
                output / ("xe" + str(A) + "_" + model.upper() + "_WM.csv"), result
            )
            summary_rows.append({
                "A": A,
                "model": model.upper(),
                "J": result["J"],
                "b_fm": result["b_fm"],
                "R0": result["R0"],
                "A2": result["A2"],
                "R0_relative_error": result["R0_relative_error"],
                "pn_np_symmetry_relative_error_at_q0":
                    result["pn_np_symmetry_relative_error_at_q0"],
            })
            all_minima.extend(find_response_minima(result))

    write_summary_csv(output / "zero_momentum_normalization.csv", summary_rows)
    write_minima_csv(output / "response_minima.csv", all_minima)

    # Directly compare the three dip energies previously read from Figure 2.
    for model in MODELS:
        r = results[(131, model)]
        interp = PchipInterpolator(r["q_GeV"], r["R_A"])
        for ER_keV in (101.0, 267.0, 542.0):
            q = float(q_from_recoil_keV(ER_keV, 131 * 0.93149410242))
            dip_rows.append({
                "A": 131,
                "model": model.upper(),
                "figure2_ER_keV": ER_keV,
                "q_MeV": q * 1000.0,
                "R_over_R0": float(interp(q)) / r["R0"],
            })
    with (output / "figure2_dip_energy_check.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=["A", "model", "figure2_ER_keV", "q_MeV", "R_over_R0"]
        )
        writer.writeheader()
        writer.writerows(dip_rows)

    # Abundance-weighted nuclear-response-only mixture.  We use amount
    # fractions x_i.  Xe-124 and Xe-126 (0.1842 atom %) are not available in
    # the dmscatter target library; absolute weights are therefore left
    # unrenormalized, while a separately normalized shape is also recorded.
    ER_grid = np.arange(0.0, ER_MAX_KEV + 0.5 * ER_STEP_KEV, ER_STEP_KEV)
    natural = {"ER_keV": ER_grid}
    abundance_sum_available = sum(NATURAL_ABUNDANCE[A] for A in AVAILABLE_ISOTOPES)
    for model in MODELS:
        R_mix = np.zeros_like(ER_grid)
        for A in AVAILABLE_ISOTOPES:
            r = results[(A, model)]
            mA = A * 0.93149410242
            q_i = q_from_recoil_keV(ER_grid, mA)
            interp = PchipInterpolator(r["q_GeV"], r["R_A"])
            R_mix += NATURAL_ABUNDANCE[A] * interp(q_i)
        R_mix_norm = R_mix / R_mix[0]
        natural[model] = {
            "R_raw": R_mix,
            "R_norm": R_mix_norm,
            "R0": float(R_mix[0]),
        }
        with (output / ("natural_xenon_" + model.upper() + "_WM.csv")).open(
            "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            writer.writerow([
                "ER_keV", "R_mix_available_abundance_unrenormalized",
                "R_mix_over_R_mix0",
            ])
            for E, v, vn in zip(ER_grid, R_mix, R_mix_norm):
                writer.writerow([f"{E:.8g}", f"{v:.12g}", f"{vn:.12g}"])

    make_plots(results, natural, output)

    metadata = {
        "dmscatter_repository": "https://github.com/ogorton/dmscatter",
        "dmscatter_commit": DMSC_VERSION,
        "nuclear_response_reference": "Anand, Fitzpatrick and Haxton, arXiv:1308.6288",
        "NIST_xenon_abundance_source": NIST_SOURCE,
        "response_definition": "R_A = 4*pi/(2J_A+1) * sum_{p,n;p,n} W_M^{ab}; equal proton/neutron coupling",
        "zero_momentum_check": "R_A(0)=A^2",
        "dmscatter_pnresponse": 1,
        "fill_nuclear_core": 1,
        "oscillator_length_prescription": "Anand, Fitzpatrick and Haxton, arXiv:1308.6288, Sec. 7.2 (SetIsotope default), explicitly repeated as hoparameter; dmscatter implements the same formula",
        "oscillator_length_formula": "b_A[fm] = sqrt(41.467 / (45 A^(-1/3) - 25 A^(-2/3)))",
        "oscillator_length_source_location": "AFH arXiv:1308.6288v1, Sec. 7.2, SetIsotope documentation, PDF p.24",
        "q_grid_GeV": [Q_MIN_GEV, Q_MAX_GEV, Q_STEP_GEV],
        "recoil_grid_keV": [0.0, ER_MAX_KEV, ER_STEP_KEV],
        "natural_xenon_available_isotopes": list(AVAILABLE_ISOTOPES),
        "natural_xenon_available_amount_fraction": abundance_sum_available,
        "natural_xenon_omitted_isotopes": [124, 126],
        "natural_xenon_omitted_amount_fraction": 1.0 - abundance_sum_available,
        "natural_mixture_note": "Response-only isotope mixture; not the full isotope-summed three-body event rate.",
        "figure2_dip_energies_keV": [101.0, 267.0, 542.0],
        "caveats": [
            "The manuscript does not specify the Xe isotope mixture or b_A; this reproduction adopts the AFH Sec. 7.2 default b(A) prescription.",
            "The AFH default is a literature-defined reference choice, not a claim that the original Figure 2 calculation used an undocumented identical input.",
            "Xe-124 and Xe-126 are absent from the pinned dmscatter target library.",
            "The mixture combines only the nuclear response factor at fixed E_R; full isotope-specific kinematics and the three-body integral must be evaluated before calling it a natural-xenon event-rate spectrum.",
        ],
    }
    (output / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    # Human-readable run report.
    lines = [
        "# Anand W_M response reproduction",
        "",
        "## Scope",
        "",
        "This run computes only the nuclear response factor. It does not compute",
        "the three-body phase-space/matrix-element integral or the halo integral.",
        "",
        "## Xe-131 zero-momentum normalization",
        "",
        "| Model | J | b [fm] | R_A(0) | A^2 | Relative error |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        if row["A"] == 131:
            lines.append(
                "| {model} | {J:g} | {b_fm:.6f} | {R0:.8g} | {A2:.0f} | {R0_relative_error:.3e} |".format(**row)
            )
    lines += [
        "",
        "## Xe-131 response minima",
        "",
        "| Model | q_min [MeV] | E_R,min [keV] | R_min/R(0) |",
        "|---|---:|---:|---:|",
    ]
    for row in all_minima:
        if row["A"] == 131:
            lines.append(
                "| {model} | {q_min_MeV:.4f} | {ER_min_keV:.3f} | {R_min_over_R0:.4e} |".format(**row)
            )
    lines += [
        "",
        "## Figure 2 dip-energy points",
        "",
        "| Model | Figure 2 E_R [keV] | q [MeV] | R_A/R_A(0) |",
        "|---|---:|---:|---:|",
    ]
    for row in dip_rows:
        lines.append(
            "| {model} | {figure2_ER_keV:.0f} | {q_MeV:.3f} | {R_over_R0:.4e} |".format(**row)
        )
    lines += [
        "",
        "## Natural xenon",
        "",
        "The abundance-weighted response-only mixture includes Xe-128, 129, 130,",
        "131, 132, 134 and 136, covering {:.5f}% of the NIST natural amount fraction.".format(
            100.0 * abundance_sum_available
        ),
        "Xe-124 and Xe-126 (combined {:.4f}%) are absent from the pinned dmscatter target library.".format(
            100.0 * (1.0 - abundance_sum_available)
        ),
        "The mixture is not the full three-body event rate: isotope-specific",
        "m_A prefactors, kinematic limits and three-body integrals still need",
        "to be applied before the halo fold.",
        "",
        "## Input prescription",
        "",
        "The oscillator length follows the default prescription explicitly",
        "documented by Anand, Fitzpatrick and Haxton, arXiv:1308.6288, Sec. 7.2:",
        "b_A[fm] = sqrt(41.467 / (45 A^(-1/3) - 25 A^(-2/3))).",
        "The same formula is implemented by dmscatter and is explicitly supplied",
        "in each control file. The original target manuscript does not state b_A;",
        "we adopt the AFH literature default rather than fit b_A to Figure 2.",
        "",
        "See metadata.json and the raw_runs directory for provenance.",
    ]
    (output / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Finished. Results written to " + str(output), flush=True)
    print("Available xenon abundance fraction: {:.6f}".format(abundance_sum_available), flush=True)


if __name__ == "__main__":
    main()
