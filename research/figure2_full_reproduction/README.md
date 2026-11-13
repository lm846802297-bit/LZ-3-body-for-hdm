# Eq. (6) kernel and Figure 2 numerical reproduction

> Canonical archive: main  
> Documentation update: 2026-11-13  
> Scope: three-body kernel, nuclear-response comparisons, natural-xenon theory rates, and the separate 450 keV diagnostics below.

## Scope and calculation layers

This directory contains the Eq. (6) particle-physics kernel and the numerical runners that connect it to selected nuclear-response and natural-xenon calculations. The calculations are related, but they do not all share the same mass scheme, width prescription, nuclear input, or physical output layer.

1. **Kernel layer:** reconstruct the final-state four-momenta, evaluate the Dirac trace, retain interference between the two scalar-emission orderings, and integrate the reduced three-body kernel over \(W^2,z,\phi_*\).
2. **Fixed-speed cross-section layer:** combine the kernel with a specified single-isotope nuclear response to obtain \(d\sigma_A/dE_R\).
3. **Natural-xenon theory-rate layer:** sum isotope-specific contributions and fold over an explicitly selected laboratory-frame halo distribution. The GCN/JJ55 continuous-spectrum runner is a separate nuclear-model comparison; AFH default-density natural-xenon results are archived in the sibling study directory and remain selected-point only.
4. **Detector-interface layer:** fold GCN/JJ55 continuous spectra with the LZ 2026 one-dimensional final-ROI efficiency. This gives rate-level expected event yields, not the official LZ likelihood.
5. **450 keV diagnostics:** a pointwise \(\mathcal L_{00}/I_6\) benchmark with a conditional scalar pole-width comparison, and a separate fixed-speed Xe-131 curve with GCN/JJ55 responses, \(m_A=131u\), and zero width. These two diagnostics are not interchangeable.

## Core Eq. (6) implementation

The kernel uses the interaction/current written in paper-source/main.tex and explicitly records the Dirac-spinor baseline. It does not silently assume a Majorana implementation or supply missing UV/gauge-sector information.

- Exact reconstruction of \(p,p',k,q\) in the target-rest frame from \((v,E_R,W^2,z,\phi_*)\).
- Both manuscript scalar-emission diagrams are included coherently.
- The initial-spin average and final-spin sum are obtained from the Dirac trace.
- The before/after interference term is retained.
- Gauss-Legendre integration is used for \(W^2\) and \(z\), with the azimuthal average normalized consistently with Eq. (6).

## Reproduce the core regression tests

From the repository root:

~~~bash
python -m unittest discover -s research/figure2_full_reproduction/tests -v
~~~

A passing test suite validates only its covered code paths. It does not by itself establish the completeness of the particle model, a full UV self-energy, a continuous AFH natural-xenon spectrum, or an LZ detector likelihood.

## Historical first numerical milestone

The initial kernel milestone used a representative diagnostic point:

- \(m_{\chi_1}=1\) TeV; approximate \(m_A=122\) GeV;
- \(m_s=300\) keV; \(\Delta m=1\) MeV;
- \(E_R=200\) keV; \(v=776\) km/s;
- \(W_{\min}^2=1{,}000{,}000.60000009\) GeV\(^2\);
- \(W_{\max}^2=1{,}000{,}000.69482081\) GeV\(^2\);
- \(I_6=8.78073\times10^5\) GeV\(^2\) at \((n_W,n_z,n_\phi)=(32,32,16)\).

The original representative-point checks covered four-momentum closure, external mass shells, explicit spin sums, before/after/interference decomposition, closed-phase-space behavior, and quadrature convergence. This historical milestone did not include a halo integral; later natural-xenon halo-fold and continuous-spectrum runners are documented separately above and in the main report's Appendix F.

Important model inputs remain explicit: the manuscript does not fully define Dirac/Majorana and chiral/CP conventions; the width depends on \(g_2\) separately; and a complete vector-sector self-energy requires the missing vector/gauge/Goldstone information. Do not infer these inputs from the product \((g_1g_2g_{VN})^2\).

## P0-4 propagator-width audit

The archived implementation includes a comparison of:
- zero width;
- constant pole width;
- a diagnostic running-width ansatz using the current virtual mass W.

The implementation is exposed through `reduced_kernel(..., width_scheme="zero"|"pole"|"running", g2=...)`. The running-width denominator uses `i W Gamma(W)`; it is a diagnostic Breit-Wigner approximation, not a full fermionic self-energy calculation.

Detailed derivation, four benchmark tables, the (W_{\max}<m_{\chi_2}) check over 544–800 km/s, and the numerical convergence comparison are recorded in:

`results/P0-4_PROPAGATOR_WIDTH_AUDIT_ZH.md`.

The P0-4 report deliberately keeps the unresolved Dirac/Majorana definition and the independent (g_2) input explicit. Do not treat the running-width ansatz as the final propagator prescription.


Reproduce the P0-4 table from the repository root:

```bash
python research/figure2_full_reproduction/run_p0_4_width_scan.py
```

This writes:
- `results/P0-4_WIDTH_SENSITIVITY.csv`
- `results/P0-4_GLOBAL_WMAX_CHECK.csv`

See `results/P0-4_PROPAGATOR_WIDTH_AUDIT_ZH.md` for the derivation and interpretation. The initial P0-4 comparison treated running width as a diagnostic ansatz. P0-4b subsequently proved that its absorptive term is exactly the one-loop chi1+s cut under the Dirac / real-scalar / pure-scalar assumptions. It still omits the dispersive Sigma_V and Sigma_S terms and the vector-channel contribution.


## P0-4b: one-loop chi2 scalar-channel self-energy

The scalar Yukawa interaction in the manuscript,
`g2 s bar(chi2) chi1 + h.c.`, has now been evaluated at one loop under the
explicit Dirac-fermion / real-scalar / pure-scalar-vertex assumptions.

Implementation:
- `chi2_scalar_self_energy.py`: finite MS-bar B0/B1 functions, derivatives,
  Sigma_V and Sigma_S, absorptive cut, real on-shell counterterms, and the
  one-loop inverse-propagator denominator.
- `run_p0_4b_scalar_self_energy.py`: benchmark scan.
- `tests/test_chi2_scalar_self_energy.py`: scalar-loop and width-identity tests.

Run:
```bash
python -m unittest discover -s research/figure2_full_reproduction/tests -v
python research/figure2_full_reproduction/run_p0_4b_scalar_self_energy.py
```

Archived outputs:
- `results/P0-4B_SCALAR_SELF_ENERGY.csv`
- `results/P0-4B_OS_DENOMINATOR_COMPARISON.csv`
- `results/P0-4B_SCALAR_SELF_ENERGY_AUDIT_ZH.md`

Key result: the running-width absorptive term used in P0-4a is exactly the
one-loop cut of the chi1+s scalar loop. The full scalar-channel propagator
still includes both dispersive form factors Sigma_V and Sigma_S.

Scope limitation: the manuscript also contains the off-diagonal vector
interaction `g1 V_mu bar(chi2) gamma^mu chi1 + h.c.`. Its one-loop
contribution cannot be fixed from the supplied source because mV and the
gauge/Goldstone completion are absent. Thus the scalar channel is complete
under its stated assumptions, but the full-model chi2 self-energy remains
open until the vector sector is defined.


## Standalone chi2 -> chi1 s pole-width calculation

The exact two-body width used to audit the pole-width input is also available as a standalone calculation:

- `chi2_decay_width.py`: exact factorized two-body width and heavy-fermion limit;
- `tests/test_chi2_decay_width.py`: eight unit tests covering the benchmark, coupling scaling, threshold closure, the keV/MeV distinction, and equivalence to the direct Kallen expression;
- derivation and assumptions: `../docs/08_chi2_decay_width.md`.

Run its unit tests from the repository root:

~~~bash
python -m unittest discover -s research/figure2_full_reproduction/tests -p 'test_chi2_decay_width.py' -v
~~~

Run the reference benchmark:

~~~bash
python research/figure2_full_reproduction/chi2_decay_width.py --mchi1 1000 --delta-m 0.001 --ms 0.0003 --g2 1
~~~

The width is conditional on the Dirac / pure-scalar / single-open-channel assumptions stated in the derivation. It is not yet folded into the integrated three-body recoil spectrum.


## Supplied L00 benchmark: Delta m = 450 keV

A separate benchmark is archived for
\(g_1=g_2=g_{VN}=1\), \(m_{\chi_1}=1\) TeV,
\(m_{\chi_2}=1\) TeV \(+450\) keV, \(m_V=10\) GeV, and
\(m_s=300\) keV.

Reproduce it from the repository root:

~~~bash
python research/figure2_full_reproduction/run_user_l00_benchmark.py
python -m unittest discover -s research/figure2_full_reproduction/tests -p 'test_user_l00_benchmark.py' -v
~~~

The pointwise trace inherits the established diagnostic kinematics
\(m_A=122\) GeV, \(E_R=200\) keV, \(v=776\) km/s,
midpoint \(W^2\), \(z=0.2\), and \(\phi_*=1.1\). These kinematics are
explicitly distinguished from the supplied particle benchmark because the
latter does not specify them.

The finite-width comparison uses the conditional Dirac / pure-scalar /
single-open-channel \(\chi_2\to\chi_1s\) width. It is not the full
vector-plus-scalar self-energy. See
results/USER_L00_BENCHMARK_G1_G2_GVN_1_DELTA_M_450KEV.md.

The high-order result is archived as native data and provenance:
- `results/user_l00_benchmark_delta_m_450kev.json`
- `results/user_l00_benchmark_run_manifest.json`
- `results/USER_L00_BENCHMARK_SHA256SUMS.txt`

The source run (commit `5cbc5d1f779575b348bfab1d74edc71747b8d9ca`, workflow run
42957904328) completed the six regression tests and generated the JSON at
\((n_W,n_z,n_\\phi)=(48,40,24)\). The ZIP transfer artifact was extracted;
only the native JSON and provenance files are committed.



## Independent local validation archive — 2026-11-13

The supplied 450 keV benchmark now has a self-contained local acceptance record under results/USER_L00_BENCHMARK_450KEV_LOCAL_2026-11-13/:

- USER_L00_BENCHMARK_450KEV_48x40x24.json: high-order pointwise L00 and reduced Eq. (6) result;
- QUADRATURE_CONVERGENCE_450KEV.csv: three quadrature orders, ending at (48,40,24);
- LOCAL_VALIDATION_2026-11-13.md: assumptions, independent spin-sum check, four-momentum closure, convergence and scope;
- run_manifest.json, validation_log.txt, and SHA256SUMS: execution provenance and native-file integrity record.

The high-order JSON is byte-identical to the existing results/user_l00_benchmark_delta_m_450kev.json archive. The additional directory preserves the local validation and convergence evidence as a complete, self-contained record. The local acceptance used the same eq6_kernel.py and run_user_l00_benchmark.py blob IDs currently present on main. It validates only the stated pointwise L00 and reduced Eq. (6) integral under the conditional Dirac/pure-scalar/single-channel width assumptions; it is not a halo-folded or detector-level prediction.


## Fixed-speed Xe-131 differential cross-section curve (450 keV benchmark)

The runner and its local diagnostic outputs are archived on main at run_user_dsigma_curve.py and in the results directory. It scans the fixed-speed Xe-131 recoil interval at v=776 km/s on a 5 keV grid, evaluates Eq. (6), and compares the GCN and JJ55 nuclear responses. The propagator prescription is zero width. The isotope mass is A*u, consistent with the current response archive, not the AME2020 exact isotope mass.

### Code-level review

- Corrected the phase-space call: eq6_kernel.limits takes five arguments (mchi, ms, mA, ER, speed_kms). Delta m enters reduced_kernel, not limits. The original six-argument call raised TypeError before any scan point could be evaluated.
- Added three local regression tests: an open recoil point, a closed recoil point above threshold, and the GeV^-3 to cm^2/keV conversion. All three pass locally; py_compile passes.
- A code-path smoke test using a synthetic response stub produced 210 rows (105 open recoil energies times two response choices). This is only a software smoke test, not a physical result.

### Response-table diagnostics

- Both GCN and JJ55 tables contain 2,401 q nodes from 0 to 0.6 GeV, with spacing 0.00025 GeV.
- For the proposed 130–650 keV open recoil interval, exact spatial recoil q runs from 0.1781199 to 0.3982887 GeV. The requested q range is inside the tabulated range; no extrapolation is required.
- PCHIP versus linear interpolation has a maximum absolute spread of about 5.31e-4 in R_A over the scan. The largest relative spreads occur near the deep response minimum at 270 keV: 2.32% for GCN and 4.63% for JJ55, where R_A is very small. This is an interpolation-scheme sensitivity diagnostic, not a direct exact-q interpolation error bound. PCHIP values at the two minima were cross-checked against SciPy's PchipInterpolator using the local four-node stencil.

## Local physical curve calculation — 2026-11-13

The fixed-speed Xe-131 differential curve has now been calculated locally and independently checked at the level of the archived response interpolation and Eq. (6) quadrature.

- 105 open recoil points, 130–650 keV in 5 keV steps; 655 keV is closed.
- Benchmark: mχ1 = 1 TeV, Δm = 450 keV, ms = 300 keV, mV = 10 GeV, v = 776 km/s, (g1 g2 gVN)^2 = 1.
- Both AFH GCN and JJ55 responses are included; q = sqrt(2 mA ER + ER^2), with mA = 131 u.
- Maximum dσ/dER: GCN 1.874622684e-32 cm²/keV and JJ55 1.985254401e-32 cm²/keV, both at 175 keV.
- A 1-keV local refinement resolves sampled dips at GCN 269/551 keV and JJ55 270/555 keV. These are sampled grid minima, not continuous minimizers.
- Ten-anchor independent SciPy PCHIP check: maximum absolute difference 3.553e-15; maximum relative difference 4.929e-14.
- Full-grid independent PCHIP reconstruction at all 105 exact recoil q values: maximum relative difference 4.64e-10 (GCN) and 3.80e-10 (JJ55), consistent with the rounded R_A values in the pointwise CSV.
- Eq. (6) quadrature comparison (20,16,12) vs (24,20,16), ten anchors: maximum relative change 7.346e-6.
- The χ2 s-channel pole is closed throughout this recoil interval; the minimum clearance is 85.663520 keV.

The corrected local validation report is recorded at
`results/USER_DSIGMA_CURVE_450KEV_LOCAL_2026-11-13.md`.
The native outputs are archived on main:

- `results/fixed_speed_xe131_dsigma_450kev.csv`
- `results/local_minima_refinement_1keV.csv`
- `results/kernel_quadrature_convergence_450kev.csv`
- `results/metadata_user_dsigma_450kev.json`
- `results/USER_DSIGMA_CURVE_450KEV_LOCAL_2026-11-13.md`
- `results/SHA256SUMS_user_dsigma_450kev.txt`

The SHA256 manifest is calculated against the committed LF-normalized file contents. The local archive also retains the original run metadata and a separate checksum manifest.

### Scope boundary and follow-up

The numerical output and native provenance are archived on main. The remaining scientific follow-up is: keep the A*u mass approximation and zero-width prescription explicitly confined to this benchmark, and do not interpret this fixed-speed, single-isotope curve as a halo-folded or detector-level LZ prediction.

This remains a fixed-speed, zero-width diagnostic using the A*u Xe-131 mass. It is not the AME2020 direct-exact-q result, a natural-xenon halo-folded recoil spectrum, a detector-level LZ prediction, or an exclusion/likelihood calculation.

### Reproduce the fixed-speed Xe-131 curve and figures

From the repository root:

```bash
python research/figure2_full_reproduction/run_user_dsigma_curve.py \
  --step-keV 5 --nw 20 --nz 16 --nphi 12 \
  --output /tmp/xe131_dsigma_450kev.csv
python research/figure2_full_reproduction/plot_user_dsigma_curve.py
python -m unittest discover -s research/figure2_full_reproduction/tests -p 'test_user_dsigma_curve.py' -v
```

The committed 105-point curve covers the interior window 130–650 keV. The full open interval is approximately [109.150286, 654.955583] keV, so 20.8497 keV at the lower end and 4.9556 keV at the upper end are not yet included. Both boundary brackets are tested; high-order Eq. (6) integration in the omitted endpoint regions remains follow-up work.

The two archived SVGs are:
- results/plots/fixed_speed_xe131_dsigma_450kev.svg
- results/plots/xe131_gcn_jj55_response_ratio_450kev.svg

This milestone remains a fixed-speed, single-isotope diagnostic with the A*u mass approximation and zero-width prescription. It is not a natural-xenon halo-folded spectrum, detector-level LZ prediction, event-rate calculation, or exclusion.


## AFH Xe-131 native response validation

The independent Wolfram 14.0.0 native Mathematica/Python 2401-point response comparison is archived at [NATIVE_MATHEMATICA_AUDIT.md](../afh_default_density_xe131/output/native_audit/NATIVE_MATHEMATICA_AUDIT.md). This validates the Xe-131 AFH response layer only; it does not validate the full Eq. (6) continuous recoil integral, the seven-isotope AFH continuous spectrum, or an LZ detector likelihood.
