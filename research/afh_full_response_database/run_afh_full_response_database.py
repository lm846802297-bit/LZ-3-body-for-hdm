#!/usr/bin/env python3
"""Seven-isotope, eight-response AFH v6.0 database generator.

This module extends the already audited AFH v6.0 Python translation with
Sigma'' (response index 2) and PhiTilde' (response index 5).  It preserves
the raw tau1=tau2=0 AFH convention and also writes the explicitly converted
physical equal-proton/equal-neutron convention.  Native Wolfram validation
is a separate acceptance step; Python consistency is not labelled native
AFH validation.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BASE_STUDY = HERE.parent / "afh_default_density_xe131"
BASE_PATH = BASE_STUDY / "run_afh_spatial_response_audit.py"
_SPEC = importlib.util.spec_from_file_location("afh_spatial_base", BASE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot load the audited AFH base implementation: {BASE_PATH}")
base = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(base)

ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
J_BY_A = {128: 0.0, 129: 0.5, 130: 0.0, 131: 1.5,
          132: 0.0, 134: 0.0, 136: 0.0}
Z_XE = 54
RESPONSE_COLUMNS = {
    "M": "W_M00_AFH",
    "SigmaDoublePrime": "W_SigmaDoublePrime00_AFH",
    "SigmaPrime": "W_SigmaPrime00_AFH",
    "PhiPP": "W_PhiPP00_AFH",
    "PhiTildePrime": "W_PhiTildePrime00_AFH",
    "Delta": "W_Delta00_AFH",
    "MPhiPP": "W_MPhiPP00_AFH",
    "SigmaPrimeDelta": "W_SigmaPrimeDelta00_AFH",
}
DIAGONAL_FAMILIES = (
    "M", "SigmaDoublePrime", "SigmaPrime",
    "PhiPP", "PhiTildePrime", "Delta",
)
PHYSICAL_FACTOR = 4.0


def _mjl_sigma(y, Np, two_jp, N, two_j, jcap, lcap):
    """AFH v6.0 MJLSigma radial-angular matrix element."""
    if lcap < 0:
        return 0.0
    nrp, lp = base.orbital(Np, two_jp)
    nr, ell = base.orbital(N, two_j)
    jp = two_jp / 2.0
    j = two_j / 2.0
    pref = (
        (-1.0) ** int(lp)
        * math.sqrt(
            base.jnorm(j) * base.jnorm(jp)
            * base.jnorm(ell) * base.jnorm(lp)
            * base.jnorm(jcap) * base.jnorm(lcap)
            / (4.0 * math.pi)
        )
        * math.sqrt(6.0)
    )
    return (
        pref
        * base.w3(lp, lcap, ell)
        * base.w9(lp, ell, lcap, 0.5, 0.5, 1.0, jp, j, jcap)
        * base.bessel(y, nrp, lp, nr, ell, lcap)
    )


def sigma_second_element(y, Np, two_jp, N, two_j, L):
    """AFH SigmaPPJ/Sigma'' operator (response index 2)."""
    if not base.abnormal_allowed(Np, two_jp, N, two_j, L):
        return 0.0
    upper = math.sqrt(L + 1.0) * _mjl_sigma(
        y, Np, two_jp, N, two_j, L, L + 1
    )
    lower = math.sqrt(float(L)) * _mjl_sigma(
        y, Np, two_jp, N, two_j, L, L - 1
    )
    return (upper + lower) / base.qnorm(L)


def sigma_element(y, Np, two_jp, N, two_j, L):
    """AFH SigmaJ operator used in PhiTilde'."""
    if not base.normal_allowed(Np, two_jp, N, two_j, L):
        return 0.0
    return _mjl_sigma(y, Np, two_jp, N, two_j, L, L)


def phi_prime_element(y, Np, two_jp, N, two_j, L):
    """AFH PhiPJ operator, before adding SigmaJ/2 in PhiTPJ."""
    if not base.normal_allowed(Np, two_jp, N, two_j, L):
        return 0.0

    nrp, lp = base.orbital(Np, two_jp)
    nr, ell = base.orbital(N, two_j)
    jp = two_jp / 2.0
    j = two_j / 2.0
    overall = (
        (-1.0) ** int(lp + 1)
        * 6.0 * base.qnorm(lp) * base.qnorm(jp) * base.qnorm(j)
        / math.sqrt(4.0 * math.pi)
    )

    def nine(lcap):
        return base.w9(lp, ell, lcap, 0.5, 0.5, 1.0, jp, j, L)

    def summand1():
        angular = 0.0
        for lc in (L, L + 1):
            angular += (
                (-1.0) ** (L - lc + 1)
                * base.jnorm(lc)
                * base.w6(L + 1, 1, lc, 1, L, 1)
                * base.w6(L + 1, 1, lc, ell, lp, ell + 1)
                * nine(lc)
            )
        return (
            base.qnorm(ell + 1) * math.sqrt(ell + 1.0)
            * base.w3(lp, L + 1, ell + 1)
            * base.bessel_derivative(
                y, nrp, lp, nr, ell, L + 1, "minus"
            )
            * angular
        )

    def summand2():
        if ell == 0:
            return 0.0
        angular = 0.0
        for lc in (L, L + 1):
            angular += (
                (-1.0) ** (L - lc)
                * base.jnorm(lc)
                * base.w6(L + 1, 1, lc, 1, L, 1)
                * base.w6(L + 1, 1, lc, ell, lp, ell - 1)
                * nine(lc)
            )
        return (
            base.qnorm(ell - 1) * math.sqrt(float(ell))
            * base.w3(lp, L + 1, ell - 1)
            * base.bessel_derivative(
                y, nrp, lp, nr, ell, L + 1, "plus"
            )
            * angular
        )

    def summand3():
        if L == 0:
            return 0.0
        angular = 0.0
        for lc in (L - 1, L):
            angular += (
                (-1.0) ** (L - lc + 1)
                * base.jnorm(lc)
                * base.w6(L - 1, 1, lc, 1, L, 1)
                * base.w6(L - 1, 1, lc, ell, lp, ell + 1)
                * nine(lc)
            )
        return (
            base.qnorm(ell + 1) * math.sqrt(ell + 1.0)
            * base.w3(lp, L - 1, ell + 1)
            * base.bessel_derivative(
                y, nrp, lp, nr, ell, L - 1, "minus"
            )
            * angular
        )

    def summand4():
        if L == 0 or ell == 0:
            return 0.0
        angular = 0.0
        for lc in (L - 1, L):
            angular += (
                (-1.0) ** (L - lc)
                * base.jnorm(lc)
                * base.w6(L - 1, 1, lc, 1, L, 1)
                * base.w6(L - 1, 1, lc, ell, lp, ell - 1)
                * nine(lc)
            )
        return (
            base.qnorm(ell - 1) * math.sqrt(float(ell))
            * base.w3(lp, L - 1, ell - 1)
            * base.bessel_derivative(
                y, nrp, lp, nr, ell, L - 1, "plus"
            )
            * angular
        )

    upper = -base.qnorm(L + 1) * math.sqrt(float(L)) * (
        summand1() + summand2()
    )
    lower = 0.0
    if L > 0:
        lower = base.qnorm(L - 1) * math.sqrt(L + 1.0) * (
            summand3() + summand4()
        )
    return overall * (upper + lower)


def phi_tilde_prime_element(y, Np, two_jp, N, two_j, L):
    """AFH PhiTPJ = PhiPJ + SigmaJ/2 (response index 5)."""
    return (
        phi_prime_element(y, Np, two_jp, N, two_j, L)
        + 0.5 * sigma_element(y, Np, two_jp, N, two_j, L)
    )


def multipole_amplitudes(A, q_GeV, density_rows):
    """Return source-defined AFH multipole amplitudes for all six diagonals."""
    if A not in J_BY_A:
        raise ValueError(f"Unsupported AFH default xenon isotope A={A}")
    b_fm = math.sqrt(
        41.467 / (45.0 * A ** (-1.0 / 3.0) - 25.0 * A ** (-2.0 / 3.0))
    )
    b_GeV_inv = b_fm * base.FM_TO_GEV_INV
    y = (q_GeV * b_GeV_inv / 2.0) ** 2
    T = abs(A / 2.0 - Z_XE)
    iso_factor = math.sqrt(2.0 / (2.0 * T + 1.0))
    families = (
        "M", "SigmaDoublePrime", "SigmaPrime",
        "PhiPP", "PhiTildePrime", "Delta",
    )
    amplitudes = {name: {} for name in families}

    for L in range(15):
        sums = {name: 0.0 for name in families}
        for row in density_rows:
            if row["rank"] != L or row["isospin"] != 0:
                continue
            args = (
                row["Nprime"], row["two_jprime"],
                row["N"], row["two_j"], L,
            )
            coefficient = row["coefficient"] * iso_factor
            sums["M"] += coefficient * base.m_element(y, *args)
            sums["SigmaDoublePrime"] += coefficient * sigma_second_element(y, *args)
            sums["SigmaPrime"] += coefficient * base.sigma_prime_element(y, *args)
            sums["PhiPP"] += coefficient * base.phi_pp_element(y, *args)
            sums["PhiTildePrime"] += coefficient * phi_tilde_prime_element(y, *args)
            sums["Delta"] += coefficient * base.delta_element(y, *args)
        for name in families:
            amplitudes[name][L] = sums[name]
    return amplitudes, y, b_fm, b_GeV_inv


def response_bundle(A, q_GeV, density_rows):
    """Compute all eight AFH responses in the raw isoscalar convention."""
    amps, y, b_fm, b_GeV_inv = multipole_amplitudes(A, q_GeV, density_rows)
    raw = {}
    for name in DIAGONAL_FAMILIES:
        raw[RESPONSE_COLUMNS[name]] = (
            sum(value * value for value in amps[name].values()) / 4.0
        )
    raw[RESPONSE_COLUMNS["MPhiPP"]] = (
        sum(amps["M"][L] * amps["PhiPP"][L] for L in amps["M"]) / 4.0
    )
    raw[RESPONSE_COLUMNS["SigmaPrimeDelta"]] = (
        sum(
            amps["SigmaPrime"][L] * amps["Delta"][L]
            for L in amps["SigmaPrime"]
        ) / 4.0
    )

    J_A = J_BY_A[A]
    response_conversion = 4.0 * math.pi / (2.0 * J_A + 1.0)
    record = {
        "A": A,
        "J_A": J_A,
        "q_GeV": q_GeV,
        "y": y,
        "b_A_fm": b_fm,
        "b_A_GeV_inverse": b_GeV_inv,
        **raw,
    }
    for name, column in RESPONSE_COLUMNS.items():
        r_raw = response_conversion * raw[column]
        record[f"R_{name}_raw"] = r_raw
        record[f"R_{name}_physical_equal_pn"] = PHYSICAL_FACTOR * r_raw
    return record


def generate_database(outdir: Path, q_values, isotopes=ISOTOPES):
    outdir.mkdir(parents=True, exist_ok=True)
    records = []
    summaries = {}
    for A in isotopes:
        density_rows = base.load_matrix(A)
        isotope_records = []
        for index, q in enumerate(q_values):
            record = response_bundle(A, float(q), density_rows)
            records.append(record)
            isotope_records.append(record)
            if (index + 1) % 400 == 0:
                print(f"Xe-{A}: {index + 1}/{len(q_values)} q nodes", flush=True)

        summaries[str(A)] = {
            "J_A": J_BY_A[A],
            "density_matrix_entries": len(density_rows),
            "q_points": len(q_values),
            "q_min_GeV": float(min(q_values)),
            "q_max_GeV": float(max(q_values)),
            "response_ranges": {
                column: {
                    "min": min(float(row[column]) for row in isotope_records),
                    "max": max(float(row[column]) for row in isotope_records),
                }
                for column in RESPONSE_COLUMNS.values()
            },
        }

    csv_path = outdir / "afh_v6_full_eight_response_7isotope.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    q_grid = {
        "points": len(q_values),
        "q_min_GeV": float(min(q_values)),
        "q_max_GeV": float(max(q_values)),
        "step_GeV": (
            float(q_values[1] - q_values[0]) if len(q_values) > 1 else None
        ),
    }
    metadata = {
        "status": "PROVISIONAL_PYTHON",
        "native_afh_validated": False,
        "source": "AFH DMFormFactor v6.0 operator definitions translated to Python",
        "afh_source_path": "v6/dmformfactor-V6.m",
        "isospin": "tau1=tau2=0 (raw AFH isoscalar package convention)",
        "isotopes": list(isotopes),
        "natural_atom_fraction_coverage": 0.998158,
        "excluded_natural_isotopes": {
            "124": "No AFH v6.0 default density matrix in the project's seven-isotope input set",
            "126": "No AFH v6.0 default density matrix in the project's seven-isotope input set",
        },
        "q_grid": q_grid,
        "response_index_map": {
            "1": "M",
            "2": "SigmaDoublePrime",
            "3": "SigmaPrime",
            "4": "PhiPP",
            "5": "PhiTildePrime",
            "6": "Delta",
            "7": "M-PhiPP interference",
            "8": "SigmaPrime-Delta interference",
        },
        "normalization": {
            "raw": "W_X = ResponseNuclear[y,index,0,0], AFH v6.0 package convention",
            "response_conversion": "R_X_raw = 4*pi/(2*J_A+1) * W_X",
            "physical_equal_pn": "R_X_physical_equal_pn = 4 * R_X_raw",
            "factor_four_applied_once_to_physical_columns": True,
            "raw_columns_unrescaled": True,
            "interference_signs_preserved": True,
        },
        "limitations": [
            "SigmaDoublePrime and PhiTildePrime are new Python translations of AFH source definitions and await native Wolfram pointwise validation.",
            "SigmaPrime, Delta, and SigmaPrime-Delta remain provisional until native AFH indices 3, 6, and 8 are compared.",
            "M, PhiPP, and M-PhiPP retain the existing Xe-131 native anchor validation; the full seven-isotope eight-response grid is not yet natively validated.",
            "No finite-t nucleon form factors or three-body L_mu_nu W_A^mu_nu contraction are included.",
            "No halo integration or detector response is included.",
        ],
        "isotope_summaries": summaries,
    }
    metadata_path = outdir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return csv_path, metadata_path, metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--isotopes", type=int, nargs="+", default=list(ISOTOPES))
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--q", type=float, nargs="*", help="Explicit q_A values in GeV")
    group.add_argument("--grid-points", type=int, default=2401)
    parser.add_argument("--q-min", type=float, default=0.0)
    parser.add_argument("--q-max", type=float, default=0.6)
    args = parser.parse_args()

    if any(A not in J_BY_A for A in args.isotopes):
        parser.error(f"--isotopes must be selected from {ISOTOPES}")
    if args.q is not None:
        q_values = list(args.q)
        if not q_values:
            parser.error("--q requires at least one q_A value")
    else:
        if args.grid_points < 2 or args.q_max <= args.q_min:
            parser.error("--grid-points must be >=2 and --q-max > --q-min")
        q_values = np.linspace(args.q_min, args.q_max, args.grid_points).tolist()

    csv_path, metadata_path, metadata = generate_database(
        args.outdir, q_values, tuple(args.isotopes)
    )
    print(json.dumps({
        "status": metadata["status"],
        "csv": str(csv_path),
        "metadata": str(metadata_path),
        "rows": len(q_values) * len(args.isotopes),
        "isotopes": args.isotopes,
        "q_grid": metadata["q_grid"],
        "responses": metadata["response_index_map"],
    }, indent=2))


if __name__ == "__main__":
    main()
