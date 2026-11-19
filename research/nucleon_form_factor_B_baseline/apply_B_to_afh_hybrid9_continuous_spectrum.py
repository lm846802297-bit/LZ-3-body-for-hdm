#!/usr/bin/env python3
"""Apply the finite-nucleon B factor to archived absolute AFH-7/Hybrid-9 rates.

The archived isotope-resolved three-body kernels are reused.  This script
reconstructs the published A spectrum first and requires machine-precision
closure before multiplying each isotope by |c_M(t_N)/3|^2.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from borah2020_lowq2 import cM_and_factor, sample_cM_draws  # noqa: E402

DEFAULT_SOURCE_DIR = (
    ROOT / "research/afh_default_density_natural_xenon_halo/results/"
    "afh7_hybrid9_continuous_2026-11-14"
)
DEFAULT_OUT_ROOT = (
    ROOT / "research/lz_detector_response/lz_2026_extended_nr/"
    "afh7_hybrid9_B_rate_level_spectra"
)
SCENARIOS = ("AFH-7", "Hybrid-9 (AFH-7 + Helm-2)")
STRANGE_MODELS = (
    "sufian2017_unit_current",
    "alexandrou2020_charge_weighted_converted",
    "alexandrou2026_continuum_unit_current",
)

C_KM_S = 299_792.458
C_CM_S = 2.99792458e10
GEV2_TO_CM2 = 0.3893793721e-27
AVOGADRO = 6.02214076e23
NIST_XE_STANDARD_ATOMIC_WEIGHT_G_MOL = 131.29276144779053


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def number(row: dict, key: str, default: float | None = None) -> float:
    raw = row.get(key, "")
    if raw in ("", None):
        if default is None:
            raise ValueError(f"missing numeric field {key}")
        return default
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError(f"non-finite {key}={value}")
    return value


def response_for_scenario(row: dict[str, str], scenario: str) -> float:
    A = int(row["A"])
    raw_afh = row.get("R_AFH_direct_exact_q", "")
    raw_helm = row.get("R_Helm", "")
    has_afh = raw_afh not in ("", None)
    if scenario == "AFH-7":
        return float(raw_afh) if has_afh else 0.0
    if scenario == "Hybrid-9 (AFH-7 + Helm-2)":
        return float(raw_afh) if has_afh else float(raw_helm)
    raise ValueError(f"unsupported nuclear scenario {scenario}")


def rate_prefactor(metadata: dict) -> float:
    particle = metadata["particle_parameters"]
    mchi = float(particle["mchi_GeV"])
    rho = float(particle["rhoDM_GeV_cm3"])
    if mchi <= 0.0 or rho <= 0.0:
        raise ValueError("mchi and rhoDM must be positive")
    return (
        (rho / mchi)
        * C_CM_S
        * (AVOGADRO * 1000.0 / NIST_XE_STANDARD_ATOMIC_WEIGHT_G_MOL)
        * GEV2_TO_CM2 * 1.0e-6 * 86400.0
    )


def run(
    source_dir: Path,
    out_dir: Path,
    strange_model: str,
    n_draws: int = 3000,
    seed: int = 20261119,
    closure_tolerance: float = 2.0e-11,
) -> dict:
    if strange_model not in STRANGE_MODELS:
        raise ValueError(f"unknown strange-current model: {strange_model}")
    spectrum_path = source_dir / "afh_hybrid9_natural_xenon_spectrum.csv"
    isotope_path = source_dir / "afh_hybrid9_isotope_kernel_integrals.csv"
    source_meta_path = source_dir / "metadata.json"
    for path in (spectrum_path, isotope_path, source_meta_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    source_meta = json.loads(source_meta_path.read_text(encoding="utf-8"))
    if source_meta.get("status") != "PASS":
        raise ValueError("archived A spectrum metadata is not PASS")
    if source_meta.get("detector_response_applied") is not False:
        raise ValueError("source spectrum must be pre-detector")
    particle = source_meta["particle_parameters"]
    mchi = float(particle["mchi_GeV"])
    mV = float(particle["mV_GeV"])
    coupling_sq = float(particle["coupling_product_squared"])
    prefactor = rate_prefactor(source_meta)

    source_spectrum = read_csv(spectrum_path)
    isotope_rows = read_csv(isotope_path)
    if not source_spectrum or not isotope_rows:
        raise ValueError("empty A-spectrum or isotope-kernel input")

    expected_benchmarks = set(particle["benchmarks"])
    spectrum_groups: dict[tuple[str, str, float], dict] = {}
    for row in source_spectrum:
        key = (row["benchmark"], row["scenario"], number(row, "ER_keV"))
        if key in spectrum_groups:
            raise ValueError(f"duplicate A spectrum key {key}")
        spectrum_groups[key] = row

    isotope_groups: dict[tuple[str, float], list[dict[str, str]]] = defaultdict(list)
    for row in isotope_rows:
        key = (row["benchmark"], number(row, "ER_keV"))
        isotope_groups[key].append(row)

    q2_values = sorted({
        number(row, "q_exact_spatial_GeV") ** 2 for row in isotope_rows
    })
    q2_index = {format(q2, ".17g"): i for i, q2 in enumerate(q2_values)}
    q2_index_for_row = {
        (row["benchmark"], number(row, "ER_keV"), int(row["A"])):
            q2_index[format(number(row, "q_exact_spatial_GeV") ** 2, ".17g")]
        for row in isotope_rows
    }

    central_ff = cM_and_factor(np.asarray(q2_values), strange_model)
    fm_draws = sample_cM_draws(
        np.asarray(q2_values), n_draws=n_draws, seed=seed,
        strange_model=strange_model,
    )
    if fm_draws.shape != (n_draws, len(q2_values)):
        raise ArithmeticError(f"unexpected F_M draw shape {fm_draws.shape}")
    multiplier_draws = fm_draws * fm_draws
    central_multipliers = np.asarray(central_ff["rate_multiplier"], dtype=float)

    output_rows: list[dict] = []
    isotope_output_rows: list[dict] = []
    max_a_closure = 0.0
    max_ff_multiplier = 0.0
    min_ff_multiplier = math.inf

    for benchmark in sorted(expected_benchmarks):
        for ER in sorted({
            energy for (b, energy) in isotope_groups if b == benchmark
        }):
            rows = isotope_groups[(benchmark, ER)]
            for scenario in SCENARIOS:
                weighted_A = 0.0
                weighted_B = 0.0
                draw_rate = np.zeros(n_draws, dtype=float)
                isotope_contributions = []
                for row in rows:
                    A = int(row["A"])
                    atom_fraction = number(row, "natural_atom_fraction")
                    base_kernel = number(row, "kernel_halo_integral_GeV")
                    mA = number(row, "mA_GeV")
                    q = number(row, "q_exact_spatial_GeV")
                    q2 = q*q
                    R_A = response_for_scenario(row, scenario)
                    if R_A == 0.0 or base_kernel == 0.0:
                        continue
                    denominator = (mV*mV + q2)**2
                    a_contribution = (
                        prefactor * atom_fraction * base_kernel * R_A / denominator
                    )
                    idx = q2_index_for_row[(benchmark, ER, A)]
                    ff_multiplier = float(central_multipliers[idx])
                    b_contribution = a_contribution * ff_multiplier
                    weighted_A += a_contribution
                    weighted_B += b_contribution
                    draw_rate += a_contribution * multiplier_draws[:, idx]
                    max_ff_multiplier = max(max_ff_multiplier, ff_multiplier)
                    min_ff_multiplier = min(min_ff_multiplier, ff_multiplier)
                    isotope_contributions.append({
                        "benchmark": benchmark,
                        "scenario": scenario,
                        "ER_keV": ER,
                        "A": A,
                        "natural_atom_fraction": atom_fraction,
                        "mA_GeV": mA,
                        "q_A_GeV": q,
                        "Q_A2_GeV2": q2,
                        "t_N_GeV2": -q2,
                        "c_M": float(central_ff["cM"][idx]),
                        "F_M": float(central_ff["F_M"][idx]),
                        "nucleon_FF_rate_multiplier": ff_multiplier,
                        "rate_A_contribution_events_kg_day_keV": a_contribution,
                        "rate_B_contribution_events_kg_day_keV": b_contribution,
                    })
                if weighted_A == 0.0 and weighted_B == 0.0:
                    pass
                elif weighted_A <= 0.0:
                    raise ArithmeticError(f"non-positive A rate for {benchmark}/{scenario}/{ER}")
                reconstructed_A = weighted_A
                original = spectrum_groups[(benchmark, scenario, ER)]
                original_A = number(original, "rate_events_kg_day_keV")
                closure = abs(reconstructed_A/original_A - 1.0) if original_A > 0 else (
                    0.0 if reconstructed_A == 0.0 else math.inf
                )
                max_a_closure = max(max_a_closure, closure)
                if closure > closure_tolerance:
                    raise ArithmeticError(
                        f"A-spectrum reconstruction failed for {benchmark}/{scenario}/{ER}: "
                        f"{closure:.6e} > {closure_tolerance:.6e}"
                    )
                if weighted_A > 0.0:
                    b_over_a = weighted_B / weighted_A
                else:
                    b_over_a = 1.0
                output_rows.append({
                    "benchmark": benchmark,
                    "scenario": scenario,
                    "ER_keV": ER,
                    "rate_events_kg_day_keV": weighted_B,
                    "rate_A_events_kg_day_keV": reconstructed_A,
                    "rate_B_events_kg_day_keV": weighted_B,
                    "B_over_A_rate": b_over_a,
                    "B_over_A_rate_shift_pct": (b_over_a-1.0)*100.0,
                    "nucleon_FF_rate_multiplier": b_over_a,
                    "rate_B_p16": float(np.percentile(draw_rate, 16)),
                    "rate_B_p50": float(np.percentile(draw_rate, 50)),
                    "rate_B_p84": float(np.percentile(draw_rate, 84)),
                    "B_rate_covariance_half_width_pct": (
                        50.0*(np.percentile(draw_rate, 84)-np.percentile(draw_rate, 16))
                        / np.percentile(draw_rate, 50)
                        if np.percentile(draw_rate, 50) > 0.0 else 0.0
                    ),
                    "coupling_product_sq": coupling_sq,
                    "mchi_GeV": mchi,
                    "mV_GeV": mV,
                    "g2_for_pole_width": float(particle["g2_for_width"]),
                    "rhoDM_GeV_cm3": float(particle["rhoDM_GeV_cm3"]),
                    "vmax_km_s": float(source_meta["halo"]["vmax_lab_km_s"]),
                    "available_atom_fraction": float(source_meta["natural_atom_fraction_AFH7"]),
                    "missing_atom_fraction": float(source_meta["natural_atom_fraction_missing"]),
                    "A2_weighted_AFH_coverage_at_q0": float(source_meta["A2_weighted_AFH_coverage_at_q0"]),
                    "mass_scheme": source_meta["nuclear_mass_scheme"],
                    "response_q_convention": "exact spatial q",
                    "width_scheme": "conditional Dirac pure-scalar pole width",
                    "detector_response_applied": False,
                })
                isotope_output_rows.extend(isotope_contributions)

    out_dir.mkdir(parents=True, exist_ok=True)
    output_csv = out_dir / "afh_hybrid9_B_natural_xenon_spectrum.csv"
    isotope_csv = out_dir / "afh_hybrid9_B_isotope_contributions.csv"
    write_csv(output_csv, output_rows)
    write_csv(isotope_csv, isotope_output_rows)

    metadata = {
        "status": "PASS",
        "calculation": "absolute natural-xenon rate-level B baseline applied to archived isotope-resolved AFH-7/Hybrid-9 three-body kernels",
        "baseline": "B = finite nucleon F1(t_N), F2(t_N) times finite-size nuclear response",
        "nucleon_form_factor_model": "Borah et al. (2020) separate proton/neutron low-Q2 z-expansion; correlated coefficient covariance",
        "strange_form_factor_model": strange_model,
        "strange_input_metadata": central_ff["strange_metadata"],
        "matching": {
            "F_i_uds": "3*(F_i_EM,p+F_i_EM,n+F_i_s,unit)",
            "c_M": "F1_uds+t_N/(8*m_N^2)*(F1_uds+2*F2_uds)",
            "F_M": "c_M/3",
            "rate_multiplier": "|F_M|^2",
            "Q_A2": "q_exact_spatial_GeV^2 = 2*m_A*E_R+E_R^2",
            "t_N": "-Q_A2",
            "nuclear_response": "archived direct AFH v6.0 W_M for seven isotopes; Helm fallback only for Hybrid-9 Xe-124/Xe-126",
        },
        "uncertainty": {
            "Borah2020_EM_coefficient_covariance_draws": n_draws,
            "seed": seed,
            "strange_lattice_uncertainties_sampled": False,
        },
        "source_files": {
            "A_spectrum_csv": str(spectrum_path.relative_to(ROOT)),
            "A_spectrum_sha256": sha256(spectrum_path),
            "isotope_kernel_csv": str(isotope_path.relative_to(ROOT)),
            "isotope_kernel_sha256": sha256(isotope_path),
            "source_metadata_json": str(source_meta_path.relative_to(ROOT)),
            "source_metadata_sha256": sha256(source_meta_path),
        },
        "source_A_metadata": source_meta,
        "particle_parameters": particle,
        "halo": source_meta["halo"],
        "recoil_grid_keV": source_meta["recoil_grid_keV"],
        "response_convention": source_meta["response_convention"],
        "afh_source_file": source_meta["afh_source_file"],
        "afh_source_sha256": source_meta["afh_source_sha256"],
        "natural_atom_fraction_AFH7": source_meta["natural_atom_fraction_AFH7"],
        "natural_atom_fraction_missing": source_meta["natural_atom_fraction_missing"],
        "A2_weighted_AFH_coverage_at_q0": source_meta["A2_weighted_AFH_coverage_at_q0"],
        "nuclear_mass_scheme": source_meta["nuclear_mass_scheme"],
        "detector_response_applied": False,
        "row_counts": {
            "natural_xenon_spectra": len(output_rows),
            "isotope_contributions": len(isotope_output_rows),
        },
        "validation": {
            "maximum_A_reconstruction_relative_difference": max_a_closure,
            "A_reconstruction_tolerance": closure_tolerance,
            "minimum_central_isotope_FF_rate_multiplier": min_ff_multiplier,
            "maximum_central_isotope_FF_rate_multiplier": max_ff_multiplier,
        },
        "output_files": {
            "spectrum_csv": output_csv.name,
            "isotope_contributions_csv": isotope_csv.name,
        },
    }
    metadata_path = out_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    (out_dir / "SHA256SUMS.txt").write_text(
        f"{sha256(output_csv)}  {output_csv.name}\n"
        f"{sha256(isotope_csv)}  {isotope_csv.name}\n"
        f"{sha256(metadata_path)}  {metadata_path.name}\n",
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--strange-model", choices=STRANGE_MODELS, required=True)
    p.add_argument("--draws", type=int, default=3000)
    p.add_argument("--seed", type=int, default=20261119)
    p.add_argument("--closure-tolerance", type=float, default=2.0e-11)
    a = p.parse_args()
    result = run(a.source_dir, a.out_dir, a.strange_model, a.draws, a.seed, a.closure_tolerance)
    print(json.dumps(result["validation"], indent=2))


if __name__ == "__main__":
    main()
