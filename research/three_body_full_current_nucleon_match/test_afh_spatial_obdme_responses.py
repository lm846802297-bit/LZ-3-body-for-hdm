import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import afh_spatial_obdme_responses as spatial


class AFHSpatialOBDMEResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix_dir = spatial.MATRIX_ROOT
        cls.xe131 = spatial.read_density_matrix(
            cls.matrix_dir / "afh_default_xe131_density_matrix.csv"
        )
        cls.xe129 = spatial.read_density_matrix(
            cls.matrix_dir / "afh_default_xe129_density_matrix.csv"
        )
        cls.xe128 = spatial.read_density_matrix(
            cls.matrix_dir / "afh_default_xe128_density_matrix.csv"
        )

    def test_even_even_spin_zero_isotopes_have_no_abnormal_spatial_responses(self):
        result = spatial.isotope_spatial_response(
            0.22, 128, self.xe128, 0.0, 10.0, 11.577645306853507
        )
        for key in (
            "W_Delta_AFH_package",
            "W_SigmaPrime_AFH_package",
            "W_SigmaPrimeDelta_AFH_package",
            "R_Delta_equal_pn",
            "R_SigmaPrime_equal_pn",
            "R_SigmaPrimeDelta_equal_pn",
        ):
            self.assertEqual(result[key], 0.0)

    def test_spinful_isotope_spatial_responses_are_finite_and_obey_cauchy(self):
        for A, rows, J_A, T, b in (
            (129, self.xe129, 0.5, 10.5, 11.590811525822195),
            (131, self.xe131, 1.5, 11.5, 11.61690053236942),
        ):
            for q in (0.0, 0.10, 0.2208257435, 0.2551469574, 0.60):
                result = spatial.isotope_spatial_response(q, A, rows, J_A, T, b)
                values = [
                    result[k] for k in (
                        "W_Delta_AFH_package",
                        "W_SigmaPrime_AFH_package",
                        "W_SigmaPrimeDelta_AFH_package",
                        "R_Delta_equal_pn",
                        "R_SigmaPrime_equal_pn",
                        "R_SigmaPrimeDelta_equal_pn",
                    )
                ]
                self.assertTrue(np.all(np.isfinite(values)), (A, q, values))
                bound = np.sqrt(
                    result["W_Delta_AFH_package"]
                    * result["W_SigmaPrime_AFH_package"]
                )
                self.assertLessEqual(
                    abs(result["W_SigmaPrimeDelta_AFH_package"]),
                    bound + 2.0e-10 * max(bound, 1.0e-300),
                )

    def test_cross_response_is_the_rankwise_sigma_delta_bilinear(self):
        result = spatial.isotope_spatial_response(
            0.2551469574, 131, self.xe131, 1.5, 11.5, 11.61690053236942
        )
        sigma = result["rank_amplitudes_SigmaPrime"]
        delta = result["rank_amplitudes_Delta"]
        expected = 0.25 * sum(sigma[k] * delta[k] for k in delta)
        self.assertAlmostEqual(
            result["W_SigmaPrimeDelta_AFH_package"], expected, places=13
        )

    def test_rank_resolved_multipoles_reconstruct_all_three_spatial_responses(self):
        result = spatial.isotope_spatial_response(
            0.2551469574, 131, self.xe131, 1.5, 11.5, 11.61690053236942
        )
        records = spatial.multipole_records_for_response(131, "Xe-131", 1.5, result)
        self.assertGreater(len(records), 0)
        self.assertEqual(
            {row["multipole_J"] for row in records},
            {int(key) for key in result["rank_amplitudes_Delta"]},
        )
        for name, total_key, rank_key in (
            ("Delta", "W_Delta_AFH_package", "W_Delta_J_AFH_package"),
            ("SigmaPrime", "W_SigmaPrime_AFH_package", "W_SigmaPrime_J_AFH_package"),
            ("SigmaPrimeDelta", "W_SigmaPrimeDelta_AFH_package", "W_SigmaPrimeDelta_J_AFH_package"),
        ):
            reconstructed = sum(row[rank_key] for row in records)
            self.assertAlmostEqual(reconstructed, result[total_key], places=14, msg=name)
        for name, total_key, rank_key in (
            ("Delta", "R_Delta_equal_pn", "R_Delta_J_equal_pn"),
            ("SigmaPrime", "R_SigmaPrime_equal_pn", "R_SigmaPrime_J_equal_pn"),
            ("SigmaPrimeDelta", "R_SigmaPrimeDelta_equal_pn", "R_SigmaPrimeDelta_J_equal_pn"),
        ):
            reconstructed = sum(row[rank_key] for row in records)
            self.assertAlmostEqual(reconstructed, result[total_key], places=13, msg=name)

    def test_rankwise_interference_keeps_its_sign(self):
        result = spatial.isotope_spatial_response(
            0.2551469574, 131, self.xe131, 1.5, 11.5, 11.61690053236942
        )
        records = spatial.multipole_records_for_response(131, "Xe-131", 1.5, result)
        rankwise = [row["W_SigmaPrimeDelta_J_AFH_package"] for row in records]
        self.assertTrue(any(value < 0.0 for value in rankwise) or
                        any(value > 0.0 for value in rankwise))
        self.assertAlmostEqual(
            sum(rankwise), result["W_SigmaPrimeDelta_AFH_package"], places=14
        )

    def test_common_equal_pn_and_matrix_normalization_are_applied_once(self):
        result = spatial.isotope_spatial_response(
            0.22, 131, self.xe131, 1.5, 11.5, 11.61690053236942
        )
        self.assertGreater(result["common_matrix_normalization"], 0.0)
        self.assertAlmostEqual(
            result["R_Delta_equal_pn"],
            4.0 * result["common_matrix_normalization"]
            * (4.0 * np.pi / 4.0)
            * result["W_Delta_AFH_package"],
            places=10,
        )

    def test_delta_and_sigma_prime_are_zero_for_even_rank_only_density_matrix(self):
        result = spatial.isotope_spatial_response(
            0.20, 130,
            spatial.read_density_matrix(
                self.matrix_dir / "afh_default_xe130_density_matrix.csv"
            ),
            0.0, 11.0, 11.603896230055925,
        )
        self.assertEqual(result["W_Delta_AFH_package"], 0.0)
        self.assertEqual(result["W_SigmaPrime_AFH_package"], 0.0)


if __name__ == "__main__":
    unittest.main()
