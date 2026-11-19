import csv
import json
import tempfile
import unittest
from pathlib import Path

from apply_nucleon_form_factors_B import process_one


class ApplyNucleonFormFactorsBTests(unittest.TestCase):
    def test_postprocessor_multiplies_each_isotope_and_resums(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            inp=root/"input"; out=root/"output"
            inp.mkdir()
            isotope_rows=[]
            for A,mA,abund,full,approx in [
                (129,120.0,0.264,2.0,1.99),
                (131,122.0,0.212,3.0,2.98),
            ]:
                isotope_rows.append({
                    "ER_keV":"248.0","A":str(A),
                    "natural_atom_fraction":str(abund),
                    "mA_GeV":str(mA),
                    "R_A_AFH_direct_exact_q":"0.5",
                    "vmin_exact_km_s":"500",
                    "vmin_NR_km_s":"501",
                    "halo_kernel_full":str(full),
                    "halo_kernel_I_D":str(approx),
                    "full_contribution_relative_units":str(full),
                    "I_D_contribution_relative_units":str(approx),
                    "isotope_relative_error_pct":str((full/approx-1)*100),
                    "approximation_zero_full_nonzero":"False",
                })
            with (inp/"seven_isotope_halo_comparison.csv").open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(isotope_rows[0]))
                w.writeheader(); w.writerows(isotope_rows)
            natural=[{
                "ER_keV":"248.0",
                "natural_xenon_full_relative_rate":"5.0",
                "natural_xenon_I_D_relative_rate":"4.97",
                "relative_error_pct":str((5/4.97-1)*100),
            }]
            with (inp/"natural_xenon_halo_comparison.csv").open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(natural[0]))
                w.writeheader(); w.writerows(natural)

            summary=process_one(
                inp,out,"sufian2017_unit_current",n_draws=64,seed=11
            )
            with (out/"seven_isotope_B_baseline.csv").open(newline="") as f:
                result=list(csv.DictReader(f))
            with (out/"natural_xenon_B_baseline.csv").open(newline="") as f:
                total=list(csv.DictReader(f))
            self.assertEqual(len(result),2)
            self.assertEqual(len(total),1)
            self.assertTrue(all(float(r["nucleon_FF_rate_multiplier"])>0 for r in result))
            self.assertAlmostEqual(
                float(total[0]["natural_xenon_full_B_relative_rate"]),
                sum(float(r["full_contribution_B_relative_units"]) for r in result),
                places=12,
            )
            self.assertEqual(summary["status"],"COMPUTED")
            self.assertTrue((out/"metadata.json").exists())


if __name__=="__main__":
    unittest.main()
