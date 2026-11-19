import unittest
import numpy as np
import reproduce_fig2 as f

class TestFig2(unittest.TestCase):
    def test_exact_endpoints(self):
        lo,hi=f.endpoints()
        self.assertAlmostEqual(lo,106.59121,delta=0.02)
        self.assertAlmostEqual(hi,670.71072,delta=0.02)
    def test_threshold_support(self):
        y=f.phase_space(np.array([0.,100.,200.,680.]),256)
        self.assertEqual(y[0],0.)
        self.assertEqual(y[1],0.)
        self.assertGreater(y[2],0.)
        self.assertEqual(y[3],0.)
    def test_unit_area(self):
        lo,hi=f.endpoints()
        er=np.unique(np.r_[np.linspace(0,700,7001),lo,hi])
        y=f.phase_space(er,256)
        self.assertAlmostEqual(float(np.trapezoid(y/np.trapezoid(y,er),er)),1.,delta=2e-6)
    def test_quadrature_convergence(self):
        er=np.linspace(120,650,101)
        a=f.phase_space(er,256); b=f.phase_space(er,512)
        mask=b>0
        self.assertLess(float(np.max(np.abs(a[mask]-b[mask])/b[mask])),1e-10)

if __name__=="__main__": unittest.main()
