from pathlib import Path
import importlib.util
import math
import unittest

HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("spatial",HERE/"run_afh_spatial_response_audit.py")
spatial=importlib.util.module_from_spec(spec)
spec.loader.exec_module(spatial)

class AFHSpatialResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows={A:spatial.load_matrix(A) for A in (129,131)}

    def test_density_matrix_inventories(self):
        self.assertEqual(len(self.rows[129]),39)
        self.assertEqual(len(self.rows[131]),67)

    def test_sigma_prime_is_nonzero_for_odd_xenon(self):
        for A in (129,131):
            wm,ws,wd,wsd,amp=spatial.response(A,0.0,self.rows[A])
            self.assertGreater(wm,0)
            self.assertGreater(ws,0)
            self.assertEqual(wd,0.0)
            self.assertEqual(wsd,0.0)

    def test_selected_sigma_prime_regression_values(self):
        expected={
            (129,0.0):0.020808872289191187,
            (129,0.158):2.9451890212616142e-6,
            (129,0.256):9.220954095438105e-5,
            (131,0.0):0.014707821388042728,
            (131,0.158):8.55117023e-4,
            (131,0.256):7.9205386e-5,
            (131,0.365):1.70004742e-4,
        }
        for (A,q),value in expected.items():
            _,ws,_,_,_=spatial.response(A,q,self.rows[A])
            self.assertTrue(math.isclose(ws,value,rel_tol=3e-6,abs_tol=1e-12),(A,q,ws,value))

    def test_delta_parity_conflict_is_explicit(self):
        audit=spatial.parity_conflict()
        self.assertTrue(audit["logical_conflict"])
        self.assertIn("odd",audit["delta_wrapper_requires"])
        self.assertIn("even",audit["delta_inner_3j_requires"])

if __name__=="__main__":
    unittest.main()
