import math
import unittest
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import eq6_kernel as eq6

class Eq6Tests(unittest.TestCase):
    def setUp(self):
        self.M=1000.; self.ms=3e-4; self.dm=1e-3
        self.mA=122.; self.ER=2e-4; self.v=776.
        self.wmin,self.wmax=eq6.limits(self.M,self.ms,self.mA,self.ER,self.v)
    def test_closed_300_mev(self):
        self.assertEqual(eq6.reduced_kernel(self.M,.300,self.dm,self.mA,self.ER,self.v,nw=4,nz=4,nphi=4),0.)
    def test_open_interval(self):
        self.assertGreater(self.wmax,self.wmin)
    def test_mass_shell_and_four_momentum(self):
        W=.5*(self.wmin+self.wmax)
        pt=eq6.build_point(self.M,self.ms,self.mA,self.ER,self.v,W,.23,1.17)
        for value in eq6.residuals(pt,self.M,self.ms,self.mA).values():
            self.assertLess(abs(value),3e-7)
    def test_trace_real_positive_and_decomposed(self):
        W=.5*(self.wmin+self.wmax)
        pt=eq6.build_point(self.M,self.ms,self.mA,self.ER,self.v,W,-.31,2.01)
        d=eq6.spin_trace(pt,self.M,self.M+self.dm)
        self.assertGreaterEqual(d["total"],0.)
        self.assertLess(d["imaginary_residual"],1e-8*d["total"])
        self.assertAlmostEqual(d["before"]+d["after"]+d["interference"],d["total"],delta=1e-8*d["total"])
    def test_trace_matches_explicit_spinor_sum(self):
        W=.5*(self.wmin+self.wmax)
        pt=eq6.build_point(self.M,self.ms,self.mA,self.ER,self.v,W,.2,1.1)
        b,a=eq6.vertices(pt,self.M+self.dm); G=b+a
        sig=[np.array([[0,1],[1,0]],complex),np.array([[0,-1j],[1j,0]],complex),np.array([[1,0],[0,-1]],complex)]
        def u(p,m,s):
            chi=np.eye(2,dtype=complex)[:,s]
            low=sum(sig[i]*p[i+1] for i in range(3))@chi/(p[0]+m)
            return math.sqrt(p[0]+m)*np.r_[chi,low]
        direct=0.
        for si in range(2):
            ui=u(pt.p,self.M,si)
            for sf in range(2):
                uf=u(pt.p_prime,self.M,sf)
                amp=uf.conj().T@eq6.GAMMA[0]@G@ui
                direct+=abs(amp)**2/2.
        trace=eq6.spin_trace(pt,self.M,self.M+self.dm)["total"]
        self.assertAlmostEqual(direct/trace,1.,places=11)
    def test_conditional_width_helper(self):
        width = eq6.chi2_width_dirac_scalar(
            self.M, self.ms, self.dm, 1.0
        )
        self.assertGreater(width, 0.0)
        self.assertEqual(
            eq6.chi2_width_dirac_scalar(self.M, 0.002, 0.001, 1.0),
            0.0
        )

    def test_quadrature_convergence(self):
        coarse=eq6.reduced_kernel(self.M,self.ms,self.dm,self.mA,self.ER,self.v,nw=16,nz=16,nphi=8)
        fine=eq6.reduced_kernel(self.M,self.ms,self.dm,self.mA,self.ER,self.v,nw=32,nz=32,nphi=16)
        self.assertLess(abs(fine/coarse-1.),5e-5)

if __name__=="__main__": unittest.main()
