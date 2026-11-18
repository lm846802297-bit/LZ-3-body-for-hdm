#!/usr/bin/env python3
"""Contract provisional AFH isotope responses with integrated 3-body coefficients.

This is a fixed-speed benchmark contraction, not a halo-folded event rate.
The AFH database input must carry physical equal-p/n response columns.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

RESPONSE_COLUMNS = {
    "M": "R_M_physical_equal_pn",
    "PhiPP": "R_PhiPP_physical_equal_pn",
    "MPhiPP": "R_MPhiPP_physical_equal_pn",
    "Delta": "R_Delta_physical_equal_pn",
    "SigmaPrime": "R_SigmaPrime_physical_equal_pn",
    "SigmaPrimeDelta": "R_SigmaPrimeDelta_physical_equal_pn",
}
REQUIRED_METADATA_ISOTOPES = (128, 129, 130, 131, 132, 134, 136)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_afh_archive(afh_dir: Path) -> dict:
    metadata_path = afh_dir / "metadata.json"
    validation_path = afh_dir / "validation.json"
    csv_path = afh_dir / "afh_v6_full_eight_response_7isotope.csv"
    sums_path = afh_dir / "SHA256SUMS.txt"
    for path in (metadata_path, validation_path, csv_path, sums_path):
        if not path.is_file():
            raise FileNotFoundError(f"required AFH artifact file is missing: {path}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if metadata.get("status") != "PROVISIONAL_PYTHON":
        raise ValueError(f"unexpected AFH metadata status: {metadata.get('status')}")
    if metadata.get("native_afh_validated") is not False:
        raise ValueError("this workflow expects the provisional Python AFH archive")
    if validation.get("status") != "PASS" or validation.get("native_afh_validated") is not False:
        raise ValueError("AFH Python internal validation is not a clean provisional PASS")
    if tuple(metadata.get("isotopes", ())) != REQUIRED_METADATA_ISOTOPES:
        raise ValueError("AFH isotope list does not match the seven-isotope contract")
    normalization = metadata.get("normalization", {})
    if normalization.get("factor_four_applied_once_to_physical_columns") is not True:
        raise ValueError("AFH physical equal-p/n factor-four provenance is missing")

    sums = {}
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2:
            sums[parts[1]] = parts[0].lower()
    expected = sums.get(csv_path.name)
    actual = sha256_file(csv_path)
    if expected is None or expected != actual:
        raise ValueError(
            f"AFH CSV SHA-256 mismatch: expected {expected}, actual {actual}"
        )
    return {
        "metadata": metadata,
        "validation": validation,
        "csv_path": csv_path,
        "csv_sha256": actual,
        "source_commit": (afh_dir / "source_commit.txt").read_text(
            encoding="utf-8"
        ).strip() if (afh_dir / "source_commit.txt").is_file() else None,
    }


def index_afh_rows(rows: list[dict], *, expected_points: int = 2401) -> dict[int, dict]:
    grouped: dict[int, list[dict]] = {}
    for row in rows:
        A = int(float(row["A"]))
        q = float(row["q_GeV"])
        for column in RESPONSE_COLUMNS.values():
            if column not in row:
                raise ValueError(f"AFH CSV is missing required physical column {column}")
            value = float(row[column])
            if not np.isfinite(value):
                raise ValueError(f"non-finite AFH response {column} at A={A}, q={q}")
        grouped.setdefault(A, []).append(row)

    if tuple(sorted(grouped)) != REQUIRED_METADATA_ISOTOPES:
        raise ValueError(
            f"AFH CSV isotope set {tuple(sorted(grouped))} does not match expected "
            f"{REQUIRED_METADATA_ISOTOPES}"
        )
    result = {}
    for A, entries in grouped.items():
        entries = sorted(entries, key=lambda item: float(item["q_GeV"]))
        q = np.asarray([float(item["q_GeV"]) for item in entries])
        if len(q) != expected_points or not np.all(np.diff(q) > 0):
            raise ValueError(f"Xe-{A}: AFH q grid is incomplete or not strictly increasing")
        if not np.isclose(q[0], 0.0, atol=1e-12) or not np.isclose(q[-1], 0.6, atol=1e-12):
            raise ValueError(f"Xe-{A}: AFH q grid does not cover [0, 0.6] GeV")
        result[A] = {
            "q": q,
            "J_A": float(entries[0]["J_A"]),
            "responses": {
                name: np.asarray([float(item[column]) for item in entries])
                for name, column in RESPONSE_COLUMNS.items()
            },
        }
    return result


def contract_archive(
    afh_rows: list[dict],
    weights_archive: dict,
    afh_metadata: dict,
    *,
    expected_points: int = 2401,
    q_tolerance_GeV: float = 1e-10,
    positivity_relative_tolerance: float = 1e-10,
) -> dict:
    isotope_data = index_afh_rows(afh_rows, expected_points=expected_points)
    if weights_archive.get("status") != "PASS_AFH_LEPTONIC_COEFFICIENT_EXTRACTION":
        raise ValueError("input three-body coefficient archive has not passed extraction")

    results = []
    failures = []
    for benchmark in weights_archive.get("benchmarks", []):
        coefficients = benchmark["afh_vector_coefficients"]
        qA = float(coefficients["qA_GeV"])
        for A, isotope in isotope_data.items():
            qgrid = isotope["q"]
            if qA < qgrid[0] - q_tolerance_GeV or qA > qgrid[-1] + q_tolerance_GeV:
                raise ValueError(f"q_A={qA} GeV is outside Xe-{A} AFH grid")
            responses = {
                name: float(np.interp(qA, qgrid, values))
                for name, values in isotope["responses"].items()
            }
            terms = {
                "M": float(coefficients["C_M"] * responses["M"]),
                "PhiPP": float(coefficients["C_PhiPP"] * responses["PhiPP"]),
                "MPhiPP": float(coefficients["C_MPhiPP"] * responses["MPhiPP"]),
                "Delta": float(coefficients["C_Delta"] * responses["Delta"]),
                "SigmaPrime": float(
                    coefficients["C_SigmaPrime"] * responses["SigmaPrime"]
                ),
                "SigmaPrimeDelta": float(
                    coefficients["C_SigmaPrimeDelta"]
                    * responses["SigmaPrimeDelta"]
                ),
            }
            charge = terms["M"] + terms["PhiPP"] + terms["MPhiPP"]
            spatial = terms["Delta"] + terms["SigmaPrime"] + terms["SigmaPrimeDelta"]
            total = charge + spatial
            scale = max(abs(charge), 1.0)
            positive = total >= -positivity_relative_tolerance * scale
            if not positive:
                failures.append(
                    f"{benchmark.get('benchmark')} {benchmark.get('width_scheme')} "
                    f"Xe-{A}: negative total response kernel {total:.12g}"
                )
            if responses["Delta"] < -1e-12 or responses["SigmaPrime"] < -1e-12:
                failures.append(f"Xe-{A}: negative diagonal AFH spatial response")
            cauchy_excess = (
                responses["SigmaPrimeDelta"] ** 2
                - max(0.0, responses["SigmaPrime"])
                * max(0.0, responses["Delta"])
            )
            cauchy_scale = max(
                responses["SigmaPrimeDelta"] ** 2,
                abs(responses["SigmaPrime"] * responses["Delta"]),
                1e-300,
            )
            if cauchy_excess > 1e-10 * cauchy_scale:
                failures.append(
                    f"Xe-{A}: interpolated SigmaPrime-Delta Cauchy bound violated"
                )
            results.append({
                "benchmark": benchmark.get("benchmark"),
                "width_scheme": benchmark.get("width_scheme"),
                "g2": benchmark.get("g2"),
                "ER_keV": benchmark.get("ER_keV"),
                "speed_kms": benchmark.get("speed_kms"),
                "A": A,
                "J_A": isotope["J_A"],
                "qA_GeV": qA,
                "interpolation": "linear in q_A on 0.25 MeV AFH grid",
                "responses_physical_equal_pn": responses,
                "coefficient_response_terms": terms,
                "charge_sector": float(charge),
                "spatial_sector": float(spatial),
                "total_response_kernel": float(total),
                "spatial_over_charge": float(spatial / charge) if charge else 0.0,
                "positive_total_kernel": bool(positive),
                "SigmaPrimeDelta_Cauchy_excess": float(cauchy_excess),
            })

    spatial_ratios = [
        abs(row["spatial_over_charge"]) for row in results
        if np.isfinite(row["spatial_over_charge"])
    ]
    return {
        "status": "PROVISIONAL_AFH_CONTRACTION_PASS" if not failures else "FAIL",
        "scope": (
            "fixed-speed benchmark contraction of leading static three-body "
            "particle coefficients with provisional Python AFH physical "
            "equal-p/n responses; no halo fold or detector response"
        ),
        "afh_source": {
            "status": afh_metadata["status"],
            "native_afh_validated": afh_metadata["native_afh_validated"],
            "source": afh_metadata["source"],
            "source_commit": afh_metadata.get("afh_source_commit"),
            "csv_sha256": afh_metadata.get("csv_sha256"),
            "isotopes": list(REQUIRED_METADATA_ISOTOPES),
            "natural_atom_fraction_coverage": afh_metadata.get(
                "natural_atom_fraction_coverage"
            ),
            "normalization": afh_metadata.get("normalization"),
        },
        "response_columns": "physical equal-p/n columns; factor four applied once in AFH database",
        "form_factor_status": weights_archive.get("form_factor_input", {}).get("status"),
        "benchmarks": results,
        "summary": {
            "benchmark_count": len(weights_archive.get("benchmarks", [])),
            "isotope_count": len(isotope_data),
            "contracted_rows": len(results),
            "positive_total_kernel_rows": sum(
                1 for row in results if row["positive_total_kernel"]
            ),
            "min_abs_spatial_over_charge": min(spatial_ratios) if spatial_ratios else 0.0,
            "max_abs_spatial_over_charge": max(spatial_ratios) if spatial_ratios else 0.0,
            "failures": failures,
        },
        "limitations": [
            "The AFH eight-response database is a provisional Python translation and is not native-Wolfram validated.",
            "F1 and F2 are constant q=0 anchors in this benchmark; finite-t_N form factors are not included.",
            "The calculation uses fixed-speed points and linear interpolation in q_A; it is not a recoil-grid or halo integration.",
            "No mediator propagator, detector efficiency, resolution, or likelihood is included.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--afh-dir", type=Path, required=True)
    parser.add_argument("--weights-json", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    verified = verify_afh_archive(args.afh_dir)
    with verified["csv_path"].open(newline="", encoding="utf-8-sig") as stream:
        afh_rows = list(csv.DictReader(stream))
    weights_archive = json.loads(args.weights_json.read_text(encoding="utf-8"))
    metadata = dict(verified["metadata"])
    metadata["csv_sha256"] = verified["csv_sha256"]
    metadata["afh_source_commit"] = verified["source_commit"]
    result = contract_archive(afh_rows, weights_archive, metadata)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "summary": result["summary"]}, indent=2))
    if result["status"] != "PROVISIONAL_AFH_CONTRACTION_PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
