import unittest
from research.afh_default_density_xe131.validate_afh_spatial_python_grid import validate_records

def make_row(A,q,mix=6.0):
    return {"A":A,"q_GeV":q,"W_M00_AFH":4.0,"W_PhiPP00_AFH":9.0,
            "W_MPhiPP00_AFH":6.0,"W_SigmaPrime00_AFH":4.0,
            "W_Delta00_AFH_literal":9.0,"W_SigmaPrimeDelta00_AFH_literal":mix}

def grid():
    return [make_row(A,q) for A in (129,131) for q in (0.0,0.1,0.2)]

class AFHSpatialPythonGridValidationTests(unittest.TestCase):
    def test_valid_grid_passes(self):
        result=validate_records(grid(),expected_points=3,q_min=0.0,q_max=0.2)
        self.assertEqual(result["status"],"PASS")
        self.assertFalse(result["native_afh_validated"])
        self.assertEqual(result["actual_total_rows"],6)
    def test_cauchy_schwarz_violation_fails(self):
        rows=grid(); rows[0]["W_SigmaPrimeDelta00_AFH_literal"]=7.0
        result=validate_records(rows,expected_points=3,q_min=0.0,q_max=0.2)
        self.assertEqual(result["status"],"FAIL")
        self.assertTrue(any("Cauchy-Schwarz" in x for x in result["failures"]))
    def test_wrong_q_grid_fails(self):
        rows=grid(); rows[1]["q_GeV"]=0.11
        result=validate_records(rows,expected_points=3,q_min=0.0,q_max=0.2)
        self.assertEqual(result["status"],"FAIL")
        self.assertTrue(any("q-grid mismatch" in x for x in result["failures"]))
    def test_wrong_row_count_fails(self):
        result=validate_records(grid()[:-1],expected_points=3,q_min=0.0,q_max=0.2)
        self.assertEqual(result["status"],"FAIL")

if __name__=="__main__": unittest.main()
