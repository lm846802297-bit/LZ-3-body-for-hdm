import importlib.util, unittest
from pathlib import Path
import numpy as np
SCRIPT=Path(__file__).resolve().parents[1]/"scripts/reproduce_fig2_mass_inference.py"
spec=importlib.util.spec_from_file_location("fig2_trial",SCRIPT)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

class Fig2TrialTests(unittest.TestCase):
    def test_endpoint_inversion(self):
        lo,hi=mod.META["red_curve_endpoints_keV"]
        mu,mt,mc=mod.invert(lo,hi)
        self.assertAlmostEqual(mt/1e6,121.043,delta=.02)
        self.assertAlmostEqual(mc/1e9,1.0,delta=.001)
    def test_A130u_endpoint_match(self):
        lo0,hi0=mod.META["red_curve_endpoints_keV"]
        *_,lo,hi,peak=mod.spectrum(130*.93149410242)
        self.assertLess(abs(lo-lo0),.2); self.assertLess(abs(hi-hi0),.8)
    def test_122_GeV_is_distinct(self):
        lo0,hi0=mod.META["red_curve_endpoints_keV"]
        *_,lo,hi,peak=mod.spectrum(122.)
        self.assertGreater(abs(lo-lo0),1.); self.assertGreater(abs(hi-hi0),10.)
    def test_three_body_normalization(self):
        e,_,y,*_=mod.spectrum(121.043)
        self.assertAlmostEqual(mod.integ(y,e)/1e3,1.,places=7)
    def test_peak_formula(self):
        *_,peak=mod.spectrum(121.043)
        self.assertAlmostEqual(peak,325.996,delta=.02)

if __name__=="__main__": unittest.main()
