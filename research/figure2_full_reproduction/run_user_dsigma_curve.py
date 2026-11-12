#!/usr/bin/env python3
"""Fixed-speed Xe-131 d sigma/dER curve for the supplied 450 keV benchmark.

This is an exploratory, fixed-speed diagnostic. The Xe-131 mass uses A*u
through joint_xe131.isotope_mass_GeV, not the AME2020 exact isotope mass.
The response is interpolated from the archived GCN/JJ55 tables with PCHIP.
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eq6_kernel


def recoil_interval(mchi_GeV: float, ms_GeV: float, mA_GeV: float,
                    ER_GeV: float, speed_km_s: float) -> tuple[float, float]:
    """Return (W_min^2, W_max^2); Delta m is not an argument of these limits."""
    return eq6_kernel.limits(mchi_GeV, ms_GeV, mA_GeV, ER_GeV, speed_km_s)


def dsigma_GeVminus3_to_cm2_per_keV(value: float) -> float:
    """Convert d sigma / d E from GeV^-3 to cm^2/keV."""
    return value * 0.3893793721e-27 * 1.0e-6


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--response-dir", type=Path,
        default=HERE / "results" / "anand_wm_response",
    )
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--nw", type=int, default=20)
    ap.add_argument("--nz", type=int, default=16)
    ap.add_argument("--nphi", type=int, default=12)
    ap.add_argument("--step-keV", type=float, default=5.0)
    args = ap.parse_args()

    if not math.isfinite(args.step_keV) or args.step_keV <= 0.0:
        ap.error("--step-keV must be finite and positive")
    if min(args.nw, args.nz, args.nphi) < 1:
        ap.error("--nw, --nz, and --nphi must all be positive")

    # Import the response reader only for an actual calculation. This keeps
    # the kinematic/unit helpers independently testable without response data.
    from joint_xe131 import isotope_mass_GeV, load_nuclear_response

    A = 131
    mA = isotope_mass_GeV(A)  # A*u approximation, not AME2020 exact mass
    mchi = 1000.0
    delta_m = 450.0e-6
    ms = 300.0e-6
    mchi2 = mchi + delta_m
    mV = 10.0
    speed_km_s = 776.0
    coupling_product_sq = 1.0

    beta = speed_km_s / eq6_kernel.C_KM_S
    pchi = mchi * beta / math.sqrt(1.0 - beta * beta)
    responses = {
        model: load_nuclear_response(
            args.response_dir / f"xe{A}_{model.upper()}_WM.csv", A, model
        )
        for model in ("gcn", "jj55")
    }

    # The common grid covers the open interval; closed points are omitted.
    recoil_energies_keV = np.arange(130.0, 671.0, args.step_keV)
    rows = []
    for er_keV in recoil_energies_keV:
        ER = float(er_keV) * 1.0e-6
        wmin2, wmax2 = recoil_interval(mchi, ms, mA, ER, speed_km_s)
        if wmax2 <= wmin2:
            continue

        I6 = eq6_kernel.reduced_kernel(
            mchi, ms, delta_m, mA, ER, speed_km_s,
            nw=args.nw, nz=args.nz, nphi=args.nphi,
            width_scheme="zero",
        )
        denominator = (mV * mV + 2.0 * mA * ER) ** 2
        for model, response in responses.items():
            RA, q_response = response.at_recoil(ER, mA)
            dsigma = (
                mA * coupling_product_sq * RA * I6
                / (256.0 * math.pi**3 * pchi**2 * denominator)
            )
            rows.append({
                "A": A,
                "model": model.upper(),
                "mass_scheme": "A*u approximate; not AME2020",
                "mA_GeV": mA,
                "ER_keV": float(er_keV),
                "q_GeV": q_response,
                "RA": RA,
                "I6_GeV2": I6,
                "pchi_GeV": pchi,
                "mV_GeV": mV,
                "coupling_product_sq": coupling_product_sq,
                "speed_km_s": speed_km_s,
                "width_scheme": "zero",
                "dsigma_dER_GeVminus3": dsigma,
                "dsigma_dER_cm2_per_keV": dsigma_GeVminus3_to_cm2_per_keV(dsigma),
            })

    if not rows:
        raise RuntimeError(
            "No open recoil points were generated; check the scan range and kinematics."
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(
        f"rows={len(rows)}; ER range={rows[0]['ER_keV']}.."
        f"{rows[-1]['ER_keV']} keV"
    )
    print(
        f"Xe-131 mA={mA:.12g} GeV (A*u approximation); "
        f"pchi={pchi:.12g} GeV; mchi2={mchi2:.12g} GeV"
    )
    for model in ("GCN", "JJ55"):
        model_rows = [row for row in rows if row["model"] == model]
        maximum = max(model_rows, key=lambda row: row["dsigma_dER_GeVminus3"])
        print(
            f"{model}: max dσ/dER={maximum['dsigma_dER_GeVminus3']:.12e} "
            f"GeV^-3 at ER={maximum['ER_keV']} keV"
        )


if __name__ == "__main__":
    main()
