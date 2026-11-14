#!/usr/bin/env python3
"""Independent Python recomputation and pointwise comparison of Mathematica Eq. (6) output."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "research" / "figure2_full_reproduction"))
import eq6_kernel  # noqa: E402
import phase_space_convergence as psc  # noqa: E402

A = 131
M_A = A * 0.93149410242
M_CHI, M_V, G_PRODUCT_SQ, SPEED = 1000.0, 10.0, 1.0e-8, 800.0
C_KM_S = 299792.458
BENCHMARKS = {
    "red_ms200_dm1": (200e-6, 1e-3),
    "green_ms300_dm1": (300e-6, 1e-3),
    "black_ms360_dm1": (360e-6, 1e-3),
    "blue_ms300_dm10": (300e-6, 10e-3),
}


def rel(a: float, b: float) -> float:
    return abs(a - b) / max(abs(b), 1e-300)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mathematica-csv", type=Path, required=True)
    ap.add_argument("--afh-response-csv", type=Path,
                    default=HERE / "output" / "afh_default_xe131_WM00.csv")
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--metadata", type=Path, required=True)
    ap.add_argument("--rtol", type=float, default=2e-7)
    args = ap.parse_args()

    m = pd.read_csv(args.mathematica_csv)
    response = pd.read_csv(args.afh_response_csv)
    required = {"benchmark", "ER_keV", "q_GeV", "R_A_AFH_package", "R_A_physical_normalized",
                "C0", "I6_GeV2", "width_scheme", "W2_mapping", "g2", "phase_space_open",
                "nW", "nz", "nphi", "dsigma_dER_GeVminus3",
                "dsigma_without_factor4_GeVminus3", "dsigma_cm2_per_keV"}
    if required - set(m.columns):
        raise ValueError(f"Missing Mathematica columns: {sorted(required-set(m.columns))}")
    if len(response) != 2401:
        raise ValueError("AFH response table must contain 2401 q nodes")

    q = response.q_GeV.to_numpy(float)
    r_package = response.R_AFH_package_4pi_over_2Jplus1.to_numpy(float)
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
              "dsigma_conversion": 0.0, "R_A_physical": 0.0,
              "R_A_package": 0.0, "factor4_mapping": 0.0,
              "factor4_ratio": 0.0, "C0": 0.0, "q": 0.0}
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
        pref = M_A*G_PRODUCT_SQ/(256*math.pi**3*pchi**2*den)
        ds_py = pref*rf_py*i6py if opened else 0.0
        ds_no4_py = ds_py/4.0
        ds_cm_py = ds_py*0.3893793721e-33
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
            "R_A_physical": rel(ram, rf_py),
            "R_A_package": rel(rpm, rp_py),
            "factor4_mapping": rel(ram, 4*c0*rpm),
            "factor4_ratio": rel(factor4_ratio, 4.0) if opened else 0.0,
        }
        for key, value in values.items():
            maxima[key] = max(maxima[key], value)
        open_count += int(opened)
        out.append({
            "benchmark": name, "ER_keV": float(r.ER_keV), "phase_space_open": int(opened),
            "q_Mathematica_GeV": q_m, "q_expected_GeV": qx,
            "q_relative_difference": values["q"],
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
            "dsigma_factor4_ratio": factor4_ratio if opened else 0.0,
        })

    result = pd.DataFrame(out)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out_csv, index=False, float_format="%.14g")
    passed = (maxima["I6"] <= args.rtol and maxima["dsigma"] <= args.rtol
              and maxima["dsigma_no4"] <= args.rtol
              and maxima["R_A_physical"] <= 2e-10 and maxima["R_A_package"] <= 2e-10
              and maxima["q"] <= 2e-12 and maxima["C0"] <= 2e-12
              and maxima["dsigma_conversion"] <= 2e-12
              and maxima["factor4_mapping"] <= 2e-12 and maxima["factor4_ratio"] <= 2e-12)
    metadata = {
        "status": "PASS" if passed else "FAIL", "rows": len(result),
        "open_phase_space_rows": open_count, "max_relative_differences": maxima,
        "tolerances": {"I6_and_dsigma": args.rtol, "PCHIP_response": 2e-10,
                       "q_C0_units_and_factor4": 2e-12},
        "W2_mappings": sorted(set(m.W2_mapping.astype(str))),
        "factor4_convention": "R_A_phys=4*C0*R_A_AFH_package; per-nucleon gVN remains in Eq. (6) prefactor",
        "width_assumption": "conditional Dirac, real scalar, pure scalar g2, chi2 -> chi1 s only",
        "comparison_csv": str(args.out_csv), "mathematica_csv": str(args.mathematica_csv),
    }
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
