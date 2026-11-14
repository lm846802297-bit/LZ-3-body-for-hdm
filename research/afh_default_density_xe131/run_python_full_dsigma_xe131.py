#!/usr/bin/env python3
"""Python-only full Xe-131 d sigma/dER calculation and AFH factor-four audit.

This runner does not invoke Mathematica/Wolfram. It evaluates the complete
Eq. (6) reduced three-body kernel in Python, interpolates the archived
source-translated AFH v6.0 response in exact spatial q, and assembles the
physical differential cross section with an explicit no-factor-four control.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "research" / "figure2_full_reproduction"))

import eq6_kernel as eq6  # noqa: E402
import phase_space_convergence as psc  # noqa: E402

A = 131
Z = 54
J_A = 1.5
U_GEV = 0.93149410242
M_A_GEV = A * U_GEV
M_CHI_GEV = 1000.0
M_V_GEV = 10.0
G_PRODUCT_SQUARED = 1.0e-8
G2_FOR_WIDTH = 1.0
SPEED_KM_S = 800.0
C_KM_S = 299_792.458
GEV2_TO_CM2_PER_KEV = 0.3893793721e-33
EXPECTED_Q_NODES = 2401
EXPECTED_Q_MAX_GEV = 0.6
FACTOR4_RTOL = 2.0e-12

BENCHMARKS = {
    "red_ms200_dm1": (200.0e-6, 1.0e-3),
    "green_ms300_dm1": (300.0e-6, 1.0e-3),
    "black_ms360_dm1": (360.0e-6, 1.0e-3),
    "blue_ms300_dm10": (300.0e-6, 10.0e-3),
}
DEFAULT_BENCHMARKS = tuple(BENCHMARKS)
DEFAULT_ANCHOR_ENERGIES_KEV = (101.0, 200.0, 267.0, 542.0)


@dataclass(frozen=True)
class ResponseTable:
    q_GeV: np.ndarray
    R_package: np.ndarray
    R_physical: np.ndarray
    C0: float
    package_interpolator: PchipInterpolator
    physical_interpolator: PchipInterpolator
    max_factor4_mapping_residual: float
    package_q0_relative_offset: float
    source_sha256: str

    def at_q(self, q_GeV: float) -> tuple[float, float]:
        if q_GeV < self.q_GeV[0] - 1.0e-14 or q_GeV > self.q_GeV[-1] + 1.0e-12:
            raise ValueError(
                f"q={q_GeV:.12g} GeV lies outside AFH support "
                f"[{self.q_GeV[0]:.12g}, {self.q_GeV[-1]:.12g}] GeV"
            )
        package = float(self.package_interpolator(q_GeV))
        physical = float(self.physical_interpolator(q_GeV))
        if not (math.isfinite(package) and math.isfinite(physical)):
            raise ArithmeticError("AFH response interpolation returned a non-finite value")
        if package < 0.0 or physical < 0.0:
            raise ArithmeticError("AFH response interpolation returned a negative response")
        return package, physical


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write an empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def load_response_table(path: Path) -> ResponseTable:
    rows = read_csv(path)
    required = {
        "q_GeV",
        "R_AFH_package_4pi_over_2Jplus1",
        "R_equal_pn_normalized",
    }
    if len(rows) != EXPECTED_Q_NODES:
        raise ValueError(
            f"AFH response table must contain {EXPECTED_Q_NODES} q nodes; got {len(rows)}"
        )
    if required - set(rows[0]):
        raise ValueError(f"AFH response table is missing columns: {sorted(required-set(rows[0]))}")

    q = np.asarray([float(row["q_GeV"]) for row in rows], dtype=float)
    package = np.asarray(
        [float(row["R_AFH_package_4pi_over_2Jplus1"]) for row in rows],
        dtype=float,
    )
    physical = np.asarray(
        [float(row["R_equal_pn_normalized"]) for row in rows],
        dtype=float,
    )
    if not (
        np.all(np.isfinite(q))
        and np.all(np.isfinite(package))
        and np.all(np.isfinite(physical))
    ):
        raise ValueError("AFH response table contains non-finite values")
    if not np.all(np.diff(q) > 0.0):
        raise ValueError("AFH q grid must be strictly increasing")
    if not math.isclose(float(q[0]), 0.0, rel_tol=0.0, abs_tol=1.0e-14):
        raise ValueError("AFH q grid must start at q=0")
    if not math.isclose(
        float(q[-1]), EXPECTED_Q_MAX_GEV, rel_tol=0.0, abs_tol=1.0e-12
    ):
        raise ValueError("AFH q grid must end at 0.6 GeV")
    if np.any(package < 0.0) or np.any(physical < 0.0):
        raise ValueError("AFH responses must be non-negative")

    package_q0_expected = A * A / 4.0
    package_q0_offset = abs(float(package[0]) / package_q0_expected - 1.0)
    if package_q0_offset > 2.0e-4:
        raise ValueError(
            "AFH package q=0 response is inconsistent with A^2/4 beyond "
            f"the rounded-density-matrix tolerance: {package_q0_offset:.3e}"
        )
    if not math.isclose(float(physical[0]), A * A, rel_tol=0.0, abs_tol=2.0e-8):
        raise ValueError("physical equal-p/n response must satisfy R_A(0)=A^2")

    # C0 removes only the small finite-decimal density-matrix offset.
    # The isospin conversion itself is the single explicit factor of four.
    c0 = A * A / (4.0 * float(package[0]))
    mapped = 4.0 * c0 * package
    residuals = np.abs(physical - mapped) / np.maximum(1.0, np.abs(physical))
    max_mapping_residual = float(np.max(residuals))
    if max_mapping_residual > FACTOR4_RTOL:
        raise ValueError(
            "AFH physical/package factor-four mapping failed: "
            f"max residual={max_mapping_residual:.3e}"
        )

    return ResponseTable(
        q_GeV=q,
        R_package=package,
        R_physical=physical,
        C0=c0,
        package_interpolator=PchipInterpolator(q, package, extrapolate=False),
        physical_interpolator=PchipInterpolator(q, physical, extrapolate=False),
        max_factor4_mapping_residual=max_mapping_residual,
        package_q0_relative_offset=package_q0_offset,
        source_sha256=sha256_file(path),
    )


def exact_spatial_q_GeV(mA_GeV: float, ER_GeV: float) -> float:
    """Exact spatial momentum from P'^2=P^2=m_A^2, not sqrt(-t)."""
    return math.sqrt(2.0 * mA_GeV * ER_GeV + ER_GeV * ER_GeV)


def mediator_denominator_GeV4(mA_GeV: float, ER_GeV: float, mV_GeV: float) -> float:
    """(m_V^2-t)^2 with t=-2*m_A*E_R; distinct from q_spatial^2."""
    return (mV_GeV * mV_GeV + 2.0 * mA_GeV * ER_GeV) ** 2


def assemble_cross_sections(
    I6_GeV2: float,
    R_A_physical: float,
    ER_GeV: float,
    *,
    mA_GeV: float = M_A_GEV,
    mchi_GeV: float = M_CHI_GEV,
    mV_GeV: float = M_V_GEV,
    speed_km_s: float = SPEED_KM_S,
    coupling_product_squared: float = G_PRODUCT_SQUARED,
) -> dict[str, float]:
    """Assemble physical and no-factor-four d sigma/dER from the same I6."""
    beta = speed_km_s / C_KM_S
    if not (0.0 < beta < 1.0):
        raise ValueError("incoming speed must satisfy 0 < v/c < 1")
    pchi = mchi_GeV * beta / math.sqrt(1.0 - beta * beta)
    denominator = mediator_denominator_GeV4(mA_GeV, ER_GeV, mV_GeV)
    prefactor = (
        mA_GeV * coupling_product_squared
        / (256.0 * math.pi**3 * pchi * pchi * denominator)
    )
    dsigma = prefactor * R_A_physical * I6_GeV2
    dsigma_no4 = prefactor * (R_A_physical / 4.0) * I6_GeV2
    return {
        "pchi_GeV": pchi,
        "mediator_denominator_GeV4": denominator,
        "dsigma_dER_GeVminus3": dsigma,
        "dsigma_without_factor4_GeVminus3": dsigma_no4,
        "dsigma_factor4_ratio": dsigma / dsigma_no4 if dsigma_no4 > 0.0 else 0.0,
        "dsigma_cm2_per_keV": dsigma * GEV2_TO_CM2_PER_KEV,
    }


def evaluate_point(
    *,
    benchmark: str,
    ER_keV: float,
    response: ResponseTable,
    nW: int = 16,
    nz: int = 16,
    nphi: int = 8,
    width_scheme: str = "pole",
) -> dict:
    if benchmark not in BENCHMARKS:
        raise ValueError(f"unknown benchmark: {benchmark}")
    if ER_keV <= 0.0 or not math.isfinite(ER_keV):
        raise ValueError("ER must be finite and positive")
    if width_scheme not in {"pole", "zero"}:
        raise ValueError("width_scheme must be pole or zero")

    ms_GeV, delta_m_GeV = BENCHMARKS[benchmark]
    ER_GeV = ER_keV * 1.0e-6
    q_GeV = exact_spatial_q_GeV(M_A_GEV, ER_GeV)
    R_package, R_physical = response.at_q(q_GeV)
    factor4_residual = abs(
        R_physical - 4.0 * response.C0 * R_package
    ) / max(1.0, abs(R_physical))
    if factor4_residual > FACTOR4_RTOL:
        raise ArithmeticError(
            f"interpolated AFH factor-four mapping failed at ER={ER_keV} keV"
        )

    wmin2, wmax2 = eq6.limits(
        M_CHI_GEV, ms_GeV, M_A_GEV, ER_GeV, SPEED_KM_S
    )
    opened = wmax2 > wmin2
    if opened:
        I6 = psc.integrate_i6(
            M_CHI_GEV,
            ms_GeV,
            delta_m_GeV,
            M_A_GEV,
            ER_GeV,
            SPEED_KM_S,
            nW=nW,
            nz=nz,
            nphi=nphi,
            mapping="threshold_u2",
            width_scheme=width_scheme,
            g2=G2_FOR_WIDTH,
        )
    else:
        I6 = 0.0

    cross = assemble_cross_sections(I6, R_physical, ER_GeV)
    pole_width = eq6.chi2_width_dirac_scalar(
        M_CHI_GEV, ms_GeV, delta_m_GeV, G2_FOR_WIDTH
    )
    pole_clearance_keV = (
        (M_CHI_GEV + delta_m_GeV - math.sqrt(wmax2)) * 1.0e6
        if wmax2 > 0.0 else math.inf
    )
    return {
        "benchmark": benchmark,
        "ER_keV": ER_keV,
        "q_exact_spatial_GeV": q_GeV,
        "R_A_AFH_package": R_package,
        "R_A_physical_normalized": R_physical,
        "R_A_physical_without_factor4": R_physical / 4.0,
        "C0": response.C0,
        "factor4_mapping_relative_residual": factor4_residual,
        "I6_GeV2": I6,
        "width_scheme": width_scheme,
        "W2_mapping": "threshold_u2",
        "g2_for_width": G2_FOR_WIDTH,
        "Gamma_chi2_pole_GeV": pole_width,
        "Wmin2_GeV2": wmin2,
        "Wmax2_GeV2": wmax2,
        "chi2_pole_clearance_keV": pole_clearance_keV,
        "phase_space_open": int(opened),
        "nW": nW,
        "nz": nz,
        "nphi": nphi,
        **cross,
    }


def recoil_energies(args: argparse.Namespace) -> list[float]:
    if args.er_list_kev:
        energies = [float(item.strip()) for item in args.er_list_kev.split(",")]
    else:
        count = int(round((args.er_stop_kev - args.er_start_kev) / args.er_step_kev))
        energies = [
            args.er_start_kev + i * args.er_step_kev
            for i in range(count + 1)
        ]
    if not energies or any((not math.isfinite(e) or e <= 0.0) for e in energies):
        raise ValueError("recoil-energy grid must contain finite positive values")
    if len(set(energies)) != len(energies):
        raise ValueError("recoil-energy grid contains duplicate values")
    if not args.skip_anchor_checks:
        energies = sorted(set(energies).union(DEFAULT_ANCHOR_ENERGIES_KEV))
    return sorted(energies)


def run(args: argparse.Namespace) -> dict:
    args.outdir.mkdir(parents=True, exist_ok=True)
    response = load_response_table(args.response_csv)
    energies = recoil_energies(args)
    benchmarks = tuple(args.benchmarks)

    rows: list[dict] = []
    lookup: dict[tuple[str, float], dict] = {}
    for benchmark in benchmarks:
        for ER_keV in energies:
            row = evaluate_point(
                benchmark=benchmark,
                ER_keV=ER_keV,
                response=response,
                nW=args.nw,
                nz=args.nz,
                nphi=args.nphi,
                width_scheme=args.width_scheme,
            )
            rows.append(row)
            lookup[(benchmark, ER_keV)] = row

    open_rows = [row for row in rows if row["phase_space_open"]]
    max_factor4_ratio_residual = max(
        (
            abs(float(row["dsigma_factor4_ratio"]) - 4.0) / 4.0
            for row in open_rows
        ),
        default=0.0,
    )
    max_factor4_mapping_residual = max(
        float(row["factor4_mapping_relative_residual"]) for row in rows
    )
    max_unit_conversion_residual = max(
        (
            abs(
                float(row["dsigma_cm2_per_keV"])
                - float(row["dsigma_dER_GeVminus3"]) * GEV2_TO_CM2_PER_KEV
            )
            / max(abs(float(row["dsigma_cm2_per_keV"]), 1.0e-300)
            for row in rows
        ),
        default=0.0,
    )
    if max_factor4_ratio_residual > FACTOR4_RTOL:
        raise ArithmeticError(
            f"physical/no-factor-four ratio failed: {max_factor4_ratio_residual:.3e}"
        )
    if max_factor4_mapping_residual > FACTOR4_RTOL:
        raise ArithmeticError(
            f"response mapping failed: {max_factor4_mapping_residual:.3e}"
        )
    if max_unit_conversion_residual > 2.0e-14:
        raise ArithmeticError(
            f"cross-section unit conversion failed: {max_unit_conversion_residual:.3e}"
        )
    if any(float(row["I6_GeV2"]) < 0.0 for row in rows):
        raise ArithmeticError("negative I6 value found")
    if any(
        row["phase_space_open"] == 0
        and (
            float(row["I6_GeV2"]) != 0.0
            or float(row["dsigma_dER_GeVminus3"]) != 0.0
        )
        for row in rows
    ):
        raise ArithmeticError("kinematically closed points must have exactly zero rate")
    if any(
        float(row["chi2_pole_clearance_keV"]) <= 0.0
        for row in open_rows
    ):
        raise ArithmeticError("chi2 pole enters the kinematically accessible W interval")

    anchor_rows: list[dict] = []
    if not args.skip_anchor_checks:
        high_nW, high_nz, high_nphi = args.anchor_order
        for benchmark in benchmarks:
            for ER_keV in DEFAULT_ANCHOR_ENERGIES_KEV:
                base = lookup[(benchmark, ER_keV)]
                if not base["phase_space_open"]:
                    anchor_rows.append({
                        "benchmark": benchmark,
                        "ER_keV": ER_keV,
                        "phase_space_open": 0,
                        "base_I6_GeV2": 0.0,
                        "high_order_I6_GeV2": 0.0,
                        "base_order": f"{args.nw}x{args.nz}x{args.nphi}",
                        "high_order": f"{high_nW}x{high_nz}x{high_nphi}",
                        "relative_difference": 0.0,
                    })
                    continue
                ms_GeV, delta_m_GeV = BENCHMARKS[benchmark]
                ER_GeV = ER_keV * 1.0e-6
                high_I6 = psc.integrate_i6(
                    M_CHI_GEV,
                    ms_GeV,
                    delta_m_GeV,
                    M_A_GEV,
                    ER_GeV,
                    SPEED_KM_S,
                    nW=high_nW,
                    nz=high_nz,
                    nphi=high_nphi,
                    mapping="threshold_u2",
                    width_scheme=args.width_scheme,
                    g2=G2_FOR_WIDTH,
                )
                base_I6 = float(base["I6_GeV2"])
                relative = abs(high_I6 / base_I6 - 1.0) if base_I6 else math.inf
                anchor_rows.append({
                    "benchmark": benchmark,
                    "ER_keV": ER_keV,
                    "phase_space_open": 1,
                    "base_I6_GeV2": base_I6,
                    "high_order_I6_GeV2": high_I6,
                    "base_order": f"{args.nw}x{args.nz}x{args.nphi}",
                    "high_order": f"{high_nW}x{high_nz}x{high_nphi}",
                    "relative_difference": relative,
                })
        max_anchor_difference = max(
            (float(row["relative_difference"]) for row in anchor_rows),
            default=0.0,
        )
        if max_anchor_difference > args.max_anchor_relative_difference:
            raise ArithmeticError(
                "high-order anchor convergence failed: "
                f"{max_anchor_difference:.3e} > {args.max_anchor_relative_difference:.3e}"
            )
    else:
        max_anchor_difference = None

    cross_section_path = args.outdir / "python_full_dsigma_xe131.csv"
    write_csv(cross_section_path, rows)
    anchor_path = args.outdir / "python_full_dsigma_quadrature_anchors.csv"
    if anchor_rows:
        write_csv(anchor_path, anchor_rows)

    metadata = {
        "status": "PASS",
        "calculation": "Python-only complete Xe-131 Eq. (6) differential cross section",
        "mathematica_or_wolfram_invoked": False,
        "target": {
            "A": A,
            "Z": Z,
            "J_A": J_A,
            "mA_GeV": M_A_GEV,
            "mass_convention": "A*u with u=0.93149410242 GeV, matching the fixed-speed Figure-2 benchmark",
        },
        "particle_inputs": {
            "m_chi1_GeV": M_CHI_GEV,
            "m_V_GeV": M_V_GEV,
            "g2_for_conditional_width": G2_FOR_WIDTH,
            "coupling_product_squared": G_PRODUCT_SQUARED,
            "speed_km_s": SPEED_KM_S,
            "width_scheme": args.width_scheme,
            "width_assumption": "conditional Dirac fermions, real scalar, pure scalar off-diagonal Yukawa, chi2 -> chi1 s only",
        },
        "benchmarks": {
            name: {"m_s_GeV": BENCHMARKS[name][0], "Delta_m_GeV": BENCHMARKS[name][1]}
            for name in benchmarks
        },
        "AFH_response": {
            "source_file": str(args.response_csv),
            "source_sha256": response.source_sha256,
            "q_nodes": len(response.q_GeV),
            "q_range_GeV": [float(response.q_GeV[0]), float(response.q_GeV[-1])],
            "R_package_q0": float(response.R_package[0]),
            "expected_R_package_q0_A2_over_4": A * A / 4.0,
            "package_q0_relative_offset_from_rounded_density_matrix": response.package_q0_relative_offset,
            "C0": response.C0,
            "R_physical_q0": float(response.R_physical[0]),
            "expected_R_physical_q0_A2": A * A,
            "physical_mapping": "R_A_physical(q) = 4*C0*R_A_AFH_package(q)",
            "max_factor4_mapping_relative_residual_on_all_2401_nodes": response.max_factor4_mapping_residual,
            "max_factor4_mapping_relative_residual_on_evaluated_points": max_factor4_mapping_residual,
        },
        "cross_section": {
            "formula": "mA*(g1*g2*gVN)^2*R_A_physical*I6/[256*pi^3*pchi^2*(mV^2+2*mA*ER)^2]",
            "no_factor4_control": "same prefactor and I6 with R_A_physical/4",
            "factor4_applied_in_physical_response_once": True,
            "per_nucleon_coupling_retained_in_prefactor": True,
            "spatial_q": "sqrt(2*mA*ER+ER^2)",
            "mediator_invariant": "t=-2*mA*ER; denominator uses (mV^2-t)^2",
            "initial_spin_average": "1/2 included once in eq6_kernel.spin_trace",
            "azimuthal_average": "1/(2*pi) included once in phase_space_convergence.integrate_i6",
            "identical_particle_factor": "none; final chi1 and scalar s are distinguishable",
            "unit_conversion_GeVminus3_to_cm2_per_keV": GEV2_TO_CM2_PER_KEV,
        },
        "quadrature": {
            "base_order": [args.nw, args.nz, args.nphi],
            "W2_mapping": "threshold_u2",
            "anchor_order": args.anchor_order if anchor_rows else None,
            "anchor_energies_keV": list(DEFAULT_ANCHOR_ENERGIES_KEV) if anchor_rows else [],
            "max_anchor_relative_difference": max_anchor_difference,
            "max_anchor_relative_difference_tolerance": args.max_anchor_relative_difference,
        },
        "acceptance": {
            "max_factor4_ratio_relative_residual": max_factor4_ratio_residual,
            "max_factor4_mapping_relative_residual": max_factor4_mapping_residual,
            "max_unit_conversion_relative_residual": max_unit_conversion_residual,
            "open_rows": len(open_rows),
            "closed_rows": len(rows) - len(open_rows),
            "total_rows": len(rows),
        },
        "scope": [
            "Xe-131 only; fixed mono-speed v=800 km/s; not a halo fold",
            "AFH response is PCHIP-interpolated from the archived 2401-node Python source translation",
            "full native Mathematica differential-cross-section comparison is deliberately deferred",
            "not a complete vector-plus-scalar chi2 self-energy",
            "no detector efficiency, energy resolution, exposure, cuts or LZ likelihood",
        ],
        "output": {
            "cross_section_csv": str(cross_section_path),
            "cross_section_csv_sha256": sha256_file(cross_section_path),
            "anchor_csv": str(anchor_path) if anchor_rows else None,
            "anchor_csv_sha256": sha256_file(anchor_path) if anchor_rows else None,
        },
    }
    metadata_path = args.outdir / "python_full_dsigma_xe131_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return metadata


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Python-only full Xe-131 d sigma/dER and AFH factor-four audit"
    )
    parser.add_argument(
        "--response-csv",
        type=Path,
        default=HERE / "output" / "afh_default_xe131_WM00.csv",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=HERE / "output" / "python_full_dsigma",
    )
    parser.add_argument("--benchmarks", nargs="+", choices=tuple(BENCHMARKS), default=list(DEFAULT_BENCHMARKS))
    parser.add_argument("--er-start-kev", type=float, default=5.0)
    parser.add_argument("--er-stop-kev", type=float, default=800.0)
    parser.add_argument("--er-step-kev", type=float, default=5.0)
    parser.add_argument(
        "--er-list-kev",
        type=str,
        default=None,
        help="optional comma-separated recoil points; otherwise use the regular grid",
    )
    parser.add_argument("--nw", type=int, default=16)
    parser.add_argument("--nz", type=int, default=16)
    parser.add_argument("--nphi", type=int, default=8)
    parser.add_argument("--width-scheme", choices=("pole", "zero"), default="pole")
    parser.add_argument("--skip-anchor-checks", action="store_true")
    parser.add_argument("--anchor-order", nargs=3, type=int, default=(48, 40, 24))
    parser.add_argument("--max-anchor-relative-difference", type=float, default=1.0e-3)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    metadata = run(args)
    if metadata["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
