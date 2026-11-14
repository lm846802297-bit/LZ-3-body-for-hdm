#!/usr/bin/env python3
"""Compare the independent Python port with the pinned NEST C++ implementation."""
from __future__ import annotations

import argparse
import csv
import math
import subprocess
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
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


def run_cpp(executable: Path, isotope: int, old_w13ev: bool):
    args = [
        str(executable), str(DENSITY), str(FIELD), str(MOLAR_MASS),
        str(isotope), "true" if old_w13ev else "false",
        *[str(e) for e in ENERGIES_KEV],
    ]
    completed = subprocess.run(args, check=True, capture_output=True, text=True)
    rows = list(csv.DictReader(completed.stdout.splitlines()))
    if len(rows) != len(ENERGIES_KEV):
        raise RuntimeError(f"NEST C++ returned {len(rows)} rows, expected {len(ENERGIES_KEV)}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    args = parser.parse_args()
    if not args.executable.is_file():
        raise FileNotFoundError(args.executable)

    comparisons = 0
    worst = 0.0
    for isotope in ISOTOPES:
        for old_flag in OLD_W_FLAGS:
            cpp_rows = run_cpp(args.executable, isotope, old_flag)
            for energy, row in zip(ENERGIES_KEV, cpp_rows):
                py = nr_mean_yield(
                    energy_keV=energy,
                    field_V_cm=FIELD,
                    density_g_cm3=DENSITY,
                    molar_mass_g_mol=MOLAR_MASS,
                    isotope_mass_number=isotope,
                    old_w13ev=old_flag,
                )
                pairs = (
                    ("photons_mean", py.photons_mean, float(row["photons_mean"])),
                    ("electrons_mean", py.electrons_mean, float(row["electrons_mean"])),
                    ("lindhard", py.lindhard, float(row["lindhard"])),
                    ("exciton_ratio", py.exciton_to_ion_ratio, float(row["exciton_ratio"])),
                )
                for name, py_value, cpp_value in pairs:
                    if not math.isclose(py_value, cpp_value, rel_tol=REL_TOL, abs_tol=ABS_TOL):
                        raise AssertionError(
                            f"Mismatch A={isotope}, OldW13eV={old_flag}, "
                            f"E={energy} keV, {name}: Python={py_value:.17g}, "
                            f"NEST C++={cpp_value:.17g}"
                        )
                    scale = max(abs(py_value), abs(cpp_value), 1.0)
                    worst = max(worst, abs(py_value - cpp_value) / scale)
                    comparisons += 1

    print("PASS: independent Python mean-yield port agrees with pinned NEST C++")
    print(f"isotopes={len(ISOTOPES)} old_w13ev_modes={len(OLD_W_FLAGS)}")
    print(f"energies_per_case={len(ENERGIES_KEV)} scalar_comparisons={comparisons}")
    print(f"worst_scaled_absolute_difference={worst:.3e}")
    print(f"relative_tolerance={REL_TOL:.1e} absolute_tolerance={ABS_TOL:.1e}")
    print("NOTE: this validates NR mean yields only, not fluctuations or detector S1/S2 PDFs.")


if __name__ == "__main__":
    main()
