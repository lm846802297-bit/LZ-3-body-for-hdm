#!/usr/bin/env python3
"""Estimate within-production MC uncertainty for the energy-resolved WS-ROI response.

The archived NEST CSV contains one seeded production split into two disjoint
within-stream halves. This script estimates weighted Bernoulli sampling errors
from the event-level response and reports half-to-half stability. It also
reports the factorized-rate mismatch divided by the NEST-response MC standard
error as a scale diagnostic only. That ratio is NOT a statistical pull or
significance: the Fig. S2 curve has no propagated uncertainty here, and the
SS/DA conditional factorization is not established at event level.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import converge_lz_2026_three_body_energy_grid as grid

RESPONSE_FAMILIES = ("eft2024", "tableS5")
BENCHMARKS = (
    "red_ms200_dm1",
    "green_ms300_dm1",
    "black_ms360_dm1",
    "blue_ms300_dm10",
)
NUCLEAR_MODELS = ("GCN", "JJ55")
EXPECTED_EVENTS_PER_REPLICA = 2000


def weighted_efficiency(
    total_weight: float,
    total_weight2: float,
    accepted_weight: float,
    accepted_weight2: float,
) -> tuple[float, float]:
    """Return a weighted Bernoulli efficiency and its plug-in MC standard error.

    For fixed event weights w_i and pass indicators I_i, the ratio estimator is
    p=sum(w_i I_i)/sum(w_i). Its conditional variance is estimated from
    sum(w_i^2 (I_i-p)^2)/sum(w_i)^2. The calculation is performed using only
    sufficient statistics, so individual event records need not be retained.
    """
    values = (total_weight, total_weight2, accepted_weight, accepted_weight2)
    if any(not math.isfinite(value) or value < -1e-12 for value in values):
        raise ValueError("weighted-efficiency sufficient statistics must be finite and non-negative")
    if accepted_weight > total_weight * (1.0 + 1e-10) + 1e-12:
        raise ValueError("accepted weight exceeds total weight")
    if accepted_weight2 > total_weight2 * (1.0 + 1e-10) + 1e-12:
        raise ValueError("accepted squared weight exceeds total squared weight")
    if total_weight <= 0.0:
        if accepted_weight > 1e-12:
            raise ValueError("positive accepted weight with zero total weight")
        return 0.0, 0.0
    p = min(1.0, max(0.0, accepted_weight / total_weight))
    pass_w2 = min(total_weight2, max(0.0, accepted_weight2))
    fail_w2 = max(0.0, total_weight2 - pass_w2)
    variance_numerator = p * p * fail_w2 + (1.0 - p) ** 2 * pass_w2
    return p, math.sqrt(max(0.0, variance_numerator)) / total_weight


def effective_sample_size(total_weight: float, total_weight2: float) -> float:
    """Kish effective sample size for the event weights in one stratum."""
    if total_weight <= 0.0 or total_weight2 <= 0.0:
        return 0.0
    return total_weight * total_weight / total_weight2


def _empty_replica() -> dict:
    return {
        "n": 0,
        "sum_w": 0.0,
        "sum_w2": 0.0,
        "nest_w": 0.0,
        "nest_w2": 0.0,
        "ws_w": 0.0,
        "ws_w2": 0.0,
    }


def accumulate_response(
    response_csv: Path,
    spectra: dict[tuple[str, str], tuple[list[float], list[float]]],
) -> dict:
    """Stream the archived NEST sample and accumulate per-bin/replica moments."""
    if not spectra:
        raise ValueError("at least one benchmark/nuclear spectrum is required")
    stats = defaultdict(_empty_replica)
    with response_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {
            "replica", "energy_bin_index", "energy_bin_low_keV",
            "energy_bin_high_keV", "energy_keV", "s1c_abs_phd",
            "s2c_abs_phd", "s2r_abs_phd", "s1_coincidence_pass",
            "s2_threshold_pass",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{response_csv} missing columns: {sorted(missing)}")
        edges = {}
        for row in reader:
            ibin = int(row["energy_bin_index"])
            replica = int(row["replica"])
            if ibin < 0 or replica not in (0, 1):
                raise ValueError(f"invalid energy bin or replica label: {ibin}, {replica}")
            lo = float(row["energy_bin_low_keV"])
            hi = float(row["energy_bin_high_keV"])
            energy = float(row["energy_keV"])
            s1c = float(row["s1c_abs_phd"])
            s2c = float(row["s2c_abs_phd"])
            s2r = float(row["s2r_abs_phd"])
            if not all(math.isfinite(v) for v in (lo, hi, energy, s1c, s2c, s2r)):
                raise ValueError(f"non-finite event observable in bin {ibin}, replica {replica}")
            if not hi > lo or energy < lo - 1e-9 or energy > hi + 1e-9:
                raise ValueError(f"event energy outside declared bin [{lo}, {hi}]")
            edge = edges.setdefault(ibin, (lo, hi))
            if abs(edge[0] - lo) > 1e-10 or abs(edge[1] - hi) > 1e-10:
                raise ValueError(f"inconsistent energy edges in bin {ibin}")
            s1_flag = int(row["s1_coincidence_pass"])
            s2_flag = int(row["s2_threshold_pass"])
            if s1_flag not in (0, 1) or s2_flag not in (0, 1):
                raise ValueError(f"invalid NEST selection flag in bin {ibin}")
            nest_pass = s1_flag == 1 and s2_flag == 1 and s1c > 0.0 and s2c > 0.0
            ws_pass = nest_pass and grid.ws_roi_pass(s1c, s2r, s2c)

            for key, (xs, ys) in spectra.items():
                weight = grid.interpolate(energy, xs, ys)
                if not math.isfinite(weight) or weight < 0.0:
                    raise ValueError(f"invalid differential-rate weight for {key}/{ibin}")
                bucket = stats[(key, ibin, replica)]
                weight2 = weight * weight
                bucket["n"] += 1
                bucket["sum_w"] += weight
                bucket["sum_w2"] += weight2
                if nest_pass:
                    bucket["nest_w"] += weight
                    bucket["nest_w2"] += weight2
                if ws_pass:
                    bucket["ws_w"] += weight
                    bucket["ws_w2"] += weight2

    expected_edges = grid.make_edges(grid.ROI_MIN_KEV, grid.ROI_MAX_KEV, 1.0)
    if sorted(edges) != list(range(len(expected_edges) - 1)):
        raise ValueError("response sample does not cover the full 1-keV energy grid")
    for ibin, (lo, hi) in enumerate(zip(expected_edges, expected_edges[1:])):
        observed = edges[ibin]
        if abs(observed[0] - lo) > 1e-9 or abs(observed[1] - hi) > 1e-9:
            raise ValueError(f"incorrect energy edges in bin {ibin}")
        for key in spectra:
            for replica in (0, 1):
                bucket = stats[(key, ibin, replica)]
                if bucket["n"] != EXPECTED_EVENTS_PER_REPLICA:
                    raise ValueError(
                        f"{key}/{ibin}/replica{replica}: expected "
                        f"{EXPECTED_EVENTS_PER_REPLICA} events, got {bucket['n']}"
                    )
    return stats


def read_bridge_bins(path: Path) -> dict:
    output = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = (
                row["response_family"], row["benchmark"],
                row["nuclear_model"], int(row["energy_bin_index"]),
            )
            if key in output:
                raise ValueError(f"duplicate bridge energy-bin row: {key}")
            output[key] = row
    return output


def build_diagnostics(
    family: str,
    spectra: dict,
    stats: dict,
    bridge_rows: dict,
) -> tuple[list[dict], list[dict]]:
    bins = []
    summaries = []
    n_energy_bins = len(grid.make_edges(grid.ROI_MIN_KEV, grid.ROI_MAX_KEV, 1.0)) - 1
    for key in spectra:
        benchmark, nuclear = key
        selected = []
        for ibin in range(n_energy_bins):
            bridge_key = (family, benchmark, nuclear, ibin)
            if bridge_key not in bridge_rows:
                raise ValueError(f"missing energy-resolved bridge row: {bridge_key}")
            bridge = bridge_rows[bridge_key]
            replica_stats = [stats[(key, ibin, replica)] for replica in (0, 1)]
            estimates = []
            for bucket in replica_stats:
                estimates.append({
                    "nest": weighted_efficiency(
                        bucket["sum_w"], bucket["sum_w2"],
                        bucket["nest_w"], bucket["nest_w2"],
                    ),
                    "ws": weighted_efficiency(
                        bucket["sum_w"], bucket["sum_w2"],
                        bucket["ws_w"], bucket["ws_w2"],
                    ),
                })
            pooled = {}
            for name, w_key, w2_key in (
                ("nest", "nest_w", "nest_w2"),
                ("ws", "ws_w", "ws_w2"),
            ):
                pooled[name] = weighted_efficiency(
                    math.fsum(b["sum_w"] for b in replica_stats),
                    math.fsum(b["sum_w2"] for b in replica_stats),
                    math.fsum(b[w_key] for b in replica_stats),
                    math.fsum(b[w2_key] for b in replica_stats),
                )
            raw_rate = float(bridge["exact_raw_rate_events_kg_day"])
            ss_da = float(bridge["figs2_ss_da_given_trigger_plus_s1"])
            final_rate = float(bridge["figs2_final_plus_roi_rate_events_kg_day"])
            factorized_rate = float(bridge["energy_resolved_factorized_rate_events_kg_day"])
            ws_acceptance, ws_se = pooled["ws"]
            mc_rate_se = raw_rate * ss_da * ws_se
            delta_rate = factorized_rate - final_rate
            mismatch_over_response_mc_se = (
                delta_rate / mc_rate_se if mc_rate_se > 0.0 else None
            )
            split_delta = abs(estimates[0]["ws"][0] - estimates[1]["ws"][0])
            split_se = math.hypot(estimates[0]["ws"][1], estimates[1]["ws"][1])
            split_pull = split_delta / split_se if split_se > 0.0 else None
            row = {
                "benchmark": benchmark,
                "nuclear_model": nuclear,
                "response_family": family,
                "energy_bin_index": ibin,
                "energy_low_keV": float(bridge["energy_low_keV"]),
                "energy_high_keV": float(bridge["energy_high_keV"]),
                "events_per_replica": EXPECTED_EVENTS_PER_REPLICA,
                "raw_effective_sample_size_replica0": effective_sample_size(
                    replica_stats[0]["sum_w"], replica_stats[0]["sum_w2"]
                ),
                "raw_effective_sample_size_replica1": effective_sample_size(
                    replica_stats[1]["sum_w"], replica_stats[1]["sum_w2"]
                ),
                "raw_effective_sample_size_pooled": effective_sample_size(
                    math.fsum(b["sum_w"] for b in replica_stats),
                    math.fsum(b["sum_w2"] for b in replica_stats),
                ),
                "nest_acceptance_replica0": estimates[0]["nest"][0],
                "nest_acceptance_replica1": estimates[1]["nest"][0],
                "nest_acceptance_pooled": pooled["nest"][0],
                "nest_acceptance_mc_se": pooled["nest"][1],
                "ws_roi_acceptance_replica0": estimates[0]["ws"][0],
                "ws_roi_acceptance_replica1": estimates[1]["ws"][0],
                "ws_roi_acceptance_pooled": ws_acceptance,
                "ws_roi_acceptance_mc_se": ws_se,
                "ws_roi_acceptance_relative_mc_se": ws_se / ws_acceptance if ws_acceptance > 0.0 else None,
                "ws_roi_split_half_abs_difference": split_delta,
                "ws_roi_split_half_tension": split_pull,
                "factorized_rate_events_kg_day": factorized_rate,
                "factorized_rate_mc_se_events_kg_day": mc_rate_se,
                "figs2_final_rate_events_kg_day": final_rate,
                "factorized_minus_figs2_final_events_kg_day": delta_rate,
                "factorized_minus_figs2_final_over_response_mc_se_diagnostic": (
                    mismatch_over_response_mc_se
                ),
            }
            bins.append(row)
            selected.append(row)

        factorized_total = math.fsum(r["factorized_rate_events_kg_day"] for r in selected)
        final_total = math.fsum(r["figs2_final_rate_events_kg_day"] for r in selected)
        total_mc_se = math.sqrt(math.fsum(
            r["factorized_rate_mc_se_events_kg_day"] ** 2 for r in selected
        ))
        total_delta = factorized_total - final_total
        mismatch_ratios = [
            r["factorized_minus_figs2_final_over_response_mc_se_diagnostic"]
            for r in selected
            if r["factorized_minus_figs2_final_over_response_mc_se_diagnostic"] is not None
        ]
        split_pulls = [r["ws_roi_split_half_tension"] for r in selected
                       if r["ws_roi_split_half_tension"] is not None]
        summaries.append({
            "benchmark": benchmark,
            "nuclear_model": nuclear,
            "response_family": family,
            "n_energy_bins": len(selected),
            "factorized_rate_events_kg_day": factorized_total,
            "figs2_final_rate_events_kg_day": final_total,
            "factorized_vs_figs2_final_relative_difference": (
                total_delta / final_total if final_total > 0.0 else None
            ),
            "factorized_rate_mc_se_events_kg_day": total_mc_se,
            "integrated_mismatch_over_response_mc_se_diagnostic": (
                total_delta / total_mc_se if total_mc_se > 0.0 else None
            ),
            "max_abs_energy_bin_mismatch_over_response_mc_se_diagnostic": (
                max((abs(v) for v in mismatch_ratios), default=None)
            ),
            "n_energy_bins_abs_mismatch_over_response_mc_se_gt_3": (
                sum(abs(v) > 3.0 for v in mismatch_ratios)
            ),
            "n_energy_bins_abs_mismatch_over_response_mc_se_gt_5": (
                sum(abs(v) > 5.0 for v in mismatch_ratios)
            ),
            "min_raw_effective_sample_size_per_bin": min(
                (r["raw_effective_sample_size_pooled"] for r in selected),
                default=None,
            ),
            "max_raw_effective_sample_size_per_bin": max(
                (r["raw_effective_sample_size_pooled"] for r in selected),
                default=None,
            ),
            "max_ws_roi_split_half_tension": max(split_pulls, default=None),
            "n_energy_bins_split_half_tension_gt_3": sum(v > 3.0 for v in split_pulls),
        })
    return bins, summaries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response-dir", type=Path, required=True)
    parser.add_argument("--bridge-bin-csv", type=Path, required=True)
    parser.add_argument("--spectrum-dir", type=Path, default=Path(
        "research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum"
    ))
    parser.add_argument("--response-families", nargs="+", choices=RESPONSE_FAMILIES,
                        default=list(RESPONSE_FAMILIES))
    parser.add_argument("--benchmarks", nargs="+", choices=BENCHMARKS, default=list(BENCHMARKS))
    parser.add_argument("--nuclear-models", nargs="+", choices=NUCLEAR_MODELS,
                        default=list(NUCLEAR_MODELS))
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    spectra = {}
    for benchmark in args.benchmarks:
        path = args.spectrum_dir / benchmark / "natural_xenon_continuous_spectrum.csv"
        for nuclear in args.nuclear_models:
            spectra[(benchmark, nuclear)] = grid.read_spectrum(path, nuclear)
    bridge_rows = read_bridge_bins(args.bridge_bin_csv)

    all_bins = []
    all_summaries = []
    for family in args.response_families:
        stats = accumulate_response(args.response_dir / f"{family}.csv", spectra)
        bins, summaries = build_diagnostics(family, spectra, stats, bridge_rows)
        all_bins.extend(bins)
        all_summaries.extend(summaries)

    if len(all_bins) != len(args.response_families) * len(spectra) * (
        len(grid.make_edges(grid.ROI_MIN_KEV, grid.ROI_MAX_KEV, 1.0)) - 1
    ):
        raise AssertionError("unexpected energy-bin diagnostic row count")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    bins_path = args.out_dir / "energy_resolved_selection_mc_uncertainty_by_bin.csv"
    summary_path = args.out_dir / "energy_resolved_selection_mc_uncertainty_summary.csv"
    json_path = args.out_dir / "energy_resolved_selection_mc_uncertainty_summary.json"
    for path, rows in ((bins_path, all_bins), (summary_path, all_summaries)):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    summary = {
        "study": "within-production MC uncertainty of energy-resolved WS-ROI selection bridge",
        "status": "WITHIN_STREAM_MC_DIAGNOSTIC_ONLY",
        "response_families": args.response_families,
        "benchmarks": args.benchmarks,
        "nuclear_models": args.nuclear_models,
        "energy_interval_keV": [grid.ROI_MIN_KEV, grid.ROI_MAX_KEV],
        "energy_bin_width_keV": 1.0,
        "events_per_replica_per_bin": EXPECTED_EVENTS_PER_REPLICA,
        "variance_method": (
            "conditional weighted-Bernoulli plug-in variance: "
            "sum_i w_i^2 (I_i-p_hat)^2 / (sum_i w_i)^2, "
            "with w_i=dR/dER(E_i)"
        ),
        "replica_interpretation": (
            "The two labels are disjoint halves of one seeded NEST event stream, "
            "not independent-seed productions. Split-half differences are diagnostics only."
        ),
        "mismatch_ratio_interpretation": (
            "The factorized-minus-Fig-S2 rate difference divided by the NEST/WS-ROI "
            "response MC standard error is a scale diagnostic only, NOT a statistical "
            "pull or significance. Fig. S2 extraction uncertainty and the unproven "
            "event-level SS/DA conditional factorization are not included."
        ),
        "uncertainties_not_included": [
            "Fig. S2 vector extraction and digitization uncertainty",
            "three-body spectrum and nuclear-response uncertainty",
            "NEST model and calibration-source configuration uncertainty",
            "official fiducial-volume, Skin/OD, waveform-trigger, and SS/data-analysis migration uncertainty",
            "between-seed and between-production variance",
        ],
        "per_key_summaries": all_summaries,
    }
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": summary["status"],
        "n_summary_rows": len(all_summaries),
        "n_energy_bin_rows": len(all_bins),
        "outputs": [str(summary_path), str(bins_path), str(json_path)],
    }, indent=2))


if __name__ == "__main__":
    main()
