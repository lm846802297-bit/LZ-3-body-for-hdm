#!/usr/bin/env python3
"""Fixed-speed recoil-spectrum scan with zero, pole and running chi2 widths.

The output is a coherent point-charge-current spectrum kernel. The nuclear
form factor is factored out, and internal nuclear spin/orbital currents are
not yet included. It is designed to test whether finite width changes the
recoil dependence, not to claim a final AFH/LZ event spectrum.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KERNEL_DIR = ROOT / "research" / "three_body_calculation_and_validation"
AUDIT_DIR = ROOT / "research" / "vector_current_response_audit"
for path in (KERNEL_DIR, AUDIT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import eq6_kernel as eq6  # noqa: E402
import vector_current_response_audit as vca  # noqa: E402

MCHI = 1000.0
MS = 300.0e-6
M_A = 131.0 * 0.93149410242
SPEED = 776.0
M_V = 10.0

CASES = (
    {
        "name": "reference_dm450_g2_1",
        "delta_m": 450.0e-6,
        "g2": 1.0,
        "energies_keV": (130.0, 160.0, 200.0, 240.0, 280.0, 320.0, 360.0, 400.0),
        "mapping": "threshold_u2",
    },
    {
        "name": "reference_dm1MeV_g2_1",
        "delta_m": 1.0e-3,
        "g2": 1.0,
        "energies_keV": (130.0, 160.0, 200.0, 240.0, 280.0, 320.0, 360.0, 400.0),
        "mapping": "threshold_u2",
    },
    {
        "name": "near_pole_dm362_g2_0p1",
        "delta_m": 362.0e-6,
        "g2": 0.1,
        "energies_keV": (200.0, 230.0, 250.0, 260.0, 267.0, 270.0, 272.0, 274.0, 274.5),
        "mapping": "sine2",
    },
    {
        "name": "near_pole_dm362_g2_1",
        "delta_m": 362.0e-6,
        "g2": 1.0,
        "energies_keV": (200.0, 230.0, 250.0, 260.0, 267.0, 270.0, 272.0, 274.0, 274.5),
        "mapping": "sine2",
    },
)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty result: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def integrate(case: dict, er_keV: float, scheme: str, orders: tuple[int, int, int]) -> dict:
    result = vca.integrate_current_components(
        mchi=MCHI,
        ms=MS,
        delta_m=case["delta_m"],
        mA=M_A,
        ER=er_keV * 1.0e-6,
        speed_kms=SPEED,
        g2=case["g2"],
        width_scheme=scheme,
        mapping=case["mapping"],
        nw=orders[0],
        nz=orders[1],
        nphi=orders[2],
    )
    return result


def run(outdir: Path) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    raw_rows: list[dict] = []
    lookup: dict[tuple[str, float, str], dict] = {}

    for case in CASES:
        for er_keV in case["energies_keV"]:
            wmin2, wmax2 = eq6.limits(
                MCHI, MS, M_A, er_keV * 1.0e-6, SPEED
            )
            if wmax2 <= wmin2:
                raw_rows.append({
                    "benchmark": case["name"], "ER_keV": er_keV,
                    "width_scheme": "all", "phase_space_open": False,
                    "status": "closed_phase_space",
                })
                continue
            pole_mass = MCHI + case["delta_m"]
            pole_clearance_keV = (pole_mass - math.sqrt(wmax2)) * 1.0e6
            if pole_clearance_keV <= 0.0:
                raw_rows.append({
                    "benchmark": case["name"], "ER_keV": er_keV,
                    "width_scheme": "all", "phase_space_open": True,
                    "pole_clearance_keV": pole_clearance_keV,
                    "status": "on_shell_chi2_accessible_not_in_offshell_scan",
                })
                continue

            near = case["mapping"] == "sine2"
            for scheme in ("zero", "pole", "running"):
                if near and scheme == "zero" and er_keV >= 274.0:
                    # The zero-width integrand becomes sharply endpoint-peaked
                    # as Wmax approaches mchi2. Increase nW for the diagnostic
                    # baseline rather than silently comparing an under-resolved
                    # zero-width value with the converged finite-width result.
                    orders = (160, 20, 10)
                else:
                    orders = (48, 12, 6) if near else (24, 12, 6)
                result = integrate(case, er_keV, scheme, orders)
                gamma_pole_keV = result["Gamma_chi2_keV"]
                mV_denominator = (
                    M_V * M_V + 2.0 * M_A * er_keV * 1.0e-6
                ) ** 2
                point_kernel = M_A * result["Ifull"] / mV_denominator
                charge_kernel = M_A * result["Icharge"] / mV_denominator
                row = {
                    "benchmark": case["name"],
                    "delta_m_keV": case["delta_m"] * 1.0e6,
                    "g2": case["g2"],
                    "ER_keV": er_keV,
                    "qA_GeV": result["qA_GeV"],
                    "pole_clearance_keV": pole_clearance_keV,
                    "Gamma_pole_keV": gamma_pole_keV,
                    "pole_clearance_over_Gamma": (
                        pole_clearance_keV / gamma_pole_keV
                        if gamma_pole_keV > 0 else math.inf
                    ),
                    "width_scheme": scheme,
                    "mapping": case["mapping"],
                    "nw": orders[0], "nz": orders[1], "nphi": orders[2],
                    "I00": result["I00"],
                    "Icharge": result["Icharge"],
                    "Ifull_point_nucleus": result["Ifull"],
                    "full_over_charge": result["Ifull"] / result["Icharge"],
                    "full_minus_charge_ppm": (
                        result["Ifull"] / result["Icharge"] - 1.0
                    ) * 1.0e6,
                    "point_charge_dsigma_kernel_mV10": point_kernel,
                    "charge_only_dsigma_kernel_mV10": charge_kernel,
                    "phase_space_open": True,
                    "status": "off_shell",
                }
                raw_rows.append(row)
                lookup[(case["name"], er_keV, scheme)] = row

    # Attach zero-width ratios and normalize each spectrum at ER=200 keV.
    for row in raw_rows:
        if row.get("status") != "off_shell":
            continue
        key = (row["benchmark"], row["ER_keV"])
        zero = lookup[(key[0], key[1], "zero")]
        row["Ifull_over_zero_width"] = (
            row["Ifull_point_nucleus"] / zero["Ifull_point_nucleus"]
        )
        row["Icharge_over_zero_width"] = row["Icharge"] / zero["Icharge"]
        ref = lookup.get((key[0], 200.0, row["width_scheme"]))
        row["spectrum_shape_over_200keV"] = (
            row["point_charge_dsigma_kernel_mV10"]
            / ref["point_charge_dsigma_kernel_mV10"]
            if ref else None
        )

    # High-order convergence at the two most sensitive near-pole points.
    convergence = []
    near_case = next(case for case in CASES if case["name"] == "near_pole_dm362_g2_1")
    for er_keV in (267.0, 274.0, 274.5):
        for scheme in ("zero", "pole", "running"):
            if scheme == "zero" and er_keV == 274.5:
                order_pairs = (
                    ((80, 16, 8), (160, 20, 10)),
                    ((160, 20, 10), (240, 24, 12)),
                )
            elif scheme == "zero" and er_keV == 274.0:
                order_pairs = (
                    ((48, 12, 6), (80, 16, 8)),
                    ((80, 16, 8), (160, 20, 10)),
                )
            else:
                order_pairs = (((48, 12, 6), (80, 16, 8)),)
            for low_order, high_order in order_pairs:
                low = integrate(near_case, er_keV, scheme, low_order)
                high = integrate(near_case, er_keV, scheme, high_order)
                for key in ("I00", "Icharge", "Ifull"):
                    relative_difference = abs(high[key] / low[key] - 1.0)
                    convergence.append({
                        "ER_keV": er_keV,
                        "width_scheme": scheme,
                        "observable": key,
                        "order_low": "x".join(map(str, low_order)),
                        "order_high": "x".join(map(str, high_order)),
                        "relative_difference": relative_difference,
                        "status": (
                            "converged_at_1e-7"
                            if relative_difference < 1.0e-7
                            else "requires_higher_order"
                        ),
                    })

    csv_path = outdir / "finite_width_recoil_spectrum.csv"
    conv_path = outdir / "near_pole_quadrature_convergence.csv"
    write_csv(csv_path, raw_rows)
    write_csv(conv_path, convergence)

    summary_cases = []
    for case in CASES:
        selected = [
            row for row in raw_rows
            if row.get("benchmark") == case["name"] and row.get("status") == "off_shell"
        ]
        if not selected:
            continue
        at_200 = {
            scheme: lookup[(case["name"], 200.0, scheme)]
            for scheme in ("zero", "pole", "running")
        }
        pole_ratios = [
            row["Ifull_over_zero_width"] for row in selected
            if row["width_scheme"] == "pole"
        ]
        summary_cases.append({
            "benchmark": case["name"],
            "delta_m_keV": case["delta_m"] * 1.0e6,
            "g2": case["g2"],
            "ER_200keV": {
                scheme: {
                    "Ifull": at_200[scheme]["Ifull_point_nucleus"],
                    "Ifull_over_zero": at_200[scheme]["Ifull_over_zero_width"],
                    "full_over_charge": at_200[scheme]["full_over_charge"],
                }
                for scheme in ("zero", "pole", "running")
            },
            "pole_width_ratio_min": min(pole_ratios),
            "pole_width_ratio_max": max(pole_ratios),
            "ER_range_keV": [
                min(row["ER_keV"] for row in selected),
                max(row["ER_keV"] for row in selected),
            ],
        })

    summary = {
        "status": "fixed_speed_point_nucleus_finite_width_spectrum_diagnostic",
        "parameters": {
            "mchi_GeV": MCHI, "ms_keV": MS * 1.0e6,
            "mA_GeV": M_A, "speed_km_s": SPEED, "mV_reference_GeV": M_V,
        },
        "width_schemes": {
            "zero": "diagnostic only",
            "pole": "current manuscript Breit-Wigner denominator; conditional scalar-only Dirac width",
            "running": "one-loop scalar-channel absorptive-width diagnostic; not the complete model self-energy",
        },
        "spectrum_definition": (
            "K_point(ER)=mA*Ifull/(mV^2+2*mA*ER)^2, with F_A(q^2) factored out; "
            "ratios between widths are exact for a common nuclear form factor"
        ),
        "cases": summary_cases,
        "near_pole_quadrature_convergence": convergence,
        "limitations": [
            "Fixed-speed kernel, not a halo-folded event rate.",
            "Coherent point-nucleus current includes centre-of-mass convection only.",
            "Internal nuclear magnetization and orbital currents (AFH Sigma', Sigma'', Delta) are not included.",
            "The scalar-only conditional width assumes Dirac chi fields, a real scalar, a pure scalar Yukawa vertex and no other open chi2 decay channels.",
            "The model's vector-sector real self-energy and any additional channels are not included.",
            "No detector response, efficiency, exposure, or likelihood is included.",
            "Any recoil point with Wmax >= mchi2 is excluded from the off-shell scan and flagged separately.",
        ],
    }
    summary_path = outdir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    sums = outdir / "SHA256SUMS.txt"
    sums.write_text(
        f"{sha256(csv_path)}  {csv_path.name}\n"
        f"{sha256(conv_path)}  {conv_path.name}\n"
        f"{sha256(summary_path)}  {summary_path.name}\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": summary["status"],
        "rows": len(raw_rows),
        "convergence_checks": len(convergence),
        "summary": str(summary_path),
    }, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    run(args.outdir.resolve())


if __name__ == "__main__":
    main()
