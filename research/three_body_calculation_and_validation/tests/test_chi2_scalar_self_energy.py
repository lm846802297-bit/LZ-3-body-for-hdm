import math
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import chi2_scalar_self_energy as se


class TestChi2ScalarSelfEnergy(unittest.TestCase):
    def test_msbar_pv_benchmarks(self):
        W = 1000.001
        b0, b1 = se.pv_b0_b1(W * W, 1000.0, 0.0003, 1000.0)
        self.assertAlmostEqual(b0.real, 2.000026463906299, places=11)
        self.assertAlmostEqual(b0.imag, 5.993767783601484e-6, places=16)
        self.assertAlmostEqual(b1.real, 1.500025463882642, places=11)
        self.assertAlmostEqual(b1.imag, 5.993761789842421e-6, places=16)

    def test_derivative_benchmarks(self):
        W = 1000.001
        b0p, b1p = se.pv_b0_b1_derivatives(W * W, 1000.0, 0.0003)
        self.assertAlmostEqual(b0p.real, 1.20551350295112e-5, places=15)
        self.assertAlmostEqual(b0p.imag, 3.29327121340398e-6, places=15)
        self.assertAlmostEqual(b1p.real, 1.15551117424872e-5, places=15)
        self.assertAlmostEqual(b1p.imag, 3.29326492326566e-6, places=15)

    def test_cut_imaginary_part_equals_two_body_width(self):
        for dm, ms in ((0.001, 0.0003), (0.001, 0.00036),
                       (0.010, 0.0003), (0.010, 0.00036)):
            W = 1000.0 + dm
            for g2 in (0.1, 1.0, 3.0):
                result = se.chi2_scalar_self_energy(W, 1000.0, ms, g2)
                width = se.scalar_two_body_width(W, 1000.0, ms, g2)
                self.assertAlmostEqual(result.gamma_from_cut / width, 1.0, places=11)

    def test_width_closes_at_threshold(self):
        threshold = 1000.0 + 0.0003
        self.assertEqual(
            se.scalar_two_body_width(threshold, 1000.0, 0.0003, 1.0), 0.0
        )
        self.assertGreater(
            se.scalar_two_body_width(threshold + 1e-4, 1000.0, 0.0003, 1.0),
            0.0
        )

    def test_on_shell_counterterms_set_real_pole_and_residue(self):
        m1, ms, dm, g2 = 1000.0, 0.0003, 0.001, 1.0
        M = m1 + dm
        result = se.on_shell_inverse_denominator(M, m1, ms, dm, g2)
        d = result["denominator_one_loop"]
        expected_im = M * se.scalar_two_body_width(M, m1, ms, g2)
        self.assertAlmostEqual(d.real, 0.0, delta=1e-8)
        self.assertAlmostEqual(d.imag, expected_im, delta=1e-10)

    def test_closed_channel_has_no_absorptive_part(self):
        W = 1000.0002
        result = se.chi2_scalar_self_energy(W, 1000.0, 0.0003, 1.0)
        self.assertEqual(result.gamma_from_cut, 0.0)

    def test_complex_coupling_enters_as_absolute_square(self):
        W = 1000.001
        real = se.chi2_scalar_self_energy(W, 1000.0, 0.0003, 1.0)
        complex_result = se.chi2_scalar_self_energy(W, 1000.0, 0.0003, 1.0j)
        self.assertAlmostEqual(real.gamma_from_cut, complex_result.gamma_from_cut, places=14)
        self.assertAlmostEqual(real.delta_M.real, complex_result.delta_M.real, places=14)


if __name__ == "__main__":
    unittest.main()
