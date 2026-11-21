"""Separate nucleon form factors from Xe-131 AFH responses. B is the reference."""
from __future__ import annotations

import json
import math
import platform
import sys
from importlib.metadata import version
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import scipy

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
REPO = STUDY.parents[1]
OUT = HERE / "output"
sys.path.insert(0, str(STUDY))
import compare_responses as phase

FORM_FACTORS = phase.ff
TENSOR_TABLE = STUDY / "results/differential_cross_sections.csv"
TENSOR_MANIFEST = STUDY / "results/run_manifest.json"
NATIVE = STUDY / "inputs/afh_v6_xe131_eight_response_native.csv"
ANCHORS = (200., 267., 269., 300., 500.)
NAMES = ("A", "B", "C", "D", "paper")


def ratio(numerator, denominator):
    """A zero denominator leaves an undefined entry, including both endpoints."""
    x, y = np.broadcast_arrays(np.asarray(numerator, float), np.asarray(denominator, float))
    return np.divide(x, y, out=np.full(y.shape, np.nan), where=y != 0.)


def charge_coefficients(q_squared, f1, f2):
    """f1 and f2 are nucleon F1 and F2 divided by the quark charge F1(0)=3."""
    spin_orbit = q_squared * (f1 + 2 * f2) / (4 * FORM_FACTORS.M_N_GEV**2)
    return f1 - .5 * spin_orbit, spin_orbit


def evaluate():
    provenance = json.loads(TENSOR_MANIFEST.read_text(encoding="utf-8"))
    expected = provenance["sha256"]["results/differential_cross_sections.csv"]
    if phase.hash_file(TENSOR_TABLE) != expected:
        raise ValueError("Archived tensor table differs from its verified SHA-256")
    tensor = pd.read_csv(TENSOR_TABLE, float_precision="round_trip")
    q_grid, nuclear_grid, nuclear_at_q, c0 = phase.load_nuclear()
    meta = pd.read_csv(NATIVE, usecols=["q_GeV", "y"], float_precision="round_trip")
    b_over_two_squared = float(meta.y.iloc[-1] / meta.q_GeV.iloc[-1]**2)
    np.testing.assert_allclose(meta.y, b_over_two_squared * q_grid**2, rtol=2e-14, atol=1e-14)

    er = tensor.ER_keV.to_numpy() * 1e-6
    q = tensor.Q_A_GeV.to_numpy()
    q_squared = q**2
    np.testing.assert_allclose(q_squared, er * (2 * phase.MA + er), rtol=3e-15)
    nuclear = nuclear_at_q(q)
    native = tensor.response_sampling.eq("exact_native_q_node").to_numpy()
    index = np.searchsorted(q_grid, q[native])
    index = np.where(abs(q_grid[index] - q[native]) < abs(q_grid[index-1] - q[native]), index, index-1)
    np.testing.assert_allclose(q[native], q_grid[index], rtol=3e-15, atol=3e-16)
    nuclear[native] = nuclear_grid[index]
    wm, w_sigma2, w_sigma1, w_phi, w_phit, w_delta, w_mphi, w_sigdelta = nuclear.T

    # Each F is a one-nucleon input. Each R is a nuclear matrix-element response.
    f1_zero, f2_zero = FORM_FACTORS.isoscalar_zexp(0.)
    f1_nucleon, f2_nucleon = np.array([FORM_FACTORS.isoscalar_zexp(x) for x in q_squared]).T
    f1, f2 = f1_nucleon / f1_zero, f2_nucleon / f1_zero
    c_static, _ = charge_coefficients(q_squared, 1., f2_zero / f1_zero)
    c_finite, c_phi = charge_coefficients(q_squared, f1, f2)
    charge_m = c_finite**2 * wm
    charge_mphi = 2 * c_finite * c_phi * w_mphi
    charge_phi = c_phi**2 * w_phi
    charge = charge_m + charge_mphi + charge_phi

    q_over_m_squared = q_squared / FORM_FACTORS.M_N_GEV**2
    transverse_delta = q_over_m_squared * f1**2 * w_delta / 2
    transverse_sigma = q_over_m_squared * (f1 + f2)**2 * w_sigma1 / 8
    transverse_mixed = -q_over_m_squared * f1 * (f1 + f2) * w_sigdelta / 2
    transverse = transverse_delta + transverse_sigma + transverse_mixed

    temporal = tensor.L00_GeV2.to_numpy()
    coulomb = tensor.LC_GeV2.to_numpy()
    leptonic_t = tensor.LT_GeV2.to_numpy()
    prefactor = phase.CONVERT * phase.MA * phase.GPROD2 / (
        256 * np.pi**3 * phase.PCHI**2 * (phase.MV**2 + 2 * phase.MA * er)**2)
    cross_sections = {
        "A": prefactor * temporal * c_static**2 * wm,
        "B": prefactor * temporal * charge_m,
        "C": prefactor * temporal * charge,
        "D": prefactor * (coulomb * charge + leptonic_t * transverse),
    }
    # The current manuscript writes y=b^2 mA ER/2 and R_M(0)=A^2. Keep this
    # separate from A-D, which use the exact common spatial recoil Q_A.
    paper_q_squared = 2 * phase.MA * er
    paper_wm = nuclear_at_q(np.sqrt(paper_q_squared))[:, 0]
    cross_sections["paper"] = prefactor * temporal * paper_wm

    data = tensor[["benchmark", "ms_keV", "delta_m_MeV", "ER_keV", "phase_space_open",
                   "response_sampling", "Q_A_GeV"]].copy()
    for name, values in cross_sections.items():
        data[f"{name}_cm2_per_keV"] = values
        data[f"{name}_over_B"] = ratio(values, cross_sections["B"])
    data["B_over_A"] = ratio(cross_sections["B"], cross_sections["A"])
    data["D_over_C"] = ratio(cross_sections["D"], cross_sections["C"])
    # Evaluate the small spatial correction before summing it into the large C term.
    data["longitudinal_over_C_ppm"] = 1e6 * ratio(tensor.deltaLC_GeV2, temporal)
    data["transverse_over_C_ppm"] = 1e6 * ratio(leptonic_t * transverse, temporal * charge)
    data["D_over_C_minus_1_ppm"] = data.longitudinal_over_C_ppm + data.transverse_over_C_ppm
    data["C_minus_B_over_B_percent"] = 100 * ratio(temporal * (charge_mphi + charge_phi), temporal * charge_m)
    data["t_N_GeV2_static"] = -q_squared
    data["t_A_GeV2"] = -paper_q_squared
    data["y_A"] = b_over_two_squared * q_squared
    data["y_paper"] = b_over_two_squared * paper_q_squared
    data["F1V_N_tN"], data["F2V_N_tN"] = f1_nucleon, f2_nucleon
    data["cM_A"], data["cM_B"], data["cPhi_C"] = c_static, c_finite, c_phi
    for i, channel in enumerate(phase.CHANNELS):
        data[f"R_{channel}"] = nuclear[:, i]
    data["R_M_paper"] = paper_wm
    data["charge_M"], data["charge_MPhiPP"], data["charge_PhiPP"] = charge_m, charge_mphi, charge_phi
    data["transverse_Delta"] = transverse_delta
    data["transverse_SigmaPrime"] = transverse_sigma
    data["transverse_SigmaPrimeDelta"] = transverse_mixed

    opened = data.phase_space_open
    closed = data.loc[~opened]
    ratios = [f"{n}_over_B" for n in NAMES] + ["B_over_A", "D_over_C", "D_over_C_minus_1_ppm"]
    absolute = [f"{n}_cm2_per_keV" for n in NAMES]
    if len(closed) != 8 or (closed[absolute] != 0).any().any() or not closed[ratios].isna().all().all():
        raise ArithmeticError("Closed endpoints must have zero cross section and undefined ratios")
    if not np.all(np.isfinite(data.loc[opened, absolute])) or (data.loc[opened, absolute] <= 0).any().any():
        raise ArithmeticError("Invalid open-phase-space cross section")
    np.testing.assert_array_equal(data.loc[opened, "B_over_B"], np.ones(opened.sum()))

    # Reproduce the previous independently tested C/D spectra with the archived tensor.
    def max_relative(values, references):
        values, references = np.asarray(values, float), np.asarray(references, float)
        return float(np.max(abs(values[opened] / references[opened] - 1)))

    errors = {
        "manuscript_eq6_over_B_vs_nuclear_ratio": max_relative(
            data.paper_over_B, ratio(paper_wm, c_finite**2 * wm)),
        "C_vs_prior_time_only": max_relative(cross_sections["C"], tensor.time_only_cm2_per_keV),
        "D_vs_prior_one_body": max_relative(cross_sections["D"], tensor.full_candidate_cm2_per_keV),
        "A_vs_prior_leading_common_q_times_cM_static_squared":
            max_relative(cross_sections["A"], tensor.paper_cm2_per_keV * c_static**2),
        "B_vs_prior_leading_common_q_times_cM_finite_squared":
            max_relative(cross_sections["B"], tensor.paper_cm2_per_keV * c_finite**2),
        "C_over_B_vs_analytic_charge_ratio": max_relative(
            data.C_over_B, 1 + 2 * c_phi/c_finite * w_mphi/wm + (c_phi/c_finite)**2 * w_phi/wm),
        "A_over_B_vs_coefficient_ratio": max_relative(data.A_over_B, (c_static/c_finite)**2),
    }
    if max(errors.values()) > 5e-12:
        raise ArithmeticError(f"Cross-section/response factorization failed: {errors}")
    np.testing.assert_allclose(data.loc[opened, "D_over_C"] - 1,
                               data.loc[opened, "D_over_C_minus_1_ppm"] * 1e-6, atol=2e-15)
    np.testing.assert_allclose(charge_coefficients(0, 1., f2_zero/f1_zero), (1., 0.), atol=1e-15)
    # Repository native four-benchmark archive is defined at exact Q_A.
    reference = pd.read_csv(STUDY / "results/native_baseline_comparison.csv", float_precision="round_trip")
    matches = reference.merge(data[opened], on=["benchmark", "ER_keV"], validate="one_to_one")
    native_b = matches.native_cm2_per_keV * matches.cM_B**2
    native_b_error = float(np.max(abs(matches.B_cm2_per_keV/native_b - 1)))
    if len(matches) != 12 or native_b_error > 2e-7:
        raise ArithmeticError("Independent native M-only anchor check failed")
    anchors = data.loc[data.ER_keV.isin(ANCHORS) & opened]
    if not np.all(anchors.groupby("ER_keV").size() == len(phase.BENCHMARKS)):
        raise ArithmeticError("Benchmark comparison is missing a common energy")
    for _, group in anchors.groupby("ER_keV"):
        np.testing.assert_allclose(group.A_over_B, group.A_over_B.iloc[0], rtol=3e-14)
        np.testing.assert_allclose(group.C_over_B, group.C_over_B.iloc[0], rtol=3e-14)
    checks = {
        "rows": len(data), "open_rows": int(opened.sum()), "closed_endpoints": len(closed),
        "max_relative_residuals_on_open_grid": errors, "native_reweighted_B_anchors": len(matches),
        "max_relative_residual_B_vs_native_M_reweighted": native_b_error,
        "R_M_at_zero": float(nuclear_grid[0, 0]), "C0": c0,
        "b_A_GeV_inverse": 2 * math.sqrt(b_over_two_squared),
        "F1V_N_at_zero": f1_zero, "F2V_N_at_zero": f2_zero,
        "max_relative_effect_of_paper_y_vs_exact_Q_on_leading_paper_curve":
            max_relative(cross_sections["paper"], tensor.paper_cm2_per_keV),
        "tensor_crosscheck": {
            k: provenance[k] for k in ("maximum_native_absolute_baseline_relative_difference",
                                       "maximum_quadrature_relative_difference",
                                       "maximum_independent_integrated_tensor_relative_difference")
        }
    }
    return data, checks


def main():
    data, checks = evaluate()
    OUT.mkdir(parents=True, exist_ok=True)
    data.to_csv(OUT / "abcd_cross_sections.csv", index=False, float_format="%.17g", lineterminator="\n")
    focus_columns = ["benchmark", "ms_keV", "delta_m_MeV", "ER_keV"]
    focus_columns += [f"{name}_cm2_per_keV" for name in NAMES]
    focus_columns += [f"{name}_over_B" for name in NAMES]
    focus_columns += ["B_over_A", "C_minus_B_over_B_percent", "D_over_C", "D_over_C_minus_1_ppm",
                      "longitudinal_over_C_ppm", "transverse_over_C_ppm"]
    focus = data.loc[data.ER_keV.isin(ANCHORS), focus_columns]
    focus.to_csv(OUT / "selected_energies.csv", index=False, float_format="%.12g", lineterminator="\n")
    from figures_abcd import draw_figures
    draw_figures(data, OUT)
    prior = json.loads(TENSOR_MANIFEST.read_text(encoding="utf-8"))
    manifest = {
        "calculation_reference": "B", "target": "Xe-131", "research_status": "leading one-body vector current candidate",
        "prescriptions": {
            "A": "F1(0),F2(0) in matched cM_A at finite Q_A; L00 times cM_A^2 R_M",
            "B": "finite-t_N F1,F2 in cM_B; L00 times cM_B^2 R_M; reference for all main ratios",
            "C": "B plus the Phi-double-prime diagonal and signed M-Phi-double-prime interference, only J0",
            "D": "C with nuclear charge-longitudinal continuity and three signed transverse terms, six allowed terms",
            "paper": ("Current manuscript leading-order recoil equation, evaluated with each panel's inputs: "
                      "S6 = P L00 * 131^2 W_M^00(y6)/W_M^00(0), normalized cM=1, only J0, "
                      "y6=b_A^2 m_A E_R/2. Gray open diamonds show S6 or S6/S_B. "
                      "S6/S_B = W_M^00(y6) / [cM_B^2 W_M^00(y_A)].")},
        "parameters": prior["parameters"], "width": prior["width"], "widths_keV": prior["widths_keV"],
        "benchmarks": phase.BENCHMARKS, "kinematic_intervals_keV": prior["recoil_intervals_keV"],
        "form_factors": prior["form_factors"], "nuclear_responses": "native AFH v6, equal p/n, common C0",
        "particle_current_matching_sha": prior["matching_source_commit"],
        "time_components": "A,B,C and paper use target-rest L00; D uses LC and LT",
        "scope": "fixed speed, single isotope; D uses leading static impulse one-body matching; bound-nucleus amplitude matching remains open",
        "numerical_checks": checks,
        "environment": dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                            pandas=pd.__version__, matplotlib=matplotlib.__version__,
                            reportlab=version("reportlab"), pypdf=version("pypdf")),
        "reproduction": "python -B research/response_comparison_four_benchmarks/ABCD/run_comparison.py",
    }
    from combined_pdf import write_combined_pdf
    write_combined_pdf(data, manifest, OUT / "pdf/xe131_cross_sections_and_ratios.pdf")
    sources = (TENSOR_TABLE, TENSOR_MANIFEST, NATIVE, STUDY/"inputs/provenance.json",
               STUDY/"inputs/native-comparison.json", STUDY/"results/native_baseline_comparison.csv",
               STUDY/"compare_responses.py", Path(FORM_FACTORS.__file__), REPO/"paper-source/main.tex",
               Path(__file__).resolve(), HERE/"figures_abcd.py", HERE/"combined_pdf.py", HERE/"README.md")
    manifest["input_and_code_sha256"] = {p.relative_to(REPO).as_posix(): phase.hash_file(p) for p in sources}
    manifest["output_sha256"] = {p.relative_to(OUT).as_posix(): phase.hash_file(p) for p in sorted(OUT.rglob("*"))
                                 if p.is_file() and p.name != "run_manifest.json"}
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
