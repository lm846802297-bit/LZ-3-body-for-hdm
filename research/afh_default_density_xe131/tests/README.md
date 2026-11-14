# Xe-131 AFH regression tests

This folder contains the five regression suites for the AFH default Xe-131 study.

| Test | Coverage |
|---|---|
| `test_afh_default_xe131.py` | AFH density-matrix inventory, oscillator length, factor-four convention, and response implementation |
| `test_afh_four_benchmarks.py` | Four-benchmark AFH/GCN/JJ55 response substitution, exact-q convention, and shared Eq. (6) integral |
| `test_ame2020_hybrid_natural_xenon.py` | Xe-131-only AME2020 replacement and rejection of inconsistent/missing baseline terms |
| `test_ame2020_xe131_halo_partial.py` | AME2020 mass prescription, halo normalization, and exact-spatial versus NR-approximate response momentum |
| `test_compute_four_benchmark_dsigma.py` | Corrected four-benchmark differential cross-section grid and response-column integrity |

Run all tests from the repository root:

~~~bash
python -m unittest discover -s research/afh_default_density_xe131/tests -p 'test_*.py' -v
~~~

These are software/regression checks. They do not, by themselves, establish a full natural-xenon prediction or an LZ likelihood.
