# Task brief: apply formal nucleon baseline B to the PR86 halo scan

**Date:** 2026-11-20  
**Owner:** LZ-3-body-for-hdm research  
**Status:** high-order Halo validation PASS; formal-B reweight on the accepted high-order artifact PASS; native output checksums verified

## Objective

Take the already-converged PR86 high-order seven-isotope full three-body versus \(I(D_{\rm NR})\) halo scan and apply the adopted formal nucleon baseline B:
\[
F_1^{V,N}(t_N),\qquad F_2^{V,N}(t_N),\qquad W_M(y_A).
\]
Do not rerun the three-body phase-space or halo integrations. Reweight each isotope contribution with the formal B rate multiplier and reconstruct natural xenon.

## Frozen input

- Workflow run: 44681433965.
- Artifact ID: 14607350801.
- Artifact name: halo-seven-isotope-full-vs-ID-full-recoil-scan.
- Artifact SHA-256: a570bbf81119e8b7b87526c51b7012d056c0c07e290618bb7e12469b43571194.
- Source commit: aabaf2f2c8ecb1b9de28cf29c13cc1f92fa10f83.
- Input files: halo-seven-isotope-highorder/seven_isotope_halo_comparison.csv and natural_xenon_halo_comparison.csv.
- Expected input dimensions: 1,456 isotope rows and 208 natural-xenon recoil points.

The AFH input covers 99.8158% of natural xenon atom abundance. Xe-124 and Xe-126 are not in the AFH source set; do not renormalize the remaining isotope abundances.

## Formal B convention

Use
\[
t_N=t_A=-2m_AE_R,\qquad Q_A^2=2m_AE_R+E_R^2.
\]
The finite nucleon form factors use \(-t_N=2m_AE_R\); the exact spatial \(Q_A^2\) remains the AFH Fourier variable. The normalized charge coefficient is \(F_M=\widehat c_M=c_M^{\rm raw}/3\), and the isotope rate multiplier is \(|F_M|^2\). Keep the factor of three exactly once under \(g_{VN}=3g_{Vq}\).

Use the pinned Borah et al. (2020) electromagnetic z-expansion coefficients and covariance from GENIE-MC/Generator commit e2e04f19e96d395ac646cf3382841646b60fa1b4. Retain three separate strange-current inputs:
- Sufian 2017 unit current;
- Alexandrou 2020 charge-weighted form factors converted by \(e_s=-1/3\);
- Alexandrou 2026 continuum unit-current slope-only input.

Use 3,000 electromagnetic covariance draws with seed 20261119. Do not sample strange-lattice uncertainties in this pass.

## Required outputs

For each strange-current input:
- seven_isotope_B_baseline.csv (1,456 rows);
- natural_xenon_B_baseline.csv (208 rows);
- metadata.json.

The workflow must also create RUN_MANIFEST.json and SHA256SUMS, then upload one artifact named pr86-formal-B-halo-reweight.

## Local calculation and acceptance checks

The local run has completed all three scenarios and produced 11 native CSV/JSON/checksum files. All checksums pass.

Acceptance criteria:
1. Exactly 1,456 isotope rows and 208 natural-xenon rows per model.
2. The isotope-level full/\(I(D_{\rm NR})\) relative-error columns remain equal within \(10^{-11}\) percentage points.
3. The maximum natural-xenon full/\(I(D_{\rm NR})\) discrepancy in 180--320 keV remains between 0.0354% and 0.0357%.
4. The maximum discrepancy over 5--800 keV remains between 0.3526% and 0.3529%.
5. The maximum change in the natural-xenon relative-error curve between source and B is below \(2\times10^{-5}\) percentage points in 180--320 keV.
6. The 68% covariance interval width in the natural-xenon full/\(I(D_{\rm NR})\) ratio remains below \(6\times10^{-9}\) in ratio units in 180--320 keV.
7. The source transfer convention and AFH finite-size response are retained; no detector response is applied.

## Numerical outcome

At 248 keV the natural-xenon full-rate correction relative to the uncorrected input is:
- Sufian 2017: \(-26.4442\%\);
- Alexandrou 2020 converted: \(-27.2648\%\);
- Alexandrou 2026 continuum: \(-26.3949\%\).

Across 180--320 keV the suppression is about 20.4--33.8%. The isotope-level full/\(I(D_{\rm NR})\) ratio is unchanged to \(2.23\times10^{-14}\) percentage points. The maximum natural-xenon relative-error change is \(1.60\times10^{-5}\) percentage points. The full-scan maximum discrepancy is 0.3527631% at 695 keV.

## Scope boundary

This task produces a B-reweighted halo rate-ratio archive. It does not rerun phase space, change AFH nuclear responses, add \(W_{\Phi''}\) or \(W_{M\Phi''}\), apply detector response, or produce an LZ likelihood/exclusion. The next detector step should consume the resulting B spectrum through the existing LZ rate-level fold.


## Independent reproduction completed

- GitHub workflow run: 44672770451 (success).
- Uploaded artifact ID: 14599834070.
- Artifact SHA-256: 05368fa13890932bed0124a651de53a998570524a70d3fe33a6992d1610f1bd9.
- All 19 B-baseline regression tests passed.
- All numerical gates passed for the three strange-current scenarios.
- Downloaded GitHub CSV outputs agree with the local outputs to below (4.6\times10^{-13}) maximum relative difference in finite numeric fields.
- The downloaded artifact's SHA256SUMS verification passed.


## Independent high-order halo validation

- Workflow run: 44673037709 (success).
- Artifact ID: 14602217987; SHA-256: eb8926b395cde165dc1f483644c999756129ca626edb78ac1b95160f642a3d9d.
- 1,456 isotope-energy rows and 208 natural-xenon recoil points; zero support mismatches.
- Natural-xenon maximum full/(I(D_{NR})) discrepancy: 0.0355190413% in 180–320 keV and 0.3527618038% over the full supported scan.
- Baseline-to-high-order maximum natural-xenon approximation-error shift: (1.0792\times10^{-5}) percentage points.
- GitHub versus archived local full halo kernel: maximum relative difference (2.82\times10^{-8}); the (I(D_{NR})) kernel is identical.
- Derived isotope relative-error maximum absolute difference: (2.83\times10^{-6}) percentage points.


## Accepted high-order convergence inputs

The pinned high-order artifact metadata records speed quadrature order 32 and internal quadrature (12,4,4), with 1,456 isotope-energy rows and 208 natural-xenon recoil points. The natural-xenon maximum Full/I(D_NR) discrepancy is 0.0355190413% in 180--320 keV and 0.3527618038% over 5--800 keV. Baseline-to-high-order active-support shifts are 9.8863e-6% (Full), 9.9873e-6% (I(D_NR)), and 2.9057e-6 percentage points (approximation error).

The formal-B workflow input has been updated to this accepted artifact and verifies the metadata quadrature settings before applying the nucleon form factors.


## Final high-order B reproduction

- Reweight workflow: 44689438445 (success).
- Output artifact: 14608091362.
- Output artifact SHA-256: b9d261a68a73e480a6e4d84c3aef9c57a0fc5fc80aa1be7079170d0305b6c6c5.
- All 19 regression tests passed; all three strange-current scenarios passed every numerical gate.
- Downloaded artifact ZIP digest and all nine native output-file checksums verified.
- Candidate-window maximum natural-xenon Full/I(D_NR) discrepancy: 0.0355092%.
- Full-range maximum discrepancy: 0.3527618%.
- Maximum isotope A/B ratio difference: 2.22e-14 percentage points.
- Maximum candidate-window B-induced error-curve change: 1.60e-5 percentage points.
- Maximum 68% covariance interval width: 5.2531e-9 in ratio units.

This artifact supersedes the earlier formal-B output as the canonical B reweight of the accepted high-order Halo input.
