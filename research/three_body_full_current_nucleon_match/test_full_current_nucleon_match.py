import math
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import full_current_nucleon_match as fm
import spin_resolved_three_body_current as dm


class FullCurrentNucleonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.point, cls.t3 = fm.build_reference_inputs()
        cls.q = np.asarray(cls.point.q_A[1:], dtype=float)
        cls.lhat = fm.perpendicular_unit(cls.q)
        cls.width_results = fm.run_finite_width_scenarios(cls.point, cls.q)

    def test_nucleon_current_is_conserved_in_static_elastic_limit(self):
        jn, qn, _ = fm.nucleon_current_matrices(
            self.q, 0.10 * fm.M_N_GEV * self.lhat, 1.0, -0.15
        )
        self.assertLess(fm.nucleon_ward_residual(qn, jn), 2e-12)
        self.assertAlmostEqual(qn[0], 0.0, places=14)

    def test_pauli_basis_reconstructs_full_amplitude(self):
        jn, _, _ = fm.nucleon_current_matrices(
            self.q, 0.10 * fm.M_N_GEV * self.lhat, 1.0, -0.15
        )
        full, _, _ = fm.full_amplitude_operator(self.t3, jn)
        self.assertLess(fm.pauli_decomposition_residual(full), 2e-13)

    def test_full_amplitude_is_charge_plus_spatial(self):
        jn, _, _ = fm.nucleon_current_matrices(
            self.q, 0.10 * fm.M_N_GEV * self.lhat, 1.0, 0.0
        )
        full, charge, spatial = fm.full_amplitude_operator(self.t3, jn)
        self.assertLess(np.linalg.norm(full - charge - spatial), 1e-12 * np.linalg.norm(full))

    def test_zero_internal_velocity_has_no_odd_spin_orbit_piece(self):
        value = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.0, 1.0, 0.0, "full")
        self.assertEqual(value, 0.0j)

    def test_spatial_current_is_retained_in_full_amplitude(self):
        jn, _, _ = fm.nucleon_current_matrices(
            self.q, 0.10 * fm.M_N_GEV * self.lhat, 1.0, 0.0
        )
        full_operator, charge_operator, spatial_operator = fm.full_amplitude_operator(self.t3, jn)
        self.assertGreater(np.linalg.norm(spatial_operator), 1e-8)
        self.assertLess(
            np.linalg.norm(full_operator - charge_operator - spatial_operator),
            1e-12 * np.linalg.norm(full_operator),
        )
        full = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.10, 1.0, 0.0, "full")
        charge = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.10, 1.0, 0.0, "charge")
        spatial = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.10, 1.0, 0.0, "spatial")
        self.assertLess(abs(full - charge - spatial), 1e-7 * max(abs(full), abs(charge), abs(spatial), 1.0))

    def test_spin_orbit_odd_piece_is_linear_at_small_vN(self):
        c02 = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.02, 1.0, 0.0, "full")
        c05 = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.05, 1.0, 0.0, "full")
        self.assertLess(abs(c02 - c05) / max(abs(c05), 1e-30), 0.08)

    def test_pauli_form_factor_changes_full_current_projection(self):
        c0 = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.10, 1.0, 0.0, "full")
        c2 = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.10, 1.0, -0.15, "full")
        self.assertGreater(abs(c0 - c2), 1e-10)

    def test_nonrel_normalized_charge_spin_orbit_matches_exact_spinor_formula(self):
        v_n = 0.10
        f1, f2 = 1.0, -0.184
        l_vec = fm.M_N_GEV * v_n * self.lhat
        p_i = l_vec - 0.5 * self.q
        p_f = l_vec + 0.5 * self.q
        energy = math.sqrt(
            fm.M_N_GEV**2 + float(np.dot(p_i, p_i))
        )
        t0_identity = 0.5 * np.trace(self.t3[0])
        expected = 1j * t0_identity * (
            f1 / (2.0 * energy * (energy + fm.M_N_GEV))
            + f2 / (2.0 * fm.M_N_GEV * energy)
        )
        got = fm.spin_orbit_odd_coefficient(
            self.t3, self.q, v_n, f1, f2, "charge",
            nonrel_normalized=True,
        )
        self.assertLess(abs(got - expected), 2e-12 * max(abs(expected), 1.0))

    def test_nonrel_state_normalization_uses_both_external_energies(self):
        l_vec = 0.10 * fm.M_N_GEV * self.lhat
        p_i = l_vec - 0.5 * self.q
        p_f = l_vec + 0.5 * self.q
        expected = 1.0 / (
            2.0 * math.sqrt(
                (fm.M_N_GEV**2 + np.dot(p_i, p_i))
                * (fm.M_N_GEV**2 + np.dot(p_f, p_f))
            ) ** 0.5
        )
        got = fm.nonrel_state_normalization(p_i, p_f)
        self.assertAlmostEqual(got, expected, places=14)

    def test_spatial_current_reduces_to_convection_plus_magnetization(self):
        # Use a deliberately small q/m and l/m so the leading NR expansion
        # is isolated from O(p^3/m^3) corrections.
        q = np.asarray([0.002, 0.0, 0.0])
        ell = np.asarray([0.0, 0.001, 0.0])
        f1, f2 = 1.0, -0.184
        current, _, (p_i, p_f) = fm.nucleon_current_matrices(
            q, ell, f1, f2
        )
        current *= fm.nonrel_state_normalization(p_i, p_f)
        eps = np.zeros((3, 3, 3))
        eps[0, 1, 2] = eps[1, 2, 0] = eps[2, 0, 1] = 1.0
        eps[0, 2, 1] = eps[2, 1, 0] = eps[1, 0, 2] = -1.0
        for i in range(3):
            identity_piece = 0.5 * np.trace(current[i + 1])
            expected_identity = f1 * ell[i] / fm.M_N_GEV
            self.assertLess(
                abs(identity_piece - expected_identity),
                1e-5 * max(abs(expected_identity), 1e-7) + 1e-12,
            )
            for j in range(3):
                spin_piece = 0.5 * np.trace(fm.PAULI[j + 1] @ current[i + 1])
                expected_spin = (
                    1j * (f1 + f2) / (2.0 * fm.M_N_GEV)
                    * sum(eps[i, j, k] * q[k] for k in range(3))
                )
                self.assertLess(
                    abs(spin_piece - expected_spin),
                    1e-5 * max(abs(expected_spin), 1e-7) + 1e-12,
                )

    def test_full_pauli_coefficients_are_json_safe_and_complete(self):
        jn, _, _ = fm.nucleon_current_matrices(
            self.q, 0.10 * fm.M_N_GEV * self.lhat, 1.0, -0.184
        )
        full, _, _ = fm.full_amplitude_operator(self.t3, jn)
        payload = fm.pauli_coefficients_as_pairs(full)
        self.assertEqual(len(payload), 4)
        self.assertTrue(all(len(row) == 4 for row in payload))
        self.assertTrue(all(len(value) == 2 for row in payload for value in row))

    def test_static_qA_energy_transfer_is_reported_as_distinct_from_qN0(self):
        self.assertGreater(float(self.point.q_A[0]), 0.0)
        jn, qn, _ = fm.nucleon_current_matrices(
            self.q, 0.10 * fm.M_N_GEV * self.lhat, 1.0, -0.184
        )
        self.assertAlmostEqual(float(qn[0]), 0.0, places=14)
        residual_qn = fm.nucleon_ward_residual(qn, jn)
        residual_qA = fm.nucleon_ward_residual(
            np.asarray(self.point.q_A, dtype=float), jn
        )
        self.assertLess(residual_qn, 2e-12)
        self.assertGreater(residual_qA, 0.0)

    def test_finite_width_scan_covers_zero_pole_running_and_both_g2(self):
        keys = {(row["g2"], row["width_scheme"]) for row in self.width_results}
        expected = {
            (g2, scheme)
            for g2 in (0.1, 1.0)
            for scheme in ("zero", "pole", "running")
        }
        self.assertEqual(keys, expected)
        for row in self.width_results:
            if row["width_scheme"] == "zero":
                self.assertEqual(row["denominator_imaginary_part_GeV2"], 0.0)
            else:
                self.assertGreater(row["denominator_imaginary_part_GeV2"], 0.0)

    def test_finite_width_spin_trace_and_modified_Ward_identity(self):
        for row in self.width_results:
            self.assertLess(row["spin_trace_relative_residual"], 2e-12)
            self.assertLess(
                row["finite_width_Ward_identity_relative_residual"], 2e-12
            )
            self.assertLess(row["full_pauli_reconstruction_residual"], 2e-13)
            self.assertLess(row["charge_pauli_reconstruction_residual"], 2e-13)
            self.assertLess(row["spatial_pauli_reconstruction_residual"], 2e-13)

    def test_finite_width_changes_near_pole_current_norm(self):
        zero = next(
            row for row in self.width_results
            if row["g2"] == 1.0 and row["width_scheme"] == "zero"
        )
        pole = next(
            row for row in self.width_results
            if row["g2"] == 1.0 and row["width_scheme"] == "pole"
        )
        self.assertGreater(
            abs(pole["DM_current_norm"] - zero["DM_current_norm"]),
            1e-8 * zero["DM_current_norm"],
        )
        self.assertGreater(pole["coherent_two_diagram_interference_norm"], 0.0)

    def test_DM_spin_trace_still_matches_PR53_tensor(self):
        ref = fm.dm.vca.dm_current_tensor(
            self.point, dm.MCHI_GEV, dm.MCHI_GEV + 362.0e-6, 0.0
        )
        got = dm.tensor_from_spin_matrices(self.t3)
        self.assertLess(dm.relative_matrix_residual(got, ref), 2e-12)


if __name__ == "__main__":
    unittest.main()
