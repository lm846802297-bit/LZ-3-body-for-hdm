#!/usr/bin/env python3
"""Compare full-response natural-xenon folds at NIST and AME2020 nuclear masses."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no comparison rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def relative_difference(reference: float, value: float) -> float:
    if reference == 0.0:
        return 0.0 if value == 0.0 else math.inf
    return value/reference - 1.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nist-dir", type=Path, required=True)
    parser.add_argument("--ame-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    nist_totals = read_csv(args.nist_dir/"natural_xenon_halo_rates.csv")
    ame_totals = read_csv(args.ame_dir/"natural_xenon_halo_rates.csv")
    nist_keyed = {
        (r["benchmark"], float(r["ER_keV"]), r["halo_model"]): r
        for r in nist_totals
    }
    ame_keyed = {
        (r["benchmark"], float(r["ER_keV"]), r["halo_model"]): r
        for r in ame_totals
    }
    if set(nist_keyed) != set(ame_keyed):
        raise ValueError("NIST and AME2020 total-rate case sets differ")

    total_comparison = []
    for key in sorted(nist_keyed):
        n, a = nist_keyed[key], ame_keyed[key]
        rn = float(n["rate_events_kg_day_keV"])
        ra = float(a["rate_events_kg_day_keV"])
        total_comparison.append({
            "benchmark": key[0],
            "ER_keV": key[1],
            "halo_model": key[2],
            "rate_nist_nuclear": rn,
            "rate_ame2020_nuclear": ra,
            "relative_ame2020_vs_nist": relative_difference(rn, ra),
            "open_isotopes_nist": n["open_isotopes"],
            "open_isotopes_ame2020": a["open_isotopes"],
            "open_abundance_nist": float(n["open_abundance_fraction"]),
            "open_abundance_ame2020": float(a["open_abundance_fraction"]),
        })
    write_csv(args.out_dir/"natural_xenon_mass_scheme_comparison.csv", total_comparison)

    nist_parts = read_csv(args.nist_dir/"isotope_halo_contributions.csv")
    ame_parts = read_csv(args.ame_dir/"isotope_halo_contributions.csv")
    def pkey(r):
        return (r["benchmark"], float(r["ER_keV"]), r["halo_model"], int(r["A"]))
    nist_part_keyed = {pkey(r): r for r in nist_parts}
    ame_part_keyed = {pkey(r): r for r in ame_parts}
    if set(nist_part_keyed) != set(ame_part_keyed):
        raise ValueError("NIST and AME2020 isotope-partial case sets differ")

    partial_comparison = []
    for key in sorted(nist_part_keyed):
        n, a = nist_part_keyed[key], ame_part_keyed[key]
        rn = float(n["rate_contribution_events_kg_day_keV"])
        ra = float(a["rate_contribution_events_kg_day_keV"])
        partial_comparison.append({
            "benchmark": key[0],
            "ER_keV": key[1],
            "halo_model": key[2],
            "A": key[3],
            "abundance": float(a["abundance"]),
            "mA_NIST_GeV": float(n["mA_GeV"]),
            "mA_AME2020_GeV": float(a["mA_GeV"]),
            "q_exact_NIST_GeV": float(n["q_exact_GeV"]),
            "q_exact_AME2020_GeV": float(a["q_exact_GeV"]),
            "R_A_NIST": float(n["R_A"]),
            "R_A_AME2020": float(a["R_A"]),
            "vmin_NIST_km_s": float(n["vmin_km_s"]),
            "vmin_AME2020_km_s": float(a["vmin_km_s"]),
            "rate_NIST": rn,
            "rate_AME2020": ra,
            "relative_AME2020_vs_NIST": relative_difference(rn, ra),
        })
    write_csv(args.out_dir/"isotope_mass_scheme_comparison.csv", partial_comparison)

    finite_total_shifts = [
        abs(r["relative_ame2020_vs_nist"])
        for r in total_comparison
        if math.isfinite(r["relative_ame2020_vs_nist"])
    ]
    finite_partial_shifts = [
        abs(r["relative_AME2020_vs_NIST"])
        for r in partial_comparison
        if math.isfinite(r["relative_AME2020_vs_NIST"])
    ]
    metadata = {
        "status": "pass",
        "total_rate_rows_compared": len(total_comparison),
        "isotope_partial_rows_compared": len(partial_comparison),
        "maximum_absolute_total_rate_shift_AME2020_vs_NIST": max(finite_total_shifts, default=0.0),
        "maximum_absolute_isotope_partial_shift_AME2020_vs_NIST": max(finite_partial_shifts, default=0.0),
        "open_isotope_sets_identical": all(
            r["open_isotopes_nist"] == r["open_isotopes_ame2020"]
            for r in total_comparison
        ),
        "available_isotope_abundance_sum": 0.998158,
        "abundance_renormalization": False,
    }
    (args.out_dir/"metadata.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    main()
