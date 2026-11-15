#!/usr/bin/env python3
"""1/5/10-keV response-grid convergence for the LZ three-body NR signal.

The NEST response samples are stratified in 1-keV true-energy bins. Coarser
5/10-keV response probabilities are reconstructed by width-averaging the
fine-bin conditional probabilities, then folded against the exact integrated
three-body spectrum in each coarse bin. This tests the piecewise-constant
response approximation without rerunning the halo/nuclear calculation.

Two response modes are retained:
  nest_level: NEST S1-coincidence and NEST S2-threshold pass flags.
  nest_plus_ws_roi: nest_level plus the published S1c/S2/S2c WS-ROI bounds.
Neither mode includes the full trigger, SS reconstruction, analysis cuts,
fiducial-volume mask, or Skin/OD veto model.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROI_MIN_KEV = 5.4
ROI_MAX_KEV = 269.9
S1_MIN_PHD = 3.0
S1_MAX_PHD = 600.0
S2_RAW_MIN_PHD = 645.0
LOG10_S2C_MIN = 2.75
LOG10_S2C_MAX = 4.15
S1_BIN_WIDTH_PHD = 10.0
LOG10_S2_BIN_WIDTH = 0.02
GRID_WIDTHS_KEV = (1.0, 5.0, 10.0)
BENCHMARKS = ("red_ms200_dm1", "green_ms300_dm1", "black_ms360_dm1", "blue_ms300_dm10")
NUCLEAR_MODELS = ("GCN", "JJ55")
RESPONSE_FAMILIES = ("eft2024", "tableS5", "ws2024", "generic")
NEST_COMMIT = "541b6430dae6ea289cf110c99f174a9187f7fdee"


def make_edges(lo: float, hi: float, width: float) -> list[float]:
    if not (hi > lo and width > 0.0):
        raise ValueError("require hi > lo and width > 0")
    edges = [lo]
    while edges[-1] + width < hi - 1e-10:
        edges.append(edges[-1] + width)
    if hi - edges[-1] > 1e-10:
        edges.append(hi)
    else:
        edges[-1] = hi
    return edges


def interpolate(x: float, xs: list[float], ys: list[float]) -> float:
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    lo, hi = 0, len(xs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xs[mid] <= x:
            lo = mid
        else:
            hi = mid
    t = (x - xs[lo]) / (xs[hi] - xs[lo])
    return ys[lo] + t * (ys[hi] - ys[lo])


def integrate_linear(xs: list[float], ys: list[float], lo: float, hi: float) -> float:
    if not lo < hi:
        return 0.0
    if xs[0] > lo or xs[-1] < hi:
        raise ValueError("spectrum does not cover requested integration interval")
    knots = sorted({lo, hi} | {x for x in xs if lo < x < hi})
    total = 0.0
    for a, b in zip(knots, knots[1:]):
        total += 0.5 * (interpolate(a, xs, ys) + interpolate(b, xs, ys)) * (b - a)
    return total


def read_spectrum(path: Path, nuclear_model: str) -> tuple[list[float], list[float]]:
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["halo_model"] == "shm_cutoff" and r["model"] == nuclear_model:
                rows.append((float(r["ER_keV"]), float(r["rate_events_kg_day_keV"])))
    rows.sort()
    if len(rows) < 2:
        raise ValueError(f"insufficient {nuclear_model} spectrum points in {path}")
    xs, ys = [x for x, _ in rows], [y for _, y in rows]
    if xs[0] > ROI_MIN_KEV or xs[-1] < ROI_MAX_KEV:
        raise ValueError(f"spectrum does not cover full ROI: {path}")
    if any(not math.isfinite(x) for x in xs + ys) or any(y < 0.0 for y in ys):
        raise ValueError(f"non-finite or negative spectrum values in {path}")
    if any(b <= a for a, b in zip(xs, xs[1:])):
        raise ValueError(f"non-increasing spectrum grid in {path}")
    return xs, ys


def cell_key(s1c: float, s2c: float) -> tuple[int, int]:
    s1_bin = math.floor(s1c / S1_BIN_WIDTH_PHD)
    log_s2 = math.log10(s2c)
    log_bin = math.floor(log_s2 / LOG10_S2_BIN_WIDTH + 1e-12)
    return s1_bin, log_bin


def ws_roi_pass(s1c: float, s2r: float, s2c: float) -> bool:
    if not (math.isfinite(s1c) and math.isfinite(s2r) and math.isfinite(s2c)):
        return False
    if s2c <= 0.0:
        return False
    log_s2 = math.log10(s2c)
    return (
        S1_MIN_PHD <= s1c <= S1_MAX_PHD
        and s2r > S2_RAW_MIN_PHD
        and LOG10_S2C_MIN <= log_s2 <= LOG10_S2C_MAX
    )


def read_response(path: Path) -> dict:
    """Stream event samples into (1-keV bin, replica) sufficient statistics."""
    stats = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {
            "replica", "energy_bin_index", "energy_bin_low_keV", "energy_bin_high_keV",
            "s1c_abs_phd", "s1_coincidence_pass", "s2c_abs_phd", "s2r_abs_phd",
            "s2_threshold_pass",
        }
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"{path} missing columns: {sorted(required - set(reader.fieldnames or []))}")
        for row in reader:
            ibin = int(row["energy_bin_index"])
            replica = int(row["replica"])
            key = (ibin, replica)
            if key not in stats:
                stats[key] = {
                    "lo": float(row["energy_bin_low_keV"]),
                    "hi": float(row["energy_bin_high_keV"]),
                    "n": 0,
                    "n_s1_coin": 0,
                    "n_s2_threshold": 0,
                    "n_nest": 0,
                    "n_ws_roi": 0,
                    "nest_cells": defaultdict(int),
                    "roi_cells": defaultdict(int),
                }
            rec = stats[key]
            rec["n"] += 1
            s1c = float(row["s1c_abs_phd"])
            s2c = float(row["s2c_abs_phd"])
            s2r = float(row["s2r_abs_phd"])
            s1_pass = int(row["s1_coincidence_pass"]) == 1
            s2_pass = int(row["s2_threshold_pass"]) == 1
            rec["n_s1_coin"] += int(s1_pass)
            rec["n_s2_threshold"] += int(s2_pass)
            nest_pass = s1_pass and s2_pass
            if not nest_pass:
                continue
            rec["n_nest"] += 1
            key_cell = cell_key(s1c, s2c)
            rec["nest_cells"][key_cell] += 1
            if ws_roi_pass(s1c, s2r, s2c):
                rec["n_ws_roi"] += 1
                rec["roi_cells"][key_cell] += 1
    if not stats:
        raise ValueError(f"empty response sample: {path}")
    return stats


def merge_bin_stats(stats: dict, fine_ids: list[int], replica: int | None) -> dict:
    """Merge fine-bin probabilities, pooling replicas without double-counting energy width."""
    n_generated = 0
    n_s1 = n_s2 = n_nest = n_roi = 0
    weighted_accept = {
        "s1_coin": 0.0, "s2_threshold": 0.0, "nest": 0.0, "ws_roi": 0.0
    }
    weighted_cells = {"nest": defaultdict(float), "ws_roi": defaultdict(float)}
    width_sum = 0.0
    for ibin in fine_ids:
        replicas = (0, 1) if replica is None else (replica,)
        records = []
        for rep in replicas:
            rec = stats.get((ibin, rep))
            if rec is None:
                raise ValueError(f"missing fine-bin/replica statistics: bin={ibin}, replica={rep}")
            records.append(rec)
        width = records[0]["hi"] - records[0]["lo"]
        if any(
            abs((rec["hi"] - rec["lo"]) - width) > 1e-10
            or abs(rec["lo"] - records[0]["lo"]) > 1e-10
            or abs(rec["hi"] - records[0]["hi"]) > 1e-10
            for rec in records[1:]
        ):
            raise ValueError(f"replica energy-bin mismatch for fine bin {ibin}")
        n = sum(rec["n"] for rec in records)
        if n <= 0:
            raise ValueError(f"empty fine energy bin {ibin}")
        width_sum += width
        n_generated += n
        n_s1 += sum(rec["n_s1_coin"] for rec in records)
        n_s2 += sum(rec["n_s2_threshold"] for rec in records)
        n_nest += sum(rec["n_nest"] for rec in records)
        n_roi += sum(rec["n_ws_roi"] for rec in records)

        for mode, cell_key_name in (("nest", "nest_cells"), ("ws_roi", "roi_cells")):
            combined = defaultdict(int)
            for rec in records:
                for cell, count in rec[cell_key_name].items():
                    combined[cell] += count
            for cell, count in combined.items():
                weighted_cells[mode][cell] += width * count / n
        for name, count_key in (
            ("s1_coin", "n_s1_coin"),
            ("s2_threshold", "n_s2_threshold"),
            ("nest", "n_nest"),
            ("ws_roi", "n_ws_roi"),
        ):
            weighted_accept[name] += width * sum(rec[count_key] for rec in records) / n

    if width_sum <= 0.0:
        raise ValueError("zero merged energy width")
    return {
        "width": width_sum,
        "n_generated": n_generated,
        "n_s1_coin": n_s1,
        "n_s2_threshold": n_s2,
        "n_nest": n_nest,
        "n_ws_roi": n_roi,
        "acceptance": {k: v / width_sum for k, v in weighted_accept.items()},
        "cell_probability": {
            mode: {cell: value / width_sum for cell, value in cells.items()}
            for mode, cells in weighted_cells.items()
        },
    }

def fold_grid(
    stats: dict,
    xs: list[float],
    ys: list[float],
    grid_width: float,
    replica: int | None,
) -> dict:
    coarse_edges = make_edges(ROI_MIN_KEV, ROI_MAX_KEV, grid_width)
    fine_edges = sorted({rec["lo"] for rec in stats.values()} | {rec["hi"] for rec in stats.values()})
    # Keep one copy of the energy edges; replicas duplicate the same values.
    fine_edges = sorted(set(fine_edges))
    if abs(fine_edges[0] - ROI_MIN_KEV) > 1e-8 or abs(fine_edges[-1] - ROI_MAX_KEV) > 1e-8:
        raise ValueError("stratified response energy edges do not match ROI")
    fine_bins = [(a, b) for a, b in zip(fine_edges, fine_edges[1:])]
    response_bin_ids = {}
    for ibin in sorted({key[0] for key in stats}):
        rec = stats[(ibin, 0)]
        response_bin_ids[ibin] = (rec["lo"], rec["hi"])

    intensity = {"nest": defaultdict(float), "ws_roi": defaultdict(float)}
    bin_rows = []
    raw_rate = integrate_linear(xs, ys, ROI_MIN_KEV, ROI_MAX_KEV)
    for lo, hi in zip(coarse_edges, coarse_edges[1:]):
        ids = [
            ibin for ibin, (flo, fhi) in response_bin_ids.items()
            if flo >= lo - 1e-8 and fhi <= hi + 1e-8
        ]
        if not ids:
            raise ValueError(f"no response strata in coarse bin [{lo},{hi}]")
        merged = merge_bin_stats(stats, ids, replica)
        if abs(merged["width"] - (hi - lo)) > 1e-7:
            raise ValueError(f"response strata do not exactly cover coarse bin [{lo},{hi}]")
        rate_bin = integrate_linear(xs, ys, lo, hi)
        for mode in ("nest", "ws_roi"):
            for cell, probability in merged["cell_probability"][mode].items():
                intensity[mode][cell] += rate_bin * probability
        bin_rows.append({
            "energy_low_keV": lo,
            "energy_high_keV": hi,
            "rate_integral_events_kg_day": rate_bin,
            "n_generated": merged["n_generated"],
            "n_s1_coincidence_pass": merged["n_s1"],
            "n_s2_threshold_pass": merged["n_s2_threshold"],
            "n_nest_joint_pass": merged["n_nest"],
            "n_ws_roi_pass": merged["n_ws_roi"],
            "s1_coin_acceptance_uniform_energy": merged["acceptance"]["s1_coin"],
            "s2_threshold_acceptance_uniform_energy": merged["acceptance"]["s2_threshold"],
            "nest_acceptance_uniform_energy": merged["acceptance"]["nest"],
            "s2_threshold_given_s1_acceptance": (
                merged["acceptance"]["nest"] / merged["acceptance"]["s1_coin"]
                if merged["acceptance"]["s1_coin"] > 0.0 else 0.0
            ),
            "ws_roi_given_nest_acceptance": (
                merged["acceptance"]["ws_roi"] / merged["acceptance"]["nest"]
                if merged["acceptance"]["nest"] > 0.0 else 0.0
            ),
            "ws_roi_acceptance_uniform_energy": merged["acceptance"]["ws_roi"],
            "nest_rate_events_kg_day": rate_bin * merged["acceptance"]["nest"],
            "ws_roi_rate_events_kg_day": rate_bin * merged["acceptance"]["ws_roi"],
        })
    result = {"raw_rate": raw_rate, "bin_rows": bin_rows, "intensity": {}}
    for mode in ("nest", "ws_roi"):
        total = math.fsum(intensity[mode].values())
        result["intensity"][mode] = dict(intensity[mode])
        result[mode] = {
            "accepted_rate_events_kg_day": total,
            "acceptance_fraction_of_raw_rate": total / raw_rate if raw_rate > 0 else 0.0,
            "number_of_cells": len(intensity[mode]),
        }
    return result


def total_variation(a: dict, b: dict) -> float:
    suma = math.fsum(a.values())
    sumb = math.fsum(b.values())
    if suma <= 0.0 or sumb <= 0.0:
        return math.nan
    keys = set(a) | set(b)
    return 0.5 * math.fsum(abs(a.get(k, 0.0) / suma - b.get(k, 0.0) / sumb) for k in keys)


def relative_difference(a: float, b: float) -> float:
    if a == 0.0 and b == 0.0:
        return 0.0
    if a == 0.0:
        return math.inf
    return abs(b / a - 1.0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--response-dir", type=Path, required=True)
    ap.add_argument(
        "--spectrum-dir", type=Path,
        default=Path("research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum"),
    )
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "study": "1/5/10-keV response-grid convergence of three-body LZ NR signal",
        "roi_keV": [ROI_MIN_KEV, ROI_MAX_KEV],
        "grid_widths_keV": list(GRID_WIDTHS_KEV),
        "response_energy_sampling": "equal-statistics stratified uniform-energy samples in 1-keV bins; two independent event halves per bin",
        "response_spatial_prior": "uniform active-TPC cylinder volume proxy; not the collaboration's 4.71-tonne fiducial-volume map or calibration-source geometry",
        "response_nest_commit": NEST_COMMIT,
        "response_probability": "N_cell/N_generated in each true-energy stratum; failed S1-coincidence or NEST S2-threshold events remain in the denominator and are not renormalized away",
        "nest_level_definition": "NEST GetS1 Parametric PMT-occupancy coincidence pass (coinLevel/numPMTs; no explicit coinWind timing in this mode) AND NEST GetS2 threshold pass",
        "ws_roi_definition": {
            "S1c_phd": [S1_MIN_PHD, S1_MAX_PHD],
            "raw_S2_phd_strictly_greater_than": S2_RAW_MIN_PHD,
            "S2c_log10_phd": [LOG10_S2C_MIN, LOG10_S2C_MAX],
        },
        "ws_roi_caveat": "This applies only the published S1c/S2/S2c observable-space ROI after NEST-level acceptance. It is not the complete LZ selection: trigger, SS reconstruction, analysis cuts, FV, and veto selections remain absent.",
        "folding_method": "For each grid, response probabilities are width-averaged over 1-keV strata within each coarse bin; the exact piecewise-linear three-body rate is integrated over the same coarse bin. The 1-keV result is the reference.",
        "results": [],
        "replica_stability": [],
    }

    intensity_path = args.out_dir / "signal_2d_intensity_1keV.csv"
    bin_path = args.out_dir / "acceptance_by_energy_grid.csv"
    comparison_rows = []
    stability_rows = []
    with intensity_path.open("w", newline="", encoding="utf-8") as f_int, \
         bin_path.open("w", newline="", encoding="utf-8") as f_bin:
        wi = csv.writer(f_int)
        wi.writerow([
            "benchmark", "nuclear_model", "response_family", "acceptance_mode",
            "s1c_bin_low_phd", "s1c_bin_high_phd", "log10s2c_bin_low",
            "log10s2c_bin_high", "rate_events_kg_day_cell",
        ])
        wb = csv.writer(f_bin)
        wb.writerow([
            "response_family", "grid_width_keV", "replica", "energy_low_keV",
            "energy_high_keV", "raw_rate_integral_events_kg_day", "n_generated",
            "n_s1_coincidence_pass", "n_s2_threshold_pass", "n_nest_joint_pass",
            "n_ws_roi_pass", "s1_coin_acceptance_uniform_energy",
            "s2_threshold_acceptance_uniform_energy", "nest_acceptance_uniform_energy",
            "s2_threshold_given_s1_acceptance", "ws_roi_given_nest_acceptance",
            "ws_roi_acceptance_uniform_energy", "nest_rate_events_kg_day",
            "ws_roi_rate_events_kg_day",
        ])

        for family in RESPONSE_FAMILIES:
            response_path = args.response_dir / f"{family}.csv"
            if not response_path.is_file():
                raise FileNotFoundError(response_path)
            stats = read_response(response_path)
            for benchmark in BENCHMARKS:
                spectrum_path = args.spectrum_dir / benchmark / "natural_xenon_continuous_spectrum.csv"
                for nuclear_model in NUCLEAR_MODELS:
                    xs, ys = read_spectrum(spectrum_path, nuclear_model)
                    folded = {}
                    for width in GRID_WIDTHS_KEV:
                        for rep in (0, 1, None):
                            folded[(width, rep)] = fold_grid(stats, xs, ys, width, rep)
                            rep_label = "pooled" if rep is None else str(rep)
                            for br in folded[(width, rep)]["bin_rows"]:
                                wb.writerow([
                                    family, width, rep_label, br["energy_low_keV"],
                                    br["energy_high_keV"], br["rate_integral_events_kg_day"],
                                    br["n_generated"], br["n_s1_coincidence_pass"],
                                    br["n_s2_threshold_pass"], br["n_nest_joint_pass"],
                                    br["n_ws_roi_pass"], br["s1_coin_acceptance_uniform_energy"],
                                    br["s2_threshold_acceptance_uniform_energy"],
                                    br["nest_acceptance_uniform_energy"],
                                    br["s2_threshold_given_s1_acceptance"],
                                    br["ws_roi_given_nest_acceptance"],
                                    br["ws_roi_acceptance_uniform_energy"],
                                    br["nest_rate_events_kg_day"], br["ws_roi_rate_events_kg_day"],
                                ])
                    for mode in ("nest", "ws_roi"):
                        reference = folded[(1.0, None)]
                        for width in GRID_WIDTHS_KEV:
                            current = folded[(width, None)]
                            ref_rate = reference[mode]["accepted_rate_events_kg_day"]
                            cur_rate = current[mode]["accepted_rate_events_kg_day"]
                            row = {
                                "benchmark": benchmark,
                                "nuclear_response": nuclear_model,
                                "response_family": family,
                                "acceptance_mode": mode,
                                "grid_width_keV": width,
                                "reference_grid_keV": 1.0,
                                "accepted_rate_events_kg_day": cur_rate,
                                "raw_rate_roi_events_kg_day": current["raw_rate"],
                                "acceptance_fraction_of_raw_rate": current[mode]["acceptance_fraction_of_raw_rate"],
                                "relative_rate_difference_vs_1keV": relative_difference(ref_rate, cur_rate),
                                "tv_distance_vs_1keV": total_variation(reference["intensity"][mode], current["intensity"][mode]),
                                "number_of_2d_cells": current[mode]["number_of_cells"],
                            }
                            summary["results"].append(row)
                            comparison_rows.append(row)
                        rep0, rep1 = folded[(1.0, 0)], folded[(1.0, 1)]
                        stability_rows.append({
                            "benchmark": benchmark,
                            "nuclear_response": nuclear_model,
                            "response_family": family,
                            "acceptance_mode": mode,
                            "grid_width_keV": 1.0,
                            "replica_relative_rate_difference": relative_difference(
                                rep0[mode]["accepted_rate_events_kg_day"],
                                rep1[mode]["accepted_rate_events_kg_day"],
                            ),
                            "replica_tv_distance": total_variation(
                                rep0["intensity"][mode], rep1["intensity"][mode]
                            ),
                            "replica0_rate_events_kg_day": rep0[mode]["accepted_rate_events_kg_day"],
                            "replica1_rate_events_kg_day": rep1[mode]["accepted_rate_events_kg_day"],
                        })
                        for (s1_bin, log_bin), rate_cell in sorted(reference["intensity"][mode].items()):
                            wi.writerow([
                                benchmark, nuclear_model, family, mode,
                                s1_bin * S1_BIN_WIDTH_PHD, (s1_bin + 1) * S1_BIN_WIDTH_PHD,
                                round(log_bin * LOG10_S2_BIN_WIDTH, 2),
                                round((log_bin + 1) * LOG10_S2_BIN_WIDTH, 2),
                                f"{rate_cell:.12g}",
                            ])

    summary["results"].sort(key=lambda x: (
        x["benchmark"], x["nuclear_response"], x["response_family"],
        x["acceptance_mode"], x["grid_width_keV"],
    ))
    summary["replica_stability"] = stability_rows
    finite_grid_rows = [
        r for r in comparison_rows
        if r["grid_width_keV"] in (5.0, 10.0)
        and math.isfinite(r["tv_distance_vs_1keV"])
        and math.isfinite(r["relative_rate_difference_vs_1keV"])
    ]
    summary["convergence_diagnostics"] = {
        "formal_pass": None,
        "status": "DIAGNOSTIC_ONLY_NO_PREDECLARED_TOLERANCE",
        "max_5keV_relative_rate_difference_vs_1keV": max(
            r["relative_rate_difference_vs_1keV"] for r in finite_grid_rows
            if r["grid_width_keV"] == 5.0
        ),
        "max_5keV_tv_distance_vs_1keV": max(
            r["tv_distance_vs_1keV"] for r in finite_grid_rows
            if r["grid_width_keV"] == 5.0
        ),
        "max_10keV_relative_rate_difference_vs_1keV": max(
            r["relative_rate_difference_vs_1keV"] for r in finite_grid_rows
            if r["grid_width_keV"] == 10.0
        ),
        "max_10keV_tv_distance_vs_1keV": max(
            r["tv_distance_vs_1keV"] for r in finite_grid_rows
            if r["grid_width_keV"] == 10.0
        ),
        "max_1keV_replica_relative_rate_difference": max(
            r["replica_relative_rate_difference"] for r in stability_rows
        ),
        "max_1keV_replica_tv_distance": max(
            r["replica_tv_distance"] for r in stability_rows
        ),
        "note": (
            "The workflow success status means the calculation and regression "
            "tests completed. It is not a scientific convergence PASS; numerical "
            "acceptance tolerances must be agreed and applied separately."
        ),
    }
    (args.out_dir / "grid_convergence_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    with (args.out_dir / "grid_convergence_comparison.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(comparison_rows[0]))
        w.writeheader()
        w.writerows(comparison_rows)
    with (args.out_dir / "replica_stability.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(stability_rows[0]))
        w.writeheader()
        w.writerows(stability_rows)

    max_tv = max(
        r["tv_distance_vs_1keV"] for r in comparison_rows
        if r["grid_width_keV"] in (5.0, 10.0) and math.isfinite(r["tv_distance_vs_1keV"])
    )
    max_rate = max(
        r["relative_rate_difference_vs_1keV"] for r in comparison_rows
        if r["grid_width_keV"] in (5.0, 10.0) and math.isfinite(r["relative_rate_difference_vs_1keV"])
    )
    print(json.dumps({
        "n_combinations": len(summary["results"]),
        "n_replica_checks": len(stability_rows),
        "max_5_or_10keV_tv_distance_vs_1keV": max_tv,
        "max_5_or_10keV_relative_rate_difference_vs_1keV": max_rate,
        "output_dir": str(args.out_dir),
    }, indent=2))


if __name__ == "__main__":
    main()
