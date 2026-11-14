# Natural-xenon regression tests

The four test modules cover separate parts of the natural-xenon calculation:

| Test module | Coverage |
|---|---|
| `test_afh_default_xenon_response_grid.py` | Official AFH v6.0 default-isotope dispatch, density-matrix entries, spins, elastic multipoles, q=0 normalization and the Xe-131 2,401-node baseline |
| `test_afh7_hybrid9_continuous_spectrum.py` | AFH-7/Hybrid-9/Helm-9 scenario composition, SHM speed quadrature, three-body kinematics and threshold-kernel convergence |
| `test_high_energy_tail_model_sensitivity.py` | Analytic piecewise-linear efficiency folding, benchmark/model coverage and rate-level scope |
| `test_target_number.py` | Nine-isotope natural-xenon mass average, target nuclei per kg and the unrenormalized AFH-supported abundance fraction |

Run all tests from the repository root:

~~~bash
python -m unittest discover -s research/afh_default_density_natural_xenon_halo/tests -p 'test_*.py' -v
~~~

These are regression and consistency checks. They do not by themselves regenerate the full seven-isotope response grid, rerun the selected-point direct exact-q fold, or produce a detector-level likelihood.
