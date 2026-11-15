#!/usr/bin/env python3
"""Compare Table S5 and EFT2024 mean yields with pinned NEST C++."""
from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
EXT = HERE / "lz_2026_extended_nr"
sys.path.insert(0, str(HERE))
from lz_2026_extended_nr.lz_2026_nr_mean_yield import nr_mean_yield

ENERGIES_KEV = (5.4, 10.0, 50.0, 74.7, 75.0, 100.0, 150.0, 200.0, 248.0, 269.9, 330.0)
ISOTOPES = (128, 131, 136)
OLD_W_FLAGS = (True, False)
DENSITY = 2.90
FIELD = 97.0
MOLAR_MASS = 131.293
REL_TOL = 3.0e-11
ABS_TOL = 3.0e-11
NEST_COMMIT = "541b6430dae6ea289cf110c99f174a9187f7fdee"


def load_parameter_families() -> dict[str, tuple[float, ...]]:
    candidate_path = EXT / "lz_2026_nest_eft2024_configuration_candidate.json"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    return {
        "tableS5": tuple(
            __import__(
                "lz_2026_extended_nr.lz_2026_nr_mean_yield",
                fromlist=["LZ2026_NR_YIELD_PARAMETERS"],
            ).LZ2026_NR_YIELD_PARAMETERS
        ),
        "eft2024": tuple(candidate["nr_mean_yield"]["source_code_vector"]),
    }


def run_cpp(
    executable: Path, isotope: int, old_w13ev: bool, model: str
) -> list[dict[str, str]]:
    args = [
        str(executable), str(DENSITY), str(FIELD), str(MOLAR_MASS),
        str(isotope), "true" if old_w13ev else "false", model,
        *[str(e) for e in ENERGIES_KEV],
    ]
    completed = subprocess.run(args, check=True, capture_output=True, text=True)
    rows = list(csv.DictReader(completed.stdout.splitlines()))
    if len(rows) != len(ENERGIES_KEV):
        raise RuntimeError(
            f"NEST C++ returned {len(rows)} rows for {model}, expected {len(ENERGIES_KEV)}"
        )
    if any(row["model"] != model for row in rows):
        raise RuntimeError(f"NEST C++ returned a mismatched model label for {model}")
    return rows


def build_rounding_effects(
    parameter_families: dict[str, tuple[float, ...]]
) -> list[dict]:
    rows = []
    for energy in ENERGIES_KEV:
        table = nr_mean_yield(
            energy_keV=energy,
            field_V_cm=FIELD,
            density_g_cm3=DENSITY,
            molar_mass_g_mol=MOLAR_MASS,
            isotope_mass_number=131,
            old_w13ev=True,
            params=parameter_families["tableS5"],
        )
        eft = nr_mean_yield(
            energy_keV=energy,
            field_V_cm=FIELD,
            density_g_cm3=DENSITY,
            molar_mass_g_mol=MOLAR_MASS,
            isotope_mass_number=131,
            old_w13ev=True,
            params=parameter_families["eft2024"],
        )
        def pct(new: float, reference: float) -> float:
            return 100.0 * (new / reference - 1.0) if reference else math.nan
        rows.append({
            "energy_keV": energy,
            "p_exponent_tableS5": table.p_exponent,
            "p_exponent_eft2024": eft.p_exponent,
            "delta_p_exponent": table.p_exponent - eft.p_exponent,
            "tableS5_vs_eft2024_photons_mean_percent": pct(
                table.photons_mean, eft.photons_mean
            ),
            "tableS5_vs_eft2024_electrons_mean_percent": pct(
                table.electrons_mean, eft.electrons_mean
            ),
            "tableS5_vs_eft2024_total_quanta_mean_percent": pct(
                table.total_quanta_mean, eft.total_quanta_mean
            ),
            "tableS5_photons_mean": table.photons_mean,
            "eft2024_photons_mean": eft.photons_mean,
            "tableS5_electrons_mean": table.electrons_mean,
            "eft2024_electrons_mean": eft.electrons_mean,
            "tableS5_total_quanta_mean": table.total_quanta_mean,
            "eft2024_total_quanta_mean": eft.total_quanta_mean,
        })
    return rows


def run_audit(executable: Path) -> dict:
    parameter_families = load_parameter_families()
    comparison_count = 0
    worst_by_model = {model: 0.0 for model in parameter_families}
    worst_detail = {model: None for model in parameter_families}

    for model, params in parameter_families.items():
        if len(params) != 15:
            raise ValueError(f"{model} NR mean-yield vector has {len(params)} entries")
        for isotope in ISOTOPES:
            for old_flag in OLD_W_FLAGS:
                cpp_rows = run_cpp(executable, isotope, old_flag, model)
                for energy, row in zip(ENERGIES_KEV, cpp_rows):
                    py = nr_mean_yield(
                        energy_keV=energy,
                        field_V_cm=FIELD,
                        density_g_cm3=DENSITY,
                        molar_mass_g_mol=MOLAR_MASS,
                        isotope_mass_number=isotope,
                        old_w13ev=old_flag,
                        params=params,
                    )
                    pairs = (
                        ("photons_mean", py.photons_mean, float(row["photons_mean"])),
                        ("electrons_mean", py.electrons_mean, float(row["electrons_mean"])),
                        ("lindhard", py.lindhard, float(row["lindhard"])),
                        ("exciton_ratio", py.exciton_to_ion_ratio, float(row["exciton_ratio"])),
                    )
                    for name, py_value, cpp_value in pairs:
                        if not math.isclose(
                            py_value, cpp_value, rel_tol=REL_TOL, abs_tol=ABS_TOL
                        ):
                            raise AssertionError(
                                f"Mismatch model={model}, A={isotope}, "
                                f"OldW13eV={old_flag}, E={energy} keV, {name}: "
                                f"Python={py_value:.17g}, NEST C++={cpp_value:.17g}"
                            )
                        scale = max(abs(py_value), abs(cpp_value), 1.0)
                        difference = abs(py_value - cpp_value) / scale
                        if difference > worst_by_model[model]:
                            worst_by_model[model] = difference
                            worst_detail[model] = {
                                "isotope": isotope,
                                "old_w13ev": old_flag,
                                "energy_keV": energy,
                                "quantity": name,
                                "scaled_absolute_difference": difference,
                            }
                        comparison_count += 1

    rounding_rows = build_rounding_effects(parameter_families)
    max_photon_change = max(
        abs(row["tableS5_vs_eft2024_photons_mean_percent"])
        for row in rounding_rows
    )
    max_electron_change = max(
        abs(row["tableS5_vs_eft2024_electrons_mean_percent"])
        for row in rounding_rows
    )
    max_total_quanta_change = max(
        abs(row["tableS5_vs_eft2024_total_quanta_mean_percent"])
        for row in rounding_rows
    )
    return {
        "study": "direct NEST C++ cross-check of rounded Table S5 and full-precision EFT2024 NR means",
        "nest_source_commit": NEST_COMMIT,
        "density_g_cm3": DENSITY,
        "field_V_cm": FIELD,
        "molar_mass_g_mol": MOLAR_MASS,
        "isotopes": list(ISOTOPES),
        "old_w13ev_modes": list(OLD_W_FLAGS),
        "energies_keV": list(ENERGIES_KEV),
        "parameter_families": {
            model: list(values) for model, values in parameter_families.items()
        },
        "cross_language_validation": {
            "status": "PASS",
            "scalar_comparisons": comparison_count,
            "relative_tolerance": REL_TOL,
            "absolute_tolerance": ABS_TOL,
            "worst_scaled_absolute_difference_by_model": worst_by_model,
            "worst_comparison_by_model": worst_detail,
            "scope": (
                "NR mean-yield equations only; not NR quanta fluctuations, S1/S2 "
                "response, spatial maps, or the full selected LZ detector response."
            ),
        },
        "rounding_effect_tableS5_relative_to_eft2024": rounding_rows,
        "max_absolute_rounding_effect_over_energy_grid_percent": {
            "photons_mean": max_photon_change,
            "electrons_mean": max_electron_change,
            "total_quanta_mean": max_total_quanta_change,
        },
        "interpretation": (
            "The high-energy p(E) extension is identical for the two vectors, "
            "but rounding alpha/beta and the Qy parameters changes the mean "
            "light/charge partition. Treat Table S5 and the full-precision "
            "EFT2024 vector as separate response hypotheses."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    args.executable = args.executable.resolve()
    if not args.executable.is_file():
        raise FileNotFoundError(args.executable)

    summary = run_audit(args.executable)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )

    print("PASS: Python mean-yield port agrees with pinned NEST C++ for both vectors")
    print(f"scalar_comparisons={summary['cross_language_validation']['scalar_comparisons']}")
    print(
        "worst_scaled_absolute_difference_by_model="
        + json.dumps(summary["cross_language_validation"]["worst_scaled_absolute_difference_by_model"])
    )
    print("Table S5 relative to EFT2024 at selected energies:")
    for row in summary["rounding_effect_tableS5_relative_to_eft2024"]:
        if row["energy_keV"] in (5.4, 74.7, 100.0, 200.0, 248.0, 269.9):
            print(
                f"E={row['energy_keV']:6.1f} keV "
                f"dNph={row['tableS5_vs_eft2024_photons_mean_percent']:+.4f}% "
                f"dNe={row['tableS5_vs_eft2024_electrons_mean_percent']:+.4f}% "
                f"dNq={row['tableS5_vs_eft2024_total_quanta_mean_percent']:+.4f}%"
            )
    if args.output_json:
        print(f"summary_json={args.output_json}")


if __name__ == "__main__":
    main()
