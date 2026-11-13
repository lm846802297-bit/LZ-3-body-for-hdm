from pathlib import Path
import csv
import importlib.util
import math
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("afh_runner", HERE / "run_afh_default_xe131.py")
afh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(afh)


class AFHDefaultXe131Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = afh.read_density_matrix_csv(HERE / "afh_default_xe131_density_matrix.csv")
        cls.b_fm = math.sqrt(41.467 / (45*131**(-1/3) - 25*131**(-2/3)))
        cls.b = cls.b_fm * 5.0677
        cls.Tiso = abs(131/2 - 54)

    def test_density_matrix_inventory(self):
        self.assertEqual(len(self.rows), 67)
        self.assertEqual(sum(r["rank"] == 0 and r["isospin"] == 0 for r in self.rows), 16)
        self.assertEqual(sum(r["rank"] == 2 and r["isospin"] == 0 for r in self.rows), 8)

    def test_default_oscillator_length(self):
        self.assertAlmostEqual(self.b_fm, 2.2923417985218975, places=12)

    def test_afh_isoscalar_zero_momentum_convention(self):
        W00, _ = afh.package_w00(0.0, self.rows, self.b, self.Tiso)
        Rpackage = 4*math.pi/(2*afh.J_A+1)*W00
        self.assertLess(abs(Rpackage/(131**2/4)-1), 2e-4)

    def test_equal_pn_normalization(self):
        W00, _ = afh.package_w00(0.0, self.rows, self.b, self.Tiso)
        Rpackage = 4*math.pi/(2*afh.J_A+1)*W00
        physical_raw = 4*Rpackage
        self.assertLess(abs(physical_raw/(131**2)-1), 2e-4)
        physical_normalized = 131**2 * physical_raw/physical_raw
        self.assertAlmostEqual(physical_normalized, 131**2, places=10)

    def test_paper_python_and_mma_share_physical_factor4_convention(self):
        repo_root = HERE.parents[1]
        paper = (repo_root / "paper-source" / "main.tex").read_text(encoding="utf-8")
        mma_runner = (HERE / "run_afh_default_xe131.wls").read_text(encoding="utf-8")
        mma_verifier = (HERE / "verify_afh_xe131_native.wls").read_text(encoding="utf-8")
        comparator = (HERE / "compare_afh_mathematica_python.py").read_text(encoding="utf-8")

        self.assertIn(r"\\frac{16\\pi}{2J_A+1}", paper)
        self.assertIn(r"W_{M,\\mathrm{AFH,v6}}^{00}", paper)
        self.assertIn(r"q=\\sqrt{2m_AE_R+E_R^2}", paper)
        self.assertNotIn(r"\\mathcal R_A(E_R)=4\\pi W_M^{00}", paper)

        self.assertIn("rEqualRaw = 4.0*rAFH;", mma_runner)
        self.assertIn("rRaw[q_?NumericQ] := 16 Pi/(2 jA + 1) wm[q];", mma_verifier)
        self.assertIn('"R_equal_pn_raw"', comparator)
        self.assertIn('"raw_AFH_W_M00"', comparator)

    def test_independent_high_precision_kernel_check_points(self):
        # Reference values independently checked with 60-digit mpmath evaluation
        # of the finite sums in AFH BesselElement.
        expected = {
            (0.157, 0): 0.16587194445197020453,
            (0.157, 2): 0.26402074701536012526,
            (0.25625, 0): -0.00073663417732777932351,
            (0.25625, 2): -0.01861327862684671077,
            (0.365, 0): -0.00042424625191455005691,
            (0.365, 2): 0.029211388204593898543,
        }
        for (q, rank), target in expected.items():
            value = afh.compute_amplitude(q, rank, self.rows, self.b, self.Tiso)
            self.assertAlmostEqual(value, target, delta=2e-11)

    def test_minima_locations(self):
        with (HERE / "output" / "minima.csv").open(newline="", encoding="utf-8") as f:
            minima = list(csv.DictReader(f))
        expected = [157.93578, 256.27187, 365.06657, 499.37189]
        self.assertEqual(len(minima), 4)
        for got, want in zip(minima, expected):
            self.assertAlmostEqual(float(got["q_min_MeV"]), want, delta=0.01)


if __name__ == "__main__":
    unittest.main()

