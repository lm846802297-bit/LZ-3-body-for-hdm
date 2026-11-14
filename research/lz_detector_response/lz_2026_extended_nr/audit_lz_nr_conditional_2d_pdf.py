#!/usr/bin/env python3
"""Structural audit of the archived LZ NR conditional 2D response PDF.

This tool validates the compact response artifact and reports what it cannot
establish.  It deliberately does not turn conditional PDFs into a post-selection
signal model or a likelihood.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


EXPECTED_NEST_COMMIT = "541b6430dae6ea289cf110c99f174a9187f7fdee"
EXPECTED_FAMILIES = ("generic", "ws2024", "eft2024", "tableS5")
EXPECTED_BINNING = {
    "energy_keV": 10.0,
    "S1c_phd": 10.0,
    "log10S2c_dex": 0.02,
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def audit_object(obj: dict[str, Any], source_sha256: str | None = None) -> dict[str, Any]:
    required_top = {
        "study", "nest_commit", "energy_prior", "spatial_prior", "binning",
        "note", "families",
    }
    missing = required_top - set(obj)
    if missing:
        raise ValueError(f"missing top-level fields: {sorted(missing)}")
    if obj["nest_commit"] != EXPECTED_NEST_COMMIT:
        raise ValueError(
            f"unexpected NEST commit {obj['nest_commit']}; expected {EXPECTED_NEST_COMMIT}"
        )
    for key, expected in EXPECTED_BINNING.items():
        if not math.isclose(float(obj["binning"][key]), expected, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(f"unexpected binning {key}: {obj['binning'][key]}")

    families = obj["families"]
    if set(families) != set(EXPECTED_FAMILIES):
        raise ValueError(
            f"unexpected NEST family set: {sorted(families)}; expected {list(EXPECTED_FAMILIES)}"
        )

    family_reports: dict[str, Any] = {}
    for family_name in EXPECTED_FAMILIES:
        family = families[family_name]
        if "n_generated" not in family or "energy_bins" not in family:
            raise ValueError(f"{family_name}: missing n_generated or energy_bins")
        n_generated = int(family["n_generated"])
        bins = family["energy_bins"]
        if n_generated <= 0 or not bins:
            raise ValueError(f"{family_name}: invalid generation count or empty energy bins")

        previous_high = None
        valid_total = 0
        max_probability_sum_residual = 0.0
        per_bin = []
        for index, energy_bin in enumerate(bins):
            lo = float(energy_bin["energy_low_keV"])
            hi = float(energy_bin["energy_high_keV"])
            n_valid = int(energy_bin["n_valid"])
            if not (math.isfinite(lo) and math.isfinite(hi) and lo < hi and n_valid >= 0):
                raise ValueError(f"{family_name} bin {index}: invalid energy bounds or n_valid")
            if previous_high is not None and not math.isclose(
                lo, previous_high, rel_tol=0.0, abs_tol=1e-10
            ):
                raise ValueError(f"{family_name}: energy bins are not contiguous at {lo} keV")
            if not math.isclose(hi - lo, EXPECTED_BINNING["energy_keV"], rel_tol=0.0, abs_tol=1e-9):
                raise ValueError(f"{family_name} bin {index}: expected 10-keV bin width")
            previous_high = hi
            valid_total += n_valid

            points = energy_bin.get("pdf_sparse")
            if not isinstance(points, list):
                raise ValueError(f"{family_name} bin {index}: pdf_sparse must be a list")
            probability_sum = 0.0
            for point in points:
                if not isinstance(point, list) or len(point) != 3:
                    raise ValueError(f"{family_name} bin {index}: malformed sparse PDF point")
                s1c, log10_s2c, probability = map(float, point)
                if not all(math.isfinite(x) for x in (s1c, log10_s2c, probability)):
                    raise ValueError(f"{family_name} bin {index}: non-finite sparse PDF point")
                if probability < 0.0:
                    raise ValueError(f"{family_name} bin {index}: negative probability")
                probability_sum += probability
            if n_valid > 0 and not points:
                raise ValueError(f"{family_name} bin {index}: valid events but empty PDF")
            if n_valid > 0:
                residual = abs(probability_sum - 1.0)
                max_probability_sum_residual = max(max_probability_sum_residual, residual)
                if residual > 1e-8:
                    raise ValueError(
                        f"{family_name} bin {index}: sparse PDF sums to {probability_sum}, not 1"
                    )
            elif points:
                raise ValueError(f"{family_name} bin {index}: empty bin must not have PDF points")

            per_bin.append({
                "energy_low_keV": lo,
                "energy_high_keV": hi,
                "n_valid": n_valid,
                "n_sparse_points": len(points),
                "conditional_pdf_probability_sum": probability_sum,
            })

        if valid_total > n_generated:
            raise ValueError(f"{family_name}: sum of per-bin n_valid exceeds n_generated")
        global_positive_fraction = valid_total / n_generated
        family_reports[family_name] = {
            "n_generated_global": n_generated,
            "n_valid_sum_over_energy_bins": valid_total,
            "not_in_positive_observable_pdf_global": n_generated - valid_total,
            "global_positive_observable_fraction": global_positive_fraction,
            "global_positive_observable_fraction_percent": 100.0 * global_positive_fraction,
            "energy_bin_count": len(bins),
            "energy_range_keV": [per_bin[0]["energy_low_keV"], per_bin[-1]["energy_high_keV"]],
            "per_bin_generated_count_present": all(
                "n_generated" in energy_bin for energy_bin in bins
            ),
            "separate_s1_coincidence_count_present": all(
                "n_s1_coincidence_pass" in energy_bin for energy_bin in bins
            ),
            "raw_s2_and_s2c_both_present": False,
            "max_conditional_pdf_normalization_residual": max_probability_sum_residual,
            "per_bin": per_bin,
        }

    note = str(obj["note"])
    return {
        "audit_status": "STRUCTURE_VALIDATED",
        "selection_status": "PRE_SELECTION_ONLY",
        "study": obj["study"],
        "nest_commit": obj["nest_commit"],
        "energy_prior": obj["energy_prior"],
        "spatial_prior": obj["spatial_prior"],
        "binning": obj["binning"],
        "source_sha256": source_sha256,
        "families": family_reports,
        "missing_information": {
            "event_level_s1_coincidence_flag": True,
            "per_energy_bin_generated_denominator": True,
            "raw_S2_phd_for_S2_gt_645_phd_cut": True,
            "true_and_reconstructed_position_for_fiducial_volume": True,
            "S1_and_S2_pulse_multiplicity_for_single_scatter_selection": True,
            "trigger_and_data_quality_cut_flags": True,
            "Skin_and_OD_veto_tags": True,
            "note_from_source_artifact": note,
        },
        "interpretation": [
            "Each stored 2D histogram is conditional on positive reconstructed S1c and S2c; its sparse probabilities are normalized within that conditional sample.",
            "n_generated is stored only once per family, while n_valid is stored per energy bin. Therefore the energy-dependent positive-observable acceptance cannot be reconstructed exactly.",
            "The global n_valid sum divided by n_generated is only a global positive-observable fraction; it is not the S1 coincidence efficiency or the final LZ selection efficiency.",
            "Do not multiply this global fraction by the published LZ final-ROI efficiency: that would risk double counting and would not restore the missing energy dependence.",
            "The archived PDF is a pre-selection response-shape artifact, not an official post-selection PDF.",
        ],
        "likelihood_allowed": False,
    }


def audit_file(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    return audit_object(obj, sha256_file(path))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()
    report = audit_file(args.input_json)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["audit_status"] != "STRUCTURE_VALIDATED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
