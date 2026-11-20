# B baseline numerical results

> **Historical transfer-convention note:** The numerical tables in this PR85 record preserve the original static diagnostic \(t_N=-Q_A^2\). The formal impulse prescription is now \(t_N=t_A=-2m_AE_R\). The updated formal B results and the added pointlike P comparison are documented in [POINTLIKE_NUCLEON_P_A_B_COMPARISON.md](POINTLIKE_NUCLEON_P_A_B_COMPARISON.md). Re-evaluating the detector-level B yields with the formal transfer changes them by only \(1.1\times10^{-5}\%\) to \(3.1\times10^{-5}\%\); the convention is nevertheless kept explicit and consistent in the production code.

## Executive result

The selected B baseline has now been applied to the converged seven-isotope halo-folded three-body calculation:

\[
F_1^{uds}(t_N),\quad F_2^{uds}(t_N),\quad W_M(y_A),
\]

with

\[
Q_A^2=2m_AE_R+E_R^2,\qquad t_N=-Q_A^2,
\]

and the normalized nucleon charge factor

\[
\mathcal C_N(Q_A^2)=\left|\frac{c_M(t_N)}{3}\right|^2.
\]

The postprocessor leaves the original three-body phase-space integral, halo folding, mediator factor and finite-size AFH \(W_M\) response unchanged. It multiplies each isotope contribution by \(\mathcal C_N\) and then re-sums natural xenon.

The zero-momentum regression is exact within numerical precision:

\[
c_M(0)=3,\qquad \mathcal C_N(0)=1.
\]

## Input and numerical setup

- Electromagnetic proton/neutron form factors: Borah, Hill, Lee and Tomalak, Phys. Rev. D 102, 074012 (2020), arXiv:2003.13640.
- The separate proton and neutron low-\(Q^2\) z-expansion fits are used, with the pinned free-coefficient covariance matrices.
- The four free coefficients are completed with the \(G(0)\) normalization and the four \(Q^4\) asymptotic sum rules.
- The Borah electromagnetic coefficient covariance is propagated with 3000 correlated Monte Carlo draws on the full \(Q_A^2\) grid.
- AFH isotopes: Xe-128, 129, 130, 131, 132, 134 and 136.
- Natural atom-fraction coverage: 0.998158; the abundances are not renormalized.
- Recoil grid: 208 energies covering 5--800 keV, with 10-keV coarse spacing and 1-keV spacing over 180--320 keV.
- The three-body/halo source is the accepted high-order scan from workflow run 44560087038.

Three strange-current scenarios are retained separately:

1. Sufian 2017, unit strange current, historical primary benchmark.
2. Alexandrou 2020, charge-weighted result converted to the unit strange current.
3. Alexandrou 2026, continuum-limit physical-point result, represented by its published electric and magnetic slopes. This third scenario is slope-only; the full published \(z\)-expansion coefficient covariance is not reconstructed.

## Natural-xenon B/A rate ratio

The following table reports the change in the full halo-folded natural-xenon rate after applying the finite nucleon form factor, relative to the existing zero-transfer A reference baseline:

\[
\Delta_B(E_R)=100\left[\frac{(dR/dE_R)_B}{(dR/dE_R)_A}-1\right].
\]

| \(E_R\) [keV] | Sufian 2017 | Alexandrou 2020 converted | Alexandrou 2026 slope-only |
|---:|---:|---:|---:|
| 180 | -20.4190% | -21.0477% | -20.3810% |
| 200 | -22.3012% | -22.9895% | -22.2596% |
| 248 | -26.4442% | -27.2648% | -26.3949% |
| 267 | -28.6017% | -29.4917% | -28.5483% |
| 300 | -31.2795% | -32.2564% | -31.2212% |
| 320 | -32.8075% | -33.8341% | -32.7463% |

Across the candidate interval 180--320 keV, the finite nucleon form factor suppresses the natural-xenon rate by approximately 20--34%, depending on recoil energy and strange-current input.

At the two reference energies:

- 248 keV: suppression is 26.39--27.26%.
- 267 keV: suppression is 28.55--29.49%.

The spread between the three strange-current scenarios is 0.870 percentage points at 248 keV and 0.943 percentage points at 267 keV. The dominant finite-\(Q_A\) suppression is therefore set by the proton/neutron electromagnetic form factors; the strange-current choice is a smaller but retained input dependence.

## Isotope dependence

For the historical Sufian 2017 scenario, the per-isotope rate multiplier \(\mathcal C_N=|F_M|^2\) is:

| Isotope | \(\mathcal C_N\) at 248 keV | \(\mathcal C_N\) at 267 keV |
|---|---:|---:|
| Xe-128 | 0.73972 | 0.72360 |
| Xe-129 | 0.73805 | 0.72185 |
| Xe-130 | 0.73639 | 0.72012 |
| Xe-131 | 0.73473 | 0.71838 |
| Xe-132 | 0.73308 | 0.71666 |
| Xe-134 | 0.72979 | 0.71322 |
| Xe-136 | 0.72652 | 0.70980 |

The heavier isotopes have slightly larger \(Q_A^2\) at fixed \(E_R\), and hence a slightly stronger nucleon form-factor suppression. The isotope ordering follows directly from the exact recoil momentum prescription; no isotope-specific form-factor fit is introduced.

## Full three-body result versus \(I(D)\)

After applying the same \(\mathcal C_N(Q_A^2)\) to the full three-body rate and the \(I(D)\) approximation, the natural-xenon discrepancy in the 180--320 keV candidate region is:

- 248 keV: 0.031406% for the three scenarios to the shown precision.
- 267 keV: 0.034201% for the three scenarios to the shown precision.
- Maximum over 180--320 keV: 0.035510%.

Thus the B correction changes the absolute recoil rate substantially, while the full three-body versus \(I(D)\) approximation remains accurate at the few-\(10^{-2}\)% level in the candidate region.

Across the complete 208-point grid, the largest full-versus-\(I(D)\) difference reaches 0.3528% near 695 keV. At that energy the A-baseline rate is only \(7.59\times10^{-9}\) of its grid maximum, below the \(10^{-8}\) active-region threshold used in the convergence audit.

## Electromagnetic fit uncertainty

The Borah 2020 proton/neutron coefficient covariance gives the following central 68% half-widths for the natural-xenon B full rate:

- 248 keV: 0.633--0.636%, depending on the strange-current scenario.
- 267 keV: 0.681--0.685%.
- Across 180--320 keV: approximately 0.47--0.77%.

These are the propagated electromagnetic-fit coefficient uncertainties only. The separate strange-lattice uncertainties are recorded in the source metadata but are not sampled in this first pass.

## B-baseline quadrature convergence

Comparing the B-applied baseline halo scan against the high-order halo scan gives:

| Strange-current scenario | Max natural-xenon full-B rate shift | Max natural-xenon \(I(D)\)-B rate shift | Max change in full-vs-\(I(D)\) error |
|---|---:|---:|---:|
| Sufian 2017 | \(9.8851\times10^{-6}\%\) | \(1.7092\times10^{-5}\%\) | \(1.0792\times10^{-5}\) percentage points |
| Alexandrou 2020 converted | \(9.8850\times10^{-6}\%\) | \(1.7092\times10^{-5}\%\) | \(1.0792\times10^{-5}\) percentage points |
| Alexandrou 2026 slope-only | \(9.8851\times10^{-6}\%\) | \(1.7092\times10^{-5}\%\) | \(1.0792\times10^{-5}\) percentage points |

The finite nucleon form factor is a deterministic recoil/isotope multiplier, so it does not degrade the convergence of the underlying three-body and halo integrations.

## Corrected strange magnetic-radius implementation

The 2020 magnetic radius is defined from the normalized magnetic form factor. The correct expansion is

\[
G_M^s(Q^2)=\mu_s\left[1-\frac{\langle r_M^2\rangle_s}{6}Q^2+O(Q^4)\right].
\]

The implementation now includes the factor \(\mu_s\) multiplying the slope. A regression test differentiates the implemented form factor and recovers the published radius. The 2026 continuum-limit scenario uses the same normalized-radius convention.

## Reproducibility

- PR: [#85](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/85)
- B-baseline, LZ detector fold and electromagnetic covariance workflow: [run 44587255746](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44587255746)
- Source halo/high-order workflow: [run 44560087038](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44560087038)
- Permanent archive and SHA-256 verification: [run 44593911420](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44593911420)
- Permanent native-output archive: [results/2026-11-20-B-baseline-PR85/README.md](results/2026-11-20-B-baseline-PR85/README.md)
- Regression tests: 14 passed in the latest complete workflow.
- Repository layout and Figure 2 benchmark manifest checks: passed.

## LZ 2026 detector-efficiency fold of the absolute B spectra

The B correction was also applied to the archived 84-point absolute AFH-7/Hybrid-9 natural-xenon spectra and passed through the existing LZ 2026 final-WIMP-search-ROI NR efficiency fold. The A-spectrum reconstruction from isotope-resolved kernels closes against the archived A spectrum at the configured \(2\times10^{-11}\) relative tolerance.

Detector-fold configuration:

- Exposure: \(2.84\) tonne-year (\(1{,}037{,}310\) kg-day).
- Reconstructed analysis interval used by the rate-level fold: \(5.4\)–\(269.9\) keV.
- Efficiency: digitized central LZ 2026 Fig. S2 final-WIMP-search-ROI NR efficiency, with its published gray envelope retained separately.
- Integration: exact integral of piecewise-linear \(dR/dE_R\) times piecewise-linear efficiency over the union of knots.
- Maximum dense-trapezoid cross-check difference: \(3.59\times10^{-7}\).
- The 2026 strange-current scenario is slope-only; the strange-lattice input uncertainties are not sampled.

### Expected events for the three strange-current inputs

Central efficiency-weighted expected events in the \(2.84\) tonne-year exposure:

| Benchmark | AFH-7: Sufian 2017 | AFH-7: Alexandrou 2020 | AFH-7: Alexandrou 2026 |
|---|---:|---:|---:|
| \(m_s=200\) keV, \(\Delta m=1\) MeV | \(2.66263\times10^{-1}\) | \(2.64697\times10^{-1}\) | \(2.66358\times10^{-1}\) |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | \(1.10267\times10^{-3}\) | \(1.09357\times10^{-3}\) | \(1.10322\times10^{-3}\) |
| \(m_s=360\) keV, \(\Delta m=1\) MeV | \(2.07412\times10^{-9}\) | \(2.04975\times10^{-9}\) | \(2.07559\times10^{-9}\) |
| \(m_s=300\) keV, \(\Delta m=10\) MeV | \(9.02733\times10^{-6}\) | \(8.95286\times10^{-6}\) | \(9.03183\times10^{-6}\) |

For Hybrid-9, the corresponding Sufian 2017 yields are \(0.266932\), \(1.10469\times10^{-3}\), \(2.07412\times10^{-9}\), and \(9.04390\times10^{-6}\). The difference from AFH-7 is due only to the explicitly labelled Helm fallback for Xe-124 and Xe-126; the seven AFH isotope contributions are unchanged.

### Detector-level A/B comparison

Using the archived A detector-fold results as the denominator, the Sufian 2017 B/A event-yield ratios are:

| Benchmark | A AFH-7 events | B AFH-7 events | B/A | Change |
|---|---:|---:|---:|---:|
| \(m_s=200\) keV, \(\Delta m=1\) MeV | 0.317278 | 0.266263 | 0.83921 | \(-16.08\%\) |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | \(1.39790\times10^{-3}\) | \(1.10267\times10^{-3}\) | 0.78881 | \(-21.12\%\) |
| \(m_s=360\) keV, \(\Delta m=1\) MeV | \(2.85849\times10^{-9}\) | \(2.07412\times10^{-9}\) | 0.72560 | \(-27.44\%\) |
| \(m_s=300\) keV, \(\Delta m=10\) MeV | \(1.14430\times10^{-5}\) | \(9.02733\times10^{-6}\) | 0.78890 | \(-21.11\%\) |

The detector-integrated suppression is smaller than the suppression at \(E_R\simeq250\) keV because the event yield integrates over the full analysis interval, including lower recoil energies where the nucleon form-factor correction is weaker.

For fixed \(g_2\), the Sufian 2017 AFH-7 values of the coupling-product-squared required for one central expected event are:

| Benchmark | \( (g_1g_2g_{VN})^2_{\;N=1}\) |
|---|---:|
| \(m_s=200\) keV, \(\Delta m=1\) MeV | \(3.75569\times10^{-8}\) |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | \(9.06888\times10^{-6}\) |
| \(m_s=360\) keV, \(\Delta m=1\) MeV | \(4.82131\) |
| \(m_s=300\) keV, \(\Delta m=10\) MeV | \(1.10775\times10^{-3}\) |

The expected yields are all below one event at the reference coupling product squared \(10^{-8}\). The coupling thresholds above are rate-level one-event benchmarks, not exclusion limits.

### Detector-level scope

The fold applies the published NR efficiency and the \(2.84\) tonne-year exposure. It does not apply energy-resolution smearing, an event-level S1c/\(\log_{10}S2_c\) signal PDF, a background model, a profile likelihood, or a confidence-level construction. The efficiency gray envelope is not assigned a confidence level by LZ.

### Propagated electromagnetic form-factor covariance

The Borah et al. (2020) proton/neutron coefficient covariance has now been propagated through the complete isotope-resolved B spectrum and the LZ efficiency integral. The calculation uses 3000 correlated draws (seed 20261119), with the same draw applied consistently across recoil energies and isotopes. This preserves the induced cross-recoil and cross-isotope correlations.

For the historical Sufian 2017 unit-current benchmark, the detector-level 16th--84th percentile intervals are:

| Benchmark | Central events | EM-covariance p16--p84 | Half-width |
|---|---:|---:|---:|
| \(m_s=200\) keV, \(\Delta m=1\) MeV | 0.266263 | [0.265358, 0.267155] | 0.3375% |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | \(1.10267\times10^{-3}\) | [\(1.09727\times10^{-3}\), \(1.10809\times10^{-3}\)] | 0.4906% |
| \(m_s=360\) keV, \(\Delta m=1\) MeV | \(2.07412\times10^{-9}\) | [\(2.06049\times10^{-9}\), \(2.08769\times10^{-9}\)] | 0.6559% |
| \(m_s=300\) keV, \(\Delta m=10\) MeV | \(9.02733\times10^{-6}\) | [\(8.98313\times10^{-6}\), \(9.07165\times10^{-6}\)] | 0.4904% |

Across the three strange-current scenarios, the electromagnetic-covariance half-width is 0.337--0.660% for these four benchmarks. The central-yield versus Monte Carlo median difference is below 0.01%.

The numerical closure checks are:

- Maximum reconstructed-A-spectrum relative difference: \(5.55\times10^{-16}\).
- Maximum central detector-yield closure difference against the independent central B fold: zero at stored precision.
- Non-finite covariance draws: zero.
- The vectorized draw integration agrees with the scalar exact piecewise-linear integral in the regression tests.

These intervals quantify the Borah electromagnetic fit covariance only. Strange-lattice uncertainties and the LZ gray efficiency envelope remain separate and are not sampled or combined here.

## Remaining work

1. Decide whether the 2026 strange-current slope-only cross-check should be replaced by a reconstruction of its full published \(z\)-expansion.
2. Propagate the strange-lattice input uncertainties once a usable coefficient covariance or joint fit information is available.
3. Add energy-resolution smearing and the two-dimensional S1c/\(\log_{10}S2_c\) response, then build the background likelihood if a formal LZ exclusion is required.
