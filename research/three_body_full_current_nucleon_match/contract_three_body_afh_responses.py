#!/usr/bin/env python3
"""Contract the three-body coefficients with charge and P3-B spatial AFH data.

The charge responses are read from the AFH-8 Python archive and multiplied
by the common OBDME correction C0 from P3-B. The spatial responses and their
rank-resolved multipoles are read from the P3-B artifact, which already
contains C0. The equal-p/n factor four is applied exactly once in both
archives. This is a fixed-speed benchmark contraction, not a halo rate.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

REQUIRED_METADATA_ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
J_BY_A = {128: 0.0, 129: 0.5, 130: 0.0, 131: 1.5, 132: 0.0, 134: 0.0, 136: 0.0}
SPIN_ZERO = {128, 130, 132, 134, 136}
EXPECTED_AFH_SOURCE_COMMIT = "dcefbeb7ad705b6c03f2b4689200eb1d9252e67b"
EXPECTED_AFH_CSV_SHA256 = "59ea25093137a05b8ebcc158e2fe6a74fe5927599dbb16766b067aa1ad8e3caa"
EXPECTED_AFH_SOURCE_SHA256 = "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372"
EXPECTED_SPATIAL_RESPONSE_SHA256 = "4e0a23c18d29df3af04a2531e75b7bffeaa3251d0efe97674b2287cf3c25e7e3"
EXPECTED_SPATIAL_MULTIPOLE_SHA256 = "e83f7499cd0af4ec8f1974238f09daf4899ca1b87205ec837ae0964a2e8532c6"

CHARGE_RESPONSE_COLUMNS = {
    "M": "R_M_physical_equal_pn",
    "PhiPP": "R_PhiPP_physical_equal_pn",
    "MPhiPP": "R_MPhiPP_physical_equal_pn",
}
SPATIAL_RESPONSE_COLUMNS = {
    "Delta": "R_Delta_equal_pn",
    "SigmaPrime": "R_SigmaPrime_equal_pn",
    "SigmaPrimeDelta": "R_SigmaPrimeDelta_equal_pn",
}
SPATIAL_MULTIPOLE_COLUMNS = {
    "Delta": "R_Delta_J_equal_pn",
    "SigmaPrime": "R_SigmaPrime_J_equal_pn",
    "SigmaPrimeDelta": "R_SigmaPrimeDelta_J_equal_pn",
}
ATOL = 2e-14
RTOL = 2e-12


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def _q_key(row: dict) -> tuple[int, float]:
    return int(float(row["A"])), round(float(row["q_GeV"]), 10)


def _close(a: float, b: float) -> bool:
    return abs(a - b) <= ATOL + RTOL * max(abs(a), abs(b))


def verify_afh_archive(afh_dir: Path) -> dict:
    metadata_path = afh_dir / "metadata.json"
    validation_path = afh_dir / "validation.json"
    csv_path = afh_dir / "afh_v6_full_eight_response_7isotope.csv"
    sums_path = afh_dir / "SHA256SUMS.txt"
    for path in (metadata_path, validation_path, csv_path, sums_path):
        if not path.is_file():
            raise FileNotFoundError(f"required AFH artifact file is missing: {path}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    validation = json.loads(validation_path.read_text(encoding="utf-8-sig"))
    if metadata.get("status") != "PROVISIONAL_PYTHON":
        raise ValueError(f"unexpected AFH metadata status: {metadata.get('status')}")
    if metadata.get("native_afh_validated") is not False:
        raise ValueError("expected the provisional Python AFH-8 archive")
    if validation.get("status") != "PASS" or validation.get("native_afh_validated") is not False:
        raise ValueError("AFH-8 Python internal validation is not a clean provisional PASS")
    if tuple(metadata.get("isotopes", ())) != REQUIRED_METADATA_ISOTOPES:
        raise ValueError("AFH isotope list does not match the seven-isotope contract")
    if metadata.get("normalization", {}).get("factor_four_applied_once_to_physical_columns") is not True:
        raise ValueError("AFH physical equal-p/n factor-four provenance is missing")

    sums = {}
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2:
            sums[parts[1]] = parts[0].lower()
    expected = sums.get(csv_path.name)
    actual = sha256_file(csv_path)
    if expected is None or expected != actual or actual != EXPECTED_AFH_CSV_SHA256:
        raise ValueError(f"AFH-8 CSV SHA-256 mismatch: expected reviewed {EXPECTED_AFH_CSV_SHA256}, got {actual}")
    source_commit_path = afh_dir / "source_commit.txt"
    source_commit = source_commit_path.read_text(encoding="utf-8").strip()
    if source_commit != EXPECTED_AFH_SOURCE_COMMIT:
        raise ValueError(f"AFH source commit mismatch: {source_commit}")
    return {
        "metadata": metadata,
        "validation": validation,
        "csv_path": csv_path,
        "csv_sha256": actual,
        "source_commit": source_commit,
    }


def verify_spatial_archive(spatial_dir: Path) -> dict:
    metadata_path = spatial_dir / "metadata.json"
    validation_path = spatial_dir / "multipole-validation.json"
    if not metadata_path.is_file() or not validation_path.is_file():
        raise FileNotFoundError("P3-B metadata or multipole-validation.json is missing")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    validation = json.loads(validation_path.read_text(encoding="utf-8-sig"))
    if metadata.get("status") != "PROVISIONAL_SOURCE_TRANSLATED_AFH_SPATIAL_RESPONSES":
        raise ValueError(f"unexpected P3-B status: {metadata.get('status')}")
    if metadata.get("source_file_sha256") != EXPECTED_AFH_SOURCE_SHA256:
        raise ValueError("P3-B AFH source SHA-256 does not match the pinned v6.0 source")
    if metadata.get("native_mathematica_spatial_crosscheck") is not False:
        raise ValueError("P3-B metadata must remain explicitly provisional")
    if metadata.get("rankwise_amplitudes_and_signed_interference_saved") is not True:
        raise ValueError("P3-B rank-resolved multipole archive is not marked complete")
    if tuple(metadata.get("isotopes", ())) != REQUIRED_METADATA_ISOTOPES:
        raise ValueError("P3-B isotope list does not match the seven-isotope contract")
    if int(metadata.get("response_rows", -1)) != 16807:
        raise ValueError("P3-B response row count is not 16,807")
    if validation.get("status") != "PASS_AFH_SPATIAL_MULTIPOLE_ARCHIVE":
        raise ValueError("P3-B rank-resolved archive validation has not passed")
    if validation.get("native_afh_validated") is not False:
        raise ValueError("P3-B archive must not claim native AFH validation")

    response_path = spatial_dir / metadata.get("response_file", "")
    multipole_path = spatial_dir / metadata.get("multipole_file", "")
    for path in (response_path, multipole_path):
        if not path.is_file():
            raise FileNotFoundError(f"P3-B archive file is missing: {path}")
    response_sha = sha256_file(response_path)
    multipole_sha = sha256_file(multipole_path)
    if response_sha != metadata.get("response_file_sha256") or response_sha != EXPECTED_SPATIAL_RESPONSE_SHA256:
        raise ValueError(f"P3-B response CSV SHA-256 mismatch: {response_sha}")
    if multipole_sha != metadata.get("multipole_file_sha256") or multipole_sha != EXPECTED_SPATIAL_MULTIPOLE_SHA256:
        raise ValueError(f"P3-B multipole CSV SHA-256 mismatch: {multipole_sha}")
    return {
        "metadata": metadata,
        "validation": validation,
        "response_path": response_path,
        "multipole_path": multipole_path,
        "response_sha256": response_sha,
        "multipole_sha256": multipole_sha,
    }


def index_afh_rows(rows: list[dict], *, expected_points: int = 2401) -> dict[int, dict]:
    grouped: dict[int, list[dict]] = {}
    for row in rows:
        A, q = _q_key(row)
        for column in CHARGE_RESPONSE_COLUMNS.values():
            if column not in row:
                raise ValueError(f"AFH-8 CSV is missing charge response column {column}")
            value = float(row[column])
            if not np.isfinite(value):
                raise ValueError(f"non-finite AFH charge response {column} at A={A}, q={q}")
        grouped.setdefault(A, []).append(row)

    if tuple(sorted(grouped)) != REQUIRED_METADATA_ISOTOPES:
        raise ValueError(f"AFH-8 isotope set {tuple(sorted(grouped))} does not match expected {REQUIRED_METADATA_ISOTOPES}")
    result = {}
    for A, entries in grouped.items():
        entries = sorted(entries, key=lambda item: float(item["q_GeV"]))
        q = np.asarray([float(item["q_GeV"]) for item in entries])
        if len(q) != expected_points or not np.all(np.diff(q) > 0):
            raise ValueError(f"Xe-{A}: AFH-8 q grid is incomplete or not strictly increasing")
        if expected_points == 2401:
            expected_q = np.arange(expected_points, dtype=float) * 0.00025
            if not np.allclose(q, expected_q, rtol=0.0, atol=1e-10):
                raise ValueError(f"Xe-{A}: AFH-8 q grid does not match the canonical 0.25 MeV grid")
        elif not np.isclose(q[0], 0.0, atol=1e-12) or not np.isclose(q[-1], 0.6, atol=1e-12):
            raise ValueError(f"Xe-{A}: synthetic AFH-8 q grid must span [0, 0.6] GeV")
        result[A] = {
            "q": q,
            "J_A": float(entries[0]["J_A"]),
            "responses": {
                name: np.asarray([float(item[column]) for item in entries])
                for name, column in CHARGE_RESPONSE_COLUMNS.items()
            },
        }
    return result


def index_spatial_archive(
    response_rows: list[dict],
    multipole_rows: list[dict],
    metadata: dict,
    *,
    expected_points: int = 2401,
) -> dict[int, dict]:
    isotope_meta = {int(item["A"]): item for item in metadata.get("isotope_metadata", [])}
    if set(isotope_meta) != set(REQUIRED_METADATA_ISOTOPES):
        raise ValueError("P3-B isotope_metadata is incomplete")
    ranks_by_A = {
        int(A): tuple(int(J) for J in ranks)
        for A, ranks in metadata.get("multipole_ranks_by_isotope", {}).items()
    }
    if set(ranks_by_A) != set(REQUIRED_METADATA_ISOTOPES):
        raise ValueError("P3-B multipole rank map is incomplete")

    grouped: dict[int, list[dict]] = {}
    c0_by_A = {}
    for row in response_rows:
        A, q = _q_key(row)
        if A not in J_BY_A or float(row["J_A"]) != J_BY_A[A]:
            raise ValueError(f"unexpected nuclear spin for Xe-{A} at q={q}")
        for column in SPATIAL_RESPONSE_COLUMNS.values():
            if column not in row or not np.isfinite(float(row[column])):
                raise ValueError(f"missing/non-finite P3-B spatial response {column} at {(A, q)}")
        c0 = float(row["common_matrix_normalization"])
        if not np.isfinite(c0) or not 0.999 <= c0 <= 1.001:
            raise ValueError(f"invalid common OBDME normalization C0={c0} for Xe-{A}")
        if A in c0_by_A and not np.isclose(c0_by_A[A], c0, rtol=0.0, atol=2e-14):
            raise ValueError(f"C0 varies across q for Xe-{A}")
        c0_by_A[A] = c0
        grouped.setdefault(A, []).append(row)

    result = {}
    for A, entries in grouped.items():
        entries = sorted(entries, key=lambda item: float(item["q_GeV"]))
        q = np.asarray([float(item["q_GeV"]) for item in entries])
        if len(q) != expected_points or not np.all(np.diff(q) > 0):
            raise ValueError(f"Xe-{A}: P3-B response q grid is incomplete")
        if expected_points == 2401:
            expected_q = np.arange(expected_points, dtype=float) * 0.00025
            if not np.allclose(q, expected_q, rtol=0.0, atol=1e-10):
                raise ValueError(f"Xe-{A}: P3-B response q grid does not match the canonical 0.25 MeV grid")
        elif not np.isclose(q[0], 0.0, atol=1e-12) or not np.isclose(q[-1], 0.6, atol=1e-12):
            raise ValueError(f"Xe-{A}: synthetic P3-B q grid must span [0, 0.6] GeV")
        recorded_c0 = float(isotope_meta[A].get("common_matrix_normalization", float("nan")))
        if not np.isclose(recorded_c0, c0_by_A[A], rtol=0.0, atol=2e-14):
            raise ValueError(f"metadata/CSV C0 mismatch for Xe-{A}")
        if float(isotope_meta[A].get("J_A", float("nan"))) != J_BY_A[A]:
            raise ValueError(f"metadata nuclear spin mismatch for Xe-{A}")
        if A in SPIN_ZERO and ranks_by_A[A]:
            raise ValueError(f"spin-zero Xe-{A} unexpectedly has spatial multipole ranks")
        result[A] = {
            "q": q,
            "J_A": J_BY_A[A],
            "C0": c0_by_A[A],
            "responses": {
                name: np.asarray([float(item[column]) for item in entries])
                for name, column in SPATIAL_RESPONSE_COLUMNS.items()
            },
            "multipole_ranks": {},
        }

    grouped_multipoles: dict[tuple[int, int], list[dict]] = {}
    for row in multipole_rows:
        A, q = _q_key(row)
        J = int(float(row["multipole_J"]))
        if A not in result or J not in ranks_by_A[A]:
            raise ValueError(f"unexpected P3-B multipole row {(A, q, J)}")
        grouped_multipoles.setdefault((A, J), []).append(row)

    for A in REQUIRED_METADATA_ISOTOPES:
        for J in ranks_by_A[A]:
            entries = sorted(grouped_multipoles.get((A, J), []), key=lambda item: float(item["q_GeV"]))
            q = np.asarray([float(item["q_GeV"]) for item in entries])
            expected_q = result[A]["q"]
            if len(q) != expected_points or not np.all(np.diff(q) > 0):
                raise ValueError(f"Xe-{A}, J={J}: incomplete rank-resolved multipole q grid")
            if not np.allclose(q, expected_q, rtol=0.0, atol=1e-10):
                raise ValueError(f"Xe-{A}, J={J}: multipole q grid is not aligned with total-response grid")
            for row in entries:
                if float(row["J_A"]) != J_BY_A[A]:
                    raise ValueError(f"Xe-{A}, J={J}: multipole nuclear spin mismatch")
                if not np.isclose(
                    float(row["common_matrix_normalization"]), c0_by_A[A],
                    rtol=0.0, atol=2e-14
                ):
                    raise ValueError(f"Xe-{A}, J={J}: multipole C0 mismatch")
            result[A]["multipole_ranks"][J] = {
                "q": q,
                "responses": {
                    name: np.asarray([float(item[column]) for item in entries])
                    for name, column in SPATIAL_MULTIPOLE_COLUMNS.items()
                },
            }

    expected_multipole_count = expected_points * sum(len(ranks_by_A[A]) for A in REQUIRED_METADATA_ISOTOPES)
    if len(multipole_rows) != expected_multipole_count or int(metadata.get("multipole_rows", -1)) != expected_multipole_count:
        raise ValueError("P3-B multipole row count does not match the isotope/rank map")

    # Reconstruct every spatial response from the retained rankwise rows.
    for A, isotope in result.items():
        for index, q in enumerate(isotope["q"]):
            for name in SPATIAL_RESPONSE_COLUMNS:
                rank_sum = sum(
                    float(rank["responses"][name][index])
                    for rank in isotope["multipole_ranks"].values()
                )
                total = float(isotope["responses"][name][index])
                if not _close(rank_sum, total):
                    raise ValueError(f"rankwise {name} does not reconstruct Xe-{A}, q={q}")
    return result


def contract_archive(
    afh_rows: list[dict],
    weights_archive: dict,
    afh_metadata: dict,
    spatial_rows: list[dict],
    spatial_multipole_rows: list[dict],
    spatial_metadata: dict,
    *,
    expected_points: int = 2401,
    q_tolerance_GeV: float = 1e-10,
    positivity_relative_tolerance: float = 1e-10,
    afh_artifact_run_id: int | None = None,
    afh_artifact_id: int | None = None,
    spatial_artifact_run_id: int | None = None,
    spatial_artifact_id: int | None = None,
) -> dict:
    charge_data = index_afh_rows(afh_rows, expected_points=expected_points)
    spatial_data = index_spatial_archive(
        spatial_rows, spatial_multipole_rows, spatial_metadata,
        expected_points=expected_points,
    )
    if set(charge_data) != set(spatial_data):
        raise ValueError("AFH-8 charge and P3-B spatial isotope sets differ")
    if weights_archive.get("status") != "PASS_AFH_LEPTONIC_COEFFICIENT_EXTRACTION":
        raise ValueError("input three-body coefficient archive has not passed extraction")
    if afh_metadata.get("afh_source_commit") != EXPECTED_AFH_SOURCE_COMMIT:
        raise ValueError("AFH-8 source commit does not match the reviewed source")
    if spatial_metadata.get("source_file_sha256") != EXPECTED_AFH_SOURCE_SHA256:
        raise ValueError("P3-B AFH source hash does not match AFH-8 source")

    results = []
    failures = []
    for benchmark in weights_archive.get("benchmarks", []):
        coefficients = benchmark["afh_vector_coefficients"]
        qA = float(coefficients["qA_GeV"])
        for A, isotope in charge_data.items():
            spatial_isotope = spatial_data[A]
            qgrid = isotope["q"]
            if qA < qgrid[0] - q_tolerance_GeV or qA > qgrid[-1] + q_tolerance_GeV:
                raise ValueError(f"q_A={qA} GeV is outside Xe-{A} AFH grid")

            # The P3-B C0 is a common OBDME normalization. Apply it to the
            # AFH-8 charge responses; P3-B spatial responses already include it.
            c0 = float(spatial_isotope["C0"])
            responses = {
                name: float(c0 * np.interp(qA, qgrid, values))
                for name, values in isotope["responses"].items()
            }
            spatial_q = spatial_isotope["q"]
            for name, values in spatial_isotope["responses"].items():
                responses[name] = float(np.interp(qA, spatial_q, values))

            terms = {
                "M": float(coefficients["C_M"] * responses["M"]),
                "PhiPP": float(coefficients["C_PhiPP"] * responses["PhiPP"]),
                "MPhiPP": float(coefficients["C_MPhiPP"] * responses["MPhiPP"]),
                "Delta": float(coefficients["C_Delta"] * responses["Delta"]),
                "SigmaPrime": float(coefficients["C_SigmaPrime"] * responses["SigmaPrime"]),
                "SigmaPrimeDelta": float(coefficients["C_SigmaPrimeDelta"] * responses["SigmaPrimeDelta"]),
            }
            charge = terms["M"] + terms["PhiPP"] + terms["MPhiPP"]
            spatial = terms["Delta"] + terms["SigmaPrime"] + terms["SigmaPrimeDelta"]

            rank_contributions = []
            for J, rank in sorted(spatial_isotope["multipole_ranks"].items()):
                rq = rank["q"]
                rank_responses = {
                    name: float(np.interp(qA, rq, values))
                    for name, values in rank["responses"].items()
                }
                rank_terms = {
                    "Delta": float(coefficients["C_Delta"] * rank_responses["Delta"]),
                    "SigmaPrime": float(coefficients["C_SigmaPrime"] * rank_responses["SigmaPrime"]),
                    "SigmaPrimeDelta": float(coefficients["C_SigmaPrimeDelta"] * rank_responses["SigmaPrimeDelta"]),
                }
                rank_contributions.append({
                    "J": J,
                    "responses_physical_equal_pn_C0_corrected": rank_responses,
                    "coefficient_response_terms": rank_terms,
                    "spatial_sector": float(sum(rank_terms.values())),
                })
            rankwise_spatial = float(sum(row["spatial_sector"] for row in rank_contributions))
            rank_residual = abs(rankwise_spatial - spatial)
            if not _close(rankwise_spatial, spatial):
                failures.append(
                    f"{benchmark.get('benchmark')} {benchmark.get('width_scheme')} "
                    f"Xe-{A}: rankwise spatial contraction does not reconstruct total "
                    f"(residual={rank_residual:.6e})"
                )

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
                failures.append(f"Xe-{A}: interpolated SigmaPrime-Delta Cauchy bound violated")

            results.append({
                "benchmark": benchmark.get("benchmark"),
                "width_scheme": benchmark.get("width_scheme"),
                "g2": benchmark.get("g2"),
                "ER_keV": benchmark.get("ER_keV"),
                "speed_kms": benchmark.get("speed_kms"),
                "A": A,
                "J_A": isotope["J_A"],
                "qA_GeV": qA,
                "common_matrix_normalization_C0": c0,
                "interpolation": "linear in q_A on the common 0.25 MeV AFH grid",
                "responses_physical_equal_pn_C0_corrected": responses,
                "coefficient_response_terms": terms,
                "charge_sector": float(charge),
                "spatial_sector": float(spatial),
                "spatial_sector_from_rank_sum": rankwise_spatial,
                "spatial_rank_reconstruction_abs_residual": rank_residual,
                "spatial_multipole_rank_contributions": rank_contributions,
                "total_response_kernel": float(total),
                "spatial_over_charge": float(spatial / charge) if charge else 0.0,
                "positive_total_kernel": bool(positive),
                "SigmaPrimeDelta_Cauchy_excess": float(cauchy_excess),
            })

    spatial_ratios = [
        abs(row["spatial_over_charge"]) for row in results
        if np.isfinite(row["spatial_over_charge"])
    ]
    rank_residuals = [row["spatial_rank_reconstruction_abs_residual"] for row in results]
    c0_values = [float(spatial_data[A]["C0"]) for A in spatial_data]
    return {
        "status": "PROVISIONAL_AFH_CONTRACTION_PASS" if not failures else "FAIL",
        "calculation_role": "P3-C charge/spatial amplitude-matching diagnostic with q=0 nucleon-current anchors; not B production",
        "primary_B_baseline_included": False,
        "scope": (
            "fixed-speed benchmark contraction of leading static three-body "
            "particle coefficients; AFH-8 charge responses are multiplied by "
            "the same P3-B C0 used by the P3-B spatial responses; rank-resolved "
            "Delta/SigmaPrime/SigmaPrime-Delta contributions are retained; "
            "no halo fold or detector response"
        ),
        "afh_source": {
            "status": afh_metadata["status"],
            "native_afh_validated": afh_metadata["native_afh_validated"],
            "source": afh_metadata["source"],
            "source_commit": afh_metadata.get("afh_source_commit"),
            "csv_sha256": afh_metadata.get("csv_sha256"),
            "artifact_run_id": afh_artifact_run_id,
            "artifact_id": afh_artifact_id,
            "isotopes": list(REQUIRED_METADATA_ISOTOPES),
            "natural_atom_fraction_coverage": afh_metadata.get("natural_atom_fraction_coverage"),
            "normalization": afh_metadata.get("normalization"),
        },
        "spatial_afh_source": {
            "status": spatial_metadata["status"],
            "native_afh_validated": False,
            "source_file_sha256": spatial_metadata["source_file_sha256"],
            "response_file_sha256": spatial_metadata["response_file_sha256"],
            "multipole_file_sha256": spatial_metadata["multipole_file_sha256"],
            "multipole_rows": spatial_metadata["multipole_rows"],
            "artifact_run_id": spatial_artifact_run_id,
            "artifact_id": spatial_artifact_id,
            "C0_by_isotope": {
                str(A): float(spatial_data[A]["C0"]) for A in spatial_data
            },
        },
        "normalization_policy": (
            "AFH factor four is already applied once in physical equal-p/n columns; "
            "the common P3-B OBDME correction C0 is applied to AFH-8 charge "
            "responses and is already present in P3-B spatial responses"
        ),
        "response_columns": "C0-corrected physical equal-p/n responses",
        "form_factor_status": weights_archive.get("form_factor_input", {}).get("status"),
        "benchmarks": results,
        "summary": {
            "benchmark_count": len(weights_archive.get("benchmarks", [])),
            "isotope_count": len(charge_data),
            "contracted_rows": len(results),
            "positive_total_kernel_rows": sum(1 for row in results if row["positive_total_kernel"]),
            "min_abs_spatial_over_charge": min(spatial_ratios) if spatial_ratios else 0.0,
            "max_abs_spatial_over_charge": max(spatial_ratios) if spatial_ratios else 0.0,
            "min_signed_spatial_over_charge": min(row["spatial_over_charge"] for row in results) if results else 0.0,
            "max_signed_spatial_over_charge": max(row["spatial_over_charge"] for row in results) if results else 0.0,
            "min_total_response_kernel": min(row["total_response_kernel"] for row in results) if results else 0.0,
            "max_total_response_kernel": max(row["total_response_kernel"] for row in results) if results else 0.0,
            "max_spatial_rank_reconstruction_abs_residual": max(rank_residuals) if rank_residuals else 0.0,
            "C0_min": min(c0_values) if c0_values else 1.0,
            "C0_max": max(c0_values) if c0_values else 1.0,
            "failures": failures,
        },
        "limitations": [
            "The AFH-8 and P3-B databases are provisional Python translations; native Wolfram validation is pending.",
            "F1 and F2 are constant q=0 anchors in this benchmark; finite-t_N form factors are not included.",
            "The calculation uses fixed-speed points and linear interpolation in q_A; it is not a recoil-grid or halo integration.",
            "No mediator propagator, detector efficiency, resolution, or likelihood is included.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--afh-dir", type=Path, required=True)
    parser.add_argument("--spatial-dir", type=Path, required=True)
    parser.add_argument("--weights-json", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--afh-artifact-run-id", type=int, default=44222087512)
    parser.add_argument("--afh-artifact-id", type=int, default=14391456283)
    parser.add_argument("--spatial-artifact-run-id", type=int, default=44305980766)
    parser.add_argument("--spatial-artifact-id", type=int, default=14428386181)
    args = parser.parse_args()

    verified_afh = verify_afh_archive(args.afh_dir)
    verified_spatial = verify_spatial_archive(args.spatial_dir)
    afh_rows = read_csv(verified_afh["csv_path"])
    spatial_rows = read_csv(verified_spatial["response_path"])
    spatial_multipole_rows = read_csv(verified_spatial["multipole_path"])
    weights_archive = json.loads(args.weights_json.read_text(encoding="utf-8-sig"))

    afh_metadata = dict(verified_afh["metadata"])
    afh_metadata["csv_sha256"] = verified_afh["csv_sha256"]
    afh_metadata["afh_source_commit"] = verified_afh["source_commit"]
    result = contract_archive(
        afh_rows,
        weights_archive,
        afh_metadata,
        spatial_rows,
        spatial_multipole_rows,
        verified_spatial["metadata"],
        afh_artifact_run_id=args.afh_artifact_run_id,
        afh_artifact_id=args.afh_artifact_id,
        spatial_artifact_run_id=args.spatial_artifact_run_id,
        spatial_artifact_id=args.spatial_artifact_id,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "summary": result["summary"]}, indent=2))
    if result["status"] != "PROVISIONAL_AFH_CONTRACTION_PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
