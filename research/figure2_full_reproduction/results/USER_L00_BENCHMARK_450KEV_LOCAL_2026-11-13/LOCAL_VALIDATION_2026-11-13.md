# Local validation — supplied L00 benchmark, Δm = 450 keV

Date: 2026-11-13  
Repository: lm846802297-bit/LZ-3-body-for-hdm  
PR: https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/5  
Source branch: research/figure2-l00-benchmark-450kev  
Source commit: 33ed2e0fa094783b0dba3dd7f7b8a695767fbd1a  
Current main HEAD at archive preparation: e8fa6ecd619dceafcffdb25b5084acee40dbf432

## 1. Source and execution provenance

Exact Git blob IDs used:
- PR-branch eq6_kernel.py: b4eac1242f9301ab8b32c4e83466d8fc218ed581
- main eq6_kernel.py: 7c796b48c3f3c2cb9079ddbf1e632cc0b9ce207c
- PR runner: 71ef22645cc5d15c9419a96083b792b5e7f66e80
- PR tests: 09313ffa3721507224ca466831040687f19ccce2

The PR and main kernels were both run with the same runner; their I6 values agreed at all tested quadrature orders. The final JSON and six-test run use the main kernel blob above. The current main HEAD was fetched and its eq6_kernel.py has the same blob SHA, so the tested numerical dependency is unchanged.

Environment: Python 3.13.5, NumPy 2.3.5, Linux x86_64, natural units, metric (+---).

Reproduce from the repository root:
~~~bash
python research/figure2_full_reproduction/run_user_l00_benchmark.py --nw 48 --nz 40 --nphi 24 --output /tmp/USER_L00_BENCHMARK_450KEV_48x40x24.json
python -m unittest discover -s research/figure2_full_reproduction/tests -p test_user_l00_benchmark.py -v
~~~
No GitHub Actions / CI was used for this local numerical acceptance.

## 2. Benchmark and kinematic convention

Supplied inputs: g1=g2=gVN=1, m_chi1=1 TeV, Delta m=450 keV, mV=10 GeV, ms=300 keV.

The supplied particle benchmark does not determine a unique pointwise L00. The reproducible diagnostic inherits mA=122 GeV (approximate Xe-131 reference), ER=200 keV, v=776 km/s, midpoint W2, z=0.2, phi*=1.1, and target-rest-frame Gamma^0. This is not the AME2020 exact Xe-131 mass prescription and is not a halo-folded prediction.

At this point Wmin2=1000000.6000000901 GeV2 and Wmax2=1000000.6948208088 GeV2. The chi1+s phase space is open, while m_chi2-sqrt(Wmax2)=102.58965597 keV>0, so the internal chi2 pole is not reached.

The width Gamma_chi2=53.38560839 keV is conditional on Dirac chi1/chi2, a pure scalar g2 vertex, and chi2 -> chi1 s as the only open channel. It omits the vector-sector self-energy and UV gauge/Goldstone completion.

## 3. Numerical results

At the W2 midpoint:
- zero-width L00 = 3.3933323920783375e14;
- conditional scalar pole-width L00 = 3.251090649060295e14;
- pointwise change = -4.19180106%.

At quadrature (nW,nz,nphi)=(48,40,24):
- zero-width I6 = 1.6218103153840005e7 GeV2;
- conditional pole-width I6 = 1.5439364806283338e7 GeV2;
- integrated change = -4.80166108%.

The corresponding prefactor-times-I6 values divided by the separate dimensionless nuclear response RA(ER) are 3.7167349466951025 GeV^-3 (zero width) and 3.5382699311972723 GeV^-3 (conditional pole width). These are not complete dσ/dER values until multiplied by a specified RA.

## 4. Independent checks and convergence

- All six checked-in regression tests pass locally with the main kernel.
- Explicit sum over the four initial/final Dirac spin combinations agrees with the trace at relative difference 2.220446049250313e-16.
- Maximum four-momentum closure residual: 2.1316282072803006e-13 GeV.
- Comparing (40,32,20) with (48,40,24): relative I6 differences are 6.53699222863402e-7 (zero width) and 6.661978180222405e-7 (pole width).
- PR-branch and main-kernel I6 outputs agree at (24,24,16), (40,32,20), and (48,40,24).

See QUADRATURE_CONVERGENCE_450KEV.csv for all three quadrature levels.

## 5. Scope

This validates only the supplied pointwise L00 benchmark and reduced Eq. (6) integral under the stated Dirac/scalar-width assumptions. It does not establish the full vector-plus-scalar chi2 self-energy, full UV gauge/Goldstone completion, exact AME2020 isotope-mass prediction, continuous AFH response, halo fold, natural-xenon isotope sum, detector response, or an LZ likelihood.

The separate fixed-speed Xe-131 curve helper and its workflow are excluded from the accepted scope and removed before merge. That helper uses historical PCHIP response interpolation without a dedicated direct-response error validation; it must not be treated as an accepted precision rate calculation.

## 6. Native archive

- USER_L00_BENCHMARK_450KEV_48x40x24.json — high-order benchmark output.
- QUADRATURE_CONVERGENCE_450KEV.csv — native convergence table.
- run_manifest.json — source, runtime, inputs, execution, and validation provenance.
- validation_log.txt — test and independent-check summary.
- SHA256SUMS — checksums of the five native files above (excluding the checksum file itself).

No ZIP/TAR bundle is used as the research-result submission.
