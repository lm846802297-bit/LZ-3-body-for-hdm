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

**S2 threshold nesting:** in pinned NEST, `GetS2()` returns raw (S2_r) in phd as
(mathrm{pulseArea}/(1+P_{mathrm{DPE}})). The EFT2024 NEST threshold is
120 phe, while the explicit WS ROI requires (S2_r>645) phd. Therefore any
event passing the raw-S2 ROI necessarily passes the lower NEST pulse threshold.
The NEST S2 flag is present in the signed response, but it does not create a
second independent acceptance loss after the raw-S2 ROI. The bridge now asserts
this nesting against the archived events. By contrast, the NEST Parametric S1
coincidence is not implied by (S1_c\geq3) phd and remains an approximate
additional preselection; it is not the official waveform-level timing cut.

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

This rerun regenerated the same calculation with the corrected audit record; it did not introduce a new response model or an independent coarse-grid Monte Carlo production. The summary still records `formal_pass: null` and `DIAGNOSTIC_ONLY_NO_PREDECLARED_TOLERANCE`.

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

The largest 5-keV shape difference is smaller than the corresponding 1-keV split-sample TV difference for every matched benchmark/model/family/mode combination. The largest 1-keV split-sample TV difference is 3.9611% in the NEST-level mode and 3.3643% in the NEST-plus-WS-ROI mode. The maximum split-sample accepted-rate difference in the WS-ROI mode is 0.4469%.

Interpretation:
- 5 keV is numerically close to the 1-keV reference at the sub-percent level for this particular response MC and these benchmark spectra.
- 10 keV shows visibly larger shape differences, reaching about 2.5% TV.
- The current workflow has no pre-registered scientific tolerance and does not fail when these metrics exceed a chosen threshold. Its green Actions status means the build, unit tests, numerical run, and artifact upload completed; it is **not** by itself a formal grid-convergence PASS.
- A formal acceptance criterion must be agreed before promoting 5 keV as the production grid. Keep 1 keV as the reference until that decision is recorded.

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



## 9. Correct release status

The previous blanket label "pre-selection" should now be made more precise:

- The original 10-keV compact 2D pilot is a positive-observable conditional response-shape artifact.
- The newer 1-keV `nest` intensity includes NEST Parametric S1 coincidence and NEST S2-threshold acceptance.
- The newer 1-keV `ws_roi` intensity additionally applies the published S1c/raw-S2/S2c ROI.
- Neither new intensity includes the complete LZ trigger, waveform-level S1 timing, SS reconstruction, data-analysis cuts, official FV, veto sample assignment, or live-time treatment.

Accordingly, describe the current result as a **NEST-level / WS-ROI intermediate three-body signal prediction**, not as the final LZ post-selection signal PDF. Keep the 1-keV response as the reference; regard 5-keV as a promising sub-percent approximation pending a pre-registered tolerance and MC covariance treatment. Do not start the final profile likelihood.




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


## 15. Explicit no-double-counting matrix and proposed grid gate

### 15.1 Selection overlap matrix

| Quantity / stage | In the current 2D response? | In Fig. S2 cumulative curve? | Correct treatment |
|---|---|---|---|
| NEST Parametric S1 threefold occupancy | Yes, as an approximate PMT-occupancy acceptance | The official S1 identification/reconstruction contribution is part of the later SS/data-analysis stage; the exact overlap is not separately digitized | Do not multiply a second generic threefold factor. Keep the NEST-vs-Full comparison as a mode check, not as proof of official reconstruction equivalence. |
| Official S1 amplitude threshold | The explicit \(3\leq S1_c\) lower WS ROI boundary is applied in the ws_roi mode; the full pulse-finding/threshold chain is not | Yes, in the orange cumulative curve | The orange curve is a rate-level audit target; do not apply it again to the WS-ROI map. |
| NEST S2 pulse-size threshold | Yes; EFT2024 uses 120 phe | Not the same quantity as the hardware S2 trigger | Retain as part of NEST response; do not call it the DAQ trigger. |
| S2 DAQ trigger | No | Yes, blue cumulative curve | Missing from the 2D map. It is unity over the present benchmark recoil support in the extracted Fig. S2 curve, but this does not validate the low-energy trigger model generally. |
| Raw-S2 and corrected-S2 WS ROI | Yes, in the WS-ROI mode | Yes, in the black cumulative curve | Direct overlap. Never multiply the full black curve into the existing WS-ROI map. |
| SS reconstruction and data-analysis cuts | No | Yes, in the green cumulative curve | Use only in a separate 1D rate-level count until a validated 2D conditional response is available. |
| Fiducial-volume spatial acceptance | No; the map uses a uniform active-TPC proxy | Not recoverable as a 2D map from Fig. S2 alone | Use the official 4.71-t FV geometry and reconstruction smearing; the exposure mass does not by itself impose the correct event-position acceptance. |
| Skin/OD science, prompt-veto, delayed-veto partition | No | The efficiency curve is not a three-sample migration model | Build correlated sample-specific signal rates; do not apply one generic veto-survival scalar. |
| Live-time hold-offs | No event-by-event model | Reflected in the published live exposure | The 2.84 tonne-year exposure is \(4.71\ {\rm t}\times220\) live days. Do not multiply by the 81.5% live-time retention again. |

The one-dimensional Fig. S2 final cumulative curve is appropriate for the
independent energy-integrated expected-count calculation. It is not a
per-event weight for the current 2D map. The current WS-ROI map already
contains NEST coincidence, the NEST pulse threshold, and the explicit WS
ROI. The missing SS/data-analysis, FV, and veto effects are correlated with
event reconstruction and/or sample assignment; Fig. S2 does not provide
their two-dimensional conditional kernels.

### 15.2 Approved response-grid engineering gate (2026-11-15)

The analysis owner approved the following point-estimate engineering gate:

\[
\boxed{
\delta_{\rm acc}^{\max}\leq 1.0\%,
\qquad
D_{\rm TV}^{\max}\leq 1.0\%.
}
\]

Both maxima are evaluated over all tested benchmarks, nuclear responses,
NEST response families, and acceptance modes, relative to the 1-keV reference.
The current artifact-level comparisons give:

| Grid relative to 1 keV | Maximum accepted-rate difference | Maximum 2D total-variation distance | Gate |
|---|---:|---:|---|
| 5 keV, all tested families/benchmarks/models/modes | 0.5131% | 0.8896% | PASS |
| 5 keV, primary EFT2024 family | 0.3249% | 0.4579% | PASS |
| 10 keV, all tested families/benchmarks/models/modes | 1.2146% | 2.4649% | FAIL |

**Decision:** 5 keV passes the approved numerical grid gate; 10 keV fails.
This is a formal acceptance of the *coarse-grid reaggregation point
estimates*, not yet an unconditional production-Monte-Carlo acceptance.
The 5-keV values are reconstructed by width-averaging the existing 1-keV
response strata; they are not an independently generated 5-keV Monte Carlo.

There are three qualifications:
1. The 5-keV rate difference exceeds the corresponding 1-keV split-sample
   rate difference in 17/64 comparisons. The two halves are disjoint portions
   of one seeded stream, not independent-seed productions; they do not provide
   a complete MC covariance estimate.
2. The dedicated 0.5-keV high-energy-tail refinement differs from the
   1-keV response by at most 0.46895% in accepted rate and 2.5446% in 2D TV.
   Its 2D TV is above the 1.0% grid threshold, so it is not a passing
   production grid. It remains a local refinement diagnostic for the black
   benchmark; two EFT2024 black-benchmark rate comparisons also exceed the
   current split-sample rate checks.
3. The event-weighted fold provides an algorithmic cross-check: its maximum
   difference from the 1-keV binned fold is 0.02821% in accepted rate and
   0.07920% in 2D TV, with raw-rate closure \(1.11\times10^{-15}\).
   This validates the folding implementation, not the detector model.

**Provisional status at this stage:** the 5-keV deterministic
reaggregation passed the point-estimate grid gate, but this was not an
independent 5-keV Monte Carlo. The later full-range independent-seed result
in Section 15.6 supersedes this provisional production-grid recommendation.
Until that check is passed, retain 1 keV as the numerical reference. This
grid decision is separate from the remaining full-LZ selection and
likelihood blockers in Section 14.5.

### 15.3 Independent-seed high-energy-tail validation (2026-11-15)

The original single-stream EFT2024 black-benchmark tail comparison showed a
0.45--0.47% accepted-rate difference and about 1.87--1.89% 2D TV between
0.5-keV and 1-keV folds. To distinguish a stable grid effect from finite-MC
fluctuations, six independent full productions were generated:

- 1-keV seeds: 20261120, 20261122, 20261124.
- 0.5-keV seeds: 20261121, 20261123, 20261125.
- 10,000 events per energy stratum per seed, over 225.4--269.9 keV.
- EFT2024 response, black benchmark, both GCN and JJ55; 4.02 million events total.
- The two within-seed halves are used only as internal diagnostics; the three
  full productions per grid are the independent replication units.

The WS-ROI mean-rate comparison is:

| Nuclear response | Mean 1-keV rate (events kg\(^{-1}\) day\(^{-1}\)) | Mean 0.5-keV rate (events kg\(^{-1}\) day\(^{-1}\)) | Relative rate difference | Difference / combined seed SEM | TV between mean 2D maps |
|---|---:|---:|---:|---:|---:|
| GCN | \(2.4334094\times10^{-15}\) | \(2.4329815\times10^{-15}\) | 0.01758% | 0.171 | 0.6865% |
| JJ55 | \(2.4549401\times10^{-15}\) | \(2.4544830\times10^{-15}\) | 0.01862% | 0.186 | 0.6803% |

For the NEST-only mode, the accepted rates are identical between the two
energy grids; the TV distances between mean maps are 0.8489% (GCN) and
0.8407% (JJ55). Therefore, across both acceptance modes and both nuclear
responses, the maximum mean-map TV is 0.8489%, and the maximum accepted-rate
difference is 0.01862%. The independent-seed mean-map comparison passes the
same 1.0% / 1.0% local-tail numerical gate.

The earlier 0.45--0.47% rate difference is not reproduced by the independent
seed means. The new difference is only 0.17--0.19 of the combined seed
standard error. This supports finite-MC fluctuations as the dominant source
of the earlier discrepancy; it does not establish a calibrated hypothesis
test, because there are only three independent productions per grid.

Individual-seed shape fluctuations remain larger than the mean-map
difference: the largest pairwise seed TV is about 1.87% for 1 keV and
1.39% for 0.5 keV across the tested modes. The mean-map gate therefore
validates the grid-averaged tail shape, not a complete cell-by-cell
covariance matrix.

The gated workflow and archived raw samples are [run 43691733080](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43691733080),
artifact 14151869654, SHA-256
837a0385cac4c784abef38a5d4efc4273fc92ba01ddfcfab9123c90baecf2543.
Its machine-readable local-tail gate reports PASS, with maximum mean-rate
difference 0.01862% and maximum mean-map TV 0.8489%.

**Local-tail update only:** the independent 0.5-keV/1-keV black-tail
mean-map comparison passes its local 1.0% / 1.0% point-estimate gate. It
does not test the full-range 5-keV grid and must not be used to promote
5 keV. The full-range independent 1-keV/5-keV result is recorded in
Section 15.6 and supersedes the earlier coarse-grid production
recommendation. Neither grid study closes the missing SS/data-analysis,
official FV, Skin/OD sample migration, or complete LZ selection response.

### 15.4 Table S5 rounding is a material NR-response alternative (2026-11-15)

The printed Table S5 vector and the public full-precision EFT2024 vector share
the same high-energy \(p(E)\) extension, but they do not give equivalent
NR mean light/charge yields. A direct C++ comparison against the pinned NEST
541b643 GetYieldNR implementation was run for both vectors:

- 528 scalar Python/C++ comparisons passed across Xe-128/131/136, both
  OldW13eV settings, and 11 energies from 5.4 to 330 keV.
- Worst scaled absolute Python/C++ differences were
  \(3.33\times10^{-16}\) for Table S5 and \(2.16\times10^{-16}\) for EFT2024.
- At 248 keV, Table S5 relative to EFT2024 gives
  \(\Delta N_\gamma=-7.4528\%\),
  \(\Delta N_e=+0.3846\%\), and
  \(\Delta(N_\gamma+N_e)=-6.9997\%\).
- At 269.9 keV, the corresponding changes are
  \(-7.5301\%\), \(+0.3846\%\), and \(-7.1019\%\).

The exponent \(p(E)\) is identical in both parameter vectors. The dominant
difference comes from the rounded NR total-quanta normalization and slope;
the light yield is then obtained after subtracting the nearly unchanged
charge yield. Consequently, a small-looking parameter rounding changes S1
appreciably near the upper recoil-energy boundary.

The existing coarse-binned 2D fold reports \(D_{\rm TV}=0.162\text{--}0.249\)
between the Table-S5-mean/EFT2024-width hybrid and full EFT2024 across the
four benchmarks and GCN/JJ55. This is a response-family difference, not a
grid-discretization error. The result belongs to the earlier 10-keV,
200,000-event-per-family fold and should not be relabelled as a 1-keV
independent-seed comparison.

The direct mean-yield cross-check is [run 43696267500](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43696267500),
artifact 14154536453, SHA-256
20b399d199c2ce5392250bc2dfb9e8ddc4e3ab3f0711e5d89e0432db596ce5af.

**Interpretation:** keep EFT2024 as the primary public executable candidate
and Table S5 as a distinct rounded-table alternative. The exact 2026
collaboration production configuration remains unconfirmed.

The 265-bin monotonicity comparison against the final Fig. S2 curve is only
a plausibility diagnostic. The simulated NEST S1 coincidence and NEST S2
pulse threshold are not identical to the collaboration's DAQ trigger and
S1-threshold stages; the uniform active-TPC spatial prior is also not the
official calibration/FV prior. Therefore, the fact that Table S5 stays above
the digitized final curve while EFT2024 falls below it in some bins must not
be used as a strict nested-efficiency proof or as a stand-alone rule for
selecting the production model.


### 15.6 Full-range independent-seed 1-keV versus 5-keV validation (2026-11-15)

The deterministic 5-keV reaggregation was followed by genuinely independent
full-range Monte Carlo productions. Both NR mean-yield families were tested
with disjoint seed sets:

- 1-keV seeds: 20261132, 20261134, 20261136.
- 5-keV seeds: 20261133, 20261135, 20261137.
- True recoil interval: 5.4--269.9 keV.
- Event density: 4,000 events/keV, scaled to the exact width of every stratum,
  including 2,000 events in the final 0.5-keV bin and 18,000 in the final
  4.5-keV bin.
- Each seed/grid/family sample contains 1,058,000 events; the paired-family
  study contains 12,696,000 events.
- Each response family has 16 comparisons: four benchmarks × GCN/JJ55 ×
  NEST-only/NEST+WS-ROI.

The independent-seed mean-map gate gives:

| Response family | Maximum accepted-rate difference | Maximum 2D TV between mean maps | 1% / 1% gate |
|---|---:|---:|---|
| EFT2024 | 0.645014% | 1.481245% | FAIL |
| Table S5 | 0.201630% | 1.468098% | FAIL |

The accepted-rate differences pass the 1% requirement for both families.
The 2D TV requirement does not. The limiting rows are the black
\(m_s=360\) keV benchmark:

| Black benchmark comparison | EFT2024 | Table S5 |
|---|---:|---:|
| GCN, NEST-only 2D TV | 1.4812% | 1.4681% |
| JJ55, NEST-only 2D TV | 1.4664% | 1.4504% |
| GCN, NEST+WS-ROI 2D TV | 1.0716% | 1.2706% |
| JJ55, NEST+WS-ROI 2D TV | 1.0635% | 1.2561% |

The red/green/blue benchmark mean-map TV values remain approximately
0.745--0.782%. Thus the full-range failure is localized to the black
high-energy benchmark, not a global normalization difference.

The observed black cross-grid mean-map TV (about 1.06--1.48%) is smaller
than the largest pairwise seed-to-seed TV within either grid (about
2.1--2.9%); within-seed split-half TV reaches about 3.9%. This indicates
that the present three-seed MC spread is comparable to or larger than the
observed grid difference. It does **not** establish a statistically
significant systematic 5-keV bias. Nevertheless, the pre-agreed
point-estimate engineering gate is not passed, and it must not be relaxed
after seeing the result.

The raw independent-production artifact is [run 43699011757](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43699011757),
artifact 14155573365 (981,003,582 bytes). The summary-only export is
[run 43699599124](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43699599124),
artifact 14155488034, ZIP SHA-256
9439cb84533beb4aed9104fa529ab9d132af573b9feac19db255b1f81d08b1bf.
Both family summaries and the per-seed CSVs were downloaded and inspected.

**Updated full-range grid decision:** retain 1 keV as the numerical reference
for both EFT2024 and Table S5. Do not promote 5 keV as the production grid
under the approved 1% / 1% gate. The earlier deterministic reaggregation
PASS remains a valid statement about that fixed response sample, but it is
not an independent-MC validation. If reducing the full-range production
cost is necessary, the next justified step is a targeted higher-statistics
black-benchmark comparison or additional independent seeds, not relaxing
the gate. This remains an intermediate NEST/WS-ROI result and does not
supply the missing full LZ selected-event response.


### 15.5 Conditional Fig. S2 bridge is model-dependent (2026-11-15)

The updated event-weighted 2D fold was joined to the four vector-extracted
Fig. S2 cumulative stages separately for EFT2024 and the Table S5-mean /
EFT2024-width hybrid. Each family has eight matched rows (four benchmarks ×
GCN/JJ55). The maximum absolute rate-level factorisation mismatch is 7.6250%
for EFT2024 and 13.0272% for Table S5.

For the black \(m_s=360\) keV, GCN point:

| Quantity | EFT2024 | Table S5 hybrid |
|---|---:|---:|
| NEST-only acceptance | 100.00% | 100.00% |
| WS ROI conditional acceptance | 74.0612% | 90.6191% |
| Fig. S2 SS+DA conditional efficiency | 95.5790% | 95.5790% |
| Fig. S2 ROI conditional efficiency | 80.1746% | 80.1746% |
| Fig. S2 final cumulative efficiency | 76.6301% | 76.6301% |
| NEST ROI × residual SS+DA factor | 70.7870% | 86.6128% |
| Factorised / Fig. S2 final − 1 | −7.6250% | +13.0272% |

JJ55 gives −7.5937% (EFT2024) and +12.7022% (Table S5). The red/green/blue
benchmarks close to within about 0.63% or better. The opposite-sign mismatch
for the black point is therefore not a universal residual-efficiency
normalization issue; it is tied to the high-energy ROI response and the
choice of NR mean-yield family.

The factorisation used here is
\[
\epsilon_{\rm NEST}\,
\epsilon_{\rm WS\,ROI\mid NEST}\,
\epsilon_{\rm SS+DA\mid preROI},
\]
compared with the Fig. S2 final cumulative efficiency. The WS ROI is already
present in the 2D response, so the Fig. S2 ROI conditional factor is not
multiplied again. This is only a rate-level bookkeeping test. It does not
supply the conditional 2D SS/DA migration kernel and cannot be used as a
global scalar correction to the \((S1_c,\log_{10}S2_c)\) intensity.

The calculation is [run 43697104437](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43697104437),
artifact 14155360851, ZIP SHA-256
682e2ba71063d6ef835b37a6d328a84ab7c609f404856aa83d56e4b875794bab.
The artifact was downloaded and the two response-family bridge JSON files
were independently inspected.




### 15.7 Paired Parametric/Full S1 two-dimensional response and finite-sample stability (2026-11-15)

A paired event-level comparison was run with the pinned NEST commit
541b6430dae6ea289cf110c99f174a9187f7fdee and
LZ_Detector_2024::SetEFT2024Configuration().

Production definition:

- True recoil support: 35--269.9 keV, 235 one-keV strata.
- 2,000 events per stratum, 1,000 in each of two disjoint within-stream halves;
  470,000 events total.
- Both S1 modes receive the same intrinsic NR quanta and true position.
  Parametric and Full S1 use separate response random streams, while a single
  common NEST Full S2 response is shared by the pair.
- Four three-body benchmarks: red \(m_s=200\) keV, green \(m_s=300\) keV,
  black \(m_s=360\) keV, and blue \(m_s=300\) keV with
  \(\Delta m=10\) MeV.
- GCN and JJ55 spectra are folded separately. The NEST detector/yield
  configuration in this production is EFT2024 only; this is not a Table S5
  NEST-yield production.
- Two stages are retained: NEST coincidence plus S2-threshold acceptance
  (nest), and the same response plus the WS S1c/raw-S2/S2c ROI (ws_roi).

The artifact contains 1,880 per-energy-bin rows (8 benchmark/nuclear pairs
times 235 bins), 16 stage summaries, and 20,244 2D map cells. The pooled
event-weighted TV values from the independent audit reproduce the fold
summary exactly: the maximum absolute difference across all 16 rows is zero.

#### 15.7.1 Integrated rate versus 2D shape

The generated sample has 100% NEST S1-coincidence and NEST S2-threshold
acceptance in every 1-keV signal-support bin for both S1 modes. The difference
between modes is therefore not an observed NEST threshold-acceptance loss in
this support; it is principally a redistribution of the corrected S1
observable in the 2D response.

Averaging GCN and JJ55 results, the WS-ROI totals are:

| Benchmark | Parametric WS-ROI acceptance | Full WS-ROI acceptance | Full/Parametric rate change |
|---|---:|---:|---:|
| Red, 200 keV | 99.8157% | 99.8090% | -0.0067% |
| Green, 300 keV | 99.2705% | 99.2446% | -0.0261% |
| Black, 360 keV | 74.2696% | 74.0600% | -0.2822% |
| Blue, 300 keV, \(\Delta m=10\) MeV | 99.2746% | 99.2489% | -0.0259% |

The 2D TV, one-dimensional marginal TVs, and within-mode split-half
comparisons are:

| Benchmark | Stage | Parametric/Full 2D TV | S1c marginal TV | \(\log_{10}S2_c\) marginal TV | Mean within-mode split-half TV | 2D TV / split-half TV |
|---|---|---:|---:|---:|---:|---:|
| Red | NEST | 1.652% | 0.647% | 0.000% | 2.574% | 0.642 |
| Red | WS ROI | 1.644% | 0.643% | 0.004% | 2.565% | 0.641 |
| Green | NEST | 1.750% | 0.761% | 0.000% | 2.635% | 0.664 |
| Green | WS ROI | 1.721% | 0.745% | 0.013% | 2.600% | 0.662 |
| Black | NEST | 3.851% | 1.409% | 0.000% | 5.176% | 0.744 |
| Black | WS ROI | 3.233% | 1.252% | 0.211% | 4.291% | 0.754 |
| Blue | NEST | 1.750% | 0.761% | 0.000% | 2.634% | 0.664 |
| Blue | WS ROI | 1.721% | 0.745% | 0.013% | 2.600% | 0.662 |

The marginal TV values are averaged over GCN and JJ55. At the NEST stage,
the S2 marginal is identical to floating-point precision because the same
S2 draw is shared by the two S1 modes and every event in this signal support
passes the NEST thresholds. The non-zero joint TV is therefore a change in
the conditional S1c--S2c structure, not a shift in the S2 marginal. After
WS-ROI selection, the S1-dependent cuts induce small changes in the S2
marginal, largest for the black benchmark.

The observed pooled Parametric/Full TV is below the mean within-mode
replica-0-versus-replica-1 TV in every row: the ratio ranges from 0.641 to
0.754. This is a descriptive within-production stability comparison only.
The two replicas are disjoint halves of one seeded event design, not
independent-seed productions. It is not a confidence interval or a
significance test. The result does not establish that the two S1 modes are
statistically equivalent; it shows that the current single-seed sample does
not resolve the mode difference cleanly against its own split-half map
fluctuations.

#### 15.7.2 Histogram-binning sensitivity

The 2D TV is sensitive to the map binning. Rebinning the same native
10-phd by 0.02-dex maps (without generating new events) gives:

| Benchmark | Stage | 10 phd / 0.02 dex | 20 phd / 0.04 dex | 40 phd / 0.08 dex |
|---|---|---:|---:|---:|
| Red | NEST | 1.652% | 0.878% | 0.476% |
| Red | WS ROI | 1.644% | 0.875% | 0.474% |
| Green | NEST | 1.750% | 1.051% | 0.504% |
| Green | WS ROI | 1.721% | 1.041% | 0.499% |
| Black | NEST | 3.851% | 2.041% | 0.790% |
| Black | WS ROI | 3.233% | 1.604% | 0.734% |
| Blue | NEST | 1.750% | 1.050% | 0.504% |
| Blue | WS ROI | 1.721% | 1.041% | 0.500% |

This is exact cell aggregation of the existing map, not an independent response
calculation. It demonstrates that TV cannot be quoted without specifying
histogram resolution. A final likelihood must choose binning based on the
analysis observable resolution and demonstrate its own binning stability;
the 1% energy-grid convergence gate is not automatically a gate on S1/S2
histogram resolution.

#### 15.7.3 Status and next requirement

The paired NEST 2D calculation and its exact weighted closure passed. It
remains a diagnostic EFT2024 NEST response, not the official LZ selected PDF:
Full S1 is not the collaboration waveform-level reconstruction; S2 is NEST
integrated Full mode rather than hardware DAQ; SS reconstruction, data-analysis
cuts, official 4.71-tonne FV, Skin/OD veto samples, and live-time migration
remain absent.

The single-seed comparison above is not accepted as a final equivalence
test. The requested independent-seed ensemble and separate observable-binning
audit have now been completed; their results and limitations are recorded in
Section 15.8. The EFT2024 result remains separate from the Table S5 NR-yield
alternative. No final profile likelihood is authorized by these intermediate
NEST-level response studies.

The original paired production is
[run 43717240547](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43717240547),
artifact 14162588482, ZIP SHA-256
6002e6ea4c345c13aa8c3e056647bb317bb41e3d6ff670dabf23c0bb343bee9b.
The downloaded archive and all response/summary files were independently
inspected.

## 15.8 Independent-seed paired S1 ensemble and observable-binning audit

### Production design and provenance

The initial three-seed study has been extended to ten independent paired
Parametric/Full S1 productions. Each production covers the complete
35--269.9 keV signal support in 235 one-keV strata, with 2,000 events per
stratum (470,000 events per seed; 4,700,000 events total). The ten base seeds
are 20261117, 40261117, 60261117, 80261117, 100261117, 120261117,
140261117, 160261117, 180261117, and 200261117. For event index i, the
driver uses four NEST streams base_seed + 4i + {1,2,3,4}. The minimum
base-seed gap is 20,000,000, larger than the maximum per-event offset of
1,880,000; the random-stream non-overlap check passed.

Within each seed, both S1 modes use the same intrinsic NR quanta and true
position, but independent S1 response draws; each paired event shares one
NEST Full S2 draw. The event samples are folded with exact piecewise-linear
natural-xenon three-body rate weights, normalized independently in each
true-energy stratum. The detector-response configuration is
LZ_Detector_2024::SetEFT2024Configuration() at pinned NEST commit
541b6430dae6ea289cf110c99f174a9187f7fdee. GCN/JJ55 label the nuclear-recoil
spectra, not alternative NEST detector configurations.

Production:
[run 43750948249](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43750948249),
artifact 14176882910, ZIP SHA-256
606397d9eac594008630a18b97f1e72fbbfa1d157e34779de7ce5fd0fe5b8cb5.
The downloaded ZIP is 489,714,347 bytes. All 75 entries in its internal
SHA256SUMS manifest were independently verified. Each of the ten raw event
CSV files contains exactly 470,000 sequential event rows (event indices
0--469,999), with exactly 2,000 events in each of the 235 energy bins.
The seed ranges are disjoint under the event-level NEST seed rule.

The archived ten-seed fold products contain all ten per-seed response maps,
rate summaries, and split-half diagnostics, plus the ensemble maps and
metadata. The ten raw event CSVs remain in the immutable Actions artifact;
raw_event_artifact_SHA256SUMS.txt preserves the complete 75-file manifest.
The original production artifact remains unchanged.

### Independent-seed ensemble results

The ensemble map is the equal-weight arithmetic mean of the ten
event-weighted per-seed rate maps. The table below averages the GCN and JJ55
results for the WS-ROI stage:

| Benchmark | Ensemble-mean Parametric/Full 2D TV | Mean per-seed mode TV | Within-mode seed-pair TV | Full/Parametric WS-ROI rate change |
|---|---:|---:|---:|---:|
| Red, 200 keV | 0.649% | 1.753% | 1.884% | -0.0054% |
| Green, 300 keV | 0.648% | 1.816% | 1.898% | -0.0210% |
| Black, 360 keV | 0.938% | 2.900% | 3.003% | -0.594% |
| Blue, 300 keV, Δm=10 MeV | 0.648% | 1.815% | 1.898% | -0.0209% |

The ensemble-mean TV, mean per-seed TV, and within-mode pairwise seed TV
are different statistics. The ratio of the ensemble-mean TV to the
within-mode pairwise TV is descriptive only; it is not the standard error
or confidence interval of the ensemble-mean TV and is not an equivalence
test. The ensemble metadata has been corrected to state the actual ten-seed
count and this limitation. The archived ensemble summaries were regenerated
from the same ten per-seed fold products; no NEST events were regenerated
and no numerical inputs were changed. The original production artifact
remains immutable.

The black benchmark remains the sensitive case. At the native
10-phd by 0.02-dex binning, its WS-ROI ensemble-mean TV is 0.943% (GCN)
and 0.932% (JJ55), while its mean per-seed mode TV is 2.916% and 2.883%.
The within-mode pairwise seed TV is 3.021% and 2.986%, respectively.

A seed-subset check shows why the combined point estimate must not be
promoted to a precision equivalence claim. Averaging GCN/JJ55, the black
WS-ROI mean-map TV is 1.912% for the original three seeds, 1.124% for the
seven newly added seeds alone, and 0.938% for all ten seeds together.
Thus the ten-seed combined point estimate is below the 1% engineering
threshold, but the independent seven-seed subset remains above it. The
point-estimate gate is not yet robust to the seed subset.

The black integrated WS-ROI rate shift is more stable. Across all ten
seeds, Full relative to Parametric changes the rate by -0.598% (GCN) and
-0.588% (JJ55); the seed-to-seed standard deviations are 0.288 and
0.282 percentage points. Student-t intervals over the ten seed-level
differences are approximately [-0.805%, -0.392%] for GCN and
[-0.790%, -0.386%] for JJ55. The seven newly added seeds alone give
-0.641% (GCN) and -0.631% (JJ55), with all seven seed-level changes
negative in both nuclear-response cases. These are seed-level Monte Carlo
diagnostics for the current NEST proxy, not official detector-systematic
intervals or a detector correction factor.

At the NEST threshold stage, the black 2D mean-map TV remains 1.168%
(GCN) and 1.154% (JJ55), above the 1% point-estimate threshold. The
WS-ROI result must not be generalized to every selection stage.

Both NEST S1-coincidence and NEST S2-threshold acceptances are 100% in
the generated signal-support samples. Thus the observed rate changes
arise primarily from S1-dependent WS-ROI migration, not a loss at the
NEST threshold stage. Since S2 is shared event by event, the NEST-stage
S2 marginal remains identical between the two S1 modes; the small
nonzero WS-ROI S2-marginal difference arises from S1-dependent selection.

### Observable histogram-binning dependence

The ten-seed binning audit exactly aggregates the same native maps from
10-phd by 0.02-dex cells to 20-phd by 0.04-dex and 40-phd by 0.08-dex
cells. No new events are generated and no interpolation is used. It
contains 48 ensemble rows (16 benchmark/nuclear/stage combinations times
three rebin factors) and 480 per-seed rows.

Binning audit:
[run 43754946092](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43754946092),
artifact 14177248273, ZIP SHA-256
ceca6a9d05cd0342da2d6e994a206111d6a2eadf4863526a7bb540bdbabd7b01.
All three native output-file checksums were independently verified.

The maximum ensemble-mean TV across all benchmark/nuclear combinations
at each stage is:

| Stage | 10 phd / 0.02 dex | 20 phd / 0.04 dex | 40 phd / 0.08 dex |
|---|---:|---:|---:|
| NEST | 1.168% | 0.750% | 0.571% |
| WS ROI | 0.943% | 0.496% | 0.358% |

For the black WS-ROI map specifically, the GCN/JJ55 TV values are
0.943%/0.932% at native binning, 0.496%/0.493% after the first
coarsening, and 0.358%/0.358% after the second. The S1 marginal
contributes 0.411%/0.410% at native binning, while the S2 marginal
contributes 0.099%/0.096%; the S1 marginal is dominant.

The monotonic decrease under coarsening is expected: deterministic
aggregation of cells cannot increase total-variation distance. It is not
evidence that the physical mode difference disappears, and coarse bins
must not be selected merely to force a numerical TV threshold. The native
10-phd by 0.02-dex partition remains the reference until likelihood
binning is chosen from detector resolution and the background/statistical
model, then independently checked for stability. This observable-binning
audit is distinct from the 1/5/10-keV true-recoil response-grid study.

### Interpretation and next requirement

The ten-seed production and 48/480-row binning audit close the numerical
production, map aggregation, and exact-rebinning bookkeeping. They do not
establish Parametric/Full equivalence. In particular, the black 360-keV
WS-ROI mean-map TV is below 1% only in the combined ten-seed point estimate;
the independent seven-seed subset is above 1%. No bootstrap confidence
interval for the ensemble-map TV is included. The black WS-ROI integrated
rate shift is consistently about -0.6%, but it remains a NEST-proxy
mode-dependence diagnostic rather than a detector correction.

The dedicated black 360-keV S1 upper-tail and selection-migration audit
has now been completed; see Section 15.9 and the archived
[upper-tail report](paired_s1_independent_seeds_2026-11-15/upper-tail-audit/REPORT.md).
The complete conditional response matrix must still include the
shared-observable correlations across DAQ, SS reconstruction/data-analysis,
official FV, Skin/OD veto partitions, and live-time treatment. The Fig. S2
residual efficiency must not be multiplied into the existing 2D map as an
independent scalar. No final profile likelihood or 90% CL exclusion is
authorized.


## 15.9 Black 360-keV S1 upper-tail and ROI-migration audit

The dedicated ten-independent-seed upper-tail audit is complete. It reuses
the immutable paired Parametric/Full EFT2024 NEST production from run
43750948249 and does not regenerate events. The black signal support is
\(E_R\in[205,269.9]\ \mathrm{keV}\), containing 1,300,000 paired events
across the ten seeds.

The event-level weights are normalized within each one-keV stratum to the
exact integrated recoil rate from the original per-seed fold. The maximum
relative closure residual over all seeds, GCN/JJ55 models, and strata is
\(6.33\times10^{-15}\), below the \(5\times10^{-12}\) requirement. The
corrected audit passes its unit tests and all production-manifest,
row-count, stratum-closure, selection-closure, and output validations.

### 15.9.1 Main rate and S1 upper-tail result

| Nuclear response | Parametric S1 ROI | Full S1 ROI | Full/Parametric change | 95% seed-level interval |
|---|---:|---:|---:|---:|
| GCN | 73.9501% | 73.5072% | -0.5983% | [-0.8046%, -0.3920%] |
| JJ55 | 74.3246% | 73.8871% | -0.5881% | [-0.7901%, -0.3860%] |

The S1 quantiles shift upward by approximately 1--2 phd in Full mode. For
GCN, the conditional fraction above 600 phd increases from 26.0499% to
26.4928%; for JJ55 it increases from 25.6754% to 26.1129%. The paired
crossing weights show the mechanism directly: 6.4630% (GCN) and 6.3960%
(JJ55) of the raw signal weight moves from Parametric \(S1_c\leq600\) to
Full \(S1_c>600\), while 6.0201% and 5.9585%, respectively, cross in the
opposite direction. The net accepted-weight loss is about 0.44 percentage
points.

### 15.9.2 Energy dependence and shape

| True recoil band [keV] | GCN change | JJ55 change |
|---|---:|---:|
| 205--225 | -0.0603% | -0.0603% |
| 225--240 | -0.1614% | -0.1617% |
| 240--255 | -0.2977% | -0.2983% |
| 255--269.9 | -1.0337% | -1.0335% |
| Legacy tail, 225.4--269.9 | -0.6479% | -0.6372% |

The migration grows toward the highest recoil-energy band. At native
10-phd S1 binning, the ensemble-mean conditional S1 histogram TV is
0.5957% (GCN) and 0.5896% (JJ55); the \(S1_c>500\) upper-tail TV is
0.5832% and 0.5763%. The NEST-stage 2D TV remains above 1% (1.1679% and
1.1538%), while the WS-ROI 2D TV is 0.9425% and 0.9318%. These point
estimates do not establish Parametric/Full equivalence; mean per-seed S1
histogram TV is about 1.44--1.46%.

### 15.9.3 S2 selection is inactive in this support

The raw-event selection audit shows that all 1,300,000 events pass both S1
coincidence flags, the NEST S2 threshold, the strict
\(S2_{\rm raw}>645\ \mathrm{phd}\) cut, and the
\(2.75\leq\log_{10}S2_c\leq4.15\) window. The observed \(S2_{\rm raw}\)
minimum is 4,855.60 phd; \(S2_c\) spans 7,418.07--13,690.33 phd, within
the allowed 562.34--14,125.38 phd range. No event inside either S1 ROI
fails the S2 part of the WS ROI.

Thus, for this black support, the WS-ROI acceptance equals the S1
\([3,600]\)-phd acceptance. The approximately \(-0.59\%\) relative rate
change is caused by the S1 upper-boundary migration, not S2 selection.
This conclusion is specific to this benchmark and energy support.

### 15.9.4 Interpretation and limits

The audit resolves the mechanism behind the black benchmark's integrated
mode dependence: Full S1 is slightly higher in its upper tail, so more
events cross the 600-phd upper boundary than return below it. The effect
reaches about a 1.03% relative loss in the 255--269.9 keV band. GCN and
JJ55 give nearly identical migration trends.

This remains an EFT2024 NEST response diagnostic, not the official LZ
waveform-level selected-event PDF. DAQ trigger, SS reconstruction and
data-analysis cuts, official fiducial volume, Skin/OD veto, live-time
migration, and their joint covariance are absent. The seed-level intervals
quantify production-level Monte Carlo variation only. No detector-systematic
interval, final profile likelihood, or 90% CL exclusion is provided.

Full methods, tables, source hashes, and output descriptions are in the
[archived upper-tail report](paired_s1_independent_seeds_2026-11-15/upper-tail-audit/REPORT.md).
The successful audit is
[run 43759124017](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43759124017),
artifact 14179542527.
