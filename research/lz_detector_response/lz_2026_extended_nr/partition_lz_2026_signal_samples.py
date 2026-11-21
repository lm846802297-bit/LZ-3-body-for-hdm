#!/usr/bin/env python3
"""Partition Fig. S2-folded formal-B signal counts into LZ's three veto samples.

This is rate-level sample bookkeeping using the published random-coincidence
fractions. It is not a two-dimensional signal PDF or a profile likelihood.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

PROMPT_FRACTION = 1.0e-4
DELAYED_FRACTION = 2.86e-2
SCIENCE_FRACTION = 1.0 - PROMPT_FRACTION - DELAYED_FRACTION
MODEL_NAMES = (
    "sufian2017_unit_current",
    "alexandrou2020_charge_weighted_converted",
    "alexandrou2026_continuum_unit_current",
)
INPUT_FILENAME = "lz_2026_afh7_hybrid9_rate_level_event_yields.csv"
OUTPUT_FILENAME = "lz_2026_B_signal_three_sample_partition.csv"


def load_source_rows(input_root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for model in MODEL_NAMES:
        source = input_root / "B-detector" / model / INPUT_FILENAME
        if not source.is_file():
            raise FileNotFoundError(source)
        with source.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                row["strange_model"] = model
                rows.append(row)
    if len(rows) != 24:
        raise ValueError(f"expected 24 rows (3 strange-current inputs x 8 scenarios), got {len(rows)}")
    return rows


def partition_rows(source_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in source_rows:
        if row["detector_efficiency_applied"].lower() != "true":
            raise ValueError("input must already include the LZ Fig. S2 final efficiency")
        if row["energy_resolution_smearing_applied"].lower() != "false":
            raise ValueError("unexpected energy-resolution treatment in rate-level input")
        if row["two_dimensional_signal_pdf_applied"].lower() != "false":
            raise ValueError("input must be a rate-level yield, not a 2D signal PDF")
        if row["background_likelihood_applied"].lower() != "false":
            raise ValueError("input must not already include a background likelihood")

        total = float(row["expected_events_in_high_efficiency_window"])
        candidate = float(row["expected_events_in_candidate_statistical_slice"])
        science = total * SCIENCE_FRACTION
        prompt = total * PROMPT_FRACTION
        delayed = total * DELAYED_FRACTION
        closure = math.fsum((science, prompt, delayed)) - total
        if not math.isclose(closure, 0.0, rel_tol=0.0, abs_tol=max(1e-300, abs(total) * 2e-15)):
            raise AssertionError(f"three-sample partition does not close for {row['benchmark']}")

        output.append({
            "strange_model": row["strange_model"],
            "benchmark": row["benchmark"],
            "afh_scenario": row["scenario"],
            "ms_MeV": row["ms_MeV"],
            "delta_m_MeV": row["delta_m_MeV"],
            "exposure_tonne_year": row["exposure_tonne_year"],
            "exposure_kg_day": row["exposure_kg_day"],
            "expected_events_after_FigS2_before_veto": total,
            "expected_events_science": science,
            "expected_events_prompt_veto": prompt,
            "expected_events_delayed_veto": delayed,
            "sample_sum_closure_abs": closure,
            "candidate_slice_events_after_FigS2_before_veto": candidate,
            "candidate_slice_events_science": candidate * SCIENCE_FRACTION,
            "candidate_slice_events_prompt_veto": candidate * PROMPT_FRACTION,
            "candidate_slice_events_delayed_veto": candidate * DELAYED_FRACTION,
            "science_fraction": SCIENCE_FRACTION,
            "prompt_fraction": PROMPT_FRACTION,
            "delayed_fraction": DELAYED_FRACTION,
            "prompt_to_science_ratio": PROMPT_FRACTION / SCIENCE_FRACTION,
            "delayed_to_science_ratio": DELAYED_FRACTION / SCIENCE_FRACTION,
            "energy_resolution_smearing_applied": False,
            "two_dimensional_signal_pdf_applied": False,
            "background_likelihood_applied": False,
            "is_exclusion_limit": False,
        })
    return output


def write_outputs(rows: list[dict[str, object]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_csv = output_dir / OUTPUT_FILENAME
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    metadata = {
        "status": "RATE_LEVEL_SAMPLE_PARTITION_DIAGNOSTIC",
        "input_rows": len(rows),
        "source_input_artifact": {
            "workflow_run_id": 44662497177,
            "artifact_id": 14596147908,
            "artifact_name": "finite-nucleon-form-factor-B-baseline",
            "sha256": "f5c1d8d791bffff3159a6e279e5a0e68b705bf07466be6b489ba9a49e29ce7ac",
        },
        "source_models": list(MODEL_NAMES),
        "sample_fractions": {
            "science": SCIENCE_FRACTION,
            "prompt_veto": PROMPT_FRACTION,
            "delayed_veto": DELAYED_FRACTION,
            "sum": SCIENCE_FRACTION + PROMPT_FRACTION + DELAYED_FRACTION,
        },
        "partition_assumption": "prompt and delayed veto classes are mutually exclusive; delayed events are outside the prompt window",
        "published_signal_yield_crosscheck": {
            "prompt_over_science_from_LZ_Table_S1": 1.0e-4,
            "delayed_over_science_from_LZ_Table_S2": 3.1e-2,
            "partition_prompt_over_science": PROMPT_FRACTION / SCIENCE_FRACTION,
            "partition_delayed_over_science": DELAYED_FRACTION / SCIENCE_FRACTION,
            "note": "Table S1/S2 signal yields are rounded, fit-dependent cross-checks; the central partition uses the published random-coincidence fractions.",
        },
        "efficiency_source": "LZ 2026 Supplemental Fig. S2 final cumulative efficiency, already applied in the input B-detector rate-yield tables",
        "veto_source": "LZ 2026 main text random-coincidence losses: 0.01% prompt and 2.86% delayed",
        "limitations": [
            "Rate-level sample partition only; no sample-specific S1c/log10(S2c) signal PDFs.",
            "No official fiducial-volume position map or position-reconstruction smearing.",
            "No event-level Skin/OD simulation; only published random-coincidence central fractions are applied.",
            "No background component PDFs, nuisance covariance, or unbinned extended likelihood.",
            "Not an official LZ likelihood, confidence interval, or exclusion.",
        ],
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True,
                        help="Directory containing B-detector/<model>/ rate-yield CSVs")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    write_outputs(partition_rows(load_source_rows(args.input_root)), args.output_dir)


if __name__ == "__main__":
    main()
