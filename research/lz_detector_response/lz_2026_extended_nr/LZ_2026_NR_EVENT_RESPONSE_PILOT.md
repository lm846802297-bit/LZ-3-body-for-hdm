# LZ 2026 NR event-level NEST response pilot

**Status:** implementation prepared; local numerical execution is pending. No event-level output is claimed yet.

## 1. Objective

Move from the previously validated NR mean-yield model to event-level detector observables. The aim is to determine how much the LZ WS2024-tuned NR fluctuation vector changes the predicted S1c/S2c distributions relative to generic NEST NR-width defaults, while holding the 2026 mean-yield model and detector candidate fixed.

This is a detector-response pilot only. It is not an attempt to reproduce the official LZ likelihood or infer the recoil energy of the observed candidate event.

## 2. Pinned inputs

| Input | Choice | Provenance |
|---|---|---|
| NEST source | commit 423b9745a5bfbb0402514f1d7955e67445de0810 | public NEST source commit |
| Detector class | LZ_Detector_2024 | include/Detectors/LZ_WS2024.hh at the pinned commit |
| NR mean yields | 15 parameters from 2026 Supplemental Table S5 | lz_2026_nest_nr_mean_yield_parameters.json |
| NR width A | LZ WS2024 tuned 13-element vector | detector class get_nr_er_width_params() |
| NR width B | generic NEST default 13-element vector | include/NEST/NEST.hh at the same commit |
| ER yield vector | ten NEST default entries -1 | passed for API completeness; the event species is NR |

The 2026 Table S5 mean-yield vector is passed explicitly to FullCalculation, overriding the older 12-element mean-yield vector stored inside the WS2024 detector class. The detector's OldW13eV=true setting is retained.

## 3. Calculation sequence

For every monoenergetic NR event:

1. NESTcalc::FullCalculation(NR, E_R, rho, E_d, A, Z, NRYieldsParam, NRERWidthsParam, ERYieldsParam, false) calculates the 2026 NR mean yields and draws the intrinsic fluctuated quanta.
2. NESTcalc::GetS1(..., S1CalculationMode::Full, ...) simulates S1 detection, including photon detection, PMT-level SPE/DPE response, pulse-area smearing, and the NEST coincidence logic.
3. NESTcalc::GetS2(..., S2CalculationMode::Full, ...) simulates the integrated S2 pulse area, including extraction, electron lifetime, electroluminescence gain, SPE/DPE response, and the configured S2 threshold.

The driver uses the NEST detector response functions directly. It does not approximate event-level signals as g1*Nph and g2*Ne.

### Output index convention

The NEST execNEST.cpp NESTObservableArray::store_signals implementation identifies:

- GetS1()[5]: S1c, corrected pulse area in phd;
- GetS2()[7]: S2c, corrected pulse area in phd.

The signs are meaningful. NEST negates the S1 observables when the S1 coincidence condition fails, and negates the S2 observables when the configured S2 threshold fails. The driver therefore retains signed values in the raw CSV and separately writes pass flags. Do not take absolute values before applying the flags.

## 4. Detector point and response mode

The initial pilot fixes the interaction at:

- \(x=y=0\);
- \(z = z_{\rm top}-v_d\,dt_{\rm cntr}\);
- drift time \(dt=dt_{\rm cntr}\).

This is the central reference depth used by the WS2024 S1 position correction. At this point, the normalized S1 and S2 spatial corrections are unity by construction. No spatial-position distribution, position reconstruction smearing, or isotope-by-isotope natural-xenon mixture is applied in this first pilot. The NEST detector's natural-xenon mean molar mass is used.

S1 uses S1CalculationMode::Full. S2 uses S2CalculationMode::Full, which is NEST's integrated pulse-area branch, not its waveform branch. It retains the integrated response fluctuations but does not generate the detailed S2 waveform or waveform-mode diffusion/electron-train treatment. This distinction is deliberate and must be retained in any interpretation of the results.

## 5. Energy grid and statistics

Default energy grid:

\[
E_R = \{5.4,\ 10,\ 50,\ 74.7,\ 100,\ 150,\ 200,\ 248,\ 269.9\}\ \mathrm{keV}.
\]

The 248 keV point is included as a dedicated comparison point near the candidate-event discussion; it is not treated as a calibration point. The 269.9 keV point probes the high-energy analysis endpoint.

Default sample size is 2,000 events per energy per baseline, i.e. 36,000 events total. The same base seed is reset for the two baselines at each energy. This ensures reproducible runs and a controlled seed choice; it does not guarantee identical event-by-event random draws after the width model changes.

## 6. Baselines

### A. LZ WS2024 tuned NR widths

Uses the 13-entry vector exposed by LZ_Detector_2024::get_nr_er_width_params():

\[
\{0.404,\ 0.393,\ 0.0383,\ 0.497,\ 0.1906,\ 2.220,\ 0.3,\ 0.04311,\ 0.46894,\ 0.15505,\ -0.26564,\ 0,\ 0\}.
\]

For NR, the relevant entries in the pinned GetQuanta implementation are indices 0, 1, 2, 3, 4, 5, 11, and 12.

### B. Generic NEST NR widths

Uses the pinned NEST default:

\[
\{0.4,\ 0.4,\ 0.04,\ 0.5,\ 0.19,\ 2.25,\ -0.001,\ 0.046452,\ 0.45,\ 0.205,\ -0.2,\ 0,\ 0\}.
\]

The two baselines share the 2026 Table S5 mean-yield vector, the same detector class, field, density, position, energy grid, event count, and seed policy. Thus the comparison isolates the NR width-vector choice within this detector candidate.

## 7. Expected output

The local PowerShell runner writes:

- lz_2026_nr_response_ws2024.csv: raw event records for baseline A;
- lz_2026_nr_response_generic.csv: raw event records for baseline B;
- lz_2026_nr_response_summary.json: full distribution summaries;
- lz_2026_nr_response_summary.csv: compact baseline/energy comparison;
- lz_2026_nr_response_run_metadata.json: run configuration and source pin.

The output directory defaults to %LOCALAPPDATA%\LZ-3-body-for-hdm\nr_event_response, outside the Git working tree.

The summary reports generated-event count, S1 coincidence pass fraction, S2 threshold pass fraction, joint pass fraction, quanta means/widths, S1c and S2c means/widths/quantiles, and the correlation between S1c and log10(S2c) among jointly passing events.

## 8. Execution on the user's Windows workstation

The self-hosted Windows runner has not been confirmed registered or online, and the user's earlier constraint was not to rely on GitHub-hosted Actions quota. Therefore this pilot is prepared for local execution; no remote runner dispatch or hosted workflow is assumed.

Prerequisites:
- Git;
- CMake;
- Visual Studio 2022 Build Tools with the Desktop development with C++ workload (or another C++17 toolchain recognized by CMake);
- Python 3.10 or newer.

From a Visual Studio 2022 Developer PowerShell:

~~~powershell
Set-ExecutionPolicy -Scope Process Bypass
cd <repository-root>\research\lz_detector_response
.\run_lz_2026_nr_event_response.ps1
~~~

Optional larger run:

~~~powershell
.\run_lz_2026_nr_event_response.ps1 -EventsPerEnergy 5000 -Seed 20261115
~~~

The script checks out the exact NEST commit, builds NESTCore and the C++ driver, runs both baselines, and summarizes the raw outputs. The local NEST checkout and build products are ignored by Git.

## 9. Interpretation limits and next gates

1. **No numerical result exists until the PowerShell run completes.** Source inspection and code preparation must not be described as a successful event-level reproduction.
2. The WS2024 detector class is a well-motivated LZ candidate because its gain and S2 threshold agree closely with values quoted in the 2026 paper. It is not confirmed as the exact 2026 extended-NR response configuration.
3. The detector header recommends NEST v2.4.0, while the 2026 paper says NEST v2.4.5. The selected source commit contains the high-energy Table S5 mean-yield extension but is a commit pin, not an official tagged-version claim.
4. The pilot uses a central reference position, not the full spatial distribution or detector maps.
5. S2 waveform mode, waveform diffusion/electron-train details, the complete selection, ER model, calibration PDFs, nuisance covariance, backgrounds, and the 2D signal likelihood are not included.
6. The 248 keV candidate event is not a calibration anchor and must not be used to tune the NR response.

After local execution, inspect the CSV integrity, compare A/B distributions at 74.7, 248, and 269.9 keV first, then expand only if the pilot passes. Any claim of matching the 2026 NR band requires the relevant collaboration response configuration and calibration checks.

## 10. Reproducibility files

- C++ driver: research/lz_detector_response/cpp/lz_2026_nr_event_response.cpp
- CMake project: research/lz_detector_response/CMakeLists.txt
- Windows runner: research/lz_detector_response/run_lz_2026_nr_event_response.ps1
- Table S5 vector: research/lz_detector_response/lz_2026_extended_nr/lz_2026_nr_yield_params_s5.txt
- Summary program: research/lz_detector_response/lz_2026_extended_nr/summarize_nr_event_response.py
- Configuration tests: research/lz_detector_response/tests/test_lz_2026_nr_event_response_config.py


## 11. Pinned NEST source locations audited

All source references below use commit 423b9745a5bfbb0402514f1d7955e67445de0810:

- [runNESTvec call sequence in src/execNEST.cpp](https://github.com/NESTCollaboration/nest/blob/423b9745a5bfbb0402514f1d7955e67445de0810/src/execNEST.cpp): calls FullCalculation, then GetS1 and GetS2.
- [NESTObservableArray::store_signals in src/execNEST.cpp](https://github.com/NESTCollaboration/nest/blob/423b9745a5bfbb0402514f1d7955e67445de0810/src/execNEST.cpp): documents S1c as S1 result index 5 and S2c as S2 result index 7.
- [GetS1 and GetS2 implementations in src/NEST.cpp](https://github.com/NESTCollaboration/nest/blob/423b9745a5bfbb0402514f1d7955e67445de0810/src/NEST.cpp): preserve negative signs when the S1 coincidence or S2 pulse-area threshold fails.
- [LZ_WS2024 detector class](https://github.com/NESTCollaboration/nest/blob/423b9745a5bfbb0402514f1d7955e67445de0810/include/Detectors/LZ_WS2024.hh): provides the detector settings and calibration-tuned NR width vector.
- [generic NEST defaults and API declarations](https://github.com/NESTCollaboration/nest/blob/423b9745a5bfbb0402514f1d7955e67445de0810/include/NEST/NEST.hh): provides the generic NR width vector and FullCalculation/GetS1/GetS2 interfaces.
