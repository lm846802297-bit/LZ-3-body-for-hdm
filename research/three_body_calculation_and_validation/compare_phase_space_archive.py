#!/usr/bin/env python3
"""Compare fresh P1 phase-space CSVs with the committed audit archive.

Primary numerical columns are compared across runs. Derived relative-difference
columns are validated against their defining formula within each run instead of
being compared directly across runs: a small allowed shift in I6 necessarily
propagates into a different relative-to-reference diagnostic.
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

CSV_NAMES = (
    "phase_space_mapping_convergence.csv",
    "phase_space_angular_convergence.csv",
    "phase_space_threshold_convergence.csv",
    "phase_space_li_prefactor_crosscheck.csv",
    "phase_space_historical_800_anchor.csv",
)

DERIVED_COLUMNS = {
    "relative_to_archived": ("I6_GeV2", "archived_I6_GeV2"),
    "relative_to_high_order_reference": ("I6_GeV2", "reference_I6_GeV2"),
}
DERIVED_ABS_TOL = 5e-12


def _derived_column_failures(
    row: dict[str, str], key: str, source: str, row_index: int
) -> list[str]:
    numerator_key, denominator_key = DERIVED_COLUMNS[key]
    try:
        numerator = float(row[numerator_key])
        denominator = float(row[denominator_key])
        actual = float(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        return [f"{source}:{row_index}:{key}: cannot evaluate defining formula ({exc})"]
    if denominator == 0.0:
        return [f"{source}:{row_index}:{key}: zero denominator in defining formula"]
    expected = numerator / denominator - 1.0
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=DERIVED_ABS_TOL):
        return [
            f"{source}:{row_index}:{key}: {actual} is inconsistent with "
            f"{numerator_key}/{denominator_key}-1 = {expected}"
        ]
    return []


def compare_rows(
    name: str,
    old_rows: list[dict[str, str]],
    new_rows: list[dict[str, str]],
    relative_tolerance: float = 5e-8,
    absolute_tolerance: float = 1e-12,
) -> list[str]:
    failures: list[str] = []
    if len(old_rows) != len(new_rows):
        return [f"{name}: row count {len(new_rows)} != {len(old_rows)}"]

    for row_index, (old, new) in enumerate(zip(old_rows, new_rows), start=2):
        if set(old) != set(new):
            failures.append(f"{name}:{row_index}: columns differ")
            continue

        for key in old:
            if key == "mass_scheme":
                historical_alias = {old[key], new[key]} == {
                    "historical_A_times_u_approx",
                    "coarse_mA_122_GeV_approx",
                }
                same_coarse_mass = math.isclose(
                    float(old["mA_GeV"]), 122.0, rel_tol=0.0, abs_tol=1e-12
                ) and math.isclose(
                    float(new["mA_GeV"]), 122.0, rel_tol=0.0, abs_tol=1e-12
                )
                if old[key] != new[key] and not (historical_alias and same_coarse_mass):
                    failures.append(f"{name}:{row_index}:{key}: {old[key]} != {new[key]}")
                    break
                continue

            if key in DERIVED_COLUMNS:
                derived_failures = _derived_column_failures(
                    old, key, f"{name}:reference", row_index
                ) + _derived_column_failures(
                    new, key, f"{name}:fresh", row_index
                )
                if derived_failures:
                    failures.extend(derived_failures)
                    break
                continue

            try:
                old_value, new_value = float(old[key]), float(new[key])
            except (TypeError, ValueError):
                if old[key] != new[key]:
                    failures.append(f"{name}:{row_index}:{key}: {old[key]} != {new[key]}")
                    break
            else:
                if not math.isclose(
                    old_value,
                    new_value,
                    rel_tol=relative_tolerance,
                    abs_tol=absolute_tolerance,
                ):
                    failures.append(
                        f"{name}:{row_index}:{key}: {old_value} != {new_value}"
                    )
                    break
    return failures


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def compare_directories(
    reference_dir: Path,
    fresh_dir: Path,
    relative_tolerance: float = 5e-8,
) -> list[str]:
    failures: list[str] = []
    for name in CSV_NAMES:
        reference_path = reference_dir / name
        fresh_path = fresh_dir / name
        if not reference_path.is_file():
            failures.append(f"{name}: missing reference file {reference_path}")
            continue
        if not fresh_path.is_file():
            failures.append(f"{name}: missing fresh file {fresh_path}")
            continue
        failures.extend(
            compare_rows(
                name,
                _read_rows(reference_path),
                _read_rows(fresh_path),
                relative_tolerance=relative_tolerance,
            )
        )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-dir", type=Path, required=True)
    parser.add_argument("--fresh-dir", type=Path, required=True)
    parser.add_argument("--relative-tolerance", type=float, default=5e-8)
    args = parser.parse_args()

    failures = compare_directories(
        args.reference_dir,
        args.fresh_dir,
        relative_tolerance=args.relative_tolerance,
    )
    if failures:
        raise SystemExit("\n".join(failures))

    print("Fresh phase-space scans reproduce all primary numerical columns within tolerance.")
    print("Derived relative-difference columns were independently checked against their defining formulas.")
    print("Accepted only the historical/coarse mass-scheme label alias when both mA_GeV values are exactly 122.")
    print("The off-shell near-pole scan remains a separate reproduction artifact, not a committed reference CSV.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
