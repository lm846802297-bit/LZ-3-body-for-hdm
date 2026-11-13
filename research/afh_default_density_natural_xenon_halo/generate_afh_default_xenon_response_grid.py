#!/usr/bin/env python3
"""Generate the complete AFH v6.0 default-response grid for available natural-Xe isotopes.

The AFH source contains default density matrices for A={128,129,130,131,132,134,136}.
This script extracts those matrices directly from the committed official source and
uses the already audited Python translation of the AFH finite-sum kernel.  It does
not synthesize Xe-124 or Xe-126 matrices.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "afh_default_density_xe131"))
import run_afh_default_xe131 as afh  # noqa: E402

Z = 54
ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
Q_MAX_GEV = 0.60
Q_STEP_GEV = 0.00025
EXPECTED_ENTRIES = {128: 21, 129: 39, 130: 21, 131: 67, 132: 21, 134: 21, 136: 21}
MATRIX_FIELDS = (
    "index", "coefficient", "rank", "isospin",
    "Nprime", "two_jprime", "N", "two_j",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _spin_value(raw: str) -> float:
    if "/" in raw:
        numerator, denominator = raw.split("/", 1)
        return int(numerator) / int(denominator)
    return float(raw)


def parse_isotopic_spins(source_text: str) -> dict[int, float]:
    match = re.search(r"IsotopicSpins=\{(.*?)\};", source_text, flags=re.S)
    if not match:
        raise RuntimeError("Could not locate AFH IsotopicSpins table")
    result = {
        int(m.group(1)): _spin_value(m.group(2))
        for m in re.finditer(
            r"\{\s*54\s*,\s*(\d+)\s*,\s*([0-9]+(?:/[0-9]+)?)\s*\}",
            match.group(1),
        )
    }
    required = set(ISOTOPES) | {124, 126}
    missing = sorted(required - result.keys())
    if missing:
        raise RuntimeError(f"AFH IsotopicSpins table lacks xenon A={missing}")
    return result


def parse_default_dispatch(source_text: str, A: int) -> bool:
    pattern = (
        rf"If\[Ziso==54&&Mxx=={A},[\s\S]*?"
        rf"DensityMatrix=sdgXe{A};[\s\S]*?"
        rf"SetDMmatrixLength\[sdgXe{A}length\];[\s\S]*?Return\[\];\];"
    )
    return re.search(pattern, source_text) is not None


def parse_density_matrix(source_text: str, A: int) -> list[dict]:
    start = source_text.find(f"sdgXe{A}[1]")
    end = source_text.find(f"sdgXe{A}length", start)
    if start < 0 or end < 0:
        raise RuntimeError(f"Could not locate AFH sdgXe{A} matrix block")
    length_match = re.search(rf"sdgXe{A}length\s*=\s*(\d+)\s*;", source_text[end:])
    if not length_match:
        raise RuntimeError(f"Could not read AFH sdgXe{A}length")
    expected = int(length_match.group(1))
    if expected != EXPECTED_ENTRIES[A]:
        raise RuntimeError(
            f"AFH source matrix length changed for Xe-{A}: "
            f"expected {EXPECTED_ENTRIES[A]}, found {expected}"
        )

    block = source_text[start:end]
    pattern = re.compile(
        rf"sdgXe{A}\[(\d+)\]=\{{[^=]+?="
        r"([-+]?\d+(?:\.\d*)?(?:[Ee][-+]?\d+)?),"
        r"(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\};"
    )
    rows = []
    for match in pattern.finditer(block):
        idx, coeff, rank, tau, Np, two_jp, Nn, two_jn = match.groups()
        rows.append({
            "index": int(idx),
            "coefficient": float(coeff),
            "rank": int(rank),
            "isospin": int(tau),
            "Nprime": int(Np),
            "two_jprime": int(two_jp),
            "N": int(Nn),
            "two_j": int(two_jn),
        })
    if len(rows) != expected:
        raise RuntimeError(
            f"AFH Xe-{A}: expected {expected} matrix entries, parsed {len(rows)}"
        )
    if [row["index"] for row in rows] != list(range(1, expected + 1)):
        raise RuntimeError(f"AFH Xe-{A}: matrix indices are not contiguous")
    return rows


def read_natural_xenon_masses(path: Path) -> dict[int, dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    result = {}
    for row in rows:
        A = int(row["A"])
        result[A] = {
            "isotope": row["isotope"],
            "atomic_mass_u": float(row["atomic_mass_u"]),
            "natural_atom_fraction": float(row["natural_atom_fraction"]),
            "AFH_default_density_available": row["AFH_default_density_available"].lower() == "true",
            "nuclear_mass_GeV": float(row["nuclear_mass_GeV"]),
        }
    return result


def oscillator_length_fm(A: int) -> float:
    return math.sqrt(41.467 / (45 * A ** (-1 / 3) - 25 * A ** (-2 / 3)))


def recoil_keV(q_GeV: float, mass_GeV: float) -> float:
    return (math.sqrt(mass_GeV * mass_GeV + q_GeV * q_GeV) - mass_GeV) * 1.0e6


def compute_isotope_grid(
    A: int,
    rows: list[dict],
    J_A: float,
    mass_GeV: float,
    q_grid: np.ndarray,
) -> tuple[list[dict], dict]:
    b_fm = oscillator_length_fm(A)
    b_GeV_inv = b_fm * afh.FM_TO_GEV_INV_AFH
    T_iso = abs(A / 2.0 - Z)
    records = []
    for q_value in q_grid:
        q = float(q_value)
        W00, amplitudes = afh.package_w00(q, rows, b_GeV_inv, T_iso)
        package_response = 4.0 * math.pi / (2.0 * J_A + 1.0) * W00
        records.append({
            "A": A,
            "J_A": J_A,
            "T_iso": T_iso,
            "b_A_fm": b_fm,
            "q_GeV": q,
            "y": (q * b_GeV_inv / 2.0) ** 2,
            "ER_keV": recoil_keV(q, mass_GeV),
            "W_M00_AFH_package": W00,
            "R_AFH_package_4pi_over_2Jplus1": package_response,
            "R_equal_pn_raw": 4.0 * package_response,
            "rank0_amplitude": amplitudes[0],
            "rank2_amplitude": amplitudes[2],
        })

    package_zero = records[0]["R_AFH_package_4pi_over_2Jplus1"]
    expected_zero = A * A / 4.0
    zero_relative_error = abs(package_zero / expected_zero - 1.0)
    if zero_relative_error > 2.0e-4:
        raise RuntimeError(
            f"Xe-{A}: AFH package R(0) differs from A^2/4 by "
            f"{zero_relative_error:.6e}"
        )

    raw_zero = records[0]["R_equal_pn_raw"]
    normalization = (A * A) / raw_zero
    for row in records:
        row["A0_normalization_factor"] = normalization
        row["R_equal_pn_normalized"] = row["R_equal_pn_raw"] * normalization
        row["R_equal_J0_normalized"] = (
            normalization * math.pi * row["rank0_amplitude"] ** 2
        )
        row["R_equal_J2_normalized"] = (
            normalization * math.pi * row["rank2_amplitude"] ** 2
        )
        row["R_over_A2"] = row["R_equal_pn_normalized"] / (A * A)

    values = np.asarray([row["R_over_A2"] for row in records], dtype=float)
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"Xe-{A}: non-finite response value encountered")
    if abs(records[0]["R_equal_pn_normalized"] / (A * A) - 1.0) > 2.0e-14:
        raise RuntimeError(f"Xe-{A}: physical q=0 normalization failed")

    summary = {
        "A": A,
        "J_A": J_A,
        "T_iso": T_iso,
        "matrix_entries": len(rows),
        "isoscalar_rank_counts": {
            str(rank): sum(row["rank"] == rank and row["isospin"] == 0 for row in rows)
            for rank in sorted({row["rank"] for row in rows if row["isospin"] == 0})
        },
        "b_A_fm": b_fm,
        "b_A_GeV_inverse": b_GeV_inv,
        "AFH_package_R0": package_zero,
        "AFH_expected_R0_A2_over_4": expected_zero,
        "AFH_R0_relative_error": zero_relative_error,
        "physical_R0": records[0]["R_equal_pn_normalized"],
        "A2": A * A,
        "finite_precision_shape_normalization": normalization,
        "grid_minimum_q_GeV": records[int(np.argmin(values))]["q_GeV"],
        "grid_minimum_R_over_A2": float(np.min(values)),
    }
    return records, summary


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def generate(afh_package: Path, weights_path: Path, outdir: Path) -> dict:
    source_text = afh_package.read_text(encoding="utf-8", errors="strict")
    if "Welcome to DMFormFactor version 1.1." not in source_text:
        raise RuntimeError("Unexpected AFH package version marker")
    source_sha = sha256_file(afh_package)
    spins = parse_isotopic_spins(source_text)
    masses = read_natural_xenon_masses(weights_path)

    if not all(parse_default_dispatch(source_text, A) for A in ISOTOPES):
        raise RuntimeError("AFH default xenon dispatch does not match the audited seven-isotope set")
    if any(parse_default_dispatch(source_text, A) for A in (124, 126)):
        raise RuntimeError("AFH Xe-124/Xe-126 default dispatch unexpectedly appeared; update the audit")

    available_fraction = sum(
        masses[A]["natural_atom_fraction"] for A in ISOTOPES
    )
    total_a2_weight = sum(
        item["natural_atom_fraction"] * A * A for A, item in masses.items()
    )
    available_a2_weight = sum(
        masses[A]["natural_atom_fraction"] * A * A for A in ISOTOPES
    )
    q_grid = np.arange(round(Q_MAX_GEV / Q_STEP_GEV) + 1) * Q_STEP_GEV
    if len(q_grid) != 2401 or abs(q_grid[-1] - Q_MAX_GEV) > 1.0e-14:
        raise RuntimeError("Unexpected AFH q grid")

    outdir.mkdir(parents=True, exist_ok=True)
    matrix_dir = outdir / "density_matrices"
    matrix_dir.mkdir(parents=True, exist_ok=True)
    combined_rows = []
    summaries = []
    output_files = []

    for A in ISOTOPES:
        rows = parse_density_matrix(source_text, A)
        matrix_path = matrix_dir / f"afh_default_xe{A}_density_matrix.csv"
        write_csv(matrix_path, rows)
        output_files.append(matrix_path)

        grid_rows, summary = compute_isotope_grid(
            A=A,
            rows=rows,
            J_A=spins[A],
            mass_GeV=masses[A]["nuclear_mass_GeV"],
            q_grid=q_grid,
        )
        summary.update({
            "isotope": masses[A]["isotope"],
            "natural_atom_fraction": masses[A]["natural_atom_fraction"],
            "nuclear_mass_GeV": masses[A]["nuclear_mass_GeV"],
            "density_matrix_sha256": sha256_file(matrix_path),
        })
        summaries.append(summary)
        combined_rows.extend(grid_rows)

        per_isotope_path = outdir / f"afh_default_xe{A}_response_2401.csv"
        write_csv(per_isotope_path, grid_rows)
        output_files.append(per_isotope_path)

    combined_path = outdir / "afh_v6_default_xenon_7isotope_response_16807.csv"
    write_csv(combined_path, combined_rows)
    output_files.append(combined_path)

    summary_path = outdir / "isotope_response_summary.csv"
    write_csv(summary_path, summaries)
    output_files.append(summary_path)

    missing = []
    for A in (124, 126):
        item = masses[A]
        missing.append({
            "A": A,
            "isotope": item["isotope"],
            "J_A": spins[A],
            "natural_atom_fraction": item["natural_atom_fraction"],
            "reason": "No sdgXeA default density matrix or SetIsotope default dispatch in AFH v6.0",
        })

    metadata = {
        "status": "PASS",
        "source": "AFH DMFormFactor v6.0 committed source",
        "source_file": str(afh_package.relative_to(ROOT)),
        "source_file_sha256": source_sha,
        "weights_file": str(weights_path.relative_to(ROOT)),
        "weights_file_sha256": sha256_file(weights_path),
        "response_convention": "AFH exact spatial momentum q; y=(b_A q/2)^2",
        "physical_response_convention": "R_equal_pn(q)=A^2 R_AFH_package(q)/R_AFH_package(0); AFH factor four applied exactly once",
        "q_grid_GeV": {
            "minimum": float(q_grid[0]),
            "maximum": float(q_grid[-1]),
            "step": Q_STEP_GEV,
            "points_per_isotope": len(q_grid),
        },
        "available_isotopes": list(ISOTOPES),
        "missing_default_isotopes": missing,
        "natural_atom_fraction_coverage": available_fraction,
        "A2_weighted_zero_q_coherent_coverage": available_a2_weight / total_a2_weight,
        "response_rows": len(combined_rows),
        "response_file": combined_path.name,
        "response_file_sha256": sha256_file(combined_path),
        "isotopes": summaries,
        "scope_limit": (
            "This is the complete 7-isotope AFH v6.0 default response grid. "
            "It is not a 9-isotope all-AFH grid: Xe-124 and Xe-126 lack default matrices."
        ),
    }
    metadata_path = outdir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    output_files.append(metadata_path)

    sums_path = outdir / "SHA256SUMS.txt"
    sums_path.write_text(
        "".join(f"{sha256_file(path)}  {path.relative_to(outdir).as_posix()}\n"
                for path in output_files if path != sums_path),
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--afh-package", type=Path,
        default=ROOT / "v6" / "dmformfactor-V6.m",
    )
    parser.add_argument(
        "--weights", type=Path,
        default=HERE / "input" / "natural_xenon_isotope_weights.csv",
    )
    parser.add_argument(
        "--outdir", type=Path, required=True,
    )
    args = parser.parse_args()
    metadata = generate(
        args.afh_package.resolve(),
        args.weights.resolve(),
        args.outdir.resolve(),
    )
    print(json.dumps({
        "status": metadata["status"],
        "response_rows": metadata["response_rows"],
        "available_isotopes": metadata["available_isotopes"],
        "missing_default_isotopes": metadata["missing_default_isotopes"],
        "natural_atom_fraction_coverage": metadata["natural_atom_fraction_coverage"],
        "A2_weighted_zero_q_coherent_coverage": metadata["A2_weighted_zero_q_coherent_coverage"],
        "response_file_sha256": metadata["response_file_sha256"],
        "output_directory": str(args.outdir),
    }, indent=2))


if __name__ == "__main__":
    main()
