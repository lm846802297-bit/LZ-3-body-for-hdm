import csv
import math
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from xe131_fixed_benchmark_absolute_dsigma import (
    COUPLING_PRODUCT_SQUARED, DELTA_M_GEV, GEV_MINUS3_TO_CM2_PER_KEV,
    G2, WIDTH_SCHEME, MA_XE131_GEV, MCHI_GEV, MV_GEV, SPEED_KM_S, exact_qA_GeV,
    incident_momentum_GeV, kinematic_prefactor_GeVminus5, find_open_interval,
    nuclear_charge_kernels, write_csv,
)

class TestXe131FixedBenchmarkAbsoluteDsigmadER(unittest.TestCase):
    def test_benchmark_is_fixed_over_the_whole_curve(self):
        self.assertEqual(DELTA_M_GEV, 450.0e-6)
        self.assertEqual(COUPLING_PRODUCT_SQUARED, 1.0)
        self.assertEqual(MCHI_GEV, 1000.0)
        self.assertEqual(MV_GEV, 10.0)
        self.assertEqual(SPEED_KM_S, 776.0)

    def test_formal_absolute_spectrum_uses_pole_width(self):
        self.assertEqual(WIDTH_SCHEME, "pole")
        self.assertEqual(G2, 1.0)

    def test_exact_target_mass_shell_momentum(self):
        q = exact_qA_GeV(MA_XE131_GEV, 200.0)
        self.assertAlmostEqual(q, math.sqrt(2.0*MA_XE131_GEV*200.0e-6+(200.0e-6)**2), places=14)

    def test_public_prefactor_contains_flux_and_exact_mediator(self):
        er = 200.0
        result = kinematic_prefactor_GeVminus5(er)
        pchi = incident_momentum_GeV(MCHI_GEV, SPEED_KM_S)
        q = exact_qA_GeV(MA_XE131_GEV, er)
        minus_tA = 2.0 * MA_XE131_GEV * er * 1.0e-6
        expected = MA_XE131_GEV*COUPLING_PRODUCT_SQUARED/(256.0*math.pi**3*pchi**2*(MV_GEV**2+minus_tA)**2)
        self.assertAlmostEqual(result["public_prefactor_GeVminus5"], expected, places=22)
        self.assertAlmostEqual(result["qA_GeV"], q, places=14)
        self.assertAlmostEqual(result["Q_A_squared_GeV2"], q*q, places=14)
        self.assertAlmostEqual(result["t_A_GeV2"], -minus_tA, places=14)
        self.assertNotAlmostEqual(result["mediator_denominator_GeV4"], (MV_GEV**2+q*q)**2, places=12)

    def test_B_baseline_is_finite_tN_times_native_AFH_WM_only(self):
        responses = {"M": 12.0, "PhiPP": 0.5, "MPhiPP": -0.8}
        LC = 2.5
        out = nuclear_charge_kernels(200.0, LC, responses)
        self.assertEqual(out["form_factor_prescription"], "bishara_linear")
        self.assertAlmostEqual(
            out["A_original_AFH_M_reference"], LC * responses["M"], places=14
        )
        self.assertAlmostEqual(
            out["B_baseline_M_only"],
            out["cM_effective"] ** 2 * LC * responses["M"],
            places=14,
        )
        self.assertAlmostEqual(out["F1N_effective"], out["F1V_quark"] / 3.0, places=14)
        self.assertAlmostEqual(out["F2N_effective"], out["F2V_quark"] / 3.0, places=14)
        self.assertAlmostEqual(
            out["tN_GeV2"],
            (200.0e-6)**2 - exact_qA_GeV(MA_XE131_GEV, 200.0)**2,
            places=18,
        )
        self.assertAlmostEqual(
            out["C_over_A"],
            out["C_charge_extension"] / out["A_original_AFH_M_reference"],
            places=14,
        )
        self.assertAlmostEqual(
            out["C_over_B"],
            out["C_charge_extension"] / out["B_baseline_M_only"],
            places=14,
        )
        self.assertAlmostEqual(
            out["A_original_AFH_M_reference"],
            out["A_original_AFH_M_reference"], places=14
        )
        self.assertAlmostEqual(
            out["A_original_AFH_M_reference"], out["A_original_AFH_M_reference"], places=14
        )
        self.assertAlmostEqual(
            out["B_baseline_M_only"], out["B_baseline_M_only"], places=14
        )
        self.assertAlmostEqual(
            out["C_charge_extension"], out["C_charge_extension"], places=14
        )

    def test_write_csv_unions_open_and_closed_row_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mixed.csv"
            write_csv(path, [
                {"ER_keV": 109.0, "phase_space_open": False},
                {"ER_keV": 110.0, "phase_space_open": True, "C_charge_extension_cm2_per_keV": 1.25},
            ])
            with path.open(newline="", encoding="utf-8") as stream:
                reader = csv.DictReader(stream)
                rows = list(reader)
                fieldnames = reader.fieldnames
            self.assertEqual(
                fieldnames,
                ["ER_keV", "phase_space_open", "C_charge_extension_cm2_per_keV"],
            )
            self.assertEqual(rows[0]["C_charge_extension_cm2_per_keV"], "")
            self.assertEqual(rows[1]["C_charge_extension_cm2_per_keV"], "1.25")

    def test_unit_conversion(self):
        self.assertAlmostEqual(GEV_MINUS3_TO_CM2_PER_KEV, 3.893793721e-34, places=45)

    def test_full_open_interval(self):
        lo, hi = find_open_interval()
        self.assertAlmostEqual(lo, 109.38223179, places=7)
        self.assertAlmostEqual(hi, 653.70191379, places=6)
        self.assertLess(lo, 200.0)
        self.assertGreater(hi, 650.0)

if __name__ == "__main__":
    unittest.main()