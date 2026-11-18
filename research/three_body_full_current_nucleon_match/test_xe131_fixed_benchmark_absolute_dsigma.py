import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from xe131_fixed_benchmark_absolute_dsigma import (
    COUPLING_PRODUCT_SQUARED, DELTA_M_GEV, GEV_MINUS3_TO_CM2_PER_KEV,
    MA_XE131_GEV, MCHI_GEV, MV_GEV, SPEED_KM_S, exact_qA_GeV,
    incident_momentum_GeV, kinematic_prefactor_GeVminus5, find_open_interval,
)

class TestXe131FixedBenchmarkAbsoluteDsigmadER(unittest.TestCase):
    def test_benchmark_is_fixed_over_the_whole_curve(self):
        self.assertEqual(DELTA_M_GEV, 450.0e-6)
        self.assertEqual(COUPLING_PRODUCT_SQUARED, 1.0)
        self.assertEqual(MCHI_GEV, 1000.0)
        self.assertEqual(MV_GEV, 10.0)
        self.assertEqual(SPEED_KM_S, 776.0)

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
