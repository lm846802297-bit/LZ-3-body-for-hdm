#!/usr/bin/env python3
"""Efficiency-weighted LZ 2026 high-efficiency-window event-yield estimate.

This is a rate-level fold only. It does not construct S1c/log10(S2c) PDFs,
profile the LZ background likelihood, or produce an exclusion limit.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

TONNE_YEAR_TO_KG_DAY = 1000.0 * 365.25
DEFAULT_ROI_MIN_KEV = 5.4
DEFAULT_ROI_MAX_KEV = 269.9


def read_xy(path: Path, x_key: str, y_key: str) -> tuple[list[float], list[float]]:
    xs: list[float] = []
    ys: list[float] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            xs.append(float(row[x_key]))
            ys.append(float(row[y_key]))
    order = sorted(range(len(xs)), key=xs.__getitem__)
    return [xs[i] for i in order], [ys[i] for i in order]


def interpolate(x: float, xs: list[float], ys: list[float]) -> float:
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    lo, hi = 0, len(xs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xs[mid] <= x:
            lo = mid
        else:
            hi = mid
    fraction = (x - xs[lo]) / (xs[hi] - xs[lo])
    return ys[lo] + fraction * (ys[hi] - ys[lo])


def integrate_weighted_rate(
    rate_x: list[float],
    rate_y: list[float],
    efficiency_x: list[float],
    efficiency_y: list[float],
    lo: float,
    hi: float,
    n_steps: int = 10000,
) -> tuple[float, float]:
    """Return raw and efficiency-weighted integrals in events/(kg day)."""
    if not (lo < hi and n_steps >= 2):
        raise ValueError("require lo < hi and n_steps >= 2")
    step = (hi - lo) / n_steps
    raw_values = []
    weighted_values = []
    for i in range(n_steps + 1):
        energy = lo + i * step
        rate = interpolate(energy, rate_x, rate_y)
        efficiency = interpolate(energy, efficiency_x, efficiency_y)
        raw_values.append(rate)
        weighted_values.append(rate * efficiency)

    def trapezoid(values: list[float]) -> float:
        return step * (
            0.5 * values[0] + math.fsum(values[1:-1]) + 0.5 * values[-1]
        )

    return trapezoid(raw_values), trapezoid(weighted_values)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spectrum-dir",
        type=Path,
        default=Path("research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum"),
    )
    parser.add_argument(
        "--efficiency-csv",
        type=Path,
        default=Path("research/lz_detector_response/lz_2026_extended_nr/lz_2026_nr_efficiency_digitized.csv"),
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--roi-min-keV", type=float, default=DEFAULT_ROI_MIN_KEV)
    parser.add_argument("--roi-max-keV", type=float, default=DEFAULT_ROI_MAX_KEV)
    parser.add_argument("--exposure-tonne-year", type=float, default=2.84)
    parser.add_argument("--integration-steps", type=int, default=10000)
    args = parser.parse_args()

    if not args.efficiency_csv.is_file():
        raise FileNotFoundError(args.efficiency_csv)
    efficiency_x, efficiency_y = read_xy(
        args.efficiency_csv, "ER_keV", "efficiency_final_WS_ROI"
    )
    exposure_kg_day = args.exposure_tonne_year * TONNE_YEAR_TO_KG_DAY
    args.out_dir.mkdir(parents=True, exist_ok=True)

    output_rows = []
    spectrum_files = []
    for benchmark_dir in sorted(p for p in args.spectrum_dir.iterdir() if p.is_dir()):
        spectrum_path = benchmark_dir / "natural_xenon_continuous_spectrum.csv"
        if not spectrum_path.is_file():
            continue
        spectrum_files.append(str(spectrum_path))
        grouped: dict[str, list[dict[str, str]]] = {}
        with spectrum_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("halo_model") != "shm_cutoff":
                    continue
                grouped.setdefault(row["model"], []).append(row)

        for model, rows in sorted(grouped.items()):
            rows.sort(key=lambda r: float(r["ER_keV"]))
            rate_x = [float(r["ER_keV"]) for r in rows]
            rate_y = [float(r["rate_events_kg_day_keV"]) for r in rows]
            if len(rate_x) < 2:
                raise RuntimeError(f"Insufficient spectrum points: {spectrum_path} ({model})")
            reference = rows[0]
            coupling_sq = float(reference["coupling_product_sq"])
            if any(
                not math.isclose(float(r["coupling_product_sq"]), coupling_sq, rel_tol=1e-12)
                for r in rows
            ):
                raise RuntimeError(f"Coupling normalization varies with recoil energy: {spectrum_path}")

            raw_integral, weighted_integral = integrate_weighted_rate(
                rate_x, rate_y, efficiency_x, efficiency_y,
                args.roi_min_keV, args.roi_max_keV, args.integration_steps,
            )
            expected = exposure_kg_day * weighted_integral
            ideal = exposure_kg_day * raw_integral
            effective_efficiency = weighted_integral / raw_integral if raw_integral > 0.0 else 0.0
            coupling_sq_one_event = coupling_sq / expected if expected > 0.0 else None
            output_rows.append({
                "benchmark": benchmark_dir.name,
                "model": model,
                "halo_model": "shm_cutoff",
                "roi_min_keV": args.roi_min_keV,
                "roi_max_keV": args.roi_max_keV,
                "exposure_tonne_year": args.exposure_tonne_year,
                "exposure_kg_day": exposure_kg_day,
                "raw_roi_integral_events_kg_day": raw_integral,
                "efficiency_weighted_integral_events_kg_day": weighted_integral,
                "spectrum_weighted_mean_efficiency": effective_efficiency,
                "expected_events_in_high_efficiency_window": expected,
                "ideal_100pct_efficiency_events_in_window": ideal,
                "coupling_product_sq_reference": coupling_sq,
                "coupling_product_sq_for_one_expected_event_at_fixed_g2": coupling_sq_one_event,
                "g2_for_conditional_pole_width": float(reference["g2"]),
                "width_scheme": reference["width_scheme"],
                "mass_scheme": reference["mass_scheme"],
                "response_q_convention": reference["response_q_convention"],
                "detector_efficiency_applied": True,
                "energy_resolution_smearing_applied": False,
                "two_dimensional_signal_pdf_applied": False,
                "background_likelihood_applied": False,
                "is_exclusion_limit": False,
            })

    if not output_rows:
        raise RuntimeError(f"No continuous spectra found under {args.spectrum_dir}")

    output_csv = args.out_dir / "lz_2026_rate_level_event_yields.csv"
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    metadata = {
        "calculation": "LZ 2026 efficiency-weighted rate-level expected event yield",
        "roi_keV": [args.roi_min_keV, args.roi_max_keV],
        "exposure_tonne_year": args.exposure_tonne_year,
        "exposure_kg_day": exposure_kg_day,
        "efficiency_curve": str(args.efficiency_csv),
        "efficiency_curve_sha256": sha256(args.efficiency_csv),
        "efficiency_source": "LZ 2026 Fig. S2 black final WIMP-search ROI curve, vector-extracted",
        "spectrum_files": spectrum_files,
        "integration_steps": args.integration_steps,
        "nuclear_response_models": ["GCN", "JJ55"],
        "interpretation": (
            "Expected signal counts in the published high-efficiency true-NR window. "
            "Rates are pre-detector and are folded with the digitized final ROI efficiency."
        ),
        "coupling_scaling": (
            "The one-event coupling normalization assumes the reference g2 and conditional "
            "pole width are held fixed; it is a rate normalization, not a confidence limit."
        ),
        "limitations": [
            "LZ efficiency uncertainty band not propagated",
            "no S1c/log10(S2c) two-dimensional signal PDFs",
            "no NEST nuisance-parameter covariance",
            "no energy-resolution smearing beyond the published efficiency curve",
            "no background model or profile likelihood",
            "not a 90% confidence-level exclusion",
            "continuous nuclear responses are GCN/JJ55, not the LZ-modified DMFormFactor-v6 inputs",
            "AFH v6.0 is available only at selected recoil points in the current archive",
        ],
    }
    (args.out_dir / "lz_2026_rate_level_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"rows": output_rows, "metadata": metadata}, indent=2))


if __name__ == "__main__":
    main()
