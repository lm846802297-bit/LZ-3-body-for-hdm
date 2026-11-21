import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import full_current_nucleon_match as full
import three_body_multipole_leptonic_weights as weights


class ThreeBodyQFrameFullCurrentTests(unittest.TestCase):
    def test_q_aligned_rotation_is_right_handed_and_maps_q_to_positive_z(self):
        point, _ = full.build_reference_inputs()
        q = np.asarray(point.q_A[1:], dtype=float)
        rotation = full.q_aligned_rotation(q)
        q_qframe = rotation @ q
        self.assertLess(np.linalg.norm(rotation @ rotation.T - np.eye(3)), 1e-13)
        self.assertAlmostEqual(np.linalg.det(rotation), 1.0, places=13)
        self.assertLess(np.linalg.norm(q_qframe[:2]), 1e-13)
        self.assertAlmostEqual(q_qframe[2], np.linalg.norm(q), places=13)

    def test_exact_full_dm_times_nucleon_amplitude_is_rotation_invariant(self):
        result = full.run_q_frame_full_current_validation()
        self.assertEqual(result["status"], "PASS_DIRECT_VS_Q_FRAME_FULL_CURRENT_CONTRACTION")
        for key in (
            "rotation_orthogonality_residual",
            "DM_tensor_rotation_residual",
            "nucleon_current_rotation_residual",
            "full_amplitude_rotation_residual",
            "charge_amplitude_rotation_residual",
            "spatial_amplitude_rotation_residual",
            "spin_summed_norm_relative_residual",
            "nucleon_Ward_residual_qN",
        ):
            self.assertLess(result[key], 2e-12, key)
        self.assertAlmostEqual(result["rotation_determinant"], 1.0, places=12)
        self.assertLess(abs(result["nucleon_qN0_minus_qA0_GeV"]), 2e-13)

    def test_actual_three_body_spin_amplitudes_reproduce_afh_eq107_tensor_coefficients(self):
        point, t3 = full.build_reference_inputs()
        qA_lab = np.asarray(point.q_A[1:], dtype=float)
        Q = float(np.linalg.norm(qA_lab))
        rotation = full.q_aligned_rotation(qA_lab)
        t3_q = full.rotate_current_to_q_frame(t3, rotation)
        L_q = full.dm.tensor_from_spin_matrices(t3_q)
        amplitudes = t3_q[1:].transpose(1, 2, 0).reshape(-1, 3)
        direct = weights.afh_eq107_spatial_coefficients_from_amplitudes(
            amplitudes,
            np.asarray([0.0, 0.0, Q]),
            f1=1.0,
            f2=-0.184,
            mN_GeV=full.M_N_GEV,
            spin_average_denominator=2.0,
        )
        tensor = weights.extract_afh_vector_coefficients(
            L_q,
            Q,
            f1=1.0,
            f2=-0.184,
            mN_GeV=full.M_N_GEV,
            omega_GeV=float(point.q_A[0]),
        )
        for key in ("C_Delta", "C_SigmaPrime", "C_SigmaPrimeDelta"):
            scale = max(abs(direct[key]), abs(tensor[key]), 1.0e-300)
            self.assertLess(
                abs(direct[key] - tensor[key]) / scale,
                2.0e-13,
                key,
            )
        self.assertLess(direct["C_SigmaPrimeDelta"], 0.0)
        lhs = direct["transverse_DM_norm_L_T"]
        rhs = float(np.real(L_q[1, 1] + L_q[2, 2]))
        self.assertLess(abs(lhs - rhs) / max(abs(lhs), abs(rhs), 1.0e-300), 2.0e-13)


if __name__ == "__main__":
    unittest.main()
