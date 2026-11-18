#!/usr/bin/env python3
"""Native-AFH M+Phi'' charge-sector natural-xenon halo fold.

This module is the next-stage rate engine after PR #58.  It deliberately
accepts only a pointwise-validated native AFH v6.0 eight-response archive.
For each isotope and recoil it recomputes the exact three-body DM tensor with
that isotope's nuclear mass, evaluates q_A exactly, interpolates the native
M, Phi'', and signed M-Phi'' responses, and applies the finite-t_N charge
coefficients.

The engine is charge-sector only:
    M + Phi'' + M-Phi''
The Delta/Sigma'/Sigma'' sector is intentionally not inserted here because
the current PR #58 result already bounds it separately and the native
seven-isotope spatial-response promotion is a distinct acceptance gate.

The output always contains the old pointlike M-only baseline, the finite-t
M-only result, the M+Phi'' result, and interpolation diagnostics.  No
single "full-spectrum correction" is reported unless all requested isotopes,
recoil points, and halo quadrature evaluations complete.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.interpolate import PchipInterpolator
from numpy.polynomial.legendre import leggauss

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HALO_INPUT = ROOT / "research" / "afh_default_density_natural_xenon_halo" / "input"
sys_path = ROOT / "research" / "three_body_full_current_nucleon_match"
import sys
if str(sys_path) not in sys.path:
    sys.path.insert(0, str(sys_path))

from nucleon_vector_form_factors import (  # noqa: E402
    F1V0,
    F2V0,
    bishara_linear,
    isoscalar_zexp,
    charge_coefficients,
)
from three_body_phase_space_tensor import integrate_spin_resolved_tensor  # noqa: E402

C_KM_S = 299792.458
C_CM_S = 2.99792458e10
GEV2_TO_CM2 = 0.3893793721e-27
AVOGADRO = 6.02214076e23
U_GEV = 0.93149410242
ME_U = 0.000548579909065
Z_XE = 54
MCHI_DEFAULT = 1000.0
MV_DEFAULT = 10.0
RHO_DEFAULT = 0.3
G2_DEFAULT = 1.0
COUPLING_PRODUCT_SQUARED_DEFAULT = 1.0e-8

ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
J_BY_A = {128: 0.0, 129: 0.5, 130: 0.0, 131: 1.5, 132: 0.0, 134: 0.0, 136: 0.0}
RESPONSE_NAMES = ("M", "PhiPP", "MPhiPP")
RESPONSE_W_COLUMNS = {
    "M": "W_M00_AFH",
    "PhiPP": "W_PhiPP00_AFH",
    "MPhiPP": "W_MPhiPP00_AFH",
}

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def load_isotope_inputs(path: Path = HALO_INPUT / "natural_xenon_isotope_weights.csv") -> dict[int, dict]:
    rows = read_csv(path)
    data = {}
    for row in rows:
        A = int(row["A"])
        if row["AFH_default_density_available"].lower() != "true":
            continue
        data[A] = {
            "abundance": float(row["natural_atom_fraction"]),
            "atomic_mass_u": float(row["atomic_mass_u"]),
            "mA_GeV": (float(row["atomic_mass_u"]) - Z_XE * ME_U) * U_GEV,
        }
    if tuple(sorted(data)) != ISOTOPES:
        raise ValueError(f"expected AFH isotope set {ISOTOPES}, got {tuple(sorted(data))}")
    return data


def exact_qA_GeV(mA_GeV: float, ER_keV: float) -> float:
    """Exact spatial recoil momentum from P'^2=P^2=m_A^2."""
    ER = float(ER_keV) * 1.0e-6
    if ER < 0.0 or mA_GeV <= 0.0:
        raise ValueError("invalid recoil or nuclear mass")
    return math.sqrt(2.0 * mA_GeV * ER + ER * ER)


def vmin_three_body_km_s(mchi: float, ms: float, mA: float, ER_keV: float) -> float:
    ER = ER_keV * 1.0e-6
    q = exact_qA_GeV(mA, ER_keV)
    a = ms + (mA * ER + 0.5 * ms * ms) / mchi
    beta = (q * ER + a * math.sqrt(q * q - ER * ER + a * a)) / (q * q + a * a)
    return C_KM_S * beta


def mb_untruncated_pdf(v: float, v0: float = 220.0, ve: float = 232.0) -> float:
    if v < 0.0:
        return 0.0
    return v / (math.sqrt(math.pi) * v0 * ve) * (
        math.exp(-((v - ve) / v0) ** 2)
        - math.exp(-((v + ve) / v0) ** 2)
    )


def shm_truncated_pdf(
    v: float, v0: float = 220.0, ve: float = 232.0, vesc: float = 544.0
) -> float:
    if v < 0.0 or v > vesc + ve:
        return 0.0
    z = vesc / v0
    norm = math.erf(z) - 2.0 * z / math.sqrt(math.pi) * math.exp(-z * z)
    if v < vesc - ve:
        bracket = math.exp(-((v - ve) / v0) ** 2) - math.exp(-((v + ve) / v0) ** 2)
    else:
        bracket = math.exp(-((v - ve) / v0) ** 2) - math.exp(-z * z)
    return v * bracket / (math.sqrt(math.pi) * v0 * ve * norm)


def _native_validation_gate(native_dir: Path) -> dict:
    comparison_path = native_dir / "native-comparison.json"
    metadata_path = native_dir / "native_metadata.txt"
    if not comparison_path.is_file():
        raise RuntimeError(
            "native AFH comparison manifest is missing; do not use raw native CSVs "
            "before the 16,807-row pointwise comparison passes"
        )
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    if (
        comparison.get("status") != "PASS"
        or comparison.get("native_afh_validated") is not True
        or comparison.get("rows_compared") != 16807
    ):
        raise RuntimeError(
            "native AFH gate is not closed: "
            f"status={comparison.get('status')}, "
            f"native_afh_validated={comparison.get('native_afh_validated')}, "
            f"rows_compared={comparison.get('rows_compared')}"
        )
    if metadata_path.is_file():
        metadata = metadata_path.read_text(encoding="utf-8")
    else:
        metadata = ""
    return {"comparison": comparison, "native_metadata": metadata}


def load_native_response_bundle(native_dir: Path) -> tuple[dict, dict]:
    gate = _native_validation_gate(native_dir)
    bundle = {}
    for A in ISOTOPES:
        path = native_dir / f"afh_v6_xe{A}_eight_response_native.csv"
        if not path.is_file():
            raise FileNotFoundError(f"missing native AFH export: {path}")
        rows = read_csv(path)
        if len(rows) != 2401:
            raise ValueError(f"Xe-{A}: expected 2401 native rows, got {len(rows)}")
        q = np.asarray([float(row["q_GeV"]) for row in rows], dtype=float)
        if not np.all(np.diff(q) > 0.0) or not np.isclose(q[0], 0.0) or not np.isclose(q[-1], 0.6):
            raise ValueError(f"Xe-{A}: native q grid is not the canonical [0,0.6] GeV grid")
        physical = {}
        for name, column in RESPONSE_W_COLUMNS.items():
            values = np.asarray([float(row[column]) for row in rows], dtype=float)
            imaginary = np.asarray(
                [float(row[f"Im_{column}"]) for row in rows], dtype=float
            )
            if not np.all(np.isfinite(values)) or not np.all(np.isfinite(imaginary)):
                raise ValueError(f"Xe-{A}: non-finite native {name} response")
            if np.max(np.abs(imaginary)) > 2.0e-12:
                raise ValueError(f"Xe-{A}: native {name} imaginary residual is too large")
            conversion = 4.0 * math.pi / (2.0 * J_BY_A[A] + 1.0)
            physical[name] = 4.0 * conversion * values
        bundle[A] = {"q": q, "physical": physical}
    return bundle, gate


def interpolate_native_response(bundle_entry: dict, q_GeV: float) -> dict:
    q = bundle_entry["q"]
    if q_GeV < q[0] or q_GeV > q[-1]:
        raise ValueError(f"q_A={q_GeV:.12g} GeV lies outside native AFH grid")
    out = {}
    linear = {}
    for name in RESPONSE_NAMES:
        values = bundle_entry["physical"][name]
        pchip = PchipInterpolator(q, values, extrapolate=False)
        out[name] = float(pchip(q_GeV))
        linear[name] = float(np.interp(q_GeV, q, values))
    return {
        "physical_equal_pn": out,
        "linear_physical_equal_pn": linear,
        "pchip_linear_relative_difference": {
            name: abs(out[name] - linear[name]) / max(abs(out[name]), abs(linear[name]), 1.0e-300)
            for name in RESPONSE_NAMES
        },
    }


def form_factor_values(qA_GeV: float, prescription: str) -> tuple[float, float]:
    Q2 = qA_GeV * qA_GeV
    if prescription == "pointlike":
        return F1V0, F2V0
    if prescription == "bishara_linear":
        return bishara_linear(Q2)
    if prescription == "isoscalar_zexp":
        return isoscalar_zexp(Q2)
    raise ValueError(f"unknown form-factor prescription: {prescription}")


def charge_kernel_from_L00(
    L00: float,
    qA_GeV: float,
    responses: dict[str, float],
    form_factor_prescription: str,
) -> dict:
    F1, F2 = form_factor_values(qA_GeV, form_factor_prescription)
    cM, cPhi = charge_coefficients(qA_GeV, F1=F1, F2=F2)
    C_M = cM * cM * L00
    C_PhiPP = cPhi * cPhi * L00
    C_MPhiPP = 2.0 * cM * cPhi * L00
    terms = {
        "M": C_M * responses["M"],
        "PhiPP": C_PhiPP * responses["PhiPP"],
        "MPhiPP": C_MPhiPP * responses["MPhiPP"],
    }
    charge = sum(terms.values())
    pointlike_M = (F1V0 * F1V0) * L00 * responses["M"]
    finite_t_M = (cM * cM) * L00 * responses["M"]
    return {
        "F1V": F1,
        "F2V": F2,
        "cM": cM,
        "cPhiPP": cPhi,
        "terms": terms,
        "charge_sector": charge,
        "pointlike_M": pointlike_M,
        "finite_t_M": finite_t_M,
        "relative_charge_vs_pointlike_M": charge / pointlike_M - 1.0
        if pointlike_M != 0.0 else math.nan,
        "relative_finite_t_M_vs_pointlike_M": finite_t_M / pointlike_M - 1.0
        if pointlike_M != 0.0 else math.nan,
        "relative_phi_vs_finite_t_M": charge / finite_t_M - 1.0
        if finite_t_M != 0.0 else math.nan,
    }


def _l00_from_result(result: dict) -> float:
    value = result["point_nucleus_contractions"]["I00"]
    if not math.isfinite(float(value)) or value < 0.0:
        raise ValueError(f"invalid integrated L00={value}")
    return float(value)


def integrate_l00(
    *,
    mchi: float,
    ms: float,
    delta_m: float,
    mA: float,
    ER_keV: float,
    speed_kms: float,
    g2: float,
    width_scheme: str,
    nw: int,
    nz: int,
    nphi: int,
) -> dict:
    result = integrate_spin_resolved_tensor(
        mchi=mchi,
        ms=ms,
        delta_m=delta_m,
        mA=mA,
        ER=ER_keV * 1.0e-6,
        speed_kms=speed_kms,
        g2=g2,
        width_scheme=width_scheme,
        mapping="threshold_u2",
        nw=nw,
        nz=nz,
        nphi=nphi,
        crosscheck_dirac_trace=False,
    )
    if not result.get("phase_space_open", False):
        return {"phase_space_open": False}
    return {
        "phase_space_open": True,
        "L00": _l00_from_result(result),
        "qA_GeV": float(result["qA_magnitude_GeV"]),
        "quadrature_points": int(result["quadrature_points"]),
        "pole_clearance_keV": float(result["pole_clearance_keV"]),
    }


def _rate_factor(mchi: float, rho: float, mean_atomic_weight: float) -> float:
    target_nuclei_per_kg = AVOGADRO * 1000.0 / mean_atomic_weight
    return (
        (rho / mchi)
        * C_CM_S
        * target_nuclei_per_kg
        * GEV2_TO_CM2
        * 1.0e-6
        * 86400.0
    )


def mean_atomic_weight_from_input(path: Path) -> float:
    rows = read_csv(path)
    return sum(float(row["atomic_mass_u"]) * float(row["natural_atom_fraction"]) for row in rows)


def fold(
    *,
    native_dir: Path,
    mchi: float,
    ms: float,
    delta_m: float,
    mV: float,
    g2: float,
    coupling_product_squared: float,
    rho: float,
    ER_values_keV: Iterable[float],
    nv: int,
    nw: int,
    nz: int,
    nphi: int,
    form_factor_prescription: str,
    width_scheme: str,
    response_input: Path = HALO_INPUT / "natural_xenon_isotope_weights.csv",
) -> dict:
    native_bundle, native_gate = load_native_response_bundle(native_dir)
    isotope_data = load_isotope_inputs(response_input)
    mean_atomic_weight = mean_atomic_weight_from_input(response_input)
    rate_factor = _rate_factor(mchi, rho, mean_atomic_weight)

    speed_nodes, speed_weights = leggauss(nv)
    rows = []
    for ER_keV in ER_values_keV:
        ER = ER_keV * 1.0e-6
        for halo_name, pdf, vmax in (
            ("shm_cutoff", shm_truncated_pdf, 776.0),
            ("mb_untruncated", mb_untruncated_pdf, 1600.0),
        ):
            isotope_rows = []
            for A in ISOTOPES:
                xA = isotope_data[A]["abundance"]
                mA = isotope_data[A]["mA_GeV"]
                qA = exact_qA_GeV(mA, ER_keV)
                vmin = vmin_three_body_km_s(mchi, ms, mA, ER_keV)
                if vmin >= vmax:
                    isotope_rows.append({
                        "A": A, "abundance": xA, "open": False,
                        "vmin_km_s": vmin, "qA_GeV": qA,
                    })
                    continue
                vs = 0.5 * (vmax + vmin) + 0.5 * (vmax - vmin) * speed_nodes
                ws = 0.5 * (vmax - vmin) * speed_weights
                halo_charge = 0.0
                halo_pointlike = 0.0
                halo_finite_t_M = 0.0
                max_interp_difference = 0.0
                for v, w in zip(vs, ws):
                    fv = pdf(float(v))
                    if fv == 0.0:
                        continue
                    beta = float(v) / C_KM_S
                    pchi = mchi * beta / math.sqrt(1.0 - beta * beta)
                    l00_result = integrate_l00(
                        mchi=mchi, ms=ms, delta_m=delta_m, mA=mA,
                        ER_keV=ER_keV, speed_kms=float(v), g2=g2,
                        width_scheme=width_scheme, nw=nw, nz=nz, nphi=nphi,
                    )
                    if not l00_result["phase_space_open"]:
                        continue
                    response = interpolate_native_response(native_bundle[A], qA)
                    max_interp_difference = max(
                        max_interp_difference,
                        max(response["pchip_linear_relative_difference"].values()),
                    )
                    kernel = charge_kernel_from_L00(
                        l00_result["L00"], qA,
                        response["physical_equal_pn"],
                        form_factor_prescription,
                    )
                    denominator = (mV * mV + 2.0 * mA * ER) ** 2
                    common = (
                        mA * coupling_product_squared
                        / (256.0 * math.pi**3 * pchi * pchi * denominator)
                    )
                    halo_charge += float(w) * fv * beta * common * kernel["charge_sector"]
                    halo_pointlike += float(w) * fv * beta * common * kernel["pointlike_M"]
                    halo_finite_t_M += float(w) * fv * beta * common * kernel["finite_t_M"]
                isotope_rows.append({
                    "A": A, "abundance": xA, "open": True,
                    "mA_GeV": mA, "qA_GeV": qA, "vmin_km_s": vmin,
                    "charge_halo_integral": halo_charge,
                    "pointlike_M_halo_integral": halo_pointlike,
                    "finite_t_M_halo_integral": halo_finite_t_M,
                    "relative_charge_vs_pointlike_M": halo_charge / halo_pointlike - 1.0
                    if halo_pointlike else math.nan,
                    "relative_finite_t_M_vs_pointlike_M": halo_finite_t_M / halo_pointlike - 1.0
                    if halo_pointlike else math.nan,
                    "max_pchip_linear_response_difference": max_interp_difference,
                    "nv": nv, "nw": nw, "nz": nz, "nphi": nphi,
                })
            total_charge = sum(r.get("abundance", 0.0) * r.get("charge_halo_integral", 0.0) for r in isotope_rows)
            total_point = sum(r.get("abundance", 0.0) * r.get("pointlike_M_halo_integral", 0.0) for r in isotope_rows)
            total_finite = sum(r.get("abundance", 0.0) * r.get("finite_t_M_halo_integral", 0.0) for r in isotope_rows)
            total_rate = rate_factor * total_charge
            point_rate = rate_factor * total_point
            finite_rate = rate_factor * total_finite
            rows.append({
                "ER_keV": ER_keV,
                "halo_model": halo_name,
                "rate_charge_MplusPhi_events_kg_day_keV": total_rate,
                "rate_pointlike_M_events_kg_day_keV": point_rate,
                "rate_finite_t_M_events_kg_day_keV": finite_rate,
                "relative_charge_vs_pointlike_M": total_rate / point_rate - 1.0
                if point_rate else math.nan,
                "relative_finite_t_M_vs_pointlike_M": finite_rate / point_rate - 1.0
                if point_rate else math.nan,
                "relative_phi_vs_finite_t_M": total_rate / finite_rate - 1.0
                if finite_rate else math.nan,
                "open_abundance_fraction": sum(
                    r["abundance"] for r in isotope_rows if r.get("open")
                ),
                "isotope_rows": isotope_rows,
            })

    return {
        "status": "PASS_NATIVE_AFH_CHARGE_SECTOR_FOLD",
        "scope": (
            "seven-isotope natural-xenon charge-sector halo fold using native "
            "AFH M/Phi''/M-Phi'' responses and finite-t_N diagnostics; "
            "Delta/Sigma spatial sector intentionally excluded"
        ),
        "native_gate": native_gate["comparison"],
        "form_factor_prescription": form_factor_prescription,
        "width_scheme": width_scheme,
        "mchi_GeV": mchi,
        "ms_GeV": ms,
        "delta_m_GeV": delta_m,
        "mV_GeV": mV,
        "g2": g2,
        "coupling_product_squared": coupling_product_squared,
        "rho_GeV_cm3": rho,
        "isotopes": list(ISOTOPES),
        "natural_atom_fraction_coverage": sum(
            isotope_data[A]["abundance"] for A in ISOTOPES
        ),
        "response_interpolation": "PCHIP on native 0.25 MeV absolute response values; linear interpolation retained as diagnostic",
        "recoil_momentum": "q_A=sqrt(2 m_A E_R + E_R^2), exact nuclear mass-shell relation",
        "results": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mchi-GeV", type=float, default=MCHI_DEFAULT)
    parser.add_argument("--ms-keV", type=float, required=True)
    parser.add_argument("--delta-m-keV", type=float, required=True)
    parser.add_argument("--mV-GeV", type=float, default=MV_DEFAULT)
    parser.add_argument("--g2", type=float, default=G2_DEFAULT)
    parser.add_argument("--coupling-product-squared", type=float, default=COUPLING_PRODUCT_SQUARED_DEFAULT)
    parser.add_argument("--rho-GeV-cm3", type=float, default=RHO_DEFAULT)
    parser.add_argument("--ER-keV", type=float, nargs="+", required=True)
    parser.add_argument("--nv", type=int, default=8)
    parser.add_argument("--nw", type=int, default=16)
    parser.add_argument("--nz", type=int, default=12)
    parser.add_argument("--nphi", type=int, default=6)
    parser.add_argument(
        "--form-factor",
        choices=("pointlike", "bishara_linear", "isoscalar_zexp"),
        required=True,
    )
    parser.add_argument(
        "--width-scheme",
        choices=("zero", "pole", "running"),
        default="pole",
    )
    parser.add_argument(
        "--response-input",
        type=Path,
        default=HALO_INPUT / "natural_xenon_isotope_weights.csv",
    )
    args = parser.parse_args()
    if min(args.nv, args.nw, args.nz, args.nphi) < 2:
        parser.error("all quadrature orders must be >= 2")
    result = fold(
        native_dir=args.native_dir,
        mchi=args.mchi_GeV,
        ms=args.ms_keV * 1.0e-6,
        delta_m=args.delta_m_keV * 1.0e-6,
        mV=args.mV_GeV,
        g2=args.g2,
        coupling_product_squared=args.coupling_product_squared,
        rho=args.rho_GeV_cm3,
        ER_values_keV=args.ER_keV,
        nv=args.nv,
        nw=args.nw,
        nz=args.nz,
        nphi=args.nphi,
        form_factor_prescription=args.form_factor,
        width_scheme=args.width_scheme,
        response_input=args.response_input,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "form_factor_prescription": result["form_factor_prescription"],
        "n_recoil_points": len(args.ER_keV),
        "output": str(args.out),
    }, indent=2))


if __name__ == "__main__":
    main()
