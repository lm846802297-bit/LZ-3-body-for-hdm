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

    def test_response_functions_are_finite(self):
        for A in (129,131):
            for q in (0.0,0.158,0.256,0.365):
                wm,ws,wd,wsd,amp=spatial.response(A,q,self.rows[A])
                self.assertTrue(all(math.isfinite(x) for x in (wm,ws,wd,wsd)))
                self.assertGreaterEqual(wm,0.0)
                self.assertGreaterEqual(ws,0.0)
                self.assertGreaterEqual(wd,0.0)

    def test_delta_uses_deltaop_not_deltaprime(self):
        source=spatial.delta_inner_element
        # The DeltaJ path must call the same-rank MJLDivQ component.
        # A direct numerical regression is intentionally deferred until
        # native Wolfram output is available.
        self.assertTrue(callable(source))
        audit=spatial.parity_audit()
        self.assertFalse(audit["logical_conflict"])
        self.assertTrue(audit["delta_prime_is_not_delta_j"])

if __name__=="__main__":
    unittest.main()
