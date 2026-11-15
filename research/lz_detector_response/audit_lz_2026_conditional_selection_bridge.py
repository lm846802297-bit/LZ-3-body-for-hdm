#!/usr/bin/env python3
"""Audit the rate-level bridge between NEST+WS-ROI and residual Fig. S2 stages.

This is a conditional-efficiency bookkeeping diagnostic. It does not create a
two-dimensional SS/data-analysis migration kernel and must not be used as a
global correction to the 2D signal intensity.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


def _finite_probability(value: Any, label: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < -1e-10 or number > 1.0 + 1e-8:
        raise ValueError(f"{label} is not a finite probability: {number}")
    return min(1.0, max(0.0, number))


def build_bridge_rows(
    event_weighted_summary: dict,
    selection_stage_summary: dict,
    response_family: str | None = None,
) -> list[dict]:
    """Build matched benchmark/nuclear/family conditional-stage comparisons."""
    if not isinstance(event_weighted_summary.get("comparisons"), list):
        raise ValueError("event-weighted summary is missing comparisons")
    if not isinstance(selection_stage_summary.get("results"), list):
        raise ValueError("selection-stage summary is missing results")

    selection = {}
    for row in selection_stage_summary["results"]:
        key = (row["benchmark"], row["model"])
        if key in selection:
            raise ValueError(f"duplicate selection-stage row: {key}")
        selection[key] = row

    event = {}
    for row in event_weighted_summary["comparisons"]:
        key = (
            row["benchmark"], row["nuclear_model"],
            row["response_family"], row["acceptance_mode"],
        )
        if key in event:
            raise ValueError(f"duplicate event-weighted row: {key}")
        event[key] = row

    output = []
    for key, roi_row in sorted(event.items()):
        benchmark, nuclear_model, family, mode = key
        if mode != "ws_roi":
            continue
        if response_family is not None and family != response_family:
            continue
        nest_key = (benchmark, nuclear_model, family, "nest")
        if nest_key not in event:
            raise ValueError(f"missing matched NEST-only row: {nest_key}")
        stage_key = (benchmark, nuclear_model)
        if stage_key not in selection:
            raise ValueError(f"missing Fig. S2 stage row: {stage_key}")

        nest_row = event[nest_key]
        stage_row = selection[stage_key]
        conditional = stage_row["conditional_stage_efficiencies"]

        raw_rate = float(roi_row["exact_raw_rate_events_kg_day"])
        nest_rate = float(nest_row["event_weighted_rate_events_kg_day"])
        roi_rate = float(roi_row["event_weighted_rate_events_kg_day"])
        if not all(math.isfinite(x) and x >= 0.0 for x in (raw_rate, nest_rate, roi_rate)):
            raise ValueError(f"invalid event-weighted rates for {key}")
        if raw_rate <= 0.0 or nest_rate <= 0.0:
            raise ValueError(f"non-positive denominator rate for {key}")

        epsilon_nest = _finite_probability(nest_rate / raw_rate, "NEST acceptance")
        epsilon_roi_given_nest = _finite_probability(
            roi_rate / nest_rate, "WS ROI given NEST"
        )
        epsilon_ss_da = _finite_probability(
            conditional["ss_analysis_given_s1"], "Fig. S2 SS+DA conditional"
        )
        epsilon_figs2_roi = _finite_probability(
            conditional["roi_given_ss_analysis"], "Fig. S2 ROI conditional"
        )
        epsilon_figs2_final = _finite_probability(
            conditional["total_final"], "Fig. S2 final cumulative"
        )
        epsilon_factored = epsilon_nest * epsilon_roi_given_nest * epsilon_ss_da
        ratio = (
            epsilon_factored / epsilon_figs2_final
            if epsilon_figs2_final > 0.0 else math.nan
        )

        output.append({
            "benchmark": benchmark,
            "nuclear_model": nuclear_model,
            "response_family": family,
            "raw_rate_events_kg_day": raw_rate,
            "nest_rate_events_kg_day": nest_rate,
            "nest_plus_ws_roi_rate_events_kg_day": roi_rate,
            "epsilon_nest": epsilon_nest,
            "epsilon_ws_roi_given_nest": epsilon_roi_given_nest,
            "epsilon_figs2_trigger": _finite_probability(
                conditional["trigger"], "Fig. S2 trigger"
            ),
            "epsilon_figs2_s1_given_trigger": _finite_probability(
                conditional["s1_given_trigger"], "Fig. S2 S1 given trigger"
            ),
            "epsilon_figs2_ss_da_given_pre_roi": epsilon_ss_da,
            "epsilon_figs2_roi_given_pre_roi": epsilon_figs2_roi,
            "epsilon_figs2_final": epsilon_figs2_final,
            "epsilon_factorized_nest_roi_ss_da": epsilon_factored,
            "factorized_to_figs2_final_ratio": ratio,
            "relative_difference_factorized_vs_figs2": ratio - 1.0,
        })

    if not output:
        raise ValueError("no matched WS-ROI rows found for requested response family")
    return output


def summarize(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("cannot summarize an empty conditional-selection bridge")
    families = {row["response_family"] for row in rows}
    if len(families) != 1:
        raise ValueError("one bridge summary must contain exactly one response family")
    response_family = next(iter(families))
    finite = [
        abs(row["relative_difference_factorized_vs_figs2"])
        for row in rows
        if math.isfinite(row["relative_difference_factorized_vs_figs2"])
    ]
    return {
        "study": "conditional residual-selection efficiency bridge",
        "status": "RATE_LEVEL_FACTORISATION_DIAGNOSTIC_ONLY",
        "response_family": response_family,
        "n_rows": len(rows),
        "max_absolute_relative_difference_vs_figs2": max(finite) if finite else None,
        "interpretation": (
            "The NEST-only and WS-ROI factors are derived from the event-weighted "
            "2D response; the residual SS+data-analysis factor is the energy-integrated "
            "Fig. S2 green/orange ratio. Their product is a rate-level factorisation "
            "test only. Fig. S2 does not provide the conditional 2D migration kernel."
        ),
        "prohibited_use": (
            "Do not multiply the full Fig. S2 black cumulative curve into the "
            "existing NEST+WS-ROI 2D intensity. Do not treat the factorised residual "
            "efficiency as an exact 2D selection correction."
        ),
        "rows": rows,
    }


def write_outputs(rows: list[dict], out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = summarize(rows)
    json_path = out_dir / "conditional_selection_bridge_summary.json"
    csv_path = out_dir / "conditional_selection_bridge.csv"
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return {"summary": summary, "json_path": str(json_path), "csv_path": str(csv_path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-weighted-summary", type=Path, required=True)
    parser.add_argument("--selection-stage-summary", type=Path, required=True)
    parser.add_argument("--response-family", default=None)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    event_summary = json.loads(args.event_weighted_summary.read_text(encoding="utf-8"))
    selection_summary = json.loads(args.selection_stage_summary.read_text(encoding="utf-8"))
    rows = build_bridge_rows(event_summary, selection_summary, args.response_family)
    result = write_outputs(rows, args.out_dir)
    print(json.dumps({
        "status": result["summary"]["status"],
        "n_rows": result["summary"]["n_rows"],
        "max_absolute_relative_difference_vs_figs2": (
            result["summary"]["max_absolute_relative_difference_vs_figs2"]
        ),
        "summary_json": result["json_path"],
        "summary_csv": result["csv_path"],
    }, indent=2))


if __name__ == "__main__":
    main()
