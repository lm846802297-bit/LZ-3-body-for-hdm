# LZ detector-response research archive

This directory contains the public LZ 2026 detector-response inputs, NEST
response simulations, three-body two-dimensional folds, rate-level efficiency
folds, numerical audits, and reproducibility records. The detailed index for
the extended NR/ER response study is in
[`lz_2026_extended_nr/README.md`](lz_2026_extended_nr/README.md).

## Current status (2026-11-16)

- The pinned NEST `541b643` `SetEFT2024Configuration()` is a well-supported
  public configuration candidate, not confirmation of the exact LZ
  collaboration production build.
- Keep the **1-keV full-range recoil grid** as the numerical reference. The
  independent full-range 1/5-keV study fails the 1% 2D-TV gate (1.4812% for
  EFT2024 and 1.4681% for Table S5), even though its accepted-rate comparison
  passes. The restricted black-support 1/5-keV and high-tail 0.5-keV checks
  do not override this full-range result.
- The paired S1 study uses ten independent seeds and 4.7 million unique
  events. Its 100,000-replicate seed-cluster bootstrap and 1,024 exact paired
  label swaps show that the black 360-keV point TV below 1% is not a robust
  equivalence claim; the red 200-keV mode-shape difference is statistically
  detectable after Holm correction.
- The NEST/WS-ROI 2D map remains an intermediate detector-response proxy,
  not the official waveform-level selected-event PDF. DAQ trigger, waveform
  S1 timing, SS/data-analysis cuts, official FV, Skin/OD, live-time migration,
  joint detector-systematic covariance, backgrounds, and profile likelihood
  are not complete.

## Contents

- `lz_2026_extended_nr/lz_2026_figS2.svg`: vector source figure retained for
  the efficiency digitization.
- `lz_2026_extended_nr/lz_2026_nr_efficiency_digitized.csv`: 303-point
  digitization of the central final WIMP-search ROI efficiency and the gray
  uncertainty envelope.
- `lz_2026_extended_nr/lz_2026_nr_efficiency_metadata.json`: source,
  extraction method, axis calibration, checks, and digitization caveats.
- `lz_2026_extended_nr/rate_level_event_yields/`: archived
  efficiency-weighted expected event yields and their calculation metadata.
- `lz_2026_extended_nr/lz_2026_nest_nr_mean_yield_parameters.json`: exact
  LZ 2026 Supplemental Table S5 NR mean-yield parameter set and NEST source pin.
- `lz_2026_extended_nr/lz_2026_nr_mean_yield.py`: independent Python port
  of the NEST NR mean-yield equations, including the high-energy p(E) branch.
- `LZ_2026_PUBLIC_INPUTS_AUDIT.md` and `P0_NEST_AND_WIDTH_CLOSURE_STATUS.md`:
  public-input availability and P0 closure status.
- `lz_2026_extended_nr/LZ_2026_ENERGY_RESOLVED_SELECTION_MC_AND_BLACK_TAIL_AUDIT.md`:
  artifact-level weighted-MC uncertainty, black-tail band decomposition, and
  independent-seed 1/5/0.5-keV grid checks.
- `tests/test_lz_2026_nr_mean_yield.py`: unit tests for the isolated mean-yield port.

## Provenance and interpretation

The efficiency curve is digitized from LZ Collaboration, arXiv:2609.02823v1,
Fig. S2 (PDF page 14). The corresponding HEPData release is
[doi:10.17182/hepdata.182472.v1](https://doi.org/10.17182/hepdata.182472.v1).
The metadata records the PDF SHA-256, vector-path extraction procedure, and
the comparison with an independent digitization.

The gray band is retained as a detector-systematic range. LZ does not assign
a confidence level to that envelope. The curve is not rescaled to force exact
agreement with the rounded published mean efficiency.

### Latest energy-resolved selection audit

The latest artifact-level selection bridge and weighted-MC diagnostic are
documented in
[`LZ_2026_ENERGY_RESOLVED_SELECTION_MC_AND_BLACK_TAIL_AUDIT.md`](lz_2026_extended_nr/LZ_2026_ENERGY_RESOLVED_SELECTION_MC_AND_BLACK_TAIL_AUDIT.md).
The restricted 5-keV black-support comparison passes the 1% accepted-rate
and 1% mean-map TV point-estimate gates using three independent seeds per
grid; the 0.5-keV check is restricted to the high-energy tail. A separate
independent full-range 1/5-keV comparison fails the 1% 2D-TV gate, so 1 keV
remains the global reference grid. These are numerical checks for the current
NEST proxy, not validation of the complete LZ selection response. The report
retains the distinction between NEST's approximate S1 coincidence/S2 pulse
threshold and the official DAQ, SS/data-analysis, FV, and veto selections.

The event-level pilot uses the Table S5 NR mean-yield vector with the public LZ WS2024 detector class and compares its tuned NR width vector with generic NEST defaults. Its first paired 248-keV run is a one-energy, one-position sanity check, not a full reproduction of the published NR band. The paper's Fig. 2 band is constructed from flat-in-energy NR spectra and evaluated at fixed S1c. The historical flat-spectrum pilot tests both the 5.4–269.9 keV analysis-window prior and approximately 0.1–330 keV AmBe range at the candidate position, but used hybrid Table-S5/WS2024 inputs and is superseded. The primary public candidate is now NEST commit 541b643's `SetEFT2024Configuration()`; full-S1c NR and ER bands plus conditional 2D PDFs are documented in `LZ_2026_NR_ER_FULL_RESPONSE_CANDIDATE_REPORT.md`. The uniform active-TPC position distribution remains a proxy, not the actual D-D/AmBe calibration-source distribution.

The rate-level event-yield files fold the continuous natural-xenon spectra
with the digitized central efficiency and its gray envelope over the
5.4–269.9 keV analysis window. They are rate-level diagnostics only: they do
not include the two-dimensional S1c/log10(S2c) signal PDFs, NEST nuisance
covariance, energy-resolution smearing, background likelihood, or profile
likelihood. They are not a 90% confidence-level exclusion and are not the
official LZ likelihood.

### AFH-7 / Hybrid-9 rate-level archive

- `lz_2026_extended_nr/afh7_hybrid9_rate_level_yields/`: AFH-7 and Hybrid-9 continuous-spectrum folds, including CSV, JSON provenance, and SHA-256 manifest. Four benchmarks times two scenarios give eight output rows.
- The fold is generated by `research/three_body_calculation_and_validation/fold_lz_2026_afh_hybrid9_rate_level.py`; regression tests are in `research/three_body_calculation_and_validation/tests/test_lz_2026_afh_hybrid9_rate_level_fold.py`.
- The end-to-end workflow passed in [GitHub Actions run 43527099172](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43527099172).

AFH-7 uses official AFH v6.0 default-density responses for the seven supported isotopes. Xe-124 and Xe-126 are omitted without renormalizing the other abundances. Hybrid-9 uses Helm only for those two missing isotope responses; it is a labelled diagnostic fallback, not a full nine-isotope AFH result. Neither fold recomputes the AFH nuclear responses or the archived three-body kernel.

See the main study report and
`research/three_body_calculation_and_validation/fold_lz_2026_rate_level.py` for the
calculation and limitations.


## Historical NR event-level response pilot

The next stage after the Table S5 mean-yield validation is a direct event-level
NEST comparison. The driver calls the pinned NEST implementation in this order:

1. `FullCalculation(NR, ...)` to obtain fluctuated intrinsic quanta;
2. `GetS1(..., S1CalculationMode::Full)` to simulate the S1 response;
3. `GetS2(..., S2CalculationMode::Full)` to simulate the integrated S2 area response.

The code does **not** replace the detector response with the shortcut
`S1 = g1 * Nph` or `S2 = g2 * Ne`.

Two NR fluctuation baselines are compared while keeping the 2026 Table S5
15-parameter mean-yield vector and the LZ WS2024 detector class fixed:

- `ws2024`: the calibration-tuned NR width vector in
  `LZ_WS2024.hh`;
- `generic`: the generic NEST default NR width vector at the pinned commit.

The simulation uses 2,000 events per energy by default at
5.4, 10, 50, 74.7, 100, 150, 200, 248, and 269.9 keV. Events are placed at
the detector's central `dtCntr` reference depth, with x=y=0 and no position
smearing. The same seed is used for both width baselines at each energy.

### Run locally on Windows

From a Visual Studio 2022 Developer PowerShell (or another shell in which
CMake can find an MSVC C++17 toolchain), run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
cd <path-to-repository>\research\lz_detector_response
.\run_lz_2026_nr_event_response.ps1
```

Optional pilot size and seed:

```powershell
.\run_lz_2026_nr_event_response.ps1 -EventsPerEnergy 5000 -Seed 20261115
```

Prerequisites: Git, CMake, a C++17 compiler (Visual Studio 2022 Build Tools
with the Desktop development with C++ workload is recommended), and Python
3.10 or newer. The script checks out the exact NEST commit, configures and
builds NESTCore, compiles the event driver, runs both baselines, and writes
raw CSV plus JSON/CSV summaries outside the repository under
`%LOCALAPPDATA%\LZ-3-body-for-hdm\nr_event_response` by default.

### Observable and limitations

- `S1c` is the signed corrected-phd value returned by `GetS1()[5]`.
- `S2c` is the signed corrected-phd value returned by `GetS2()[7]`.
- NEST uses the sign to flag S1 coincidence failure and S2 threshold failure;
  the raw signed values are retained in the CSV.
- NEST tests the S2 threshold before lifetime correction: the raw 783 phe threshold is 644.98 phd after DPE conversion, while the reference-depth corrected-S2c boundary is about 683.72 phd. Both are recorded separately; the sign flag from GetS2 is authoritative.
- S1 uses the full PMT-level S1 mode. S2 uses NEST's integrated `Full` mode,
  not the waveform mode; this retains extraction, lifetime, EL gain, DPE/SPE
  and pulse-area fluctuations, but does not create the detailed S2 waveform
  or its waveform-mode diffusion/electron-train treatment.
- The detector class is an LZ SR3/WS2024 candidate, not confirmed as the exact
  2026 extended-NR configuration. The mean-yield vector is updated to 2026
  Table S5; spatial response maps and the complete analysis selection are
  not reproduced.
- The output is an NR detector-response pilot, not the official LZ signal PDF,
  background model, nuisance likelihood, or exclusion.

The code and assumptions are documented in
`lz_2026_extended_nr/LZ_2026_NR_EVENT_RESPONSE_PILOT.md`.


## NEST configuration status

The HEPData v1 ZIP is a 46-table export and contains no separate NEST configuration resource. A separate public LZ-specific EFT2024 configuration candidate is available in NEST commit `541b643`; it is not in a tagged NEST release and its identity with the exact LZ 2026 production build is not proven. Use the provenance report and machine-readable JSON before selecting parameters. Earlier Table-S5-plus-WS2024-width pilot results are historical hybrid checks, not the primary EFT2024 response.


## Historical first 10-keV three-body NR 2D response fold

This section records the original 200,000-event/family, 10-keV-bin pilot; it is superseded for current grid work by the stratified 1/5/10-keV response in the next section. The first end-to-end pre-selection fold is documented in
`lz_2026_extended_nr/LZ_2026_THREE_BODY_NR_2D_RESPONSE_FOLD_REPORT.md`.

- `cpp/lz_2026_nr_full_calibration_band.cc`: event-level NEST response sampler; now accepts explicit recoil-energy minimum and maximum.
- `fold_lz_2026_three_body_2d_response.py`: constructs per-energy-bin response probabilities and folds the archived continuous natural-xenon three-body spectra into `(S1c, log10(S2c))) cell intensities.
- `tests/test_lz_2026_three_body_2d_response.py`: numerical tests for exact piecewise-linear rate integration, partial ROI bins, and probability-mass preservation.
- `.github/workflows/lz-2026-three-body-2d-response-fold.yml`: reproducible pinned-NEST workflow.

The workflow passed as [run 43645345194](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43645345194). Its artifact contains four 200k-event response samples, the 2D cell-intensity CSV, and closure summaries. The 2D output is a pre-selection observable intensity. The energy-only final-ROI efficiency is deliberately kept separate because it does not specify the selected two-dimensional response and must not be double counted.

The response uses a uniform active-TPC volume proxy, not the actual calibration-source spatial distribution. It is not the official production NEST configuration, full selected-event PDF, background likelihood, or confidence interval.


## Three-body 1/5/10-keV response grid and selection audit (2026-11-15)

The stratified event-level response and grid-comparison implementation is:

- `cpp/lz_2026_nr_stratified_energy_response.cc`: generates stratified true-NR response samples with two disjoint event halves and saves signed S1/S2 flags, corrected and raw observables, and true position. Its optional `events_per_keV` argument scales event counts to each stratum's exact width, including partial terminal bins.
- `converge_lz_2026_three_body_energy_grid.py`: folds the same 1-keV response strata into 1-, 5-, and 10-keV response grids. The deterministic reaggregation gives a 5-keV point-estimate PASS and a 10-keV FAIL, but the independent full-range 1/5-keV productions fail the 1% 2D-TV gate for both NR mean-yield families. Keep 1 keV as the reference; 5 keV is not accepted as the production grid.
- `audit_lz_2026_conditional_selection_bridge.py`: compares the event-weighted NEST/WS-ROI rate with the Fig. S2 residual SS/data-analysis stage separately for EFT2024 and Table S5, without multiplying the full cumulative efficiency into the 2D map.
- `audit_lz_2026_black_tail_independent_seeds.py` and `.github/workflows/lz-2026-black-tail-independent-seeds.yml`: generate and summarize three independent full productions per grid for both EFT2024 and Table S5 black high-energy benchmarks.
- `audit_lz_2026_full_range_grid_independent_seeds.py` and `.github/workflows/lz-2026-full-range-grid-independent-seeds.yml`: compare three independently generated 1-keV and 5-keV full-range samples for EFT2024 and Table S5, with disjoint seeds and a common 4,000 events/keV density.
- `lz_2026_extended_nr/LZ_2026_THREE_BODY_RESPONSE_SELECTION_AUDIT.md`: records the exact acceptance definitions, approved grid gate, S1 Parametric limitation, Fig. S2 overlap, and remaining selection gaps.
- `lz_2026_extended_nr/LZ_2026_THREE_BODY_EVENT_WEIGHTED_FOLD_AUDIT.md`: records the event-weighted fold, residual-efficiency factorization diagnostic, and why the black high-energy benchmark is not yet closed.

The initial 2026-11-14 workflow is [run 43648916347](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43648916347). The cutflow-instrumented run is [43656826463](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43656826463), artifact ID `14137998811`, SHA-256 `e5005d73b57b86c05a5af9e999782df765fa6db870333320030863897a1ecdea`. The combined grid/event-weighted run is [43680164807](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43680164807), artifact ID `14147354124`, SHA-256 `0f2bf102f440245d98a10462a42fa9625b26e28124e7e2096b3ca8dfa90533b2`. The selection-stage closure is [43681260816](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43681260816), and the expanded rerun is [43682860360](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43682860360), artifact ID `14149540926`, SHA-256 `0167a2c74e179215584b573097dce28dc8ea12672ecebd826d7d98362634af27`. The deterministic reaggregation of 1-keV response strata gives a 5-keV point-estimate difference of 0.5131% in accepted rate and 0.8896% in 2D TV; 10 keV fails at 1.2146% and 2.4649%. This is not an independent 5-keV Monte Carlo. The independent full-range study [run 43699011757](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43699011757), raw artifact 14155573365 (981,003,582 bytes), generated three independent 1-keV and three independent 5-keV productions for each of EFT2024 and Table S5. It used disjoint seed sets (1 keV: 20261132/34/36; 5 keV: 20261133/35/37), 4,000 events per keV including the partial terminal bins, and 12,696,000 events total. Across 16 benchmark/nuclear/mode comparisons per family, maximum rate differences are 0.6450% (EFT2024) and 0.2016% (Table S5), both below 1%; maximum mean-map TV distances are 1.4812% and 1.4681%, both above 1%. The failures are driven by the black (m_s=360) keV benchmark; red/green/blue remain around 0.75–0.78%. The black cross-grid TV values are smaller than the largest seed-to-seed pairwise TV values (about 2.5–2.9%), so three seeds do not isolate a stable systematic grid bias, but the pre-agreed point-estimate gate still fails. A summary-only export was independently downloaded and inspected from [run 43699599124](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43699599124), artifact 14155488034, ZIP SHA-256 `9439cb84533beb4aed9104fa529ab9d132af573b9feac19db255b1f81d08b1bf`. **Decision: retain 1 keV as the numerical reference; do not promote 5 keV to the production grid.** The independent 0.5/1-keV black-tail check is a separate local refinement result and does not override this full-range 1/5-keV finding.

The new `nest` and `ws_roi` modes must be distinguished:
- `nest`: NEST Parametric S1 coincidence and NEST S2-threshold pass;
- `ws_roi`: `nest` plus \(3\leq S1_c\leq600\) phd, raw \(S2>645\) phd, and \(2.75\leq\log_{10}S2_c\leq4.15\).

The Parametric S1 mode uses a PMT-occupancy probability with threefold level and 481 PMTs, but does not explicitly apply the configured 150-ns coincidence window. The response also uses a uniform active-TPC cylinder prior and passes true positions as the position-correction coordinates. Trigger, waveform-level S1 timing, SS reconstruction, data-analysis cuts, the official 4.71-tonne fiducial volume, Skin/OD veto partition, and live-time treatment remain absent.

The \(ws\_roi\) output is therefore a **NEST-level plus WS-ROI intermediate three-body signal prediction**, not the final LZ selected signal PDF. See the quantitative audit before using these outputs. Do not multiply the full Fig. S2 cumulative efficiency into this 2D intensity; the selections overlap, and the 2D migration information is not supplied by the scalar efficiency curve.


### NEST 2.4.5 release lineage and EFT2024 configuration provenance

The source-level comparison between the public v2.4.5beta tag and the later LZ-specific development branch is documented in [LZ_2026_NEST_RELEASE_LINEAGE_AUDIT.md](lz_2026_extended_nr/LZ_2026_NEST_RELEASE_LINEAGE_AUDIT.md). The 2026 LZ paper's double-skew-Gaussian ER model and high-energy NR p(E) extension are absent from the public v2.4.5beta tag at commit `19bc9bc`; the physics features and EFT2024 configuration were added later, with the LZ configuration first appearing at `307fb27` before the paper's arXiv submission. The audited `541b643` commit adds getters/storage only relative to `307fb27`. This makes it a strong public candidate, not proof of the exact collaboration build. The candidate's derived g1=0.1104 and g2=34.5263 agree with the paper's quoted gains within 0.20σ and 0.024σ, respectively. See the [machine-readable candidate record](lz_2026_extended_nr/lz_2026_nest_eft2024_configuration_candidate.json).

The rounded Table S5 vector and the public full-precision EFT2024 vector
are separate NR response hypotheses, not interchangeable precision variants.
The direct NEST C++ cross-check [run 43696267500](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43696267500)
passed 528 Python/C++ scalar comparisons for both vectors (worst scaled
absolute difference below \(3.4\times10^{-16}\)). At 269.9 keV, Table S5
relative to EFT2024 changes the mean photon yield by −7.5301%, electron yield
by +0.3846%, and total quanta by −7.1019%; the high-energy \(p(E)\) extension
is identical. Thus the rounded mean-yield table can materially alter S1 and
the high-energy ROI acceptance. Keep both families separate. See the
[quantitative source audit](lz_2026_extended_nr/LZ_2026_NEST_RELEASE_LINEAGE_AUDIT.md#61-quantitative-effect-of-the-printed-table-s5-rounding).

### Full-range NR band and NR fluctuation-vector audit

The separate full-range flat-energy NR band study is documented in
[LZ_2026_NR_FULL_BAND_PARAMETER_SENSITIVITY_AUDIT.md](lz_2026_extended_nr/LZ_2026_NR_FULL_BAND_PARAMETER_SENSITIVITY_AUDIT.md).
It compares the public EFT2024 candidate, rounded Table S5 mean yields,
EFT2024 means with WS2024/generic NR fluctuation vectors, WS2024, and
generic NEST.

A source-level check of NEST GetQuanta shows that NRERWidthsParam indices
0–5, 11, and 12 control NR quanta fluctuations. In particular, EFT2024
p2 = −0.707 gives lambda_Chen = 0.293 and omega_NR = 0 after clamping,
whereas WS2024/generic p2 > 0 gives lambda_Chen = 1 and nonzero omega_NR.
Thus the NR fluctuation-vector swap changes the physical recombination
variance model, not merely a width.

**Drift audit:** the first full-band driver used a detector-centre drift
velocity for every event. The pinned LZ detector class actually returns a
constant 96.5 V/cm at every position, so the old and corrected outputs are
bitwise identical for the present configuration. The corrected driver now
calculates the velocity event by event, writes drift distance/time/speed, and
the summarizer checks kinematic closure. This makes the code safe to extend
to a future nonuniform field map. The corrected run includes rounded Table S5.

The corrected run is [43660830473](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43660830473),
artifact 14139657582, with 12 samples and 90 band comparisons. The
bootstrap-enabled run is [43661274708](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43661274708),
artifact 14139997390, ZIP SHA-256
1f053db6e3d49863c8b36b6a753d4e4eed0410a8530e73d98eb62d771f4bd967.
It archives 2,000-replica finite-MC bootstrap intervals for all 12 samples.
The full tables and interpretation are in the linked audit report.

The energy prior remains uniform in true NR energy and the spatial prior is
uniform in the active TPC (or fixed at the candidate position). These are
diagnostic proxies, not the official D-D/AmBe calibration priors or a
collaboration production response. This study is not a likelihood input.

Implementation:
- `cpp/lz_2026_nr_flat_spectrum_eft2024.cc` — event-level NEST response driver with event-local drift velocity.
- `summarize_lz_2026_nr_flat_band_eft2024.py` — 5-phd band summaries and model comparisons.
- `bootstrap_lz_2026_nr_full_band_candidate.py` — deterministic finite-MC bootstrap.
- `.github/workflows/lz-2026-nr-eFT2024-full-band.yml` — pinned NEST build, event generation, closure checks, and artifact upload.

### ER far-tail support audit

The ER full-band pilot gives a central-band offset of about −6.7 sigma-equivalent,
but the empirical Monte Carlo has no support at the observed candidate point:
in the 540–545 phd S1c bin, the EFT2024 sample's minimum S2c is 29,595 phd,
whereas the observed event has S2c = 9,267.53 phd. There are zero events at
or below the candidate S2c and zero events in the candidate's 10-phd by
0.02-dex 2D histogram cell. Thus the 6.7-sigma-equivalent band displacement
is not a measured ER tail probability, and the sparse ER PDF cannot be used
directly as a likelihood density at the candidate. See
[LZ_2026_ER_TAIL_SUPPORT_AUDIT.md](lz_2026_extended_nr/LZ_2026_ER_TAIL_SUPPORT_AUDIT.md).

The corrected ER run is [43662363556](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43662363556),
artifact 14140966494, SHA-256
a2a138d262245e811c94b8bc41d76f4af16c53196d1a12adea044bf66a9f7bc1.
It includes local-drift closure and deterministic bootstrap output.

### Rate-level selection-stage closure

An independent exact integration of the four vector-extracted Fig. S2
cumulative curves against all eight benchmark/nuclear-response spectra
reproduces the stored rate-level expected counts to floating-point
precision. Over the signal support (35–269.9 keV), the trigger and S1
threshold curves are unity; the SS/data-analysis stage is 95.50–95.58%.
The high-energy black benchmark is further reduced by the upper S1c ROI,
giving a total rate-level efficiency of 76.63–76.99%, compared with about
95.47–95.56% for the other three benchmarks. See
[LZ_2026_SELECTION_STAGE_RATE_LEVEL_CLOSURE.md](lz_2026_extended_nr/LZ_2026_SELECTION_STAGE_RATE_LEVEL_CLOSURE.md).
This is a one-dimensional rate-level check, not a 2D selected signal PDF. The lightweight CI passed in
[run 43681260816](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43681260816),
artifact 14148377892, SHA-256
53fa87cc4b2fdb3361e73fd65d847992b2ea2c96996891d7cfd6c10850b136b5.
The same audit also passed from the clean PR integration branch in
[run 43682717319](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43682717319),
artifact 14149346224, ZIP SHA-256
`5fdacaed77cde4a65db56801997f75e8171b6a4bb3d7ba0218be7d708cfbba0e`. The eight-row closure is unchanged.
The expanded integration-branch workflow [43682860360](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43682860360)
also runs the 0.5-keV refinement, event-weighted-fold, and selection-rate unit
tests before re-extracting Fig. S2 and closing all eight rows. It passed; artifact
14149540926, SHA-256
`0167a2c74e179215584b573097dce28dc8ea12672ecebd826d7d98362634af27`.


It closes all eight rows with maximum final-yield relative difference
\(7.02\times10^{-10}\) against a \(10^{-8}\) tolerance. The calculation is reproducible through
summarize_lz_2026_selection_stage_rates.py and its lightweight
lz-2026-selection-stage-rate-audit.yml workflow; this workflow re-extracts
Fig. S2 and validates all eight rate-level rows without rebuilding NEST.

### Complete LZ 2026 selection and three-sample likelihood audit

The updated selection audit now distinguishes the hardware S2 DAQ trigger from
the NEST S2 pulse threshold, and separates NEST's threefold PMT-occupancy
approximation from the official S1 pulse classification and single-scatter
reconstruction. It records the inherited WS2024 selection chain, the exact
2026 4.71-tonne fiducial-volume requirements, the WS ROI, prompt/delayed
Skin/OD veto definitions, and the three correlated likelihood samples:
[LZ_2026_THREE_BODY_RESPONSE_SELECTION_AUDIT.md](lz_2026_extended_nr/LZ_2026_THREE_BODY_RESPONSE_SELECTION_AUDIT.md).

The 2026 likelihood uses science, prompt-veto, and delayed-veto samples
simultaneously, with expected counts correlated through tagging-efficiency
parameters. The present 2D response has no veto-sample label and is therefore
not a complete likelihood signal model. The 2.84 tonne-year exposure already
uses the 220 live days after the published live-time exclusions; do not apply
the 81.5% live-time retention a second time.

The collaboration's official two-dimensional signal/background PDFs are
generated with BACCARAT/GEANT4 and the tuned NEST v2.4.5 response. The
one-dimensional Fig. S2 efficiency curve does not provide that 2D migration
kernel. The waveform discussion of the candidate is event-specific and is
not an extra generic NR signal cut. These are additional reasons to retain
the present NEST-level/WS-ROI map as an intermediate prediction only.

The selection audit now includes an explicit no-double-counting matrix:
NEST S1 occupancy is only an approximation to official S1 classification;
the NEST S2 pulse threshold is distinct from the hardware S2 trigger; the
WS ROI is already present in the current 2D map; and the full Fig. S2
cumulative efficiency must remain a separate rate-level calculation.
It also records a proposed 1% accepted-rate / 1% 2D-TV grid tolerance.
That tolerance is not yet approved, so the 1-keV response remains the
reference and no formal grid PASS is claimed.

### Parametric-versus-Full S1 coincidence validation

Because the three-body stratified driver uses NEST Parametric S1 mode, a paired
comparison against NEST Full S1 mode was added. [Run 43658191416](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43658191416)
completed successfully; artifact ID `14138858617`, SHA-256
`4475a152732eae45c76b8dbf4e8c4c52a476c402e3870b3f16b2fc7cfd5bd408`.
It contains 10,000 paired events in each of ten energy bins.
The same NR quanta and true event positions were passed to both modes, with
separate deterministic S1 random streams. The maximum absolute coincidence
acceptance difference was 0.25 percentage points (paired interval from a Bonferroni 95% joint Wilson construction); both modes passed all
10,000 events in every tested signal-support bin (35, 101, 210, 248, and
269.4–269.9 keV). This supports the Parametric approximation for the present
benchmark spectra, but does not replace a full LZ waveform, trigger, SS, FV,
veto, or data-quality selection model.

Implementation:
- `cpp/lz_2026_nr_s1_coincidence_mode_comparison.cc`
- `summarize_lz_2026_s1_coincidence_mode_comparison.py`
- `tests/test_lz_2026_s1_coincidence_mode_comparison.py`
- `.github/workflows/lz-2026-s1-coincidence-mode-crosscheck.yml`




### Three-body NR response fold: 1-keV reference and 0.5-keV high-energy check

The full-range three-body signal has been folded through the event-level NEST
response using the exact piecewise-linear GCN/JJ55 recoil spectra. The
1-keV response is the full-range reference; the 5/10-keV comparisons are
diagnostics only. The 0.5-keV refinement covers 225.4–269.9 keV, where the
\(m_s=360\) keV benchmark approaches the upper S1c boundary.

The combined full-range and high-energy refinement is confirmed by the
latest successful rerun [43680164807](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43680164807),
artifact 14147354124, SHA-256
0f2bf102f440245d98a10462a42fa9625b26e28124e7e2096b3ca8dfa90533b2
(437,589,152 bytes; 28 files). The earlier event-weighted fold run is
[43676553810](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43676553810),
artifact 14146333000; the latest rerun has identical numerical diagnostics.
Across 64 high-energy comparisons, the maximum 0.5-keV versus 1-keV
accepted-rate difference is 0.46895% and the maximum 2D total-variation
distance is 2.5446%. After a \(10^{-12}\) numerical tolerance, two rate
comparisons (EFT2024 black benchmark, GCN/JJ55) exceed both split-sample rate
checks; no 2D shape comparison does. This is a refinement diagnostic, not a
formal convergence PASS. The full interpretation is in
[LZ_2026_THREE_BODY_RESPONSE_SELECTION_AUDIT.md](lz_2026_extended_nr/LZ_2026_THREE_BODY_RESPONSE_SELECTION_AUDIT.md).

The 1-keV 2D intensity contains NEST Parametric S1 coincidence, NEST S2
threshold, and the WS S1c/raw-S2/S2c ROI. It is an intermediate
NEST-level/WS-ROI prediction, not the final LZ selected signal PDF. The
published final cumulative Fig. S2 efficiency is already folded separately
at rate level in
[lz_2026_rate_level_event_yields.csv](lz_2026_extended_nr/rate_level_event_yields/lz_2026_rate_level_event_yields.csv).
Do not multiply that final efficiency into the existing 2D map: the WS ROI
and some NEST acceptance are already represented, and the missing selections
do not have a validated 2D migration model.

The latest combined artifact also performs a direct event-level
\(dR/dE_R\)-weighted fold of each stratified NEST event. Within every 1-keV
true-energy stratum, the event weights are normalized to the exact
piecewise-linear three-body rate integral. Across 64 matched comparisons,
raw-rate closure is \(1.11\times10^{-15}\), the maximum weighted-versus-binned
accepted-rate difference is 0.02821%, and the maximum 2D total-variation
distance is 0.07920%. These are below the observed split-replica variations.
See [LZ_2026_THREE_BODY_EVENT_WEIGHTED_FOLD_AUDIT.md](lz_2026_extended_nr/LZ_2026_THREE_BODY_EVENT_WEIGHTED_FOLD_AUDIT.md).

The latest event-weighted fold and conditional bridge are [run 43697104437](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43697104437), artifact 14155360851, SHA-256 `682e2ba71063d6ef835b37a6d328a84ab7c609f404856aa83d56e4b875794bab` (327,668,756 bytes). I downloaded and inspected the actual artifact, including both bridge JSON files. For the black (m_s=360) keV benchmark, the rate-level factorisation is 7.625% low for EFT2024 and 13.027% high for the Table S5 hybrid; the other red/green/blue benchmarks close to within about 0.63% or better. The model-dependent opposite-sign mismatch shows that no universal scalar residual efficiency can close the black 2D response. This is a diagnostic, not an extra efficiency factor or a 2D correction. The exact production NEST/calibration response and the missing 2D SS/DA, FV, and Skin/OD migrations must be resolved before a final selected PDF.

Implementation:
- `cpp/lz_2026_nr_stratified_energy_response.cc` — stratified event-level NEST NR response.
- `converge_lz_2026_three_body_energy_grid.py` — 1/5/10-keV response fold and provenance checks.
- `compare_lz_2026_nr_high_energy_half_kev.py` — 0.5/1-keV high-energy response comparison.
- `.github/workflows/lz-2026-three-body-response-grid-convergence.yml` — pinned NEST build, samples, folds, checks, and artifact upload.


A 265-bin comparison of NEST+WS-ROI acceptance with the published final
Fig. S2 curve finds Table S5 never below the curve, while EFT2024, WS2024,
and generic are below it in 33, 19, and 74 bins, respectively. The new
rate-level bridge reinforces the model sensitivity: Table S5 overshoots the
final black benchmark by 13.0%, whereas EFT2024 undershoots it by 7.6%.
Treat the 265-bin comparison only as a plausibility diagnostic, not a strict
nested-efficiency proof or a stand-alone model-selection rule: NEST S1 coincidence/S2 pulse-threshold
flags are not identical to the official DAQ trigger/S1-threshold stages, and
the simulated spatial prior is not the official calibration/FV prior. The
Table S5 alignment is interesting, but it does not establish the exact LZ
2026 production configuration. See the detailed response-selection audit.


### Paired Parametric/Full S1 two-dimensional response (2026-11-15)

A paired NEST EFT2024 response was generated over the full three-body signal
support, 35--269.9 keV, using 2,000 events per 1-keV stratum (470,000 events
total). Both S1 modes use the same intrinsic NR quanta and true position, with
one common NEST Full S2 draw per event. The response is folded separately for
the red, green, black, and blue benchmarks and GCN/JJ55 nuclear spectra.

The 10-phd by 0.02-dex 2D map comparison gives pooled Parametric-versus-Full
TV distances of 1.64--3.85%, while the corresponding integrated WS-ROI rate
differences are only 0.0067--0.2822%. The largest shape difference is the black
\(m_s=360\) keV benchmark. The exact event-weighted split-half audit reproduces
the fold's pooled TV values with zero numerical difference; however, the
observed mode TV is only 64--75% of the within-mode split-half TV benchmark.
The two halves share one seed and are not independent-seed uncertainty
estimates or a significance test.

The NEST-stage S1 coincidence and S2-threshold acceptances are 100% in the
generated signal-support sample. The S2 marginal TV is consistent with zero
at this stage because the same S2 event is shared by both S1 modes. The
non-zero joint 2D TV therefore reflects changes in the S1c--S2c conditional
shape, not a different S2 marginal. WS-ROI selection introduces small
S2-marginal changes through the S1-dependent cuts and correlations.

The 2D TV is histogram-binning dependent: exact rebinning from 10-phd/0.02-dex
to 20-phd/0.04-dex and 40-phd/0.08-dex reduces the TV substantially. This is
a binning diagnostic, not a new Monte Carlo sample or a universal 1% gate.
The full interpretation and tables are in
[LZ_2026_THREE_BODY_RESPONSE_SELECTION_AUDIT.md](lz_2026_extended_nr/LZ_2026_THREE_BODY_RESPONSE_SELECTION_AUDIT.md).

The ten-independent-seed EFT2024 paired S1 ensemble generated 4.7 million
paired events (ten disjoint 470,000-event productions) and closed all 16
benchmark/nuclear/stage ensemble summaries plus 160 per-seed summaries.
For the WS-ROI maps, the ten-seed ensemble-mean Parametric/Full TV is
0.648--0.943%, while the mean per-seed mode TV is 1.753--2.900% and the
within-mode pairwise seed TV is 1.884--3.003%. These point estimates are
descriptive; the paired bootstrap and randomization audit below supplies
additional seed-level uncertainty diagnostics, not a formal equivalence test.

The black 360-keV benchmark remains sensitive: the current ten-seed
WS-ROI mean-map TV is 0.943% (GCN) and 0.932% (JJ55). The leave-one-seed-out
ranges are 0.955--1.011% (GCN) and 0.942--0.998% (JJ55), so the point estimate
below 1% does not establish a robust sub-1% equivalence result. The black
WS-ROI integrated rate changes by about -0.59% between Full and Parametric
modes.

The ten-seed observable-binning audit contains 48 ensemble rows and 480
per-seed rows. It exactly aggregates the same maps without interpolation
or new event generation. The maximum WS-ROI TV is 0.943% at native
10-phd/0.02-dex binning, 0.496% at 20-phd/0.04-dex, and 0.358% at
40-phd/0.08-dex. The maximum NEST-stage TV at native binning is 1.168%.
The reduction under coarsening is mathematical TV contraction, not evidence
that the underlying distributions become equivalent. Do not choose coarse
bins merely to force a numerical threshold.

See Section 15.8 of the linked selection audit and the
[independent-seed archive](lz_2026_extended_nr/paired_s1_independent_seeds_2026-11-15/ARCHIVE_README.md).

- Independent-seed production: [run 43750948249](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43750948249), artifact 14176882910.
- Observable-binning audit: [run 43754946092](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43754946092), artifact 14177248273.
- The paired seed-cluster bootstrap, leave-one-seed-out ranges, and exact
  randomization results are now archived in the
  [paired S1 bootstrap audit](lz_2026_extended_nr/LZ_2026_PAIRED_S1_ENSEMBLE_BOOTSTRAP_AUDIT_2026-11-16.md).
  Its percentile and basic intervals are method-sensitive diagnostics for a
  non-smooth TV statistic with only ten independent clusters; neither is a
  formal equivalence interval. These results do not validate the official
  waveform-level LZ reconstruction.

Implementation:
- cpp/lz_2026_nr_paired_s1_mode_2d_response.cc — paired Parametric/Full S1 and common Full S2 generation.
- fold_lz_2026_paired_s1_mode_2d_response.py — exact event-weighted 2D signal maps.
- audit_lz_2026_paired_s1_2d_sampling_noise.py — pooled-TV closure, marginal TV, and within-stream split-half stability.
- aggregate_lz_2026_paired_s1_2d_independent_seeds.py — ten-seed ensemble maps, per-seed summaries, rate closure, and seed-spread diagnostics.
- paired_s1_ensemble_tv_bootstrap.py — paired seed-cluster bootstrap, leave-one-seed-out checks, exact paired randomization, and archive-closure validation.
- audit_lz_2026_paired_s1_2d_binning_stability.py and .github/workflows/lz-2026-paired-s1-binning-stability.yml — 10-seed exact 10/20/40-phd by 0.02/0.04/0.08-dex rebin audit (48 ensemble and 480 per-seed rows).
- tests/test_lz_2026_paired_s1_mode_2d_response.py and tests/test_lz_2026_paired_s1_2d_sampling_noise.py — fold and diagnostic tests.
- tests/test_paired_s1_ensemble_tv_bootstrap.py — bootstrap, exact-randomization, and closure regression tests.
- .github/workflows/lz-2026-paired-s1-mode-2d-response.yml — pinned-NEST build, response production, fold, validation, and artifact upload.
- .github/workflows/lz-2026-paired-s1-bootstrap.yml — runs the five bootstrap regression tests, 100,000 paired seed-cluster replicates, exact randomization, archive-closure checks, and output archival.

The calculation passed in [run 43717240547](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43717240547), artifact 14162588482, ZIP SHA-256
6002e6ea4c345c13aa8c3e056647bb317bb41e3d6ff670dabf23c0bb343bee9b.
This is an EFT2024 NEST response only; GCN/JJ55 label the nuclear-response
spectra, not alternative NEST NR-yield configurations. It is still not the
official LZ waveform-level S1 reconstruction or final selected PDF.


### Four-benchmark paired S1 upper-tail and ROI-migration audit (2026-11-15)

The ten-seed paired S1 upper-tail audit extends the black-only study to all
four Fig. 2 three-body benchmarks. It reuses the immutable paired EFT2024
NEST event production; no NEST events were regenerated. The same detector
events are reweighted independently with each benchmark's GCN and JJ55
continuous recoil spectrum.

- Source production: [run 43750948249](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43750948249), artifact 14176882910.
- Four-benchmark audit: [run 43764753139](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43764753139), artifact 14181863680.
- 10 independent seeds; 4.7 million unique paired events; 18,800 exact
  benchmark/seed/nuclear-model/1-keV weight-closure checks.
- Maximum relative closure residual: \(7.2002\times10^{-15}\), below the
  \(5\times10^{-12}\) tolerance. Six unit tests and all production-manifest,
  support, event-count, output-row, and checksum validations passed.
- On common \(E_R=205\)--\(269.9\) keV support, the Full/Parametric S1 ROI
  changes are red −0.0676/−0.0684%, green −0.0795/−0.0805%,
  black −0.5983/−0.5881%, and blue −0.0794/−0.0804% (GCN/JJ55).
- The energy dependence is shared by all benchmarks: the 255--269.9 keV
  band gives about −0.95% to −1.03% in every case. Black is more strongly
  affected after integration because about 59--60% of its common-support
  recoil rate lies in this highest-energy band, versus about 1--2% for the
  other three benchmarks.
- Every raw event in each benchmark's full non-zero recoil support passes
  both S1 coincidence flags, the NEST S2 threshold, raw-S2 \(>645\) phd,
  and the corrected-S2 window. Thus WS-ROI and S1-ROI changes coincide
  for these supports; this is not a general statement about lower-energy NR.

The audit archives 48 summary rows, 480 per-seed rows, 4,800 threshold
rows, canonical metadata, and checksums under
[the four-benchmark audit archive](lz_2026_extended_nr/paired_s1_independent_seeds_2026-11-15/multi-benchmark-upper-tail-audit/).
See the [full report](lz_2026_extended_nr/paired_s1_independent_seeds_2026-11-15/multi-benchmark-upper-tail-audit/REPORT.md)
and Section 15.10 of the
[response-selection audit](lz_2026_extended_nr/LZ_2026_THREE_BODY_RESPONSE_SELECTION_AUDIT.md).

The audit artifact ZIP is 445,869 bytes with SHA-256
`4490b4e8a0631569617a5e6fb1e7037a1e5a70290fd5dd3f3e3c12d4518faa04`.
This remains an EFT2024 NEST proxy diagnostic, not the official LZ
waveform-level selected-event PDF. DAQ trigger, waveform-level S1 timing,
SS reconstruction/data-analysis cuts, official FV, Skin/OD veto,
live-time migration, and their joint covariance remain outside scope.
No detector-systematic covariance, final likelihood, or 90% CL exclusion
is claimed.

Implementation:
- `audit_lz_2026_paired_s1_upper_tail_all_benchmarks.py` — exact
  per-stratum reweighting, paired S1/S2 selection audit, seed-level
  summaries, bootstrap TV diagnostics, and threshold scan.
- `tests/test_lz_2026_paired_s1_upper_tail_all_benchmarks.py` — support,
  boundary, and model-support regression tests.
- `.github/workflows/lz-2026-paired-s1-upper-tail-all-benchmarks.yml` —
  immutable artifact download, manifest verification, tests, audit,
  archive/checksum update, and output artifact upload.
