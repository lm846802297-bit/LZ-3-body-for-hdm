import csv
import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
RESEARCH = HERE.parent
sys.path.insert(0, str(HERE))
import afh_vv_phi_xe131 as audit


class AFHVVPhiXe131Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = RESEARCH / 'afh_default_density_xe131' / 'input' / 'afh_default_xe131_density_matrix.csv'
        cls.minima = RESEARCH / 'afh_default_density_xe131' / 'output' / 'minima.csv'
        cls.rows = audit.read_matrix(cls.matrix)

    def test_matrix_inventory_and_isoscalar_rank_coverage(self):
        self.assertEqual(len(self.rows), 67)
        self.assertEqual(sum(r['rank'] == 0 and r['isospin'] == 0 for r in self.rows), 16)
        self.assertEqual(sum(r['rank'] == 2 and r['isospin'] == 0 for r in self.rows), 8)

    def test_default_oscillator_length(self):
        self.assertAlmostEqual(audit.B_FM, 2.2923417985218975, places=12)
        self.assertAlmostEqual(audit.B_GEV_INV, 11.61690053236942, places=11)

    def test_q0_response_and_nonzero_phi_double_prime(self):
        wm, wp, wmp, _, _ = audit.calculate([0.0], self.rows)
        self.assertAlmostEqual(float(wm[0]), 1365.5162934039433, places=9)
        self.assertAlmostEqual(float(wp[0]), 47.51550032254746, places=8)
        self.assertAlmostEqual(float(wmp[0]), -254.63655637049632, places=8)
        self.assertGreater(float(wp[0]), 0.0)

    def test_mass_response_amplitudes_reproduce_archived_minima(self):
        with self.minima.open(newline='', encoding='utf-8') as f:
            minima = list(csv.DictReader(f))
        self.assertEqual(len(minima), 4)
        for row in minima:
            q = float(row['q_min_MeV'])/1000
            _, _, _, m_amp, _ = audit.calculate([q], self.rows)
            self.assertAlmostEqual(float(m_amp[0][0]), float(row['rank0_amplitude']), places=11)
            self.assertAlmostEqual(float(m_amp[2][0]), float(row['rank2_amplitude']), places=11)

    def test_selected_q256_response_ratio(self):
        q = 0.25627186761670686
        wm, wp, wmp, _, _ = audit.calculate([q], self.rows)
        self.assertAlmostEqual(float(wp[0]/wm[0]), 115.88946418006599, places=8)
        self.assertAlmostEqual(float(wmp[0]/wm[0]), -1.4624899896015526, places=8)

    def test_full_grid_cauchy_schwarz(self):
        q = [i*0.00025 for i in range(2401)]
        wm, wp, wmp, _, _ = audit.calculate(q, self.rows)
        corr = abs(wmp)/((wm*wp)**0.5)
        self.assertLessEqual(float(max(corr)), 1.0+1e-9)
        self.assertAlmostEqual(float(max(corr)), 0.9999998601592628, places=10)

    def test_raw_physical_factor_and_shape_normalization_are_distinct(self):
        physical_factor = 4*4*math.pi/(2*audit.J_A+1)
        wm0, _, _, _, _ = audit.calculate([0.0], self.rows)
        raw_r0_over_a2 = physical_factor*float(wm0[0])/audit.A**2
        self.assertAlmostEqual(raw_r0_over_a2, 0.9999174770036694, places=12)
        self.assertNotAlmostEqual(raw_r0_over_a2, 1.0, places=7)


if __name__ == '__main__':
    unittest.main(verbosity=2)
