#!/usr/bin/env python3
"""High-statistics independent 1-keV/5-keV comparison over black-benchmark support.

The black ms=360-keV spectrum has no support below 210 keV in the archived
benchmark spectra. This targeted study increases the generated event density
to 16,000 events/keV while retaining three independent productions per grid
and per NR mean-yield family.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import audit_lz_2026_full_range_grid_independent_seeds as base

DEFAULT_ROI_MIN_KEV = 210.0
DEFAULT_ROI_MAX_KEV = 269.9
DEFAULT_BENCHMARKS = ("black_ms360_dm1",)


def configure_base(
    roi_min_keV: float = DEFAULT_ROI_MIN_KEV,
    roi_max_keV: float = DEFAULT_ROI_MAX_KEV,
    benchmarks: tuple[str, ...] = DEFAULT_BENCHMARKS,
) -> None:
    if roi_max_keV <= roi_min_keV:
        raise ValueError("ROI maximum must exceed ROI minimum")
    if not benchmarks:
        raise ValueError("at least one benchmark is required")
    base.ROI_MIN_KEV = roi_min_keV
    base.ROI_MAX_KEV = roi_max_keV
    base.BENCHMARKS = tuple(benchmarks)


def run_audit(args: argparse.Namespace) -> dict:
    original = (base.ROI_MIN_KEV, base.ROI_MAX_KEV, base.BENCHMARKS)
    try:
        configure_base(args.roi_min_keV, args.roi_max_keV, tuple(args.benchmarks))
        summary = base.run_audit(args)
    finally:
        base.ROI_MIN_KEV, base.ROI_MAX_KEV, base.BENCHMARKS = original
    one_edges = base.grid.make_edges(args.roi_min_keV, args.roi_max_keV, 1.0)
    five_edges = base.grid.make_edges(args.roi_min_keV, args.roi_max_keV, 5.0)
    summary["expected_events_per_terminal_1keV_bin"] = round(
        args.events_per_keV * (one_edges[-1] - one_edges[-2])
    )
    summary["expected_events_per_terminal_5keV_bin"] = round(
        args.events_per_keV * (five_edges[-1] - five_edges[-2])
    )
    summary["events_per_seed_per_grid"] = sum(
        round(args.events_per_keV * (hi - lo))
        for lo, hi in zip(one_edges, one_edges[1:])
    )
    summary.pop("expected_events_in_terminal_0p5keV_bin", None)
    summary.pop("expected_events_in_terminal_4p5keV_bin", None)
    summary["study"] = (
        f"high-statistics independent-seed 1-keV versus 5-keV "
        f"{args.response_family} black-support NR response audit"
    )
    summary["benchmarks"] = list(args.benchmarks)
    summary["gate"]["scope"] = (
        f"black-benchmark signal-support interval "
        f"{args.roi_min_keV:g}--{args.roi_max_keV:g} keV; "
        "GCN/JJ55; NEST and NEST+WS-ROI modes"
    )
    summary["limitations"].extend([
        "The interval begins at the first nonzero recoil-rate grid point of the black benchmark.",
        "This targeted high-statistics study does not replace the independent full-range checks of red/green/blue.",
        "The 2D TV gate remains a point-estimate engineering gate; three independent seeds do not provide a full cell-by-cell covariance matrix.",
    ])
    return summary


def write_outputs(summary: dict, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "black_full_support_grid_independent_seed_summary.json"
    comparison_path = out_dir / "black_full_support_grid_comparison.csv"
    seed_path = out_dir / "black_full_support_grid_seed_details.csv"
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    for path, rows_key in (
        (comparison_path, "comparisons"),
        (seed_path, "per_seed"),
    ):
        rows = summary[rows_key]
        with path.open("w", newline="", encoding="utf-8") as handle:
            if rows:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
    return {
        "summary_json": str(json_path),
        "comparison_csv": str(comparison_path),
        "seed_details_csv": str(seed_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response-family", choices=base.FAMILIES, required=True)
    parser.add_argument("--one-kev-response-dirs", type=Path, nargs=3, required=True)
    parser.add_argument("--five-kev-response-dirs", type=Path, nargs=3, required=True)
    parser.add_argument("--one-kev-seeds", type=int, nargs=3, required=True)
    parser.add_argument("--five-kev-seeds", type=int, nargs=3, required=True)
    parser.add_argument("--events-per-keV", type=int, default=16000)
    parser.add_argument("--roi-min-keV", type=float, default=DEFAULT_ROI_MIN_KEV)
    parser.add_argument("--roi-max-keV", type=float, default=DEFAULT_ROI_MAX_KEV)
    parser.add_argument(
        "--benchmarks", nargs="+", choices=base.BENCHMARKS,
        default=list(DEFAULT_BENCHMARKS),
    )
    parser.add_argument("--spectrum-dir", type=Path, default=Path(
        "research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum"
    ))
    parser.add_argument(
        "--nuclear-models", nargs="+", choices=base.NUCLEAR_MODELS,
        default=list(base.NUCLEAR_MODELS),
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    summary = run_audit(args)
    outputs = write_outputs(summary, args.out_dir)
    print(json.dumps({
        "response_family": summary["response_family"],
        "roi_keV": summary["true_recoil_interval_keV"],
        "gate": summary["gate"],
        "outputs": outputs,
    }, indent=2))


if __name__ == "__main__":
    main()
