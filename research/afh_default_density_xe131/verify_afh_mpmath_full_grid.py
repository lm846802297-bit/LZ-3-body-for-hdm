#!/usr/bin/env python3
"""Independent 60-digit mpmath check of the full AFH Xe-131 response grid.

The reference implementation reorganizes the finite BesselElement sums by
hypergeometric parameter before evaluation. It does not call SciPy's hyp1f1
or the Python runner's BesselElement implementation.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import mpmath as mp
from sympy import Integer, Rational, pi, simplify, N as symN
from sympy.physics.wigner import wigner_3j, wigner_6j

A, Z, J_A, T_ISO = 131, 54, 1.5, 11.5
B_GEV_INV = "11.61690053236942"


def orbital_n_l(Nprincipal: int, two_j: int) -> tuple[int, int]:
    jph = (two_j + 1) // 2
    ell = jph if (Nprincipal - jph) % 2 == 0 else jph - 1
    n = (Nprincipal - ell) // 2 + 1
    if n < 1:
        raise ValueError("invalid AFH oscillator orbital")
    return n, ell


def angular_exact(row: dict[str, str], rank: int, dps: int) -> mp.mpf:
    _, ell = orbital_n_l(int(row["N"]), int(row["two_j"]))
    _, lp = orbital_n_l(int(row["Nprime"]), int(row["two_jprime"]))
    jp = Rational(int(row["two_jprime"]), 2)
    jn = Rational(int(row["two_j"]), 2)
    J = Integer(rank)
    phase = (-1) ** (Rational(1, 2) + jn + J)
    prefactor = mp.mpf(str(symN(simplify(
        ((2*jn+1)*(2*jp+1)*(2*ell+1)*(2*lp+1)*(2*J+1)/(4*pi))**Rational(1,2)
    ), dps + 12)))
    w3 = mp.mpf(str(symN(wigner_3j(Integer(lp), J, Integer(ell), 0, 0, 0), dps + 12)))
    w6 = mp.mpf(str(symN(wigner_6j(Integer(lp), jp, Rational(1,2),
                                    jn, Integer(ell), J), dps + 12)))
    phase_mp = mp.mpf(str(symN(phase, dps + 12)))
    return phase_mp * prefactor * w3 * w6


def build_grouped_coefficients(matrix_csv: Path, dps: int):
    mp.mp.dps = dps
    grouped = {0: defaultdict(mp.mpf), 2: defaultdict(mp.mpf)}
    isoscalar_factor = mp.sqrt(mp.mpf(2) / (2 * mp.mpf(str(T_ISO)) + 1))
    with matrix_csv.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

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
                grouped[rank][a] += isoscalar_factor * rho * angular * base * c1 * c2

    return {rank: dict(values) for rank, values in grouped.items()}


def amplitude_mp(q_gev: str, rank: int, grouped, b_gev_inv: mp.mpf) -> mp.mpf:
    q = mp.mpf(q_gev)
    y = (q * b_gev_inv / 2) ** 2
    prefactor = (
        mp.mpf(2) ** rank / mp.fac2(2*rank + 1)
        * y ** (mp.mpf(rank) / 2) * mp.exp(-y)
    )
    total = mp.mpf("0")
    b = mp.mpf(rank) + mp.mpf("1.5")
    for a, coefficient in grouped[rank].items():
        total += coefficient * mp.hyp1f1(a, b, y)
    return prefactor * total


def read_response(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 2401:
        raise ValueError(f"expected 2401 response rows, got {len(rows)}")
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix-csv", type=Path,
                        default=Path(__file__).resolve().parent / "input" / "afh_default_xe131_density_matrix.csv")
    parser.add_argument("--response-csv", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--dps", type=int, default=60)
    parser.add_argument("--amplitude-absolute-tolerance", type=float, default=2e-10)
    parser.add_argument("--response-absolute-over-A2-tolerance", type=float, default=2e-11)
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    mp.mp.dps = args.dps
    grouped = build_grouped_coefficients(args.matrix_csv, args.dps)
    b = mp.mpf(B_GEV_INV)
    rows = read_response(args.response_csv)

    reference = []
    for row in rows:
        q = row["q_GeV"]
        a0 = amplitude_mp(q, 0, grouped, b)
        a2 = amplitude_mp(q, 2, grouped, b)
        w00 = mp.mpf("0.25") * (a0*a0 + a2*a2)
        r_package = (4*mp.pi/(2*mp.mpf(str(J_A))+1))*w00
        reference.append((a0, a2, r_package))

    r0 = reference[0][2]
    if r0 <= 0:
        raise ArithmeticError("mpmath q=0 response is non-positive")

    out_rows = []
    max_abs_amp = mp.mpf("0")
    max_rel_amp = mp.mpf("0")
    max_abs_r_over_a2 = mp.mpf("0")
    max_rel_r = mp.mpf("0")
    for row, (a0_mp, a2_mp, r_mp) in zip(rows, reference):
        a0_py = mp.mpf(row["rank0_amplitude"])
        a2_py = mp.mpf(row["rank2_amplitude"])
        r_py = mp.mpf(row["R_equal_pn_normalized"])
        r_phys_mp = mp.mpf(A*A) * r_mp / r0
        d0 = abs(a0_py - a0_mp)
        d2 = abs(a2_py - a2_mp)
        dr = abs(r_py - r_phys_mp)
        max_abs_amp = max(max_abs_amp, d0, d2)
        if abs(a0_mp) > mp.mpf("1e-10"):
            max_rel_amp = max(max_rel_amp, d0/abs(a0_mp))
        if abs(a2_mp) > mp.mpf("1e-10"):
            max_rel_amp = max(max_rel_amp, d2/abs(a2_mp))
        max_abs_r_over_a2 = max(max_abs_r_over_a2, dr/mp.mpf(A*A))
        if r_phys_mp > mp.mpf("1e-12"):
            max_rel_r = max(max_rel_r, dr/abs(r_phys_mp))
        out_rows.append({
            "q_GeV": q,
            "rank0_python": row["rank0_amplitude"],
            "rank0_mpmath": mp.nstr(a0_mp, 25),
            "rank0_abs_diff": mp.nstr(d0, 12),
            "rank2_python": row["rank2_amplitude"],
            "rank2_mpmath": mp.nstr(a2_mp, 25),
            "rank2_abs_diff": mp.nstr(d2, 12),
            "R_equal_pn_python": row["R_equal_pn_normalized"],
            "R_equal_pn_mpmath": mp.nstr(r_phys_mp, 25),
            "R_abs_diff": mp.nstr(dr, 12),
        })

    with (args.outdir / "full_grid_mpmath_comparison.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0]))
        writer.writeheader()
        writer.writerows(out_rows)

    summary = {
        "method": "independent grouped finite-sum evaluation with mpmath.hyp1f1",
        "reference_precision_decimal_digits": args.dps,
        "grid_points": len(rows),
        "density_matrix_entries_used": 24,
        "multipoles": [0, 2],
        "max_absolute_amplitude_difference": float(max_abs_amp),
        "max_relative_amplitude_difference_where_abs_reference_gt_1e-10": float(max_rel_amp),
        "max_absolute_response_difference_over_A2": float(max_abs_r_over_a2),
        "max_relative_response_difference_where_R_over_A2_gt_1e-12": float(max_rel_r),
        "amplitude_absolute_tolerance": args.amplitude_absolute_tolerance,
        "response_absolute_over_A2_tolerance": args.response_absolute_over_A2_tolerance,
        "status": "pass" if (
            max_abs_amp <= mp.mpf(str(args.amplitude_absolute_tolerance))
            and max_abs_r_over_a2 <= mp.mpf(str(args.response_absolute_over_A2_tolerance))
        ) else "fail",
        "scope": "full 2401-point Xe-131 grid; same AFH finite-sum definition and rounded source density matrix; not a native Mathematica comparison",
    }
    (args.outdir / "full_grid_mpmath_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    if summary["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
