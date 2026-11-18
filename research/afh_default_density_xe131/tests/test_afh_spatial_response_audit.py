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
                self.assertLessEqual(wsd*wsd,ws*wd+max(1e-24,1e-12*ws*wd))

    def test_response_bundle_reuses_consistent_channel_definitions(self):
        bundle,_=spatial.response_bundle(131,0.158,self.rows[131])
        wm,ws,wd,wsd,_=spatial.response(131,0.158,self.rows[131])
        wm2,wphi,wmphi,_=spatial.phi_response(131,0.158,self.rows[131])
        self.assertAlmostEqual(bundle["W_M00_AFH"],wm,places=13)
        self.assertAlmostEqual(bundle["W_SigmaPrime00_AFH"],ws,places=13)
        self.assertAlmostEqual(bundle["W_Delta00_AFH_literal"],wd,places=13)
        self.assertAlmostEqual(bundle["W_SigmaPrimeDelta00_AFH_literal"],wsd,places=13)
        self.assertAlmostEqual(bundle["W_M00_AFH"],wm2,places=13)
        self.assertAlmostEqual(bundle["W_PhiPP00_AFH"],wphi,places=13)
        self.assertAlmostEqual(bundle["W_MPhiPP00_AFH"],wmphi,places=13)

    def test_default_q_anchors_match_native_grid(self):
        self.assertEqual(len(spatial.Q_POINTS),11)
        self.assertIn(0.25625,spatial.Q_POINTS)
        self.assertIn(0.49925,spatial.Q_POINTS)

    def test_parity_audit_schema(self):
        audit=spatial.parity_audit()
        self.assertIn("delta_wrapper_requires",audit)
        self.assertIn("deltaop_3j_requires",audit)
        self.assertIn("logical_conflict",audit)
        self.assertIn("delta_prime_is_not_delta_j",audit)

    def test_delta_uses_deltaop_not_deltaprime(self):
        source=spatial.delta_inner_element
        # The DeltaJ path must call the same-rank MJLDivQ component.
        # A direct numerical regression is intentionally deferred until
        # native Wolfram output is available.
        self.assertTrue(callable(source))
        audit=spatial.parity_audit()
        self.assertFalse(audit["logical_conflict"])
        self.assertTrue(audit["delta_prime_is_not_delta_j"])

    def test_native_xe131_m_phi_crosscheck_at_selected_q(self):
        native_path=HERE/"output"/"phi_response_native"/"afh_default_xe131_M_PhiPP_native.csv"
        with native_path.open(newline="",encoding="utf-8") as stream:
            native={round(float(row["q_GeV"]),8):row for row in __import__("csv").DictReader(stream)}
        for q in (0.0,0.05,0.10,0.158,0.25625,0.365,0.49925,0.60):
            wm,wphi,wmphi,_=spatial.phi_response(131,q,self.rows[131])
            row=native[round(q,8)]
            for got,key in ((wm,"W_M00_AFH"),(wphi,"W_PhiPP00_AFH"),(wmphi,"W_MPhiPP00_AFH")):
                self.assertTrue(math.isclose(got,float(row[key]),rel_tol=5e-9,abs_tol=2e-13),
                                msg=f"q={q} {key}: Python={got} native={row[key]}")

if __name__=="__main__":
    unittest.main()
