#!/usr/bin/env python3
"""Build a Xe-131-only AME2020 replacement diagnostic for the natural-Xe sum.

The six other AFH isotope terms are intentionally retained at their archived
NIST-mass baseline. This is a hybrid sensitivity diagnostic, not a full
AME2020 natural-xenon prediction.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def key(row: dict[str, str]) -> tuple[str, float, str]:
    return row["benchmark"], float(row["ER_keV"]), row["halo_model"]


def build_hybrid_rows(
    baseline_isotopes: list[dict[str, str]],
    baseline_totals: list[dict[str, str]],
    xe131_partials: list[dict[str, str]],
    *,
    max_nist_baseline_relative_difference: float = 5e-9,
) -> tuple[list[dict], dict]:
    """Replace only the Xe-131 term by its AME2020/exact-spatial value."""
    baseline_131 = {
        key(r): float(r["rate_contribution_events_kg_day_keV"])
        for r in baseline_isotopes
        if int(r["A"]) == 131
    }
    totals = {key(r): r for r in baseline_totals}

    partials = [
        r for r in xe131_partials
        if r["response_q_convention"] == "exact_spatial"
        and int(r["nv"]) == 32
        and r["mass_scheme"] in ("nist_nuclear", "ame2020_nuclear")
    ]
    nist = {
        key(r): float(r["Xe131_partial_rate_events_kg_day_keV"])
        for r in partials if r["mass_scheme"] == "nist_nuclear"
    }
    ame = {
        key(r): float(r["Xe131_partial_rate_events_kg_day_keV"])
        for r in partials if r["mass_scheme"] == "ame2020_nuclear"
    }

    expected = set(totals)
    if set(baseline_131) != expected:
        raise ValueError("NIST baseline Xe-131 isotope rows do not match total-rate keys")
    if set(nist) != expected or set(ame) != expected:
        raise ValueError("Xe-131 NIST/AME2020 exact-spatial partial-rate keys are incomplete")

    rows = []
    max_baseline_difference = 0.0
    for k in sorted(expected):
        base_total = float(totals[k]["rate_events_kg_day_keV"])
        nist_compact = baseline_131[k]
        nist_recomputed = nist[k]
        ame_rate = ame[k]

        if nist_compact > 0.0:
            rel_check = abs(nist_recomputed / nist_compact - 1.0)
            max_baseline_difference = max(max_baseline_difference, rel_check)
            if rel_check > max_nist_baseline_relative_difference:
                raise ArithmeticError(
                    f"NIST baseline mismatch for {k}: {rel_check:.3e}"
                )
        else:
            rel_check = 0.0 if nist_recomputed == 0.0 else math.inf
            if not math.isfinite(rel_check):
                raise ArithmeticError(f"zero/nonzero NIST baseline mismatch for {k}")

        hybrid_total = base_total - nist_compact + ame_rate
        if base_total > 0.0:
            xe131_fraction = nist_compact / base_total
            hybrid_shift = hybrid_total / base_total - 1.0
        else:
            xe131_fraction = None
            hybrid_shift = None

        if nist_compact > 0.0:
            xe131_rate_shift = ame_rate / nist_compact - 1.0
        else:
            xe131_rate_shift = 0.0 if ame_rate == 0.0 else None

        rows.append({
            "benchmark": k[0],
            "ER_keV": k[1],
            "halo_model": k[2],
            "open_isotopes_NIST_baseline": totals[k]["open_isotopes"],
            "open_abundance_fraction_NIST_baseline": float(
                totals[k]["open_abundance_fraction"]
            ),
            "natural_xenon_rate_NIST_baseline": base_total,
            "Xe131_rate_NIST_baseline": nist_compact,
            "Xe131_rate_AME2020_exact_spatial": ame_rate,
            "Xe131_fraction_of_NIST_total": xe131_fraction,
            "Xe131_partial_rate_shift_AME2020_vs_NIST": xe131_rate_shift,
            "hybrid_total_Xe131_only_AME2020": hybrid_total,
            "hybrid_total_relative_shift": hybrid_shift,
            "NIST_partial_reproduction_relative_difference": rel_check,
            "mass_scheme_scope": "Xe-131=AME2020; other six AFH isotopes=NIST",
        })

    metadata = {
        "calculation": "Xe-131-only AME2020 replacement in the NIST natural-xenon baseline",
        "scope": "hybrid diagnostic only; not a full AME2020 natural-xenon prediction",
        "baseline": "mainline exact-spatial-q natural-xenon selected-point fold",
        "baseline_mass_scheme": "NIST nuclear masses for all seven AFH-default isotopes",
        "replacement": "Xe-131 term recomputed with unrounded AME2020 atomic mass and CODATA-2022 constants",
        "response_q_convention": "exact_spatial for both baseline and replacement",
        "other_isotope_terms": "Xe-128, Xe-129, Xe-130, Xe-132, Xe-134, Xe-136 remain at NIST baseline",
        "Xe124_Xe126": "omitted in the AFH default-density baseline",
        "number_of_selected_point_rows": len(rows),
        "max_NIST_partial_reproduction_relative_difference": max_baseline_difference,
        "NIST_baseline_consistency_tolerance": max_nist_baseline_relative_difference,
        "rate_units": "events/(kg day keV)",
        "detector_response": "not applied",
    }
    return rows, metadata


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows to write: {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    study_dir = Path(__file__).resolve().parents[1]
    repo_root = study_dir.parents[1]
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--baseline-isotope-contributions",
        type=Path,
        default=repo_root / "research/afh_default_density_natural_xenon_halo/results/isotope_halo_contributions_compact.csv",
    )
    ap.add_argument(
        "--baseline-total-rates",
        type=Path,
        default=repo_root / "research/afh_default_density_natural_xenon_halo/results/natural_xenon_halo_rates.csv",
    )
    ap.add_argument("--xe131-partial-rates", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows, metadata = build_hybrid_rows(
        read_csv(args.baseline_isotope_contributions),
        read_csv(args.baseline_total_rates),
        read_csv(args.xe131_partial_rates),
    )
    write_csv(args.out_dir / "xe131_only_ame2020_hybrid_natural_xenon.csv", rows)
    metadata.update({
        "baseline_isotope_contributions_file": str(args.baseline_isotope_contributions),
        "baseline_isotope_contributions_sha256": sha256(args.baseline_isotope_contributions),
        "baseline_total_rates_file": str(args.baseline_total_rates),
        "baseline_total_rates_sha256": sha256(args.baseline_total_rates),
        "xe131_partial_rates_file": str(args.xe131_partial_rates),
        "xe131_partial_rates_sha256": sha256(args.xe131_partial_rates),
    })
    (args.out_dir / "xe131_only_ame2020_hybrid_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Hybrid selected-point rows: {len(rows)}")
    print(
        "Max NIST partial reproduction difference: "
        f"{metadata['max_NIST_partial_reproduction_relative_difference']:.3e}"
    )
    max_total_shift = max(
        abs(r["hybrid_total_relative_shift"])
        for r in rows if r["hybrid_total_relative_shift"] is not None
    )
    print(f"Max absolute Xe-131-only total shift: {max_total_shift:.3e}")


if __name__ == "__main__":
    main()
