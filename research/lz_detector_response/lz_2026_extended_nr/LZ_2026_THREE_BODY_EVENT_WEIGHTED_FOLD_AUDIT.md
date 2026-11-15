# LZ 2026 event-level differential-rate weighted three-body response fold

Date: 2026-11-15

**Status:** numerical weighting and raw-rate closure validated; detector/selection model remains intermediate and no formal grid PASS is assigned.

## 1. Purpose

The 1-keV stratified NEST response samples are generated uniformly in true recoil energy within each 1-keV stratum. The physical three-body spectrum is not flat within those strata. This audit therefore applies the exact benchmark-specific differential rate event by event before constructing the two-dimensional observable-space intensity.

The workflow uses the pinned public NEST source commit `541b6430dae6ea289cf110c99f174a9187f7fdee`, four response families (EFT2024, rounded Table S5, WS2024, and generic), two nuclear responses (GCN and JJ55), four three-body benchmarks, and two acceptance definitions (`nest` and `ws_roi`). This gives 64 matched comparisons.

## 2. Event weighting and exact normalization

For each 1-keV response stratum \(b=[E_b^-,E_b^+]\), the exact piecewise-linear spectrum integral is

\[
R_b=\int_{E_b^-}^{E_b^+}r(E)\,dE,
\qquad r(E)=\frac{dR}{dE_R}.
\]

The response events are sampled uniformly in true energy within the stratum. For event \(j\), the code evaluates the piecewise-linear spectrum at the event energy and assigns the normalized weight

\[
w_{bj}=R_b\,
\frac{r(E_{bj})}{\sum_{k\in b}r(E_{bk})}.
\]

The weights are normalized independently within each energy stratum and each of the two disjoint response replicas. Consequently, the event weights sum to the exact rate integral \(R_b\) in every populated stratum and replica. The pooled two-replica result is formed from the combined event weights, not by averaging already-normalized replica histograms.

The two-dimensional observable intensity is

\[
I_{ab}=\sum_j w_j\,
\mathbf{1}\!\left[(S1_c,\log_{10}S2_c)_j\in \text{cell}_{ab}\right]
\mathbf{1}(\text{acceptance}_j).
\]

The sum over all populated cells must equal the accepted event-weighted rate. The code checks this closure and separately compares the total raw spectrum integral with the rate-level yield input.

## 3. Numerical closure and comparison with the 1-keV binned fold

Latest workflow:
- [GitHub Actions run 43676553810](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43676553810), conclusion: success.
- Commit: `825e55910a1e12b9842f4ced1a8aaf612425d005`.
- Artifact ID: `14146333000`.
- Artifact ZIP SHA-256: `3af588a74576db65462545ff305d453b63febaa701d3cf42762e8edb91e7b7d7`.
- Artifact size: 437,589,152 bytes; 28 files.

A subsequent documentation-triggered rerun on the final selection-audit revision
also completed successfully:
- [GitHub Actions run 43680164807](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43680164807).
- Artifact ID: `14147354124`.
- ZIP SHA-256: `0f2bf102f440245d98a10462a42fa9625b26e28124e7e2096b3ca8dfa90533b2`.
- The 64 event-weighted comparisons and all convergence diagnostics are
  numerically identical to the earlier successful run; the rerun does not
  constitute an independent response-MC production.
- The workflow builds the pinned NEST source, generates the full 1-keV response and the dedicated 0.5-keV tail samples, runs the 1/5/10-keV folds, performs the event-weighted fold, checks raw-rate closure, and archives the outputs.

Across all 64 comparisons:
- Maximum raw-rate closure relative difference: \(1.11\times10^{-15}\).
- Maximum event-weighted versus 1-keV binned accepted-rate difference: \(2.8206\times10^{-4}\), or 0.02821%.
- Maximum event-weighted versus 1-keV binned 2D total-variation distance: \(7.9197\times10^{-4}\), or 0.07920%.
- Maximum disjoint-replica accepted-rate difference: 0.4381%.
- Maximum disjoint-replica 2D total-variation distance: 3.9654%.

Thus, for the tested response samples, applying the physical \(dR/dE_R\) event weights changes the accepted rate and 2D shape only slightly relative to the existing 1-keV binned fold. The largest weighted-fold versus binned-fold differences are below the corresponding observed split-sample Monte Carlo variations. This is a numerical folding consistency result; it is not a detector-model validation or a formal convergence PASS.

## 4. 1/5/10-keV response-grid comparison

The same artifact records 192 comparisons (four benchmarks, two nuclear responses, four response families, two acceptance modes, and three grid widths). Relative to the 1-keV reference:

| Response grid | Maximum accepted-rate difference | Maximum 2D total-variation distance |
|---|---:|---:|
| 5 keV | 0.5131% | 0.8896% |
| 10 keV | 1.2146% | 2.4649% |

The maximum 5-keV rate and shape differences occur in the `ws_roi` mode. In `nest` mode, the accepted rates are unchanged at floating-point precision for the signal-support region because the tested benchmark spectra begin above the energies at which the NEST S1-coincidence efficiency is less than unity. The 1-keV reference remains the default. The 5-keV and 10-keV values are diagnostics, not accepted production grids.

The grid summary records the maximum 1-keV split-sample rate difference as 0.4469% and the maximum split-sample 2D TV distance as 3.9611%. The 5-keV maximum rate difference is comparable to this rate variation, while its maximum 2D shape difference is well below the split-sample TV variation. The 10-keV rate difference is larger. These comparisons should not be converted into a formal pass/fail without a pre-registered tolerance and a treatment of the MC covariance.

## 5. Dedicated 0.5-keV high-energy refinement

The 0.5-keV response sample covers 225.4–269.9 keV, where the \(m_s=360\) keV benchmark approaches the upper S1c boundary. It uses 4,000 generated events per 0.5-keV stratum, divided into two disjoint 2,000-event halves. The matched 1-keV comparison uses 4,000 events per 1-keV stratum, also split into two halves.

Across 64 matched comparisons:
- Maximum 0.5-keV versus 1-keV accepted-rate difference: 0.46895%.
- Maximum 2D total-variation distance: 2.5446%.
- No 2D shape difference exceeds both corresponding split-sample TV checks.
- Two accepted-rate differences exceed both corresponding split-sample rate checks after applying the \(10^{-12}\) absolute numerical tolerance. They are the EFT2024 black benchmark for GCN and JJ55, with rate differences 0.46895% and 0.45331%, respectively.

The two 0.5-keV tail halves are disjoint halves of the same seeded streams, not independently seeded full productions. The 0.5-keV shape differences are below the observed split-sample variation, but the two EFT2024 black-benchmark rate differences remain moderately above it. Retain 0.5 keV as a high-energy refinement diagnostic; it does not replace the 1-keV full-range reference or establish a formal convergence PASS.

## 6. Comparison with the rate-level Fig. S2 efficiency result

The workflow deliberately keeps the published final cumulative Fig. S2 efficiency in the separate rate-level yield. It does **not** multiply the scalar Fig. S2 efficiency into the `nest` or `ws_roi` two-dimensional intensity. This avoids double counting overlapping NEST and observable-space cuts and avoids inventing a two-dimensional migration kernel from a one-dimensional efficiency curve.

For bookkeeping, the workflow reports the ratio

\[
\frac{N_{\rm event\ weighted,\ NEST/WS\ ROI}}
{N_{\rm rate\ level,\ Fig.\ S2\ final\ efficiency}}.
\]

Across the 64 rows this ratio ranges from 0.6024 to 1.3050. For the EFT2024 family it is about 1.04 for the red, green, and blue benchmarks, but about 0.966 for the black benchmark. For the black benchmark it is about 1.183 for rounded Table S5, 1.150 for WS2024, and 0.602 for generic NEST.

The independent one-dimensional integration of each cumulative Fig. S2 stage against all eight benchmark spectra is documented in [LZ_2026_SELECTION_STAGE_RATE_LEVEL_CLOSURE.md](LZ_2026_SELECTION_STAGE_RATE_LEVEL_CLOSURE.md); it reproduces the archived rate-level yields to floating-point precision and quantifies the energy-weighted SS/data-analysis and ROI factors.

This ratio is a **model/provenance and selection-closure diagnostic only**. It is not an extra efficiency factor, not a correction to the 2D PDF, and not proof that one response family is the collaboration's production model. The response families use different public parameterizations; the event-level spatial prior is a uniform active-TPC cylinder rather than the official calibration-source/FV distribution; and the exact production configuration and position-correction model remain unconfirmed. The strong family dependence, especially for the high-energy black benchmark, is a reason to resolve the calibration/provenance mismatch before constructing a final selected PDF.

## 7. Acceptance definitions and missing selection stages

- `nest`: NEST Parametric S1 threefold PMT-occupancy acceptance and the configured NEST S2 threshold, with positive S1c/S2c observables.
- `ws_roi`: `nest` plus \(3\leq S1_c\leq600\) phd, raw \(S2>645\) phd, and \(2.75\leq\log_{10}S2_c\leq4.15\).

The Parametric S1 branch uses a PMT-occupancy approximation and does not explicitly apply the configured 150-ns coincidence window. A separate paired Parametric-versus-Full NEST S1 comparison found a maximum absolute acceptance difference of 0.25 percentage points; both modes passed all tested events in the four benchmark signal-support bins. This validates the approximation only within the tested NEST response and event samples.

The present two-dimensional response still does not implement:
1. the full hardware/DAQ trigger efficiency;
2. waveform-level S1 timing and the full detector pulse reconstruction;
3. single-scatter classification and S2 splitting/reconstruction;
4. all data-quality and analysis-selection cuts;
5. the depth- and azimuth-dependent official 4.71-tonne fiducial-volume mask and its position uncertainty;
6. prompt and delayed Skin/OD veto tagging and the corresponding likelihood sample partitions;
7. event-dependent live-time hold-offs.

No scalar cumulative efficiency should be multiplied into the existing 2D intensity until its overlap with these already-applied NEST/WS-ROI cuts is resolved and a two-dimensional response/migration treatment is available.

## 8. Required status and next work

1. Keep the 1-keV full-range response as the numerical reference.
2. Keep 5-keV as a sub-percent diagnostic and 10-keV as a coarser diagnostic; neither has a formal PASS because no scientific tolerance was pre-registered.
3. Keep the 0.5-keV tail sample as a targeted high-energy refinement; resolve the two EFT2024 black-benchmark rate comparisons with an independent higher-statistics production if the 0.5-keV rate is to be used.
4. Resolve the response-family / Fig. S2 rate-level closure using the official calibration-source spectrum and geometry, production NEST configuration, and position-correction model.
5. Implement or obtain the missing trigger, SS, data-quality, FV, veto, and live-time response/selection information.
6. Do not start the final profile likelihood until the response provenance and complete selection model are resolved.

## 9. Reproduction references

- [LZ 2026 three-body response-grid workflow](../../../.github/workflows/lz-2026-three-body-response-grid-convergence.yml)
- [Event-weighted fold implementation](../fold_lz_2026_three_body_event_weighted_response.py)
- [Event-weighted fold tests](../tests/test_lz_2026_three_body_event_weighted_fold.py)
- [1/5/10-keV convergence implementation](../converge_lz_2026_three_body_energy_grid.py)
- [0.5/1-keV high-energy comparison](../compare_lz_2026_nr_high_energy_half_kev.py)
- [Full response and selection audit](LZ_2026_THREE_BODY_RESPONSE_SELECTION_AUDIT.md)
- [Rate-level Fig. S2 event-yield table](rate_level_event_yields/lz_2026_rate_level_event_yields.csv)
