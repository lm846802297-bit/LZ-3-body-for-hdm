#!/usr/bin/env python3
"""Compare pointlike Dirac P, zero-transfer A, and finite-form-factor B.

All three baselines use the same isotope-resolved three-body/halo kernels and
the same finite-size AFH W_M response. The formal impulse prescription is
q_N^mu=q_A^mu and t_N=t_A=-2*m_A*E_R. The exact spatial Q_A^2 remains the
AFH Fourier variable and is not substituted into the nucleon form factors.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "research/three_body_calculation_and_validation"))

from apply_B_to_afh_hybrid9_continuous_spectrum import (  # noqa: E402
    SCENARIOS,
    number,
    rate_prefactor,
    read_csv,
    response_for_scenario,
)
from borah2020_lowq2 import MAVG_GEV, cM_and_factor  # noqa: E402
from fold_lz_2026_rate_level import (  # noqa: E402
    integrate_piecewise_linear_product,
    read_efficiency_curves,
    sha256,
)

DEFAULT_SOURCE_DIR = (
    ROOT / "research/afh_default_density_natural_xenon_halo/results/"
    "afh7_hybrid9_continuous_2026-11-14"
)
DEFAULT_EFFICIENCY = (
    ROOT / "research/lz_detector_response/lz_2026_extended_nr/"
    "lz_2026_nr_efficiency_digitized.csv"
)
MODELS = (
    "sufian2017_unit_current",
    "alexandrou2020_charge_weighted_converted",
    "alexandrou2026_continuum_unit_current",
)
TONNE_YEAR_TO_KG_DAY = 1000.0 * 365.25
DEFAULT_ROI_MIN_KEV = 5.4
DEFAULT_ROI_MAX_KEV = 269.9
DEFAULT_EXPOSURE_TONNE_YEAR = 2.84
A_ZERO_TRANSFER_F1_HAT = 1.0
A_ZERO_TRANSFER_F2_HAT = -0.184


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def q2_form_factor_from_recoil(mA_GeV: float, ER_keV: float) -> float:
    """Return -t_N=-t_A=2*m_A*E_R for the formal impulse prescription."""
    if mA_GeV <= 0.0 or ER_keV < 0.0:
        raise ValueError("invalid nuclear mass or recoil energy")
    return 2.0 * mA_GeV * ER_keV * 1.0e-6


def qA2_spatial_from_recoil(mA_GeV: float, ER_keV: float) -> float:
    """Return exact spatial Q_A^2=2*m_A*E_R+E_R^2 for AFH."""
    ER = ER_keV * 1.0e-6
    return 2.0 * mA_GeV * ER + ER * ER


def pointlike_dirac_cM_hat(q2_form_factor_GeV2: float) -> float:
    """P: Fhat_1=1, Fhat_2=0, retaining the formal c_M recoil term."""
    if not math.isfinite(q2_form_factor_GeV2) or q2_form_factor_GeV2 < 0.0:
        raise ValueError("invalid -t_N")
    return 1.0 - q2_form_factor_GeV2 / (8.0 * MAVG_GEV**2)


def read_keyed_spectrum(rows: list[dict[str, str]]) -> dict[tuple[str, str, float], dict]:
    result = {}
    for row in rows:
        key = (row["benchmark"], row["scenario"], number(row, "ER_keV"))
        if key in result:
            raise ValueError(f"duplicate source-spectrum key: {key}")
        result[key] = row
    return result


def run(
    source_dir: Path = DEFAULT_SOURCE_DIR,
    efficiency_csv: Path = DEFAULT_EFFICIENCY,
    out_dir: Path | None = None,
    roi_min_keV: float = DEFAULT_ROI_MIN_KEV,
    roi_max_keV: float = DEFAULT_ROI_MAX_KEV,
    exposure_tonne_year: float = DEFAULT_EXPOSURE_TONNE_YEAR,
    closure_tolerance: float = 2.0e-11,
) -> dict:
    if out_dir is None:
        raise ValueError("out_dir is required")
    if not roi_min_keV < roi_max_keV or exposure_tonne_year <= 0.0:
        raise ValueError("invalid detector ROI or exposure")

    spectrum_path = source_dir / "afh_hybrid9_natural_xenon_spectrum.csv"
    isotope_path = source_dir / "afh_hybrid9_isotope_kernel_integrals.csv"
    metadata_path = source_dir / "metadata.json"
    for path in (spectrum_path, isotope_path, metadata_path, efficiency_csv):
        if not path.is_file():
            raise FileNotFoundError(path)

    source_meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    if source_meta.get("status") != "PASS":
        raise ValueError("source AFH/halo metadata is not PASS")
    if source_meta.get("detector_response_applied") is not False:
        raise ValueError("source spectrum must be pre-detector")

    particle = source_meta["particle_parameters"]
    mV = float(particle["mV_GeV"])
    coupling_sq = float(particle["coupling_product_squared"])
    prefactor = rate_prefactor(source_meta)
    source_spectrum = read_csv(spectrum_path)
    isotope_rows = read_csv(isotope_path)
    if not source_spectrum or not isotope_rows:
        raise ValueError("source spectrum or isotope kernel table is empty")

    spectrum_lookup = read_keyed_spectrum(source_spectrum)
    isotope_groups: dict[tuple[str, float], list[dict[str, str]]] = defaultdict(list)
    q2_values_set: set[float] = set()
    q2_by_isotope: dict[tuple[str, float, int], float] = {}
    for row in isotope_rows:
        benchmark = row["benchmark"]
        ER = number(row, "ER_keV")
        A = int(row["A"])
        mA = number(row, "mA_GeV")
        q2_form_factor = q2_form_factor_from_recoil(mA, ER)
        key = (benchmark, ER, A)
        if key in q2_by_isotope:
            raise ValueError(f"duplicate isotope-kernel key: {key}")
        q2_by_isotope[key] = q2_form_factor
        q2_values_set.add(q2_form_factor)
        isotope_groups[(benchmark, ER)].append(row)

    q2_values = sorted(q2_values_set)
    q2_index = {format(q2, ".17g"): i for i, q2 in enumerate(q2_values)}
    q2_index_by_isotope = {
        key: q2_index[format(q2, ".17g")]
        for key, q2 in q2_by_isotope.items()
    }

    central_form_factors = {
        model: cM_and_factor(np.asarray(q2_values), model)
        for model in MODELS
    }

    efficiency_x, efficiency_central, efficiency_lower, efficiency_upper = (
        read_efficiency_curves(efficiency_csv)
    )
    if efficiency_x[0] > roi_min_keV or efficiency_x[-1] < roi_max_keV:
        raise ValueError("LZ efficiency curve does not cover the requested ROI")
    exposure_kg_day = exposure_tonne_year * TONNE_YEAR_TO_KG_DAY

    output_spectrum_rows: list[dict] = []
    output_isotope_rows: list[dict] = []
    output_detector_rows: list[dict] = []
    max_A_closure = 0.0
    max_A_closure_key = None

    benchmarks = sorted(particle["benchmarks"])
    for benchmark in benchmarks:
        for scenario in SCENARIOS:
            energies = sorted({
                number(row, "ER_keV")
                for row in source_spectrum
                if row["benchmark"] == benchmark and row["scenario"] == scenario
            })
            if len(energies) < 2:
                raise ValueError(f"{benchmark}/{scenario}: incomplete recoil grid")

            rate_series = {
                model: {"A": [], "P": [], "B": []}
                for model in MODELS
            }
            for ER in energies:
                isotope_A_sum = 0.0
                isotope_P_sum = 0.0
                isotope_B_sums = {model: 0.0 for model in MODELS}

                rows = isotope_groups.get((benchmark, ER), [])
                if not rows:
                    raise ValueError(f"missing isotope kernels for {benchmark}/{ER}")

                for row in rows:
                    A = int(row["A"])
                    atom_fraction = number(row, "natural_atom_fraction")
                    mA = number(row, "mA_GeV")
                    qA = number(row, "q_exact_spatial_GeV")
                    Q_A2 = qA * qA
                    q2_form_factor = q2_form_factor_from_recoil(mA, ER)
                    tA = -q2_form_factor
                    response = response_for_scenario(row, scenario)
                    kernel = number(row, "kernel_halo_integral_GeV")
                    denominator = (mV * mV - tA) ** 2

                    if response == 0.0 or kernel == 0.0:
                        base_contribution = 0.0
                    else:
                        base_contribution = (
                            prefactor * atom_fraction * kernel * response / denominator
                        )

                    # A is the zero-transfer nucleon-current reference:
                    # Fhat_1(0)=1, Fhat_2(0)=-0.184, hence cM(0)=1.
                    A_contribution = base_contribution

                    # P is a pointlike Dirac nucleon at the physical transfer:
                    # Fhat_1=1, Fhat_2=0, with the same formal c_M matching.
                    cM_P = pointlike_dirac_cM_hat(q2_form_factor)
                    P_multiplier = cM_P * cM_P
                    P_contribution = base_contribution * P_multiplier

                    isotope_model_records = []
                    for model in MODELS:
                        index = q2_index_by_isotope[(benchmark, ER, A)]
                        ff = central_form_factors[model]
                        cM_B_hat = float(ff["F_M"][index])
                        B_multiplier = cM_B_hat * cM_B_hat
                        B_contribution = base_contribution * B_multiplier
                        isotope_B_sums[model] += B_contribution
                        isotope_model_records.append({
                            "strange_form_factor_model": model,
                            "F1hat_B": float(ff["F1uds"][index] / 3.0),
                            "F2hat_B": float(ff["F2uds"][index] / 3.0),
                            "cMhat_B": cM_B_hat,
                            "B_rate_multiplier": B_multiplier,
                            "rate_B_contribution_events_kg_day_keV": B_contribution,
                        })

                    isotope_A_sum += A_contribution
                    isotope_P_sum += P_contribution

                    for model_record in isotope_model_records:
                        output_isotope_rows.append({
                            "benchmark": benchmark,
                            "scenario": scenario,
                            "ER_keV": ER,
                            "A": A,
                            "natural_atom_fraction": atom_fraction,
                            "mA_GeV": mA,
                            "q_A_spatial_GeV": qA,
                            "Q_A2_spatial_GeV2": Q_A2,
                            "Q2_form_factor_GeV2": q2_form_factor,
                            "t_N_GeV2": tA,
                            "t_A_GeV2": tA,
                            "AFH_response_model": scenario,
                            "AFH_response_value": response,
                            "kernel_halo_integral_GeV": kernel,
                            "rate_A_contribution_events_kg_day_keV": A_contribution,
                            "F1hat_P": 1.0,
                            "F2hat_P": 0.0,
                            "cMhat_P": cM_P,
                            "P_rate_multiplier": P_multiplier,
                            "rate_P_contribution_events_kg_day_keV": P_contribution,
                            "F1hat_A": A_ZERO_TRANSFER_F1_HAT,
                            "F2hat_A": A_ZERO_TRANSFER_F2_HAT,
                            "cMhat_A": 1.0,
                            **model_record,
                        })

                source_A = number(
                    spectrum_lookup[(benchmark, scenario, ER)],
                    "rate_events_kg_day_keV",
                )
                closure = (
                    abs(isotope_A_sum / source_A - 1.0)
                    if source_A > 0.0
                    else (0.0 if isotope_A_sum == 0.0 else math.inf)
                )
                if closure > max_A_closure:
                    max_A_closure = closure
                    max_A_closure_key = (benchmark, scenario, ER)
                if closure > closure_tolerance:
                    raise ArithmeticError(
                        f"A reconstruction failed for {benchmark}/{scenario}/{ER}: "
                        f"{closure:.6e} > {closure_tolerance:.6e}"
                    )

                for model in MODELS:
                    B_rate = isotope_B_sums[model]
                    rate_series[model]["A"].append(isotope_A_sum)
                    rate_series[model]["P"].append(isotope_P_sum)
                    rate_series[model]["B"].append(B_rate)
                    output_spectrum_rows.append({
                        "benchmark": benchmark,
                        "scenario": scenario,
                        "strange_form_factor_model": model,
                        "ER_keV": ER,
                        "rate_A_events_kg_day_keV": isotope_A_sum,
                        "rate_P_events_kg_day_keV": isotope_P_sum,
                        "rate_B_events_kg_day_keV": B_rate,
                        "P_over_A_rate": isotope_P_sum / isotope_A_sum if isotope_A_sum > 0 else 1.0,
                        "B_over_A_rate": B_rate / isotope_A_sum if isotope_A_sum > 0 else 1.0,
                        "B_over_P_rate": B_rate / isotope_P_sum if isotope_P_sum > 0 else 1.0,
                        "coupling_product_squared": coupling_sq,
                    })

            for model in MODELS:
                series = rate_series[model]
                detector_integrals = {}
                for baseline in ("A", "P", "B"):
                    raw, weighted = integrate_piecewise_linear_product(
                        energies,
                        series[baseline],
                        efficiency_x,
                        efficiency_central,
                        roi_min_keV,
                        roi_max_keV,
                    )
                    detector_integrals[baseline] = {
                        "raw_integral_events_kg_day": raw,
                        "efficiency_weighted_integral_events_kg_day": weighted,
                        "expected_events": weighted * exposure_kg_day,
                    }

                A_events = detector_integrals["A"]["expected_events"]
                P_events = detector_integrals["P"]["expected_events"]
                B_events = detector_integrals["B"]["expected_events"]
                output_detector_rows.append({
                    "benchmark": benchmark,
                    "scenario": scenario,
                    "strange_form_factor_model": model,
                    "roi_min_keV": roi_min_keV,
                    "roi_max_keV": roi_max_keV,
                    "exposure_tonne_year": exposure_tonne_year,
                    "exposure_kg_day": exposure_kg_day,
                    "A_expected_events": A_events,
                    "P_expected_events": P_events,
                    "B_expected_events": B_events,
                    "P_over_A_events": P_events / A_events if A_events > 0 else 1.0,
                    "B_over_A_events": B_events / A_events if A_events > 0 else 1.0,
                    "B_over_P_events": B_events / P_events if P_events > 0 else 1.0,
                    "A_raw_integral_events_kg_day": detector_integrals["A"]["raw_integral_events_kg_day"],
                    "P_raw_integral_events_kg_day": detector_integrals["P"]["raw_integral_events_kg_day"],
                    "B_raw_integral_events_kg_day": detector_integrals["B"]["raw_integral_events_kg_day"],
                    "A_efficiency_weighted_integral_events_kg_day": detector_integrals["A"]["efficiency_weighted_integral_events_kg_day"],
                    "P_efficiency_weighted_integral_events_kg_day": detector_integrals["P"]["efficiency_weighted_integral_events_kg_day"],
                    "B_efficiency_weighted_integral_events_kg_day": detector_integrals["B"]["efficiency_weighted_integral_events_kg_day"],
                    "coupling_product_squared": coupling_sq,
                    "detector_efficiency_curve": "LZ 2026 Fig. S2 central final-WIMP-search-ROI NR efficiency",
                    "energy_resolution_smearing_applied": False,
                    "background_likelihood_applied": False,
                })

    out_dir.mkdir(parents=True, exist_ok=True)
    spectrum_out = out_dir / "pointlike_A_B_natural_xenon_spectrum.csv"
    isotope_out = out_dir / "pointlike_A_B_isotope_contributions.csv"
    detector_out = out_dir / "pointlike_A_B_detector_yields.csv"
    write_csv(spectrum_out, output_spectrum_rows)
    write_csv(isotope_out, output_isotope_rows)
    write_csv(detector_out, output_detector_rows)

    metadata = {
        "status": "PASS",
        "calculation": "pointlike Dirac P versus zero-transfer A and finite-form-factor B, applied to archived AFH-7/Hybrid-9 three-body halo kernels",
        "baseline_definitions": {
            "P": "pointlike Dirac nucleon: Fhat_1=1, Fhat_2=0, cMhat=1+t_N/(8*m_N^2)",
            "A": "zero-transfer nucleon-current reference: Fhat_1(0)=1, Fhat_2(0)=-0.184, t_N=0 and cMhat=1",
            "B": "finite Borah-2020 proton/neutron Dirac-Pauli form factors plus the selected unit-strange-current input, evaluated at t_N=t_A",
        },
        "normalization": {
            "raw_universal_uds_form_factors_divided_by": 3,
            "external_coupling_convention": "g_VN=3*g_Vq",
            "AFH_equal_p_n_factor": "already contained once in the physical AFH response",
        },
        "momentum_transfer": {
            "t_N_GeV2": "-2*m_A*E_R",
            "t_A_GeV2": "-2*m_A*E_R",
            "Q2_form_factor_GeV2": "2*m_A*E_R=-t_N",
            "Q_A2_spatial_GeV2": "2*m_A*E_R+E_R^2; used for AFH y_A only",
            "mediator_denominator_squared_GeV4": "(m_V^2-t_A)^2",
        },
        "nuclear_response": "AFH v6.0 finite-size W_M for seven supported isotopes; Helm fallback only for Xe-124/Xe-126 in Hybrid-9; no point-nucleus substitution",
        "nucleon_form_factor_source": "Borah et al., Phys. Rev. D 102, 074012 (2020), arXiv:2003.13640; separate p/n low-Q2 z expansion",
        "strange_current_models": list(MODELS),
        "detector_fold": {
            "efficiency_source": "LZ 2026 Fig. S2 central final-WIMP-search-ROI NR efficiency",
            "roi_keV": [roi_min_keV, roi_max_keV],
            "exposure_tonne_year": exposure_tonne_year,
            "integration": "exact analytic integration of piecewise-linear rate times piecewise-linear efficiency over the union of knots",
            "energy_resolution_smearing": False,
            "background_likelihood": False,
            "confidence_level_exclusion": False,
        },
        "source_files": {
            "isotope_kernel_csv": str(isotope_path),
            "isotope_kernel_sha256": sha256(isotope_path),
            "source_spectrum_csv": str(spectrum_path),
            "source_spectrum_sha256": sha256(spectrum_path),
            "source_metadata_json": str(metadata_path),
            "source_metadata_sha256": sha256(metadata_path),
            "efficiency_csv": str(efficiency_csv),
            "efficiency_sha256": sha256(efficiency_csv),
        },
        "validation": {
            "maximum_A_reconstruction_relative_difference": max_A_closure,
            "maximum_A_reconstruction_key": list(max_A_closure_key) if max_A_closure_key else None,
            "A_reconstruction_tolerance": closure_tolerance,
            "recoil_points_per_benchmark_scenario": len({
                number(row, "ER_keV") for row in source_spectrum
                if row["benchmark"] == benchmarks[0] and row["scenario"] == SCENARIOS[0]
            }),
        },
        "row_counts": {
            "natural_xenon_spectra": len(output_spectrum_rows),
            "isotope_contributions": len(output_isotope_rows),
            "detector_yields": len(output_detector_rows),
        },
        "output_files": {
            "spectrum": spectrum_out.name,
            "isotope_contributions": isotope_out.name,
            "detector_yields": detector_out.name,
        },
    }
    metadata_out = out_dir / "metadata.json"
    metadata_out.write_text(json.dumps(metadata, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (out_dir / "SHA256SUMS.txt").write_text(
        f"{sha256(spectrum_out)}  {spectrum_out.name}\n"
        f"{sha256(isotope_out)}  {isotope_out.name}\n"
        f"{sha256(detector_out)}  {detector_out.name}\n"
        f"{sha256(metadata_out)}  {metadata_out.name}\n",
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--efficiency-csv", type=Path, default=DEFAULT_EFFICIENCY)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--roi-min-keV", type=float, default=DEFAULT_ROI_MIN_KEV)
    parser.add_argument("--roi-max-keV", type=float, default=DEFAULT_ROI_MAX_KEV)
    parser.add_argument("--exposure-tonne-year", type=float, default=DEFAULT_EXPOSURE_TONNE_YEAR)
    parser.add_argument("--closure-tolerance", type=float, default=2.0e-11)
    args = parser.parse_args()
    result = run(
        source_dir=args.source_dir,
        efficiency_csv=args.efficiency_csv,
        out_dir=args.out_dir,
        roi_min_keV=args.roi_min_keV,
        roi_max_keV=args.roi_max_keV,
        exposure_tonne_year=args.exposure_tonne_year,
        closure_tolerance=args.closure_tolerance,
    )
    print(json.dumps(result["validation"], indent=2))


if __name__ == "__main__":
    main()
