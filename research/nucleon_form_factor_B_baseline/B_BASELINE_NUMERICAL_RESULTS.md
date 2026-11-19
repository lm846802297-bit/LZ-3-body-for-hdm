# B baseline numerical results

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

The following table reports the change in the full halo-folded natural-xenon rate after applying the finite nucleon form factor, relative to the existing pointlike-nucleon A baseline:

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

- PR: [#83](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/83)
- B-baseline workflow: [run 44574863232](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44574863232)
- Source halo/high-order workflow: [run 44560087038](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44560087038)
- B artifact: \`finite-nucleon-form-factor-B-baseline\`
- Regression tests: 10 passed.
- Repository layout and Figure 2 benchmark manifest checks: passed.

## Remaining work

1. Decide whether the 2026 strange-current slope-only cross-check should be replaced by a reconstruction of its full published \(z\)-expansion.
2. Propagate the strange-lattice input uncertainties once a usable coefficient covariance or joint fit information is available.
3. Fold the B-baseline recoil spectrum through the LZ detector efficiency, energy-resolution kernel, exposure and analysis window to obtain observable event counts.
