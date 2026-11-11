#!/usr/bin/env python3
"""Compare a fresh exact-spatial-q halo fold with the archived selected-point rates."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def close_value(label, archived, reproduced, rel_tol, abs_tol=1e-300):
    a = float(archived)
    b = float(reproduced)
    if not math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol):
        raise AssertionError(
            f"{label} mismatch: archived={a:.16e}, reproduced={b:.16e}, "
            f"relative={(b-a)/a if a else math.inf:.6e}"
        )
    return abs((b-a)/a) if a else abs(b)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reproduced-dir", type=Path, required=True)
    parser.add_argument("--archived-results-dir", type=Path, default=RESULTS)
    parser.add_argument("--relative-tolerance", type=float, default=5e-8)
    args = parser.parse_args()

    archived = read_csv(args.archived_results_dir / "isotope_halo_contributions_compact.csv")
    reproduced = read_csv(args.reproduced_dir / "isotope_halo_contributions.csv")
    archived_rates = read_csv(args.archived_results_dir / "natural_xenon_halo_rates.csv")
    reproduced_rates = read_csv(args.reproduced_dir / "natural_xenon_halo_rates.csv")
    metadata = json.loads((args.reproduced_dir / "metadata.json").read_text(encoding="utf-8"))

    if metadata.get("response_q_convention") not in ("exact_spatial", "legacy_exact", "legacy_exact_spatial"):
        raise AssertionError(
            "reproduction metadata does not identify the exact spatial AFH response-q convention"
        )
    if len(archived) != 98 or len(reproduced) != 98:
        raise AssertionError(f"expected 98 isotope rows; got archived={len(archived)}, reproduced={len(reproduced)}")
    if len(archived_rates) != 14 or len(reproduced_rates) != 14:
        raise AssertionError("expected 14 rate-summary rows")

    fields = {
        "abundance": "abundance",
        "mA_GeV": "mA_GeV",
        "q_response_GeV": "q_response_GeV",
        "R_A": "R_A",
        "vmin_km_s": "vmin_km_s",
        "J_A_GeV": "J_A_GeV",
        "rate_contribution_events_kg_day_keV": "rate_contribution_events_kg_day_keV",
    }
    rep_index = {
        (r["benchmark"], float(r["ER_keV"]), r["halo_model"], int(r["A"])): r
        for r in reproduced
    }
    if len(rep_index) != len(reproduced):
        raise AssertionError("duplicate isotope key in reproduced rows")

    max_relative = {field: 0.0 for field in fields}
    for old in archived:
        key = (old["benchmark"], float(old["ER_keV"]), old["halo_model"], int(old["A"]))
        if key not in rep_index:
            raise AssertionError(f"missing reproduced isotope row: {key}")
        new = rep_index[key]
        if old["open"].lower() != new["open"].lower():
            raise AssertionError(f"phase-space-open mismatch for {key}")
        for field, new_field in fields.items():
            delta = close_value(
                f"{field} at {key}", old[field], new[new_field],
                args.relative_tolerance
            )
            max_relative[field] = max(max_relative[field], delta)

    rate_index = {
        (r["benchmark"], float(r["ER_keV"]), r["halo_model"]): r
        for r in reproduced_rates
    }
    max_rate_relative = 0.0
    for old in archived_rates:
        key = (old["benchmark"], float(old["ER_keV"]), old["halo_model"])
        if key not in rate_index:
            raise AssertionError(f"missing reproduced rate row: {key}")
        new = rate_index[key]
        if old["open_isotopes"] != new["open_isotopes"]:
            raise AssertionError(f"open-isotope set mismatch for {key}")
        if not math.isclose(
            float(old["open_abundance_fraction"]),
            float(new["open_abundance_fraction"]),
            rel_tol=0.0, abs_tol=2e-12
        ):
            raise AssertionError(f"open abundance mismatch for {key}")
        max_rate_relative = max(
            max_rate_relative,
            close_value("total rate", old["rate_events_kg_day_keV"],
                        new["rate_events_kg_day_keV"], args.relative_tolerance)
        )

    summary = {
        "status": "pass",
        "response_q_convention": metadata["response_q_convention"],
        "isotope_rows_compared": len(archived),
        "rate_rows_compared": len(archived_rates),
        "relative_tolerance": args.relative_tolerance,
        "maximum_relative_differences_by_field": max_relative,
        "maximum_relative_total_rate_difference": max_rate_relative,
        "interpretation": "The updated halo-fold code reproduces the archived selected-point results using the exact spatial AFH momentum transfer. The q_NR=sqrt(2*m_A*E_R) option is a separate non-relativistic approximation.",
    }
    (args.reproduced_dir / "legacy_reproduction_comparison.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
