#!/usr/bin/env python3
"""Reproducible high-energy LZ candidate-window nuclear-model audit.

The calculation integrates the archived unsmeared natural-xenon recoil spectra
against the digitized one-dimensional LZ final-ROI efficiency. It is a
rate-level diagnostic, not a detector-level likelihood.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
AFH_DIR = HERE / "results" / "afh7_hybrid9_continuous_2026-11-14"
GCN_DIR = ROOT / "research" / "figure2_full_reproduction" / "results" / "natural_xenon_continuous_spectrum"
EFFICIENCY_CSV = ROOT / "research" / "lz_detector_response" / "lz_2026_extended_nr" / "lz_2026_nr_efficiency_digitized.csv"

ROI_MIN_KEV = 5.4
ROI_MAX_KEV = 269.9
CANDIDATE_CENTER_KEV = 248.0
CANDIDATE_SIGMA_KEV = 23.0
TAIL_MIN_KEV = max(ROI_MIN_KEV, CANDIDATE_CENTER_KEV - CANDIDATE_SIGMA_KEV)
TAIL_MAX_KEV = min(ROI_MAX_KEV, CANDIDATE_CENTER_KEV + CANDIDATE_SIGMA_KEV)
EXPOSURE_TONNE_YEAR = 2.84
EXPOSURE_KG_DAY = EXPOSURE_TONNE_YEAR * 1000.0 * 365.25
BENCHMARKS = ("red_ms200_dm1", "green_ms300_dm1", "black_ms360_dm1", "blue_ms300_dm10")
AFH_SCENARIOS = (
    "AFH-7",
    "Hybrid-9 (AFH-7 + Helm-2)",
    "AFH-7 + A2-2 ceiling",
    "Helm-9",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    return rows


def read_efficiency(path: Path) -> tuple[list[float], dict[str, list[float]]]:
    rows = read_csv(path)
    rows.sort(key=lambda row: float(row["ER_keV"]))
    x = [float(row["ER_keV"]) for row in rows]
    columns = {
        "central": [float(row["efficiency_final_WS_ROI"]) for row in rows],
        "lower": [float(row["efficiency_lower_envelope"]) for row in rows],
        "upper": [float(row["efficiency_upper_envelope"]) for row in rows],
    }
    if any(b <= a for a, b in zip(x, x[1:])):
        raise ValueError("efficiency recoil-energy grid is not strictly increasing")
    for i in range(len(x)):
        lo, mid, hi = columns["lower"][i], columns["central"][i], columns["upper"][i]
        if not all(math.isfinite(v) and 0.0 <= v <= 1.0 for v in (lo, mid, hi)):
            raise ValueError("efficiency values must be finite and lie in [0,1]")
        if lo > mid + 2.0e-3 or mid > hi + 2.0e-3:
            raise ValueError("central efficiency is outside its digitization envelope")
    return x, columns


def interpolate(x: float, xs: list[float], ys: list[float]) -> float:
    if x < xs[0] or x > xs[-1]:
        raise ValueError(f"interpolation point {x} outside [{xs[0]}, {xs[-1]}]")
    if x == xs[0]:
        return ys[0]
    if x == xs[-1]:
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


def integrate_piecewise_linear_product(
    rate_x: list[float],
    rate_y: list[float],
    efficiency_x: list[float],
    efficiency_y: list[float],
    lo: float,
    hi: float,
) -> tuple[float, float]:
    """Integrate rate and rate*efficiency exactly for piecewise-linear inputs."""
    if not lo < hi:
        raise ValueError("require lo < hi")
    if rate_x[0] > lo or rate_x[-1] < hi:
        raise ValueError("rate grid does not cover integration interval")
    if efficiency_x[0] > lo or efficiency_x[-1] < hi:
        raise ValueError("efficiency grid does not cover integration interval")
    knots = sorted(
        {lo, hi}
        | {x for x in rate_x if lo < x < hi}
        | {x for x in efficiency_x if lo < x < hi}
    )
    raw_segments = []
    weighted_segments = []
    for a, b in zip(knots, knots[1:]):
        width = b - a
        r0 = interpolate(a, rate_x, rate_y)
        r1 = interpolate(b, rate_x, rate_y)
        e0 = interpolate(a, efficiency_x, efficiency_y)
        e1 = interpolate(b, efficiency_x, efficiency_y)
        dr, de = r1 - r0, e1 - e0
        raw_segments.append(0.5 * width * (r0 + r1))
        weighted_segments.append(
            width * (r0 * e0 + 0.5 * (r0 * de + e0 * dr) + dr * de / 3.0)
        )
    return math.fsum(raw_segments), math.fsum(weighted_segments)


def _validated_rate_rows(rows: list[dict[str, str]], model_key: str, model: str):
    selected = [row for row in rows if row.get(model_key) == model]
    if not selected:
        raise ValueError(f"missing spectrum group {model}")
    selected.sort(key=lambda row: float(row["ER_keV"]))
    x = [float(row["ER_keV"]) for row in selected]
    y = [float(row["rate_events_kg_day_keV"]) for row in selected]
    if len(x) < 2 or any(b <= a for a, b in zip(x, x[1:])):
        raise ValueError(f"{model}: recoil grid is not strictly increasing")
    if any(not math.isfinite(v) or v < 0.0 for v in y):
        raise ValueError(f"{model}: rate contains a non-finite or negative value")
    return selected, x, y


def _integral_bundle(x, y, efficiency_x, efficiency):
    tail = {}
    full = {}
    for name in ("central", "lower", "upper"):
        _, tail[name] = integrate_piecewise_linear_product(
            x, y, efficiency_x, efficiency[name], TAIL_MIN_KEV, TAIL_MAX_KEV
        )
        _, full[name] = integrate_piecewise_linear_product(
            x, y, efficiency_x, efficiency[name], ROI_MIN_KEV, ROI_MAX_KEV
        )
    tail_raw, _ = integrate_piecewise_linear_product(
        x, y, efficiency_x, efficiency["central"], TAIL_MIN_KEV, TAIL_MAX_KEV
    )
    full_raw, _ = integrate_piecewise_linear_product(
        x, y, efficiency_x, efficiency["central"], ROI_MIN_KEV, ROI_MAX_KEV
    )
    return tail, full, tail_raw, full_raw


def build_results(
    afh_csv: Path = AFH_DIR / "afh_hybrid9_natural_xenon_spectrum.csv",
    gcn_root: Path = GCN_DIR,
    efficiency_csv: Path = EFFICIENCY_CSV,
):
    efficiency_x, efficiency = read_efficiency(efficiency_csv)
    afh_rows = read_csv(afh_csv)
    afh_benchmarks = {row["benchmark"] for row in afh_rows}
    if afh_benchmarks != set(BENCHMARKS):
        raise ValueError(f"unexpected AFH benchmark set: {sorted(afh_benchmarks)}")

    output = []
    for benchmark in BENCHMARKS:
        benchmark_afh = [row for row in afh_rows if row["benchmark"] == benchmark]
        for row in benchmark_afh:
            if row.get("halo_model") != "truncated SHM" or row.get("detector_response_applied") != "False":
                raise ValueError(f"{benchmark}: AFH input is not the archived pre-detector truncated-SHM spectrum")
            if row.get("response_q_convention") != "exact spatial q":
                raise ValueError(f"{benchmark}: AFH input does not use exact spatial q")
        for scenario in AFH_SCENARIOS:
            selected, x, y = _validated_rate_rows(benchmark_afh, "scenario", scenario)
            tail, full, tail_raw, full_raw = _integral_bundle(x, y, efficiency_x, efficiency)
            output.append(_make_output_row(benchmark, scenario, "AFH/Helm diagnostic", 7 if scenario == "AFH-7" else 9, tail, full, tail_raw, full_raw))

        gcn_benchmark_dir = gcn_root / benchmark
        gcn_meta = json.loads((gcn_benchmark_dir / "metadata.json").read_text(encoding="utf-8"))
        if gcn_meta.get("mass_scheme") != "nist_nuclear":
            raise ValueError(f"{benchmark}: GCN/JJ55 metadata does not use NIST nuclear masses")
        if not str(gcn_meta.get("response_q_convention", "")).startswith("exact spatial q"):
            raise ValueError(f"{benchmark}: GCN/JJ55 metadata does not use exact spatial q")
        if gcn_meta.get("halo_model") != "truncated SHM":
            raise ValueError(f"{benchmark}: GCN/JJ55 metadata does not use truncated SHM")
        if gcn_meta.get("abundance_renormalization") != "none":
            raise ValueError(f"{benchmark}: GCN/JJ55 isotope abundances were renormalized")
        if gcn_meta.get("available_isotopes") != [128, 129, 130, 131, 132, 134, 136]:
            raise ValueError(f"{benchmark}: unexpected GCN/JJ55 isotope coverage")
        gcn_csv = gcn_benchmark_dir / "natural_xenon_continuous_spectrum.csv"
        gcn_rows = read_csv(gcn_csv)
        gcn_rows = [
            row for row in gcn_rows
            if row.get("halo_model") == "shm_cutoff"
            and row.get("detector_response_applied") == "False"
        ]
        for model in ("GCN", "JJ55"):
            selected, x, y = _validated_rate_rows(gcn_rows, "model", model)
            tail, full, tail_raw, full_raw = _integral_bundle(x, y, efficiency_x, efficiency)
            output.append(_make_output_row(benchmark, model, "seven-isotope shell-model", 7, tail, full, tail_raw, full_raw))

    references = {
        row["benchmark"]: row["tail_expected_events_central"]
        for row in output if row["model"] == "AFH-7"
    }
    for row in output:
        reference = references[row["benchmark"]]
        row["relative_tail_shift_vs_AFH7"] = (
            row["tail_expected_events_central"] / reference - 1.0
            if reference > 0.0 else ""
        )

    output.sort(key=lambda row: (row["benchmark"], row["model"]))
    metadata = {
        "status": "PASS",
        "calculation": "one-dimensional efficiency-weighted rate-level tail audit",
        "source_commit": "ce4e500363778832c672117819dfd385f9346be7",
        "afh_spectrum": str(afh_csv),
        "gcn_jj55_spectrum_root": str(gcn_root),
        "efficiency_curve": str(efficiency_csv),
        "candidate_energy_keV": CANDIDATE_CENTER_KEV,
        "candidate_statistical_interval_keV": [CANDIDATE_CENTER_KEV - CANDIDATE_SIGMA_KEV, CANDIDATE_CENTER_KEV + CANDIDATE_SIGMA_KEV],
        "integrated_tail_interval_keV": [TAIL_MIN_KEV, TAIL_MAX_KEV],
        "full_efficiency_roi_keV": [ROI_MIN_KEV, ROI_MAX_KEV],
        "exposure_tonne_year": EXPOSURE_TONNE_YEAR,
        "exposure_kg_day": EXPOSURE_KG_DAY,
        "integration": "analytic integration of the product of piecewise-linear recoil rate and piecewise-linear efficiency on the union knot grid",
        "central_efficiency": "digitized LZ 2026 Fig. S2 central final-ROI curve",
        "efficiency_envelope": "digitized gray lower/upper envelope; not a confidence interval",
        "common_physics_inputs": {
            "mchi_GeV": 1000.0,
            "mV_GeV": 10.0,
            "coupling_product_squared": 1.0e-8,
            "g2_for_conditional_pole_width": 1.0,
            "rhoDM_GeV_cm3": 0.3,
            "halo": "truncated SHM, v0=220 km/s, vE=232 km/s, vesc=544 km/s, vmax_lab=776 km/s",
            "mass_scheme": "NIST nuclear masses",
            "spatial_momentum": "exact q_A=sqrt(2*m_A*E_R+E_R^2)",
            "width": "conditional constant pole width for Dirac chi2 -> chi1 s, pure scalar coupling, only that decay open",
        },
        "model_coverage": {
            "AFH-7": "AFH v6.0 default density matrices for seven isotopes; no abundance renormalization",
            "Hybrid-9 (AFH-7 + Helm-2)": "same seven AFH isotopes plus Helm only for Xe-124/Xe-126",
            "AFH-7 + A2-2 ceiling": "diagnostic coherent A^2 ceiling for Xe-124/Xe-126; not a physical nuclear model",
            "Helm-9": "independent Helm response for all nine naturally occurring isotopes; not AFH",
            "GCN": "seven-isotope GCN shell-model response",
            "JJ55": "seven-isotope JJ55 shell-model response",
        },
        "limitations": [
            "The recoil spectra are pre-detector and are folded only with a one-dimensional efficiency curve.",
            "No energy-resolution smearing, NEST S1/S2 PDFs, backgrounds, nuisance covariance, or profile likelihood is included.",
            "The LZ Fig. S2 gray envelope is a digitization/systematic envelope without an assigned confidence level.",
            "The candidate +/- statistical-energy interval is used only as a recoil-energy integration window; it is not a detector energy-resolution model.",
            "Helm-9 is a separate all-isotope phenomenological model comparison; it must not be interpreted as the missing-isotope correction to AFH-7. Hybrid-9 is the corresponding AFH-7 plus Helm-2 fallback.",
            "The AFH/GCN/JJ55 model differences include the nuclear response choice; they are not detector-level likelihood differences.",
        ],
        "row_count": len(output),
    }
    return output, metadata


def _make_output_row(benchmark, model, family, isotope_count, tail, full, tail_raw, full_raw):
    return {
        "benchmark": benchmark,
        "model": model,
        "model_family": family,
        "nominal_isotope_count": isotope_count,
        "tail_min_keV": TAIL_MIN_KEV,
        "tail_max_keV": TAIL_MAX_KEV,
        "tail_raw_rate_integral_events_kg_day": tail_raw,
        "tail_expected_events_central": tail["central"] * EXPOSURE_KG_DAY,
        "tail_expected_events_efficiency_lower": tail["lower"] * EXPOSURE_KG_DAY,
        "tail_expected_events_efficiency_upper": tail["upper"] * EXPOSURE_KG_DAY,
        "full_roi_expected_events_central": full["central"] * EXPOSURE_KG_DAY,
        "tail_fraction_of_full_roi_central": tail["central"] / full["central"] if full["central"] > 0.0 else "",
        "tail_average_efficiency": tail["central"] / tail_raw if tail_raw > 0.0 else "",
        "full_roi_raw_rate_integral_events_kg_day": full_raw,
        "relative_tail_shift_vs_AFH7": "",
    }


def write_outputs(output: list[dict], metadata: dict, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "high_energy_tail_model_sensitivity.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(output[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    (outdir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--afh-spectrum", type=Path, default=AFH_DIR / "afh_hybrid9_natural_xenon_spectrum.csv")
    parser.add_argument("--gcn-spectrum-root", type=Path, default=GCN_DIR)
    parser.add_argument("--efficiency-csv", type=Path, default=EFFICIENCY_CSV)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    output, metadata = build_results(args.afh_spectrum, args.gcn_spectrum_root, args.efficiency_csv)
    write_outputs(output, metadata, args.outdir)
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
