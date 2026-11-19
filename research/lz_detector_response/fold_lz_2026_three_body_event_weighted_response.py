#!/usr/bin/env python3
"""Event-level energy-weighted fold of three-body spectra through NEST NR response.

Each response stratum is generated uniformly in true recoil energy. Within
that stratum, event weights are proportional to dR/dE at the event's true
energy and normalized to the exact piecewise-linear rate integral of the
stratum. This avoids factorizing an unweighted mean response probability and
the rate integral when the response changes across an energy bin.
"""
from __future__ import annotations

import argparse
import array
import bisect
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import converge_lz_2026_three_body_energy_grid as grid

FAMILIES = ("eft2024", "tableS5", "ws2024", "generic")
BENCHMARKS = ("red_ms200_dm1", "green_ms300_dm1", "black_ms360_dm1", "blue_ms300_dm10")
NUCLEAR_MODELS = ("GCN", "JJ55")
MODES = ("nest", "ws_roi")
EXPOSURE_KG_DAY = 1_037_310.0


def interpolate_linear(xs: list[float], ys: list[float], x: float) -> float:
    if x < xs[0] - 1e-10 or x > xs[-1] + 1e-10:
        raise ValueError(f"spectrum does not cover event energy {x}")
    i = bisect.bisect_right(xs, x) - 1
    i = max(0, min(i, len(xs) - 2))
    dx = xs[i + 1] - xs[i]
    t = (x - xs[i]) / dx
    return ys[i] + t * (ys[i + 1] - ys[i])


def read_event_sample(path: Path) -> dict:
    """Retain compact per-stratum arrays needed for weighted folding."""
    events = {}
    required = {
        "replica", "energy_bin_index", "energy_bin_low_keV",
        "energy_bin_high_keV", "energy_keV", "s1c_abs_phd",
        "s1_coincidence_pass", "s2c_abs_phd", "s2r_abs_phd",
        "s2_threshold_pass",
    }
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} missing columns: {sorted(missing)}")
        for row in reader:
            ibin = int(row["energy_bin_index"])
            replica = int(row["replica"])
            key = (ibin, replica)
            if key not in events:
                events[key] = {
                    "lo": float(row["energy_bin_low_keV"]),
                    "hi": float(row["energy_bin_high_keV"]),
                    "energy": array.array("d"),
                    "s1_bin": array.array("i"),
                    "log_s2_bin": array.array("i"),
                    "nest_pass": bytearray(),
                    "roi_pass": bytearray(),
                }
            rec = events[key]
            energy = float(row["energy_keV"])
            s1c = float(row["s1c_abs_phd"])
            s2c = float(row["s2c_abs_phd"])
            s2r = float(row["s2r_abs_phd"])
            s1_pass = int(row["s1_coincidence_pass"]) == 1
            s2_pass = int(row["s2_threshold_pass"]) == 1
            nest_pass = s1_pass and s2_pass and s1c > 0.0 and s2c > 0.0
            if nest_pass:
                s1_bin, log_bin = grid.cell_key(s1c, s2c)
                roi_pass = grid.ws_roi_pass(s1c, s2r, s2c)
            else:
                s1_bin = log_bin = -1
                roi_pass = False
            rec["energy"].append(energy)
            rec["s1_bin"].append(s1_bin)
            rec["log_s2_bin"].append(log_bin)
            rec["nest_pass"].append(int(nest_pass))
            rec["roi_pass"].append(int(roi_pass))

    if not events:
        raise ValueError(f"empty response sample: {path}")
    bins = sorted({ibin for ibin, _ in events})
    for ibin in bins:
        for replica in (0, 1):
            rec = events.get((ibin, replica))
            if rec is None:
                raise ValueError(f"missing response bin/replica {ibin}/{replica} in {path}")
            if len(rec["energy"]) == 0:
                raise ValueError(f"empty response bin/replica {ibin}/{replica} in {path}")
    return events


def weighted_fold_all_replicas(events: dict, xs: list[float], ys: list[float]) -> dict:
    """Return replica 0, replica 1, and pooled weighted observable intensities."""
    bins = sorted({ibin for ibin, _ in events})
    output = {
        rep: {
            "raw_rate": 0.0,
            "intensity": {mode: defaultdict(float) for mode in MODES},
            "accepted_rate": {mode: 0.0 for mode in MODES},
            "bin_rows": [],
        }
        for rep in (0, 1, None)
    }

    for ibin in bins:
        recs = [events[(ibin, 0)], events[(ibin, 1)]]
        lo, hi = recs[0]["lo"], recs[0]["hi"]
        if abs(recs[1]["lo"] - lo) > 1e-10 or abs(recs[1]["hi"] - hi) > 1e-10:
            raise ValueError(f"replica energy-bin mismatch in bin {ibin}")
        exact_bin_rate = grid.integrate_linear(xs, ys, lo, hi)
        replica_sum_r = [0.0, 0.0]
        replica_cells = [
            {mode: defaultdict(float) for mode in MODES}
            for _ in (0, 1)
        ]
        replica_n = [0, 0]
        replica_pass = [
            {mode: 0 for mode in MODES}
            for _ in (0, 1)
        ]

        for rep, rec in enumerate(recs):
            energies = rec["energy"]
            replica_n[rep] = len(energies)
            for j, energy in enumerate(energies):
                rate_density = interpolate_linear(xs, ys, energy)
                replica_sum_r[rep] += rate_density
                if not rec["nest_pass"][j]:
                    continue
                cell = (rec["s1_bin"][j], rec["log_s2_bin"][j])
                replica_cells[rep]["nest"][cell] += rate_density
                replica_pass[rep]["nest"] += 1
                if rec["roi_pass"][j]:
                    replica_cells[rep]["ws_roi"][cell] += rate_density
                    replica_pass[rep]["ws_roi"] += 1

        for rep in (0, 1):
            if replica_sum_r[rep] <= 0.0 and exact_bin_rate > 0.0:
                raise ValueError(f"zero sampled spectrum weight in bin {ibin}, replica {rep}")
            output[rep]["raw_rate"] += exact_bin_rate
            for mode in MODES:
                denom = replica_sum_r[rep]
                if denom <= 0.0:
                    continue
                scale = exact_bin_rate / denom
                for cell, rate_density_sum in replica_cells[rep][mode].items():
                    output[rep]["intensity"][mode][cell] += scale * rate_density_sum
                output[rep]["accepted_rate"][mode] += (
                    scale * math.fsum(replica_cells[rep][mode].values())
                )

        pooled_denom = replica_sum_r[0] + replica_sum_r[1]
        if pooled_denom <= 0.0 and exact_bin_rate > 0.0:
            raise ValueError(f"zero pooled spectrum weight in bin {ibin}")
        output[None]["raw_rate"] += exact_bin_rate
        for mode in MODES:
            if pooled_denom <= 0.0:
                continue
            combined = defaultdict(float)
            for rep in (0, 1):
                for cell, value in replica_cells[rep][mode].items():
                    combined[cell] += value
            scale = exact_bin_rate / pooled_denom
            for cell, rate_density_sum in combined.items():
                output[None]["intensity"][mode][cell] += scale * rate_density_sum
            output[None]["accepted_rate"][mode] += (
                scale * math.fsum(combined.values())
            )

        output[None]["bin_rows"].append({
            "energy_bin_index": ibin,
            "energy_low_keV": lo,
            "energy_high_keV": hi,
            "exact_raw_rate_integral_events_kg_day": exact_bin_rate,
            "n_generated_replica0": replica_n[0],
            "n_generated_replica1": replica_n[1],
            "nest_acceptance_weighted_replica0": (
                math.fsum(replica_cells[0]["nest"].values()) / replica_sum_r[0]
                if replica_sum_r[0] > 0.0 else 0.0
            ),
            "nest_acceptance_weighted_replica1": (
                math.fsum(replica_cells[1]["nest"].values()) / replica_sum_r[1]
                if replica_sum_r[1] > 0.0 else 0.0
            ),
            "ws_roi_acceptance_weighted_replica0": (
                math.fsum(replica_cells[0]["ws_roi"].values()) / replica_sum_r[0]
                if replica_sum_r[0] > 0.0 else 0.0
            ),
            "ws_roi_acceptance_weighted_replica1": (
                math.fsum(replica_cells[1]["ws_roi"].values()) / replica_sum_r[1]
                if replica_sum_r[1] > 0.0 else 0.0
            ),
        })

    for rep in (0, 1, None):
        for mode in MODES:
            output[rep]["accepted_rate"][mode] = math.fsum(
                output[rep]["intensity"][mode].values()
            )
    return output


def read_binned_intensity(path: Path) -> dict:
    maps = defaultdict(lambda: defaultdict(float))
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = (
                row["benchmark"], row["nuclear_model"],
                row["response_family"], row["acceptance_mode"],
            )
            s1_bin = int(round(float(row["s1c_bin_low_phd"]) / grid.S1_BIN_WIDTH_PHD))
            log_bin = int(round(float(row["log10s2c_bin_low"]) / grid.LOG10_S2_BIN_WIDTH))
            maps[key][(s1_bin, log_bin)] += float(row["rate_events_kg_day_cell"])
    return maps


def read_rate_level_counts(path: Path) -> dict:
    out = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = (row["benchmark"], row["model"])
            out[key] = {
                "final_efficiency_count": float(row["expected_events_in_high_efficiency_window"]),
                "raw_rate_integral": float(row["raw_roi_integral_events_kg_day"]),
                "exposure_kg_day": float(row["exposure_kg_day"]),
            }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--response-dir", type=Path, required=True)
    ap.add_argument("--spectrum-dir", type=Path, default=Path(
        "research/three_body_calculation_and_validation/results/natural_xenon_continuous_spectrum"
    ))
    ap.add_argument("--binned-intensity", type=Path, required=True)
    ap.add_argument("--grid-summary", type=Path, required=True)
    ap.add_argument("--rate-level-counts", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    binned_maps = read_binned_intensity(args.binned_intensity)
    rate_level = read_rate_level_counts(args.rate_level_counts)
    grid_summary = json.loads(args.grid_summary.read_text(encoding="utf-8"))
    binned_rates = {}
    for row in grid_summary["results"]:
        if row["grid_width_keV"] == 1.0:
            binned_rates[(
                row["benchmark"], row["nuclear_response"],
                row["response_family"], row["acceptance_mode"],
            )] = row["accepted_rate_events_kg_day"]

    comparisons = []
    summary = {
        "study": "event-level energy-weighted three-body NR response fold",
        "response_energy_sampling": "uniform true energy within each 1-keV stratum; event weights proportional to dR/dE at the event energy",
        "within_bin_weighting": "per event w_j = R_bin * r(E_j) / sum_k r(E_k), where R_bin is the exact piecewise-linear rate integral; weights are normalized separately in each bin and replica",
        "response_spatial_prior": "uniform active-TPC cylinder volume proxy; not the official calibration-source or fiducial-volume distribution",
        "response_nest_commit": grid.NEST_COMMIT,
        "exposure_kg_day": EXPOSURE_KG_DAY,
        "final_efficiency_policy": "published final Fig. S2 efficiency remains in the separate rate-level yield; it is not multiplied into the NEST+WS-ROI 2D intensity",
        "comparisons": comparisons,
    }

    intensity_path = args.out_dir / "event_weighted_signal_2d_intensity.csv"
    comparison_path = args.out_dir / "event_weighted_fold_comparison.csv"
    bin_path = args.out_dir / "event_weighted_acceptance_by_bin.csv"
    replica_path = args.out_dir / "event_weighted_replica_stability.csv"

    with intensity_path.open("w", newline="", encoding="utf-8") as f_int, \
         comparison_path.open("w", newline="", encoding="utf-8") as f_cmp, \
         bin_path.open("w", newline="", encoding="utf-8") as f_bin, \
         replica_path.open("w", newline="", encoding="utf-8") as f_rep:
        wi = csv.writer(f_int)
        wi.writerow([
            "benchmark", "nuclear_model", "response_family", "acceptance_mode",
            "s1c_bin_low_phd", "s1c_bin_high_phd",
            "log10s2c_bin_low", "log10s2c_bin_high",
            "rate_events_kg_day_cell",
        ])
        wc = csv.DictWriter(f_cmp, fieldnames=[
            "benchmark", "nuclear_model", "response_family", "acceptance_mode",
            "exact_raw_rate_events_kg_day", "raw_rate_closure_relative_difference",
            "event_weighted_rate_events_kg_day", "event_weighted_expected_events_2p84_tonne_year",
            "final_efficiency_rate_level_expected_events",
            "event_weighted_to_final_efficiency_count_ratio",
            "binned_1keV_rate_events_kg_day",
            "relative_rate_difference_vs_binned_1keV",
            "tv_distance_vs_binned_1keV",
            "replica_relative_rate_difference",
            "replica_tv_distance",
        ])
        wc.writeheader()
        wb = csv.DictWriter(f_bin, fieldnames=[
            "benchmark", "nuclear_model", "response_family",
            "energy_bin_index", "energy_low_keV", "energy_high_keV",
            "exact_raw_rate_integral_events_kg_day",
            "n_generated_replica0", "n_generated_replica1",
            "nest_acceptance_weighted_replica0",
            "nest_acceptance_weighted_replica1",
            "ws_roi_acceptance_weighted_replica0",
            "ws_roi_acceptance_weighted_replica1",
        ])
        wb.writeheader()
        wr = csv.DictWriter(f_rep, fieldnames=[
            "benchmark", "nuclear_model", "response_family", "acceptance_mode",
            "replica0_rate_events_kg_day", "replica1_rate_events_kg_day",
            "relative_rate_difference", "tv_distance",
        ])
        wr.writeheader()

        for family in FAMILIES:
            events = read_event_sample(args.response_dir / f"{family}.csv")
            for benchmark in BENCHMARKS:
                spectrum_path = args.spectrum_dir / benchmark / "natural_xenon_continuous_spectrum.csv"
                for nuclear in NUCLEAR_MODELS:
                    xs, ys = grid.read_spectrum(spectrum_path, nuclear)
                    folded = weighted_fold_all_replicas(events, xs, ys)
                    rate_info = rate_level[(benchmark, nuclear)]
                    for br in folded[None]["bin_rows"]:
                        wb.writerow({
                            "benchmark": benchmark,
                            "nuclear_model": nuclear,
                            "response_family": family,
                            **br,
                        })
                    for mode in MODES:
                        pooled_rate = folded[None]["accepted_rate"][mode]
                        rep0_rate = folded[0]["accepted_rate"][mode]
                        rep1_rate = folded[1]["accepted_rate"][mode]
                        rep_rate_diff = grid.relative_difference(rep0_rate, rep1_rate)
                        rep_tv = grid.total_variation(
                            folded[0]["intensity"][mode],
                            folded[1]["intensity"][mode],
                        )
                        key = (benchmark, nuclear, family, mode)
                        binned_rate = binned_rates[key]
                        binned_map = binned_maps[key]
                        tv_binned = grid.total_variation(
                            folded[None]["intensity"][mode], binned_map
                        )
                        final_count = rate_info["final_efficiency_count"]
                        raw_rate_closure = grid.relative_difference(
                            rate_info["raw_rate_integral"], folded[None]["raw_rate"]
                        )
                        if raw_rate_closure > 1e-10:
                            raise ValueError(
                                f"raw spectrum integral does not close for {benchmark}/{nuclear}: "
                                f"{raw_rate_closure}"
                            )
                        exposure_kg_day = rate_info["exposure_kg_day"]
                        row = {
                            "benchmark": benchmark,
                            "nuclear_model": nuclear,
                            "response_family": family,
                            "acceptance_mode": mode,
                            "exact_raw_rate_events_kg_day": folded[None]["raw_rate"],
                            "raw_rate_closure_relative_difference": raw_rate_closure,
                            "event_weighted_rate_events_kg_day": pooled_rate,
                            "event_weighted_expected_events_2p84_tonne_year": pooled_rate * exposure_kg_day,
                            "final_efficiency_rate_level_expected_events": final_count,
                            "event_weighted_to_final_efficiency_count_ratio": (
                                pooled_rate * exposure_kg_day / final_count if final_count > 0.0 else None
                            ),
                            "binned_1keV_rate_events_kg_day": binned_rate,
                            "relative_rate_difference_vs_binned_1keV": grid.relative_difference(
                                binned_rate, pooled_rate
                            ),
                            "tv_distance_vs_binned_1keV": tv_binned,
                            "replica_relative_rate_difference": rep_rate_diff,
                            "replica_tv_distance": rep_tv,
                        }
                        comparisons.append(row)
                        wc.writerow(row)
                        wr.writerow({
                            "benchmark": benchmark,
                            "nuclear_model": nuclear,
                            "response_family": family,
                            "acceptance_mode": mode,
                            "replica0_rate_events_kg_day": rep0_rate,
                            "replica1_rate_events_kg_day": rep1_rate,
                            "relative_rate_difference": rep_rate_diff,
                            "tv_distance": rep_tv,
                        })
                        for (s1_bin, log_bin), rate_cell in sorted(
                            folded[None]["intensity"][mode].items()
                        ):
                            wi.writerow([
                                benchmark, nuclear, family, mode,
                                s1_bin * grid.S1_BIN_WIDTH_PHD,
                                (s1_bin + 1) * grid.S1_BIN_WIDTH_PHD,
                                round(log_bin * grid.LOG10_S2_BIN_WIDTH, 2),
                                round((log_bin + 1) * grid.LOG10_S2_BIN_WIDTH, 2),
                                f"{rate_cell:.12g}",
                            ])

    summary["diagnostics"] = {
        "n_comparisons": len(comparisons),
        "max_raw_rate_closure_relative_difference": max(
            x["raw_rate_closure_relative_difference"] for x in comparisons
        ),
        "max_relative_rate_difference_vs_binned_1keV": max(
            x["relative_rate_difference_vs_binned_1keV"] for x in comparisons
        ),
        "max_tv_distance_vs_binned_1keV": max(
            x["tv_distance_vs_binned_1keV"] for x in comparisons
        ),
        "max_replica_relative_rate_difference": max(
            x["replica_relative_rate_difference"] for x in comparisons
        ),
        "max_replica_tv_distance": max(x["replica_tv_distance"] for x in comparisons),
        "formal_pass": None,
        "status": "DIAGNOSTIC_ONLY_NO_PREDECLARED_TOLERANCE",
    }
    (args.out_dir / "event_weighted_fold_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary["diagnostics"], indent=2))


if __name__ == "__main__":
    main()
