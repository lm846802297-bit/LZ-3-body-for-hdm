#!/usr/bin/env python3
"""Reproduce the supplied g1=g2=gVN=1, Delta-m=450 keV benchmark.

The user supplied the particle/coupling benchmark. Since no recoil and halo
kinematics were specified with it, this script explicitly reuses the
established Eq. (6) diagnostic point (mA=122 GeV, ER=200 keV,
v=776 km/s, W2 midpoint, z=0.2, phi*=1.1). This is a reproducible
numerical check, not a claim that those kinematics were in the source caption.

The finite-width result is conditional on the Dirac / pure-scalar /
chi2 -> chi1 s-only width used by eq6_kernel.py. It is not the full
vector-plus-scalar chi2 self-energy.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import eq6_kernel as eq6

# Supplied benchmark: all masses/energies are in GeV internally.
G1 = 1.0
G2 = 1.0
GVN = 1.0
MCHI1 = 1000.0
DELTA_M = 450.0e-6
MCHI2 = MCHI1 + DELTA_M
MV = 10.0
MS = 300.0e-6

# Explicitly inherited diagnostic kinematics, not part of the supplied set.
MA = 122.0
ER = 200.0e-6
SPEED_KM_S = 776.0
Z = 0.2
PHI = 1.1


def calculate_benchmark(nw: int = 48, nz: int = 40, nphi: int = 24) -> dict:
    wmin2, wmax2 = eq6.limits(MCHI1, MS, MA, ER, SPEED_KM_S)
    if wmax2 <= wmin2:
        raise ArithmeticError("The selected diagnostic point has closed phase space.")
    w2 = 0.5 * (wmin2 + wmax2)
    point = eq6.build_point(MCHI1, MS, MA, ER, SPEED_KM_S, w2, Z, PHI)

    # L00 is defined in the target-rest frame by eq6_kernel's construction.
    trace_zero = eq6.spin_trace(point, MCHI1, MCHI2, width=0.0)
    pole_width = eq6.chi2_width_dirac_scalar(MCHI1, MS, DELTA_M, G2)
    trace_pole = eq6.spin_trace(point, MCHI1, MCHI2, width=pole_width)

    i6_zero = eq6.reduced_kernel(
        MCHI1, MS, DELTA_M, MA, ER, SPEED_KM_S,
        nw=nw, nz=nz, nphi=nphi, width_scheme="zero",
    )
    i6_pole = eq6.reduced_kernel(
        MCHI1, MS, DELTA_M, MA, ER, SPEED_KM_S,
        nw=nw, nz=nz, nphi=nphi, width_scheme="pole", g2=G2,
    )

    beta = SPEED_KM_S / eq6.C_KM_S
    gamma = 1.0 / math.sqrt(1.0 - beta * beta)
    pchi = MCHI1 * gamma * beta
    coupling_product_sq = (G1 * G2 * GVN) ** 2
    prefactor_over_RA = (
        MA * coupling_product_sq
        / (256.0 * math.pi**3 * pchi**2 * (MV**2 + 2.0 * MA * ER)**2)
    )

    return {
        "benchmark": {
            "g1": G1,
            "g2": G2,
            "gVN": GVN,
            "coupling_product_squared": coupling_product_sq,
            "mchi1_GeV": MCHI1,
            "mchi2_GeV": MCHI2,
            "delta_m_keV": DELTA_M * 1.0e6,
            "mV_GeV": MV,
            "ms_keV": MS * 1.0e6,
        },
        "inherited_diagnostic_kinematics": {
            "mA_GeV": MA,
            "ER_keV": ER * 1.0e6,
            "speed_km_s": SPEED_KM_S,
            "W2_GeV2": w2,
            "z": Z,
            "phi_rad": PHI,
            "frame": "target rest frame",
        },
        "phase_space": {
            "Wmin2_GeV2": wmin2,
            "Wmax2_GeV2": wmax2,
            "sqrt_Wmax_GeV": math.sqrt(wmax2),
            "mchi2_minus_sqrt_Wmax_keV": (MCHI2 - math.sqrt(wmax2)) * 1.0e6,
            "mchi2_squared_minus_Wmax2_GeV2": MCHI2**2 - wmax2,
            "on_shell_chi2_accessible": bool(wmax2 >= MCHI2**2),
        },
        "conditional_scalar_width": {
            "Gamma_chi2_GeV": pole_width,
            "Gamma_chi2_keV": pole_width * 1.0e6,
            "assumptions": [
                "Dirac chi1 and chi2",
                "pure scalar g2 vertex",
                "chi2 -> chi1 s is the only open decay channel",
                "vector-sector self-energy contribution not included",
            ],
        },
        "L00_at_W2_midpoint": {
            "zero_width": trace_zero,
            "conditional_scalar_pole_width": trace_pole,
            "relative_pole_vs_zero": trace_pole["total"] / trace_zero["total"] - 1.0,
        },
        "Eq6_integral": {
            "quadrature": {"nw": nw, "nz": nz, "nphi": nphi},
            "I6_zero_width_GeV2": i6_zero,
            "I6_conditional_scalar_pole_width_GeV2": i6_pole,
            "relative_pole_vs_zero": i6_pole / i6_zero - 1.0,
        },
        "differential_cross_section": {
            "prefactor_times_I6_over_RA_GeVminus3_zero_width": prefactor_over_RA * i6_zero,
            "prefactor_times_I6_over_RA_GeVminus3_pole_width": prefactor_over_RA * i6_pole,
            "note": "Multiply by the separately supplied dimensionless nuclear response R_A(ER).",
        },
        "interpretation": [
            "L00 is the initial-spin-averaged and final-spin-summed Dirac trace.",
            "g1, gVN and mV do not enter L00 itself; they enter the full cross-section prefactor.",
            "g2 enters L00 only through the finite-width prescription used here.",
            "The numerical L00 point depends on the explicitly listed inherited kinematics.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nw", type=int, default=48)
    parser.add_argument("--nz", type=int, default=40)
    parser.add_argument("--nphi", type=int, default=24)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = calculate_benchmark(args.nw, args.nz, args.nphi)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
