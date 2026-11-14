# LZ detector-response inputs and rate-level archive

This directory stores the detector-response inputs used to connect the
three-body natural-xenon recoil spectra to the published LZ 2026
high-efficiency nuclear-recoil region.

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

The event-level pilot uses the Table S5 NR mean-yield vector with the public LZ WS2024 detector class and compares its tuned NR width vector with generic NEST defaults. Its first paired 248-keV run is a one-energy, one-position sanity check, not a full reproduction of the published NR band. The paper's Fig. 2 band is constructed from flat-in-energy NR spectra and evaluated at fixed S1c. The historical flat-spectrum pilot tests both the 5.4–269.9 keV analysis-window prior and approximately 0.1–330 keV AmBe range at the candidate position, but used hybrid Table-S5/WS2024 inputs and is superseded. The primary public candidate is now NEST commit 541b643's `SetEFT2024Configuration()`; full-S1c NR and ER bands plus conditional 2D PDFs are documented in `LZ_2026_NR_ER_FULL_RESPONSE_CANDIDATE_REPORT.md`. The uniform active-TPC position distribution remains a proxy, not the actual D-D/AmBe calibration-source distribution.\n\nThe rate-level event-yield files fold the continuous natural-xenon spectra
with the digitized central efficiency and its gray envelope over the
5.4–269.9 keV analysis window. They are rate-level diagnostics only: they do
not include the two-dimensional S1c/log10(S2c) signal PDFs, NEST nuisance
covariance, energy-resolution smearing, background likelihood, or profile
likelihood. They are not a 90% confidence-level exclusion and are not the
official LZ likelihood.

See the main study report and
`research/figure2_full_reproduction/fold_lz_2026_rate_level.py` for the
calculation and limitations.


## NR event-level response pilot (new)

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


## Three-body signal folded through the NR 2D response (new)

The first end-to-end pre-selection fold is documented in
`lz_2026_extended_nr/LZ_2026_THREE_BODY_NR_2D_RESPONSE_FOLD_REPORT.md`.

- `cpp/lz_2026_nr_full_calibration_band.cc`: event-level NEST response sampler; now accepts explicit recoil-energy minimum and maximum.
- `fold_lz_2026_three_body_2d_response.py`: constructs per-energy-bin response probabilities and folds the archived continuous natural-xenon three-body spectra into `(S1c, log10(S2c))) cell intensities.
- `tests/test_lz_2026_three_body_2d_response.py`: numerical tests for exact piecewise-linear rate integration, partial ROI bins, and probability-mass preservation.
- `.github/workflows/lz-2026-three-body-2d-response-fold.yml`: reproducible pinned-NEST workflow.

The workflow passed as [run 43645345194](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43645345194). Its artifact contains four 200k-event response samples, the 2D cell-intensity CSV, and closure summaries. The 2D output is a pre-selection observable intensity. The energy-only final-ROI efficiency is deliberately kept separate because it does not specify the selected two-dimensional response and must not be double counted.

The response uses a uniform active-TPC volume proxy, not the actual calibration-source spatial distribution. It is not the official production NEST configuration, full selected-event PDF, background likelihood, or confidence interval.
