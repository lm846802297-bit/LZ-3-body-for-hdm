#!/usr/bin/env python3
"""Pole width for the two-body decay chi2 -> chi1 + s.

All masses and the returned width are in GeV. The coupling g2 is
dimensionless. The formula assumes spin-1/2 Dirac fermions and a pure
scalar off-diagonal Yukawa interaction.
"""

from __future__ import annotations

import argparse
import math
from typing import Union

Coupling = Union[float, complex]


def _validate_inputs(
    m_chi1_GeV: float,
    delta_m_GeV: float,
    m_s_GeV: float,
    g2: Coupling,
) -> None:
    values = (m_chi1_GeV, delta_m_GeV, m_s_GeV)
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("Mass inputs must be finite real numbers.")
    if m_chi1_GeV <= 0.0:
        raise ValueError("m_chi1_GeV must be positive.")
    if delta_m_GeV < 0.0:
        raise ValueError("delta_m_GeV must be non-negative.")
    if m_s_GeV < 0.0:
        raise ValueError("m_s_GeV must be non-negative.")
    if not math.isfinite(abs(g2)):
        raise ValueError("g2 must be finite.")


def chi2_to_chi1s_width_GeV(
    m_chi1_GeV: float,
    delta_m_GeV: float,
    m_s_GeV: float,
    g2: Coupling,
) -> float:
    """Return Gamma(chi2 -> chi1 s) in GeV.

    The implementation uses a factorized Kallen function to avoid
    subtracting nearly equal O(m_chi1**4) quantities when delta_m and m_s
    are sub-MeV while m_chi1 is at the TeV scale.

    If delta_m <= m_s, the two-body channel is kinematically closed and
    the returned partial width is exactly zero.
    """
    _validate_inputs(m_chi1_GeV, delta_m_GeV, m_s_GeV, g2)
    if delta_m_GeV <= m_s_GeV:
        return 0.0

    m_chi2_GeV = m_chi1_GeV + delta_m_GeV
    delta_phase_space = delta_m_GeV**2 - m_s_GeV**2
    heavy_factor = (2.0 * m_chi1_GeV + delta_m_GeV) ** 2 - m_s_GeV**2

    return (
        abs(g2) ** 2
        * math.sqrt(delta_phase_space)
        * heavy_factor ** 1.5
        / (16.0 * math.pi * m_chi2_GeV**3)
    )


def chi2_to_chi1s_width_heavy_limit_GeV(
    m_chi1_GeV: float,
    delta_m_GeV: float,
    m_s_GeV: float,
    g2: Coupling,
) -> float:
    """Return the m_chi1 >> delta_m, m_s approximation in GeV."""
    _validate_inputs(m_chi1_GeV, delta_m_GeV, m_s_GeV, g2)
    if delta_m_GeV <= m_s_GeV:
        return 0.0
    return (
        abs(g2) ** 2
        / (2.0 * math.pi)
        * math.sqrt(delta_m_GeV**2 - m_s_GeV**2)
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute the pole partial width chi2 -> chi1 + s."
    )
    parser.add_argument("--mchi1", type=float, required=True, help="m_chi1 in GeV")
    parser.add_argument("--delta-m", type=float, required=True, help="Delta m in GeV")
    parser.add_argument("--ms", type=float, required=True, help="m_s in GeV")
    parser.add_argument("--g2", type=float, required=True, help="dimensionless |g2|")
    args = parser.parse_args()

    exact = chi2_to_chi1s_width_GeV(args.mchi1, args.delta_m, args.ms, args.g2)
    approx = chi2_to_chi1s_width_heavy_limit_GeV(
        args.mchi1, args.delta_m, args.ms, args.g2
    )
    is_open = args.delta_m > args.ms

    print(f"m_chi2 = {args.mchi1 + args.delta_m:.12g} GeV")
    print(f"two-body channel open = {is_open}")
    print(f"Gamma_exact = {exact:.12e} GeV = {exact * 1.0e6:.9f} keV")
    print(f"Gamma_heavy_limit = {approx:.12e} GeV = {approx * 1.0e6:.9f} keV")
    if exact > 0.0:
        rel = (approx - exact) / exact
        print(f"(approx - exact) / exact = {rel:.9e}")


if __name__ == "__main__":
    main()
