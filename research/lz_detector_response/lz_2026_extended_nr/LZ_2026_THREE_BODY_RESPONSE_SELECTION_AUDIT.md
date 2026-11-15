# LZ 2026 three-body NR response: selection audit and energy-grid convergence plan

Date: 2026-11-15  
Branch: `research/figure2-p0-4-mainline`  
NEST source pin: `541b6430dae6ea289cf110c99f174a9187f7fdee`

## 1. Corrected status of the existing 2D response

The earlier label "pre-selection signal prediction" was too broad. The existing event driver calls

\[
\texttt{FullCalculation(NR)}\to\texttt{GetS1(Parametric)}\to\texttt{GetS2(Full)}.
\]

At the pinned NEST source:

- `LZ_Detector_2024` sets `coinWind = 150 ns`, `coinLevel = 3`, and `numPMTs = 481`.
- `SetEFT2024Configuration()` changes `g1\), `g1_gas\), `s2_thr = 120 phe\), `eLife_us = 15000 us\), and the EFT2024 yield/width vectors. It does not overwrite the threefold-coincidence settings.
- In `GetS1()`, the Parametric mode estimates the S1 coincidence probability. When the coincidence draw fails, NEST makes the returned S1 observables negative to flag the failure.
- In `GetS2()`, if the uncorrected pulse area is below `abs(s2_thr)`, NEST makes the returned S2 observables negative.

The current fold filters on positive signed `s1c` and `s2c`. Thus the existing 2D intensity already includes the **NEST-parametric S1 threefold-coincidence acceptance** and the **NEST 120-phe S2 pulse threshold**. These are already applied and must not be multiplied in a second time.

Important qualification: NEST's Parametric S1 coincidence is an analytical PMT-occupancy approximation using the spike estimate, `coinLevel`, and `numPMTs`. The detector header also sets `coinWind = 150 ns`, but the Parametric branch does not explicitly apply that time window. It is therefore not a waveform-by-waveform reconstruction of the collaboration's three-PMT-in-time trigger.

Primary source files:
- [Pinned NEST GetS1/GetS2 implementation](https://github.com/NESTCollaboration/nest/blob/541b6430dae6ea289cf110c99f174a9187f7fdee/src/NEST.cpp)
- [Pinned LZ detector configuration](https://github.com/NESTCollaboration/nest/blob/541b6430dae6ea289cf110c99f174a9187f7fdee/include/Detectors/LZ_WS2024.hh)
- [Stratified response driver](../cpp/lz_2026_nr_stratified_energy_response.cc)
- [Three-body response fold](../fold_lz_2026_three_body_2d_response.py)

## 2. What is and is not included

| Response/selection item | Existing implementation | Status |
|---|---|---|
| NR mean quanta and fluctuations | NEST EFT2024 candidate | Included |
| S1 photon detection and SPE response | NEST GetS1 Parametric | Included |
| S1 threefold coincidence | NEST Parametric PMT-occupancy probability, level 3, 481 PMTs; no explicit 150-ns window in this branch | Included approximately, not full timing coincidence |
| NEST S2 pulse threshold | 120 phe in EFT2024 configuration | Included |
| Position-dependent S1/S2 response | Public NEST detector maps, uniform active-volume positions | Included as a proxy |
| DAQ trigger efficiency | Not simulated by the event driver | Missing |
| Analysis S1c range | 3--600 phd | Missing in the previous fold; applied as an explicit ROI mask in the convergence fold |
| Raw S2 ROI threshold | S2 > 645 phd | Missing in the previous fold; applied as an explicit ROI mask in the convergence fold |
| Corrected S2 ROI range | \(10^{2.75}<S2_c<10^{4.15}\) phd | Missing in the previous fold; applied as an explicit ROI mask in the convergence fold |
| Single-scatter reconstruction | No multi-pulse event reconstruction or S2-splitting model | Missing |
| Data-quality and accidental-rejection cuts | No pulse-shape or waveform-level analysis cuts | Missing |
| Fiducial-volume selection | Uniform active-TPC cylinder proxy, not the 4.71-t analysis FV map | Missing |
| Skin/OD prompt and delayed veto | No Skin/OD event simulation or veto tagging | Missing |
| Live-time hold-offs | Exposure is applied separately; event-dependent live-time exclusions are not simulated | Missing |
| Background PDFs and nuisance covariance | Not available in the response fold | Missing; no profile likelihood |

The LZ 2026 paper defines the WS ROI as \(3\leq S1_c\leq600\) phd, raw \(S2>645\) phd, and \(10^{2.75}\leq S2_c\leq10^{4.15}\) phd. It requires single scatters, all data/analysis selections, and the fiducial volume. The main-analysis fiducial mass is \(4.71\pm0.08\) tonnes. The current uniform active-volume prior is not a substitute for that depth- and azimuth-dependent FV.

The paper's veto partition is also separate from the NR response: prompt veto uses Skin \(>2.5\) phd within \(\pm0.25\,\mu s\) or OD \(>4.5\) phd within \(\pm0.3\,\mu s\) of TPC S1; delayed veto uses Skin/OD signals above 300/200 keV within 600 \(\mu s\), outside the prompt window. The likelihood fits science, prompt-veto, and delayed-veto samples simultaneously.

## 3. Reconstructed event-selection requirements inherited from WS2024

The 2026 paper states that its data/analysis selections are unchanged from the 4.2 tonne-year WS2024 analysis, except for the ROI, FV, and sideband handling. The WS2024 paper provides the following reconstruction details that are absent from the current NEST-only response driver:

- **DAQ trigger:** the digital filter is designed primarily for S2 pulses; the WS2024 trigger efficiency is 95% for S2 pulses corresponding to 3.5 extracted electrons.
- **S1 pulse classification:** a pulse is classified as S1 only if coincident photons are recorded in at least three PMTs. Undersized PMT responses and photon transit-time differences can cause missed S1s. The SS S1-identification efficiency is above 90% for all S1 pulse sizes and rises to 100% above 35 phd; it is calibrated by comparing automated reconstruction with manual event categorization of tritium and DD samples.
- **Single-scatter classification:** SS means one S1 preceding one S2. The SS efficiency depends on both S1 and S2 pulse classification. Electron diffusion can split S2 pulses; the splitting probability is below 1% on average for the relevant pulses, based on waveform simulations.
- **Accidental-rejection cuts:** pulse-shape selections reject accidental S1-S2 pairings. Their rejection power is 99.5% for known accidental events in the WIMP ROI, evaluated using unphysical-drift-time sidebands.
- **Live-time exclusions:** hold-offs follow large S2 signals and periods with elevated accidental rates. In WS2024, the cumulative exclusions leave 81.5% of collected live time, corresponding to 220.0 live days.
- **Fiducial volume:** the radial boundary is a depth- and azimuth-dependent contour, with additional drift-time and field-cage-resistor exclusions. The 2026 analysis uses \(4.71\pm0.08\) tonnes; a uniform active-cylinder prior is not the FV.
- **Veto samples:** the 2026 analysis separates science, prompt-veto, and delayed-veto samples. Prompt and delayed definitions are given in the main paper and must be modelled as sample partitions/tagging efficiencies, not as a single generic multiplicative loss.

These items make clear why the NEST sign flags are insufficient to claim full LZ S1/SS selection. The NEST Parametric occupancy model is a useful partial detector-response ingredient, but it does not replace pulse finding, timing coincidence, SS reconstruction, waveform-based accidental rejection, FV reconstruction, or live-time handling.

## 4. Cumulative efficiency curves in Supplemental Fig. S2

The published figure contains four cumulative curves:

1. Blue: Trigger.
2. Orange: Trigger + S1 Threshold.
3. Green: Trigger + S1 Threshold + SS & Data Analysis Cuts.
4. Black: all of the above + WS ROI in S1c/S2c.

The new extractor writes all four curves and the ratios of adjacent cumulative curves. These ratios are conditional stage factors only under the nesting represented by the figure; they are not independent detector efficiencies.

Vector-path digitization checks:

| NR energy | Trigger | + S1 threshold | + SS & analysis cuts | + WS ROI |
|---:|---:|---:|---:|---:|
| 5.4 keV | 1.000000 | 0.683993 | 0.615499 | 0.571765 |
| 248 keV | 1.000000 | 1.000000 | 0.955793 | 0.945688 |
| 269.9 keV | 1.000000 | 1.000000 | 0.955796 | 0.498820 |

At 248 keV, the conditional ratios are 1.000000 for the S1-threshold stage, 0.955793 for SS+analysis cuts, and 0.989427 for the ROI stage. At 5.4 keV, the corresponding ratios are 0.683993, 0.899862, and 0.928945.

The black curve is the final cumulative efficiency. It must not simply be multiplied into the current NEST-accepted 2D PDF without checking overlap: the NEST response already applies its own S1 coincidence and S2 threshold. The figure's cumulative curves are therefore used as an audit/validation target first. The energy-only curve also does not specify the selected two-dimensional migration kernel.

Extractor:
- `extract_lz_2026_nr_selection_efficiency_components.py`
- Output: `lz_2026_nr_selection_efficiency_components.csv` and metadata JSON.

## 5. 1/5/10-keV convergence definition

The new response driver stratifies the exact \(5.4\)--\(269.9\) keV interval into 1-keV true-energy strata, with a final 0.5-keV partial stratum. Each stratum has equal Monte Carlo statistics and two event replicas.

For a coarse bin \(B=[E_a,E_b]\), the response probability is reconstructed by width-averaging the fine-stratum probabilities:

\[
P_B(c)=\frac{1}{E_b-E_a}\sum_{j\subset B}\Delta E_j\,P_j(c).
\]

The three-body rate is integrated exactly for the piecewise-linear spectrum within the same coarse bin:

\[
R_B=\int_{E_a}^{E_b}dE\,\frac{dR_{3b}}{dE}.
\]

The folded cell intensity is

\[
I_c^{(\Delta E)}=\sum_B R_B P_B(c).
\]

The 1-keV grid is the reference; 5- and 10-keV results are compared using:
- relative difference in accepted integrated rate;
- total-variation distance between normalized 2D cell distributions;
- independent-replica rate and 2D-shape differences.

Two acceptance definitions are kept separate:
- `nest_level`: NEST S1-coincidence AND NEST S2-threshold pass.
- `nest_plus_ws_roi`: `nest_level` plus the published S1c, raw-S2, and S2c ROI conditions.

The second definition is still **not** the full LZ selection. It deliberately excludes trigger, SS reconstruction, analysis cuts, FV, and veto selections. The convergence outputs must not be labelled final selected signal PDFs.

## 6. No-profile-likelihood gate

Do not start the final profile likelihood until all of the following are resolved:

1. 1/5/10-keV response-grid convergence is numerically acceptable for both NEST-level and WS-ROI-masked distributions.
2. The NEST coincidence and S2-threshold overlap with the published cumulative efficiency curve is quantified; no stage is applied twice.
3. Trigger, SS reconstruction, and analysis-cut acceptance are either modelled in the response or included through a validated residual efficiency treatment.
4. The 4.71-t fiducial-volume acceptance and position dependence are represented, not replaced by the uniform active-volume proxy.
5. Skin/OD veto tagging and the science/prompt/delayed sample signal expectations are addressed.
6. The required background PDFs, rate constraints, and nuisance covariance are available or a clearly scoped non-official likelihood study is explicitly approved.

Until then, report rate-level and 2D response predictions with their exact acceptance definition and provenance; do not call them official LZ selected signal PDFs or exclusion limits.

## 7. Public-paper source anchors

- [LZ 2026 extended-NR paper, arXiv:2609.02823](https://arxiv.org/abs/2609.02823): SS/data-analysis/FV requirement and exact WS ROI; 4.71-t FV; prompt/delayed veto definitions; three-sample likelihood; Supplemental Fig. S2 cumulative efficiency.
- [LZ WS2024 4.2 tonne-year analysis, arXiv:2410.17036](https://arxiv.org/abs/2410.17036): S2 trigger efficiency, three-PMT S1 classification, SS reconstruction efficiency, S2 splitting, accidental pulse-shape cuts, FV geometry, veto and live-time exclusions.
- [LZ 4.2 tonne-year WS2024 analysis, arXiv:2410.17036](https://arxiv.org/abs/2410.17036): the 2026 paper identifies this as the starting analysis whose selections remain unchanged apart from ROI, FV, and sideband handling. The separate covariant EFT first-science-run paper is arXiv:2404.17666 and is not Ref. [5] in the 2026 paper.


## 8. Artifact-level numerical audit — 2026-11-14 response-grid run

The 1/5/10-keV workflow completed on commit
`5c0e3c254dbcf81f55a5af49be8e1e1f409ef294`:

- [GitHub Actions run 43648916347](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43648916347), conclusion: success.
- Artifact: `lz-2026-three-body-response-grid-convergence`, artifact ID `14135491602`.
- Downloaded archive SHA-256:
  `7ba7e268026f5607f0a4cfecbc1e910ec3c1ec808f727e8d42308b8fa00a96b6`.
- The archived `grid_convergence_summary.json` contains 192 grid comparisons and 64 1-keV replica comparisons.

A follow-up run after adding the explicit per-bin S1/S2 cutflow completed successfully:
- [GitHub Actions run 43656826463](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43656826463), head `fb6e40ec34bfc200aa212b3d731d9b60b8d9433e`.
- Updated artifact ID: `14137998811`.
- Artifact SHA-256: `e5005d73b57b86c05a5af9e999782df765fa6db870333320030863897a1ecdea`.

The updated `acceptance_by_energy_grid.csv` now stores the generated and passed counts separately for S1 coincidence, NEST S2 threshold, their joint pass, and the WS ROI. It also stores width-weighted per-bin acceptance factors and conditional ratios. The JSON now explicitly reports `formal_pass: null` and `DIAGNOSTIC_ONLY_NO_PREDECLARED_TOLERANCE`, so a green workflow cannot be mistaken for a scientific convergence certification.

A subsequent audit rerun after correcting the maximum 5-keV TV value completed successfully:
- [GitHub Actions run 43658526640](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43658526640), conclusion: success.
- Artifact ID: `14138704927`.
- Downloaded archive SHA-256: `bf8bc09f0b648eaf4dfccbe6b8fc6aad6536667e02264cf2fbd22f3c189071cd`.
- The archive contains 14 files, including four 1.06-million-event response CSVs, the 1/5/10-keV summary, the energy-resolved cutflow, and the 1-keV 2D intensity.
- Directly reading the archived JSON gives 192 grid comparisons and 64 split-sample comparisons. The maximum 5-keV TV distance is 0.8895571%; the maximum 5-keV relative accepted-rate difference is 0.5130969%. The corresponding 10-keV maxima are 2.464879% and 1.214624%.

The energy-resolved cutflow CSV initially omitted benchmark and nuclear-model identifiers even though its rate-integral columns varied with both. This was an output-provenance defect, not a response-calculation defect. It has been fixed and the workflow now validates the full key matrix and uniqueness. The corrected archive is:
- [GitHub Actions run 43674775899](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43674775899), successful.
- Artifact ID: `14145826957`.
- ZIP SHA-256: `68d2e837bbcaef82e03df49545c54735cac79c97413c860a52110e2b74f2a661`.
- The corrected `acceptance_by_energy_grid.csv` contains 33,120 rows and 21 columns, including benchmark and nuclear model; the seven-field provenance key has zero duplicates.

This rerun regenerated the same physical calculation with corrected audit metadata; it did not introduce a new response model or an independent coarse-grid Monte Carlo production. The summary still records `formal_pass: null` and `DIAGNOSTIC_ONLY_NO_PREDECLARED_TOLERANCE`.

### 8.1 What the run actually sampled

Each of the four response families (`eft2024`, `tableS5`, `ws2024`, `generic`) contains 1,060,000 events:
- 265 true-energy strata covering 5.4–269.9 keV;
- 4,000 generated events in every 1-keV stratum;
- two disjoint 2,000-event halves labelled replica 0 and 1;
- common true-energy and position design points across response families.

The 5-keV and 10-keV response probabilities are **not independent new MC runs**. They are reconstructed by width-averaging the same 1-keV stratum probabilities, then folding them against the exact piecewise-linear three-body rate integral in each coarse bin. This isolates the effect of response-energy binning while holding the underlying response MC fixed.

The two replica labels are disjoint halves of one seeded NEST random stream, not two separately seeded production runs. Their comparison is a useful split-sample stability diagnostic, not a full independent-seed covariance estimate.

### 8.2 Grid differences

The largest differences over all four response families, four particle benchmarks, two nuclear responses, and both acceptance modes are:

| Response grid | Maximum relative accepted-rate difference vs 1 keV | Maximum 2D total-variation distance vs 1 keV |
|---|---:|---:|
| 5 keV | 0.5131% | 0.8896% |
| 10 keV | 1.2146% | 2.4649% |

For the primary public EFT2024 candidate, the maxima across both acceptance modes are:
- 5 keV: 0.3249% in accepted rate and 0.4579% in 2D total variation;
- 10 keV: 0.8947% in accepted rate and 0.9535% in 2D total variation.

For every matched benchmark/nuclear-response/family/acceptance combination, both the 5-keV and 10-keV 2D TV differences are smaller than the corresponding 1-keV split-sample TV difference. The largest 1-keV split-sample TV difference is 3.9611% in the NEST-level mode and 3.3643% in the NEST-plus-WS-ROI mode. Thus the observed coarse-grid shape differences are not resolved above the within-grid split-sample shape fluctuation in this diagnostic.

The accepted-rate comparison is more restrictive. Comparing each coarse-grid relative rate difference with the corresponding 1-keV split-sample relative rate difference:
- 5-keV rate differences exceed the split-sample rate difference in 17 of 64 matched comparisons.
- 10-keV rate differences exceed it in 37 of 64 matched comparisons.
- The maximum split-sample accepted-rate difference in the WS-ROI mode is 0.4469%, while the largest coarse-grid rate differences are 0.5131% (5 keV) and 1.2146% (10 keV).

Interpretation:
- The 2D shape comparison alone would make 5- and 10-keV grids look adequate relative to the present split-sample noise, but it does not establish rate convergence.
- 5 keV has sub-percent maximum rate differences, yet 17/64 comparisons exceed the corresponding split-sample rate variation. It is not accepted as a production rate grid.
- 10 keV shows larger rate differences, with 37/64 comparisons exceeding split-sample variation; it is not accepted as a production rate grid.
- Keep 1 keV as the reference for both rate and 2D shape until a finer high-energy comparison and a pre-registered scientific tolerance are completed.
- The current workflow has no pre-registered scientific tolerance and does not fail when these metrics exceed a chosen threshold. Its green Actions status means the build, unit tests, numerical run, and artifact upload completed; it is **not** by itself a formal grid-convergence PASS.

### 8.3 Event-level S1 and S2 acceptance is present in the new artifact

This is a correction to the earlier compact-JSON audit in Sections 1 and 2. The older
`lz_nr_conditional_2d_pdf.json` pilot did not retain event-level coincidence and
threshold flags. The newer stratified CSVs do retain:

- true \(E_{\rm NR}\), true \(x,y,z\), field, and drift time;
- signed and absolute corrected \(S1_c\) and \(S2_c\);
- uncorrected S1 and S2 in phd;
- the NEST S1 spike-count field `s1.at(8)`;
- explicit sign-derived `s1_coincidence_pass` and `s2_threshold_pass` flags;
- photons and extracted electrons.

The new `signal_2d_intensity_1keV.csv` contains 62,224 observable-cell intensity rows, with two distinct modes:
- `nest`: NEST S1 Parametric coincidence pass AND NEST S2 threshold pass;
- `ws_roi`: the above plus \(3\leq S1_c\leq600\) phd, raw \(S2>645\) phd, and \(2.75\leq\log_{10}S2_c\leq4.15\).

The probabilities use \(N_{\rm cell}/N_{\rm generated}\); failed NEST-level events remain in the denominator. The `ws_roi` intensity is therefore an intermediate NEST-plus-WS-ROI signal prediction, not the full LZ selected signal PDF.

The event driver uses `GetS1(S1CalculationMode::Parametric)`. In the pinned NEST source, this mode samples a PMT-occupancy coincidence probability from the spike count, `coinLevel=3`, and `numPMTs=481`. Although the LZ detector header sets `coinWind=150 ns`, the Parametric branch does **not** explicitly apply that timing window. It is not a waveform-level reconstruction of three distinct PMTs within 150 ns. The saved `s1_spike_count` is the NEST spike-count input to this occupancy approximation, not a measured distinct-PMT multiplicity.

The event driver also passes the same \(x,y,z\) as both the true and smeared positions to NEST. Thus the position correction uses perfect reconstructed position in this run. The uniform active-cylinder spatial prior is not the 4.71-tonne FV map, and position-reconstruction smearing is not represented.

The energy-resolved event cutflow makes the low-energy S1 effect and high-energy ROI effect explicit:

| True-energy bin | Response family | S1 coincidence pass | NEST S2-threshold pass | Joint NEST pass | NEST + WS ROI pass |
|---|---|---:|---:|---:|---:|
| 5.4–6.4 keV | EFT2024 | 85.45% | 100.00% | 85.45% | 71.88% |
|  | Table S5 | 83.80% | 100.00% | 83.80% | 69.45% |
|  | WS2024 | 81.17% | 93.47% | 75.82% | 64.15% |
|  | Generic | 82.63% | 100.00% | 82.63% | 69.20% |
| 10.4–11.4 keV | EFT2024 | 99.72% | 100.00% | 99.72% | 99.40% |
|  | Table S5 | 99.65% | 100.00% | 99.65% | 99.10% |
|  | WS2024 | 99.62% | 100.00% | 99.62% | 99.08% |
|  | Generic | 99.65% | 100.00% | 99.65% | 99.28% |
| 247.4–248.4 keV | EFT2024 | 100.00% | 100.00% | 100.00% | 84.95% |
|  | Table S5 | 100.00% | 100.00% | 100.00% | 97.65% |
|  | WS2024 | 100.00% | 100.00% | 100.00% | 92.55% |
|  | Generic | 100.00% | 100.00% | 100.00% | 52.18% |

The first nonzero recoil-rate grid points are 35 keV (red), 101 keV (green), 210 keV (black), and 101 keV (blue), identically for GCN and JJ55. Thus none of the four benchmark spectra has support in the low-energy region where the NEST S1 coincidence acceptance is below unity. Consequently, the rate-weighted `nest` acceptance is 1.0 for these particular spectra, even though the detector response itself has substantial low-energy S1 losses. This is a property of the chosen signal spectra, not a general claim of unit S1 efficiency.

The NEST S2 threshold is response-family dependent: `SetEFT2024Configuration()` sets \(s2_{\rm thr}=120\) phe for the EFT2024, rounded-Table-S5, and generic-yield runs, while the unmodified WS2024 detector constructor sets \(s2_{\rm thr}=783\) phe. The published raw-S2 ROI condition is \(S2>645\) phd. With \(P_{\rm dphe}=0.214\), 645 phd corresponds to about \(645(1+0.214)=783.03\) phe, so the WS2024 detector threshold is effectively aligned with the raw-S2 ROI boundary; the EFT2024 120-phe threshold is looser. In the archived 4.24-million-event sample, no event with raw \(S2>645\) phd failed its configured NEST S2 threshold. Thus the NEST S2 threshold is redundant after the raw-S2 ROI cut for this sample; it must not be counted as a second independent efficiency loss.

### 8.4 The 2D ROI response does not yet reproduce the published cumulative efficiency

The vector-extracted black curve in Supplemental Fig. S2 is the published cumulative
\[
\text{trigger}+\text{S1 threshold}+\text{SS/data-analysis cuts}+\text{WS ROI}
\]
efficiency. The new `ws_roi` acceptance contains NEST Parametric S1 coincidence, the NEST S2 threshold, and the explicit S1c/raw-S2/S2c ROI. It does not contain trigger, SS reconstruction, data-analysis cuts, FV, or veto selections.

Representative comparisons are:

| True-energy location | Published Fig. S2 final cumulative efficiency | EFT2024 NEST+WS-ROI | Table S5 NEST+WS-ROI | WS2024 NEST+WS-ROI | Generic NEST+WS-ROI |
|---|---:|---:|---:|---:|---:|
| 5.4 keV (first 1-keV bin: 5.4–6.4) | 0.5718 | 0.7188 | 0.6945 | 0.6415 | 0.6920 |
| 248 keV (bin: 247.4–248.4) | 0.9457 | 0.8495 | 0.9765 | 0.9255 | 0.5218 |
| 269.9 keV (last bin: 269.4–269.9) | 0.4988 | 0.5555 | 0.8120 | 0.8135 | 0.2710 |

These are not identical selections or priors, so they are not a direct efficiency calibration. Nevertheless, the EFT2024 and generic NEST-plus-ROI acceptances falling **below** the published full cumulative efficiency near 248 keV is a non-closure diagnostic: a strict subset of the published selection should not have a lower acceptance if both were generated with the same response and nested definitions. The discrepancy cannot be repaired by multiplying a residual efficiency onto the current 2D map. It requires investigation of the exact LZ production NEST configuration, the spatial prior and position correction, and the response/ROI comparison.



A bin-by-bin monotonicity diagnostic was also made over the 265 unique 1-keV bins, comparing each model's `ws_roi` acceptance with the interpolated published black Fig. S2 cumulative efficiency at the bin centre:

| Response family | Bins where NEST+WS-ROI acceptance is below the published full cumulative efficiency | Worst deficit |
|---|---:|---:|
| EFT2024 | 33 / 265 | −13.93 percentage points at 252.9 keV |
| Table S5 | 0 / 265 | none; smallest positive margin +1.73 percentage points at 249.9 keV |
| WS2024 | 19 / 265 | −2.78 percentage points at 252.9 keV |
| Generic | 74 / 265 | −47.18 percentage points at 252.9 keV |

Under identical event definitions and spatial priors, a response that applies a subset of the final cuts should not have lower acceptance than the final cumulative curve. Table S5 is the only tested family that satisfies this necessary monotonicity condition in every bin. This makes the rounded Table-S5 response a more internally consistent candidate for the published selection curve than the public EFT2024 header in this particular comparison. It does **not** prove Table S5 is the exact production configuration: the published curve and this proxy still differ in spatial prior, position reconstruction, and unmodelled analysis cuts. The result is a strong provenance/calibration diagnostic, not permission to select a model solely by curve matching.

Do not treat the four NEST families as a statistical nuisance envelope. They are different response-model choices with distinct provenance.

### 8.5 High-energy sensitivity to the rounded Table S5 exponent

The EFT2024 and Table S5 response families use the same EFT2024 fluctuation vector and detector overrides; their principal difference is the mean-yield vector. In the pinned NEST code,
\[
N_q=NRYieldsParam[0]\,E_{\rm NR}^{NRYieldsParam[1]}+M_{\rm c}.
\]
The public EFT2024 header uses \(11.21\,E_{\rm NR}^{1.113}\), whereas the printed Table S5 values rounded to one decimal use \(11.2\,E_{\rm NR}^{1.1}\). At 248 keV,
\[
\frac{11.21\,248^{1.113}}{11.2\,248^{1.1}}
\simeq 1.075.
\]
This small-looking exponent rounding therefore changes the dominant quanta term by about 7.5% at the high-energy end.

The event sample confirms the effect in the corrected S1 distribution at 247.4–248.4 keV:
- EFT2024: mean \(S1_c=537.5\) phd, standard deviation 60.4 phd, WS-ROI acceptance 0.8495;
- rounded Table S5: mean \(S1_c=499.2\) phd, standard deviation 52.9 phd, WS-ROI acceptance 0.9765.

For these two families at that energy, raw S2 and the S2c interval pass all sampled events; the difference in total ROI acceptance is the upper \(S1_c\leq600\) phd boundary. This is a physical consequence of the high-energy yield parameterization, not MC noise. The rounded Table S5 vector must not be treated as numerically equivalent to the full-precision EFT2024 candidate at high recoil energy. Conversely, the public EFT2024 header remains a candidate configuration, not proven to be the exact LZ 2026 production build.

### 8.6 Intermediate expected counts

For the EFT2024 candidate and the 2.84 tonne-year exposure, the NEST-plus-WS-ROI intermediate counts are:

| Benchmark | GCN | JJ55 |
|---|---:|---:|
| red (\(m_s=200\) keV, \(\Delta m=1\) MeV) | 0.353059 | 0.361550 |
| green (\(m_s=300\) keV, \(\Delta m=1\) MeV) | \(1.5853\times10^{-3}\) | \(1.6420\times10^{-3}\) |
| black (\(m_s=360\) keV, \(\Delta m=1\) MeV) | \(2.7578\times10^{-9}\) | \(2.7846\times10^{-9}\) |
| blue (\(m_s=300\) keV, \(\Delta m=10\) MeV) | \(1.2978\times10^{-5}\) | \(1.3442\times10^{-5}\) |

These are before trigger, SS/data-analysis cuts, the official fiducial-volume mask, Skin/OD veto partition, live-time treatment, backgrounds, and likelihood. The black benchmark loses about 26% relative to its NEST-level rate after the explicit WS ROI, because its signal is concentrated near the high-energy S1c boundary. These counts are intermediate diagnostics only.

For the black benchmark, the response-family choice itself changes the NEST-plus-WS-ROI count substantially: GCN gives \(2.758\times10^{-9}\) events for EFT2024, \(3.374\times10^{-9}\) for Table S5 (+22.35%), \(3.280\times10^{-9}\) for WS2024 (+18.92%), and \(1.719\times10^{-9}\) for generic NEST (−37.67%). This is a response-model/provenance dependence, not MC statistical error. The other three benchmarks are much less sensitive to the response-family choice because their rate support lies away from the high-energy S1c/ROI boundary.





### 8.7 Half-keV high-energy response refinement

Because the \(m_s=360\) keV benchmark is concentrated near the upper recoil-energy boundary and its WS-ROI acceptance changes rapidly there, a dedicated 0.5-keV response sample was generated over the interval 225.4–269.9 keV. The lower edge is aligned to the existing 1-keV strata. The run uses 4,000 events in each 0.5-keV stratum (two disjoint 2,000-event halves) for each of EFT2024, rounded Table S5, WS2024, and generic NEST.

The high-energy refinement is also included in the latest combined response-grid and event-weighted artifact:
- [GitHub Actions run 43676553810](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43676553810), conclusion: success.
- Artifact ID: 14146333000.
- ZIP SHA-256: 3af588a74576db65462545ff305d453b63febaa701d3cf42762e8edb91e7b7d7.
- The 437,589,152-byte artifact contains the full 1-keV response samples, the 0.5-keV high-energy samples, the 1/5/10-keV fold, the event-weighted fold, and the high-energy comparison outputs.

Across 64 matched comparisons (four benchmarks, two nuclear responses, four response families, and two acceptance modes), the 0.5-keV versus 1-keV differences are:
- Maximum relative accepted-rate difference: 0.46895%.
- Maximum 2D total-variation distance: 2.5446%.
- 0/64 2D shape differences exceed both corresponding split-sample TV checks.
- 2/64 accepted-rate differences exceed both corresponding split-sample rate checks, after applying a \(10^{-12}\) absolute numerical tolerance to avoid counting floating-point roundoff.

The two rate comparisons above the split-sample checks are the EFT2024 black benchmark:
| Nuclear response | Acceptance mode | 0.5-keV vs 1-keV rate difference | Difference / largest split-sample rate variation |
|---|---|---:|---:|
| GCN | NEST + WS ROI | 0.46895% | 1.255 |
| JJ55 | NEST + WS ROI | 0.45331% | 1.247 |

The 0.5-keV sample has twice as many generated events per unit recoil energy as the 1-keV sample. The comparison is therefore a refinement check with unequal MC statistics, not a paired equal-statistics grid test. The 2D shape difference remains within the observed split-sample variation, while the two EFT2024 black-benchmark rate differences are only moderately above it.

**Conclusion:** the 0.5-keV tail sample improves the high-energy resolution check, but does not establish a formal convergence PASS. Keep the 1-keV full-range result as the reference, retain the 0.5-keV high-energy result as an independent refinement diagnostic, and do not promote either grid to a final likelihood until a rate tolerance and MC covariance treatment are pre-registered. A further independent high-statistics EFT2024 black-tail run would be the cleanest way to resolve the remaining ~0.45% rate difference.


## 9. Correct release status

The previous blanket label "pre-selection" should now be made more precise:

- The original 10-keV compact 2D pilot is a positive-observable conditional response-shape artifact.
- The newer 1-keV `nest` intensity includes NEST Parametric S1 coincidence and NEST S2-threshold acceptance.
- The newer 1-keV `ws_roi` intensity additionally applies the published S1c/raw-S2/S2c ROI.
- Neither new intensity includes the complete LZ trigger, waveform-level S1 timing, SS reconstruction, data-analysis cuts, official FV, veto sample assignment, or live-time treatment.

Accordingly, describe the current result as a **NEST-level / WS-ROI intermediate three-body signal prediction**, not as the final LZ post-selection signal PDF. Keep the 1-keV full-range response as the reference; the 0.5-keV high-energy tail sample is a refinement diagnostic, while 5-keV and 10-keV remain unaccepted as production rate grids. No grid has a formal convergence PASS because no tolerance was pre-registered. Do not start the final profile likelihood.




## 10. NEST release lineage and EFT2024 candidate status

The source-level audit is in
[LZ_2026_NEST_RELEASE_LINEAGE_AUDIT.md](LZ_2026_NEST_RELEASE_LINEAGE_AUDIT.md).
The public v2.4.5beta tag at commit 19bc9bc predates the two-component ER
recombination model and high-energy NR p(E) extension described in the 2026
LZ Supplemental Material. The relevant physics features and the public
SetEFT2024Configuration() were added later; the LZ-specific configuration
first appears in commit 307fb27, before the paper's 2026-09-02 submission.
The later audited commit 541b643 adds static getters/storage only relative to
307fb27, with no change to src/NEST.cpp or the physical vectors.

The EFT2024 detector candidate gives g1=0.1104 and a source-calculated
g2=34.5263 phd/electron, consistent with the paper's 0.110±0.002 and
34.5±1.1 values. This is a strong consistency check, not proof of the exact
collaboration build. Keep 541b643 pinned as the public candidate and retain
the rounded Table S5, literal Table S3 m6=0, WS2024, and generic NEST
alternatives explicitly. Do not select a production configuration solely
from the Fig. S2 monotonicity comparison.

## 11. Paired NEST Parametric-versus-Full S1 coincidence cross-check

Because the stratified three-body response uses `S1CalculationMode::Parametric`, a separate paired test was added against NEST `S1CalculationMode::Full`, which explicitly uses the configured PMT-level timing and coincidence logic.

Run and artifact:
- [GitHub Actions run 43658191416](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43658191416), conclusion: success.
- Artifact ID: `14138858617`.
- Artifact SHA-256: `4475a152732eae45c76b8dbf4e8c4c52a476c402e3870b3f16b2fc7cfd5bd408`.
- Pinned NEST: `541b6430dae6ea289cf110c99f174a9187f7fdee`.
- EFT2024 detector/yield candidate; 10,000 paired events in each of ten energy bins.

For each event, `FullCalculation(NR)` is run once. The same intrinsic quanta, recoil energy, and true position are then passed to Parametric and Full S1 modes, with separate deterministic S1 random streams. This isolates the S1 detector-response implementation from differences in the underlying NR quanta and event geometry.

| Energy bin (keV) | Parametric S1 pass | Full S1 pass | Full − Parametric | Paired 95% interval for difference |
|---|---:|---:|---:|---:|
| 5.4–6.4 | 86.27% | 86.02% | −0.25 percentage points | [−1.3375, +0.8168] pp |
| 10.4–11.4 | 99.77% | 99.70% | −0.07 percentage points | [−0.2938, +0.1197] pp |
| 15.4–16.4 | 99.99% | 99.99% | 0.00 percentage points | [−0.0723, +0.0723] pp |
| 20.4–21.4 | 100.00% | 100.00% | 0.00 percentage points | [−0.0502, +0.0502] pp |
| 30.4–31.4 | 100.00% | 100.00% | 0.00 percentage points | [−0.0502, +0.0502] pp |
| 35.0–36.0 | 100.00% | 100.00% | 0.00 percentage points | [−0.0502, +0.0502] pp |
| 101.0–102.0 | 100.00% | 100.00% | 0.00 percentage points | [−0.0502, +0.0502] pp |
| 210.0–211.0 | 100.00% | 100.00% | 0.00 percentage points | [−0.0502, +0.0502] pp |
| 247.4–248.4 | 100.00% | 100.00% | 0.00 percentage points | [−0.0502, +0.0502] pp |
| 269.4–269.9 | 100.00% | 100.00% | 0.00 percentage points | [−0.0502, +0.0502] pp |

The largest absolute efficiency difference is 0.25 percentage points; the largest absolute paired \(z\)-score is 0.98. The paired-difference intervals use a Bonferroni 95% joint Wilson rectangle built from two 97.5% marginal Wilson intervals: one for the discordance probability and one for the fraction of discordant events that pass Full mode. This avoids the misleading zero-width interval that a normal approximation would produce when no discordant events are observed. The paired (z)-score is undefined when a bin has no discordant pairs. At the signal-support energies of the four benchmarks (first nonzero recoil points 35, 101, 210, and 101 keV), both modes pass all 10,000 sampled events in the corresponding bins.

The S1c shapes are also close at the high-energy anchors:
- 247.4–248.4 keV: mean \(S1_c=538.27\) phd (Parametric) versus 539.60 phd (Full);
- 269.4–269.9 keV: mean \(S1_c=592.77\) phd (Parametric) versus 593.73 phd (Full).

This supports using the faster Parametric mode for the present benchmark spectra: the omission of explicit 150-ns timing in Parametric mode does not produce a statistically resolved S1-coincidence acceptance bias in the tested signal-support region. The low-energy differences are also consistent with the paired Monte Carlo uncertainty.

This is a **mode-to-mode NEST validation**, not a complete LZ waveform or analysis-selection validation. The Full S1 mode is not a complete detector waveform reconstruction, and the comparison does not add trigger, SS reconstruction, data-quality, official FV, Skin/OD veto, or live-time selections. No equivalence tolerance was pre-registered; this remains a diagnostic rather than a formal PASS.



## 12. Full-range NR band and NR fluctuation-vector audit

The full-range NR band proxy and source-level parameter audit are documented in
[LZ_2026_NR_FULL_BAND_PARAMETER_SENSITIVITY_AUDIT.md](LZ_2026_NR_FULL_BAND_PARAMETER_SENSITIVITY_AUDIT.md).
The study compares the public full-precision EFT2024 candidate, rounded
Table S5 mean yields, EFT2024 means with alternative NR fluctuation vectors,
WS2024, and generic NEST.

The source-level audit shows that the shared NEST NRERWidthsParam vector
contains NR quanta-fluctuation controls as well as ER controls. For NR,
indices 0–5, 11, and 12 are active. In particular, EFT2024 p2 = −0.707
implies lambda_Chen = 0.293 and a clamped-to-zero omega_NR, whereas WS2024
and generic p2 are positive and give lambda_Chen = 1 with nonzero omega_NR.
The width-isolation comparisons therefore probe a real change in the NR
recombination-variance model, not merely a small adjustment to a Gaussian
width.

The corrected event-local drift calculation and rounded Table S5 candidate
completed successfully. The pinned LZ detector header returns a constant
96.5 V/cm at every position, corresponding to 1.33036177945 mm/us. Thus the
initial detector-centre drift speed and the corrected local speed produce
bitwise-identical common event outputs for the current detector model. The
corrected CSVs nevertheless store per-event drift distance/time/speed, and
the summarizer verifies kinematic closure; the maximum relative residual is
1.08e−11.

The bootstrap-enabled result is [run 43661274708](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43661274708),
artifact 14139997390, SHA-256
1f053db6e3d49863c8b36b6a753d4e4eed0410a8530e73d98eb62d771f4bd967.
It contains 12 event CSVs, 90 pairwise band comparisons, and 2,000-replica
finite-MC bootstrap intervals. In the uniform-TPC sample, the candidate
offsets are −1.9545 sigma-equivalent (EFT2024), −2.3617 (rounded Table S5),
−1.6278 (EFT2024 means plus WS2024 NR fluctuations), −1.6506 (EFT2024 means
plus generic NR fluctuations), −4.9987 (WS2024), and −6.4110 (generic NEST).
These are percentile-width diagnostics, not likelihood significances.

This remains a flat true-energy prior and a uniform-TPC spatial proxy, not
the collaboration's D-D/AmBe calibration spectrum or source geometry. Do not
select an NR fluctuation vector by matching the candidate event; that would
be circular. The study is not a likelihood input and does not establish the
exact LZ 2026 production NEST configuration.


## 13. Event-level differential-rate weighted response fold

The event-level weighting method and complete result are documented in
[LZ_2026_THREE_BODY_EVENT_WEIGHTED_FOLD_AUDIT.md](LZ_2026_THREE_BODY_EVENT_WEIGHTED_FOLD_AUDIT.md).
The latest combined artifact is [run 43676553810](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43676553810),
artifact 14146333000, SHA-256
3af588a74576db65462545ff305d453b63febaa701d3cf42762e8edb91e7b7d7.

For each 1-keV response stratum, events are sampled uniformly in true recoil
energy and weighted by the benchmark-specific piecewise-linear \(dR/dE_R\).
The event weights in each stratum and replica are normalized to the exact
piecewise-linear rate integral of that stratum. Across 64 matched combinations,
the maximum raw-rate closure residual is \(1.11\times10^{-15}\), the largest
event-weighted versus 1-keV binned accepted-rate difference is 0.02821%, and
the largest 2D total-variation distance is 0.07920%. These differences are
below the observed disjoint-replica MC variations (maximum 0.4381% in rate
and 3.9654% in 2D TV).

This validates the event-level rate weighting and the numerical consistency
of the 1-keV binned fold for the generated samples. It does not establish a
formal response-grid PASS: the grid summary still records
`formal_pass: null` because no scientific tolerance was
pre-registered.

The event-weighted NEST/WS-ROI count divided by the separate rate-level
Fig. S2 final-efficiency count ranges from 0.6024 to 1.3050 across the
64 response/benchmark rows. This ratio is a selection/provenance diagnostic,
not an additional efficiency factor. Its strong response-family dependence,
especially for the high-energy black benchmark, means the public response
families cannot be treated as interchangeable and the exact production
configuration/calibration closure remains unresolved. Do not multiply the
Fig. S2 scalar efficiency into the existing 2D map.



## 14. Official 2026 selection hierarchy and three-sample likelihood closure

This section resolves an important naming ambiguity: the **NEST S2 pulse threshold is not the hardware/DAQ S2 trigger**. The two are different stages and must not be merged or double-counted.

### 14.1 Selection hierarchy inherited from WS2024

The 2026 extended-NR paper explicitly says that the data and analysis selections are unchanged from the WS2024 4.2-tonne-year analysis, except for the WS ROI, fiducial volume, and sideband handling. The public sources are [the 2026 extended-NR paper](https://arxiv.org/abs/2609.02823), especially its Data Analysis section and Supplemental Material, and [the WS2024 analysis](https://arxiv.org/abs/2410.17036), especially the detector/data-selection discussion.

| Stage | Official definition / published information | Current three-body fold |
|---|---|---|
| S2 DAQ trigger | Digital filter designed primarily for S2; WS2024 trigger efficiency is 95% for S2 pulses corresponding to 3.5 extracted electrons. The efficiency is energy-dependent and appears as the first cumulative curve in Fig. S2. | Missing. The NEST S2 pulse threshold is **not** this trigger. |
| S1 pulse classification | An S1 requires coincident photons in at least three PMTs. The SS S1-identification efficiency is above 90% for all S1 sizes and reaches 100% above 35 phd, based on tritium/DD manual-versus-automated classification. | NEST Parametric occupancy approximation is included; NEST Full timing comparison is a separate mode-to-mode check, not official waveform reconstruction. |
| Single-scatter reconstruction | One S1 preceding one S2. SS identification depends on S1 and S2 classification. Electron diffusion splits S2 pulses with probability below 1% on average for relevant pulses. | Missing. No pulse finding, multi-pulse reconstruction, or S2-splitting model. |
| S1/S2 data-analysis cuts | Pulse-shape and event-quality selections target accidental S1-S2 pairings. Their rejection power is 99.5% for known accidental events in the WIMP ROI, assessed using unphysical-drift-time sidebands. | Missing. The 99.5% rejection number is not a universal signal efficiency and must not be applied as a flat 0.5% signal factor. |
| Fiducial volume | 4.71 ± 0.08 tonnes. The radial boundary is a depth- and azimuth-dependent contour; it enforces 8.0 cm true-wall and 6.0 cm reconstructed-wall minimum stand-off. The contour's mean (maximum) distance from the true wall is 10.7 cm (18.2 cm); from the reconstructed wall it is 7.2 cm (10.4 cm). Upper/lower boundaries are 12.8 cm below the gate and 9.0 cm above the cathode. | Missing. Uniform active-TPC cylinder is only a generation prior. |
| WS ROI | \(3\leq S1_c\leq600\) phd, raw \(S2>645\) phd, and \(10^{2.75}\leq S2_c\leq10^{4.15}\) phd. | Included in the ws_roi mode. |
| Skin/OD veto | Prompt: Skin \(>2.5\) phd within ±0.25 μs or OD \(>4.5\) phd within ±0.3 μs of TPC S1. Delayed: Skin/OD energy above 300/200 keV within 600 μs of S1, outside prompt window. | Missing; no Skin/OD response or sample assignment. |
| Live-time exclusions | Hold-offs after large S2s and periods of elevated accidental rates. The WS2024 analysis retains 81.5% of collected live time, giving 220 live days. | Event-dependent hold-offs missing. The current 2.84 tonne-year exposure already corresponds to 4.71 tonnes × 220 live days; do **not** multiply by 81.5% again. |

The WS2024 paper reports a 95% S2 trigger efficiency at 3.5 extracted electrons and an S1 classification efficiency above 90% for all S1 sizes, reaching 100% above 35 phd. These are detector/selection efficiencies, not the same as the NEST s2_thr setting or a generic event-level S1 boolean. For the present high-energy benchmark spectra, the first nonzero recoil energies are 35, 101, 210, and 101 keV. The paired NEST Parametric-versus-Full test passes all sampled events in these signal-support bins, but this does not validate the hardware trigger, the event reconstruction, or the official signal-efficiency curve.

### 14.2 Three veto samples are part of the likelihood, not one extra cut

The 2026 analysis divides selected events into three samples:
1. **Science:** no qualifying Skin or OD veto signal.
2. **Prompt-veto:** Skin \(>2.5\) phd within ±0.25 μs of TPC S1, or OD \(>4.5\) phd within ±0.3 μs.
3. **Delayed-veto:** Skin \(>300\) keV or OD \(>200\) keV within 600 μs of TPC S1, but outside the prompt window.

The paper reports random coincidences with veto-detector activity that tag 0.01% of unrelated TPC signals as prompt-veto and 2.86% as delayed-veto. To a good approximation, signal and background components have the same \((S1_c,\log_{10}S2_c)\) shape in the three samples but different rates. The likelihood is a simultaneous unbinned extended likelihood over the three samples; their expected counts are correlated through tagging-efficiency parameters, not independent free normalizations.

Consequently, the current ws_roi intensity is not yet a complete likelihood signal model. It has no sample label and represents neither the full science-sample signal fraction nor the prompt/delayed signal leakage. A future model must assign sample-specific signal rates and preserve the correlations/constraints on the tagging efficiencies. It must not simply apply one generic veto-survival multiplier to the science-sample 2D map.

### 14.3 Distinguish the four S2/S1-related quantities

The following are separate and must remain separate in code and documentation:

- **S2 DAQ trigger:** hardware/digital-filter probability for an S2 pulse to trigger waveform acquisition.
- **NEST S2 threshold:** the NEST response-model pulse-size threshold used when generating a response event.
- **Raw-S2 WS ROI:** the analysis cut \(S2>645\) phd.
- **Corrected-S2 WS ROI:** the analysis cut \(10^{2.75}\leq S2_c\leq10^{4.15}\) phd.

Likewise, NEST's threefold PMT-occupancy approximation is not the same thing as the complete waveform-level S1 pulse classification and SS reconstruction. The current code's NEST pass flags and WS ROI therefore remain an intermediate response, not a complete event-selection chain.

### 14.4 Profile-likelihood blockers after the response-grid work

The remaining blockers are now explicit:

- [ ] Official production NEST build/configuration and calibration closure, including high-energy NR response.
- [ ] Calibration-source energy spectra and spatial deployment distributions for the NR band/response calibration.
- [ ] Position reconstruction and position-correction maps, including finite \((x,y,z)\) resolution and field-dependent effects.
- [ ] S2 trigger efficiency and its uncertainty/correlation with S1/SS reconstruction.
- [ ] Full SS reconstruction, pulse-quality/data-analysis cuts, and their energy-dependent NR acceptance/covariance.
- [ ] Exact 4.71-tonne FV contour or a validated equivalent spatial mask and reconstruction smearing.
- [ ] Skin/OD response and signal tagging fractions for science, prompt-veto, and delayed-veto samples.
- [ ] Event-dependent live-time exclusions and consistency with the already-used 220-live-day, 2.84-tonne-year exposure.
- [ ] Background PDFs, normalization constraints, tagging-efficiency constraints, and nuisance covariance needed for the simultaneous three-sample likelihood.

Until these inputs are resolved, keep the event-weighted two-dimensional map labelled **NEST-level / WS-ROI intermediate three-body signal prediction**. The 1-keV energy response remains the numerical reference; 5-keV and 0.5-keV comparisons remain diagnostics without a pre-registered formal tolerance. Do not start the final profile likelihood.

