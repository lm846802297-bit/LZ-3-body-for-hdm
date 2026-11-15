#!/usr/bin/env python3
"""Paired seed-cluster bootstrap and exact seed-pair randomization for LZ S1 maps.

The resampling unit is an independent NEST production seed. Parametric and
Full maps from the same seed are always kept together. The primary statistic
is the total-variation distance between separately normalized equal-weight
means of the per-seed event-weighted rate maps.

This is a Monte-Carlo response diagnostic, not an official detector response,
detector-systematic uncertainty, equivalence test, or profile likelihood.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np

SEEDS = (
    20261117, 40261117, 60261117, 80261117, 100261117,
    120261117, 140261117, 160261117, 180261117, 200261117,
)
BENCHMARKS = (
    "red_ms200_dm1", "green_ms300_dm1", "black_ms360_dm1", "blue_ms300_dm10",
)
NUCLEAR_MODELS = ("GCN", "JJ55")
MODES = ("parametric", "full")
STAGES = ("nest", "ws_roi")
SOURCE_ARTIFACT_SHA256 = "606397d9eac594008630a18b97f1e72fbbfa1d157e34779de7ce5fd0fe5b8cb5"
T_CRIT_9 = 2.2621571627409915


def total_variation(map_a: np.ndarray, map_b: np.ndarray) -> float:
    """TV distance between two non-negative, unnormalized map vectors."""
    a = np.asarray(map_a, dtype=np.float64)
    b = np.asarray(map_b, dtype=np.float64)
    total_a = float(a.sum())
    total_b = float(b.sum())
    if a.ndim != 1 or b.ndim != 1 or a.shape != b.shape:
        raise ValueError("TV inputs must be one-dimensional vectors with equal shape")
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError("TV maps must be finite")
    if np.any(a < 0.0) or np.any(b < 0.0):
        raise ValueError("TV maps must be non-negative")
    if total_a <= 0.0 or total_b <= 0.0:
        raise ValueError("TV maps must have positive total weight")
    return float(0.5 * np.abs(a / total_a - b / total_b).sum())


def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm step-down adjusted p-values, returned in original order."""
    if any(not (0.0 <= p <= 1.0) for p in p_values):
        raise ValueError("p-values must lie in [0, 1]")
    order = sorted(range(len(p_values)), key=lambda i: p_values[i])
    adjusted = [0.0] * len(p_values)
    running = 0.0
    n = len(p_values)
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (n - rank) * p_values[idx]))
        adjusted[idx] = running
    return adjusted


def verify_input_manifest(seed_root: Path, required_paths: list[Path]) -> dict:
    """Verify the required input files against SHA256SUMS when it is present.

    Both the immutable Actions-artifact prefix and the committed archive's
    './' relative paths are accepted.
    """
    manifest = seed_root / "SHA256SUMS"
    if not manifest.exists():
        raise FileNotFoundError(f"missing input SHA256SUMS: {manifest}")
    entries = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(None, 1)
        name = name.strip().lstrip("*")
        name = name.removeprefix("paired-s1-independent-seeds-output/")
        name = name.removeprefix("./")
        entries[name] = digest
    checked = 0
    for path in required_paths:
        rel = path.relative_to(seed_root).as_posix()
        if rel not in entries:
            raise ValueError(f"required input is absent from SHA256SUMS: {rel}")
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        if h != entries[rel]:
            raise ValueError(f"SHA-256 mismatch for {rel}: {h} != {entries[rel]}")
        checked += 1
    return {"manifest_entries": len(entries), "required_files_verified": checked}


def read_map(path: Path) -> dict:
    output: dict[tuple, dict[tuple[int, int], float]] = defaultdict(dict)
    required = {
        "benchmark", "nuclear_model", "response_model", "s1_mode", "stage",
        "s1_bin_index", "s1_bin_low_phd", "log10s2_bin_index",
        "log10s2_bin_low", "rate_events_kg_day",
    }
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} missing columns: {sorted(missing)}")
        for row in reader:
            if row["response_model"].lower() != "eft2024":
                raise ValueError(f"unexpected response model in {path}: {row['response_model']}")
            key = (row["benchmark"], row["nuclear_model"], row["stage"], row["s1_mode"])
            cell = (int(row["s1_bin_index"]), int(row["log10s2_bin_index"]))
            value = float(row["rate_events_kg_day"])
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"invalid map weight in {path}: {row}")
            if abs(float(row["s1_bin_low_phd"]) - 10.0 * cell[0]) > 1e-9:
                raise ValueError(f"invalid S1 bin coordinate in {path}: {row}")
            if abs(float(row["log10s2_bin_low"]) - 0.02 * cell[1]) > 1e-9:
                raise ValueError(f"invalid log10(S2c) bin coordinate in {path}: {row}")
            if cell in output[key]:
                raise ValueError(f"duplicate map cell in {path}: {key}/{cell}")
            output[key][cell] = value
    return output


def read_csv_index(path: Path, key_columns: tuple[str, ...], value_column: str) -> dict:
    output = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = tuple(row[column] for column in key_columns)
            if key in output:
                raise ValueError(f"duplicate key in {path}: {key}")
            output[key] = float(row[value_column])
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write an empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_and_validate(seed_root: Path):
    maps_by_seed = {}
    required_paths = []
    for seed in SEEDS:
        path = seed_root / f"seed-{seed}" / "fold" / "paired_s1_mode_2d_signal_intensity.csv"
        required_paths.append(path)
        maps_by_seed[seed] = read_map(path)
    per_seed_path = seed_root / "ensemble" / "paired_s1_independent_seed_per_seed_summary.csv"
    ensemble_path = seed_root / "ensemble" / "paired_s1_independent_seed_ensemble_summary.csv"
    mean_maps_path = seed_root / "ensemble" / "paired_s1_independent_seed_mean_maps.csv"
    required_paths.extend([per_seed_path, ensemble_path, mean_maps_path, seed_root / "run_manifest.json"])
    manifest_info = verify_input_manifest(seed_root, required_paths)
    production_manifest = json.loads((seed_root / "run_manifest.json").read_text(encoding="utf-8"))
    if production_manifest.get("seeds") != list(SEEDS):
        raise ValueError("production run manifest seed list does not match the audited ten seeds")
    if production_manifest.get("total_events") != 4_700_000 or production_manifest.get("events_per_seed") != 470_000:
        raise ValueError("production run manifest event counts do not match the ten-seed design")
    if production_manifest.get("map_binning") != {"s1_phd": 10.0, "log10_s2c": 0.02}:
        raise ValueError("production run manifest map binning does not match the native map definition")

    per_seed_ref = read_csv_index(
        per_seed_path,
        ("seed", "benchmark", "nuclear_model", "stage"),
        "parametric_vs_full_2d_tv",
    )
    ensemble_ref = read_csv_index(
        ensemble_path,
        ("benchmark", "nuclear_model", "stage"),
        "mean_map_parametric_vs_full_tv",
    )
    mean_maps_ref = read_map_mean(mean_maps_path)

    expected_map_keys = {
        (b, n, stage, mode)
        for b in BENCHMARKS for n in NUCLEAR_MODELS
        for stage in STAGES for mode in MODES
    }
    for seed in SEEDS:
        observed = set(maps_by_seed[seed])
        if observed != expected_map_keys:
            raise ValueError(f"seed {seed} map keys incomplete: missing={expected_map_keys-observed}, extra={observed-expected_map_keys}")
    if len(per_seed_ref) != len(SEEDS) * len(BENCHMARKS) * len(NUCLEAR_MODELS) * len(STAGES):
        raise ValueError("per-seed summary does not have 160 rows")
    if len(ensemble_ref) != len(BENCHMARKS) * len(NUCLEAR_MODELS) * len(STAGES):
        raise ValueError("ensemble summary does not have 16 rows")
    expected_mean_keys = {(b, n, stage, mode) for b in BENCHMARKS for n in NUCLEAR_MODELS for stage in STAGES for mode in MODES}
    if set(mean_maps_ref) != expected_mean_keys:
        raise ValueError("archived ensemble mean-map keys are incomplete")
    return maps_by_seed, per_seed_ref, ensemble_ref, mean_maps_ref, manifest_info, production_manifest


def read_map_mean(path: Path) -> dict:
    output: dict[tuple, dict[tuple[int, int], float]] = defaultdict(dict)
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = (row["benchmark"], row["nuclear_model"], row["stage"], row["s1_mode"])
            cell = (int(row["s1_bin_index"]), int(row["log10s2_bin_index"]))
            if cell in output[key]:
                raise ValueError(f"duplicate archived ensemble mean-map cell: {key}/{cell}")
            output[key][cell] = float(row["mean_rate_events_kg_day"])
    return output


def exact_paired_permutation(p_map: np.ndarray, f_map: np.ndarray) -> dict:
    """Enumerate all 2^n within-seed P/F swaps under the exchangeability null."""
    n_seed = p_map.shape[0]
    if f_map.shape != p_map.shape or n_seed > 20:
        raise ValueError("permutation maps must match and have at most 20 seed pairs")
    observed = total_variation(p_map.mean(axis=0), f_map.mean(axis=0))
    n_permutations = 1 << n_seed
    values = np.empty(n_permutations, dtype=np.float64)
    for mask in range(n_permutations):
        swap = np.fromiter(((mask >> i) & 1 for i in range(n_seed)), dtype=bool, count=n_seed)
        perm_p = np.where(swap[:, None], f_map, p_map).mean(axis=0)
        perm_f = np.where(swap[:, None], p_map, f_map).mean(axis=0)
        values[mask] = total_variation(perm_p, perm_f)
    exceed = int(np.count_nonzero(values >= observed - 1e-14))
    return {
        "observed_tv": observed,
        "n_permutations": n_permutations,
        "n_ge_observed": exceed,
        "exact_p_value": exceed / n_permutations,
        "permutation_q50": float(np.quantile(values, 0.50)),
        "permutation_q95": float(np.quantile(values, 0.95)),
        "permutation_q975": float(np.quantile(values, 0.975)),
        "permutation_max": float(values.max()),
    }


def analyze(seed_root: Path, out_dir: Path, n_bootstrap: int, rng_seed: int) -> dict:
    if n_bootstrap < 1000:
        raise ValueError("use at least 1000 bootstrap replicates")
    maps_by_seed, per_seed_ref, ensemble_ref, mean_maps_ref, manifest_info, production_manifest = load_and_validate(seed_root)
    rng = np.random.default_rng(rng_seed)
    # The same resampled seed indices are reused across all observables. P/F maps
    # are always resampled as a pair, preserving their within-seed covariance.
    bootstrap_counts = rng.multinomial(len(SEEDS), [1.0 / len(SEEDS)] * len(SEEDS), size=n_bootstrap)
    summary_rows, loo_rows, closure_rows, permutation_rows = [], [], [], []
    max_seed_closure = 0.0
    max_ensemble_closure = 0.0
    max_mean_map_cell_abs = 0.0
    permutation_cache = []

    for benchmark in BENCHMARKS:
        for nuclear in NUCLEAR_MODELS:
            for stage in STAGES:
                key = (benchmark, nuclear, stage)
                cells = sorted({
                    cell for seed in SEEDS for mode in MODES
                    for cell in maps_by_seed[seed][(*key, mode)]
                })
                arrays = {}
                for mode in MODES:
                    values = np.zeros((len(SEEDS), len(cells)), dtype=np.float64)
                    for i, seed in enumerate(SEEDS):
                        source = maps_by_seed[seed][(*key, mode)]
                        values[i] = [source.get(cell, 0.0) for cell in cells]
                    arrays[mode] = values

                seed_tvs = []
                for i, seed in enumerate(SEEDS):
                    value = total_variation(arrays["parametric"][i], arrays["full"][i])
                    reference = per_seed_ref[(str(seed), *key)]
                    difference = abs(value - reference)
                    max_seed_closure = max(max_seed_closure, difference)
                    seed_tvs.append(value)
                    closure_rows.append({
                        "benchmark": benchmark, "nuclear_model": nuclear, "stage": stage,
                        "seed": seed, "recomputed_seed_tv": value,
                        "archived_seed_tv": reference, "abs_difference": difference,
                    })

                p_mean = arrays["parametric"].mean(axis=0)
                f_mean = arrays["full"].mean(axis=0)
                point = total_variation(p_mean, f_mean)
                archived_point = ensemble_ref[key]
                point_closure = abs(point - archived_point)
                max_ensemble_closure = max(max_ensemble_closure, point_closure)
                for mode, mean_map in (("parametric", p_mean), ("full", f_mean)):
                    archived = mean_maps_ref[(*key, mode)]
                    if not set(archived).issubset(set(cells)):
                        raise ValueError(f"archived mean-map contains cells absent from seed maps for {(*key, mode)}")
                    for cell, value in zip(cells, mean_map):
                        max_mean_map_cell_abs = max(
                            max_mean_map_cell_abs, abs(float(value) - archived.get(cell, 0.0))
                        )

                # Paired nonparametric cluster bootstrap over the ten independent seeds.
                boots = np.empty(n_bootstrap, dtype=np.float64)
                batch_size = 1000
                for offset in range(0, n_bootstrap, batch_size):
                    counts = bootstrap_counts[offset:offset + batch_size].astype(np.float64)
                    bp = counts @ arrays["parametric"]
                    bf = counts @ arrays["full"]
                    sp = bp.sum(axis=1)
                    sf = bf.sum(axis=1)
                    if np.any(sp <= 0.0) or np.any(sf <= 0.0):
                        raise ValueError("bootstrap resample produced an empty map")
                    stop = offset + len(counts)
                    boots[offset:stop] = 0.5 * np.abs(
                        bp / sp[:, None] - bf / sf[:, None]
                    ).sum(axis=1)

                q025, q50, q975 = np.quantile(boots, [0.025, 0.50, 0.975], method="linear")
                basic_low = max(0.0, 2.0 * point - float(q975))
                basic_high = 2.0 * point - float(q025)
                loo = []
                for i, seed in enumerate(SEEDS):
                    keep = np.arange(len(SEEDS)) != i
                    value = total_variation(
                        arrays["parametric"][keep].mean(axis=0),
                        arrays["full"][keep].mean(axis=0),
                    )
                    loo.append(value)
                    loo_rows.append({
                        "benchmark": benchmark, "nuclear_model": nuclear, "stage": stage,
                        "omitted_seed": seed, "loo_tv": value,
                        "delta_from_full_ensemble": value - point,
                    })

                perm = exact_paired_permutation(arrays["parametric"], arrays["full"])
                permutation_rows.append({
                    "benchmark": benchmark, "nuclear_model": nuclear, "stage": stage,
                    **perm,
                })
                permutation_cache.append((key, perm["exact_p_value"]))

                seed_mean = statistics.fmean(seed_tvs)
                seed_sd = statistics.stdev(seed_tvs)
                summary_rows.append({
                    "benchmark": benchmark, "nuclear_model": nuclear, "stage": stage,
                    "n_seeds": len(SEEDS), "n_bootstrap": n_bootstrap,
                    "point_ensemble_mean_map_tv": point,
                    "archived_point_tv": archived_point,
                    "point_closure_abs_difference": point_closure,
                    "bootstrap_mean": float(boots.mean()),
                    "bootstrap_bias_vs_point": float(boots.mean() - point),
                    "bootstrap_median": float(q50),
                    "bootstrap_percentile_2p5": float(q025),
                    "bootstrap_percentile_97p5": float(q975),
                    "bootstrap_basic_2p5": basic_low,
                    "bootstrap_basic_97p5": basic_high,
                    "bootstrap_fraction_below_point": float(np.mean(boots < point)),
                    "bootstrap_fraction_below_1pct": float(np.mean(boots < 0.01)),
                    "mean_per_seed_tv": seed_mean,
                    "sd_per_seed_tv": seed_sd,
                    "per_seed_tv_t95_low": seed_mean - T_CRIT_9 * seed_sd / math.sqrt(len(SEEDS)),
                    "per_seed_tv_t95_high": seed_mean + T_CRIT_9 * seed_sd / math.sqrt(len(SEEDS)),
                    "loo_min": min(loo), "loo_max": max(loo),
                    "n_map_cells_union": len(cells),
                })

    # Holm correction over the eight WS-ROI tests and, separately, all 16 tests.
    p_all = [p for _key, p in permutation_cache]
    adjusted_all = holm_adjust(p_all)
    ws_indices = [i for i, (key, _p) in enumerate(permutation_cache) if key[2] == "ws_roi"]
    adjusted_ws = holm_adjust([p_all[i] for i in ws_indices])
    ws_lookup = {idx: adjusted_ws[j] for j, idx in enumerate(ws_indices)}
    for i, row in enumerate(permutation_rows):
        row["holm_adjusted_p_all16"] = adjusted_all[i]
        row["holm_adjusted_p_wsroi8"] = ws_lookup.get(i, "")

    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "paired_s1_ensemble_tv_bootstrap_summary.csv", summary_rows)
    write_csv(out_dir / "paired_s1_ensemble_tv_leave_one_seed_out.csv", loo_rows)
    write_csv(out_dir / "paired_s1_ensemble_tv_reproduction_closure.csv", closure_rows)
    write_csv(out_dir / "paired_s1_ensemble_tv_exact_paired_permutation.csv", permutation_rows)

    metadata = {
        "study": "Paired-seed cluster bootstrap and exact paired randomization for LZ 2026 Parametric/Full S1 2D maps",
        "status": "BOOTSTRAP_AND_RANDOMIZATION_DIAGNOSTIC_ONLY",
        "source_production_run_id": int(production_manifest["workflow_run_id"]),
        "source_production_commit": production_manifest["source_commit"],
        "pinned_nest_commit": production_manifest["nest_commit"],
        "detector_configuration": production_manifest["detector_configuration"],
        "energy_support_keV": production_manifest["energy_support_keV"],
        "native_map_binning": production_manifest["map_binning"],
        "total_events": production_manifest["total_events"],
        "source_artifact_id": 14176882910,
        "source_artifact_sha256": SOURCE_ARTIFACT_SHA256,
        "source_seed_archive": seed_root.name,
        "input_manifest": manifest_info,
        "seeds": list(SEEDS), "n_seeds": len(SEEDS),
        "n_bootstrap_replicates": n_bootstrap, "bootstrap_rng": "NumPy default_rng",
        "bootstrap_rng_seed": rng_seed,
        "bootstrap_resampling_unit": "independent NEST production seed; Parametric and Full maps from each selected seed are resampled together",
        "bootstrap_statistic": "TV between separately normalized equal-weight arithmetic means of the resampled per-seed event-weighted rate maps",
        "tv_definition": "0.5 * sum_cells(abs(P_cell/sum(P) - F_cell/sum(F)))",
        "bootstrap_intervals": {
            "percentile": "2.5th and 97.5th empirical percentiles of the paired seed-cluster bootstrap distribution",
            "basic": "reflected interval [2*theta_hat - q97.5, 2*theta_hat - q2.5], lower-clipped at zero",
            "interpretation": "The TV functional is non-smooth and non-negative; percentile and basic intervals are reported as sensitivity diagnostics, not a formal equivalence interval. BCa was not used because the bias-correction tail was degenerate/extreme for several combinations with only ten clusters."
        },
        "exact_randomization": {
            "method": "enumerate all 2^10 within-seed Parametric/Full label swaps",
            "null": "exchangeability of the paired mode labels at the independent-seed cluster level",
            "p_value": "inclusive fraction of permutations with TV >= observed TV",
            "holm_families": ["all 16 benchmark/nuclear/stage combinations", "eight WS-ROI combinations"]
        },
        "support": "native 10-phd by 0.02-dex histogram; four benchmarks, GCN/JJ55, NEST and WS-ROI stages",
        "limitations": [
            "Ten independent seed clusters are a small sample; bootstrap intervals are method-sensitive for the non-smooth TV statistic.",
            "Failure to reject the paired randomization null is not evidence of Parametric/Full equivalence.",
            "No official waveform-level LZ reconstruction or detector-systematic covariance is included.",
            "DAQ, SS/data-analysis, official FV, Skin/OD, and live-time migration remain absent.",
            "No final profile likelihood or 90% CL exclusion is provided."
        ],
        "closure": {
            "max_abs_per_seed_tv_difference_vs_archived": max_seed_closure,
            "max_abs_ensemble_tv_difference_vs_archived": max_ensemble_closure,
            "max_abs_mean_map_cell_difference_vs_archived": max_mean_map_cell_abs,
        },
    }
    (out_dir / "paired_s1_ensemble_tv_bootstrap_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    checksum_lines = []
    for path in sorted(out_dir.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS":
            checksum_lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (out_dir / "SHA256SUMS").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-root", type=Path, required=True,
                        help="directory containing seed-*/fold maps and ensemble/ summaries")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--n-bootstrap", type=int, default=100_000)
    parser.add_argument("--rng-seed", type=int, default=2026111601)
    args = parser.parse_args()
    metadata = analyze(args.seed_root, args.out_dir, args.n_bootstrap, args.rng_seed)
    print(json.dumps(metadata["closure"], indent=2))
    print(f"Wrote paired-seed bootstrap and permutation diagnostics to {args.out_dir}")


if __name__ == "__main__":
    main()
