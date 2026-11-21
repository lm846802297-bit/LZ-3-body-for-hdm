#!/usr/bin/env python3
"""Merge the q=0 analytic-limit rows into the native spatial multipole export."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

COLUMNS = [
    "A", "q_GeV", "y", "multipole_J",
    "M_Delta_J_native", "M_SigmaPrime_J_native",
    "Im_M_Delta_J_native", "Im_M_SigmaPrime_J_native",
]


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_rows(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def update_metadata(path: Path, rows: list[dict], q0_rows: int) -> None:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    values["q_grid"] = (
        "2401 uniform nodes from 0 to 0.6 GeV, step 0.00025 GeV; "
        "q=0 value is the analytic y=0 limit"
    )
    values["q0_method"] = "analytic Limit[y->0] of the native DeltaJ and SigmaPJ OBDME sums"
    values["q0_rows"] = str(q0_rows)
    values["max_imaginary_residual"] = repr(max(
        max(abs(float(row["Im_M_Delta_J_native"])),
            abs(float(row["Im_M_SigmaPrime_J_native"])))
        for row in rows
    ))
    values["rows"] = str(len(rows))
    order = [
        "source", "source_commit", "AFH_source_path", "AFH_source_sha256",
        "wolfram_version", "isotopes", "q_grid", "q0_method", "q0_rows",
        "multipole_amplitudes", "isospin", "normalization",
        "imaginary_parts", "max_imaginary_residual", "rank_map", "rows",
    ]
    path.write_text(
        "\n".join(f"{key}={values[key]}" for key in order if key in values) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-csv", type=Path, required=True)
    parser.add_argument("--q0-csv", type=Path, required=True)
    parser.add_argument("--out-csv", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    args = parser.parse_args()

    main_rows = read_rows(args.main_csv)
    q0_rows = read_rows(args.q0_csv)
    if len(q0_rows) != 4:
        raise ValueError(f"expected 4 q=0 rows, got {len(q0_rows)}")
    keys = [
        (int(float(row["A"])), round(float(row["q_GeV"]), 10), int(float(row["multipole_J"])))
        for row in main_rows + q0_rows
    ]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate A/q/J row while merging")

    rows = sorted(
        main_rows + q0_rows,
        key=lambda row: (
            int(float(row["A"])),
            round(float(row["q_GeV"]), 10),
            int(float(row["multipole_J"]))
        ),
    )
    if len(rows) != 9604:
        raise ValueError(f"expected 9604 merged rows, got {len(rows)}")
    write_rows(args.out_csv, rows)
    update_metadata(args.metadata, rows, len(q0_rows))
    print(f"wrote {len(rows)} rows to {args.out_csv}")


if __name__ == "__main__":
    main()
