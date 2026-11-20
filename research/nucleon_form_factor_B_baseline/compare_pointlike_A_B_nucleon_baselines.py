#!/usr/bin/env python3
"""Compare four nucleon-current baselines P0, P, A0 and B.

All four use the same isotope-resolved three-body/halo kernels and finite-size
AFH W_M response. P0 is the archived leading-order charge-only rate; P is
pointlike Dirac with the recoil matching term; A0 freezes F1,F2 at zero
transfer while retaining F2(0); B uses finite Borah/strange form factors.
The formal impulse prescription is t_N=t_A=-2*m_A*E_R. Exact spatial Q_A^2
is retained separately for the AFH Fourier variable.
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


def leading_order_pointlike_cM_hat() -> float:
    """P0: normalized coefficient cM_hat=1; omit finite-t_N terms (raw cM=3)."""
    return 1.0


def pointlike_dirac_cM_hat(q2_form_factor_GeV2: float) -> float:
    """P: normalized coefficient cM_hat for the finite-transfer M-only match.

    P and P0 both use Fhat_1=1 and Fhat_2=0. P0 truncates cM_hat to 1,
    whereas P retains cM_hat=1-Q_N^2/(8*m_N^2), with Q_N^2=-t_N.
    The argument is -t_N=2*m_A*E_R under the formal impulse prescription;
    it is not the AFH spatial Fourier variable Q_A^2.
    """
    if not math.isfinite(q2_form_factor_GeV2) or q2_form_factor_GeV2 < 0.0:
        raise ValueError("invalid -t_N")
    return 1.0 - q2_form_factor_GeV2 / (8.0 * MAVG_GEV**2)


def zero_transfer_pauli_hat(strange_model: str) -> float:
    """A0: return F2hat(0) for the selected unit-strange-current input."""
    ff0 = cM_and_factor(np.asarray([0.0]), strange_model)
    return float(ff0["F2uds"][0] / 3.0)


def zero_transfer_pauli_cM_hat(
    q2_form_factor_GeV2: float, f2hat0: float
) -> float:
    """A0: freeze F1,F2 at zero transfer, but retain the actual t_N recoil term."""
    if not math.isfinite(q2_form_factor_GeV2) or q2_form_factor_GeV2 < 0.0:
        raise ValueError("invalid -t_N")
    if not math.isfinite(f2hat0):
        raise ValueError("invalid zero-transfer Pauli form factor")
    return 1.0 - q2_form_factor_GeV2 / (8.0 * MAVG_GEV**2) * (1.0 + 2.0*f2hat0)


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
    zero_transfer_f2hat = {
        model: zero_transfer_pauli_hat(model)
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
    max_P0_closure = 0.0
    max_P0_closure_key = None

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
                model: {"P0": [], "P": [], "A0": [], "B": []}
                for model in MODELS
            }
            for ER in energies:
                isotope_P0_sum = 0.0
                isotope_P_sum = 0.0
                isotope_A0_sums = {model: 0.0 for model in MODELS}
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

                    # P0 and P share Fhat_1=1, Fhat_2=0. P0 is the
                    # leading-order charge-only truncation cM=1; it is not A0.
                    cM_P0 = leading_order_pointlike_cM_hat()
                    P0_multiplier = cM_P0 * cM_P0
                    P0_contribution = base_contribution * P0_multiplier

                    # P retains the finite-transfer M-only matching term.
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

                        f2hat0 = zero_transfer_f2hat[model]
                        cM_A0 = zero_transfer_pauli_cM_hat(
                            q2_form_factor, f2hat0
                        )
                        A0_multiplier = cM_A0 * cM_A0
                        A0_contribution = base_contribution * A0_multiplier

                        isotope_A0_sums[model] += A0_contribution
                        isotope_B_sums[model] += B_contribution
                        isotope_model_records.append({
                            "strange_form_factor_model": model,
                            "F1hat_A0": 1.0,
                            "F2hat_A0": f2hat0,
                            "cMhat_A0": cM_A0,
                            "A0_rate_multiplier": A0_multiplier,
                            "rate_A0_contribution_events_kg_day_keV": A0_contribution,
                            "F1hat_B": float(ff["F1uds"][index] / 3.0),
                            "F2hat_B": float(ff["F2uds"][index] / 3.0),
                            "cMhat_B": cM_B_hat,
                            "B_rate_multiplier": B_multiplier,
                            "rate_B_contribution_events_kg_day_keV": B_contribution,
                        })

                    isotope_P0_sum += P0_contribution
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
                            "rate_P0_contribution_events_kg_day_keV": P0_contribution,
                            "F1hat_P0": 1.0,
                            "F2hat_P0": 0.0,
                            "cMhat_P0": cM_P0,
                            "P0_rate_multiplier": P0_multiplier,
                            "rate_P_contribution_events_kg_day_keV": P_contribution,
                            "F1hat_P": 1.0,
                            "F2hat_P": 0.0,
                            "cMhat_P": cM_P,
                            "P_rate_multiplier": P_multiplier,
                            **model_record,
                        })

                source_P0 = number(
                    spectrum_lookup[(benchmark, scenario, ER)],
                    "rate_events_kg_day_keV",
                )
                closure = (
                    abs(isotope_P0_sum / source_P0 - 1.0)
                    if source_P0 > 0.0
                    else (0.0 if isotope_P0_sum == 0.0 else math.inf)
                )
                if closure > max_P0_closure:
                    max_P0_closure = closure
                    max_P0_closure_key = (benchmark, scenario, ER)
                if closure > closure_tolerance:
                    raise ArithmeticError(
                        f"P0 reconstruction failed for {benchmark}/{scenario}/{ER}: "
                        f"{closure:.6e} > {closure_tolerance:.6e}"
                    )

                for model in MODELS:
                    P0_rate = isotope_P0_sum
                    P_rate = isotope_P_sum
                    A0_rate = isotope_A0_sums[model]
                    B_rate = isotope_B_sums[model]
                    rate_series[model]["P0"].append(P0_rate)
                    rate_series[model]["P"].append(P_rate)
                    rate_series[model]["A0"].append(A0_rate)
                    rate_series[model]["B"].append(B_rate)
                    output_spectrum_rows.append({
                        "benchmark": benchmark,
                        "scenario": scenario,
                        "strange_form_factor_model": model,
                        "ER_keV": ER,
                        "rate_P0_events_kg_day_keV": P0_rate,
                        "rate_P_events_kg_day_keV": P_rate,
                        "rate_A0_events_kg_day_keV": A0_rate,
                        "rate_B_events_kg_day_keV": B_rate,
                        "P_over_P0_rate": P_rate / P0_rate if P0_rate > 0 else 1.0,
                        "A0_over_P_rate": A0_rate / P_rate if P_rate > 0 else 1.0,
                        "B_over_A0_rate": B_rate / A0_rate if A0_rate > 0 else 1.0,
                        "B_over_P0_rate": B_rate / P0_rate if P0_rate > 0 else 1.0,
                        "B_over_P_rate": B_rate / P_rate if P_rate > 0 else 1.0,
                        "F2hat_A0": zero_transfer_f2hat[model],
                        "coupling_product_squared": coupling_sq,
                    })

            for model in MODELS:
                series = rate_series[model]
                detector_integrals = {}
                for baseline in ("P0", "P", "A0", "B"):
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

                events = {
                    baseline: detector_integrals[baseline]["expected_events"]
                    for baseline in ("P0", "P", "A0", "B")
                }
                p0_events = events["P0"]
                p_events = events["P"]
                a0_events = events["A0"]
                b_events = events["B"]
                output_detector_rows.append({
                    "benchmark": benchmark,
                    "scenario": scenario,
                    "strange_form_factor_model": model,
                    "F2hat_A0": zero_transfer_f2hat[model],
                    "roi_min_keV": roi_min_keV,
                    "roi_max_keV": roi_max_keV,
                    "exposure_tonne_year": exposure_tonne_year,
                    "exposure_kg_day": exposure_kg_day,
                    "P0_expected_events": p0_events,
                    "P_expected_events": p_events,
                    "A0_expected_events": a0_events,
                    "B_expected_events": b_events,
                    "P_over_P0_events": p_events / p0_events if p0_events > 0 else 1.0,
                    "A0_over_P_events": a0_events / p_events if p_events > 0 else 1.0,
                    "B_over_A0_events": b_events / a0_events if a0_events > 0 else 1.0,
                    "B_over_P0_events": b_events / p0_events if p0_events > 0 else 1.0,
                    "B_over_P_events": b_events / p_events if p_events > 0 else 1.0,
                    **{
                        f"{baseline}_raw_integral_events_kg_day":
                            detector_integrals[baseline]["raw_integral_events_kg_day"]
                        for baseline in ("P0", "P", "A0", "B")
                    },
                    **{
                        f"{baseline}_efficiency_weighted_integral_events_kg_day":
                            detector_integrals[baseline]["efficiency_weighted_integral_events_kg_day"]
                        for baseline in ("P0", "P", "A0", "B")
                    },
                    "coupling_product_squared": coupling_sq,
                    "detector_efficiency_curve": "LZ 2026 Fig. S2 central final-WIMP-search-ROI NR efficiency",
                    "energy_resolution_smearing_applied": False,
                    "background_likelihood_applied": False,
                })

    out_dir.mkdir(parents=True, exist_ok=True)
    spectrum_out = out_dir / "nucleon_P0_P_A0_B_natural_xenon_spectrum.csv"
    isotope_out = out_dir / "nucleon_P0_P_A0_B_isotope_contributions.csv"
    detector_out = out_dir / "nucleon_P0_P_A0_B_detector_yields.csv"
    write_csv(spectrum_out, output_spectrum_rows)
    write_csv(isotope_out, output_isotope_rows)
    write_csv(detector_out, output_detector_rows)

    metadata = {
        "status": "PASS",
        "calculation": "four-level P0/P/A0/B nucleon-current comparison applied to archived AFH-7/Hybrid-9 three-body halo kernels",
        "baseline_definitions": {
            "P0": "leading-order point-nucleon charge: Fhat_1=1, Fhat_2=0, cMhat=1; omit the finite-t_N/m_N^2 matching term; legacy source spectrum label A maps to P0",
            "P": "finite-transfer pointlike Dirac charge (M-only): Fhat_1=1, Fhat_2=0, cMhat=1+t_N/(8*m_N^2); same pointlike form factors as P0, but retain the finite-transfer matching term",
            "A0": "zero-transfer form factors frozen at Fhat_1(0)=1 and model-specific Fhat_2(0), retaining the physical t_N recoil term",
            "B": "finite Borah-2020 proton/neutron Dirac-Pauli form factors plus the selected unit-strange-current input, evaluated at t_N=t_A",
        },
        "zero_transfer_pauli_inputs": zero_transfer_f2hat,
        "normalization": {
            "raw_universal_uds_form_factors_divided_by": 3,
            "external_coupling_convention": "g_VN=3*g_Vq",
            "AFH_equal_p_n_factor": "already contained once in the physical AFH response",
        },
        "momentum_transfer": {
            "t_N_GeV2": "-2*m_A*E_R",
            "t_A_GeV2": "-2*m_A*E_R",
            "Q2_form_factor_GeV2": "Q_N^2=2*m_A*E_R=-t_N; used in P finite-transfer c_M and B nucleon form factors",
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
            "maximum_P0_reconstruction_relative_difference": max_P0_closure,
            "maximum_P0_reconstruction_key": list(max_P0_closure_key) if max_P0_closure_key else None,
            "P0_reconstruction_tolerance": closure_tolerance,
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
