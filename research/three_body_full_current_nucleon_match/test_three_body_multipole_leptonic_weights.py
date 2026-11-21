import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import three_body_multipole_leptonic_weights as weights


class LeptonicMultipoleWeightTests(unittest.TestCase):
    def test_symmetric_tensor_has_zero_helicity_odd_weight(self):
        L = np.diag([100.0, 2.0, 6.0, 3.0]).astype(complex)
        result = weights.extract_leptonic_weights(L)
        self.assertEqual(result["charge_L00"], 100.0)
        self.assertEqual(result["longitudinal_L33"], 3.0)
        self.assertEqual(result["transverse_even_half_sum"], 4.0)
        self.assertEqual(
            result["transverse_helicity_odd_minus_2i_L12_minus_L21"], 0.0
        )
        self.assertEqual(result["transverse_even_over_charge"], 0.04)

    def test_circular_transverse_tensor_has_expected_helicity_weight(self):
        L = np.diag([10.0, 2.0, 2.0, 1.0]).astype(complex)
        L[1, 2] = 0.2j
        L[2, 1] = -0.2j
        result = weights.extract_leptonic_weights(L)
        self.assertAlmostEqual(
            result["transverse_helicity_odd_minus_2i_L12_minus_L21"], 0.8
        )
        self.assertAlmostEqual(
            result["transverse_helicity_odd_over_transverse_sum"], 0.2
        )

    def test_weights_are_invariant_under_transverse_axis_rotation(self):
        L = np.asarray([
            [10, 0, 0, 0],
            [0, 3, 0.4j, 0],
            [0, -0.4j, 2, 0],
            [0, 0, 0, 1],
        ], dtype=complex)
        angle = 0.731
        c, s = np.cos(angle), np.sin(angle)
        rotation = np.eye(4)
        rotation[1:3, 1:3] = [[c, -s], [s, c]]
        rotated = rotation @ L @ rotation.T
        original = weights.extract_leptonic_weights(L)
        transformed = weights.extract_leptonic_weights(rotated)
        for key in (
            "transverse_even_half_sum",
            "transverse_helicity_odd_minus_2i_L12_minus_L21",
            "transverse_even_over_charge",
            "transverse_helicity_odd_over_transverse_sum",
        ):
            self.assertAlmostEqual(original[key], transformed[key], places=12)

    def test_nuclear_continuity_combines_charge_and_longitudinal_weights(self):
        L = np.asarray([
            [100.0, 0.0, 0.0, 2.0 + 0.1j],
            [0.0, 3.0, 0.0, 0.0],
            [0.0, 0.0, 3.0, 0.0],
            [2.0 - 0.1j, 0.0, 0.0, 4.0],
        ], dtype=complex)
        result = weights.extract_leptonic_weights(
            L, qA_GeV=0.2, omega_GeV=0.01
        )
        expected = 100.0 - 0.05 * 4.0 + 0.05**2 * 4.0
        self.assertAlmostEqual(result["continuity_adjusted_coulomb_weight"], expected)
        self.assertAlmostEqual(result["nuclear_omega_over_Q"], 0.05)
        self.assertAlmostEqual(
            result["continuity_charge_relative_correction"],
            expected / 100.0 - 1.0,
        )
        afh = weights.extract_afh_vector_coefficients(
            L, 0.2, f1=3.0, f2=-0.552, mN_GeV=0.938918,
            omega_GeV=0.01,
        )
        cM = 3.0 + (-0.2**2) * (3.0 + 2.0 * -0.552) / (8.0 * 0.938918**2)
        self.assertAlmostEqual(afh["C_M"], cM**2 * expected)

    def test_zero_transfer_limit_keeps_the_charge_weight(self):
        L = np.diag([100.0, 2.0, 2.0, 3.0]).astype(complex)
        weight, ratio = weights.continuity_adjusted_coulomb_weight(
            L, qA_GeV=0.0, omega_GeV=0.0
        )
        self.assertEqual(weight, 100.0)
        self.assertEqual(ratio, 0.0)
        with self.assertRaises(ValueError):
            weights.continuity_adjusted_coulomb_weight(
                L, qA_GeV=0.0, omega_GeV=1.0e-4
            )

    def test_afh_sigma_prime_delta_coefficient_is_nonzero_even_when_helicity_odd_is_zero(self):
        L = np.diag([100.0, 2.0, 6.0, 3.0]).astype(complex)
        leptonic = weights.extract_leptonic_weights(L)
        afh = weights.extract_afh_vector_coefficients(
            L, 0.2, f1=3.0, f2=-0.552, mN_GeV=0.938918
        )
        self.assertEqual(
            leptonic["generic_transverse_helicity_odd_minus_2i_L12_minus_L21"],
            0.0,
        )
        self.assertGreater(afh["C_Delta"], 0.0)
        self.assertGreater(afh["C_SigmaPrime"], 0.0)
        self.assertLess(afh["C_SigmaPrimeDelta"], 0.0)
        self.assertGreater(abs(afh["C_SigmaPrimeDelta"]), 0.0)
        self.assertLess(
            afh["C_SigmaPrimeDelta_cauchy_identity_relative_residual"],
            1e-14,
        )

    def test_afh_spatial_coefficients_have_expected_q_squared_scaling(self):
        L = np.diag([100.0, 2.0, 6.0, 3.0]).astype(complex)
        at_q = weights.extract_afh_vector_coefficients(
            L, 0.2, f1=3.0, f2=-0.552, mN_GeV=0.938918
        )
        at_2q = weights.extract_afh_vector_coefficients(
            L, 0.4, f1=3.0, f2=-0.552, mN_GeV=0.938918
        )
        for key in ("C_Delta", "C_SigmaPrime", "C_SigmaPrimeDelta"):
            self.assertAlmostEqual(at_2q[key] / at_q[key], 4.0, places=12)

    def test_zero_momentum_has_no_leading_spatial_coefficients(self):
        L = np.diag([100.0, 2.0, 6.0, 3.0]).astype(complex)
        result = weights.extract_afh_vector_coefficients(L, 0.0)
        for key in ("C_Delta", "C_SigmaPrime", "C_SigmaPrimeDelta"):
            self.assertEqual(result[key], 0.0)
        self.assertEqual(result["C_SigmaDoublePrime"], 0.0)
        self.assertEqual(result["C_PhiTildePrime"], 0.0)

    def test_nonhermitian_or_wrong_shape_tensor_is_rejected(self):
        bad = np.eye(4, dtype=complex)
        bad[0, 1] = 1j
        with self.assertRaises(ValueError):
            weights.extract_leptonic_weights(bad)
        with self.assertRaises(ValueError):
            weights.extract_leptonic_weights(np.eye(3))

    def _continuity_test_benchmark(self):
        L = np.diag([100.0, 2.0, 6.0, 3.0]).astype(complex)
        mA = 99.9999
        omega = 0.0002
        qA = np.sqrt(2.0 * mA * omega + omega * omega)
        eta = omega / qA
        LC = L[0, 0].real + eta * eta * L[3, 3].real
        J0 = 2.0 * mA + omega
        direct = J0 * J0 * L[0, 0].real + qA * qA * L[3, 3].real
        contractions = {
            "I00": float(L[0, 0].real),
            "L_C_continuity_adjusted": float(LC),
            "Ifull": float(direct),
            "continuity_reduced_relative_residual": 0.0,
        }
        pairs = np.stack((L.real, L.imag), axis=-1).tolist()
        return L, {
            "benchmark": "test",
            "width_scheme": "pole",
            "g2": 1.0,
            "ER_keV": 200.0,
            "ER_GeV": omega,
            "mA_GeV": mA,
            "qA_magnitude_GeV": float(qA),
            "point_nucleus_contractions": contractions,
            "speed_kms": 776.0,
            "nw": 24,
            "nz": 16,
            "nphi": 8,
            "L_q_aligned_real_imag": pairs,
        }

    def test_archive_summary_preserves_width_benchmarks(self):
        _, benchmark = self._continuity_test_benchmark()
        archive = {
            "status": "PASS_SPIN_RESOLVED_DM_TENSOR",
            "benchmarks": [benchmark],
        }
        result = weights.analyze_tensor_archive(archive)
        self.assertEqual(result["status"], "PASS_AFH_LEPTONIC_COEFFICIENT_EXTRACTION")
        self.assertEqual(result["summary"]["benchmark_count"], 1)
        self.assertEqual(result["benchmarks"][0]["width_scheme"], "pole")
        self.assertLess(
            result["summary"]["max_qA_mass_shell_relative_residual"], 1e-14
        )
        self.assertLess(
            result["summary"]["max_direct_vs_continuity_relative_residual"], 1e-14
        )

    def test_archive_rejects_inconsistent_qA_mass_shell(self):
        _, benchmark = self._continuity_test_benchmark()
        benchmark["qA_magnitude_GeV"] *= 1.01
        with self.assertRaisesRegex(ValueError, "mass-shell relation"):
            weights.analyze_tensor_archive({
                "status": "PASS_SPIN_RESOLVED_DM_TENSOR",
                "benchmarks": [benchmark],
            })

    def test_archive_rejects_corrupt_stored_continuity_contraction(self):
        _, benchmark = self._continuity_test_benchmark()
        benchmark["point_nucleus_contractions"]["Ifull"] *= 1.001
        with self.assertRaisesRegex(ValueError, "stored Ifull disagrees"):
            weights.analyze_tensor_archive({
                "status": "PASS_SPIN_RESOLVED_DM_TENSOR",
                "benchmarks": [benchmark],
            })


if __name__ == "__main__":
    unittest.main()
