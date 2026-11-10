"""Reproduce the P0-4 width-scheme sensitivity table.

Run from the repository root:
python research/figure2_full_reproduction/run_p0_4_width_scan.py

Requires Python 3 and NumPy (through eq6_kernel.py).
The running-width result is a diagnostic Breit-Wigner ansatz, not a full
fermionic self-energy calculation.
"""
from __future__ import annotations

import csv
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
sys.path.insert(0, str(HERE))
import eq6_kernel as eq6


BENCHMARKS = [
    # ms [GeV], Delta m [GeV], ER [GeV], v [km/s]
    ("ms300_dm1", 3.0e-4, 1.0e-3, 2.0e-4, 776.0),
    ("ms300_dm10", 3.0e-4, 1.0e-2, 2.0e-4, 776.0),
    ("ms360_dm1", 3.6e-4, 1.0e-3, 3.0e-4, 800.0),
    ("ms360_dm10", 3.6e-4, 1.0e-2, 3.0e-4, 800.0),
]
MCHI = 1000.0
MA = 122.0
ORDERS = (24, 24, 16)
G2_VALUES = (1.0, 3.0)


def global_wmax(mchi: float, mA: float, speed_kms: float):
    """Analytic maximum of W_max^2 over ER >= 0 for fixed speed."""
    beta = speed_kms / eq6.C_KM_S
    gamma = 1.0 / (1.0 - beta * beta) ** 0.5
    energy = mchi * gamma
    momentum = mchi * gamma * beta
    c = energy + mA
    x = mA * c / (c * c - momentum * momentum) ** 0.5
    er_star = x - mA
    q_star = (x * x - mA * mA) ** 0.5
    w2 = mchi * mchi + 2.0 * momentum * q_star - 2.0 * c * er_star
    return er_star, w2 ** 0.5


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    nW, nz, nphi = ORDERS
    rows = []
    for label, ms, dm, er, speed in BENCHMARKS:
        wmin2, wmax2 = eq6.limits(MCHI, ms, MA, er, speed)
        mchi2 = MCHI + dm
        wmin, wmax = wmin2 ** 0.5, wmax2 ** 0.5
        zero = eq6.reduced_kernel(
            MCHI, ms, dm, MA, er, speed,
            nw=nW, nz=nz, nphi=nphi, width_scheme="zero"
        )
        rows.append({
            "benchmark": label, "ms_keV": ms * 1e6, "delta_m_MeV": dm * 1e3,
            "ER_keV": er * 1e6, "v_km_s": speed, "g2": 0.0,
            "width_scheme": "zero", "Gamma_pole_MeV": 0.0,
            "Gamma_run_at_Wmax_MeV": 0.0, "I6_GeV2": zero,
            "relative_change_percent": 0.0, "Wmin_GeV": wmin,
            "Wmax_GeV": wmax, "mchi2_GeV": mchi2,
            "pole_gap_keV": (mchi2 - wmax) * 1e6,
            "nW": nW, "nz": nz, "nphi": nphi,
        })
        for g2 in G2_VALUES:
            gamma_pole = eq6.chi2_width_dirac_scalar(MCHI, ms, dm, g2)
            gamma_run_max = eq6.chi2_width_dirac_scalar_at_mass(
                wmax, MCHI, ms, g2
            )
            for scheme in ("pole", "running"):
                value = eq6.reduced_kernel(
                    MCHI, ms, dm, MA, er, speed,
                    nw=nW, nz=nz, nphi=nphi,
                    width_scheme=scheme, g2=g2
                )
                rows.append({
                    "benchmark": label, "ms_keV": ms * 1e6,
                    "delta_m_MeV": dm * 1e3, "ER_keV": er * 1e6,
                    "v_km_s": speed, "g2": g2, "width_scheme": scheme,
                    "Gamma_pole_MeV": gamma_pole * 1e3,
                    "Gamma_run_at_Wmax_MeV": gamma_run_max * 1e3,
                    "I6_GeV2": value,
                    "relative_change_percent": 100.0 * (value / zero - 1.0),
                    "Wmin_GeV": wmin, "Wmax_GeV": wmax,
                    "mchi2_GeV": mchi2,
                    "pole_gap_keV": (mchi2 - wmax) * 1e6,
                    "nW": nW, "nz": nz, "nphi": nphi,
                })

    out = RESULTS / "P0-4_WIDTH_SENSITIVITY.csv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    speeds = (544.0, 600.0, 770.0, 776.0, 800.0)
    wrows = []
    for speed in speeds:
        er_star, wmax = global_wmax(MCHI, MA, speed)
        wrows.append({
            "v_km_s": speed,
            "ER_at_global_Wmax_keV": er_star * 1e6,
            "max_sqrt_Wmax2_minus_mchi_keV": (wmax - MCHI) * 1e6,
            "minimum_gap_for_delta_m_1MeV_keV": (MCHI + 1e-3 - wmax) * 1e6,
            "minimum_gap_for_delta_m_10MeV_keV": (MCHI + 1e-2 - wmax) * 1e6,
        })
    out2 = RESULTS / "P0-4_GLOBAL_WMAX_CHECK.csv"
    with out2.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(wrows[0]))
        writer.writeheader()
        writer.writerows(wrows)

    print(f"Wrote {out}")
    print(f"Wrote {out2}")


if __name__ == "__main__":
    main()
