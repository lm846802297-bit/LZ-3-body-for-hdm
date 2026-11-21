#!/usr/bin/env python3
"""Numerically compare freshly regenerated AFH audit outputs with the archive."""

import argparse
import csv
import math
from pathlib import Path

FILES = (
    "zero_momentum_normalization.csv",
    "multipole_reconstruction.csv",
    "selected_recoil_shape_comparison.csv",
    "first_local_minima_grid.csv",
    "xe131_rank2_fraction.csv",
)


def rows(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def is_number(value):
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def compare_file(generated, archived):
    left, right = rows(generated), rows(archived)
    if len(left) != len(right):
        raise AssertionError(f"{generated.name}: row count differs {len(left)} != {len(right)}")
    if not left:
        raise AssertionError(f"{generated.name}: empty output")
    if list(left[0]) != list(right[0]):
        raise AssertionError(f"{generated.name}: columns differ")
    for i, (a, b) in enumerate(zip(left, right), start=2):
        for key in a:
            if is_number(a[key]) and is_number(b[key]):
                if not math.isclose(float(a[key]), float(b[key]), rel_tol=1e-12, abs_tol=1e-15):
                    raise AssertionError(
                        f"{generated.name}:{i}:{key}: {a[key]} != archived {b[key]}"
                    )
            elif a[key] != b[key]:
                raise AssertionError(
                    f"{generated.name}:{i}:{key}: {a[key]!r} != archived {b[key]!r}"
                )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-dir", type=Path, required=True)
    parser.add_argument("--archived-dir", type=Path, required=True)
    args = parser.parse_args()
    for name in FILES:
        compare_file(args.generated_dir / name, args.archived_dir / name)
        print(f"PASS {name}")
    print("PASS all archived AFH isotope audit tables reproduce within numeric tolerance")


if __name__ == "__main__":
    main()
