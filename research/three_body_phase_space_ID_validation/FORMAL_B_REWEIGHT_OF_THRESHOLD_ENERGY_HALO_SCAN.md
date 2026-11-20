# Formal B reweight of the PR86 threshold-energy seven-isotope halo scan

**Status:** local calculation and independent GitHub reproduction both PASS; native GitHub artifact downloaded and compared against local outputs.  
**Date:** 2026-11-20  
**Input:** PR86 high-order 5--800 keV scan using the unified exact threshold-energy \(u^2\) map.  
**Output:** formal B finite-nucleon correction applied to all seven isotope contributions and the natural-xenon total.

## 1. Research question and conclusion

Does the adopted B baseline,
\[
F_1^{V,N}(t_N),\quad F_2^{V,N}(t_N),\quad W_M(y_A),
\]
change the full three-body versus \(I(D_{NR})\) comparison after the exact threshold-energy Halo scan?

**Conclusion:** the B correction leaves every individual isotope's full/\(I(D_{NR})\) ratio unchanged to numerical precision. It changes the natural-xenon ratio only through the relative reweighting of isotope contributions, and that change is at most \(1.61\times10^{-5}\) percentage points in the 180--320 keV candidate interval. The absolute rate correction is much larger: approximately 26--34% in the candidate interval and up to about 58% over the full scan.

This separation is exact at the isotope level because the finite-nucleon factor depends on isotope and recoil energy, but not on the internal three-body phase-space variables.

## 2. Immutable source and benchmark

| Item | Source |
|---|---|
| Halo high-order input | [PR86 workflow run 44655861356](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44655861356) |
| Halo artifact | ID 14595907606; SHA-256 `05ceeea175e39ed658b0bfab4a15f6f654e1a49a9508c147291ef58c622471f8` |
| Input rows | 1,456 isotope-energy rows and 208 natural-xenon recoil points |
| B form-factor implementation | research/nucleon_form_factor_B_baseline/apply_nucleon_form_factors_B.py |
| Electromagnetic form-factor source | Borah et al., Phys. Rev. D 102, 074012 (2020), arXiv:2003.13640 |
| Strange-current alternatives | Sufian 2017; Alexandrou 2020 charge-weighted converted to unit current; Alexandrou 2026 continuum unit-current slope-only |

The seven-isotope AFH input covers 99.8158% of natural xenon atom abundance. Xe-124 and Xe-126 are absent from this AFH source set; the seven isotope abundances are retained without renormalization. The source rate has nonzero support from 105 to 695 keV for this benchmark. The input is in relative-rate units, so this reweighting reports B/source-rate ratios and B-corrected relative rates rather than a newly normalized detector event rate.

The input is the PR86 numerical-comparison benchmark:
\[
m_{\chi_1}=1\ {\rm TeV},\quad m_s=300\ {\rm keV},\quad
\Delta m=10\ {\rm MeV},\quad m_V=5\ {\rm GeV},
\]
with the historical zero-width comparison prescription. This is the same benchmark as the seven-isotope full-versus-\(I(D_{NR})\) scan, not the four production benchmarks in PR87.

## 3. Formal transfer and B multiplier

The calculation uses the formal impulse prescription
\[
t_N=t_A=-2m_AE_R,\qquad Q_A^2=2m_AE_R+E_R^2.
\]
The form factors use \(Q_N^2=-t_N=2m_AE_R\). The exact spatial \(Q_A^2\) remains the AFH Fourier-transfer variable.

The normalized charge coefficient is
\[
\widehat c_M^B(t_N)=\frac{c_M^{\rm raw}(t_N)}{3}
=\widehat F_1^B(t_N)
+\frac{t_N}{8m_N^2}
\left[\widehat F_1^B(t_N)+2\widehat F_2^B(t_N)\right],
\]
and the rate multiplier is
\[
\mathcal C_A^B(E_R)=|\widehat c_{M,A}^B(t_N)|^2.
\]
It multiplies both the full and \(I(D_{NR})\) isotope contributions at fixed \(A,E_R\). No three-body phase-space integral is rerun.

For 3,000 correlated Borah2020 electromagnetic-coefficient covariance draws (seed 20261119), the code also propagates the EM form-factor covariance into the B-weighted full rate, \(I(D_{NR})\) rate, and their ratio. The three strange-current central-value models are kept separate; their lattice errors are not sampled in this pass.

## 4. Isotope-resolved result

For each isotope,
\[
\frac{R_{A,B}^{\rm full}}{R_{A,B}^{I(D_{NR})}}
=
\frac{\mathcal C_A^B R_{A,A}^{\rm full}}
{\mathcal C_A^B R_{A,A}^{I(D_{NR})}}
=
\frac{R_{A,A}^{\rm full}}{R_{A,A}^{I(D_{NR})}}.
\]
The largest numerical difference between the A and B isotope-level relative-error columns is
\[
\boxed{2.23\times10^{-14}\ {\rm percentage\ points}}
\]
over the 1,271 isotope-energy rows with nonzero \(I(D_{NR})\) support, for each of the three strange-current alternatives.

Thus the seven-isotope comparison is unchanged by B at fixed isotope and recoil energy. The isotope-resolved absolute rates are still modified by \(\mathcal C_A^B\).

## 5. Natural-xenon result

The B correction changes the natural-xenon ratio only because the seven isotope contributions are reweighted before summation.

### Candidate interval: 180--320 keV

| Strange-current input | Maximum \(|R_{\rm full}/R_{I(D)}-1|\) | Recoil energy |
|---|---:|---:|
| Sufian 2017 | 0.0355091723% | 320 keV |
| Alexandrou 2020 converted | 0.0355086926% | 320 keV |
| Alexandrou 2026 continuum | 0.0355091998% | 320 keV |

For the Sufian input:
\[
\delta_B(248\ {\rm keV})=0.0314062867\%,
\]
\[
\delta_B(267\ {\rm keV})=0.0342009503\%,
\]
\[
\delta_B(320\ {\rm keV})=0.0355091723\%.
\]

The maximum absolute change in the natural-xenon relative-error curve between A and B over 180--320 keV is \(1.61\times10^{-5}\) percentage points across the three strange-current inputs.

### Full interval: 5--800 keV

All three strange-current alternatives give
\[
\boxed{\delta_B^{\max}=0.3527630812\%\quad\text{at }E_R=695\ {\rm keV}.}
\]
At this point the dominant isotope contribution makes the common B multiplier cancel from the natural-xenon ratio as well.

### Absolute rate correction

The B correction has a substantial effect on absolute rates even though the full/\(I(D_{NR})\) ratio barely changes. For the Sufian input, the natural-xenon full-rate shift is
- \(-26.4442\%\) at 248 keV;
- \(-28.6016\%\) at 267 keV;
- \(-32.8075\%\) at 320 keV;
- \(-56.4345\%\) at 695 keV.

Across the three strange-current alternatives, the 320 keV correction ranges from \(-32.7463\%\) to \(-33.8341\%\); at 695 keV it ranges from \(-56.3300\%\) to \(-58.2480\%\).

The B correction therefore matters for absolute event rates, while it does not materially alter the full-versus-\(I(D_{NR})\) comparison.

## 6. Electromagnetic covariance

The 3,000-draw Borah2020 covariance propagation gives a maximum 68% interval width in the natural-xenon full/\(I(D_{NR})\) ratio of \(5.26\times10^{-9}\) in ratio units over 180--320 keV (about \(5.26\times10^{-7}\) percentage points). This is negligible relative to the central \(3.55\times10^{-2}\%\) discrepancy.

For the Sufian 2017 input at 248 keV, the B-corrected natural-xenon full rate is \(9.06064\times10^{-5}\) at the covariance median, with p16/p84 values \(9.00426\times10^{-5}\) and \(9.11894\times10^{-5}\). This corresponds to approximately \(-0.622\%\) and \(+0.643\%\) relative to the median. The three strange-current alternatives remain separate central-value scenarios; their lattice uncertainties are not sampled.

This statement concerns the correlated electromagnetic z-expansion coefficient covariance only. The three strange-current alternatives remain separate central-value scenarios.

For the Sufian 2017 input at 248 keV, the B-corrected natural-xenon full rate is \(9.06064\times10^{-5}\) at the covariance median, with p16/p84 values \(9.00426\times10^{-5}\) and \(9.11894\times10^{-5}\). This is approximately \(-0.622\%\) and \(+0.643\%\) relative to the median. The three strange-current alternatives remain separate central-value scenarios; their lattice uncertainties are not sampled.

## 7. Reproduction and outputs

The new workflow downloads the exact PR86 high-order artifact and runs the existing formal B postprocessor without repeating the Halo scan:

- Workflow: .github/workflows/pr86-halo-formal-B-reweight.yml
- B implementation: research/nucleon_form_factor_B_baseline/apply_nucleon_form_factors_B.py
- B form-factor model: research/nucleon_form_factor_B_baseline/borah2020_lowq2.py
- Source artifact: run 44655861356, artifact 14595907606

For each strange-current input the output contains:
- seven_isotope_B_baseline.csv (1,456 rows);
- natural_xenon_B_baseline.csv (208 rows);
- metadata.json (transfer, normalization, covariance, and result provenance).

The workflow additionally writes RUN_MANIFEST.json and SHA256SUMS and uploads the output artifact as pr86-formal-B-halo-reweight. The local run independently verified all 11 generated CSV/JSON/checksum files against SHA256SUMS; the three models each contain 1,456 isotope rows and 208 natural-xenon rows.

## 8. Physical interpretation

1. The B form factor must be included for absolute recoil rates and event-yield predictions.
2. The isotope-resolved full/\(I(D_{NR})\) ratio is exactly invariant under the common per-isotope B multiplier.
3. The natural-xenon ratio changes only through isotope reweighting, by at most \(1.61\times10^{-5}\) percentage points in the candidate interval.
4. The three-body phase-space comparison remains a robust statement; the important B effect is the absolute rate normalization.
5. This is a zero-width numerical-comparison benchmark. It does not replace the formal finite-pole-width production calculation or the separate NEST detector-response fold.


### Independent GitHub reproduction: PASS

The independent workflow [44672770451](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44672770451) completed successfully. All 19 existing B-baseline regression tests passed. The three model reweightings, row-count checks, isotope cancellation, natural-xenon error shifts, and covariance-width gates also passed.

The workflow uploaded artifact 14599834070, pr86-formal-B-halo-reweight, with SHA-256:
05368fa13890932bed0124a651de53a998570524a70d3fe33a6992d1610f1bd9.

I downloaded the GitHub artifact and compared all six numeric CSV outputs against the local 3,000-draw calculation. The largest relative difference in any finite numeric CSV field is below (4.6\times10^{-13}); the largest absolute difference in the exact spatial-transfer column is (1.11\times10^{-16}\,\mathrm{GeV}^2). The independently generated artifact's own SHA256SUMS check also passes. The local calculation and GitHub reproduction therefore agree to floating-point precision.


### Independent high-order halo rerun: PASS

The full high-order halo validation workflow [44673037709](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44673037709) completed successfully. It regenerated the baseline and high-order scans, compared all 1,456 isotope-energy rows and 208 natural-xenon points, found zero support mismatches, and uploaded artifact 14602217987 (`halo-seven-isotope-full-vs-ID-full-recoil-scan`; SHA-256 `eb8926b395cde165dc1f483644c999756129ca626edb78ac1b95160f642a3d9d`).

For the independently regenerated high-order natural-xenon spectrum:
- maximum (|mathrm{Full}/I(D_{NR})-1|) over 180–320 keV: (0.0355190413\%), at 320 keV;
- maximum over the full supported 5–800 keV grid: (0.3527618038\%), at 695 keV;
- the 208-point natural-xenon grid and 1,456 isotope-energy rows are complete;
- AFH isotope abundance coverage remains 99.8158%, with Xe-124/Xe-126 absent and no abundance renormalization.

The baseline-to-high-order quadrature comparison gives zero support mismatches. The maximum natural-xenon full-rate shift is (9.8863\times10^{-6}\%), the maximum (I(D_{NR})) rate shift is (1.7092\times10^{-5}\%), and the maximum approximation-error shift is (1.0792\times10^{-5}) percentage points. At isotope level, the maximum approximation-error shift is (2.8425\times10^{-5}) percentage points.

I downloaded the high-order GitHub artifact and compared it with the archived local scan. The full halo kernel agrees to a maximum relative difference of (2.82\times10^{-8}); the (I(D_{NR})) kernel is identical. The maximum absolute difference in the derived isotope relative-error column is (2.83\times10^{-6}) percentage points, and the maximum natural-xenon relative-error difference is (1.75\times10^{-6}) percentage points. These small differences do not change the convergence conclusion or any acceptance result.
