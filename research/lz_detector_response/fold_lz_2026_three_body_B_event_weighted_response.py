#!/usr/bin/env python3
"""Event-weight formal nucleon-B spectra through the pinned LZ/NEST NR response.

The NEST events are stratified uniformly in 1-keV true-recoil bins. For every
B-corrected spectrum, the event weights are proportional to dR_B/dE_R and
normalized to the exact piecewise-linear rate integral in each bin and replica.
The published Fig. S2 final efficiency remains a separate rate-level count; it
is never multiplied into the NEST/WS-ROI two-dimensional intensity.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import converge_lz_2026_three_body_energy_grid as grid  # noqa: E402
from fold_lz_2026_three_body_event_weighted_response import (  # noqa: E402
    EXPOSURE_KG_DAY,
    FAMILIES,
    MODES,
    read_event_sample,
    weighted_fold_all_replicas,
)

ROI_MIN_KEV = 5.4
ROI_MAX_KEV = 269.9
BENCHMARKS = ("red_ms200_dm1", "green_ms300_dm1", "black_ms360_dm1", "blue_ms300_dm10")
STRANGE_MODELS = (
    "sufian2017_unit_current",
    "alexandrou2020_charge_weighted_converted",
    "alexandrou2026_continuum_unit_current",
)
SCENARIOS = ("AFH-7", "Hybrid-9 (AFH-7 + Helm-2)")
RESPONSE_NEST_COMMIT = "541b6430dae6ea289cf110c99f174a9187f7fdee"


def read_b_spectrum(path: Path, benchmark: str, scenario: str) -> tuple[list[float], list[float]]:
    """Read the formal B column, never the legacy P0 rate column."""
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["benchmark"] == benchmark and row["scenario"] == scenario:
                rows.append((float(row["ER_keV"]), float(row["rate_B_events_kg_day_keV"])))
    rows.sort()
    if len(rows) < 2:
        raise ValueError(f"missing B spectrum for {benchmark}/{scenario} in {path}")
    xs = [row[0] for row in rows]
    ys = [row[1] for row in rows]
    if xs[0] > ROI_MIN_KEV or xs[-1] < ROI_MAX_KEV:
        raise ValueError(f"B spectrum does not cover full ROI: {path} {benchmark}/{scenario}")
    if any(not math.isfinite(x) for x in xs + ys) or any(y < 0.0 for y in ys):
        raise ValueError(f"non-finite or negative B spectrum in {path}")
    if any(b <= a for a, b in zip(xs, xs[1:])):
        raise ValueError(f"non-increasing B spectrum grid in {path}")
    return xs, ys


def read_rate_level_counts(path: Path) -> dict:
    """Read the separate published-Fig.-S2 efficiency-weighted event counts."""
    out = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            out[(row["benchmark"], row["scenario"])] = {
                "raw_rate_integral": float(row["raw_roi_integral_events_kg_day"]),
                "final_efficiency_count": float(row["expected_events_in_high_efficiency_window"]),
                "exposure_kg_day": float(row["exposure_kg_day"]),
            }
    return out


def validate_formal_B_metadata(path: Path) -> dict:
    metadata = json.loads(path.read_text(encoding="utf-8"))
    if metadata.get("detector_response_applied") is not False:
        raise ValueError(f"B input must be pre-detector: {path}")
    transfer = metadata.get("matching", {}).get("t_N", "")
    if "-2*m_A*E_R" not in transfer:
        raise ValueError(f"B input does not use formal t_N=t_A=-2*m_A*E_R: {path}")
    return metadata


def fold_one_spectrum(events: dict, xs: list[float], ys: list[float]) -> dict:
    """Public wrapper for the shared, regression-tested event-weighted kernel."""
    return weighted_fold_all_replicas(events, xs, ys)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--response-dir", type=Path, required=True)
    parser.add_argument("--b-absolute-root", type=Path, required=True)
    parser.add_argument("--b-detector-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    intensity_path = args.out_dir / "B_event_weighted_signal_2d_intensity.csv"
    comparison_path = args.out_dir / "B_event_weighted_fold_comparison.csv"
    bin_path = args.out_dir / "B_event_weighted_acceptance_by_bin.csv"
    replica_path = args.out_dir / "B_event_weighted_replica_stability.csv"
    comparison_rows = []
    replica_rows = []
    max_raw_closure = 0.0
    max_replica_relative_difference = 0.0
    max_replica_tv_distance = 0.0
    n_bin_rows = 0
    n_cell_rows = 0

    intensity_fields = [
        "strange_model", "benchmark", "scenario", "response_family", "acceptance_mode",
        "s1c_bin_low_phd", "s1c_bin_high_phd", "log10s2c_bin_low", "log10s2c_bin_high",
        "rate_events_kg_day_cell",
    ]
    comparison_fields = [
        "strange_model", "benchmark", "scenario", "response_family", "acceptance_mode",
        "raw_rate_integral_events_kg_day", "raw_rate_closure_relative_difference",
        "event_weighted_rate_events_kg_day", "event_weighted_expected_events_2p84_tonne_year",
        "final_efficiency_rate_level_expected_events", "event_weighted_to_final_efficiency_count_ratio",
        "weighted_acceptance", "replica_relative_rate_difference", "replica_tv_distance",
    ]
    bin_fields = [
        "strange_model", "benchmark", "scenario", "response_family", "energy_bin_index",
        "energy_low_keV", "energy_high_keV", "exact_raw_rate_integral_events_kg_day",
        "n_generated_replica0", "n_generated_replica1",
        "nest_acceptance_weighted_replica0", "nest_acceptance_weighted_replica1",
        "ws_roi_acceptance_weighted_replica0", "ws_roi_acceptance_weighted_replica1",
    ]
    replica_fields = [
        "strange_model", "benchmark", "scenario", "response_family", "acceptance_mode",
        "replica0_rate_events_kg_day", "replica1_rate_events_kg_day",
        "relative_rate_difference", "tv_distance",
    ]

    with intensity_path.open("w", newline="", encoding="utf-8") as f_int, \
         comparison_path.open("w", newline="", encoding="utf-8") as f_cmp, \
         bin_path.open("w", newline="", encoding="utf-8") as f_bin, \
         replica_path.open("w", newline="", encoding="utf-8") as f_rep:
        wi = csv.DictWriter(f_int, fieldnames=intensity_fields)
        wc = csv.DictWriter(f_cmp, fieldnames=comparison_fields)
        wb = csv.DictWriter(f_bin, fieldnames=bin_fields)
        wr = csv.DictWriter(f_rep, fieldnames=replica_fields)
        wi.writeheader(); wc.writeheader(); wb.writeheader(); wr.writeheader()

        for family in FAMILIES:
            events = read_event_sample(args.response_dir / f"{family}.csv")
            n_events = sum(len(record["energy"]) for record in events.values())
            print(f"Loaded {family}: {n_events} events across {len(events)//2} energy bins", flush=True)
            for strange_model in STRANGE_MODELS:
                absolute_dir = args.b_absolute_root / strange_model
                detector_dir = args.b_detector_root / strange_model
                spectrum_path = absolute_dir / "afh_hybrid9_B_natural_xenon_spectrum.csv"
                metadata_path = absolute_dir / "metadata.json"
                rate_level_path = detector_dir / "lz_2026_afh7_hybrid9_rate_level_event_yields.csv"
                validate_formal_B_metadata(metadata_path)
                rate_level = read_rate_level_counts(rate_level_path)

                for benchmark in BENCHMARKS:
                    for scenario in SCENARIOS:
                        xs, ys = read_b_spectrum(spectrum_path, benchmark, scenario)
                        folded = fold_one_spectrum(events, xs, ys)
                        info = rate_level[(benchmark, scenario)]
                        closure = grid.relative_difference(info["raw_rate_integral"], folded[None]["raw_rate"])
                        max_raw_closure = max(max_raw_closure, closure)
                        if closure > 2e-10:
                            raise ValueError(
                                f"raw-rate closure failed for {strange_model}/{benchmark}/{scenario}: {closure}"
                            )

                        for bin_row in folded[None]["bin_rows"]:
                            wb.writerow({
                                "strange_model": strange_model,
                                "benchmark": benchmark,
                                "scenario": scenario,
                                "response_family": family,
                                **bin_row,
                            })
                            n_bin_rows += 1

                        for mode in MODES:
                            result = folded[None]["intensity"][mode]
                            pooled_rate = folded[None]["accepted_rate"][mode]
                            rep0_rate = folded[0]["accepted_rate"][mode]
                            rep1_rate = folded[1]["accepted_rate"][mode]
                            rep_rate_difference = grid.relative_difference(rep0_rate, rep1_rate)
                            rep_tv_distance = grid.total_variation(
                                folded[0]["intensity"][mode], folded[1]["intensity"][mode]
                            )
                            expected_events = pooled_rate * info["exposure_kg_day"]
                            final_count = info["final_efficiency_count"]
                            row = {
                                "strange_model": strange_model,
                                "benchmark": benchmark,
                                "scenario": scenario,
                                "response_family": family,
                                "acceptance_mode": mode,
                                "raw_rate_integral_events_kg_day": folded[None]["raw_rate"],
                                "raw_rate_closure_relative_difference": closure,
                                "event_weighted_rate_events_kg_day": pooled_rate,
                                "event_weighted_expected_events_2p84_tonne_year": expected_events,
                                "final_efficiency_rate_level_expected_events": final_count,
                                "event_weighted_to_final_efficiency_count_ratio": (
                                    expected_events / final_count if final_count > 0.0 else None
                                ),
                                "weighted_acceptance": (
                                    pooled_rate / folded[None]["raw_rate"] if folded[None]["raw_rate"] > 0.0 else None
                                ),
                                "replica_relative_rate_difference": rep_rate_difference,
                                "replica_tv_distance": rep_tv_distance,
                            }
                            comparison_rows.append(row)
                            wc.writerow(row)
                            replica_row = {
                                "strange_model": strange_model,
                                "benchmark": benchmark,
                                "scenario": scenario,
                                "response_family": family,
                                "acceptance_mode": mode,
                                "replica0_rate_events_kg_day": rep0_rate,
                                "replica1_rate_events_kg_day": rep1_rate,
                                "relative_rate_difference": rep_rate_difference,
                                "tv_distance": rep_tv_distance,
                            }
                            replica_rows.append(replica_row)
                            wr.writerow(replica_row)
                            max_replica_relative_difference = max(
                                max_replica_relative_difference, rep_rate_difference
                            )
                            max_replica_tv_distance = max(max_replica_tv_distance, rep_tv_distance)
                            for (s1_bin, log_s2_bin), rate_cell in sorted(result.items()):
                                wi.writerow({
                                    "strange_model": strange_model,
                                    "benchmark": benchmark,
                                    "scenario": scenario,
                                    "response_family": family,
                                    "acceptance_mode": mode,
                                    "s1c_bin_low_phd": s1_bin * grid.S1_BIN_WIDTH_PHD,
                                    "s1c_bin_high_phd": (s1_bin + 1) * grid.S1_BIN_WIDTH_PHD,
                                    "log10s2c_bin_low": round(log_s2_bin * grid.LOG10_S2_BIN_WIDTH, 2),
                                    "log10s2c_bin_high": round((log_s2_bin + 1) * grid.LOG10_S2_BIN_WIDTH, 2),
                                    "rate_events_kg_day_cell": f"{rate_cell:.12g}",
                                })
                                n_cell_rows += 1

    summary = {
        "status": "COMPUTED",
        "study": "formal B finite-nucleon spectra event-weighted NEST NR response fold",
        "response_nest_commit": RESPONSE_NEST_COMMIT,
        "response_sampling": "1-keV true-energy strata, two replicas, 2,000 events per replica per bin",
        "response_families": list(FAMILIES),
        "benchmarks": list(BENCHMARKS),
        "strange_models": list(STRANGE_MODELS),
        "nuclear_scenarios": list(SCENARIOS),
        "acceptance_modes": list(MODES),
        "roi_keV": [ROI_MIN_KEV, ROI_MAX_KEV],
        "exposure_kg_day": EXPOSURE_KG_DAY,
        "figS2_policy": "Fig. S2 final efficiency remains a separate rate-level expected-event count; it is not multiplied into the NEST or NEST+WS-ROI 2D intensity.",
        "spatial_prior": "uniform active-TPC cylinder volume proxy; not the official calibration-source or fiducial-volume distribution",
        "scope": "NEST S1-coincidence and S2-threshold response, plus published WS observable ROI; excludes trigger, SS reconstruction, analysis cuts, fiducial-volume mask, veto, background likelihood, and official waveform-level response.",
        "row_counts": {
            "comparisons": len(comparison_rows),
            "per_bin": n_bin_rows,
            "two_d_cells": n_cell_rows,
            "replica_checks": len(replica_rows),
        },
        "diagnostics": {
            "max_raw_rate_closure_relative_difference": max_raw_closure,
            "max_replica_relative_rate_difference": max_replica_relative_difference,
            "max_replica_tv_distance": max_replica_tv_distance,
            "formal_pass": None,
            "status": "DIAGNOSTIC_ONLY_NO_PREDECLARED_TOLERANCE",
        },
    }
    summary_path = args.out_dir / "B_event_weighted_fold_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "status": "COMPUTED",
        "response_artifact_run": 43697104437,
        "response_artifact_id": 14155360851,
        "response_artifact_sha256": "682e2ba71063d6ef835b37a6d328a84ab7c609f404856aa83d56e4b875794bab",
        "B_artifact_run": 44662497177,
        "B_artifact_id": 14596147908,
        "B_artifact_sha256": "f5c1d8d791bffff3159a6e279e5a0e68b705bf07466be6b489ba9a49e29ce7ac",
        "B_source_commit": "40a3291ba2d00516ed8d6f8bf69c48531326047d",
        "response_nest_commit": RESPONSE_NEST_COMMIT,
        "summary": summary,
    }
    manifest_path = args.out_dir / "RUN_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    output_files = sorted(p for p in args.out_dir.iterdir() if p.is_file() and p.name != "SHA256SUMS")
    (args.out_dir / "SHA256SUMS").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in output_files), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
