# LZ 2026 formal B baseline: event-weighted NEST NR response fold

**Status:** local calculation and independent GitHub reproduction both PASS; downloaded GitHub artifact matches the local outputs exactly.  
**Date:** 2026-11-20  
**Primary nuclear response:** AFH-7.  
**Diagnostic nuclear response:** Hybrid-9 (AFH-7 plus Helm fallback for Xe-124/Xe-126).

## 1. Purpose and scope

This calculation carries the adopted formal nucleon baseline B into the existing stratified NEST NR response. It produces event-weighted \(S1_c\)--\(\log_{10}S2_c\) signal intensities and observable-ROI event yields for all four Fig. 2 benchmarks.

The formal B prescription is
\[
\widehat F_{1,2}^{\,N}(t_N)=\frac{F_{1,2}^{uds,N}(t_N)}{3},
\qquad
\widehat c_M^B(t_N)=
\widehat F_1^B(t_N)+
\frac{t_N}{8m_N^2}
\left[\widehat F_1^B(t_N)+2\widehat F_2^B(t_N)\right],
\]
with
\[
t_N=t_A=-2m_AE_R,\qquad
Q_A^2=2m_AE_R+E_R^2.
\]
The invariant \(t_N\) is used in the nucleon form factors; the exact spatial \(Q_A^2\) remains in the AFH Fourier variable. The B input metadata is checked by the fold program before any event weighting.

This is the detector-response continuation of the four-benchmark production calculation in PR #87. Its particle benchmark is \(m_V=10\) GeV, \(g_2=1\), and the conditional pure-scalar pole-width prescription. It is distinct from the PR #86 zero-width \(m_s=300\) keV, \(\Delta m=10\) MeV, \(m_V=5\) GeV numerical comparison benchmark.

## 2. Frozen inputs and provenance

| Input | Immutable source | Version / provenance |
|---|---|---|
| Stratified NEST response | [run 43697104437](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43697104437), artifact 14155360851 | NEST commit 541b6430dae6ea289cf110c99f174a9187f7fdee; SHA-256 682e2ba71063d6ef835b37a6d328a84ab7c609f404856aa83d56e4b875794bab |
| Formal B spectra and Fig. S2 rate-level counts | [PR #87 workflow run 44662497177](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44662497177), artifact 14596147908 | source commit 40a3291ba2d00516ed8d6f8bf69c48531326047d; SHA-256 f5c1d8d791bffff3159a6e279e5a0e68b705bf07466be6b489ba9a49e29ce7ac |
| B form-factor choices | PR #87 | Sufian 2017, Alexandrou 2020 converted to unit strange current, Alexandrou 2026 continuum unit-current slope-only |
| Nuclear response | AFH v6.0 | AFH-7 is primary; Hybrid-9 retains the separately labelled Helm fallback for Xe-124/Xe-126 |

The response artifact contains four event samples (eft2024, tableS5, ws2024, generic). Each sample has 1,060,000 events: 265 one-keV true-energy strata, two replicas, and 2,000 events per replica and stratum. The generated spatial prior is a uniform active-TPC cylinder proxy, not the official calibration-source or fiducial-volume distribution.

The formal B source artifact contains the four benchmarks:
- red: \(m_s=200\) keV, \(\Delta m=1\) MeV;
- green: \(m_s=300\) keV, \(\Delta m=1\) MeV;
- black: \(m_s=360\) keV, \(\Delta m=1\) MeV;
- blue: \(m_s=300\) keV, \(\Delta m=10\) MeV.

All use \(m_{\chi_1}=1\) TeV, \(m_V=10\) GeV, reference coupling-product squared \(10^{-8}\), \(g_2=1\), and the truncated SHM.

## 3. Event-weighting method

For each benchmark, strange-current scenario, nuclear scenario, and response family, the B-corrected differential rate is linearly interpolated at each generated true recoil energy \(E_j\). In a true-energy bin \(b\), the event weight is
\[
w_j^{(r)}=
R_b\,
\frac{(dR_B/dE_R)(E_j)}
{\sum_{k\in(b,r)}(dR_B/dE_R)(E_k)},
\]
where \(R_b\) is the exact piecewise-linear integral of the B spectrum over the bin and \(r\) labels the response replica. The pooled estimator uses the combined denominator from both replicas, so the pooled events integrate to one copy of \(R_b\), not twice the rate.

The observable map uses \(10\) phd bins in \(S1_c\) and \(0.02\)-dex bins in \(\log_{10}S2_c\). Two acceptance modes are kept separate:

1. **NEST level:** S1 coincidence and NEST S2-threshold flags.
2. **NEST + WS observable ROI:** \(3\leq S1_c\leq600\) phd, raw \(S2>645\) phd, and \(2.75\leq\log_{10}S2_c\leq4.15\).

The published final Fig. S2 efficiency-weighted event count is read from the separate PR #87 rate-level output. It is not multiplied into either NEST map. The ratio between the NEST/WS-ROI yield and the Fig. S2 count is reported only as a selection-stage diagnostic.

## 4. Numerical closure and output coverage

The local calculation produced:

| Output | Rows |
|---|---:|
| Benchmark / strange input / nuclear scenario / response family / acceptance comparisons | 192 |
| Per-energy-bin response diagnostics | 25,440 |
| Nonzero 2D signal cells | 120,000 |
| Split-replica stability checks | 192 |

The maximum closure residual between the event-weighted raw spectrum integral and the independent PR #87 Fig. S2 rate-level raw integral is
\[
\boxed{\delta_{\rm raw}^{\max}=7.77\times10^{-16}.}
\]
This is floating-point closure of the same piecewise-linear rate integral.

The maximum split-replica accepted-rate difference is \(0.4144\%\), and the maximum split-replica 2D total-variation distance is \(3.8592\%\). These are within-stream split diagnostics from the existing two-replica sample, not independent-seed confidence intervals or a formal equivalence test.

The raw response samples do contain NEST-level failures: 1,095 (EFT2024), 1,276 (Table S5), 1,805 (WS2024), and 1,356 (generic) events fail at least one of the S1-coincidence/S2-threshold flags. Every such failure lies in the first 11 true-energy strata, 5.4--16.4 keV. All four B spectra have zero support there: their first nonzero AFH-7 recoil points are 35 keV (red), 101 keV (green), 210 keV (black), and 101 keV (blue). Therefore the B-weighted NEST-level acceptance is exactly 100% on the physical support of these four benchmarks. The WS observable ROI supplies the additional event rejection shown below.

## 5. Primary AFH-7 event yields

The following table uses the Sufian 2017 unit-strange-current central input. All counts correspond to the \(2.84\) tonne-year exposure (\(1{,}037{,}310\) kg-day).

The Fig. S2 column is the separate published-efficiency rate-level result. NEST and NEST+WS-ROI columns are event-weighted NEST proxy folds; the Fig. S2 efficiency is not applied again.

| Benchmark | Fig. S2 rate-level | NEST level | EFT2024 + WS ROI | Table S5 + WS ROI | WS2024 + WS ROI | Generic + WS ROI |
|---|---:|---:|---:|---:|---:|---:|
| red, 200 keV / 1 MeV | \(2.66263\times10^{-1}\) | \(2.78634\times10^{-1}\) | \(2.78219\times10^{-1}\) | \(2.78564\times10^{-1}\) | \(2.78234\times10^{-1}\) | \(2.73499\times10^{-1}\) |
| green, 300 keV / 1 MeV | \(1.10267\times10^{-3}\) | \(1.15481\times10^{-3}\) | \(1.14731\times10^{-3}\) | \(1.15347\times10^{-3}\) | \(1.14836\times10^{-3}\) | \(1.08130\times10^{-3}\) |
| black, 360 keV / 1 MeV | \(2.07413\times10^{-9}\) | \(2.68005\times10^{-9}\) | \(2.00636\times10^{-9}\) | \(2.43781\times10^{-9}\) | \(2.36929\times10^{-9}\) | \(1.26028\times10^{-9}\) |
| blue, 300 keV / 10 MeV | \(9.02734\times10^{-6}\) | \(9.45413\times10^{-6}\) | \(9.39303\times10^{-6}\) | \(9.44318\times10^{-6}\) | \(9.40153\times10^{-6}\) | \(8.85471\times10^{-6}\) |

The WS-ROI-to-Fig.-S2 ratios for the same central input are:

| Benchmark | EFT2024 | Table S5 | WS2024 | Generic |
|---|---:|---:|---:|---:|
| red | 1.0449 | 1.0462 | 1.0450 | 1.0272 |
| green | 1.0405 | 1.0461 | 1.0414 | 0.9806 |
| black | 0.9673 | 1.1753 | 1.1423 | 0.6076 |
| blue | 1.0405 | 1.0461 | 1.0415 | 0.9809 |

The black \(m_s=360\) keV benchmark is distinctly response-model sensitive: its Sufian AFH-7 WS-ROI yield ranges from \(1.2603\times10^{-9}\) (generic) to \(2.4378\times10^{-9}\) (Table S5), a 93.4% max/min spread. The corresponding response-family spreads are much smaller for red (1.85%), green (6.67%), and blue (6.65%). The black spectrum places a much larger fraction of its weight near the upper recoil boundary, where the S1/S2 response models differ most.

For a fixed NEST response family, changing among the three strange-current inputs changes the AFH-7 WS-ROI yield by at most about 1.28% in these four benchmarks. The detector-response family is the dominant uncertainty in the black high-tail benchmark, not the strange-current scenario.

## 6. Interpretation

- The B form-factor correction is applied with the formal impulse transfer \(t_N=t_A=-2m_AE_R\). The historical PR85 \(t_N=-Q_A^2\) diagnostic is rejected by the metadata gate.
- AFH-7 is the primary result. Hybrid-9 is a separate fallback diagnostic; it is not relabelled as a complete AFH calculation.
- The NEST-level 100% acceptance is a property of the current generated sample and its simplified S1-coincidence/S2-threshold flags. It is not the complete LZ trigger or analysis efficiency.
- The WS-ROI map is an observable-space proxy. It does not include the official trigger, single-scatter reconstruction, analysis cuts, fiducial-volume mask, Skin/OD veto, or the collaboration's waveform-level S1 response.
- The Fig. S2 final efficiency and the NEST/WS-ROI response are different selection descriptions. Their ratio is a closure/plausibility diagnostic, not a universal correction factor. The black benchmark's response-family dependence explicitly rules out applying one scalar residual efficiency to every benchmark.
- The maps contain NEST stochastic quanta and detector fluctuations. No extra Gaussian recoil-energy smearing is applied on top of those observables.
- The rate-level Fig. S2 expected counts and the NEST 2D intensities are not a background-subtracted signal likelihood and do not constitute an LZ exclusion.

## 7. Reproduction

The repository workflow downloads the immutable NEST and formal-B source artifacts, runs the regression tests, performs all 192 folds, verifies the exact raw-rate closure, and uploads the native CSV/JSON outputs with SHA-256 checksums:

- Workflow: .github/workflows/lz-2026-B-baseline-nest-fold.yml
- Implementation: research/lz_detector_response/fold_lz_2026_three_body_B_event_weighted_response.py
- Vectorized repeated-spectrum kernel: research/lz_detector_response/fold_lz_2026_three_body_B_event_weighted_kernel.py
- Event reader: research/lz_detector_response/fold_lz_2026_three_body_event_weighted_response.py
- Tests: research/lz_detector_response/tests/test_lz_2026_B_event_weighted_fold.py

The output artifact contains the 2D intensity, fold comparison, per-bin acceptance, replica stability, summary, run manifest, and SHA256SUMS files. The numerical values above were first computed locally from the exact two source artifacts. GitHub Actions is the independent reproducibility check.


The complete local rerun used the pinned 1.06-million-event sample for each of the four NEST response families and the vectorized B-specific kernel. It reproduced all 192 comparisons, 25,440 per-bin diagnostics, and 120,000 nonzero 2D cells. The maximum raw-rate closure residual is (7.77\times10^{-16}); the maximum split-replica accepted-rate difference is (0.4144\%), and the maximum split-replica 2D TV distance is (3.8592\%). All seven local output files pass SHA256SUMS. The three new regression tests cover formal-B column selection, transfer provenance, and event-weight normalization; two additional guards test zero-rate strata and reject positive-rate bins with zero sampled support.


## 8. Independent GitHub reproduction: PASS

The corrected workflow [44680838189](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44680838189) completed successfully after fixing the downloaded-artifact root path and adding the pinned NumPy 2.3.5 dependency.

- Five regression tests passed, including the zero-rate and zero-sampled-support guards.
- The full fold completed for all 192 comparisons, 25,440 energy-bin rows, 192 replica checks, and 120,000 nonzero 2D cells.
- Maximum raw-rate closure residual: (7.771561172376096\times10^{-16}).
- All seven files in the GitHub output artifact passed SHA256SUMS verification.
- GitHub artifact: ID 14603649214, `lz-2026-formal-B-baseline-nest-fold`, SHA-256 `ff078d772a212a8bb25c8e61b99732e94f0983798659124b7027f5a0b6a310aa`.

I downloaded the GitHub artifact and compared it with the local 4.24-million-event fold. The four CSV tables have identical dimensions and every numeric field is exactly equal; the summary JSON is also identical. This establishes bit-for-bit numerical agreement for the archived fold outputs.

The two vector figures are archived in [B_BASELINE_RECOIL_FIGURES.md](B_BASELINE_RECOIL_FIGURES.md), with their normalization and selection conventions documented.
