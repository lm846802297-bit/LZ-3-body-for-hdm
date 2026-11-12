#!/usr/bin/env python3
"""Independent high-precision AFH response checks at selected exact spatial-q points.

This script distinguishes the archived 28 selected values (PCHIP samples from
the historical 2401-node grid) from direct evaluations of the AFH finite-sum
response at the exact isotope-specific momentum transfer. It also produces
the exact-q response table needed by the selected-point halo fold.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import mpmath as mp
import numpy as np
from scipy.interpolate import PchipInterpolator
from sympy import Integer, Rational, pi, simplify, N as symN
from sympy.physics.wigner import wigner_3j, wigner_6j

import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "figure2_full_reproduction"))
from isotope_mass_schemes import isotope_mass_GeV  # noqa: E402

ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
GROUND_STATE_SPIN = {
    128: 0.0, 129: 0.5, 130: 0.0, 131: 1.5,
    132: 0.0, 134: 0.0, 136: 0.0,
}
Z = 54
ER_POINTS_KEV = (101.0, 200.0, 267.0, 542.0)
MASS_SCHEMES = ("nist_nuclear", "ame2020_nuclear")
FM_TO_GEV_INV = mp.mpf("5.0677")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def orbital_n_l(Nprincipal: int, two_j: int) -> tuple[int, int]:
    jph = (two_j + 1) // 2
    ell = jph if (Nprincipal - jph) % 2 == 0 else jph - 1
    n = (Nprincipal - ell) // 2 + 1
    if n < 1:
        raise ValueError("Invalid AFH oscillator orbital")
    return n, ell


def angular_exact(row: dict[str, str], rank: int, dps: int) -> mp.mpf:
    _, ell = orbital_n_l(int(row["N"]), int(row["two_j"]))
    _, lp = orbital_n_l(int(row["Nprime"]), int(row["two_jprime"]))
    jp = Rational(int(row["two_jprime"]), 2)
    jn = Rational(int(row["two_j"]), 2)
    J = Integer(rank)
    phase = (-1) ** (Rational(1, 2) + jn + J)
    prefactor = mp.mpf(str(symN(simplify(
        ((2*jn+1)*(2*jp+1)*(2*ell+1)*(2*lp+1)*(2*J+1)/(4*pi))**Rational(1, 2)
    ), dps + 12)))
    w3 = mp.mpf(str(symN(
        wigner_3j(Integer(lp), J, Integer(ell), 0, 0, 0), dps + 12
    )))
    w6 = mp.mpf(str(symN(
        wigner_6j(Integer(lp), jp, Rational(1, 2), jn, Integer(ell), J),
        dps + 12
    )))
    phase_mp = mp.mpf(str(symN(phase, dps + 12)))
    return phase_mp * prefactor * w3 * w6


def build_grouped_coefficients(
    A: int, matrix_csv: Path, dps: int
) -> dict[int, dict[mp.mpf, mp.mpf]]:
    mp.mp.dps = dps
    T_iso = mp.mpf(str(abs(A / 2.0 - Z)))
    isoscalar_factor = mp.sqrt(mp.mpf(2) / (2*T_iso + 1))
    grouped = {0: defaultdict(mp.mpf), 2: defaultdict(mp.mpf)}
    rows = read_csv(matrix_csv)

    for row in rows:
        rank = int(row["rank"])
        if rank not in (0, 2) or int(row["isospin"]) != 0:
            continue
        np_, lp = orbital_n_l(int(row["Nprime"]), int(row["two_jprime"]))
        n, ell = orbital_n_l(int(row["N"]), int(row["two_j"]))
        rho = mp.mpf(row["coefficient"])
        angular = angular_exact(row, rank, dps)
        base = mp.sqrt(
            mp.factorial(np_ - 1) * mp.factorial(n - 1)
            * mp.gamma(np_ + lp + mp.mpf("0.5"))
            * mp.gamma(n + ell + mp.mpf("0.5"))
        )
        for r in range(n):
            for s in range(np_):
                c1 = mp.mpf((-1) ** (r+s)) / (
                    mp.factorial(r) * mp.factorial(s)
                    * mp.factorial(n - 1 - r) * mp.factorial(np_ - 1 - s)
                )
                c2 = mp.gamma(mp.mpf(ell + lp + rank + 2*r + 2*s + 3) / 2) / (
                    mp.gamma(ell + r + mp.mpf("1.5"))
                    * mp.gamma(lp + s + mp.mpf("1.5"))
                )
                a = mp.mpf(rank - lp - ell - 2*r - 2*s) / 2
                grouped[rank][a] += (
                    isoscalar_factor * rho * angular * base * c1 * c2
                )
    return {rank: dict(values) for rank, values in grouped.items()}


def amplitude_mp(q_gev: mp.mpf, rank: int, grouped, b_gev_inv: mp.mpf) -> mp.mpf:
    y = (q_gev * b_gev_inv / 2) ** 2
    prefactor = (
        mp.mpf(2) ** rank / mp.fac2(2*rank + 1)
        * y ** (mp.mpf(rank) / 2) * mp.exp(-y)
    )
    total = mp.mpf("0")
    b = mp.mpf(rank) + mp.mpf("1.5")
    for a, coefficient in grouped[rank].items():
        total += coefficient * mp.hyp1f1(a, b, y)
    return prefactor * total


def package_response_mp(
    A: int, q_gev: mp.mpf, grouped, b_gev_inv: mp.mpf
) -> mp.mpf:
    J_A = mp.mpf(str(GROUND_STATE_SPIN[A]))
    a0 = amplitude_mp(q_gev, 0, grouped, b_gev_inv)
    a2 = amplitude_mp(q_gev, 2, grouped, b_gev_inv)
    w00 = mp.mpf("0.25") * (a0*a0 + a2*a2)
    return 4*mp.pi/(2*J_A + 1)*w00


def load_grid_interpolators(path: Path):
    grouped: dict[int, list[dict[str, str]]] = {}
    for row in read_csv(path):
        grouped.setdefault(int(row["A"]), []).append(row)
    if set(grouped) != set(ISOTOPES):
        raise ValueError(f"Unexpected response-grid isotopes: {sorted(grouped)}")
    interpolators = {}
    for A, rows in grouped.items():
        q = np.asarray([float(row["q_GeV"]) for row in rows])
        R = np.asarray([float(row["R_equal_pn_normalized"]) for row in rows])
        if len(q) != 2401 or not np.all(np.diff(q) > 0):
            raise ValueError(f"Xe-{A} response grid must have 2401 increasing nodes")
        interpolators[A] = PchipInterpolator(q, R, extrapolate=False)
    return interpolators


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix-dir", type=Path, required=True)
    parser.add_argument("--response-csv", type=Path, required=True)
    parser.add_argument(
        "--selected-samples", type=Path,
        default=HERE / "input" / "afh_response_samples.csv",
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--dps", type=int, default=60)
    parser.add_argument("--max-q0-relative-error", type=float, default=5.0e-4)
    parser.add_argument("--max-pchip-archive-relative-error", type=float, default=5.0e-7)
    args = parser.parse_args()

    mp.mp.dps = args.dps
    interpolators = load_grid_interpolators(args.response_csv)
    archived_rows = read_csv(args.selected_samples)
    archived = {
        (int(row["A"]), float(row["ER_keV"])): float(row["R_A"])
        for row in archived_rows
    }
    output_rows = []
    q0_metadata = {}
    max_q0_relative_error = 0.0
    max_pchip_archive_relative_error = 0.0
    max_pchip_exact_relative_error = {"nist_nuclear": 0.0, "ame2020_nuclear": 0.0}

    for A in ISOTOPES:
        matrix_path = args.matrix_dir / f"afh_default_xe{A}_density_matrix.csv"
        grouped = build_grouped_coefficients(A, matrix_path, args.dps)
        b_fm = mp.sqrt(
            mp.mpf("41.467") /
            (45*mp.mpf(A)**(-mp.mpf(1)/3) - 25*mp.mpf(A)**(-mp.mpf(2)/3))
        )
        b_inv = b_fm * FM_TO_GEV_INV
        package_zero = package_response_mp(A, mp.mpf("0"), grouped, b_inv)
        expected_zero = mp.mpf(A*A) / 4
        q0_rel = abs(package_zero / expected_zero - 1)
        max_q0_relative_error = max(max_q0_relative_error, float(q0_rel))
        q0_metadata[str(A)] = {
            "matrix_entries": len(read_csv(matrix_path)),
            "J_A": GROUND_STATE_SPIN[A],
            "T_iso": abs(A / 2.0 - Z),
            "b_A_fm": mp.nstr(b_fm, 18),
            "package_R0": mp.nstr(package_zero, 22),
            "expected_A2_over_4": A*A/4,
            "relative_q0_error": float(q0_rel),
        }
        if q0_rel > mp.mpf(str(args.max_q0_relative_error)):
            raise ArithmeticError(f"Xe-{A} q=0 normalization failed: {float(q0_rel):.3e}")

        for scheme in MASS_SCHEMES:
            for ER_keV in ER_POINTS_KEV:
                mA = mp.mpf(str(isotope_mass_GeV(A, scheme)))
                ER = mp.mpf(str(ER_keV)) * mp.mpf("1e-6")
                q = mp.sqrt(2*mA*ER + ER*ER)
                package_R = package_response_mp(A, q, grouped, b_inv)
                direct_R = mp.mpf(A*A) * package_R / package_zero
                pchip_R = mp.mpf(str(float(interpolators[A](float(q)))))
                interpolation_rel = abs(pchip_R / direct_R - 1)
                max_pchip_exact_relative_error[scheme] = max(
                    max_pchip_exact_relative_error[scheme], float(interpolation_rel)
                )
                archived_R = archived.get((A, ER_keV)) if scheme == "nist_nuclear" else None
                pchip_archive_rel = None
                if archived_R is not None:
                    pchip_archive_rel = abs(float(pchip_R) / archived_R - 1.0)
                    max_pchip_archive_relative_error = max(
                        max_pchip_archive_relative_error, pchip_archive_rel
                    )
                output_rows.append({
                    "mass_scheme": scheme,
                    "A": A,
                    "ER_keV": ER_keV,
                    "mA_GeV": mp.nstr(mA, 18),
                    "q_exact_spatial_GeV": mp.nstr(q, 18),
                    "b_A_fm": mp.nstr(b_fm, 18),
                    "R_A_exact_q_mpmath": mp.nstr(direct_R, 25),
                    "R_A_PCHIP_2401_grid": mp.nstr(pchip_R, 25),
                    "PCHIP_vs_exact_relative_difference": float(interpolation_rel),
                    "R_A_archived_28_sample": "" if archived_R is None else archived_R,
                    "PCHIP_vs_archived_relative_difference": (
                        "" if pchip_archive_rel is None else pchip_archive_rel
                    ),
                })

    args.out_dir.mkdir(parents=True, exist_ok=True)
    response_path = args.out_dir / "afh_selected_exact_q_responses.csv"
    write_csv(response_path, output_rows)
    fold_interpolation_max = max(max_pchip_exact_relative_error.values())
    summary = {
        "method": "independent grouped finite-sum evaluation with 60-digit mpmath.hyp1f1",
        "reference_precision_decimal_digits": args.dps,
        "source": "AFH DMFormFactor v6.0 default density matrices extracted from official package",
        "source_archive_sha256": "4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727",
        "source_package_sha256": "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372",
        "isotopes": list(ISOTOPES),
        "mass_schemes": list(MASS_SCHEMES),
        "recoil_points_keV": list(ER_POINTS_KEV),
        "exact_q_response_rows": len(output_rows),
        "q0_normalization": q0_metadata,
        "max_q0_relative_error": max_q0_relative_error,
        "max_PCHIP_vs_archived_28_sample_relative_error_NIST": max_pchip_archive_relative_error,
        "max_PCHIP_vs_exact_q_relative_error_by_mass_scheme": max_pchip_exact_relative_error,
        "max_PCHIP_vs_exact_q_relative_error": fold_interpolation_max,
        "historical_sample_interpretation": (
            "The 28 archived R_A values are PCHIP interpolants from the historical "
            "2401-node grid, not direct AFH evaluations at the off-grid q values."
        ),
        "fold_interpolation_status": (
            "NOT_ACCEPTED_FOR_PRECISION_RATE_FOLD"
            if fold_interpolation_max > 5.0e-4 else "WITHIN_5E-4_DIAGNOSTIC"
        ),
        "response_table": response_path.name,
        "status": (
            "PASS" if (
                max_q0_relative_error <= args.max_q0_relative_error
                and max_pchip_archive_relative_error <= args.max_pchip_archive_relative_error
            ) else "FAIL"
        ),
        "limitations": [
            "This validates selected exact-q points, not the full continuous response curve.",
            "It is an independent high-precision Python finite-sum evaluation, not a native Mathematica execution.",
            "The 2401-node PCHIP interpolation remains unsuitable for a precision fold at points where its residual exceeds the stated threshold.",
        ],
    }
    summary_path = args.out_dir / "afh_selected_q_mpmath_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __!__ == "__main__":
    main()
