#!/usr/bin/env python3
"""Independent Python recomputation and pointwise comparison of Mathematica Eq. (6) output."""
from __future__ import annotations
import argparse, json, math, platform, sys
import scipy
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "research" / "three_body_calculation_and_validation"))
import eq6_kernel  # noqa: E402
import phase_space_convergence as psc  # noqa: E402

A = 131
M_A = A * 0.93149410242
M_CHI, M_V, G_PRODUCT_SQ, SPEED = 1000.0, 10.0, 1.0e-8, 800.0
C_KM_S = 299792.458
GEV3_TO_CM2_PER_KEV = 0.3893793721e-33
CONVERSION_IDENTITY_RTOL = 2.0e-12
BENCHMARKS = {
    "red_ms200_dm1": (200e-6, 1e-3),
    "green_ms300_dm1": (300e-6, 1e-3),
    "black_ms360_dm1": (360e-6, 1e-3),
    "blue_ms300_dm10": (300e-6, 10e-3),
}


def rel(a: float, b: float) -> float:
    return abs(a - b) / max(abs(b), 1e-300)


def portable_path(path: Path) -> str:
    """Avoid machine-specific absolute paths in committed or uploaded metadata."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return path.name


def conversion_identity_residual(
    converted_cm2_per_keV: float, dsigma_GeVminus3: float, opened: bool
) -> float:
    """Check one code's own GeV^-3 -> cm^2/keV conversion, not cross-code agreement."""
    expected = dsigma_GeVminus3 * GEV3_TO_CM2_PER_KEV
    return rel(converted_cm2_per_keV, expected) if opened else abs(converted_cm2_per_keV - expected)


def comparison_passes(
    maxima: dict[str, float], rtol: float, response_rtol: float
) -> bool:
    """Apply observable-level and algebraic-identity tolerances separately."""
    return (
        maxima["I6"] <= rtol and maxima["dsigma"] <= rtol
        and maxima["dsigma_no4"] <= rtol and maxima["dsigma_conversion"] <= rtol
        and maxima["R_A_physical"] <= response_rtol
        and maxima["R_A_package"] <= response_rtol
        and all(maxima[key] <= CONVERSION_IDENTITY_RTOL for key in (
            "q", "C0", "dsigma_conversion_identity_Mathematica",
            "dsigma_conversion_identity_Python", "factor4_mapping",
            "factor4_ratio", "pchi", "mediator_denominator",
        ))
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mathematica-csv", type=Path, required=True)
    ap.add_argument("--afh-response-csv", type=Path,
                    default=HERE / "output" / "native_exports" / "afh_default_xe131_WM00_mathematica.csv")
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--metadata", type=Path, required=True)
    ap.add_argument("--rtol", type=float, default=2e-7,
                    help="relative tolerance for independently recomputed I6 and dSigma")
    ap.add_argument("--response-rtol", type=float, default=2e-10,
                    help="response tolerance when both implementations use the same fixed native AFH table")
    ap.add_argument("--require-full-grid", action="store_true",
                    help="require all four benchmarks and the complete 5--800 keV grid plus explicit anchors")
    args = ap.parse_args()

    m = pd.read_csv(args.mathematica_csv)
    response = pd.read_csv(args.afh_response_csv)
    package_column = next((c for c in ("R_AFH_package_4pi_over_2Jplus1", "R_AFH_4Pi_over_2Jplus1")
                           if c in response.columns), None)
    if package_column is None:
        raise ValueError("AFH response table is missing the package-normalized response column")
    required = {"benchmark", "ER_keV", "q_GeV", "R_A_AFH_package", "R_A_physical_normalized",
                "C0", "I6_GeV2", "width_scheme", "W2_mapping", "g2", "phase_space_open",
                "nW", "nz", "nphi", "pchi_GeV", "mediator_denominator_GeV4",
                "dsigma_dER_GeVminus3", "dsigma_without_factor4_GeVminus3",
                "dsigma_cm2_per_keV"}
    if required - set(m.columns):
        raise ValueError(f"Missing Mathematica columns: {sorted(required-set(m.columns))}")
    if len(response) != 2401:
        raise ValueError("AFH response table must contain 2401 q nodes")
    if m.duplicated(["benchmark", "ER_keV"]).any():
        raise ValueError("Mathematica output contains duplicate benchmark/recoil rows")
    if args.require_full_grid:
        expected_energies = set(float(x) for x in range(5, 801, 5))
        expected_energies.update({101.0, 200.0, 267.0, 542.0})
        expected_keys = {
            (name, energy) for name in BENCHMARKS for energy in expected_energies
        }
        actual_keys = {
            (str(row.benchmark), float(row.ER_keV))
            for row in m.itertuples(index=False)
        }
        if actual_keys != expected_keys:
            missing = sorted(expected_keys - actual_keys)[:8]
            extra = sorted(actual_keys - expected_keys)[:8]
            raise ValueError(
                f"Mathematica output is not the complete 4x163 grid; "
                f"rows={len(m)}, missing={missing}, extra={extra}"
            )

    q = response.q_GeV.to_numpy(float)
    r_package = response[package_column].to_numpy(float)
    r_physical = response.R_equal_pn_normalized.to_numpy(float)
    if not np.all(np.isfinite(q)) or not np.all(np.diff(q) > 0):
        raise ValueError("AFH q grid must be finite and strictly increasing")
    if not np.isclose(r_physical[0], A*A, rtol=0.0, atol=2e-8):
        raise ValueError("AFH physical response must satisfy R_A(0)=A^2")
    c0_expected = A*A/(4.0*r_package[0])
    pkg = PchipInterpolator(q, r_package, extrapolate=False)
    phys = PchipInterpolator(q, r_physical, extrapolate=False)
    out = []
    maxima = {"I6": 0.0, "dsigma": 0.0, "dsigma_no4": 0.0,
              "dsigma_conversion": 0.0,
              "dsigma_conversion_identity_Mathematica": 0.0,
              "dsigma_conversion_identity_Python": 0.0,
              "R_A_physical": 0.0,
              "R_A_package": 0.0, "factor4_mapping": 0.0,
              "factor4_ratio": 0.0, "C0": 0.0, "q": 0.0,
              "pchi": 0.0, "mediator_denominator": 0.0}
    open_count = 0

    for r in m.itertuples(index=False):
        name = str(r.benchmark)
        if name not in BENCHMARKS:
            raise ValueError(f"Unknown benchmark: {name}")
        ms, dm = BENCHMARKS[name]
        ER = float(r.ER_keV) * 1e-6
        qx = math.sqrt(2*M_A*ER + ER**2)
        q_m = float(r.q_GeV)
        rp_py, rf_py = float(pkg(qx)), float(phys(qx))
        opened = bool(int(r.phase_space_open))
        wmin, wmax = eq6_kernel.limits(M_CHI, ms, M_A, ER, SPEED)
        if opened != (wmax > wmin):
            raise AssertionError(f"{name} ER={r.ER_keV}: phase-space mask mismatch")
        nw, nz, nphi = int(r.nW), int(r.nz), int(r.nphi)
        scheme, mapping, g2 = str(r.width_scheme), str(r.W2_mapping), float(r.g2)
        if mapping not in {"threshold_u2", "linear_w2"}:
            raise ValueError(f"Unsupported W2 mapping: {mapping}")
        if scheme not in {"pole", "zero"}:
            raise ValueError(f"Unsupported width scheme: {scheme}")
        i6py = psc.integrate_i6(
            M_CHI, ms, dm, M_A, ER, SPEED,
            nW=nw, nz=nz, nphi=nphi, mapping=mapping,
            width_scheme=scheme, g2=g2,
        ) if opened else 0.0

        beta = SPEED/C_KM_S
        pchi = M_CHI*beta/math.sqrt(1-beta**2)
        den = (M_V**2 + 2*M_A*ER)**2
        pchi_m = float(r.pchi_GeV)
        den_m = float(r.mediator_denominator_GeV4)
        pref = M_A*G_PRODUCT_SQ/(256*math.pi**3*pchi**2*den)
        ds_py = pref*rf_py*i6py if opened else 0.0
        ds_no4_py = ds_py/4.0
        ds_cm_py = ds_py*GEV3_TO_CM2_PER_KEV
        i6m, dsm = float(r.I6_GeV2), float(r.dsigma_dER_GeVminus3)
        ds_no4_m = float(r.dsigma_without_factor4_GeVminus3)
        ds_cm_m = float(r.dsigma_cm2_per_keV)
        ram, rpm, c0 = float(r.R_A_physical_normalized), float(r.R_A_AFH_package), float(r.C0)
        factor4_ratio = dsm/ds_no4_m if opened and ds_no4_m != 0.0 else 0.0
        values = {
            "q": rel(q_m, qx),
            "C0": rel(c0, c0_expected),
            "I6": rel(i6m, i6py) if opened else abs(i6m-i6py),
            "dsigma": rel(dsm, ds_py) if opened else abs(dsm-ds_py),
            "dsigma_no4": rel(ds_no4_m, ds_no4_py) if opened else abs(ds_no4_m-ds_no4_py),
            "dsigma_conversion": rel(ds_cm_m, ds_cm_py) if opened else abs(ds_cm_m-ds_cm_py),
            "dsigma_conversion_identity_Mathematica": conversion_identity_residual(ds_cm_m, dsm, opened),
            "dsigma_conversion_identity_Python": conversion_identity_residual(ds_cm_py, ds_py, opened),
            "R_A_physical": rel(ram, rf_py),
            "R_A_package": rel(rpm, rp_py),
            "factor4_mapping": rel(ram, 4*c0*rpm),
            "factor4_ratio": rel(factor4_ratio, 4.0) if opened else 0.0,
            "pchi": rel(pchi_m, pchi),
            "mediator_denominator": rel(den_m, den),
        }
        for key, value in values.items():
            maxima[key] = max(maxima[key], value)
        open_count += int(opened)
        out.append({
            "benchmark": name, "ER_keV": float(r.ER_keV), "phase_space_open": int(opened),
            "q_Mathematica_GeV": q_m, "q_expected_GeV": qx,
            "q_relative_difference": values["q"],
            "pchi_Mathematica_GeV": pchi_m, "pchi_Python_GeV": pchi,
            "pchi_relative_difference": values["pchi"],
            "mediator_denominator_Mathematica_GeV4": den_m,
            "mediator_denominator_Python_GeV4": den,
            "mediator_denominator_relative_difference": values["mediator_denominator"],
            "I6_Mathematica_GeV2": i6m, "I6_Python_GeV2": i6py,
            "I6_relative_difference": values["I6"],
            "R_A_Mathematica": ram, "R_A_Python_PCHIP": rf_py,
            "R_A_relative_difference": values["R_A_physical"],
            "R_A_package_Mathematica": rpm, "R_A_package_Python_PCHIP": rp_py,
            "R_A_package_relative_difference": values["R_A_package"],
            "factor4_mapping_relative_residual": values["factor4_mapping"],
            "C0_Mathematica": c0, "C0_expected_from_AFH_q0": c0_expected,
            "C0_relative_difference": values["C0"],
            "dsigma_Mathematica_GeVminus3": dsm, "dsigma_Python_GeVminus3": ds_py,
            "dsigma_relative_difference": values["dsigma"],
            "dsigma_no4_Mathematica_GeVminus3": ds_no4_m,
            "dsigma_no4_Python_GeVminus3": ds_no4_py,
            "dsigma_no4_relative_difference": values["dsigma_no4"],
            "dsigma_cm2_per_keV_Mathematica": ds_cm_m,
            "dsigma_cm2_per_keV_Python": ds_cm_py,
            "dsigma_conversion_relative_difference": values["dsigma_conversion"],
            "dsigma_conversion_identity_Mathematica_relative_residual": values["dsigma_conversion_identity_Mathematica"],
            "dsigma_conversion_identity_Python_relative_residual": values["dsigma_conversion_identity_Python"],
            "dsigma_factor4_ratio": factor4_ratio if opened else 0.0,
        })

    result = pd.DataFrame(out)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out_csv, index=False, float_format="%.14g")
    passed = comparison_passes(maxima, args.rtol, args.response_rtol)
    metadata = {
        "status": "PASS" if passed else "FAIL", "rows": len(result),
        "benchmarks": sorted(set(m.benchmark.astype(str))),
        "recoil_energies_keV": sorted(float(x) for x in m.ER_keV.unique()),
        "python_environment": {
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
            "pandas_version": pd.__version__,
            "scipy_version": scipy.__version__,
        },
        "open_phase_space_rows": open_count, "max_relative_differences": maxima,
        "tolerances": {
            "I6_dsigma_and_cross_code_converted_dsigma": args.rtol,
            "PCHIP_response": args.response_rtol,
            "response_tolerance_rationale": "Both implementations interpolate the same fixed native Mathematica AFH response table; source-translation differences are audited separately.",
            "q_C0_per_code_unit_conversion_identities_factor4_pchi_and_mediator_denominator": CONVERSION_IDENTITY_RTOL,
            "unit_conversion_factor_GeVminus3_to_cm2_per_keV": GEV3_TO_CM2_PER_KEV,
        },
        "full_grid_required": args.require_full_grid,
        "W2_mappings": sorted(set(m.W2_mapping.astype(str))),
        "factor4_convention": "R_A_phys=4*C0*R_A_AFH_package; per-nucleon gVN remains in Eq. (6) prefactor",
        "width_assumption": "conditional Dirac, real scalar, pure scalar g2, chi2 -> chi1 s only",
        "comparison_csv": portable_path(args.out_csv), "mathematica_csv": portable_path(args.mathematica_csv),
        "path_convention": "Repository paths are repository-relative; paths outside the repository are stored as portable basenames.",
    }
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
