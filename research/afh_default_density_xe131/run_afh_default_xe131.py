#!/usr/bin/env python3
"""Reproduce AFH DMFormFactor v6.0 default Xe-131 W_M^{00} response.

Input: the 67-entry built-in sdgXe131 matrix extracted from AFH's v6.0
distribution. Optionally pass the official dmformfactor-V6.m to verify the
extracted matrix byte-for-byte at the parsed-entry level. The script
translates the package's M_J radial/angular matrix-element formula and
ResponseNuclear normalization into Python.

This is intentionally not a dmscatter/GCN/JJ55 calculation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path
from functools import lru_cache

import numpy as np
from scipy.special import hyp1f1, factorial2
from scipy.interpolate import PchipInterpolator
from scipy.signal import find_peaks
from scipy.optimize import minimize_scalar
from sympy import Rational, Integer, pi, sqrt, simplify, N as symN
from sympy.physics.wigner import wigner_3j, wigner_6j

A, Z = 131, 54
J_A = 1.5
M_N_GEV = 0.93149410242
FM_TO_GEV_INV_AFH = 5.0677  # exact constant in AFH v6 source
Q_MAX_GEV = 0.60
Q_STEP_GEV = 0.00025
FIGURE2_DIPS_KEV = (101.0, 267.0, 542.0)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def parse_xe131_density_matrix(package_path: Path) -> list[dict]:
    text = package_path.read_text(encoding="utf-8", errors="strict")
    start = text.find("sdgXe131[1]")
    end = text.find("sdgXe131length", start)
    if start < 0 or end < 0:
        raise RuntimeError("Could not find built-in sdgXe131 density matrix")
    block = text[start:end]
    pattern = re.compile(
        r"sdgXe131\[(\d+)\]=\{[^=]+?=([-+0-9.]+),"
        r"(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\};"
    )
    rows = []
    for m in pattern.finditer(block):
        idx, coeff, rank, tau, Np, two_jp, Nn, two_jn = m.groups()
        rows.append({
            "index": int(idx), "coefficient": float(coeff),
            "rank": int(rank), "isospin": int(tau),
            "Nprime": int(Np), "two_jprime": int(two_jp),
            "N": int(Nn), "two_j": int(two_jn),
        })
    if len(rows) != 67:
        raise RuntimeError(f"Expected 67 sdgXe131 entries, parsed {len(rows)}")
    return rows


def read_density_matrix_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = []
        for r in csv.DictReader(f):
            rows.append({
                "index": int(r["index"]),
                "coefficient": float(r["coefficient"]),
                "rank": int(r["rank"]),
                "isospin": int(r["isospin"]),
                "Nprime": int(r["Nprime"]),
                "two_jprime": int(r["two_jprime"]),
                "N": int(r["N"]),
                "two_j": int(r["two_j"]),
            })
    if len(rows) != 67:
        raise RuntimeError(f"Expected 67 density-matrix entries, read {len(rows)}")
    return rows


def orbital_n_l(Nprincipal: int, two_j: int) -> tuple[int, int]:
    # AFH: Lnumber[N,j] = j+1/2 if N-(j+1/2) is even, otherwise j-1/2.
    j_plus_half = (two_j + 1) // 2
    ell = j_plus_half if (Nprincipal - j_plus_half) % 2 == 0 else j_plus_half - 1
    n_radial = (Nprincipal - ell) // 2 + 1
    if n_radial < 1:
        raise ValueError("Invalid AFH oscillator orbital")
    return n_radial, ell


@lru_cache(maxsize=None)
def angular_mj(Np: int, two_jp: int, Nn: int, two_jn: int, rank: int) -> float:
    np_, lp = orbital_n_l(Np, two_jp)
    n, ell = orbital_n_l(Nn, two_jn)
    jp, jn, J = Rational(two_jp, 2), Rational(two_jn, 2), Integer(rank)
    phase = (-1) ** (Rational(1, 2) + jn + J)
    prefactor = sqrt(
        (2*jn + 1) * (2*jp + 1) * (2*ell + 1) * (2*lp + 1) *
        (2*J + 1) / (4*pi)
    )
    value = (
        phase * prefactor *
        wigner_3j(Integer(lp), J, Integer(ell), 0, 0, 0) *
        wigner_6j(Integer(lp), jp, Rational(1, 2), jn, Integer(ell), J)
    )
    return float(symN(simplify(value), 30))


def bessel_element(y: float, np_: int, lp: int, n: int, ell: int, rank: int) -> float:
    # Literal translation of BesselElement in dmformfactor-V6.m.
    if y == 0.0 and rank > 0:
        return 0.0
    f1 = (
        (2.0 ** rank) / float(factorial2(2*rank + 1)) *
        (y ** (rank / 2.0)) * math.exp(-y) *
        math.sqrt(math.factorial(np_ - 1) * math.factorial(n - 1))
    )
    f2 = math.sqrt(
        math.gamma(np_ + lp + 0.5) * math.gamma(n + ell + 0.5)
    )
    total = 0.0
    for m in range(n):
        for mp in range(np_):
            s1 = ((-1.0) ** (m + mp)) / (
                math.factorial(m) * math.factorial(mp) *
                math.factorial(n - 1 - m) * math.factorial(np_ - 1 - mp)
            )
            s2 = math.gamma((ell + lp + rank + 2*m + 2*mp + 3) / 2.0) / (
                math.gamma(ell + m + 1.5) * math.gamma(lp + mp + 1.5)
            )
            a = (rank - lp - ell - 2*mp - 2*m) / 2.0
            total += s1 * s2 * hyp1f1(a, rank + 1.5, y)
    return f1 * f2 * total


def compute_amplitude(q_GeV: float, rank: int, rows: list[dict],
                      b_GeV_inv: float, T_iso: float) -> float:
    y = (q_GeV * b_GeV_inv / 2.0) ** 2
    # Isoscalar coefficient appearing in the AFH source's Response[].
    isoscalar_reduced_factor = math.sqrt(2.0 / (2.0*T_iso + 1.0))
    amplitude = 0.0
    for r in rows:
        if r["rank"] != rank or r["isospin"] != 0:
            continue
        np_, lp = orbital_n_l(r["Nprime"], r["two_jprime"])
        n, ell = orbital_n_l(r["N"], r["two_j"])
        ang = angular_mj(r["Nprime"], r["two_jprime"],
                         r["N"], r["two_j"], rank)
        radial = bessel_element(y, np_, lp, n, ell, rank)
        amplitude += (
            r["coefficient"] * isoscalar_reduced_factor * ang * radial
        )
    return amplitude


def package_w00(q_GeV: float, rows: list[dict], b_GeV_inv: float,
                T_iso: float) -> tuple[float, dict[int, float]]:
    # AFH ResponseNuclear[y,1,0,0]:
    # e^(-2y) * (2J_A+1)/(4pi) * 1/4 * sum(FF_pp+FF_nn+FF_pn+FF_np).
    # The e^(+y) in Response[] cancels e^(-2y) after the squared matrix
    # elements are formed, leaving W00 = 1/4 sum_rank amplitude_rank^2.
    amps = {
        rank: compute_amplitude(q_GeV, rank, rows, b_GeV_inv, T_iso)
        for rank in (0, 2)
    }
    return 0.25 * sum(v*v for v in amps.values()), amps


def recoil_keV(q_GeV: float, mass_GeV: float) -> float:
    return (math.sqrt(mass_GeV*mass_GeV + q_GeV*q_GeV) - mass_GeV) * 1e6


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--afh-package", type=Path, default=None,
                        help="Optional official dmformfactor-V6.m for provenance re-parse")
    parser.add_argument("--density-matrix-csv", type=Path,
                        default=Path(__file__).with_name("afh_default_xe131_density_matrix.csv"),
                        help="Extracted built-in sdgXe131 67-entry matrix")
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    matrix_csv = args.density_matrix_csv.resolve()
    rows = read_density_matrix_csv(matrix_csv)
    source = args.afh_package.resolve() if args.afh_package else None
    source_file_sha = None
    if source is not None:
        source_text = source.read_text(encoding="utf-8", errors="strict")
        if "Welcome to DMFormFactor version 1.1." not in source_text:
            raise RuntimeError("Unexpected AFH package footer/version marker")
        parsed_rows = parse_xe131_density_matrix(source)
        if parsed_rows != rows:
            raise RuntimeError("Extracted CSV does not match official AFH source matrix")
        source_file_sha = sha256(source)

    # Exact default formula and unit conversion used by SetIsotope in AFH v6.
    b_fm = math.sqrt(41.467 / (45*A**(-1/3) - 25*A**(-2/3)))
    b_GeV_inv = b_fm * FM_TO_GEV_INV_AFH
    T_iso = abs(A/2.0 - Z)
    q_grid = np.arange(round(Q_MAX_GEV/Q_STEP_GEV) + 1) * Q_STEP_GEV
    mass_GeV = A * M_N_GEV

    records = []
    amp_cache = {0: [], 2: []}
    for q in q_grid:
        W00, amps = package_w00(float(q), rows, b_GeV_inv, T_iso)
        W00_norm = 4*math.pi/(2*J_A+1)*W00
        for rank in (0, 2):
            amp_cache[rank].append(amps[rank])
        records.append({
            "q_GeV": float(q),
            "y": (float(q)*b_GeV_inv/2.0)**2,
            "ER_keV": recoil_keV(float(q), mass_GeV),
            "W_M00_AFH_package": W00,
            "R_AFH_package_4pi_over_2Jplus1": W00_norm,
            "rank0_amplitude": amps[0],
            "rank2_amplitude": amps[2],
        })

    package_zero = records[0]["R_AFH_package_4pi_over_2Jplus1"]
    expected_package_zero = A*A/4.0
    package_zero_relerr = abs(package_zero/expected_package_zero - 1.0)
    if package_zero_relerr > 2e-4:
        raise RuntimeError(
            f"AFH package normalization outside rounded-matrix tolerance: "
            f"{package_zero_relerr:.3e}"
        )

    # Equal proton/neutron coupling is four times the AFH isoscalar-isospin
    # response, because the AFH isoscalar nucleon operator carries 1/2.
    # Normalize the rounded built-in density matrix to the exact q=0 charge.
    shape = np.array([r["R_AFH_package_4pi_over_2Jplus1"] for r in records])
    R_equal_raw = 4.0 * shape
    normalization = (A*A) / R_equal_raw[0]
    R_equal = R_equal_raw * normalization
    for i, r in enumerate(records):
        r["R_equal_pn_raw"] = float(R_equal_raw[i])
        r["R_equal_pn_normalized"] = float(R_equal[i])
        r["R_equal_J0_normalized"] = float(normalization * math.pi * amp_cache[0][i]**2)
        r["R_equal_J2_normalized"] = float(normalization * math.pi * amp_cache[2][i]**2)
        r["R_over_A2"] = float(R_equal[i]/(A*A))
        r["A0_normalization_factor"] = float(normalization)

    csv_path = args.outdir / "afh_default_xe131_WM00.csv"
    fields = list(records[0].keys())
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)

    # Locate minima of the physical equal-pn normalized response using PCHIP
    # and then refine against the direct AFH-translated kernel.
    q_arr = q_grid
    R_arr = R_equal
    peaks, _ = find_peaks(-R_arr, prominence=A*A*1e-8, distance=10)
    interp = PchipInterpolator(q_arr, R_arr)
    minima = []
    for idx in peaks:
        if not (0.08 <= q_arr[idx] <= 0.50):
            continue
        def direct_equal_response(q: float) -> float:
            W00, _ = package_w00(float(q), rows, b_GeV_inv, T_iso)
            package_R = 4*math.pi/(2*J_A+1)*W00
            return A*A*package_R/package_zero
        res = minimize_scalar(
            direct_equal_response,
            bounds=(q_arr[idx-1], q_arr[idx+1]),
            method="bounded",
            options={"xatol": 1e-14},
        )
        qmin = float(res.x)
        _, amps_min = package_w00(qmin, rows, b_GeV_inv, T_iso)
        minima.append({
            "q_min_MeV": qmin*1000.0,
            "ER_min_keV": recoil_keV(qmin, mass_GeV),
            "R_over_A2": float(res.fun/(A*A)),
            "rank0_amplitude": float(amps_min[0]),
            "rank2_amplitude": float(amps_min[2]),
        })

    dip_checks = []
    for E in (101.0, 267.0, 542.0):
        q = math.sqrt(2*mass_GeV*E*1e-6 + (E*1e-6)**2)
        W00_at_q, _ = package_w00(q, rows, b_GeV_inv, T_iso)
        package_R_at_q = 4*math.pi/(2*J_A+1)*W00_at_q
        value = A*A*package_R_at_q/package_zero
        dip_checks.append({
            "figure2_ER_keV": E, "q_MeV": q*1000.0,
            "R_over_A2": value/(A*A),
        })

    meta = {
        "source_archive": "AFH DMFormFactor v6.0",
        "source_file": source.name if source else "afh_default_xe131_density_matrix.csv extracted from official AFH v6.0",
        "source_file_sha256": source_file_sha if source_file_sha else None,
        "density_matrix_csv_sha256": sha256(matrix_csv),
        "source_zip_sha256": "4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727",
        "source_density_matrix": "built-in sdgXe131, 67 entries",
        "source_selection": 'SetIsotope[54,131,"default","default"]',
        "source_response_function": "ResponseNuclear[y,1,0,0]",
        "source_response_definition": "AFH W_M^{00}(y)",
        "source_response_convention": "AFH isoscalar convention c0=(cp+cn)/2; R_AFH(0)=A^2/4",
        "physical_equal_proton_neutron_response": "R_equal=4*(4*pi/(2J_A+1))*W_M_AFH^{00}",
        "normalization_convention": "R_equal(q)=A^2*R_AFH(q)/R_AFH(0), preserving AFH shape and enforcing R_equal(0)=A^2",
        "A": A, "Z": Z, "J_A": J_A, "T_iso": T_iso,
        "b_A_fm": b_fm, "AFH_femtometer_GeV_inverse": FM_TO_GEV_INV_AFH,
        "b_A_GeV_inverse": b_GeV_inv,
        "AFH_package_R0": package_zero,
        "expected_AFH_package_R0_A2_over_4": expected_package_zero,
        "AFH_package_R0_relative_error": package_zero_relerr,
        "equal_pn_normalization_factor_for_rounded_density": normalization,
        "physical_R0": float(R_equal[0]), "A_squared": A*A,
        "q_grid_GeV": [0.0, Q_MAX_GEV, Q_STEP_GEV],
        "recoil_mass_convention_GeV": mass_GeV,
        "nuclear_response_only": True,
        "no_three_body_integral_or_halo_fold": True,
        "minima": minima,
        "figure2_dip_energy_checks": dip_checks,
        "limitations": [
            "AFH built-in density-matrix coefficients are printed to finite decimal precision; the q=0 package response differs from A^2/4 at the 8e-5 level.",
            "The exact A^2 normalization is imposed by dividing by the computed q=0 response; this changes only the overall normalization, not the response shape.",
            "This is the nuclear response only; it is not yet the full three-body cross section or natural-xenon event rate.",
            "The manuscript's stated R_A(0)=A^2 must be checked against the AFH isoscalar factor-of-four convention before finalizing the equation."
        ],
    }
    (args.outdir/"metadata.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")
    with (args.outdir/"minima.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(minima[0].keys()))
        w.writeheader(); w.writerows(minima)
    with (args.outdir/"figure2_dip_check.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(dip_checks[0].keys()))
        w.writeheader(); w.writerows(dip_checks)

    lines = [
        "# AFH DMFormFactor v6.0 default Xe-131 response",
        "",
        "## Input and convention",
        "",
        "The input is the built-in `sdgXe131` default density matrix (67 entries), selected by SetIsotope with Z=54, A=131, b=default, filename=default. The oscillator length is the AFH default formula and the AFH source uses Femtometer=5.0677/GeV.",
        "",
        "The package returns `ResponseNuclear[y,1,0,0] = W_M^{00}`. In the AFH isoscalar convention, its normalized zero-momentum response is A^2/4, not A^2. For equal physical proton and neutron couplings, the coherent response is four times the AFH isoscalar-normalized response. The density matrix's finite decimal precision gives a small q=0 deviation, removed by normalizing the shape to the exact A^2 charge.",
        "",
        "## Zero-momentum normalization",
        "",
        f"- AFH package: {package_zero:.9f}",
        f"- Expected AFH package value A^2/4: {expected_package_zero:.9f}",
        f"- Relative difference: {package_zero_relerr:.3e}",
        f"- Equal-pn response after shape normalization: {R_equal[0]:.9f}",
        f"- A^2: {A*A}",
        f"- Shape normalization factor: {normalization:.10f}",
        "",
        "## AFH default b_A",
        "",
        f"- b_A = {b_fm:.10f} fm",
        f"- b_A = {b_GeV_inv:.10f} GeV^-1",
        "",
        "## Response minima",
        "",
        "| q_min [MeV] | E_R,min [keV] | R/A^2 |",
        "|---:|---:|---:|",
    ]
    for m in minima:
        lines.append(f"| {m['q_min_MeV']:.5f} | {m['ER_min_keV']:.5f} | {m['R_over_A2']:.6e} |")
    lines += ["", "## Figure 2 recoil-energy points", "",
              "| E_R [keV] | q [MeV] | R/A^2 |", "|---:|---:|---:|"]
    for d in dip_checks:
        lines.append(f"| {d['figure2_ER_keV']:.1f} | {d['q_MeV']:.5f} | {d['R_over_A2']:.6e} |")
    lines += [
        "", "## Scope and caution", "",
        "This result is only the AFH default Xe-131 nuclear response. It is not the complete three-body differential cross section, not a halo-folded spectrum, and not a natural-xenon rate. The manuscript's equation identifying `4 pi W_M^{00}/(2J_A+1)` directly with a response normalized to A^2 must be corrected or its W convention explicitly redefined by a factor of four.",
        "",
        "The GCN/JJ55 results previously archived from dmscatter are separate nuclear-structure calculations and are not substituted here."
    ]
    (args.outdir/"RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

    # Save a simple machine-readable run summary.
    print(json.dumps({
        "b_A_fm": b_fm, "b_A_GeV_inverse": b_GeV_inv,
        "AFH_package_R0": package_zero,
        "AFH_expected_R0": expected_package_zero,
        "AFH_R0_relerr": package_zero_relerr,
        "physical_R0": float(R_equal[0]), "A2": A*A,
        "normalization_factor": normalization,
        "minima": minima, "figure2_dip_checks": dip_checks,
        "csv": str(csv_path),
    }, indent=2))


if __name__ == "__main__":
    main()

