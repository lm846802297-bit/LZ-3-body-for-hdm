#!/usr/bin/env python3
"""Audit finite-sample stability of the paired Parametric/Full S1 2D maps.

The event CSV contains two disjoint halves of one seeded production. This
script constructs exact event-weighted maps for each half and for the pooled
sample, then compares:
  * Parametric versus Full maps (the mode-difference diagnostic);
  * replica 0 versus replica 1 within each mode (a within-stream stability
    benchmark for finite-sample map fluctuations).

The split-half TV is NOT an independent-seed uncertainty estimate, confidence
interval, or significance test. The output is diagnostic only.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import converge_lz_2026_three_body_energy_grid as grid

BENCHMARKS = (
    "red_ms200_dm1",
    "green_ms300_dm1",
    "black_ms360_dm1",
    "blue_ms300_dm10",
)
NUCLEAR_MODELS = ("GCN", "JJ55")
MODES = ("parametric", "full")
STAGES = ("nest", "ws_roi")
ENERGY_MIN_KEV = 35.0
ENERGY_MAX_KEV = 269.9
ENERGY_BIN_WIDTH_KEV = 1.0
REQUIRED = {
    "event", "replica", "energy_bin_index", "energy_bin_low_keV",
    "energy_bin_high_keV", "energy_keV",
    "s1_param_signed_phd", "s1_param_abs_phd", "s1_param_pass",
    "s1_full_signed_phd", "s1_full_abs_phd", "s1_full_pass",
    "s2_signed_phd", "s2_abs_phd", "s2_raw_phd", "s2_threshold_pass",
}


def total_variation(map_a: dict, map_b: dict) -> float | None:
    total_a = math.fsum(map_a.values())
    total_b = math.fsum(map_b.values())
    if total_a <= 0.0 or total_b <= 0.0:
        return None
    keys = set(map_a) | set(map_b)
    return 0.5 * math.fsum(
        abs(map_a.get(key, 0.0) / total_a - map_b.get(key, 0.0) / total_b)
        for key in keys
    )


def compare_mode_maps(
    parametric_pooled: dict,
    full_pooled: dict,
    parametric_replica0: dict,
    parametric_replica1: dict,
    full_replica0: dict,
    full_replica1: dict,
) -> dict:
    """Return mode TV and within-mode split-half stability diagnostics."""
    p_split = total_variation(parametric_replica0, parametric_replica1)
    f_split = total_variation(full_replica0, full_replica1)
    mode_tv = total_variation(parametric_pooled, full_pooled)
    split_values = [value for value in (p_split, f_split) if value is not None]
    split_reference = math.fsum(split_values) / len(split_values) if split_values else None
    return {
        "parametric_vs_full_pooled_tv": mode_tv,
        "parametric_replica0_vs_replica1_tv": p_split,
        "full_replica0_vs_replica1_tv": f_split,
        "parametric_vs_full_replica0_tv": total_variation(
            parametric_replica0, full_replica0
        ),
        "parametric_vs_full_replica1_tv": total_variation(
            parametric_replica1, full_replica1
        ),
        "mean_within_mode_split_half_tv": split_reference,
        "mode_tv_over_mean_split_half_tv": (
            mode_tv / split_reference
            if mode_tv is not None and split_reference is not None and split_reference > 0.0
            else None
        ),
    }


def _read_reference_summary(path: Path) -> dict:
    output = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = (row["benchmark"], row["nuclear_model"], row["stage"])
            if key in output:
                raise ValueError(f"duplicate fold summary row: {key}")
            output[key] = row
    return output


def audit(
    event_csv: Path,
    spectrum_dir: Path,
    fold_summary_csv: Path,
    events_per_bin: int,
) -> tuple[list[dict], dict]:
    if events_per_bin < 2 or events_per_bin % 2:
        raise ValueError("events_per_bin must be an even integer >= 2")

    spectra = {}
    for benchmark in BENCHMARKS:
        spectrum_path = (
            spectrum_dir / benchmark / "natural_xenon_continuous_spectrum.csv"
        )
        for nuclear in NUCLEAR_MODELS:
            spectra[(benchmark, nuclear)] = grid.read_spectrum(
                spectrum_path, nuclear
            )

    # Sufficient statistics and cell weights are kept separately for each
    # true-energy bin and each half, so exact per-bin spectrum normalization
    # can be reproduced for both the pooled and split-half maps.
    denominators = defaultdict(float)
    cell_weights = defaultdict(lambda: defaultdict(float))
    counts = defaultdict(int)
    observed_edges = {}
    n_events = 0

    with event_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{event_csv} missing columns: {sorted(missing)}")

        for row in reader:
            event = int(row["event"])
            if event != n_events:
                raise ValueError(
                    f"event sequence is not contiguous: expected {n_events}, got {event}"
                )
            n_events += 1

            ibin = int(row["energy_bin_index"])
            replica = int(row["replica"])
            if ibin < 0 or replica not in (0, 1):
                raise ValueError(f"invalid energy-bin or replica label: {ibin}/{replica}")

            lo = float(row["energy_bin_low_keV"])
            hi = float(row["energy_bin_high_keV"])
            energy = float(row["energy_keV"])
            if not all(math.isfinite(value) for value in (lo, hi, energy)):
                raise ValueError(f"non-finite energy coordinate in bin {ibin}")
            if not hi > lo or energy < lo - 1e-9 or energy > hi + 1e-9:
                raise ValueError(f"event energy outside declared bin {ibin}")
            edge = observed_edges.setdefault(ibin, (lo, hi))
            if abs(edge[0] - lo) > 1e-10 or abs(edge[1] - hi) > 1e-10:
                raise ValueError(f"inconsistent energy edges in bin {ibin}")
            counts[(ibin, replica)] += 1

            p_signed = float(row["s1_param_signed_phd"])
            p_s1 = float(row["s1_param_abs_phd"])
            f_signed = float(row["s1_full_signed_phd"])
            f_s1 = float(row["s1_full_abs_phd"])
            s2_signed = float(row["s2_signed_phd"])
            s2c = float(row["s2_abs_phd"])
            s2r = float(row["s2_raw_phd"])
            values = (p_signed, p_s1, f_signed, f_s1, s2_signed, s2c, s2r)
            if any(not math.isfinite(value) for value in values):
                raise ValueError(f"non-finite detector observable in bin {ibin}")
            if p_s1 < 0.0 or f_s1 < 0.0 or s2c < 0.0 or s2r < 0.0:
                raise ValueError(f"negative absolute detector observable in bin {ibin}")

            p_flag = int(row["s1_param_pass"])
            f_flag = int(row["s1_full_pass"])
            s2_flag = int(row["s2_threshold_pass"])
            if any(flag not in (0, 1) for flag in (p_flag, f_flag, s2_flag)):
                raise ValueError(f"non-binary selection flag in bin {ibin}")
            if (p_signed > 0.0) != bool(p_flag):
                raise ValueError(f"Parametric S1 sign/pass mismatch in bin {ibin}")
            if (f_signed > 0.0) != bool(f_flag):
                raise ValueError(f"Full S1 sign/pass mismatch in bin {ibin}")
            if (s2_signed > 0.0) != bool(s2_flag):
                raise ValueError(f"S2 sign/pass mismatch in bin {ibin}")

            p_ws_mask = grid.ws_roi_pass(p_s1, s2r, s2c)
            f_ws_mask = grid.ws_roi_pass(f_s1, s2r, s2c)
            if (p_ws_mask or f_ws_mask) and not s2_flag:
                raise ValueError(
                    "WS raw-S2 ROI passed but NEST S2 threshold failed; "
                    "check raw/corrected S2 units and threshold nesting"
                )

            for key, (xs, ys) in spectra.items():
                weight = grid.interpolate(energy, xs, ys)
                if not math.isfinite(weight) or weight < 0.0:
                    raise ValueError(f"invalid differential-rate weight for {key}/{ibin}")
                denominators[(key, ibin, replica)] += weight

                for mode, s1c, coin_flag, ws_mask in (
                    ("parametric", p_s1, p_flag, p_ws_mask),
                    ("full", f_s1, f_flag, f_ws_mask),
                ):
                    nest_pass = bool(coin_flag) and bool(s2_flag) and s1c > 0.0 and s2c > 0.0
                    ws_pass = bool(coin_flag) and bool(s2_flag) and ws_mask
                    for stage, passed in (("nest", nest_pass), ("ws_roi", ws_pass)):
                        if passed:
                            cell = grid.cell_key(s1c, s2c)
                            cell_weights[(key, mode, stage, ibin, replica)][cell] += weight

    expected_edges = grid.make_edges(
        ENERGY_MIN_KEV, ENERGY_MAX_KEV, ENERGY_BIN_WIDTH_KEV
    )
    n_bins = len(expected_edges) - 1
    if n_events != n_bins * events_per_bin:
        raise ValueError(
            f"expected {n_bins * events_per_bin} events, observed {n_events}"
        )
    if sorted(observed_edges) != list(range(n_bins)):
        raise ValueError("event response does not cover every expected energy bin")
    for ibin, (lo, hi) in enumerate(zip(expected_edges, expected_edges[1:])):
        if abs(observed_edges[ibin][0] - lo) > 1e-9:
            raise ValueError(f"incorrect lower energy edge in bin {ibin}")
        if abs(observed_edges[ibin][1] - hi) > 1e-9:
            raise ValueError(f"incorrect upper energy edge in bin {ibin}")
        for replica in (0, 1):
            if counts[(ibin, replica)] != events_per_bin // 2:
                raise ValueError(
                    f"bin {ibin}/replica {replica}: expected {events_per_bin//2}, "
                    f"got {counts[(ibin, replica)]}"
                )

    reference = _read_reference_summary(fold_summary_csv)
    rows = []
    for key, (xs, ys) in spectra.items():
        benchmark, nuclear = key
        for stage in STAGES:
            pooled_maps = {
                mode: defaultdict(float) for mode in MODES
            }
            split_maps = {
                (mode, replica): defaultdict(float)
                for mode in MODES for replica in (0, 1)
            }

            for ibin, (lo, hi) in enumerate(zip(expected_edges, expected_edges[1:])):
                raw_rate = grid.integrate_linear(xs, ys, lo, hi)
                den0 = denominators[(key, ibin, 0)]
                den1 = denominators[(key, ibin, 1)]
                den_pooled = den0 + den1
                if raw_rate > 0.0 and den_pooled <= 0.0:
                    raise ValueError(
                        f"{key}/{ibin}: positive raw rate with zero sampled denominator"
                    )
                if raw_rate <= 0.0 or den_pooled <= 0.0:
                    continue

                for mode in MODES:
                    for replica, denominator in ((0, den0), (1, den1)):
                        source = cell_weights[(key, mode, stage, ibin, replica)]
                        if denominator > 0.0:
                            target = split_maps[(mode, replica)]
                            for cell, value in source.items():
                                target[cell] += raw_rate * value / denominator

                    source0 = cell_weights[(key, mode, stage, ibin, 0)]
                    source1 = cell_weights[(key, mode, stage, ibin, 1)]
                    pooled_cells = defaultdict(float)
                    for cell, value in source0.items():
                        pooled_cells[cell] += value
                    for cell, value in source1.items():
                        pooled_cells[cell] += value
                    target = pooled_maps[mode]
                    for cell, value in pooled_cells.items():
                        target[cell] += raw_rate * value / den_pooled

            metrics = compare_mode_maps(
                pooled_maps["parametric"],
                pooled_maps["full"],
                split_maps[("parametric", 0)],
                split_maps[("parametric", 1)],
                split_maps[("full", 0)],
                split_maps[("full", 1)],
            )
            ref_key = (benchmark, nuclear, stage)
            if ref_key not in reference:
                raise ValueError(f"missing paired-fold summary reference: {ref_key}")
            reference_tv = float(reference[ref_key]["full_vs_parametric_2d_total_variation"])
            closure = abs(metrics["parametric_vs_full_pooled_tv"] - reference_tv)
            if closure > 1e-10:
                raise ValueError(
                    f"pooled TV does not reproduce paired fold for {ref_key}: "
                    f"audit={metrics['parametric_vs_full_pooled_tv']}, fold={reference_tv}"
                )
            rows.append({
                "benchmark": benchmark,
                "nuclear_model": nuclear,
                "stage": stage,
                **metrics,
                "paired_fold_reference_tv": reference_tv,
                "pooled_tv_reproduction_abs_difference": closure,
                "interpretation": (
                    "within-stream split-half stability diagnostic only; not an "
                    "independent-seed uncertainty, confidence interval, or significance"
                ),
            })

    if len(rows) != len(BENCHMARKS) * len(NUCLEAR_MODELS) * len(STAGES):
        raise AssertionError(f"unexpected summary row count: {len(rows)}")

    metadata = {
        "study": "paired S1 2D mode difference versus within-stream split-half stability",
        "status": "WITHIN_STREAM_2D_TV_STABILITY_DIAGNOSTIC_ONLY",
        "n_events": n_events,
        "n_energy_bins": n_bins,
        "events_per_energy_bin": events_per_bin,
        "events_per_replica_per_energy_bin": events_per_bin // 2,
        "response_families": ["eft2024"],
        "benchmarks": list(BENCHMARKS),
        "nuclear_models": list(NUCLEAR_MODELS),
        "stages": list(STAGES),
        "weighting": (
            "Exact event-level dR/dER interpolation; per-energy-bin normalization "
            "to the exact piecewise-linear spectrum integral."
        ),
        "replica_interpretation": (
            "Replica 0 and 1 are disjoint halves of one seeded event production. "
            "Within-mode split-half TV is a descriptive finite-sample stability "
            "benchmark, not an independent-seed uncertainty or significance."
        ),
        "limitations": [
            "No independent-seed ensemble or bootstrap confidence interval is included.",
            "The 2D TV depends on the stated 10-phd by 0.02 log10(S2c) histogram binning.",
            "NEST Full S1 is not official waveform-level LZ reconstruction.",
            "No DAQ trigger, SS/data-analysis, official FV, Skin/OD, or live-time migration is included."
        ],
        "per_key_summaries": rows,
    }
    return rows, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-csv", type=Path, required=True)
    parser.add_argument("--spectrum-dir", type=Path, default=Path(
        "research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum"
    ))
    parser.add_argument("--fold-summary-csv", type=Path, required=True)
    parser.add_argument("--events-per-bin", type=int, default=2000)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    rows, metadata = audit(
        args.event_csv, args.spectrum_dir, args.fold_summary_csv, args.events_per_bin
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.out_dir / "paired_s1_2d_sampling_noise_summary.csv"
    json_path = args.out_dir / "paired_s1_2d_sampling_noise_metadata.json"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": metadata["status"],
        "n_summary_rows": len(rows),
        "n_events": metadata["n_events"],
        "n_energy_bins": metadata["n_energy_bins"],
        "max_pooled_tv_reproduction_abs_difference": max(
            row["pooled_tv_reproduction_abs_difference"] for row in rows
        ),
        "outputs": [str(csv_path), str(json_path)],
    }, indent=2))


if __name__ == "__main__":
    main()
