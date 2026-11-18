import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import three_body_multipole_leptonic_weights as weights


class AFHEq107SpatialProjectionTests(unittest.TestCase):
    def _random_amplitudes(self):
        rng = np.random.default_rng(20261118)
        return rng.normal(size=(7, 3)) + 1j * rng.normal(size=(7, 3))

    def _lorentz_tensor_from_amplitudes(self, amplitudes):
        L = np.zeros((4, 4), dtype=complex)
        L[1:, 1:] = np.einsum(
            "si,sj->ij", amplitudes, amplitudes.conjugate()
        ) / amplitudes.shape[0]
        return L

    def test_direct_eq107_matches_lorentz_tensor_extractor_and_fixes_cross_sign(self):
        amplitudes = self._random_amplitudes()
        qA = np.asarray([0.0, 0.0, 0.2552681134])
        f1, f2, m = 3.0, -0.552, 0.938918
        direct = weights.afh_eq107_spatial_coefficients_from_amplitudes(
            amplitudes, qA, f1=f1, f2=f2, mN_GeV=m
        )
        L = self._lorentz_tensor_from_amplitudes(amplitudes)
        tensor = weights.extract_afh_vector_coefficients(
            L, np.linalg.norm(qA), f1=f1, f2=f2, mN_GeV=m
        )
        for key in ("C_Delta", "C_SigmaPrime", "C_SigmaPrimeDelta"):
            self.assertAlmostEqual(direct[key], tensor[key], places=12)
        self.assertLess(direct["C_SigmaPrimeDelta"], 0.0)
        self.assertAlmostEqual(
            direct["C_SigmaPrimeDelta"],
            -2.0 * np.sqrt(direct["C_Delta"] * direct["C_SigmaPrime"]),
            places=12,
        )

    def test_cross_coefficient_is_not_the_transverse_helicity_odd_weight(self):
        amplitudes = self._random_amplitudes()
        qA = np.asarray([0.0, 0.0, 0.22])
        L = self._lorentz_tensor_from_amplitudes(amplitudes)
        leptonic = weights.extract_leptonic_weights(L)
        direct = weights.afh_eq107_spatial_coefficients_from_amplitudes(
            amplitudes, qA, f1=3.0, f2=-0.552
        )
        self.assertGreater(
            abs(leptonic["generic_transverse_helicity_odd_minus_2i_L12_minus_L21"]),
            0.0,
        )
        self.assertLess(direct["C_SigmaPrimeDelta"], 0.0)
        self.assertNotAlmostEqual(
            direct["C_SigmaPrimeDelta"],
            leptonic["generic_transverse_helicity_odd_minus_2i_L12_minus_L21"],
            places=8,
        )

    def test_eq107_coefficients_are_invariant_under_transverse_axis_rotation(self):
        amplitudes = self._random_amplitudes()
        qA = np.asarray([0.0, 0.0, 0.22])
        angle = 0.731
        c, s = np.cos(angle), np.sin(angle)
        rotation = np.asarray([
            [c, -s, 0.0],
            [s, c, 0.0],
            [0.0, 0.0, 1.0],
        ])
        rotated = amplitudes @ rotation.T
        first = weights.afh_eq107_spatial_coefficients_from_amplitudes(
            amplitudes, qA, f1=3.0, f2=-0.552
        )
        second = weights.afh_eq107_spatial_coefficients_from_amplitudes(
            rotated, qA, f1=3.0, f2=-0.552
        )
        for key in ("C_Delta", "C_SigmaPrime", "C_SigmaPrimeDelta"):
            self.assertAlmostEqual(first[key], second[key], places=12)

    def test_longitudinal_dm_current_does_not_enter_transverse_eq107_coefficients(self):
        qA = np.asarray([0.0, 0.0, 0.22])
        transverse = self._random_amplitudes()
        longitudinal = np.zeros((transverse.shape[0], 3), dtype=complex)
        longitudinal[:, 2] = np.linspace(0.1, 0.7, transverse.shape[0]) * (1.0 + 0.2j)
        first = weights.afh_eq107_spatial_coefficients_from_amplitudes(
            transverse, qA, f1=3.0, f2=-0.552
        )
        second = weights.afh_eq107_spatial_coefficients_from_amplitudes(
            transverse + longitudinal, qA, f1=3.0, f2=-0.552
        )
        for key in ("C_Delta", "C_SigmaPrime", "C_SigmaPrimeDelta"):
            self.assertAlmostEqual(first[key], second[key], places=12)


if __name__ == "__main__":
    unittest.main()
