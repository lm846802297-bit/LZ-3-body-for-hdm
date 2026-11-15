#!/usr/bin/env python3
"""Summarize paired NEST Parametric-versus-Full S1 coincidence samples."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


REQUIRED = {
    "event", "energy_bin_index", "energy_bin_low_keV", "energy_bin_high_keV",
    "energy_keV", "x_mm", "y_mm", "z_mm", "n_photons", "n_electrons",
    "s1_param_signed_phd", "s1_param_abs_phd", "s1_param_spike_count",
    "s1_param_pass", "s1_full_signed_phd", "s1_full_abs_phd",
    "s1_full_spike_count", "s1_full_pass",
}


def wilson_interval(passed: int, total: int, z: float = 1.959963984540054) -> list[float]:
    if total <= 0:
        raise ValueError("Wilson interval requires a positive denominator")
    p = passed / total
    z2 = z * z
    den = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / den
    half = z * math.sqrt(p * (1.0 - p) / total + z2 / (4.0 * total * total)) / den
    return [max(0.0, center - half), min(1.0, center + half)]


def quantile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lo = int(math.floor(position))
    hi = int(math.ceil(position))
    if lo == hi:
        return ordered[lo]
    fraction = position - lo
    return ordered[lo] * (1.0 - fraction) + ordered[hi] * fraction


def read_events(path: Path) -> dict[int, list[dict[str, float]]]:
    groups: dict[int, list[dict[str, float]]] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        for row in reader:
            ibin = int(row["energy_bin_index"])
            item = {key: float(row[key]) for key in REQUIRED if key not in {
                "event", "energy_bin_index"
            }}
            item["event"] = float(row["event"])
            item["energy_bin_index"] = float(ibin)
            if not all(math.isfinite(value) for value in item.values()):
                raise ValueError(f"{path}: non-finite value in event {row['event']}")
            if item["s1_param_pass"] not in (0.0, 1.0) or item["s1_full_pass"] not in (0.0, 1.0):
                raise ValueError(f"{path}: invalid pass flag in event {row['event']}")
            if (item["s1_param_signed_phd"] > 0.0) != bool(item["s1_param_pass"]):
                raise ValueError(f"{path}: Parametric S1 sign/pass mismatch in event {row['event']}")
            if (item["s1_full_signed_phd"] > 0.0) != bool(item["s1_full_pass"]):
                raise ValueError(f"{path}: Full S1 sign/pass mismatch in event {row['event']}")
            groups.setdefault(ibin, []).append(item)
    if not groups:
        raise ValueError(f"{path}: no event rows")
    return groups


def summarize_bin(ibin: int, rows: list[dict[str, float]]) -> dict[str, Any]:
    total = len(rows)
    first = rows[0]
    for row in rows[1:]:
        for key in ("energy_bin_low_keV", "energy_bin_high_keV"):
            if abs(row[key] - first[key]) > 1e-10:
                raise ValueError(f"energy-bin metadata mismatch in bin {ibin}")

    n_param = sum(int(row["s1_param_pass"]) for row in rows)
    n_full = sum(int(row["s1_full_pass"]) for row in rows)
    n_both = sum(
        int(row["s1_param_pass"] and row["s1_full_pass"]) for row in rows
    )
    n_param_only = sum(
        int(row["s1_param_pass"] and not row["s1_full_pass"]) for row in rows
    )
    n_full_only = sum(
        int(row["s1_full_pass"] and not row["s1_param_pass"]) for row in rows
    )
    n_neither = total - n_both - n_param_only - n_full_only

    p_param = n_param / total
    p_full = n_full / total
    difference = p_full - p_param
    discordant_fraction = (n_param_only + n_full_only) / total
    paired_variance = max(0.0, discordant_fraction - difference * difference)
    paired_se = math.sqrt(paired_variance / total)
    ci = [
        max(-1.0, difference - 1.959963984540054 * paired_se),
        min(1.0, difference + 1.959963984540054 * paired_se),
    ]
    z_score = difference / paired_se if paired_se > 0.0 else (0.0 if difference == 0.0 else math.inf)

    param_s1 = [r["s1_param_abs_phd"] for r in rows if r["s1_param_pass"]]
    full_s1 = [r["s1_full_abs_phd"] for r in rows if r["s1_full_pass"]]

    return {
        "energy_bin_index": ibin,
        "energy_low_keV": first["energy_bin_low_keV"],
        "energy_high_keV": first["energy_bin_high_keV"],
        "n_generated": total,
        "n_parametric_pass": n_param,
        "n_full_pass": n_full,
        "parametric_efficiency": p_param,
        "parametric_efficiency_95pct_wilson": wilson_interval(n_param, total),
        "full_efficiency": p_full,
        "full_efficiency_95pct_wilson": wilson_interval(n_full, total),
        "full_minus_parametric_efficiency": difference,
        "paired_difference_standard_error": paired_se,
        "paired_difference_95pct_interval": ci,
        "paired_difference_z_score": z_score,
        "n_both_pass": n_both,
        "n_parametric_only_pass": n_param_only,
        "n_full_only_pass": n_full_only,
        "n_both_fail": n_neither,
        "paired_discordance_fraction": discordant_fraction,
        "parametric_s1c_mean_phd": sum(param_s1) / len(param_s1) if param_s1 else None,
        "parametric_s1c_q10_q50_q90_phd": [
            quantile(param_s1, 0.1), quantile(param_s1, 0.5), quantile(param_s1, 0.9)
        ],
        "full_s1c_mean_phd": sum(full_s1) / len(full_s1) if full_s1 else None,
        "full_s1c_q10_q50_q90_phd": [
            quantile(full_s1, 0.1), quantile(full_s1, 0.5), quantile(full_s1, 0.9)
        ],
    }


def summarize(path: Path) -> dict[str, Any]:
    groups = read_events(path)
    bins = [summarize_bin(index, rows) for index, rows in sorted(groups.items())]
    finite_z_scores = [
        abs(row["paired_difference_z_score"])
        for row in bins
        if math.isfinite(row["paired_difference_z_score"])
    ]
    return {
        "study": "Paired NEST Parametric versus Full S1 coincidence comparison",
        "status": "DIAGNOSTIC_ONLY_NO_EQUIVALENCE_TOLERANCE",
        "formal_pass": None,
        "nest_commit": "541b6430dae6ea289cf110c99f174a9187f7fdee",
        "detector_configuration": "LZ_Detector_2024::SetEFT2024Configuration",
        "parametric_mode": "Analytic PMT-occupancy probability; does not explicitly apply coinWind timing",
        "full_mode": "NEST Full S1 mode; applies PMT-level timing and configured coinWind/coinLevel",
        "pairing": "Same generated NR quanta, true recoil energy, and true position; separate deterministic S1 random streams",
        "spatial_prior": "Uniform active-TPC cylinder proxy; not the official 4.71-tonne FV or calibration-source distribution",
        "scope_limitations": [
            "This compares the NEST S1 coincidence implementations only.",
            "It does not simulate LZ trigger, SS reconstruction, data-analysis cuts, FV selection, Skin/OD veto, or live-time exclusions.",
            "The Full NEST S1 mode is not a complete waveform-level LZ analysis reconstruction.",
            "No equivalence tolerance is pre-registered; confidence intervals are descriptive MC diagnostics.",
        ],
        "maximum_absolute_efficiency_difference": max(
            abs(row["full_minus_parametric_efficiency"]) for row in bins
        ),
        "maximum_absolute_paired_z_score": max(finite_z_scores) if finite_z_scores else None,
        "energy_bins": bins,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    result = summarize(args.input_csv)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.out_dir / "s1_parametric_vs_full_summary.json"
    csv_path = args.out_dir / "s1_parametric_vs_full_summary.csv"
    json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    flat_rows = []
    for row in result["energy_bins"]:
        flat_rows.append({
            key: json.dumps(value) if isinstance(value, list) else value
            for key, value in row.items()
        })
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(flat_rows[0]))
        writer.writeheader()
        writer.writerows(flat_rows)

    print(json.dumps({
        "status": result["status"],
        "formal_pass": result["formal_pass"],
        "energy_bin_count": len(result["energy_bins"]),
        "maximum_absolute_efficiency_difference": result["maximum_absolute_efficiency_difference"],
        "maximum_absolute_paired_z_score": result["maximum_absolute_paired_z_score"],
        "summary_json": str(json_path),
        "summary_csv": str(csv_path),
    }, indent=2))


if __name__ == "__main__":
    main()
