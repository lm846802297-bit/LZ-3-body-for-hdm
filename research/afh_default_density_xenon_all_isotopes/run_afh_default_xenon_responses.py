#!/usr/bin/env python3
"""Extract and evaluate AFH v6.0 built-in default xenon density matrices.

The response is evaluated on the spatial-momentum grid q=0..0.6 GeV.
For each isotope the physical equal-proton/equal-neutron response is
shape-normalized to R_A(0)=A^2. The response curve itself is a function of q;
the selected mass scheme only controls the q <-> E_R annotation and subsequent
three-body kinematics.
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
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "afh_default_density_xe131"))
sys.path.insert(0, str(HERE.parent / "figure2_full_reproduction"))

import run_afh_default_xe131 as afh
from isotope_mass_schemes import isotope_mass_GeV

Z_XE = 54
ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
Q_MAX_GEV = 0.60
Q_STEP_GEV = 0.00025
FM_TO_GEV_INV = 5.0677


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def parse_default_density_matrix(package_path: Path, A: int) -> list[dict]:
    """Parse the built-in sdgXeA matrix selected by SetIsotope[54,A,...]."""
    text = package_path.read_text(encoding="utf-8", errors="strict")
    name = f"sdgXe{A}"
    start = text.find(f"{name}[1]")
    end = text.find(f"{name}length", start)
    if start < 0 or end < 0:
        raise RuntimeError(f"Could not locate built-in {name} default density matrix")

    block = text[start:end]
    number = r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)"
    pattern = re.compile(
        rf"{re.escape(name)}\[(\d+)\]\s*=\s*\{{[^=]+?=\s*{number}\s*,"
        r"\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\};"
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
    if not rows:
        raise RuntimeError(f"No entries parsed from built-in {name} matrix")
    indices = [row["index"] for row in rows]
    if indices != list(range(1, len(rows) + 1)):
        raise RuntimeError(f"{name} density-matrix indices are not contiguous")
    if not any(row["rank"] == 0 and row["isospin"] == 0 for row in rows):
        raise RuntimeError(f"{name} has no isoscalar rank-0 entries")
    return rows


def write_matrix_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def compute_isotope_response(A: int, rows: list[dict], mass_scheme: str):
    b_fm = math.sqrt(41.467 / (45.0*A**(-1.0/3.0) - 25.0*A**(-2.0/3.0)))
    b_GeV_inv = b_fm * FM_TO_GEV_INV
    T_iso = abs(A/2.0 - Z_XE)
    mA = isotope_mass_GeV(A, mass_scheme)
    q_grid = np.arange(round(Q_MAX_GEV/Q_STEP_GEV) + 1, dtype=float) * Q_STEP_GEV

    W00 = np.empty_like(q_grid)
    rank0 = np.empty_like(q_grid)
    rank2 = np.empty_like(q_grid)
    for i, q in enumerate(q_grid):
        value, amplitudes = afh.package_w00(float(q), rows, b_GeV_inv, T_iso)
        W00[i] = value
        rank0[i] = amplitudes[0]
        rank2[i] = amplitudes[2]

    if not np.all(np.isfinite(W00)) or W00[0] <= 0.0:
        raise ArithmeticError(f"Invalid q=0 or non-finite AFH response for Xe-{A}")
    if np.any(W00 < -1e-13 * W00[0]):
        raise ArithmeticError(f"Negative AFH W_M00 beyond roundoff for Xe-{A}")

    R_equal = A*A * W00 / W00[0]
    R_equal[0] = float(A*A)
    ER_keV = np.array([
        afh.recoil_keV(float(q), mA) for q in q_grid
    ])

    records = []
    for i, q in enumerate(q_grid):
        records.append({
            "A": A,
            "Z": Z_XE,
            "q_GeV": float(q),
            "y": float((q*b_GeV_inv/2.0)**2),
            "ER_keV_AME2020": float(ER_keV[i]),
            "W_M00_AFH_isoscalar": float(W00[i]),
            "rank0_amplitude": float(rank0[i]),
            "rank2_amplitude": float(rank2[i]),
            "R_A_equal_pn": float(R_equal[i]),
            "R_over_A2": float(R_equal[i]/(A*A)),
        })

    meta = {
        "A": A,
        "Z": Z_XE,
        "source_density_matrix": f"built-in {f'sdgXe{A}'}",
        "source_selection": f'SetIsotope[54,{A},"default","default"]',
        "density_matrix_entries": len(rows),
        "density_matrix_isoscalar_entries": sum(row["isospin"] == 0 for row in rows),
        "rank0_isoscalar_entries": sum(row["rank"] == 0 and row["isospin"] == 0 for row in rows),
        "rank2_isoscalar_entries": sum(row["rank"] == 2 and row["isospin"] == 0 for row in rows),
        "b_A_fm": b_fm,
        "b_A_GeV_inverse": b_GeV_inv,
        "T_iso": T_iso,
        "mass_scheme_for_ER_annotation": mass_scheme,
        "mA_GeV_for_ER_annotation": mA,
        "q_grid_GeV": [0.0, Q_MAX_GEV, Q_STEP_GEV],
        "W_M00_q0": float(W00[0]),
        "R_A_q0": float(R_equal[0]),
        "expected_R_A_q0": float(A*A),
        "normalization": "R_A(q)=A^2*W_M00(q)/W_M00(0); AFH shape preserved and equal-pn R_A(0)=A^2 imposed",
        "response_q_definition": "q=|spatial momentum transfer|; q grid is independent of the target-mass convention",
        "native_Mathematica_reexecution": False,
    }
    return records, meta


def compare_archived_samples(full_rows: list[dict], sample_path: Path,
                             relative_tolerance: float) -> dict:
    grouped = {}
    interpolators = {}
    for row in full_rows:
        grouped.setdefault(int(row["A"]), []).append(row)
    for A in grouped:
        grouped[A].sort(key=lambda row: float(row["q_GeV"]))
        interpolators[A] = PchipInterpolator(
            [float(row["q_GeV"]) for row in grouped[A]],
            [float(row["R_A_equal_pn"]) for row in grouped[A]],
            extrapolate=False,
        )

    samples = read_csv(sample_path)
    max_relative = 0.0
    comparisons = []
    for sample in samples:
        A = int(sample["A"])
        q = float(sample["q_response_GeV"])
        expected = float(sample["R_A"])
        got = float(interpolators[A](q))
        relative = abs(got/expected - 1.0) if expected else abs(got)
        max_relative = max(max_relative, relative)
        comparisons.append({
            "A": A,
            "ER_keV": float(sample["ER_keV"]),
            "q_response_GeV": q,
            "R_A_archived": expected,
            "R_A_full_grid_interpolated": got,
            "relative_difference": relative,
        })
    if max_relative > relative_tolerance:
        raise ArithmeticError(
            f"AFH full-grid versus archived 28-sample comparison failed: "
            f"max relative difference {max_relative:.3e} > {relative_tolerance:.3e}"
        )
    return {
        "status": "pass",
        "samples_compared": len(samples),
        "isotopes_compared": sorted({int(row["A"]) for row in samples}),
        "relative_tolerance": relative_tolerance,
        "maximum_relative_difference": max_relative,
        "comparisons": comparisons,
    }


def compare_xe131_reference(full_rows: list[dict], reference_path: Path,
                             relative_tolerance: float) -> dict:
    rows = [row for row in full_rows if int(row["A"]) == 131]
    reference = read_csv(reference_path)
    if len(rows) != len(reference):
        raise ValueError("Xe-131 full-grid reference length mismatch")
    max_relative = 0.0
    max_absolute = 0.0
    for new, old in zip(rows, reference):
        q_new, q_old = float(new["q_GeV"]), float(old["q_GeV"])
        if q_new != q_old:
            raise ValueError("Xe-131 reference q grid is not identical")
        a = float(new["R_A_equal_pn"])
        b = float(old["R_equal_pn_normalized"])
        max_absolute = max(max_absolute, abs(a-b))
        if b:
            max_relative = max(max_relative, abs(a/b-1.0))
    if max_relative > relative_tolerance:
        raise ArithmeticError(
            f"Xe-131 reference comparison failed: {max_relative:.3e} > {relative_tolerance:.3e}"
        )
    return {
        "status": "pass",
        "points_compared": len(rows),
        "maximum_absolute_difference": max_absolute,
        "maximum_relative_difference": max_relative,
        "relative_tolerance": relative_tolerance,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--afh-package", type=Path, required=True)
    parser.add_argument("--source-zip", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--mass-scheme", choices=("ame2020_nuclear", "nist_nuclear"),
                        default="ame2020_nuclear")
    parser.add_argument("--isotopes", nargs="+", type=int, default=list(ISOTOPES))
    parser.add_argument("--archived-samples", type=Path,
                        default=HERE.parent/"afh_default_density_natural_xenon_halo"/"input"/"afh_response_samples.csv")
    parser.add_argument("--xe131-reference", type=Path,
                        default=HERE.parent/"afh_default_density_xe131"/"output"/"afh_default_xe131_WM00.csv")
    parser.add_argument("--sample-relative-tolerance", type=float, default=5e-8)
    parser.add_argument("--xe131-relative-tolerance", type=float, default=2e-12)
    args = parser.parse_args()

    if tuple(args.isotopes) != ISOTOPES:
        if len(set(args.isotopes)) != len(args.isotopes):
            raise ValueError("duplicate isotope requested")
    package = args.afh_package.resolve()
    source_zip = args.source_zip.resolve()
    source_text = package.read_text(encoding="utf-8", errors="strict")
    if "Welcome to DMFormFactor version 1.1." not in source_text:
        raise RuntimeError("Unexpected AFH package footer/version marker")

    matrix_dir = args.outdir/"density_matrices"
    matrix_dir.mkdir(parents=True, exist_ok=True)
    all_rows = []
    isotope_metadata = []
    for A in args.isotopes:
        rows = parse_default_density_matrix(package, A)
        matrix_path = matrix_dir/f"afh_default_xe{A}_density_matrix.csv"
        write_matrix_csv(matrix_path, rows)
        response_rows, meta = compute_isotope_response(A, rows, args.mass_scheme)
        meta["density_matrix_csv"] = str(matrix_path.relative_to(args.outdir))
        meta["density_matrix_csv_sha256"] = sha256(matrix_path)
        all_rows.extend(response_rows)
        isotope_metadata.append(meta)
        print(
            f"Xe-{A}: {len(rows)} density entries, b_A={meta['b_A_fm']:.8f} fm, "
            f"R_A(0)={meta['R_A_q0']:.8g}, {len(response_rows)} q points",
            flush=True,
        )

    response_path = args.outdir/"afh_default_xenon_WM00.csv"
    with response_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)

    sample_comparison = compare_archived_samples(
        all_rows, args.archived_samples, args.sample_relative_tolerance
    )
    xe131_comparison = compare_xe131_reference(
        all_rows, args.xe131_reference, args.xe131_relative_tolerance
    )
    (args.outdir/"archived_28_sample_comparison.csv").write_text(
        "A,ER_keV,q_response_GeV,R_A_archived,R_A_full_grid_interpolated,relative_difference\n" +
        "\n".join(
            f"{r['A']},{r['ER_keV']:.12g},{r['q_response_GeV']:.15g},"
            f"{r['R_A_archived']:.15g},{r['R_A_full_grid_interpolated']:.15g},"
            f"{r['relative_difference']:.12g}"
            for r in sample_comparison["comparisons"]
        ) + "\n",
        encoding="utf-8",
    )

    metadata = {
        "source_archive": "DMFormFactor v6.0",
        "source_zip": source_zip.name,
        "source_zip_sha256": sha256(source_zip),
        "source_file": package.name,
        "source_file_sha256": sha256(package),
        "source_url": "https://www.ocf.berkeley.edu/~nanand/software/dmformfactor/v6.zip",
        "mass_scheme_for_ER_annotation": args.mass_scheme,
        "isotopes": list(args.isotopes),
        "isotope_metadata": isotope_metadata,
        "response_file": response_path.name,
        "response_rows": len(all_rows),
        "q_grid_GeV": [0.0, Q_MAX_GEV, Q_STEP_GEV],
        "response_definition": "AFH v6.0 built-in default-density W_M^{00}; physical equal-pn shape normalized to R_A(0)=A^2",
        "response_q_definition": "q=|spatial momentum transfer|; exact-spatial q is applied later in the three-body halo fold",
        "archived_28_sample_comparison": {k:v for k,v in sample_comparison.items() if k!="comparisons"},
        "xe131_full_grid_reference_comparison": xe131_comparison,
        "limitations": [
            "This is a source-translated Python evaluation of the AFH v6.0 built-in default matrices, not a native Mathematica re-execution.",
            "The 28 archived NIST-mass response samples are used only as validation points; the full curves are evaluated independently from the v6.0 source matrices.",
            "The response grid is a function of spatial q. AME2020 masses enter when mapping each recoil energy to q_exact and in the three-body kinematics.",
            "Xe-124 and Xe-126 are not included because the AFH v6.0 default density matrices used by the natural-xenon baseline are unavailable for these isotopes."
        ],
    }
    (args.outdir/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "response_rows": len(all_rows),
        "archived_28_sample_comparison": metadata["archived_28_sample_comparison"],
        "xe131_reference_comparison": xe131_comparison,
        "output": str(args.outdir),
    },indent=2),flush=True)


if __name__ == "__main__":
    main()
