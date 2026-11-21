#!/usr/bin/env python3
"""Charge-sector M + Phi'' contraction for the three-body VV Xe-131 process.

This is a deliberately restricted contraction: it uses the time component
T_3^0 and the AFH Coulomb multipoles M and Phi''. It is not the full
L_{mu nu} W_A^{mu nu} contraction.
"""
from __future__ import annotations
import argparse, bisect, csv, hashlib, json, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = HERE / "input"
DEFAULT_OUT = HERE / "results" / "2026-11-18"
M_N_GEV = 0.938918
MASS_U_GEV = 0.93149410242
M_A_GEV = 131.0 * MASS_U_GEV
R2_SCENARIOS = (0.0, -0.14, -0.15, -0.17, -0.184)


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def charge_response_terms(q_gev, w_m, w_phi, w_mphi, f2_over_f1, m_n_gev=M_N_GEV):
    """Charge multipole: C_M/F1=1-eta/2, C_Phi/F1=eta."""
    if q_gev < 0 or w_m <= 0 or w_phi < 0:
        raise ValueError("q must be nonnegative, W_M positive, W_Phi'' nonnegative")
    eta = q_gev**2 / (4.0 * m_n_gev**2) * (1.0 + 2.0 * f2_over_f1)
    c_m, c_phi = 1.0 - eta / 2.0, eta
    d_df = c_m**2 - 1.0
    d_int = 2.0 * c_m * c_phi * (w_mphi / w_m)
    d_phi = c_phi**2 * (w_phi / w_m)
    ratio = 1.0 + d_df + d_int + d_phi
    if ratio < -1e-10:
        raise ArithmeticError(f"negative charge response ratio: {ratio}")
    return {
        "eta": eta, "C_M_over_F1": c_m, "C_PhiPP_over_F1": c_phi,
        "delta_Darwin_Foldy": d_df,
        "delta_M_Phi_interference": d_int,
        "delta_PhiPP_square": d_phi,
        "R_charge_over_M": ratio,
    }


def _lagrange(x, points):
    terms = []
    for i, (xi, yi) in enumerate(points):
        term = yi
        for j, (xj, _) in enumerate(points):
            if i != j:
                term *= (x - xj) / (xi - xj)
        terms.append(term)
    return math.fsum(terms)


def interpolate_response(grid, q_gev, order=8):
    """Local polynomial interpolation on the archived uniform AFH q grid."""
    if order < 2 or order % 2:
        raise ValueError("interpolation order must be an even integer >= 2")
    q_values = [float(row["q_GeV"]) for row in grid]
    if not q_values[0] <= q_gev <= q_values[-1]:
        raise ValueError("requested q lies outside AFH grid")
    right = bisect.bisect_left(q_values, q_gev)
    start = max(0, min(len(grid) - order, right - order // 2))
    chosen = grid[start:start + order]
    return {
        key: _lagrange(
            q_gev,
            [(float(row["q_GeV"]), float(row[key])) for row in chosen],
        )
        for key in ("W_M00_AFH", "W_PhiPP_AFH", "W_MPhiPP_AFH")
    }


def validate_grid(grid):
    if len(grid) != 2401:
        raise AssertionError(f"expected 2401 AFH grid points, got {len(grid)}")
    q = [float(row["q_GeV"]) for row in grid]
    steps = [q[i + 1] - q[i] for i in range(len(q) - 1)]
    if max(abs(step - 0.00025) for step in steps) > 2e-12:
        raise AssertionError("AFH q grid is not the archived 0.25-MeV grid")
    max_corr = 0.0
    for row in grid:
        wm, wp, wmp = (float(row[k]) for k in
                       ("W_M00_AFH", "W_PhiPP_AFH", "W_MPhiPP_AFH"))
        if wm <= 0 or wp < 0:
            raise AssertionError("non-positive diagonal AFH response")
        corr = abs(wmp) / math.sqrt(wm * wp) if wp else 0.0
        max_corr = max(max_corr, corr)
        if corr > 1.0 + 2e-6:
            raise AssertionError(f"Cauchy-Schwarz violation: {corr}")
    return {"points": len(grid), "q_min_GeV": q[0], "q_max_GeV": q[-1],
            "dq_GeV": steps[0], "max_interference_correlation": max_corr}


def scenario_tag(value):
    if abs(value) < 1e-15:
        return "r2_zero"
    return "r2_" + ("p" if value > 0 else "m") + f"{abs(value):.3f}".replace(".", "p")


def make_grid_output(grid):
    output = []
    for row in grid:
        q = float(row["q_GeV"])
        wm, wp, wmp = (float(row[k]) for k in
                       ("W_M00_AFH", "W_PhiPP_AFH", "W_MPhiPP_AFH"))
        item = {"q_GeV": q, "ER_keV": float(row["ER_keV"]),
                "q_over_mN": q / M_N_GEV, "W_M00_AFH_raw": wm,
                "W_PhiPP_AFH_raw": wp, "W_MPhiPP_AFH_raw": wmp,
                "W_PhiPP_over_W_M": wp / wm, "W_MPhiPP_over_W_M": wmp / wm}
        for r2 in R2_SCENARIOS:
            tag = scenario_tag(r2)
            terms = charge_response_terms(q, wm, wp, wmp, r2)
            item[f"{tag}_eta"] = terms["eta"]
            item[f"{tag}_R_charge_over_M"] = terms["R_charge_over_M"]
            item[f"{tag}_delta_total_percent"] = 100.0 * (terms["R_charge_over_M"] - 1.0)
        output.append(item)
    return output


def make_benchmark_output(grid, pr53):
    output = []
    for row in pr53:
        if row["phase_space_open"].lower() != "true":
            continue
        q = float(row["qA_GeV"])
        resp8, resp6 = interpolate_response(grid, q, 8), interpolate_response(grid, q, 6)
        wm, wp, wmp = (resp8[k] for k in ("W_M00_AFH", "W_PhiPP_AFH", "W_MPhiPP_AFH"))
        if wm <= 0 or wp < 0:
            raise ArithmeticError("interpolated AFH response left physical domain")
        for r2 in R2_SCENARIOS:
            terms = charge_response_terms(q, wm, wp, wmp, r2)
            r6 = charge_response_terms(
                q, resp6["W_M00_AFH"], resp6["W_PhiPP_AFH"],
                resp6["W_MPhiPP_AFH"], r2
            )["R_charge_over_M"]
            output.append({
                "benchmark": row["benchmark"], "width_scheme": row["width_scheme"],
                "g2": float(row["g2"]), "ER_keV": float(row["ER_keV"]),
                "qA_GeV": q, "I00_M_only_kernel": float(row["I00"]),
                "F2_over_F1_scenario": r2, "W_M00_AFH_interpolated": wm,
                "W_PhiPP_AFH_interpolated": wp, "W_MPhiPP_AFH_interpolated": wmp,
                "W_PhiPP_over_W_M": wp / wm, "W_MPhiPP_over_W_M": wmp / wm,
                **terms,
                "I00_charge_corrected_kernel": float(row["I00"]) * terms["R_charge_over_M"],
                "interpolation_order6_vs8_abs_delta_R": abs(r6 - terms["R_charge_over_M"]),
                "q_over_mN": q / M_N_GEV,
                "NR_expansion_warning_q_over_mN_gt_0p3": q / M_N_GEV > 0.3,
            })
    return output


def make_exact_minima_output(selected):
    output = []
    for row in selected:
        q = float(row["q_min_MeV"]) / 1000.0
        wm, wp, wmp = (float(row[k]) for k in
                       ("W_M00_AFH", "W_PhiPP_AFH", "W_MPhiPP_AFH"))
        for r2 in R2_SCENARIOS:
            output.append({
                "AFH_point": "exact_selected_WM_minimum", "q_GeV": q,
                "ER_keV": float(row["ER_min_keV"]), "F2_over_F1_scenario": r2,
                "W_M00_AFH_exact": wm, "W_PhiPP_AFH_exact": wp,
                "W_MPhiPP_AFH_exact": wmp, "W_PhiPP_over_W_M": wp / wm,
                "W_MPhiPP_over_W_M": wmp / wm,
                **charge_response_terms(q, wm, wp, wmp, r2),
            })
    return output


def build_summary(grid, benchmark, minima, grid_stats):
    selected = [row for row in benchmark if abs(row["F2_over_F1_scenario"] + 0.184) < 1e-12]
    qwindow = [row for row in make_grid_output(grid) if 0.2 <= row["q_GeV"] <= 0.3]
    key = "r2_m0p184_R_charge_over_M"
    qmin, qmax = min(qwindow, key=lambda x: x[key]), max(qwindow, key=lambda x: x[key])
    return {
        "status": "charge_sector_matched_zero_momentum_form_factor_diagnostic",
        "grid_validation": grid_stats,
        "F2_over_F1_scenarios": list(R2_SCENARIOS),
        "selected_three_body_benchmarks_r2_minus_0p184": [
            {"benchmark": row["benchmark"], "width_scheme": row["width_scheme"],
             "ER_keV": row["ER_keV"], "qA_MeV": row["qA_GeV"] * 1000.0,
             "R_charge_over_M": row["R_charge_over_M"],
             "delta_total_percent": 100.0 * (row["R_charge_over_M"] - 1.0)}
            for row in selected
        ],
        "exact_AFH_minima_r2_minus_0p184": [
            {"qA_MeV": row["q_GeV"] * 1000.0, "ER_keV": row["ER_keV"],
             "R_charge_over_M": row["R_charge_over_M"],
             "delta_total_percent": 100.0 * (row["R_charge_over_M"] - 1.0)}
            for row in minima if abs(row["F2_over_F1_scenario"] + 0.184) < 1e-12
        ],
        "grid_sampled_q_0p2_to_0p3_GeV_r2_minus_0p184": {
            "q_grid_step_MeV": 0.25,
            "minimum": {"qA_MeV": qmin["q_GeV"] * 1000.0,
                        "ER_keV": qmin["ER_keV"],
                        "R_charge_over_M": qmin[key],
                        "delta_total_percent": 100.0 * (qmin[key] - 1.0)},
            "maximum": {"qA_MeV": qmax["q_GeV"] * 1000.0,
                        "ER_keV": qmax["ER_keV"],
                        "R_charge_over_M": qmax[key],
                        "delta_total_percent": 100.0 * (qmax[key] - 1.0)},
            "note": "grid-sampled extrema, not a continuous minimization",
        },
        "max_abs_interpolation_order6_vs8_delta_R": max(
            (row["interpolation_order6_vs8_abs_delta_R"] for row in benchmark),
            default=0.0,
        ),
        "interpretation_boundary": [
            "The M+Phi'' vector-charge coefficient is derived from the one-nucleon Dirac-Pauli charge expansion.",
            "The exact PR53 T3^0 phase-space kernel is reused; it cancels from the relative charge correction at fixed q_A.",
            "The default F2/F1=-0.184 is the ratio of the adopted zero-momentum flavour benchmark F2^V(0)=-0.552 and F1^V(0)=3; it is not a finite-t fit.",
            "Spatial T3^i terms and the Delta, Sigma', Sigma'' responses remain outside this charge-sector calculation.",
            "Native Mathematica Phi'' cross-check in source PR #54 remains pending.",
            "No complete all-current natural-xenon spectrum, detector response, or likelihood is produced.",
        ],
    }


def run(outdir):
    grid = read_csv(INPUT / "afh_vv_phi_xe131_full_grid_pr54_snapshot.csv")
    selected = read_csv(INPUT / "afh_vv_phi_xe131_selected_points_pr54_snapshot.csv")
    pr53 = read_csv(ROOT / "research/vector_current_response_audit/results/2026-11-18/vector_current_response_audit.csv")
    stats = validate_grid(grid)
    grid_output = make_grid_output(grid)
    benchmark_output = make_benchmark_output(grid, pr53)
    minima_output = make_exact_minima_output(selected)
    summary = build_summary(grid, benchmark_output, minima_output, stats)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    write_csv(outdir / "phi_charge_contraction_grid.csv", grid_output)
    write_csv(outdir / "phi_charge_contraction_three_body_benchmarks.csv", benchmark_output)
    write_csv(outdir / "phi_charge_contraction_exact_afh_minima.csv", minima_output)
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    names = ("phi_charge_contraction_grid.csv",
             "phi_charge_contraction_three_body_benchmarks.csv",
             "phi_charge_contraction_exact_afh_minima.csv", "summary.json")
    (outdir / "SHA256SUMS.txt").write_text(
        "\n".join(f"{sha256(outdir / name)}  {name}" for name in names) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": summary["status"], "grid_points": len(grid_output),
                      "three_body_benchmark_rows": len(benchmark_output),
                      "exact_afh_minima_rows": len(minima_output),
                      "max_abs_interpolation_order6_vs8_delta_R":
                          summary["max_abs_interpolation_order6_vs8_delta_R"]}, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    run(args.outdir.resolve())


if __name__ == "__main__":
    main()
