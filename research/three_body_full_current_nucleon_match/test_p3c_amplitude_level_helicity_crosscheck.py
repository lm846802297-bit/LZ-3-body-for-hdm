import sys
import unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import p3c_amplitude_level_helicity_crosscheck as p3c

class P3CAmplitudeLevelTests(unittest.TestCase):
    def setUp(self):
        rng=np.random.default_rng(20261119)
        c=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4))
        self.G=np.einsum("ma,nb->manb",c,c.conj())
        self.Q=.2552681134213372; self.f1=1.; self.f2=-.184; self.mN=.938918
    def test_afh_q_minus_axis_basis_is_right_handed(self):
        e=p3c.basis()
        self.assertEqual(set(e),{-1,1})
        self.assertTrue(np.allclose(np.cross([1,0,0],[0,-1,0]),[0,0,-1]))
        self.assertAlmostEqual(float(np.vdot(e[1],e[1]).real),1.,places=14)
    def test_spin_resolved_helicity_coefficients_reproduce_eq107(self):
        h,L=p3c.helicity_coeffs(self.G,self.Q,self.f1,self.f2,self.mN)
        d=p3c.eq107(L,self.Q,self.f1,self.f2,self.mN)
        for k in d: self.assertAlmostEqual(h[k],d[k],delta=2e-12*max(abs(d[k]),1.))
    def test_per_rank_amplitude_reconstruction_matches_cartesian_contraction(self):
        h,L=p3c.helicity_coeffs(self.G,self.Q,self.f1,self.f2,self.mN)
        d=p3c.eq107(L,self.Q,self.f1,self.f2,self.mN)
        amps={1:(.13-.07j,-.21+.04j),2:(-.03+.02j,.05+.08j),3:(.09+.11j,-.17-.06j)}
        kc,rc=p3c.kernel(d,amps,1.00008,1.5)
        kh,rh=p3c.kernel(h,amps,1.00008,1.5,h["helicity_components"])
        self.assertAlmostEqual(kc,kh,delta=2e-12*max(abs(kc),1.))
        for J in amps: self.assertAlmostEqual(rc[J],rh[J],delta=2e-12*max(abs(rc[J]),1.))
    def test_wrong_sigma_prime_helicity_phase_reverses_signed_interference(self):
        h,L=p3c.helicity_coeffs(self.G,self.Q,self.f1,self.f2,self.mN)
        wrong,_=p3c.helicity_coeffs(self.G,self.Q,self.f1,self.f2,self.mN,phase=-1.)
        d=p3c.eq107(L,self.Q,self.f1,self.f2,self.mN)
        self.assertAlmostEqual(h["C_SigmaPrimeDelta"],d["C_SigmaPrimeDelta"],delta=2e-12*abs(d["C_SigmaPrimeDelta"]))
        self.assertAlmostEqual(wrong["C_SigmaPrimeDelta"],-d["C_SigmaPrimeDelta"],delta=2e-12*abs(d["C_SigmaPrimeDelta"]))
        self.assertAlmostEqual(wrong["C_Delta"],d["C_Delta"],places=12)
        self.assertAlmostEqual(wrong["C_SigmaPrime"],d["C_SigmaPrime"],places=12)

if __name__=="__main__": unittest.main()
