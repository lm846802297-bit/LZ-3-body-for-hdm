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


### 6.1 Conditional residual-selection factorization diagnostic

To make the no-double-counting logic quantitative, define the rate-integrated
factors

\[
\epsilon_{\rm NEST} =
\frac{R_{\rm NEST}}{R_{\rm raw}},
\qquad
\epsilon_{\rm ROI|NEST} =
\frac{R_{\rm NEST+WS\,ROI}}{R_{\rm NEST}},
\]

and extract the remaining one-dimensional SS/data-analysis factor from the
nested Fig. S2 cumulative curves,

\[
\epsilon_{\rm SS+DA|preROI}^{\rm Fig.S2}
=
\frac{R_{\rm green}}{R_{\rm orange}}.
\]

A deliberately factorized rate-level diagnostic is then

\[
\epsilon_{\rm factored}
=
\epsilon_{\rm NEST}\,
\epsilon_{\rm ROI|NEST}\,
\epsilon_{\rm SS+DA|preROI}^{\rm Fig.S2}.
\]

It is compared with the independently integrated Fig. S2 final cumulative
efficiency. The table below uses EFT2024 and GCN; the factors are computed
from the event-weighted response fold and the eight-row Fig. S2 stage closure.

| Benchmark | NEST acceptance | WS ROI given NEST | Fig. S2 SS+DA given pre-ROI | Factorized efficiency | Fig. S2 final efficiency | Factorized / Fig. S2 |
|---|---:|---:|---:|---:|---:|---:|
| Red, \(m_s=200\) keV | 100.0000% | 99.8196% | 95.5780% | 95.4055% | 95.5557% | 0.99843 |
| Green, \(m_s=300\) keV | 100.0000% | 99.2794% | 95.5783% | 94.8896% | 95.4728% | 0.99389 |
| Black, \(m_s=360\) keV | 100.0000% | 74.0612% | 95.5790% | 70.7870% | 76.6301% | 0.92375 |
| Blue, \(m_s=300\) keV, \(\Delta m=10\) MeV | 100.0000% | 99.2835% | 95.5783% | 94.8935% | 95.4736% | 0.99392 |

For red, green, and blue, this factorized rate-level diagnostic is within
about 0.2--0.6% relative to Fig. S2. For the black high-energy benchmark it
is about 7.6% low. In that benchmark, the NEST-derived WS-ROI conditional
acceptance is 74.06%, whereas the Fig. S2 ROI conditional factor is about
80.17%. The mismatch is concentrated in the upper-S1c/high-energy region.

This is **not** a validated correction and must not be applied as a global
scale factor to the 2D PDF. Fig. S2 supplies only an energy-dependent
cumulative efficiency, not
\(P({\rm SS+DA}\mid E_R,S1_c,\log_{10}S2_c,x,y,z)\). The factorized
calculation tests whether a simple residual efficiency would close the
integrated rate; it does not establish the required 2D conditional kernel.
The black-benchmark discrepancy also depends strongly on the public NEST
response family, so it cannot be assigned uniquely to SS/data-analysis
correlations with the current inputs.

**Consequence:** do not multiply the Fig. S2 black cumulative curve into
the current WS-ROI map, and do not yet multiply the 95.58% residual factor
into that map as though it were an exact 2D selection model. Retain the
Fig. S2 result as the independent 1D selected-count benchmark and the
NEST+WS-ROI result as an intermediate 2D response. A calibrated conditional
response or official event-level selection model is still required.



### 6.2 Independent-seed EFT2024 black-tail check

The original single-stream 0.5-keV/1-keV black-tail comparison gave a
0.45--0.47% rate difference and about 1.9% 2D TV. Three independent full
productions per grid were subsequently generated, with 10,000 events per
energy stratum per seed over 225.4--269.9 keV. The 1-keV seeds were
20261120/20261122/20261124; the 0.5-keV seeds were
20261121/20261123/20261125.

| Nuclear response | Relative WS-ROI rate difference of seed means | Difference / combined seed SEM | TV between mean 2D maps |
|---|---:|---:|---:|
| GCN | 0.01758% | 0.171 | 0.6865% |
| JJ55 | 0.01862% | 0.186 | 0.6803% |

Including the NEST-only mode, the maximum rate difference is 0.01862% and
the maximum TV between mean maps is 0.8489%. Thus the independent-seed
mean-map comparison passes the 1.0% / 1.0% local-tail gate. The earlier
0.45--0.47% rate difference is not reproduced and is consistent with
finite-MC fluctuations in the original sample.

This comparison uses three independent seeds per grid. The ratio to the
combined seed SEM is a descriptive stability statistic, not a calibrated
hypothesis-test significance. Individual seed-pair TV fluctuations remain
above 1% in some comparisons; this does not provide a complete
cell-by-cell covariance matrix. See [the full grid and selection audit](LZ_2026_THREE_BODY_RESPONSE_SELECTION_AUDIT.md#153-independent-seed-high-energy-tail-validation-2026-11-15)
and [gated run 43691733080](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43691733080), artifact 14151869654 (SHA-256 `837a0385cac4c784abef38a5d4efc4273fc92ba01ddfcfab9123c90baecf2543`). Its local-tail gate passes the 1.0% / 1.0% point-estimate criteria.



### 6.3 Fig. S2 residual-stage bridge for both NR mean-yield families

The event-weighted 2D fold and the extracted Fig. S2 conditional stages were
joined for both EFT2024 and the Table S5-mean/EFT2024-width hybrid. Each
family has eight matched rows (four benchmarks × GCN/JJ55). The largest
absolute rate-level factorisation mismatch is:

| Response family | Maximum absolute mismatch | Worst benchmark | Worst nuclear response |
|---|---:|---|---|
| EFT2024 | 7.6250% | black, \(m_s=360\) keV | GCN |
| Table S5 hybrid | 13.0272% | black, \(m_s=360\) keV | GCN |

For the black GCN point, the detailed factors are:

| Quantity | EFT2024 | Table S5 hybrid |
|---|---:|---:|
| NEST-only acceptance | 100.00% | 100.00% |
| WS ROI conditional acceptance | 74.0612% | 90.6191% |
| Fig. S2 SS+DA conditional efficiency | 95.5790% | 95.5790% |
| Fig. S2 ROI conditional efficiency | 80.1746% | 80.1746% |
| Fig. S2 final cumulative efficiency | 76.6301% | 76.6301% |
| NEST ROI × residual SS+DA factor | 70.7870% | 86.6128% |
| Factorised / Fig. S2 final − 1 | −7.6250% | +13.0272% |

The JJ55 black point gives −7.5937% (EFT2024) and +12.7022% (Table S5
hybrid). For the red/green/blue benchmarks the factorisation mismatch is
below about 0.63% in EFT2024 and below 0.03% in the Table S5 hybrid.

This establishes that the black high-energy ROI acceptance is strongly
response-family dependent. The same Fig. S2 residual SS+DA factor cannot
close both hypotheses: it underpredicts the final cumulative efficiency
for EFT2024 and overpredicts it for the Table S5 hybrid. Do not choose a
single scalar efficiency to reconcile these differences, and do not apply
the full Fig. S2 cumulative curve to the 2D map. The bridge is a
rate-level diagnostic only; the missing conditional 2D migration kernel,
official FV, and Skin/OD selections remain unmodelled.

The paired-family event-weighted fold and bridge are in [run 43697104437](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43697104437),
artifact 14155360851, ZIP SHA-256
682e2ba71063d6ef835b37a6d328a84ab7c609f404856aa83d56e4b875794bab.
The artifact was downloaded and the two bridge JSON summaries were
independently inspected.


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
2. Apply the approved 1.0% accepted-rate / 1.0% 2D-TV engineering gate. The deterministic 5-keV reaggregation passes its point-estimate gate and 10 keV fails, but the independent full-range 1/5-keV productions fail the 2D-TV gate for both EFT2024 (1.4812%) and Table S5 (1.4681%), despite passing the accepted-rate gate. Keep 1 keV as the numerical reference; do not promote 5 keV as the production grid. The independent 0.5/1-keV black-tail mean-map check passes locally, but it is a separate high-energy refinement and does not validate the full-range 5-keV grid.
3. Keep 0.5 keV as a targeted high-energy refinement only; the independent-seed mean comparison passes the local 1.0% / 1.0% gate, but it is not a full-range 0.5-keV production.
4. Resolve the response-family / Fig. S2 rate-level closure using the official calibration-source spectrum and geometry, production NEST configuration, and position-correction model.
5. Implement or obtain the missing trigger, SS, data-quality, FV, veto, and live-time response/selection information.
6. Do not start the final profile likelihood until the response provenance and complete selection model are resolved.

## 9. Reproduction references

- [LZ 2026 three-body response-grid workflow](../../../.github/workflows/lz-2026-three-body-response-grid-convergence.yml)
- [Event-weighted fold implementation](../fold_lz_2026_three_body_event_weighted_response.py)
- [Event-weighted fold tests](../tests/test_lz_2026_three_body_event_weighted_fold.py)
- [1/5/10-keV convergence implementation](../converge_lz_2026_three_body_energy_grid.py)
- [0.5/1-keV high-energy comparison](../compare_lz_2026_nr_high_energy_half_kev.py)
- [Independent-seed black-tail audit](../audit_lz_2026_black_tail_independent_seeds.py)
- [Independent-seed workflow](../../../.github/workflows/lz-2026-black-tail-independent-seeds.yml)
- [Full response and selection audit](LZ_2026_THREE_BODY_RESPONSE_SELECTION_AUDIT.md)
- [Rate-level Fig. S2 event-yield table](rate_level_event_yields/lz_2026_rate_level_event_yields.csv)
