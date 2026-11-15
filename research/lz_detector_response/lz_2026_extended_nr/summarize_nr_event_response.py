#!/usr/bin/env python3
"""Summarize the direct-NEST LZ NR event-response pilot (stdlib only)."""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable


def quantile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = probability * (len(ordered) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def describe(values: list[float]) -> dict:
    if not values:
        return {"n": 0, "mean": None, "std": None, "q05": None,
                "q16": None, "median": None, "q84": None, "q95": None}
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "std": statistics.stdev(values) if len(values) > 1 else 0.0,
        "q05": quantile(values, 0.05),
        "q16": quantile(values, 0.16),
        "median": quantile(values, 0.50),
        "q84": quantile(values, 0.84),
        "q95": quantile(values, 0.95),
    }


def correlation(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    sx = statistics.stdev(xs)
    sy = statistics.stdev(ys)
    if sx == 0.0 or sy == 0.0:
        return None
    return statistics.correlation(xs, ys)


def read_rows(paths: Iterable[Path]) -> dict[tuple[str, float], list[dict]]:
    groups: dict[tuple[str, float], list[dict]] = defaultdict(list)
    for path in paths:
        with path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            required = {
                "baseline", "energy_keV", "event_id", "photons", "electrons",
                "s1c_signed_phd", "s2c_signed_phd", "s1_trigger_pass",
                "s2_threshold_pass", "log10_s2c_if_pass",
            }
            missing = required.difference(reader.fieldnames or [])
            if missing:
                raise ValueError(f"{path}: missing columns {sorted(missing)}")
            for row in reader:
                baseline = row["baseline"]
                energy = float(row["energy_keV"])
                row["_photons"] = float(row["photons"])
                row["_electrons"] = float(row["electrons"])
                row["_s1_abs"] = abs(float(row["s1c_signed_phd"]))
                row["_s2_abs"] = abs(float(row["s2c_signed_phd"]))
                row["_s1_pass"] = row["s1_trigger_pass"] == "1"
                row["_s2_pass"] = row["s2_threshold_pass"] == "1"
                log_s2 = float(row["log10_s2c_if_pass"])
                row["_log_s2"] = log_s2 if math.isfinite(log_s2) else None
                groups[(baseline, energy)].append(row)
    return groups


def summarize_group(baseline: str, energy: float, rows: list[dict]) -> dict:
    n = len(rows)
    s1_pass = [r for r in rows if r["_s1_pass"]]
    s2_pass = [r for r in rows if r["_s2_pass"]]
    joint = [r for r in rows if r["_s1_pass"] and r["_s2_pass"]]

    s1_pass_values = [r["_s1_abs"] for r in s1_pass]
    s2_pass_values = [r["_s2_abs"] for r in s2_pass]
    log_s2_pass_values = [
        r["_log_s2"] for r in s2_pass if r["_log_s2"] is not None
    ]
    joint_s1 = [r["_s1_abs"] for r in joint]
    joint_log_s2 = [
        r["_log_s2"] for r in joint if r["_log_s2"] is not None
    ]
    joint_for_corr = [
        r for r in joint if r["_log_s2"] is not None
    ]

    return {
        "baseline": baseline,
        "energy_keV": energy,
        "generated_events": n,
        "s1_trigger_pass_fraction": len(s1_pass) / n if n else None,
        "s2_threshold_pass_fraction": len(s2_pass) / n if n else None,
        "joint_s1_s2_pass_fraction": len(joint) / n if n else None,
        "photons_quanta": describe([r["_photons"] for r in rows]),
        "electrons_quanta": describe([r["_electrons"] for r in rows]),
        "s1c_abs_all_events_phd": describe([r["_s1_abs"] for r in rows]),
        "s1c_phd_given_s1_trigger": describe(s1_pass_values),
        "s2c_abs_all_events_phd": describe([r["_s2_abs"] for r in rows]),
        "s2c_phd_given_s2_threshold": describe(s2_pass_values),
        "log10_s2c_given_s2_threshold": describe(log_s2_pass_values),
        "s1c_phd_given_joint_pass": describe(joint_s1),
        "log10_s2c_given_joint_pass": describe(joint_log_s2),
        "corr_s1c_log10s2c_given_joint_pass": correlation(
            [r["_s1_abs"] for r in joint_for_corr],
            [r["_log_s2"] for r in joint_for_corr],
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", nargs="+", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    args = parser.parse_args()

    groups = read_rows(args.inputs)
    results = [
        summarize_group(baseline, energy, rows)
        for (baseline, energy), rows in sorted(groups.items())
    ]

    payload = {
        "title": "LZ 2026 NR event-level NEST response pilot",
        "status": "candidate detector-response comparison; not official LZ likelihood",
        "source_pin": {
            "repository": "NESTCollaboration/nest",
            "commit": "423b9745a5bfbb0402514f1d7955e67445de0810",
        },
        "observables": {
            "S1c": "NEST GetS1 result index 5, signed corrected phd area",
            "S2c": "NEST GetS2 result index 7, signed corrected phd area",
            "negative_sign": (
                "NEST flag: S1 coincidence failure or S2 configured-threshold "
                "failure, respectively"
            ),
        },
        "limitations": [
            "LZ_WS2024 is a calibration-tuned candidate detector class, not confirmed exact 2026 response configuration.",
            "The 2026 Table S5 NR mean-yield vector is supplied explicitly.",
            "S1 uses NEST S1CalculationMode::Full; S2 uses S2CalculationMode::Full (integrated/parametric pulse-area branch, not waveform mode).",
            "Events are generated at x=y=0 and the NEST dtCntr reference depth; no spatial-position distribution or reconstruction smearing is applied.",
            "The NEST S2 threshold and S1 coincidence logic are applied, but the complete LZ analysis selection and signal likelihood are not.",
            "No background model, nuisance covariance, BACCARAT PDFs, or official 2D likelihood is included.",
        ],
        "groups": results,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    columns = [
        "baseline", "energy_keV", "generated_events",
        "s1_trigger_pass_fraction", "s2_threshold_pass_fraction",
        "joint_s1_s2_pass_fraction",
        "s1c_pass_mean_phd", "s1c_pass_std_phd",
        "s1c_pass_q16_phd", "s1c_pass_median_phd", "s1c_pass_q84_phd",
        "s2c_pass_mean_phd", "s2c_pass_std_phd",
        "s2c_pass_q16_phd", "s2c_pass_median_phd", "s2c_pass_q84_phd",
        "log10_s2c_joint_median", "corr_s1c_log10s2c_joint",
    ]
    with args.output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for item in results:
            s1 = item["s1c_phd_given_s1_trigger"]
            s2 = item["s2c_phd_given_s2_threshold"]
            joint_log = item["log10_s2c_given_joint_pass"]
            writer.writerow({
                "baseline": item["baseline"],
                "energy_keV": item["energy_keV"],
                "generated_events": item["generated_events"],
                "s1_trigger_pass_fraction": item["s1_trigger_pass_fraction"],
                "s2_threshold_pass_fraction": item["s2_threshold_pass_fraction"],
                "joint_s1_s2_pass_fraction": item["joint_s1_s2_pass_fraction"],
                "s1c_pass_mean_phd": s1["mean"],
                "s1c_pass_std_phd": s1["std"],
                "s1c_pass_q16_phd": s1["q16"],
                "s1c_pass_median_phd": s1["median"],
                "s1c_pass_q84_phd": s1["q84"],
                "s2c_pass_mean_phd": s2["mean"],
                "s2c_pass_std_phd": s2["std"],
                "s2c_pass_q16_phd": s2["q16"],
                "s2c_pass_median_phd": s2["median"],
                "s2c_pass_q84_phd": s2["q84"],
                "log10_s2c_joint_median": joint_log["median"],
                "corr_s1c_log10s2c_joint":
                    item["corr_s1c_log10s2c_given_joint_pass"],
            })

    print(f"Wrote {len(results)} baseline-energy summaries")
    print(f"JSON: {args.output_json}")
    print(f"CSV:  {args.output_csv}")
    for item in results:
        print(
            f"{item['baseline']:7s} E={item['energy_keV']:6.1f} keV "
            f"N={item['generated_events']:5d} "
            f"S1pass={item['s1_trigger_pass_fraction']:.4f} "
            f"S2pass={item['s2_threshold_pass_fraction']:.4f} "
            f"joint={item['joint_s1_s2_pass_fraction']:.4f}"
        )


if __name__ == "__main__":
    main()
