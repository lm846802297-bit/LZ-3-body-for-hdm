# LZ 2026 three-body NR response: selection audit and energy-grid convergence plan

Date: 2026-11-15  
Branch: \`research/figure2-p0-4-mainline\`  
NEST source pin: \`541b6430dae6ea289cf110c99f174a9187f7fdee\`

## 1. Corrected status of the existing 2D response

The earlier label "pre-selection signal prediction" was too broad. The existing event driver calls

\[
\texttt{FullCalculation(NR)}\to\texttt{GetS1(Parametric)}\to\texttt{GetS2(Full)}.
\]

At the pinned NEST source:

- \`LZ_Detector_2024\` sets \`coinWind = 150 ns\`, \`coinLevel = 3\`, and \`numPMTs = 481\`.
- \`SetEFT2024Configuration()\` changes \`g1\), \`g1_gas\), \`s2_thr = 120 phe\), \`eLife_us = 15000 us\), and the EFT2024 yield/width vectors. It does not overwrite the threefold-coincidence settings.
- In \`GetS1()\`, the Parametric mode estimates the S1 coincidence probability. When the coincidence draw fails, NEST makes the returned S1 observables negative to flag the failure.
- In \`GetS2()\`, if the uncorrected pulse area is below \`abs(s2_thr)\`, NEST makes the returned S2 observables negative.

The current fold filters on positive signed \`s1c\` and \`s2c\`. Thus the existing 2D intensity already includes the **NEST-parametric S1 threefold-coincidence acceptance** and the **NEST 120-phe S2 pulse threshold**. These are already applied and must not be multiplied in a second time.

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
- \`extract_lz_2026_nr_selection_efficiency_components.py\`
- Output: \`lz_2026_nr_selection_efficiency_components.csv\` and metadata JSON.

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
- \`nest_level\`: NEST S1-coincidence AND NEST S2-threshold pass.
- \`nest_plus_ws_roi\`: \`nest_level\` plus the published S1c, raw-S2, and S2c ROI conditions.

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
\`5c0e3c254dbcf81f55a5af49be8e1e1f409ef294\`:

- [GitHub Actions run 43648916347](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43648916347), conclusion: success.
- Artifact: \`lz-2026-three-body-response-grid-convergence\`, artifact ID \`14135491602\`.
- Downloaded archive SHA-256:
  \`7ba7e268026f5607f0a4cfecbc1e910ec3c1ec808f727e8d42308b8fa00a96b6\`.
- The archived \`grid_convergence_summary.json\` contains 192 grid comparisons and 64 1-keV replica comparisons.

### 8.1 What the run actually sampled

Each of the four response families (\`eft2024\`, \`tableS5\`, \`ws2024\`, \`generic\`) contains 1,060,000 events:
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
| 5 keV | 0.5131% | 0.8499% |
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
\`lz_nr_conditional_2d_pdf.json\` pilot did not retain event-level coincidence and
threshold flags. The newer stratified CSVs do retain:

- true \(E_{\rm NR}\), true \(x,y,z\), field, and drift time;
- signed and absolute corrected \(S1_c\) and \(S2_c\);
- uncorrected S1 and S2 in phd;
- the NEST S1 spike-count field \`s1.at(8)\`;
- explicit sign-derived \`s1_coincidence_pass\` and \`s2_threshold_pass\` flags;
- photons and extracted electrons.

The new \`signal_2d_intensity_1keV.csv\` contains 62,224 observable-cell intensity rows, with two distinct modes:
- \`nest\`: NEST S1 Parametric coincidence pass AND NEST S2 threshold pass;
- \`ws_roi\`: the above plus \(3\leq S1_c\leq600\) phd, raw \(S2>645\) phd, and \(2.75\leq\log_{10}S2_c\leq4.15\).

The probabilities use \(N_{\rm cell}/N_{\rm generated}\); failed NEST-level events remain in the denominator. The \`ws_roi\` intensity is therefore an intermediate NEST-plus-WS-ROI signal prediction, not the full LZ selected signal PDF.

The event driver uses \`GetS1(S1CalculationMode::Parametric)\`. In the pinned NEST source, this mode samples a PMT-occupancy coincidence probability from the spike count, \`coinLevel=3\`, and \`numPMTs=481\`. Although the LZ detector header sets \`coinWind=150 ns\`, the Parametric branch does **not** explicitly apply that timing window. It is not a waveform-level reconstruction of three distinct PMTs within 150 ns. The saved \`s1_spike_count\` is the NEST spike-count input to this occupancy approximation, not a measured distinct-PMT multiplicity.

The event driver also passes the same \(x,y,z\) as both the true and smeared positions to NEST. Thus the position correction uses perfect reconstructed position in this run. The uniform active-cylinder spatial prior is not the 4.71-tonne FV map, and position-reconstruction smearing is not represented.

The NEST S2 threshold is response-family dependent: \`SetEFT2024Configuration()\` sets \(s2_{\rm thr}=120\) phe for the EFT2024, rounded-Table-S5, and generic-yield runs, while the unmodified WS2024 detector constructor sets \(s2_{\rm thr}=783\) phe. The published raw-S2 ROI condition is \(S2>645\) phd. With \(P_{\rm dphe}=0.214\), 645 phd corresponds to about \(645(1+0.214)=783.03\) phe, so the WS2024 detector threshold is effectively aligned with the raw-S2 ROI boundary; the EFT2024 120-phe threshold is looser. In the archived 4.24-million-event sample, no event with raw \(S2>645\) phd failed its configured NEST S2 threshold. Thus the NEST S2 threshold is redundant after the raw-S2 ROI cut for this sample; it must not be counted as a second independent efficiency loss.

### 8.4 The 2D ROI response does not yet reproduce the published cumulative efficiency

The vector-extracted black curve in Supplemental Fig. S2 is the published cumulative
\[
\text{trigger}+\text{S1 threshold}+\text{SS/data-analysis cuts}+\text{WS ROI}
\]
efficiency. The new \`ws_roi\` acceptance contains NEST Parametric S1 coincidence, the NEST S2 threshold, and the explicit S1c/raw-S2/S2c ROI. It does not contain trigger, SS reconstruction, data-analysis cuts, FV, or veto selections.

Representative comparisons are:

| True-energy location | Published Fig. S2 final cumulative efficiency | EFT2024 NEST+WS-ROI | Table S5 NEST+WS-ROI | WS2024 NEST+WS-ROI | Generic NEST+WS-ROI |
|---|---:|---:|---:|---:|---:|
| 5.4 keV (first 1-keV bin: 5.4–6.4) | 0.5718 | 0.7188 | 0.6945 | 0.6415 | 0.6920 |
| 248 keV (bin: 247.4–248.4) | 0.9457 | 0.8495 | 0.9765 | 0.9255 | 0.5218 |
| 269.9 keV (last bin: 269.4–269.9) | 0.4988 | 0.5555 | 0.8120 | 0.8135 | 0.2710 |

These are not identical selections or priors, so they are not a direct efficiency calibration. Nevertheless, the EFT2024 and generic NEST-plus-ROI acceptances falling **below** the published full cumulative efficiency near 248 keV is a non-closure diagnostic: a strict subset of the published selection should not have a lower acceptance if both were generated with the same response and nested definitions. The discrepancy cannot be repaired by multiplying a residual efficiency onto the current 2D map. It requires investigation of the exact LZ production NEST configuration, the spatial prior and position correction, and the response/ROI comparison.

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

## 9. Correct release status

The previous blanket label "pre-selection" should now be made more precise:

- The original 10-keV compact 2D pilot is a positive-observable conditional response-shape artifact.
- The newer 1-keV \`nest\` intensity includes NEST Parametric S1 coincidence and NEST S2-threshold acceptance.
- The newer 1-keV \`ws_roi\` intensity additionally applies the published S1c/raw-S2/S2c ROI.
- Neither new intensity includes the complete LZ trigger, waveform-level S1 timing, SS reconstruction, data-analysis cuts, official FV, veto sample assignment, or live-time treatment.

Accordingly, describe the current result as a **NEST-level / WS-ROI intermediate three-body signal prediction**, not as the final LZ post-selection signal PDF. Keep the 1-keV response as the reference; regard 5-keV as a promising sub-percent approximation pending a pre-registered tolerance and MC covariance treatment. Do not start the final profile likelihood.
