import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import contract_three_body_afh_responses as contract


ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
J_BY_A = {128: 0.0, 129: 0.5, 130: 0.0, 131: 1.5, 132: 0.0, 134: 0.0, 136: 0.0}
RANKS = {128: [], 129: [1], 130: [], 131: [1], 132: [], 134: [], 136: []}
C0 = 1.001


def synthetic_afh_rows(*, violate_cauchy=False):
    rows = []
    for A in ISOTOPES:
        for q in (0.0, 0.6):
            rows.append({
                "A": A,
                "J_A": J_BY_A[A],
                "q_GeV": q,
                "R_M_physical_equal_pn": 100.0,
                "R_PhiPP_physical_equal_pn": 1.0,
                "R_MPhiPP_physical_equal_pn": 0.5,
            })
    return rows


def synthetic_spatial_rows(*, violate_cauchy=False):
    rows = []
    for A in ISOTOPES:
        for q in (0.0, 0.6):
            if A in (129, 131):
                delta, sigma = 0.1, 0.2
                cross = 0.3 if violate_cauchy else -0.1
            else:
                delta = sigma = cross = 0.0
            rows.append({
                "A": A,
                "isotope": f"Xe-{A}",
                "J_A": J_BY_A[A],
                "q_GeV": q,
                "y": q*q,
                "R_Delta_equal_pn": delta,
                "R_SigmaPrime_equal_pn": sigma,
                "R_SigmaPrimeDelta_equal_pn": cross,
                "common_matrix_normalization": C0,
            })
    return rows


def synthetic_multipole_rows(*, violate_cauchy=False):
    rows = []
    for A in (129, 131):
        for q in (0.0, 0.6):
            cross = 0.3 if violate_cauchy else -0.1
            rows.append({
                "A": A,
                "isotope": f"Xe-{A}",
                "J_A": J_BY_A[A],
                "q_GeV": q,
                "y": q*q,
                "multipole_J": 1,
                "M_Delta_J": 0.2,
                "M_SigmaPrime_J": 0.4,
                "W_Delta_J_AFH_package": 0.01,
                "W_SigmaPrime_J_AFH_package": 0.04,
                "W_SigmaPrimeDelta_J_AFH_package": cross,
                "R_Delta_J_equal_pn": 0.1,
                "R_SigmaPrime_J_equal_pn": 0.2,
                "R_SigmaPrimeDelta_J_equal_pn": cross,
                "common_matrix_normalization": C0,
            })
    return rows


def synthetic_weights():
    return {
        "status": "PASS_AFH_LEPTONIC_COEFFICIENT_EXTRACTION",
        "form_factor_input": {
            "status": "constant provisional q=0 anchors; finite-t dependence not included"
        },
        "benchmarks": [{
            "benchmark": "test",
            "width_scheme": "pole",
            "g2": 1.0,
            "ER_keV": 200.0,
            "speed_kms": 776.0,
            "afh_vector_coefficients": {
                "qA_GeV": 0.3,
                "C_M": 100.0,
                "C_PhiPP": 1.0,
                "C_MPhiPP": 2.0,
                "C_Delta": 0.2,
                "C_SigmaPrime": 0.1,
                "C_SigmaPrimeDelta": -0.2,
            },
        }],
    }


def synthetic_metadata():
    return {
        "status": "PROVISIONAL_PYTHON",
        "native_afh_validated": False,
        "source": "synthetic test data",
        "afh_source_commit": contract.EXPECTED_AFH_SOURCE_COMMIT,
        "csv_sha256": "test",
        "natural_atom_fraction_coverage": 0.998158,
        "normalization": {
            "factor_four_applied_once_to_physical_columns": True
        },
    }


def synthetic_spatial_metadata():
    return {
        "status": "PROVISIONAL_SOURCE_TRANSLATED_AFH_SPATIAL_RESPONSES",
        "source_file_sha256": contract.EXPECTED_AFH_SOURCE_SHA256,
        "response_file_sha256": contract.EXPECTED_SPATIAL_RESPONSE_SHA256,
        "multipole_file_sha256": contract.EXPECTED_SPATIAL_MULTIPOLE_SHA256,
        "isotopes": list(ISOTOPES),
        "multipole_ranks_by_isotope": {str(A): RANKS[A] for A in ISOTOPES},
        "multipole_rows": len(synthetic_multipole_rows()),
        "isotope_metadata": [
            {"A": A, "J_A": J_BY_A[A], "common_matrix_normalization": C0}
            for A in ISOTOPES
        ],
    }


class ThreeBodyAFHContractionTests(unittest.TestCase):
    def contract(self, *, violate_cauchy=False):
        return contract.contract_archive(
            synthetic_afh_rows(),
            synthetic_weights(),
            synthetic_metadata(),
            synthetic_spatial_rows(violate_cauchy=violate_cauchy),
            synthetic_multipole_rows(violate_cauchy=violate_cauchy),
            synthetic_spatial_metadata(),
            expected_points=2,
        )

    def test_seven_isotope_contraction_applies_common_c0_and_is_provisional(self):
        result = self.contract()
        self.assertEqual(result["status"], "PROVISIONAL_AFH_CONTRACTION_PASS")
        self.assertEqual(result["summary"]["contracted_rows"], 7)
        self.assertEqual(result["summary"]["positive_total_kernel_rows"], 7)
        self.assertFalse(result["afh_source"]["native_afh_validated"])
        self.assertFalse(result["spatial_afh_source"]["native_afh_validated"])
        xe129 = next(row for row in result["benchmarks"] if row["A"] == 129)
        self.assertAlmostEqual(xe129["responses_physical_equal_pn_C0_corrected"]["M"], 100.0*C0)
        self.assertAlmostEqual(
            xe129["charge_sector"],
            100.0*(100.0*C0) + 1.0*(1.0*C0) + 2.0*(0.5*C0),
        )
        self.assertAlmostEqual(xe129["spatial_sector"], 0.2*0.1 + 0.1*0.2 + (-0.2)*(-0.1))
        self.assertAlmostEqual(
            xe129["spatial_sector_from_rank_sum"], xe129["spatial_sector"]
        )
        self.assertEqual(len(xe129["spatial_multipole_rank_contributions"]), 1)

    def test_interpolation_uses_q_a_and_preserves_signed_interference(self):
        rows = synthetic_spatial_rows()
        for row in rows:
            if int(row["A"]) in (129, 131) and float(row["q_GeV"]) == 0.6:
                row["R_Delta_equal_pn"] = 0.5
                row["R_SigmaPrime_equal_pn"] = 0.4
                row["R_SigmaPrimeDelta_equal_pn"] = -0.3
        multipoles = synthetic_multipole_rows()
        for row in multipoles:
            if float(row["q_GeV"]) == 0.6:
                row["R_Delta_J_equal_pn"] = 0.5
                row["R_SigmaPrime_J_equal_pn"] = 0.4
                row["R_SigmaPrimeDelta_J_equal_pn"] = -0.3
        result = contract.contract_archive(
            synthetic_afh_rows(), synthetic_weights(), synthetic_metadata(),
            rows, multipoles, synthetic_spatial_metadata(), expected_points=2
        )
        xe129 = next(row for row in result["benchmarks"] if row["A"] == 129)
        self.assertAlmostEqual(
            xe129["responses_physical_equal_pn_C0_corrected"]["SigmaPrimeDelta"], -0.2
        )
        self.assertGreater(xe129["coefficient_response_terms"]["SigmaPrimeDelta"], 0.0)

    def test_cauchy_violation_is_rejected(self):
        result = self.contract(violate_cauchy=True)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("Cauchy" in item for item in result["summary"]["failures"]))

    def test_missing_charge_response_column_is_rejected(self):
        rows = synthetic_afh_rows()
        del rows[0]["R_M_physical_equal_pn"]
        with self.assertRaises(ValueError):
            contract.index_afh_rows(rows, expected_points=2)

    def test_incomplete_charge_isotope_set_is_rejected(self):
        rows = [row for row in synthetic_afh_rows() if int(row["A"]) != 136]
        with self.assertRaises(ValueError):
            contract.index_afh_rows(rows, expected_points=2)

    def test_rankwise_spatial_reconstruction_failure_is_rejected(self):
        multipoles = synthetic_multipole_rows()
        multipoles[0]["R_Delta_J_equal_pn"] = 0.09
        with self.assertRaises(ValueError):
            contract.index_spatial_archive(
                synthetic_spatial_rows(), multipoles,
                synthetic_spatial_metadata(), expected_points=2
            )


if __name__ == "__main__":
    unittest.main()
