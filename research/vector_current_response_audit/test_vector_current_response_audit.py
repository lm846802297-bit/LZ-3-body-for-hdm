import unittest
import numpy as np

from vector_current_response_audit import (
    dm_current_tensor,
    decompose_current,
    integrate_current_components,
    pointlike_coherent_charge_current,
    stable_build_point,
    width_imaginary_part,
)
import eq6_kernel as eq6
import phase_space_convergence as phase

MCHI = 1000.0
MS = 300.0e-6
DM = 450.0e-6
MA = 131.0 * 0.93149410242
ER = 200.0e-6
SPEED = 776.0


def representative_point():
    wmin, wmax = eq6.limits(MCHI, MS, MA, ER, SPEED)
    return stable_build_point(
        MCHI, MS, MA, ER, SPEED, 0.5 * (wmax - wmin), 0.2, 1.1
    )


class VectorCurrentResponseTests(unittest.TestCase):
    def test_temporal_component_matches_legacy_eq6_trace(self):
        point = representative_point()
        mchi2 = MCHI + DM
        tensor = dm_current_tensor(point, MCHI, mchi2, 0.0)
        legacy = eq6.spin_trace(point, MCHI, mchi2, 0.0)["total"]
        self.assertLess(abs(tensor[0, 0].real / legacy - 1.0), 2e-13)

        imag = width_imaginary_part(point, MCHI, MS, DM, 1.0, "pole")
        tensor_pole = dm_current_tensor(point, MCHI, mchi2, imag)
        width = eq6.chi2_width_dirac_scalar(MCHI, MS, DM, 1.0)
        legacy_pole = eq6.spin_trace(
            point, MCHI, mchi2, width
        )["total"]
        self.assertLess(abs(tensor_pole[0, 0].real / legacy_pole - 1.0), 2e-13)

    def test_tensor_is_hermitian_and_positive_semidefinite(self):
        point = representative_point()
        tensor = dm_current_tensor(point, MCHI, MCHI + DM, 0.0)
        scale = np.max(np.abs(tensor))
        self.assertLess(np.max(np.abs(tensor - tensor.conj().T)) / scale, 1e-12)
        eigenvalues = np.linalg.eigvalsh(tensor)
        self.assertGreaterEqual(
            float(np.min(eigenvalues)),
            -1e-11 * float(np.max(eigenvalues)),
        )

    def test_point_nucleus_current_is_conserved(self):
        point = representative_point()
        current = pointlike_coherent_charge_current(point, MA)
        qdotj = point.E_R * current[0] - np.dot(point.q_A[1:], current[1:])
        self.assertLess(abs(float(qdotj)), 2e-12)

    def test_current_decomposition_is_exact(self):
        point = representative_point()
        tensor = dm_current_tensor(point, MCHI, MCHI + DM, 0.0)
        d = decompose_current(tensor, point, MA)
        rhs = (
            d["charge_piece"] + d["spatial_nuclear_piece"]
            + d["charge_spatial_interference"]
        )
        self.assertLess(abs(d["full_point_nucleus"] / rhs - 1.0), 2e-13)

    def test_width_changes_rate_more_than_current_direction(self):
        common = dict(
            mchi=MCHI, ms=MS, delta_m=DM, mA=MA, ER=ER,
            speed_kms=SPEED, g2=1.0, mapping="threshold_u2",
            nw=12, nz=8, nphi=6,
        )
        zero = integrate_current_components(**common, width_scheme="zero")
        pole = integrate_current_components(**common, width_scheme="pole")
        rate_shift = abs(pole["I00"] / zero["I00"] - 1.0)
        current_shift = abs(
            pole["rchi_spatial_over_temporal"]
            / zero["rchi_spatial_over_temporal"] - 1.0
        )
        self.assertGreater(rate_shift, 1e-3)
        self.assertLess(current_shift, 1e-4)


    def test_integrated_l00_matches_independent_phase_space_integrator_zero_width(self):
        common = dict(
            mchi=MCHI, ms=MS, delta_m=DM, mA=MA, ER=ER,
            speed_kms=SPEED, g2=1.0, mapping="threshold_u2",
            nw=8, nz=6, nphi=4,
        )
        result = integrate_current_components(**common, width_scheme="zero")
        reference = phase._integrate(
            MCHI, MS, DM, MA, ER, SPEED, 8, 6, 4,
            "threshold_u2", "average", "zero", 1.0,
        )
        self.assertLess(abs(result["I00"] / reference - 1.0), 2e-12)

    def test_integrated_l00_matches_independent_phase_space_integrator_pole_width(self):
        common = dict(
            mchi=MCHI, ms=MS, delta_m=DM, mA=MA, ER=ER,
            speed_kms=SPEED, g2=1.0, mapping="threshold_u2",
            nw=8, nz=6, nphi=4,
        )
        result = integrate_current_components(**common, width_scheme="pole")
        reference = phase._integrate(
            MCHI, MS, DM, MA, ER, SPEED, 8, 6, 4,
            "threshold_u2", "average", "pole", 1.0,
        )
        self.assertLess(abs(result["I00"] / reference - 1.0), 2e-12)

    def test_closed_phase_space_returns_without_fake_rate(self):
        result = integrate_current_components(
            mchi=MCHI, ms=MS, delta_m=DM, mA=MA, ER=1.0,
            speed_kms=SPEED, g2=1.0, width_scheme="pole",
            mapping="threshold_u2", nw=8, nz=8, nphi=4,
        )
        self.assertFalse(result["phase_space_open"])


if __name__ == "__main__":
    unittest.main()
