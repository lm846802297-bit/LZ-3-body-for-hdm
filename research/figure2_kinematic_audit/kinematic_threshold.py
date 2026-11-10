#!/usr/bin/env python3
"""Independent kinematic support check for Fig. 2 of 3body-for-HDM.

Tests whether chi1 + Xe -> chi1 + Xe + s has non-empty three-body phase
space using the W_max expression printed in the manuscript. This is NOT
a calculation of dR/dE_R and does not reproduce the vertical event-rate
normalization or full spectral curves.

Units: GeV internally; km/s for speeds; keV in output tables.
"""
from __future__ import annotations
import csv
from pathlib import Path
import numpy as np
from scipy.optimize import brentq, minimize_scalar

M_CHI_GEV = 1000.0
M_XE_GEV = 122.0  # approximate Xe-131 nuclear mass
C_KM_S = 299_792.458
SPEEDS_KM_S = (544.0, 600.0, 770.0, 776.0, 800.0)
SCALAR_MASSES_KEV = (200.0, 300.0, 360.0, 300_000.0, 360_000.0)


def wmax_squared(er_gev: float, speed_km_s: float) -> float:
    beta = speed_km_s / C_KM_S
    gamma = 1.0 / np.sqrt(1.0 - beta * beta)
    energy_chi = M_CHI_GEV * gamma
    momentum_chi = energy_chi * beta
    return (
        M_CHI_GEV**2
        + 2.0 * momentum_chi * np.sqrt(2.0 * M_XE_GEV * er_gev + er_gev**2)
        - 2.0 * (energy_chi + M_XE_GEV) * er_gev
    )


def max_scalar_mass_kev(er_kev: float, speed_km_s: float) -> float:
    w2 = wmax_squared(er_kev / 1.0e6, speed_km_s)
    if w2 <= 0.0:
        return float("nan")
    return (np.sqrt(w2) - M_CHI_GEV) * 1.0e6


def optimize_mass(speed_km_s: float) -> tuple[float, float]:
    result = minimize_scalar(
        lambda er: -max_scalar_mass_kev(er, speed_km_s),
        bounds=(1.0, 1000.0), method="bounded",
        options={"xatol": 1.0e-10},
    )
    return -float(result.fun), float(result.x)


def allowed_recoil_roots(ms_kev: float, speed_km_s: float) -> list[float]:
    grid = np.linspace(0.1, 1000.0, 20_000)
    vals = np.array([max_scalar_mass_kev(er, speed_km_s) - ms_kev for er in grid])
    roots: list[float] = []
    for i in range(len(grid) - 1):
        if np.isfinite(vals[i]) and np.isfinite(vals[i + 1]) and vals[i] * vals[i + 1] < 0:
            roots.append(float(brentq(
                lambda er: max_scalar_mass_kev(er, speed_km_s) - ms_kev,
                grid[i], grid[i + 1], xtol=1.0e-11,
            )))
    return roots


def minimum_speed_for_mass(ms_kev: float) -> tuple[float, float]:
    speed = brentq(lambda v: optimize_mass(v)[0] - ms_kev, 100.0, 1500.0)
    return float(speed), optimize_mass(float(speed))[1]


def main() -> None:
    out = Path(__file__).resolve().parent
    rows = []
    for speed in SPEEDS_KM_S:
        mmax, er_at_max = optimize_mass(speed)
        for ms in SCALAR_MASSES_KEV:
            roots = allowed_recoil_roots(ms, speed)
            rows.append({
                "speed_km_s": speed,
                "max_allowed_ms_keV": mmax,
                "ER_at_max_ms_keV": er_at_max,
                "tested_ms_keV": ms,
                "phase_space_nonempty": bool(mmax >= ms),
                "ER_lower_boundary_keV": roots[0] if roots else "",
                "ER_upper_boundary_keV": roots[-1] if len(roots) > 1 else "",
            })
    with (out / "phase_space_threshold.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print("m_chi = %.1f GeV; m_Xe = %.1f GeV" % (M_CHI_GEV, M_XE_GEV))
    print("speed  max(ms)  ER@max   ms=300keV ER support   ms=360keV ER support")
    for speed in SPEEDS_KM_S:
        mmax, ermax = optimize_mass(speed)
        supports = []
        for ms in (300.0, 360.0):
            roots = allowed_recoil_roots(ms, speed)
            supports.append("none" if not roots else "%.1f..%.1f" % (roots[0], roots[-1]))
        print("%5.0f  %7.1f  %7.1f   %-18s %-18s" % (speed, mmax, ermax, *supports))
    for ms in (200.0, 300.0, 360.0):
        vmin, er = minimum_speed_for_mass(ms)
        print("minimum speed for ms=%g keV: %.2f km/s (optimal ER=%.2f keV)" % (ms, vmin, er))


if __name__ == "__main__":
    main()
