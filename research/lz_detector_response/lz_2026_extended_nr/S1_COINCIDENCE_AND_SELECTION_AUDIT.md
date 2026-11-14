# LZ 2026 NR response, S1 coincidence, and event-selection audit

Date: 2026-11-15  
Status: **pre-selection signal prediction only; final event selection and profile likelihood are not authorized**

This note separates three objects that must not be conflated:

1. The NEST conditional detector-response shape in \((S1_c,\log_{10}S2_c)\).
2. The published one-dimensional, energy-dependent final-ROI signal efficiency.
3. The complete LZ event selection and three-sample likelihood.

The current 2D response is a meaningful detector-observable-space milestone, but it is not yet an official post-selection LZ signal PDF.

## 1. Current 2D artifact: what is actually archived

The current Library artifact is \`lz_nr_conditional_2d_pdf.json\`. Its recorded metadata are:

| Item | Archived value |
|---|---|
| NEST commit | \`541b6430dae6ea289cf110c99f174a9187f7fdee\` |
| Families | \`generic\`, \`ws2024\`, \`eft2024\`, \`tableS5\` |
| Generated events | 200,000 per family |
| True NR-energy prior | Uniform, 0.1–330 keV |
| Position prior | Uniform active-TPC cylinder proxy |
| True-energy binning | 10 keV |
| \(S1_c\) binning | 10 phd |
| \(\log_{10}S2_c\) binning | 0.02 dex |
| Stored observables | Corrected \(S1_c\), corrected \(S2_c\) |
| Separate S1-coincidence flag | Not stored |
| Raw \(S2\) in phd | Not stored |
| Event-level position and cut flags | Not stored |

The artifact itself states that its sparse 2D distributions are conditional on positive reconstructed observables and are not an official post-selection PDF.

### 1.1 Global positive-observable accounting

The JSON stores one \(n_{\rm generated}\) per family and \(n_{\rm valid}\) in each true-energy bin. Summing the per-bin valid counts gives:

| Family | Generated globally | Sum of per-bin \(n_{\rm valid}\) | Global positive-observable fraction |
|---|---:|---:|---:|
| generic | 200,000 | 197,458 | 98.729% |
| ws2024 | 200,000 | 196,972 | 98.486% |
| eft2024 | 200,000 | 197,708 | 98.854% |
| tableS5 | 200,000 | 197,639 | 98.8195% |

These are **global positive-observable fractions only**. They are not the S1 coincidence efficiency, not an energy-dependent acceptance curve, and not the final LZ selection efficiency. Because the per-energy-bin generated denominator is absent, \(n_{\rm valid}(E_R)/n_{\rm generated}(E_R)\) cannot be reconstructed.

The sparse PDF in each energy bin is normalized conditionally over the retained positive-observable sample. The artifact therefore provides a response-shape estimate conditional on successful positive S1/S2 reconstruction, not the probability that an NR event is accepted.

Do not multiply the global fraction above by the published LZ final-ROI efficiency. The global fraction is not energy-resolved and would risk double-counting detector losses already included in the published final-efficiency curve.

## 2. NEST source-level S1 coincidence audit

The pinned NEST commit is a descendant of the NEST v2.4.5beta release: GitHub's commit comparison reports 23 commits ahead and zero behind. This is consistent with the LZ 2026 paper's stated use of tuned NEST v2.4.5; it is not the old v2.4.0 model.

Sources:

- [Pinned NEST LZ WS2024 detector configuration](https://github.com/NESTCollaboration/nest/blob/541b6430dae6ea289cf110c99f174a9187f7fdee/include/Detectors/LZ_WS2024.hh)
- [Pinned NEST S1 implementation](https://github.com/NESTCollaboration/nest/blob/541b6430dae6ea289cf110c99f174a9187f7fdee/src/NEST.cpp)
- [Pinned NEST event driver](https://github.com/NESTCollaboration/nest/blob/541b6430dae6ea289cf110c99f174a9187f7fdee/src/execNEST.cpp)
- [Pinned NEST analysis defaults](https://github.com/NESTCollaboration/nest/blob/541b6430dae6ea289cf110c99f174a9187f7fdee/include/NEST/analysis.hh)

In \`LZ_WS2024.hh\`, the detector initialization contains:

| NEST parameter | Value | Meaning |
|---|---:|---|
| \`sPEthr\` | 0.10 phe | single-photoelectron pulse-area threshold |
| \`sPEeff\` | 1.0 | single-photoelectron efficiency setting |
| \`sPEres\` | 0.338 | single-photoelectron resolution |
| \`P_dphe\` | 0.214 | double-photoelectron probability |
| \`coinWind\` | 150 ns | S1 coincidence window |
| \`coinLevel\` | 3 | required PMT multiplicity |
| \`numPMTs\` | 481 | active PMT count used in the coincidence model |

\`SetEFT2024Configuration()\` changes the yield and gain settings (including \(g_1=0.1104\), \(g_{1,\rm gas}=0.07753555\), \(s2_{\rm thr}=120\) phe, and the EFT2024 yield vectors); it does not overwrite the inherited S1 coincidence parameters above. Thus, **if** the compact driver instantiated this LZ detector class and called \`SetEFT2024Configuration()\`, its NEST S1 model inherited the three-PMT, 150-ns coincidence configuration.

That conditional statement is not yet proof of the exact current run configuration: the C++/Python driver and build invocation that produced the JSON have not been recovered into the repository. The family label and pinned commit alone do not prove which configuration setter and calculation mode the driver actually called.

### 2.1 What NEST actually returns

In the pinned \`src/NEST.cpp\` implementation:

- The integer S1 spike count is saved in \`scintillation[8]\` for external LZLAMA coincidence accounting.
- The code evaluates the probability that the detected spikes satisfy the configured PMT coincidence level.
- The coincidence decision is sampled; when the coincidence fails, the S1 pulse observables are assigned negative signs as below-threshold/failure flags.
- The event driver documents \`scint[8]\` as the post-coincidence-window, single-PE-efficiency hit count.

The sign of the S1 observable is therefore important. Taking \(|S1_c|\), discarding negative values before recording a cutflow, or saving only a positive \(S1_c\) histogram destroys information needed to audit the coincidence acceptance.

The default NEST analysis setting \`PrintSubThr=1\` requests retention of sub-threshold events in the event output. The compact 2D artifact nevertheless keeps only positive reconstructed S1/S2 entries. The original event-level sign and the separate coincidence count were not retained in the JSON.

**Required rerun fields:** save, per event, the raw and corrected S1 quantities, the S1 spike/PMT multiplicity field (\`scint[8]\`), an explicit S1-coincidence pass flag, and the signed S1 observables before any positive-only filtering.

## 3. NEST thresholds are not the LZ analysis ROI

The NEST detector-level threshold and the published LZ analysis selection are different layers.

For the EFT2024 NEST configuration, \`s2_thr=120\` is in phe. The published LZ WS ROI separately requires uncorrected \(S2>645\) phd and corrected \(S2_c\) in its stated range. The NEST threshold must not be substituted for the LZ analysis cut.

The pinned NEST event driver exposes distinct quantities for raw and corrected S2. The rerun must preserve both:
- raw \(S2\) in phd, for the \(S2>645\) phd condition;
- corrected \(S2_c\) in phd, for the \(\log_{10}S2_c\) ROI.

The current JSON contains only corrected \(S2_c\), so the raw-S2 threshold cannot be applied or audited from this artifact.

## 4. Official LZ 2026 selection conditions

Primary reference: LZ Collaboration, [arXiv:2609.02823v1](https://arxiv.org/abs/2609.02823), including its Supplemental Material and Fig. S2. The paper states that the analysis selections are carried over from the earlier WS2024 analysis except for the ROI, fiducial volume, and sideband handling.

### 4.1 WIMP-search ROI

| Observable | Official condition |
|---|---|
| \(S1_c\) | \(3\)–\(600\) phd |
| Uncorrected \(S2\) | \(>645\) phd |
| \(S2_c\) | \(10^{2.75}\)–\(10^{4.15}\) phd |

The current 2D JSON can impose the \(S1_c\) and \(S2_c\) coordinate ranges as a shape-level diagnostic, but cannot impose the raw \(S2>645\) phd cut.

### 4.2 Fiducial volume

The selected LXe mass is \(4.71\pm0.08\) tonnes. It is not a simple cylinder:

- the radial boundary depends on depth and azimuth;
- the contour is designed to limit expected wall-background counts;
- the contour maintains at least 8.0 cm stand-off from the true wall and 6.0 cm from the reconstructed wall;
- the upper boundary is 12.8 cm below the gate and the lower boundary is 9.0 cm above the cathode.

The current uniform active-TPC cylinder proxy is not the official FV. A response averaged over that proxy cannot be promoted to an FV-conditioned response without a position-aware reweighting or rerun using the actual FV geometry and position-dependent response.

### 4.3 Single-scatter and S1/S2 reconstruction

A science candidate must be classified as a single scatter: one reconstructed S1 preceding one reconstructed S2. The earlier WS2024 analysis describes the S1 pulse classification requirement as at least three PMTs recording coincident photons. Its measured SS S1-identification efficiency is above 90% across the relevant S1 sizes and reaches 100% for S1 above 35 phd (about 8 keV). The S2 splitting probability is below 1% on average for pulses relevant to the analysis.

Those calibration-derived efficiencies must not be replaced by an assumption that every generated single-site NR automatically passes the SS reconstruction. The current NEST response artifact does not contain pulse multiplicity or an SS reconstruction flag.

### 4.4 Trigger, data quality, and veto samples

The WS2024 data-acquisition trigger is based primarily on S2 and has a reported 95% efficiency for S2 pulses corresponding to 3.5 extracted electrons. The published final NR efficiency curve is cumulative and includes, in sequence, the S2 trigger, S1 threshold, SS reconstruction and analysis cuts, and the final WS ROI.

The 2026 analysis also partitions events into three samples:

- **science:** no signal in either veto system;
- **prompt veto:** Skin signal \(>2.5\) phd within \(\pm0.25\,\mu{\rm s}\) of TPC S1, or OD signal \(>4.5\) phd within \(\pm0.3\,\mu{\rm s}\);
- **delayed veto:** Skin or OD signal above 300 or 200 keV, respectively, within 600 \(\mu{\rm s}\) of TPC S1 but outside the prompt window.

A TPC-only NEST response simulation does not generate the Skin/OD activity needed to classify these samples. The complete LZ likelihood uses the science, prompt-veto, and delayed-veto samples jointly; the current 2D response contains only a TPC-observable distribution.

## 5. How to use the published 1D efficiency without double counting

The archived LZ Fig. S2 curve is the **final, cumulative NR efficiency for the WS ROI**, not an isolated S1-coincidence efficiency. The existing AFH-7/Hybrid-9 rate-level fold applies this curve once to the pre-detector recoil spectrum.

Therefore:

1. Keep the NEST 2D PDF as a conditional observable-space shape.
2. Do not multiply the global \(n_{\rm valid}/n_{\rm generated}\) fraction by the published final efficiency.
3. Do not multiply an extra S1-coincidence or trigger factor on top of the final Fig. S2 curve unless the efficiency definition is first decomposed to prove that the factor is absent.
4. Do not label the resulting 2D density as post-selection until the raw-S2, FV, SS, data-quality, veto, and ROI mapping is closed.

The gray Fig. S2 envelope is retained as a detector-systematic range; the publication does not assign a confidence level to that envelope. It must not be relabeled as a Gaussian \(1\sigma\) band without an external justification.

## 6. Required event-level cutflow for a complete audit

The NEST rerun must preserve, at minimum:

| Stage | Required per-event information |
|---|---|
| Generation | event ID, true \(E_{\rm NR}\), event weight, random seed |
| Position | true \(x,y,z\), reconstructed \(x,y,z\), drift time |
| S1 | raw S1 phe/phd, corrected \(S1_c\), signed S1 values, \`scint[8]\`, explicit coincidence pass |
| S2 | raw S2 phd, corrected \(S2_c\), extracted-electron count, signed/threshold status |
| Pulse reconstruction | number of S1 candidates, number of S2 candidates, S2 splitting flag, SS classification |
| Trigger | trigger decision and trigger-efficiency weight |
| Analysis | data-quality flags, S1/S2 ROI flags, FV flag |
| Veto | Skin prompt/delayed flags, OD prompt/delayed flags, final science/prompt/delayed category |

For each true-energy bin, archive the cutflow counts separately:
\[
N_{\rm gen},\quad
N_{\rm S1\,coin},\quad
N_{\rm S2\,threshold},\quad
N_{\rm trigger},\quad
N_{\rm SS},\quad
N_{\rm ROI},\quad
N_{\rm FV},\quad
N_{\rm science/prompt/delayed}.
\]
The denominator at every stage must be the preceding stage's numerator. Save both absolute counts and conditional efficiencies. Do not infer a cutflow from normalized 2D histograms.

The current driver source and its exact build/run command have not yet been recovered. The source-call verification and event-level rerun are therefore open; this document records the public NEST implementation and the missing evidence, not a claim that the existing simulation has passed the full selection.

## 7. 5-keV versus 1-keV recoil-grid convergence

The natural-xenon halo-folded spectrum is the grid relevant to the detector pipeline. This is distinct from the fixed-speed Xe-131 diagnostic grid.

The archived 5-keV spectrum has:
- 5, 10, ..., 270 keV in the LZ-sensitive fine region;
- 280, 300, ..., 800 keV in the high-energy diagnostic region;
- selected extra points at 101, 267, and 542 keV;
- 84 recoil-energy points per benchmark/scenario.

The new 1-keV runner retains the same high-energy 20-keV grid and selected anchors, but uses 5, 6, ..., 270 keV in the fine region, giving 294 points per benchmark/scenario. The two grids share all 84 archived coarse nodes.

The comparison:
- verifies exact common-node agreement for the pre-detector natural-xenon rate and weighted kernel;
- integrates the raw rate and its product with the published central/lower/upper final-ROI efficiency using the exact analytic integral for piecewise-linear inputs;
- compares the total 5.4–269.9 keV ROI yield and the 225–269.9 keV candidate-tail diagnostic;
- reports the spectral peak position and height;
- keeps the four particle benchmarks and both AFH-7/Hybrid-9 scenarios.

The same particle parameters, truncated-SHM parameters, and quadrature orders as the archived 5-keV run are used. The AFH density matrices are reused; direct AFH finite sums are evaluated at the new exact spatial-\(q\) recoil nodes. This is not a regeneration of the nuclear density matrices.

Local Windows runner:

~~~powershell
.\research\afh_default_density_natural_xenon_halo\run_1kev_recoil_grid_convergence.ps1
~~~

Outputs are written to:
- \`research/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_continuous_1keV_2026-11-15/\`
- \`research/afh_default_density_natural_xenon_halo/results/recoil_grid_convergence_2026-11-15/\`

**Execution status:** comparator, tests, and local runner are prepared. The 1-keV natural-xenon run and numerical comparison have not yet been executed. No grid-convergence PASS is claimed.

A separate resolution issue remains: the NEST conditional 2D response is currently binned in 10-keV true-energy intervals. A 1-keV recoil-rate grid does not by itself establish 1-keV resolution of the 2D response. Energy interpolation or finer NEST response generation must be separately validated before using the 2D shape in a selected signal model.

## 8. Release gate

Until the recoil-grid comparison and the complete selection audit pass:

- retain the 2D result as **pre-selection signal prediction**;
- do not call it the official LZ post-selection signal PDF;
- do not construct the final science/prompt/delayed sample PDFs;
- do not start the final profile likelihood;
- do not report a 90% CL exclusion or sensitivity limit.

The rate-level efficiency fold remains a separate diagnostic and does not waive these gates.
