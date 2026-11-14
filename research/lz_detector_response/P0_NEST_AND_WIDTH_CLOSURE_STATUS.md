# P0 detector response and propagator-width closure: current audit

Date: 2026-11-15
Branch: research/figure2-p0-4-mainline

## Executive status

The final LZ parameter scan remains frozen. Two P0 tracks are active:

- Track A: reconstruct the LZ 2026 NR detector response using the actual high-energy NEST model, beginning with the published Table S5 parameter set.
- Track B: close the independent-coupling and finite-width assumptions in the three-body propagator.

A new machine-readable archive of the LZ 2026 NR mean-yield parameters has been added:
`research/lz_detector_response/lz_2026_extended_nr/lz_2026_nest_nr_mean_yield_parameters.json`.

This is a verified input extraction, not a completed detector-response simulation.

## 1. LZ 2026 NR mean-yield model: verified Table S5 input

Source: LZ Collaboration, arXiv:2609.02823v1, Supplemental Material, Table S5, PDF page 17. The table gives the NEST NR mean light- and charge-yield model parameters.

The NEST parameter vector, in the order used by the current source implementation, is:

```text
NRYieldsParam = {
  11.2, 1.1, 0.052, -0.0533,
  10.8, 0.53, 1.4,
  0.31, 2.5, 0.50,
  1.39, 1.74,
  0.0230, 0.0289, 74.7
}
```

The first twelve entries are the original NR mean-yield parameter vector. The final three entries are the high-energy extension:

- a = 0.0230
- b = 0.0289
- E0 = 74.7 keV

The exponent used in the charge-yield power law is:

[
p(E)=
egin{cases}
0.5, & Ele E_0,\
0.5+aln[1+b(E-E_0)], & E>E_0.
end{cases}
]

The purpose of this modification is to describe the high-energy NR charge-yield suppression revealed by the AmBe calibration, while retaining the low-energy DD-calibrated response. It is essential for the LZ extended-NR region and must not be replaced by the older 12-parameter NEST vector.

The LZ paper states that the NR calibration covers DD recoils at lower energies and AmBe recoils up to about 330 keV. This is the relevant calibration regime for the 5.4--269.9 keV WIMP-search ROI.

## 2. Important NEST version/source pin finding

The LZ paper cites NEST v2.4.5 (2026). The public GitHub release page currently exposes a v2.4.5beta prerelease tag at commit `19bc9bc` dated 2025-12-08.

Inspection of that prerelease source shows that its `GetYieldNR` implementation does not yet contain the 15-parameter high-energy p(E) extension. Therefore the v2.4.5beta tag is not sufficient for reproducing the LZ 2026 Table S5 model.

The NEST source history identifies the exact commit that introduced the high-energy NR charge-yield suppression:

- repository: https://github.com/NESTCollaboration/nest
- commit: `423b9745a5bfbb0402514f1d7955e67445de0810`
- commit date: 2026-08-16 16:33:43 UTC
- commit message: Add energy-dependent NR charge-yield suppression (#210)
- source file: `src/NEST.cpp`
- source blob: `7e19ee148879ae80a982f91652b90c1fc9e10256`

This commit predates the LZ paper submission and contains the 15-parameter branch in `GetYieldNR`, reading a, b, and E0 from vector entries 12, 13, and 14 when the vector length is at least 15. This is a more precise source pin than the later master HEAD.

**Reproducibility rule:** pin this source commit and record its SHA. Do not silently substitute the older v2.4.5beta tag. It is a commit pin, not a claim that the commit is an official tagged v2.4.5 release. If the HEPData package or an official final v2.4.5 release supplies a more precise release commit, compare it and update the pin only after a source-level equivalence check.

## 3. What Table S5 does not provide

Table S5 is the NR **mean yield** model. It is not a complete detector response. The following must remain separate inputs:

1. NR quanta and recombination fluctuation parameters;
2. detector light collection and charge extraction parameters;
3. position-dependent electric-field and optical maps;
4. S1 and S2 single-photon/single-electron response and resolution;
5. trigger, reconstruction, and analysis selections;
6. conditional signal PDFs in {S1c, log10(S2c)};
7. nuisance constraints/covariance.

The public NEST `LZ_WS2024.hh` detector file explicitly describes WS2024/EFT2024 response settings and is not the LZ 2026 extended-NR configuration. Its 2024 parameter vectors must not be reused as if they were the 2026 configuration.

The paper's public NR efficiency curve remains a valuable independent validation target, but it is not a substitute for the conditional two-dimensional response.

## 4. NEST implementation work to perform next

### A1. Mean-yield implementation and verification

- Implement the Table S5 15-parameter vector in a small, isolated response module.
- Port the current NEST `GetYieldNR` equations exactly, including the high-energy p(E) branch, isotope mass scaling, field dependence, density dependence, and the LZ work-function convention.
- Confirm the correct LZ 2026 electric-field, density, molar-mass, and OldW13eV settings from the official release before generating final yield curves.
- Compare the independent implementation against the pinned NEST C++ implementation at a fixed grid of recoil energies and isotope masses.
- Archive photon yield, electron yield, total quanta, and all inputs.

Do not assume the 2024 detector header's 96.5 V/cm field or its OldW13eV setting applies to the 2026 analysis without explicit evidence.

### A2. Fluctuations and detector response

- Identify the NR fluctuation parameter values used by the LZ 2026 simulation from the data release or explicit supplemental information.
- If only the mean-yield vector is available, keep the fluctuation model as a separately labelled approximation; do not call it the complete LZ-tuned NEST response.
- Generate conditional `P(S1c, log10(S2c) | ER, A, detector settings)` distributions.
- Validate the median and width of the NR band against published calibration plots, including the AmBe high-energy region.
- Apply event-selection acceptance exactly once. Keep conditional response and acceptance as separately testable layers.

### A3. Validation gates

1. Mean-yield code agrees with the pinned NEST C++ source to numerical precision.
2. Quanta conservation and physical bounds hold.
3. Repeated-seed Monte Carlo distributions are stable.
4. NR-band median and width agree with the published calibration information within digitization/statistical uncertainties.
5. Integrating the conditional response through the analysis cuts reproduces the published NR efficiency curve within the documented uncertainty.
6. The rate-level efficiency-fold result is reproduced as a cross-check, with no duplicate efficiency factor.

## 5. Independent coupling and finite-width audit

The manuscript's vector-vector Lagrangian is:

[
mathcal L_{mathrm{int}}supset
g_1 V^muarchi_2gamma_muchi_1
+g_2sarchi_2chi_1+mathrm{h.c.}
]

The plotted normalization specifies only ((g_1g_2g_{VN})^2), while the propagator uses a pole width. The product normalization does not determine (g_2) separately, and the width is proportional to (|g_2|^2) under the conditional Dirac scalar-decay calculation.

The manuscript does not explicitly identify (chi_{1,2}) as Dirac or Majorana fields, does not fully specify the scalar's real/complex nature and CP/chiral structure, and does not enumerate all possible (chi_2) decay channels. Consequently, the existing (chi_2	ochi_1s) formula is a conditional Dirac result, not yet a model-independent total width.

### B1. Model-definition closure

- Determine the intended fermion nature from the underlying model/source or author clarification.
- Fix the scalar field and vertex conventions, including hermitian-conjugate/channel counting.
- Enumerate every kinematically open (chi_2) decay channel for each benchmark.
- Derive the total width consistently from those interactions.
- Keep (g_1), (g_2), and (g_{VN}) independent in the numerical input; do not infer (g_2) from the plotted product.

### B2. Propagator/self-energy closure

The source manuscript explicitly uses a constant pole-width denominator:
[
W^2-m_{chi_2}^2+i m_{chi_2}Gamma_{chi_2}.
]

The existing width-sensitivity scan is a diagnostic. It shows that for (m_s=300) keV, (Delta m=1) MeV, (E_R=200) keV, and (v=776) km/s, the constant pole-width prescription changes the reduced kernel by about -1.12% at (g_2=1) and -45.16% at (g_2=3). The diagnostic running-width ansatz gives different results, but is not a full fermionic self-energy calculation.

Next steps:

- derive the appropriate fermion self-energy (Sigma(
ot K)) from the fixed model;
- separate its scalar/vector Dirac structures and real/imaginary parts;
- specify mass and wavefunction renormalization conditions;
- compare the resulting resummed propagator with the manuscript's constant pole-width prescription;
- repeat the W-integral and halo-fold convergence tests after the model definition is fixed.

Do not choose a width scheme because it gives a preferred spectrum.

## 6. Scan freeze and reporting policy

Until Tracks A and B pass their validation gates:

- no final large parameter-space scan;
- no reinterpretation of rate-level yields as a confidence limit;
- no claim that the 248 keV candidate is explained by the model;
- no use of an efficiency-only fold as a full detector-level likelihood;
- retain current rate-level outputs as diagnostics only.

## 7. Current deliverables

- LZ Table S5 parameters: `lz_2026_extended_nr/lz_2026_nest_nr_mean_yield_parameters.json`
- Public input audit: `LZ_2026_PUBLIC_INPUTS_AUDIT.md`
- Existing finite-width audit: `research/figure2_full_reproduction/results/P0-4_PROPAGATOR_WIDTH_AUDIT_ZH.md`
- Conditional two-body width derivation: `research/docs/08_chi2_decay_width.md`

## 8. Sources

- LZ Collaboration, arXiv:2609.02823v1, especially Supplemental Material Table S5 and the detector-response/likelihood sections.
- HEPData data release, DOI: 10.17182/hepdata.182472.v1.
- NESTCollaboration/nest source, selected commit pin `423b9745a5bfbb0402514f1d7955e67445de0810` (contains the 15-parameter high-energy NR suppression).
- NEST v2.4.5beta prerelease tag `19bc9bc`, retained as a version comparison, not the selected implementation pin.


## 9. Progress update: first independent mean-yield port

The first isolated Python implementation is now committed:

- `lz_2026_extended_nr/lz_2026_nr_mean_yield.py`
- `tests/test_lz_2026_nr_mean_yield.py`
- `.github/workflows/lz-2026-nest-nr-mean-yield.yml`

The implementation ports the 15-parameter mean-yield equations from the pinned NEST source and requires the detector field, density, molar mass, isotope mass number, and OldW13eV flag explicitly. This prevents the 2024 detector settings from being silently inherited.

CI run:
- Run ID: `43626728281`
- Result: success
- Job: `mean-yield-tests`
- Tested: 15-parameter vector, high-energy exponent turn-on, non-negative/additive mean quanta, isotope mass scaling, explicit OldW13eV dependence, and invalid-input handling.

**Validation boundary:** the current tests are unit tests of the independent Python port. They are not yet a cross-language comparison against a compiled NEST executable, and they do not validate the LZ 2026 detector configuration. No final mean-yield curve or S1/S2 PDF is claimed yet.

The field, density, isotope mass scaling convention, and OldW13eV flag must be confirmed against the LZ 2026 HEPData release or collaboration documentation before producing the production response grid.


### Source-history refinement

The first audit pinned the then-current NEST master HEAD. A subsequent history check found the exact earlier commit introducing the LZ high-energy NR suppression:
`423b9745a5bfbb0402514f1d7955e67445de0810` (2026-08-16, commit message “Add energy-dependent NR charge-yield suppression”). The JSON parameter archive has been updated to this commit and its exact source blob. This avoids pinning unrelated later changes while retaining the p(E) code used by the LZ 2026 mean-yield model.


## 10. Progress update: C++ cross-language validation passed (2026-11-15)

The direct C++ wrapper now compiles against the pinned NEST core and calls `NESTcalc::GetYieldNR` itself. The workflow uses the pinned source commit `423b9745a5bfbb0402514f1d7955e67445de0810` and the GCEM and detector-header include paths required by that build.

Successful CI:
- Run ID: `43630666034`
- URL: https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43630666034
- Python unit tests: 6 passed
- Cross-language cases: isotopes A = 128, 131, 136; both `OldW13eV=true/false`; 11 recoil energies per case from 5.4 to 330 keV, including 74.7 keV and 248 keV
- Scalar comparisons: 264
- Worst scaled absolute difference: `3.331e-16`

This validates the independent Python port of the **NR mean-yield equations only** against the pinned NEST C++ implementation. It does not validate the NR fluctuation model, LZ detector configuration, S1/S2 response, or the official LZ likelihood.

### Detector conditions that can now be fixed

The LZ 2026 extended-NR analysis uses the 220-live-day WS2024 dataset (27 March 2023--1 April 2024). The associated WS2024 drift field is 97 V/cm. The LZ 2026 paper reports the calibrated gains:
- `g1 = 0.110 +/- 0.002 phd/photon`
- `g2 = 34.5 +/- 1.1 phd/electron`

These are now verified detector-level inputs for the analysis period. They should not be confused with the older SR1/WS2022 values. The paper's `g1`/`g2` gains do not by themselves determine all underlying NEST optical, extraction, and single-electron parameters.

### Inputs still not fixed for production response

- liquid-xenon density used by the LZ-tuned NEST configuration;
- the precise molar-mass convention and isotope scaling used in the collaboration configuration;
- `OldW13eV` setting in the LZ 2026 release (the public WS2024 NEST header sets it true, but that header is not itself proof of the final 2026 analysis configuration);
- the exact NR fluctuation vector used in the 2026 BACCARAT/NEST production;
- detector spatial maps and event-level S1/S2 response configuration;
- whether the HEPData release includes the full detector header or only fitted model parameters.

The NEST cross-check driver deliberately tests both `OldW13eV` modes and uses an explicit molar mass and density. Its numerical agreement is not evidence that either mode is the official LZ choice.

## 11. Next detector-response milestone

Before producing a production S1/S2 PDF grid:
1. Resolve the LZ 2026 HEPData payload and inventory all files, not only the paper's Table S5.
2. Confirm density, molar mass, `OldW13eV`, NRERWidthsParam, and all detector gain/extraction settings.
3. Build a NEST event-level driver using the 15-parameter Table S5 mean-yield vector and the confirmed fluctuation vector.
4. Generate NR calibration samples over the DD and AmBe energy ranges and compare the median and 10--90% band to the published Figure 2 calibration data.
5. Only after that validation, produce conditional PDFs in `{S1c, log10(S2c)}` and integrate the official WS ROI cuts.

Until these gates pass, retain the current module as a validated mean-yield component, not a complete LZ response model.


## 12. HEPData retrieval attempt and event-level NEST API audit (2026-11-15)

### HEPData endpoint result

A GitHub Actions retrieval job was run on the active research branch:

- Run: https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43632033089
- Result: workflow success for PDF extraction, digitization validation, and archive steps.
- Artifact: lz-2026-hepdata-inventory-and-pdf-extraction (artifact ID 14128441663).

Important: workflow success does NOT mean the HEPData payload was retrieved. The artifact DOWNLOAD_STATUS.txt records YAML endpoint HTTP 403 and JSON record endpoint HTTP 403. The arXiv PDF was downloaded and the efficiency extraction completed. The artifact contains the PDF, Fig. S2 SVG, the 303-point efficiency CSV, its metadata, and the status file; it contains no HEPData YAML/JSON payload. At the time of this workflow run, the endpoint attempt was blocked. A subsequent user-supplied v1 archive has now been received and audited; see Section 13. The ZIP is a table export and does not include the separate NEST response configuration resource.

### What the NEST event-level API actually requires

The pinned NEST source exposes this event chain:
1. NESTcalc::FullCalculation(NEST::NR, ER, density, field, molarMass, A, NRYieldsParam, NRERWidthsParam, ...) produces fluctuated quanta;
2. GetS1(...) maps photons to detected S1 observables using detector response and an S1 mode;
3. GetS2(...) maps electrons to detected S2 observables using detector response and calculated g2_params.

The 15-element Table S5 vector is only NRYieldsParam. FullCalculation also consumes NRERWidthsParam, which controls NR quanta/recombination fluctuations. The upstream default vector at pinned commit 423b9745a5bfbb0402514f1d7955e67445de0810 is {0.4, 0.4, 0.04, 0.5, 0.19, 2.25, -0.001, 0.046452, 0.45, 0.205, -0.2, 0., 0.}. This is an upstream default, NOT yet verified as the LZ 2026 fitted fluctuation vector.

The 2026 paper Table S5 provides the mean-yield parameters only. The supplied HEPData v1 table ZIP has now been inspected and contains no separate NEST configuration resource or tuned NRERWidthsParam vector. We must not silently treat the upstream default NR fluctuation vector as the LZ best-fit configuration.

### Consequence for the pilot response

An event-level C++ driver can be compiled now as an API/build test, but its outputs would be a generic NEST pilot, not the LZ 2026 signal PDF. To avoid a misleading physics result, do not archive or use such pilot distributions as production detector response.

The production driver must require, as explicit versioned inputs: the official NRERWidthsParam vector (or a documented LZ decision to use fixed/default values); OldW13eV; density and isotope molar-mass convention; WS2024 field and detector response settings; g1, gas gain/extraction and single-electron response parameters; S1/S2 calculation modes; and position/field response configuration.

### Corrected interpretation of current status

- Mean-yield equations: validated against pinned NEST C++ (264 scalar comparisons; worst scaled difference 3.331e-16).
- Event-level NEST API: source/API audited; no LZ 2026 event-level S1/S2 Monte Carlo has yet been validated.
- HEPData v1 table archive: user-supplied ZIP parsed and structurally validated (46 YAML tables); separate NEST response resource remains unlocated.
- Scalar one-loop self-energy: the conditional Dirac, real-scalar, pure-scalar-Yukawa contribution has already been derived and numerically implemented in P0-4B_SCALAR_SELF_ENERGY_AUDIT_ZH.md.
- Full propagator self-energy: still open because the source model also has an off-diagonal vector interaction but does not specify m_V or the gauge/Goldstone completion; the Dirac/Majorana assignment is also unspecified.
- Parameter scan and final LZ likelihood: remain frozen.


## 13. User-supplied HEPData v1 archive received and audited (2026-11-15)

The user supplied `HEPData-ins3199115-v1.zip`. It was opened directly from the uploaded file and all 46 table YAML files were parsed.

- Archive size: 40,657 bytes.
- SHA-256: `ab02f6eacd1008a260f0eb8f441beb206069e18f10c6b7b2f44fcfd70463f1f1`.
- Three event samples: Science 1,710 points; PromptVeto 66; DelayedVeto 55.
- 43 model tables: 40 L01s–L20v tables and O01s, O01v, O04s.
- All columns have matching row counts; all values are numeric and finite; no structural parse errors were found.
- The Science sample's maximum-S1 point is (S1_c=540.07916\,\mathrm{phd}), (log_{10}(S2_c/\mathrm{phd})=3.966964), hence (S2_c=9267.53\,\mathrm{phd}). This matches the event of interest reported in the paper ((S1_c\simeq540.1\,\mathrm{phd}), (S2_c=9268\,\mathrm{phd})).
- The ZIP contains observed search samples and model-limit tables. It does not contain calibration event samples or a separate NEST configuration resource, NRERWidthsParam fit, S1/S2 PDFs, or nuisance covariance.
- The 15-entry Table S5 NR mean-yield vector remains in `lz_2026_nest_nr_mean_yield_parameters.json`; it is not a fluctuation vector.
- Full details and table-coverage exceptions are recorded in `lz_2026_extended_nr/HEPDATA_V1_ARCHIVE_AUDIT.md`.

Consequently, the supplied ZIP resolves the missing observed-sample tables but does not close the production event-level NEST response-input gap. The production response and final likelihood remain frozen pending the separate response resource or an explicitly documented and validated substitute.


## 14. LZ-specific NR fluctuation candidate found in pinned NEST source (2026-11-15)

A source audit of NEST commit `423b9745a5bfbb0402514f1d7955e67445de0810` found `include/Detectors/LZ_WS2024.hh`. The file identifies itself as the LZ SR3/WS2024 detector input and explicitly documents calibration-adjusted vectors for tritium and D-D data. It includes the tuned width vector:

```text
NRERWidthsParam = {
  0.404, 0.393, 0.0383, 0.497, 0.1906, 2.220,
  0.3, 0.04311, 0.46894, 0.15505, -0.26564, 0., 0.
}
```

For the NR branch, `GetQuanta` uses indices 0, 1, 2, 3, 4, 5, 11, and 12. The corresponding generic defaults are 0.4, 0.4, 0.04, 0.5, 0.19, 2.25, 0, and 0. The WS2024 values differ only modestly from the generic defaults for these NR-relevant entries.

This is a more physically motivated baseline than an unqualified generic default. However, the detector file says it is for LZ SR3/WS2024 and recommends NEST v2.4.0; it does not prove that these exact width parameters were retained in the 2026 extended-NR analysis using NEST v2.4.5. The 2026 paper's Table S5 supplies the 15 NR mean-yield parameters, but does not tabulate the NR width vector.

The two candidate vectors, source pin, index mapping, and comparison are recorded in `lz_2026_extended_nr/lz_2026_nr_fluctuation_baselines.json`. Recommended next calculation: run the LZ-WS2024-tuned width vector as the primary documented candidate and generic defaults as a sensitivity comparison. Do not label either as the exact 2026 response configuration until confirmed by a 2026 configuration file or explicit collaboration statement.


## 15. LZ WS2024 detector settings cross-checked against the 2026 paper (2026-11-15)

The same pinned NEST source's `LZ_WS2024.hh` detector class was audited. Recomputing its `CalculateG2` source formula using the class's T, pressure, gas field/gap, xenon molar mass, dielectric constants, and gas-light collection gives:

- (g_1=0.1122\,\mathrm{phd/photon}), compared with the paper's (0.110\pm0.002);
- (g_2=34.0224\,\mathrm{phd/electron}), compared with the paper's (34.5\pm1.1);
- (783\,\mathrm{phe}/(1+0.214)=644.98\,\mathrm{phd}), matching the paper's 645 phd S2 threshold;
- `FitEF` = 96.5 V/cm, close to the 97 V/cm reference shown in Table S3.

The gain/threshold consistency is strong evidence that the WS2024 class is a useful detector-response candidate. It is still not proof of the exact 2026 setup: the header recommends NEST v2.4.0 while the paper says v2.4.5; its old 12-entry mean-yield vector must be overridden by Table S5; and its 13-element width vector does not contain the 2026 double-skewed-Gaussian ER fluctuation model from Table S4. Thus it is suitable as a **candidate NR-only event-level baseline**, not as a complete ER+NR or likelihood reproduction.

Detailed source calculation and caveats are in `lz_2026_extended_nr/LZ_WS2024_DETECTOR_CROSSCHECK.md`; machine-readable values are in `lz_2026_extended_nr/lz_2026_nr_fluctuation_baselines.json`.


## 16. Direct NEST event-level NR response pilot prepared (2026-11-15)

A direct C++ event-response driver and local Windows build/run path are now committed. The driver follows the pinned NEST call chain:
- **FullCalculation(NR, ...)** with the 15-entry 2026 Table S5 mean-yield vector and one of the two NR width baselines;
- **GetS1(..., S1CalculationMode::Full, ...)**;
- **GetS2(..., S2CalculationMode::Full, ...)**.

The driver records the signed corrected-phd observables **GetS1()[5]** (S1c) and **GetS2()[7]** (S2c), preserving NEST's negative-sign flags for S1 coincidence failure and S2 threshold failure. It does not approximate the observables as g1*Nph and g2*Ne.

Two baselines are prepared:
1. **ws2024**: LZ WS2024 calibration-tuned NRERWidthsParam vector;
2. **generic**: generic NEST default NRERWidthsParam vector.

Both use the same 2026 Table S5 mean-yield vector, LZ WS2024 detector class, reference-depth event position, nine recoil energies (5.4–269.9 keV including 248 keV), 2,000 events per energy by default, and matched base seed policy. S1 uses the detailed PMT-level Full mode; S2 uses NEST's integrated Full pulse-area mode, not the waveform mode.

New files:
- research/lz_detector_response/cpp/lz_2026_nr_event_response.cpp
- research/lz_detector_response/CMakeLists.txt
- research/lz_detector_response/run_lz_2026_nr_event_response.ps1
- research/lz_detector_response/lz_2026_extended_nr/lz_2026_nr_yield_params_s5.txt
- research/lz_detector_response/lz_2026_extended_nr/summarize_nr_event_response.py
- research/lz_detector_response/lz_2026_extended_nr/LZ_2026_NR_EVENT_RESPONSE_PILOT.md
- research/lz_detector_response/tests/test_lz_2026_nr_event_response_config.py

**Execution status:** code and local runner are prepared, but no event-level simulation has yet been executed. The Windows self-hosted runner was not confirmed registered/online, and the user previously requested not to rely on GitHub-hosted Actions quota. The run is therefore intentionally left for the user's local Windows workstation; no CI success or numerical reproduction is claimed. Raw CSV and summaries are written outside the Git working tree under %LOCALAPPDATA%\LZ-3-body-for-hdm\nr_event_response by default.

Interpretation limits: this is an NR response pilot at one central reference position, with no spatial distribution, position smearing, S2 waveform/diffusion treatment, full analysis cuts, backgrounds, nuisance covariance, or 2D signal likelihood. The WS2024 detector class remains a candidate, not a confirmed exact 2026 response configuration.


**S2 threshold bookkeeping correction:** NEST tests the configured 783 phe threshold on raw S2 pulse area, then applies electron-lifetime/position corrections to S2c. The raw threshold after DPE conversion is 644.98 phd; at the pilot reference depth (525 us drift, 9000 us electron lifetime, unit spatial correction) the corresponding corrected-S2c boundary is 683.72 phd. The driver now records both values and preserves the sign-based NEST threshold flag. The 645 phd paper comparison is only a raw-threshold numerical comparison unless the paper's observable definition confirms otherwise.


## 16. First event-level NEST pilot completed; flat-spectrum NR band is next (2026-11-15)

A C++ driver now executes the pinned NEST event path `FullCalculation -> GetS1 -> GetS2` with the 2026 Table S5 mean-yield vector and the LZ WS2024 detector class. The driver extracts `s1[5]` and `s2[7]` as S1c and S2c, following the pinned `execNEST.cpp` `store_signals` mapping.

The paired 248-keV run passed in GitHub Actions: 20,000 events per width vector, same seed `20261115`, same central position ((x=y=0), (t_d=525\,\mu s)), same field/density/detector settings; only the NRERWidthsParam vector differs. Mean S1c is 506.943 phd (WS2024) versus 506.776 phd (generic), and mean S2c is 10263.151 phd versus 10265.004 phd. The mean shifts are smaller than paired Monte Carlo standard errors; SD differences are about -0.23% (S1c) and +0.91% (S2c). This one-point test shows the two width candidates are very close in mean response, not that either is calibrated correctly.

The HEPData Science sample's event at (S1_c=540.07916\,\mathrm{phd}), (S2_c=9267.53\,\mathrm{phd}) is recovered as the paper's candidate. The simple fixed-energy pilot gives 0.740% (WS2024) and 0.715% (generic) empirical fractions in the rectangular joint corner (S1_c\ge S1_{c,obs}), (S2_c\le S2_{c,obs}). These are descriptive Monte Carlo fractions only, not p-values or official NR compatibility probabilities.

Run and artifact:
- [Paired event-level workflow](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43637380941), run ID `43637380941`.
- Artifact ID `14129604751`; SHA-256 `ec8325c5d152310896a683cb123383b899371ddda8a1fc820ad58b0ddabb8644`.
- Report: `lz_2026_extended_nr/LZ_2026_NR_EVENT_LEVEL_PILOT_248KEV.md`.

**Important correction to the next-step definition:** the 2026 paper states that its NR band is formed using flat-in-energy NR recoil spectra and evaluated along lines of fixed S1c; Fig. 2 reports the mean and 10th–90th percentiles in ({S1_c,\log_{10}S2_c}). A single monoenergetic 248-keV simulation is therefore only a sanity check, not a reproduction of the published NR band. A second workflow now generates a flat 5.4–269.9 keV spectrum at the central reference position and bins (log_{10}S2_c) by S1c. This first pass still omits the spatial averaging, full FV, and calibration nuisance treatment. See [the 2026 paper, Fig. 2 description and calibration section](https://arxiv.org/abs/2609.02823).


## 17. Flat-spectrum NR band checked at the candidate reconstructed position (2026-11-15)

The first flat-spectrum band pilot used a central reference position. This was refined after checking the paper's Fig. 3: the candidate is reconstructed at (z=26.4\,\mathrm{cm}) above the cathode and near (r=45.9\,\mathrm{cm}). The event generator now uses (x=459\,\mathrm{mm},y=0,z=264\,\mathrm{mm}), invoking the WS2024 detector class's position-dependent S1/S2 corrections.

The paper's Fig. 2 caption states that bands are built from flat-in-energy recoil spectra and evaluated along fixed-S1c lines; the NR calibration coverage is D-D 0–74 keV and AmBe 0–330 keV. Because the caption does not state the exact flat-spectrum interval, two alternatives were simulated (200,000 events per width vector, same seed): uniform 5.4–269.9 keV (analysis window) and uniform 0.1–330 keV (approximately the full AmBe NR calibration range).

Using a 5-phd S1c bin (540\le S1_c<545\), the candidate's position relative to the median NR band is:
- analysis-window prior: (-1.54\sigma_{eq}) (WS2024), (-1.61\sigma_{eq}) (generic);
- full AmBe-range prior: (-1.65\sigma_{eq}) (WS2024), (-1.59\sigma_{eq}) (generic).

Here (sigma_{eq}=(Q_{90}-Q_{10})/2.5631), a Gaussian-equivalent scale derived from the central 80% interval. The range (-1.54) to (-1.65\sigma_{eq}) is close to the paper's stated (-1.5\sigma) displacement. This is a strong local-position cross-check, but not an exact reproduction: the exact flat-spectrum prior, full spatial sampling, exact 2026 best-fit NEST configuration, nuisance covariance, and full calibration distributions remain to be established.

- Workflow: [run 43638132096](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43638132096), successful.
- Artifact ID: `14130821456`, SHA-256 `4fd583cb3f7cf0eaeff6be3b06be1a51d1739b3db3cdac9fc5ad6a0a0a113559`.
- Full report: `lz_2026_extended_nr/LZ_2026_NR_FLAT_BAND_PILOT.md`.
