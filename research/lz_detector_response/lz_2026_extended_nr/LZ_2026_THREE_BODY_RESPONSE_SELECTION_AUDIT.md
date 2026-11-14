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

## 3. Cumulative efficiency curves in Supplemental Fig. S2

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

## 4. 1/5/10-keV convergence definition

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

## 5. No-profile-likelihood gate

Do not start the final profile likelihood until all of the following are resolved:

1. 1/5/10-keV response-grid convergence is numerically acceptable for both NEST-level and WS-ROI-masked distributions.
2. The NEST coincidence and S2-threshold overlap with the published cumulative efficiency curve is quantified; no stage is applied twice.
3. Trigger, SS reconstruction, and analysis-cut acceptance are either modelled in the response or included through a validated residual efficiency treatment.
4. The 4.71-t fiducial-volume acceptance and position dependence are represented, not replaced by the uniform active-volume proxy.
5. Skin/OD veto tagging and the science/prompt/delayed sample signal expectations are addressed.
6. The required background PDFs, rate constraints, and nuisance covariance are available or a clearly scoped non-official likelihood study is explicitly approved.

Until then, report rate-level and 2D response predictions with their exact acceptance definition and provenance; do not call them official LZ selected signal PDFs or exclusion limits.

## 6. Public-paper source anchors

- [LZ 2026 extended-NR paper, arXiv:2609.02823](https://arxiv.org/abs/2609.02823): SS/data-analysis/FV requirement and exact WS ROI; 4.71-t FV; prompt/delayed veto definitions; three-sample likelihood; Supplemental Fig. S2 cumulative efficiency.
- [LZ EFT/NREFT first-science-run analysis, arXiv:2404.17666](https://arxiv.org/abs/2404.17666): the 2026 paper identifies this as the starting analysis whose selections remain unchanged apart from ROI, FV, and sideband handling.
