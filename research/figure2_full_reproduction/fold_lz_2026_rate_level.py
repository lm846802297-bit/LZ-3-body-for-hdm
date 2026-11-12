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
LZ_CANDIDATE_ENERGY_KEV = 248.0
LZ_CANDIDATE_STAT_UNCERTAINTY_KEV = 23.0


def read_xy(path: Path, x_key: str, y_key: str) -> tuple[list[float], list[float]]:
    xs: list[float] = []
    ys: list[float] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            xs.append(float(row[x_key]))
            ys.append(float(row[y_key]))
    order = sorted(range(len(xs)), key=xs.__getitem__)
    xs = [xs[i] for i in order]
    ys = [ys[i] for i in order]
    if len(xs) < 2:
        raise ValueError(f"Need at least two data points in {path}")
    if any(not math.isfinite(x) for x in xs) or any(not math.isfinite(y) for y in ys):
        raise ValueError(f"Non-finite x/y value in {path}")
    if any(x1 <= x0 for x0, x1 in zip(xs, xs[1:])):
        raise ValueError(f"x values must be strictly increasing in {path}")
    return xs, ys


def read_efficiency_curves(
    path: Path,
) -> tuple[list[float], list[float], list[float], list[float]]:
    """Read central and gray-envelope curves; fall back to central-only CSVs."""
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) < 2:
        raise ValueError(f"Need at least two efficiency samples in {path}")
    rows.sort(key=lambda row: float(row["ER_keV"]))
    xs = [float(row["ER_keV"]) for row in rows]
    central = [float(row["efficiency_final_WS_ROI"]) for row in rows]
    lower = [
        float(row.get("efficiency_lower_envelope") or row["efficiency_final_WS_ROI"])
        for row in rows
    ]
    upper = [
        float(row.get("efficiency_upper_envelope") or row["efficiency_final_WS_ROI"])
        for row in rows
    ]
    if any(not math.isfinite(x) for x in xs):
        raise ValueError(f"Non-finite recoil energy in {path}")
    if any(x1 <= x0 for x0, x1 in zip(xs, xs[1:])):
        raise ValueError(f"Efficiency recoil energies must be strictly increasing in {path}")
    for lo, mid, hi in zip(lower, central, upper):
        if not all(math.isfinite(v) and 0.0 <= v <= 1.0 for v in (lo, mid, hi)):
            raise ValueError(f"Efficiency values must be finite and lie in [0, 1] in {path}")
        if lo > mid + 2e-3 or mid > hi + 2e-3:
            raise ValueError(f"Central efficiency is outside its gray envelope in {path}")
    return xs, central, lower, upper


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


def integrate_piecewise_linear_product(
    rate_x: list[float],
    rate_y: list[float],
    efficiency_x: list[float],
    efficiency_y: list[float],
    lo: float,
    hi: float,
) -> tuple[float, float]:
    """Integrate rate and rate*efficiency exactly for linear interpolation.

    The union of both input knot sets partitions the interval into segments on
    which the rate and efficiency are each linear. Their product is quadratic,
    so its integral is analytic on every segment.
    """
    if not lo < hi:
        raise ValueError("require lo < hi")
    if rate_x[0] > lo or rate_x[-1] < hi:
        raise ValueError("rate spectrum does not cover the full ROI")
    if efficiency_x[0] > lo or efficiency_x[-1] < hi:
        raise ValueError("efficiency curve does not cover the full ROI")
    knots = sorted(
        {lo, hi}
        | {x for x in rate_x if lo < x < hi}
        | {x for x in efficiency_x if lo < x < hi}
    )
    raw = 0.0
    weighted = 0.0
    for a, b in zip(knots, knots[1:]):
        width = b - a
        r0 = interpolate(a, rate_x, rate_y)
        r1 = interpolate(b, rate_x, rate_y)
        e0 = interpolate(a, efficiency_x, efficiency_y)
        e1 = interpolate(b, efficiency_x, efficiency_y)
        dr = r1 - r0
        de = e1 - e0
        raw += 0.5 * width * (r0 + r1)
        weighted += width * (
            r0 * e0 + 0.5 * (r0 * de + e0 * dr) + (dr * de) / 3.0
        )
    return raw, weighted


def candidate_tail_bounds(roi_min_keV: float, roi_max_keV: float) -> tuple[float, float]:
    """Intersect the candidate's +/- statistical-energy interval with the ROI."""
    lo = max(roi_min_keV, LZ_CANDIDATE_ENERGY_KEV - LZ_CANDIDATE_STAT_UNCERTAINTY_KEV)
    hi = min(roi_max_keV, LZ_CANDIDATE_ENERGY_KEV + LZ_CANDIDATE_STAT_UNCERTAINTY_KEV)
    if not lo < hi:
        raise ValueError("the LZ candidate statistical-energy interval does not overlap the ROI")
    return lo, hi


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
    if not args.spectrum_dir.is_dir():
        raise FileNotFoundError(
            f"continuous-spectrum directory is missing: {args.spectrum_dir}; "
            "the rate-level fold must run after the spectra have been archived"
        )
    efficiency_x, efficiency_y, efficiency_lower, efficiency_upper = read_efficiency_curves(
        args.efficiency_csv
    )
    if efficiency_x[0] > args.roi_min_keV or efficiency_x[-1] < args.roi_max_keV:
        raise ValueError("digitized LZ efficiency curves do not cover the requested ROI")
    exposure_kg_day = args.exposure_tonne_year * TONNE_YEAR_TO_KG_DAY
    candidate_tail_min, candidate_tail_max = candidate_tail_bounds(
        args.roi_min_keV, args.roi_max_keV
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)

    output_rows = []
    spectrum_files = []
    max_dense_vs_exact = 0.0
    max_refinement = 0.0
    benchmark_dirs = sorted(p for p in args.spectrum_dir.iterdir() if p.is_dir())
    for benchmark_dir in benchmark_dirs:
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
            if rate_x[0] > args.roi_min_keV or rate_x[-1] < args.roi_max_keV:
                raise RuntimeError(f"Spectrum does not cover the full ROI: {spectrum_path} ({model})")
            if any(not math.isfinite(x) for x in rate_x) or any(not math.isfinite(y) or y < 0.0 for y in rate_y):
                raise RuntimeError(f"Non-finite or negative rate in {spectrum_path} ({model})")
            reference = rows[0]
            coupling_sq = float(reference["coupling_product_sq"])
            if any(
                not math.isclose(float(r["coupling_product_sq"]), coupling_sq, rel_tol=1e-12)
                for r in rows
            ):
                raise RuntimeError(f"Coupling normalization varies with recoil energy: {spectrum_path}")

            raw_integral, weighted_integral = integrate_piecewise_linear_product(
                rate_x, rate_y, efficiency_x, efficiency_y,
                args.roi_min_keV, args.roi_max_keV,
            )
            _, weighted_lower = integrate_piecewise_linear_product(
                rate_x, rate_y, efficiency_x, efficiency_lower,
                args.roi_min_keV, args.roi_max_keV,
            )
            _, weighted_upper = integrate_piecewise_linear_product(
                rate_x, rate_y, efficiency_x, efficiency_upper,
                args.roi_min_keV, args.roi_max_keV,
            )
            _, weighted_candidate_tail = integrate_piecewise_linear_product(
                rate_x, rate_y, efficiency_x, efficiency_y,
                candidate_tail_min, candidate_tail_max,
            )
            raw_dense, weighted_dense = integrate_weighted_rate(
                rate_x, rate_y, efficiency_x, efficiency_y,
                args.roi_min_keV, args.roi_max_keV, args.integration_steps,
            )
            raw_dense_fine, weighted_dense_fine = integrate_weighted_rate(
                rate_x, rate_y, efficiency_x, efficiency_y,
                args.roi_min_keV, args.roi_max_keV, 2 * args.integration_steps,
            )
            dense_vs_exact = abs(weighted_dense / weighted_integral - 1.0) if weighted_integral > 0.0 else 0.0
            refinement = abs(weighted_dense_fine / weighted_dense - 1.0) if weighted_dense > 0.0 else 0.0
            max_dense_vs_exact = max(max_dense_vs_exact, dense_vs_exact)
            max_refinement = max(max_refinement, refinement)
            expected = exposure_kg_day * weighted_integral
            expected_lower = exposure_kg_day * weighted_lower
            expected_upper = exposure_kg_day * weighted_upper
            expected_candidate_tail = exposure_kg_day * weighted_candidate_tail
            candidate_tail_fraction = (
                weighted_candidate_tail / weighted_integral if weighted_integral > 0.0 else 0.0
            )
            ideal = exposure_kg_day * raw_integral
            effective_efficiency = weighted_integral / raw_integral if raw_integral > 0.0 else 0.0
            effective_efficiency_lower = weighted_lower / raw_integral if raw_integral > 0.0 else 0.0
            effective_efficiency_upper = weighted_upper / raw_integral if raw_integral > 0.0 else 0.0
            coupling_sq_one_event = coupling_sq / expected if expected > 0.0 else None
            coupling_sq_one_event_lower = coupling_sq / expected_lower if expected_lower > 0.0 else None
            coupling_sq_one_event_upper = coupling_sq / expected_upper if expected_upper > 0.0 else None
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
                "spectrum_weighted_mean_efficiency_lower_envelope": effective_efficiency_lower,
                "spectrum_weighted_mean_efficiency_upper_envelope": effective_efficiency_upper,
                "efficiency_envelope_treatment": "gray detector-systematic range; not assigned a confidence level by LZ",
                "integration_method": "exact analytic integral of piecewise-linear rate times piecewise-linear efficiency",
                "dense_trapezoid_relative_difference_vs_exact": dense_vs_exact,
                "dense_trapezoid_refinement_relative_difference": refinement,
                "expected_events_in_high_efficiency_window": expected,
                "expected_events_efficiency_lower_envelope": expected_lower,
                "expected_events_efficiency_upper_envelope": expected_upper,
                "candidate_tail_min_keV": candidate_tail_min,
                "candidate_tail_max_keV": candidate_tail_max,
                "expected_events_in_candidate_statistical_slice": expected_candidate_tail,
                "fraction_expected_events_in_candidate_statistical_slice": candidate_tail_fraction,
                "ideal_100pct_efficiency_events_in_window": ideal,
                "coupling_product_sq_reference": coupling_sq,
                "coupling_product_sq_for_one_expected_event_at_fixed_g2": coupling_sq_one_event,
                "coupling_product_sq_for_one_event_lower_envelope": coupling_sq_one_event_lower,
                "coupling_product_sq_for_one_event_upper_envelope": coupling_sq_one_event_upper,
                "g2_for_conditional_pole_width": float(reference["g2"]),
                "width_scheme": reference["width_scheme"],
                "mass_scheme": reference["mass_scheme"],
                "response_q_convention": "exact_spatial",
                "detector_efficiency_applied": True,
                "energy_resolution_smearing_applied": False,
                "two_dimensional_signal_pdf_applied": False,
                "background_likelihood_applied": False,
                "is_exclusion_limit": False,
            })

    if not spectrum_files:
        raise RuntimeError(f"No continuous spectrum CSV files found under {args.spectrum_dir}")
    if not output_rows:
        raise RuntimeError(f"No usable SHM-cutoff model spectra found under {args.spectrum_dir}")

    output_csv = args.out_dir / "lz_2026_rate_level_event_yields.csv"
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    metadata = {
        "calculation": "LZ 2026 efficiency-weighted rate-level expected event yield",
        "roi_keV": [args.roi_min_keV, args.roi_max_keV],
        "candidate_tail_diagnostic": {
            "candidate_energy_keV": LZ_CANDIDATE_ENERGY_KEV,
            "candidate_statistical_uncertainty_keV": LZ_CANDIDATE_STAT_UNCERTAINTY_KEV,
            "candidate_systematic_uncertainty_keV": 23.0,
            "integration_interval_keV": [candidate_tail_min, candidate_tail_max],
            "upper_edge_clipped_by_search_roi": candidate_tail_max < LZ_CANDIDATE_ENERGY_KEV + LZ_CANDIDATE_STAT_UNCERTAINTY_KEV,
            "systematic_energy_uncertainty_used": False,
            "interpretation": "high-energy spectral-shape diagnostic only; no energy-resolution smearing or event likelihood",
        },
        "exposure_tonne_year": args.exposure_tonne_year,
        "exposure_kg_day": exposure_kg_day,
        "efficiency_curve": str(args.efficiency_csv),
        "efficiency_curve_sha256": sha256(args.efficiency_csv),
        "efficiency_source": "LZ 2026 Fig. S2 black central final WIMP-search ROI curve and gray uncertainty envelope, vector-extracted",
        "efficiency_envelope_treatment": "gray detector-systematic range; no confidence level assigned by LZ",
        "efficiency_envelope_applied_to_yield_range": True,
        "spectrum_files": spectrum_files,
        "dense_trapezoid_crosscheck_steps": args.integration_steps,
        "integration_method": "exact analytic integration over the union of rate-spectrum and efficiency-curve knots, assuming linear interpolation of each input",
        "maximum_dense_trapezoid_relative_difference_vs_exact": max_dense_vs_exact,
        "maximum_dense_trapezoid_refinement_relative_difference": max_refinement,
        "nuclear_response_models": ["GCN", "JJ55"],
        "interpretation": (
            "Central expected signal counts and lower/upper detector-systematic yield variations "
            "in the published high-efficiency true-NR window. Rates are pre-detector and are folded "
            "with the digitized central final-ROI efficiency and its gray Fig. S2 envelope."
        ),
        "coupling_scaling": (
            "The one-event coupling normalization assumes the reference g2 and conditional "
            "pole width are held fixed; it is a rate normalization, not a confidence limit."
        ),
        "limitations": [
            "gray efficiency envelope is propagated as a systematic range but has no assigned confidence level",
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
