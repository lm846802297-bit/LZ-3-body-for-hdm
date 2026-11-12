# Independent Eq. (6) kernel — first numerical milestone

## Scope

This branch starts the independent numerical implementation of the paper's Eq. (6). It evaluates the fermion-line Dirac trace and the nested three-body phase-space integral over W^2, z=cos(theta*) and the azimuthal average. It deliberately does **not** perform the Galactic-halo velocity integral.

The implementation uses the interaction and current written in `paper-source/main.tex`, assumes Dirac external spinors for this baseline, and takes the target-rest-frame time component Gamma^0 exactly as stated in the manuscript.

## What is implemented

- Exact reconstruction of p, p', k and q in the target rest frame from (v, ER, W^2, z, phi*).
- The two manuscript diagrams:
  `Gamma_before^0 = gamma^0 (slash(p-k)+m_chi2) / ((p-k)^2-m_chi2^2)`
  and
  `Gamma_after^0 = (slash(p'+k)+m_chi2) gamma^0 / (W^2-m_chi2^2+i m_chi2 Gamma_chi2)`.
- Initial-spin average and final-spin sum:
  `L00 = 1/2 Tr[(slash(p')+m) Gamma^0 (slash(p)+m) bar(Gamma)^0]`.
- Explicit interference term, not an incoherent sum.
- Gauss-Legendre integration over W^2 and z; uniform Gauss-Legendre representation of the azimuthal average.

## Numerical checks performed

1. Four-momentum closure and all external mass-shell conditions at a representative open-phase-space point.
2. The trace agrees with an explicit sum over the four initial/final spin combinations to relative precision better than 5e-15 at the tested point.
3. The decomposition before + after + interference reproduces the full trace.
4. A closed-phase-space test for m_s=300 MeV returns exactly zero.
5. The reduced integral converges under increasing quadrature order at the representative point.

## Representative diagnostic point

- m_chi1 = 1 TeV; m_A = 122 GeV (approximate Xe-131 nuclear mass).
- m_s = 300 keV; Delta m = 1 MeV.
- E_R = 200 keV; v = 776 km/s.
- W_min^2 = 1,000,000.60000009 GeV^2.
- W_max^2 = 1,000,000.69482081 GeV^2.
- Reduced Eq. (6) integral (no overall prefactor): 8.78073e5 GeV^2 at (nW,nz,nphi)=(32,32,16).

This is a numerical-kernel diagnostic, **not** a prediction for d sigma/dE_R or an event-rate point.

## Important unresolved model inputs

- The manuscript does not define whether chi1, chi2 are Dirac or Majorana, nor fully specify chiral/CP conventions. The current code is explicitly the Dirac-spinor implementation of the written current; a Majorana variant is not silently assumed.
- The pole width depends on g2 separately. The Figure 2 caption only fixes (g1 g2 gVN)^2, which does not determine g2 and hence does not determine Gamma_chi2. The width is an explicit input to the kernel, not inferred from the product.
- m_V and the numerical xenon response R_A(E_R) are needed to turn this reduced kernel into the complete cross section.
- The original halo distribution is not needed for Eq. (6), and is intentionally excluded at this stage.

## Reproduce

Requires Python 3 and NumPy.

```bash
python -m unittest discover -s research/figure2_full_reproduction/tests -v
```

The next milestone is not yet a halo scan. It is to finish the model-definition audit, establish the width convention and g2 benchmark, and independently cross-check the trace and integral over a wider kinematic grid.


## P0-4 propagator-width audit

The follow-up branch now includes a first comparison of:
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

A separate benchmark has been added for
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


## Draft: fixed-speed Xe-131 differential cross-section curve (450 keV benchmark)

A separate runner is staged at run_user_dsigma_curve.py. It scans the fixed-speed Xe-131 recoil interval at v=776 km/s on a 5 keV grid, evaluates Eq. (6), and compares the AFH GCN/JJ55 nuclear responses. The propagator prescription is zero width. The isotope mass is A*u, consistent with the current response archive, not the AME2020 exact isotope mass.

### Code-level review

- Corrected the phase-space call: eq6_kernel.limits takes five arguments (mchi, ms, mA, ER, speed_kms). Delta m enters reduced_kernel, not limits. The original six-argument call raised TypeError before any scan point could be evaluated.
- Added three local regression tests: an open recoil point, a closed recoil point above threshold, and the GeV^-3 to cm^2/keV conversion. All three pass locally; py_compile passes.
- A code-path smoke test using a synthetic response stub produced 210 rows (105 open recoil energies times two response choices). This is only a software smoke test, not a physical result.

### Response-table diagnostics

- Both GCN and JJ55 tables contain 2,401 q nodes from 0 to 0.6 GeV, with spacing 0.00025 GeV.
- For the proposed 130–650 keV open recoil interval, exact spatial recoil q runs from 0.1781199 to 0.3982887 GeV. The requested q range is inside the tabulated range; no extrapolation is required.
- PCHIP versus linear interpolation has a maximum absolute spread of about 5.31e-4 in R_A over the scan. The largest relative spreads occur near the deep response minimum at 270 keV: 2.32% for GCN and 4.63% for JJ55, where R_A is very small. This is an interpolation-scheme sensitivity diagnostic, not a direct exact-q interpolation error bound. PCHIP values at the two minima were cross-checked against SciPy's PchipInterpolator using the local four-node stencil.

### Merge gate — still Draft

No physical CSV generated by the repository runner or run manifest has been archived yet. Before promotion, run the full scan against the actual response tables, compare the output with an independent SciPy PCHIP evaluation, archive the native CSV and provenance/checksum, and decide whether the response-interpolation uncertainty is acceptable for the intended diagnostic.

This remains a fixed-speed, zero-width diagnostic. It is not a halo-folded recoil spectrum or detector-level LZ prediction, and it does not replace the selected-point AME2020 direct-exact-q fold.
