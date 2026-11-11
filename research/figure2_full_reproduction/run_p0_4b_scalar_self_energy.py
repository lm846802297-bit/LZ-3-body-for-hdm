"""Run the P0-4b one-loop chi2 scalar-channel self-energy audit.

From the repository root:
  python research/figure2_full_reproduction/run_p0_4b_scalar_self_energy.py

Outputs two CSV files under results/. Requires NumPy.
This is the complete one-loop contribution from chi1+s under the explicit
Dirac / real-scalar / pure-scalar-Yukawa assumptions. It is not yet the
full model self-energy because the chi1+V loop needs mV and a gauge completion.
"""
from __future__ import annotations

import csv
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
sys.path.insert(0, str(HERE))

import eq6_kernel as eq6
import chi2_scalar_self_energy as se


MCHI1 = 1000.0
MA = 122.0
MU_R = 1000.0
G2_VALUES = (0.1, 1.0, 3.0)
BENCHMARKS = (
    ("ms300_dm1", 0.0003, 0.001, 0.0002, 776.0),
    ("ms300_dm10", 0.0003, 0.010, 0.0002, 776.0),
    ("ms360_dm1", 0.00036, 0.001, 0.0003, 800.0),
    ("ms360_dm10", 0.00036, 0.010, 0.0003, 800.0),
)


def write_csv(path: Path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    pole_rows = []
    denominator_rows = []

    for label, ms, dm, er, speed in BENCHMARKS:
        M = MCHI1 + dm
        wmin2, wmax2 = eq6.limits(MCHI1, ms, MA, er, speed)
        Wmax = wmax2 ** 0.5

        for g2 in G2_VALUES:
            pole = se.chi2_scalar_self_energy(M, MCHI1, ms, g2, MU_R)
            cts = se.on_shell_counterterms(MCHI1, ms, dm, g2, MU_R)
            width_tree = se.scalar_two_body_width(M, MCHI1, ms, g2)
            pole_rows.append({
                "benchmark": label,
                "mchi1_GeV": MCHI1,
                "ms_keV": ms * 1e6,
                "delta_m_MeV": dm * 1e3,
                "mchi2_pole_GeV": M,
                "g2": g2,
                "muR_GeV": MU_R,
                "B0_re_MSbar": pole.B0.real,
                "B0_im": pole.B0.imag,
                "B1_re_MSbar": pole.B1.real,
                "B1_im": pole.B1.imag,
                "SigmaV_re": pole.sigma_V.real,
                "SigmaV_im": pole.sigma_V.imag,
                "SigmaS_re_GeV": pole.sigma_S.real,
                "SigmaS_im_GeV": pole.sigma_S.imag,
                "deltaM_MSbar_re_GeV": pole.delta_M.real,
                "deltaM_MSbar_im_GeV": pole.delta_M.imag,
                "Gamma_from_cut_MeV": pole.gamma_from_cut * 1e3,
                "Gamma_2body_MeV": width_tree * 1e3,
                "delta_m_OS_counterterm_GeV": cts["delta_m_ct"],
                "deltaZ_OS": cts["delta_Z"],
                "one_loop_control_warning": abs(cts["delta_Z"]) >= 1.0,
            })

            os_at_max = se.on_shell_inverse_denominator(
                Wmax, MCHI1, ms, dm, g2, MU_R
            )
            gamma_run = se.scalar_two_body_width(Wmax, MCHI1, ms, g2)
            gamma_pole = width_tree
            base = Wmax * Wmax - M * M
            d_run = complex(base, Wmax * gamma_run)
            d_pole = complex(base, M * gamma_pole)
            d_one = os_at_max["denominator_one_loop"]
            d_res = os_at_max["denominator_resummed"]
            deltaZ = os_at_max["counterterms"]["delta_Z"]
            denominator_rows.append({
                "benchmark": label,
                "ms_keV": ms * 1e6,
                "delta_m_MeV": dm * 1e3,
                "ER_keV": er * 1e6,
                "v_km_s": speed,
                "Wmax_GeV": Wmax,
                "pole_gap_keV": (M - Wmax) * 1e6,
                "g2": g2,
                "deltaZ_OS": deltaZ,
                "D_base_re_GeV2": base,
                "D_pole_re_GeV2": d_pole.real,
                "D_pole_im_GeV2": d_pole.imag,
                "D_running_re_GeV2": d_run.real,
                "D_running_im_GeV2": d_run.imag,
                "D_full_1loop_OS_re_GeV2": d_one.real,
                "D_full_1loop_OS_im_GeV2": d_one.imag,
                "D_Dyson_resummed_diagnostic_re_GeV2": d_res.real,
                "D_Dyson_resummed_diagnostic_im_GeV2": d_res.imag,
                "dispersive_shift_percent": 100.0 * (d_one.real / base - 1.0),
                "absorptive_vs_running_percent": 100.0 * (d_one.imag / d_run.imag - 1.0),
                "one_loop_control_warning": abs(deltaZ) >= 1.0,
            })

    p1 = RESULTS / "P0-4B_SCALAR_SELF_ENERGY.csv"
    p2 = RESULTS / "P0-4B_OS_DENOMINATOR_COMPARISON.csv"
    write_csv(p1, pole_rows)
    write_csv(p2, denominator_rows)
    print(f"Wrote {p1}")
    print(f"Wrote {p2}")


if __name__ == "__main__":
    main()
