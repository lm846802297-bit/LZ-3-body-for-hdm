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

    def test_spatial_current_changes_charge_only_spin_orbit_projection(self):
        full = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.10, 1.0, 0.0, "full")
        charge = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.10, 1.0, 0.0, "charge")
        spatial = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.10, 1.0, 0.0, "spatial")
        self.assertGreater(abs(spatial), 1e-10)
        self.assertLess(abs(full - charge - spatial), 1e-10 * max(abs(full), abs(charge), abs(spatial), 1.0))

    def test_spin_orbit_odd_piece_is_linear_at_small_vN(self):
        c02 = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.02, 1.0, 0.0, "full")
        c05 = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.05, 1.0, 0.0, "full")
        self.assertLess(abs(c02 - c05) / max(abs(c05), 1e-30), 0.08)

    def test_pauli_form_factor_changes_full_current_projection(self):
        c0 = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.10, 1.0, 0.0, "full")
        c2 = fm.spin_orbit_odd_coefficient(self.t3, self.q, 0.10, 1.0, -0.15, "full")
        self.assertGreater(abs(c0 - c2), 1e-10)

    def test_DM_spin_trace_still_matches_PR53_tensor(self):
        ref = fm.dm.vca.dm_current_tensor(
            self.point, dm.MCHI_GEV, dm.MCHI_GEV + 362.0e-6, 0.0
        )
        got = dm.tensor_from_spin_matrices(self.t3)
        self.assertLess(dm.relative_matrix_residual(got, ref), 2e-12)


if __name__ == "__main__":
    unittest.main()
