#!/usr/bin/env python3
"""AFH v6.0 source-translated Delta, Sigma', and Sigma'-Delta OBDME responses.

The implementation follows the AFH v6.0 definitions of BesselElementMinus,
BesselElementPlus, MJLDivQ, MJLSigma, DeltaJ, and SigmaPJ. It evaluates the
available default xenon OBDME tables. It is deliberately labelled
source-translated until checked against a native Mathematica spatial-response
export.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.special import factorial2, hyp1f1
from sympy import Integer, Rational
from sympy.physics.wigner import wigner_3j, wigner_6j, wigner_9j

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MATRIX_ROOT = (
    ROOT / "research" / "afh_default_density_natural_xenon_halo"
    / "results" / "full_afh_v6_default_7_isotope_response" / "density_matrices"
)
META_PATH = (
    ROOT / "research" / "afh_default_density_natural_xenon_halo"
    / "results" / "full_afh_v6_default_7_isotope_response" / "metadata.json"
)
Q_MAX_GEV = 0.60
Q_STEP_GEV = 0.00025
ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
AFH_XE131_DIR = ROOT / "research" / "afh_default_density_xe131"
if str(AFH_XE131_DIR) not in sys.path:
    sys.path.insert(0, str(AFH_XE131_DIR))
from run_afh_default_xe131 import (  # noqa: E402
    bessel_element,
    orbital_n_l,
    package_w00,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_density_matrix(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as stream:
        rows = []
        for row in csv.DictReader(stream):
            rows.append({
                "index": int(row["index"]),
                "coefficient": float(row["coefficient"]),
                "rank": int(row["rank"]),
                "isospin": int(row["isospin"]),
                "Nprime": int(row["Nprime"]),
                "two_jprime": int(row["two_jprime"]),
                "N": int(row["N"]),
                "two_j": int(row["two_j"]),
            })
    if not rows or [r["index"] for r in rows] != list(range(1, len(rows) + 1)):
        raise ValueError(f"invalid AFH density matrix: {path}")
    return rows


@lru_cache(maxsize=None)
def _w3(j1: int, j2: int, j3: int) -> float:
    try:
        return float(wigner_3j(Integer(j1), Integer(j2), Integer(j3), 0, 0, 0))
    except ValueError:
        return 0.0


@lru_cache(maxsize=None)
def _w6(a: int, b: int, c: int, d: int, e: int, f: int) -> float:
    try:
        return float(wigner_6j(Integer(a), Integer(b), Integer(c),
                               Integer(d), Integer(e), Integer(f)))
    except ValueError:
        return 0.0


@lru_cache(maxsize=None)
def _w9(lp: int, l: int, lcap: int, two_jp: int, two_j: int, J: int) -> float:
    try:
        return float(wigner_9j(
            Integer(lp), Integer(l), Integer(lcap),
            Rational(1, 2), Rational(1, 2), Integer(1),
            Rational(two_jp, 2), Rational(two_j, 2), Integer(J),
        ))
    except ValueError:
        return 0.0


def _radial_common(y: float, np_: int, lp: int, n: int, ell: int, lcap: int):
    if lcap < 1:
        raise ValueError("BesselElementMinus/Plus requires lcap >= 1")
    if y < 0.0 or not math.isfinite(y):
        raise ValueError("y must be finite and nonnegative")
    if y == 0.0 and lcap > 1:
        return 0.0
    f1 = (
        (2.0 ** (lcap - 1))
        / float(factorial2(2 * lcap + 1, exact=False))
        * (y ** ((lcap - 1) / 2.0))
        * math.exp(-y)
        * math.sqrt(math.factorial(np_ - 1) * math.factorial(n - 1))
    )
    f2 = math.sqrt(
        math.gamma(np_ + lp + 0.5) * math.gamma(n + ell + 0.5)
    )
    return f1 * f2


@lru_cache(maxsize=300000)
def bessel_element_minus(
    y: float, np_: int, lp: int, n: int, ell: int, lcap: int
) -> float:
    """Literal translation of AFH BesselElementMinus."""
    common = _radial_common(y, np_, lp, n, ell, lcap)
    if common == 0.0:
        return 0.0
    total = 0.0
    b = lcap + 1.5
    for m in range(n):
        for mp in range(np_):
            sign_factor = ((-1.0) ** (m + mp)) / (
                math.factorial(m) * math.factorial(mp)
                * math.factorial(n - 1 - m) * math.factorial(np_ - 1 - mp)
            )
            gamma_factor = math.gamma(
                (ell + lp + lcap + 2 * m + 2 * mp + 2) / 2.0
            ) / (
                math.gamma(ell + m + 1.5)
                * math.gamma(lp + mp + 1.5)
            )
            a = (lcap - lp - ell - 2 * mp - 2 * m - 1) / 2.0
            base = (ell + lp + lcap + 2 * m + 2 * mp + 2) / 2.0
            derivative_factor = (
                -base * float(hyp1f1(a, b, y))
                + 2.0 * m * float(hyp1f1(a + 1.0, b, y))
            )
            total += sign_factor * gamma_factor * derivative_factor
    return float(common * total)


@lru_cache(maxsize=300000)
def bessel_element_plus(
    y: float, np_: int, lp: int, n: int, ell: int, lcap: int
) -> float:
    """Literal translation of AFH BesselElementPlus."""
    common = _radial_common(y, np_, lp, n, ell, lcap)
    if common == 0.0:
        return 0.0
    total = 0.0
    b = lcap + 1.5
    for m in range(n):
        for mp in range(np_):
            sign_factor = ((-1.0) ** (m + mp)) / (
                math.factorial(m) * math.factorial(mp)
                * math.factorial(n - 1 - m) * math.factorial(np_ - 1 - mp)
            )
            gamma_factor = math.gamma(
                (ell + lp + lcap + 2 * m + 2 * mp + 2) / 2.0
            ) / (
                math.gamma(ell + m + 1.5)
                * math.gamma(lp + mp + 1.5)
            )
            a = (lcap - lp - ell - 2 * mp - 2 * m - 1) / 2.0
            base = (ell + lp + lcap + 2 * m + 2 * mp + 2) / 2.0
            derivative_factor = (
                -base * float(hyp1f1(a, b, y))
                + (2.0 * ell + 2.0 * m + 1.0)
                * float(hyp1f1(a + 1.0, b, y))
            )
            total += sign_factor * gamma_factor * derivative_factor
    return float(common * total)


def _abnormal_allowed(
    Np: int, two_jp: int, N: int, two_j: int, J: int
) -> bool:
    np_, lp = orbital_n_l(Np, two_jp)
    n, ell = orbital_n_l(N, two_j)
    jp = two_jp / 2.0
    j = two_j / 2.0
    if np_ < 1 or n < 1 or J < 0:
        return False
    if not (abs(j - jp) <= J <= j + jp):
        return False
    return ((-1) ** (lp + ell + J + 1)) == 1


def _mjl_div_q(
    y: float, np_: int, lp: int, two_jp: int,
    n: int, ell: int, two_j: int, J: int,
) -> float:
    """AFH MJLDivQ[...,jcap=J,lcap=J], used by DeltaJ."""
    if J < 1:
        return 0.0
    jp = Rational(two_jp, 2)
    j = Rational(two_j, 2)
    lcap = J
    try:
        six_outer = float(wigner_6j(
            Integer(lp), jp, Rational(1, 2),
            j, Integer(ell), Integer(J)
        ))
    except ValueError:
        return 0.0
    phase_power = int(lcap + j + Rational(1, 2))
    overall = (
        (-1.0) ** phase_power
        * math.sqrt(
            (2 * lp + 1) * (two_jp + 1) * (two_j + 1)
            * (2 * J + 1) * (2 * lcap + 1) / (4.0 * math.pi)
        )
        * six_outer
    )
    l_plus = ell + 1
    six_1 = _w6(lcap, 1, J, ell, lp, l_plus)
    three_1 = _w3(lp, lcap, l_plus)
    term1 = (
        -math.sqrt(ell + 1.0) * math.sqrt(2.0 * ell + 3.0)
        * six_1 * three_1
        * bessel_element_minus(y, np_, lp, n, ell, lcap)
    )
    term2 = 0.0
    if ell > 0:
        l_minus = ell - 1
        six_2 = _w6(lcap, 1, J, ell, lp, l_minus)
        three_2 = _w3(lp, lcap, l_minus)
        term2 = (
            math.sqrt(ell) * math.sqrt(2.0 * ell - 1.0)
            * six_2 * three_2
            * bessel_element_plus(y, np_, lp, n, ell, lcap)
        )
    return float(overall * (term1 + term2))


def _mjl_sigma(
    y: float, np_: int, lp: int, two_jp: int,
    n: int, ell: int, two_j: int, J: int, lcap: int,
) -> float:
    """AFH MJLSigma[...,jcap=J,lcap], used by SigmaPrime."""
    if lcap < 0:
        return 0.0
    jp = Rational(two_jp, 2)
    j = Rational(two_j, 2)
    six_nine = _w9(lp, ell, lcap, two_jp, two_j, J)
    three = _w3(lp, lcap, ell)
    if six_nine == 0.0 or three == 0.0:
        return 0.0
    phase = (-1.0) ** lp
    prefactor = (
        phase * math.sqrt(6.0)
        * math.sqrt(
            (two_j + 1) * (two_jp + 1)
            * (2 * ell + 1) * (2 * lp + 1)
            * (2 * J + 1) * (2 * lcap + 1)
            / (4.0 * math.pi)
        )
    )
    return float(
        prefactor * three * six_nine
        * bessel_element(y, np_, lp, n, ell, lcap)
    )


def delta_j_element(
    y: float, Np: int, two_jp: int, N: int, two_j: int, J: int
) -> float:
    if not _abnormal_allowed(Np, two_jp, N, two_j, J):
        return 0.0
    np_, lp = orbital_n_l(Np, two_jp)
    n, ell = orbital_n_l(N, two_j)
    return _mjl_div_q(y, np_, lp, two_jp, n, ell, two_j, J)


def sigma_prime_j_element(
    y: float, Np: int, two_jp: int, N: int, two_j: int, J: int
) -> float:
    if J < 1 or not _abnormal_allowed(Np, two_jp, N, two_j, J):
        return 0.0
    np_, lp = orbital_n_l(Np, two_jp)
    n, ell = orbital_n_l(N, two_j)
    first = -math.sqrt(J / (2.0 * J + 1.0)) * _mjl_sigma(
        y, np_, lp, two_jp, n, ell, two_j, J, J + 1
    )
    second = math.sqrt((J + 1.0) / (2.0 * J + 1.0)) * _mjl_sigma(
        y, np_, lp, two_jp, n, ell, two_j, J, J - 1
    )
    return float(first + second)


def isotope_spatial_response(
    q_GeV: float,
    A: int,
    rows: list[dict],
    J_A: float,
    T_iso: float,
    b_GeV_inv: float,
    common_matrix_normalization: float | None = None,
) -> dict:
    """Return package and physical equal-p/n Delta/Sigma' responses."""
    if q_GeV < 0.0 or not math.isfinite(q_GeV):
        raise ValueError("q_GeV must be finite and nonnegative")
    y = (q_GeV * b_GeV_inv / 2.0) ** 2
    isoscalar_factor = math.sqrt(2.0 / (2.0 * T_iso + 1.0))
    ranks = sorted({
        row["rank"] for row in rows
        if row["isospin"] == 0 and row["rank"] >= 1
    })
    amp_delta = {}
    amp_sigma = {}
    for J in ranks:
        if J < 1:
            continue
        a_delta = 0.0
        a_sigma = 0.0
        for row in rows:
            if row["isospin"] != 0 or row["rank"] != J:
                continue
            common = row["coefficient"] * isoscalar_factor
            a_delta += common * delta_j_element(
                y, row["Nprime"], row["two_jprime"],
                row["N"], row["two_j"], J
            )
            a_sigma += common * sigma_prime_j_element(
                y, row["Nprime"], row["two_jprime"],
                row["N"], row["two_j"], J
            )
        amp_delta[J] = float(a_delta)
        amp_sigma[J] = float(a_sigma)

    w_delta = 0.25 * sum(value * value for value in amp_delta.values())
    w_sigma = 0.25 * sum(value * value for value in amp_sigma.values())
    w_cross = 0.25 * sum(
        amp_sigma[J] * amp_delta[J] for J in amp_delta
    )
    bound = math.sqrt(max(0.0, w_delta) * max(0.0, w_sigma))
    cauchy_excess = max(0.0, abs(w_cross) - bound)
    if cauchy_excess > 2.0e-10 * max(abs(w_cross), bound, 1.0e-300):
        raise ArithmeticError(
            f"AFH Sigma'-Delta Cauchy bound failed for Xe-{A}: "
            f"excess={cauchy_excess:.6e}"
        )

    response_prefactor = 4.0 * math.pi / (2.0 * J_A + 1.0)
    package_delta = response_prefactor * w_delta
    package_sigma = response_prefactor * w_sigma
    package_cross = response_prefactor * w_cross

    # The common OBDME rounding correction is calibrated only from the
    # coherent M(q=0)=A^2 anchor; the isospin factor four is applied once.
    if common_matrix_normalization is None:
        w00, _ = package_w00(0.0, rows, b_GeV_inv, T_iso)
        package_m_zero = response_prefactor * w00
        if package_m_zero <= 0.0:
            raise ArithmeticError(f"nonpositive M(q=0) normalization for Xe-{A}")
        common_matrix_normalization = (A * A) / (4.0 * package_m_zero)
    physical_factor = 4.0 * common_matrix_normalization
    return {
        "A": A,
        "q_GeV": q_GeV,
        "y": y,
        "W_Delta_AFH_package": w_delta,
        "W_SigmaPrime_AFH_package": w_sigma,
        "W_SigmaPrimeDelta_AFH_package": w_cross,
        "R_Delta_equal_pn": physical_factor * package_delta,
        "R_SigmaPrime_equal_pn": physical_factor * package_sigma,
        "R_SigmaPrimeDelta_equal_pn": physical_factor * package_cross,
        "common_matrix_normalization": common_matrix_normalization,
        "Cauchy_excess": cauchy_excess,
        "rank_amplitudes_Delta": {str(k): v for k, v in amp_delta.items()},
        "rank_amplitudes_SigmaPrime": {str(k): v for k, v in amp_sigma.items()},
    }


def multipole_records_for_response(
    A: int, isotope: str, J_A: float, result: dict
) -> list[dict]:
    """Expand the total spatial responses into signed rank-by-rank records."""
    delta = result["rank_amplitudes_Delta"]
    sigma = result["rank_amplitudes_SigmaPrime"]
    ranks = sorted({int(k) for k in delta} | {int(k) for k in sigma})
    response_prefactor = 4.0 * math.pi / (2.0 * J_A + 1.0)
    physical_factor = 4.0 * float(result["common_matrix_normalization"])
    records = []
    for J in ranks:
        key = str(J)
        amp_delta = float(delta.get(key, 0.0))
        amp_sigma = float(sigma.get(key, 0.0))
        w_delta = 0.25 * amp_delta * amp_delta
        w_sigma = 0.25 * amp_sigma * amp_sigma
        w_cross = 0.25 * amp_sigma * amp_delta
        conversion = physical_factor * response_prefactor
        records.append({
            "A": A,
            "isotope": isotope,
            "J_A": J_A,
            "q_GeV": float(result["q_GeV"]),
            "y": float(result["y"]),
            "multipole_J": J,
            "M_Delta_J": amp_delta,
            "M_SigmaPrime_J": amp_sigma,
            "W_Delta_J_AFH_package": w_delta,
            "W_SigmaPrime_J_AFH_package": w_sigma,
            "W_SigmaPrimeDelta_J_AFH_package": w_cross,
            "R_Delta_J_equal_pn": conversion * w_delta,
            "R_SigmaPrime_J_equal_pn": conversion * w_sigma,
            "R_SigmaPrimeDelta_J_equal_pn": conversion * w_cross,
            "common_matrix_normalization": float(
                result["common_matrix_normalization"]
            ),
        })
    return records


def generate_grid(
    matrix_dir: Path = MATRIX_ROOT,
    metadata_path: Path = META_PATH,
    out_dir: Path | None = None,
    q_grid: np.ndarray | None = None,
) -> tuple[list[dict], dict]:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("source_file_sha256") != (
        "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372"
    ):
        raise RuntimeError("AFH v6.0 source hash does not match the pinned source")
    if q_grid is None:
        q_grid = np.arange(round(Q_MAX_GEV / Q_STEP_GEV) + 1) * Q_STEP_GEV
    if len(q_grid) != 2401 or abs(float(q_grid[-1]) - Q_MAX_GEV) > 1.0e-13:
        raise ValueError("expected canonical 2401-point q grid from 0 to 0.6 GeV")

    rows_out = []
    multipole_rows = []
    isotope_meta = []
    max_multipole_reconstruction_abs = {
        "W_Delta": 0.0,
        "W_SigmaPrime": 0.0,
        "W_SigmaPrimeDelta": 0.0,
        "R_Delta": 0.0,
        "R_SigmaPrime": 0.0,
        "R_SigmaPrimeDelta": 0.0,
    }
    multipole_ranks_by_isotope = {}
    for isotope in metadata["isotopes"]:
        A = int(isotope["A"])
        matrix_path = matrix_dir / f"afh_default_xe{A}_density_matrix.csv"
        rows = read_density_matrix(matrix_path)
        J_A = float(isotope["J_A"])
        T_iso = float(isotope["T_iso"])
        b = float(isotope["b_A_GeV_inverse"])
        response_prefactor = 4.0 * math.pi / (2.0 * J_A + 1.0)
        multipole_ranks = sorted({
            int(row["rank"]) for row in rows
            if row["isospin"] == 0 and row["rank"] >= 1
        })
        multipole_ranks_by_isotope[str(A)] = multipole_ranks
        w00, _ = package_w00(0.0, rows, b, T_iso)
        package_m_zero = response_prefactor * w00
        if package_m_zero <= 0.0:
            raise ArithmeticError(f"nonpositive M(q=0) normalization for Xe-{A}")
        common_normalization = (A * A) / (4.0 * package_m_zero)
        for q in q_grid:
            result = isotope_spatial_response(
                float(q), A, rows, J_A, T_iso, b,
                common_matrix_normalization=common_normalization,
            )
            rows_out.append({
                "A": A,
                "isotope": f"Xe-{A}",
                "J_A": J_A,
                "q_GeV": result["q_GeV"],
                "y": result["y"],
                "R_Delta_equal_pn": result["R_Delta_equal_pn"],
                "R_SigmaPrime_equal_pn": result["R_SigmaPrime_equal_pn"],
                "R_SigmaPrimeDelta_equal_pn": result["R_SigmaPrimeDelta_equal_pn"],
                "W_Delta_AFH_package": result["W_Delta_AFH_package"],
                "W_SigmaPrime_AFH_package": result["W_SigmaPrime_AFH_package"],
                "W_SigmaPrimeDelta_AFH_package": result["W_SigmaPrimeDelta_AFH_package"],
                "common_matrix_normalization": result["common_matrix_normalization"],
                "Cauchy_excess": result["Cauchy_excess"],
            })
            rank_records = multipole_records_for_response(
                A, f"Xe-{A}", J_A, result
            )
            multipole_rows.extend(rank_records)
            # Reconstruct all three raw and physical responses from the
            # retained rank amplitudes; this is an archive-integrity check.
            reconstructed = {
                "W_Delta": math.fsum(x["W_Delta_J_AFH_package"] for x in rank_records),
                "W_SigmaPrime": math.fsum(x["W_SigmaPrime_J_AFH_package"] for x in rank_records),
                "W_SigmaPrimeDelta": math.fsum(x["W_SigmaPrimeDelta_J_AFH_package"] for x in rank_records),
                "R_Delta": math.fsum(x["R_Delta_J_equal_pn"] for x in rank_records),
                "R_SigmaPrime": math.fsum(x["R_SigmaPrime_J_equal_pn"] for x in rank_records),
                "R_SigmaPrimeDelta": math.fsum(x["R_SigmaPrimeDelta_J_equal_pn"] for x in rank_records),
            }
            expected_responses = {
                "W_Delta": result["W_Delta_AFH_package"],
                "W_SigmaPrime": result["W_SigmaPrime_AFH_package"],
                "W_SigmaPrimeDelta": result["W_SigmaPrimeDelta_AFH_package"],
                "R_Delta": result["R_Delta_equal_pn"],
                "R_SigmaPrime": result["R_SigmaPrime_equal_pn"],
                "R_SigmaPrimeDelta": result["R_SigmaPrimeDelta_equal_pn"],
            }
            for name, reconstructed_value in reconstructed.items():
                residual = abs(reconstructed_value - expected_responses[name])
                max_multipole_reconstruction_abs[name] = max(
                    max_multipole_reconstruction_abs[name], residual
                )
                tolerance = 2.0e-14 + 2.0e-12 * max(
                    abs(reconstructed_value), abs(expected_responses[name])
                )
                if residual > tolerance:
                    raise ArithmeticError(
                        f"rank-summed {name} does not reconstruct total response "
                        f"for Xe-{A} q={float(q):.8g}: residual={residual:.6e}"
                    )
        isotope_meta.append({
            "A": A,
            "J_A": J_A,
            "matrix_entries": len(rows),
            "matrix_sha256": sha256_file(matrix_path),
            "common_matrix_normalization": common_normalization,
            "nonzero_abnormal_rank_count": len({
                row["rank"] for row in rows
                if row["isospin"] == 0 and row["rank"] > 0
            }),
        })

    result_meta = {
        "status": "PROVISIONAL_SOURCE_TRANSLATED_AFH_SPATIAL_RESPONSES",
        "source": "AFH DMFormFactor v6.0 source definitions",
        "source_file_sha256": metadata["source_file_sha256"],
        "response_channels": ["Delta", "SigmaPrime", "SigmaPrimeDelta"],
        "isotopes": [item["A"] for item in isotope_meta],
        "q_points_per_isotope": len(q_grid),
        "response_rows": len(rows_out),
        "physical_convention": (
            "equal-p/n isospin factor four applied once; common OBDME "
            "rounding normalization anchored to the M(q=0)=A^2 convention"
        ),
        "native_mathematica_spatial_crosscheck": False,
        "isotope_metadata": isotope_meta,
    }
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        csv_path = out_dir / "afh_spatial_obdme_responses_7isotope_2401.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows_out[0]))
            writer.writeheader()
            writer.writerows(rows_out)
        multipole_path = out_dir / "afh_spatial_obdme_multipoles_7isotope_2401.csv"
        multipole_fields = [
            "A", "isotope", "J_A", "q_GeV", "y", "multipole_J",
            "M_Delta_J", "M_SigmaPrime_J",
            "W_Delta_J_AFH_package", "W_SigmaPrime_J_AFH_package",
            "W_SigmaPrimeDelta_J_AFH_package",
            "R_Delta_J_equal_pn", "R_SigmaPrime_J_equal_pn",
            "R_SigmaPrimeDelta_J_equal_pn", "common_matrix_normalization",
        ]
        with multipole_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=multipole_fields)
            writer.writeheader()
            writer.writerows(multipole_rows)
        result_meta["response_file"] = csv_path.name
        result_meta["response_file_sha256"] = sha256_file(csv_path)
        result_meta["multipole_file"] = multipole_path.name
        result_meta["multipole_file_sha256"] = sha256_file(multipole_path)
        result_meta["multipole_rows"] = len(multipole_rows)
        result_meta["multipole_ranks_by_isotope"] = multipole_ranks_by_isotope
        result_meta["multipole_reconstruction_max_absolute_residual"] = (
            max_multipole_reconstruction_abs
        )
        result_meta["multipole_reconstruction_tolerance"] = (
            "2e-14 + 2e-12 * max(abs(rank_sum), abs(total_response))"
        )
        result_meta["rankwise_amplitudes_and_signed_interference_saved"] = True
        (out_dir / "metadata.json").write_text(
            json.dumps(result_meta, indent=2) + "\n", encoding="utf-8"
        )
    return rows_out, result_meta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix-dir", type=Path, default=MATRIX_ROOT)
    parser.add_argument("--metadata", type=Path, default=META_PATH)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    _, result = generate_grid(args.matrix_dir, args.metadata, args.out_dir)
    print(json.dumps({
        "status": result["status"],
        "rows": result["response_rows"],
        "native_mathematica_spatial_crosscheck": False,
        "output": str(args.out_dir),
    }, indent=2))


if __name__ == "__main__":
    main()
