# LZ 2026 NR event-level NEST pilot at 248 keV

**Status:** C++ event-level pilot compiled and ran successfully in GitHub Actions. The paired 20,000-event run passed. This is a candidate-model diagnostic, not an official LZ 2026 response or likelihood reproduction.

## 1. Reproducibility

- Workflow: [LZ 2026 NR event-level NEST pilot](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43637380941)
- Workflow run ID: `43637380941`
- Workflow head commit: `73581c7c3b01a69946f86bba7094db87be72b777`
- NEST source commit: `423b9745a5bfbb0402514f1d7955e67445de0810`
- Detector class: `LZ_Detector_2024` from `include/Detectors/LZ_WS2024.hh`
- Recoil energy: 248 keV NR
- Events: 20,000 per width vector
- Seed: 20261115 for both samples (paired/common random-number stream)
- Reference position: (x=y=0), (z=762.5601\,\mathrm{mm}), selected for (t_d=525\,\mu\mathrm{s})
- Density: (2.8687209\,\mathrm{g/cm^3})
- Drift field: 96.5 V/cm
- NEST S1 mode: Parametric; S2 mode: Full
- Mean yields: LZ 2026 Table S5 15-parameter vector
- Width vectors: LZ WS2024 tuned versus generic NEST defaults
- Output observables: NEST `s1[5]` = S1c phd and `s2[7]` = S2c phd, following `execNEST.cpp`'s `store_signals` mapping.

The two samples share the same event count, seed, energy, position, mean-yield parameters, and detector class; only the NRERWidthsParam vector changes.

## 2. Event-level output

| Observable | WS2024 width vector | Generic NEST widths |
|---|---:|---:|
| Mean photons | 4524.296 | 4523.763 |
| SD photons | 44.448 | 44.615 |
| Mean electrons | 302.194 | 302.289 |
| SD electrons | 17.579 | 17.539 |
| Mean S1c (phd) | 506.943 | 506.776 |
| SD S1c (phd) | 24.055 | 24.111 |
| S1c 10–50–90% (phd) | 476.202 / 506.693 / 538.000 | 476.054 / 506.516 / 537.917 |
| Mean S2c (phd) | 10263.151 | 10265.004 |
| SD S2c (phd) | 729.913 | 723.297 |
| S2c 10–50–90% (phd) | 9360.841 / 10224.234 / 11226.598 | 9370.926 / 10225.710 / 11214.938 |
| Corr(S1c,S2c) | -0.04890 | -0.05422 |
| Corr(Nphotons,Nelectrons) | -0.24550 | -0.24016 |

Relative to the generic-width sample, WS2024 changes the S1c mean by +0.033% and S2c mean by -0.018%. The S1c standard deviation changes by -0.231%; the S2c standard deviation changes by +0.915%.

Paired event-wise differences:
- S1c mean difference: (+0.1674\,\mathrm{phd}\), paired standard error (0.2361\,\mathrm{phd}).
- S2c mean difference: (-1.853\,\mathrm{phd}\), paired standard error (7.117\,\mathrm{phd}).

Thus the mean shifts are smaller than their paired Monte Carlo standard errors. At this one energy and one position, the two width candidates yield very similar mean detector signals and modestly different widths.

## 3. Comparison with the observed candidate

The HEPData Science sample contains the event:
[
S1_c=540.07916\,\mathrm{phd},\qquad S2_c=9267.53\,\mathrm{phd}.
]
The paper reports (S1_c\simeq540.1\,\mathrm{phd}), (S2_c=9268\,\mathrm{phd}), and an NR-consistent reconstructed energy (248\pm23\,(\mathrm{stat})\pm23\,(\mathrm{sys})\,\mathrm{keV}).

Within the fixed-248-keV pilot:
- WS2024 sample: 91.45% of events have S1c at or below the observed S1c; 7.495% have S2c at or below the observed S2c; 148/20,000 (0.740%) lie in the joint corner (S1_c\ge S1_{c,obs}) and (S2_c\le S2_{c,obs}).
- Generic-width sample: 91.495% have S1c at or below the observed S1c; 7.305% have S2c at or below the observed S2c; 143/20,000 (0.715%) lie in the same joint corner.

**These joint-corner fractions are not p-values, likelihood ratios, or NR-rejection probabilities.** They are simple empirical fractions in a fixed-energy, fixed-position simulation. They omit the event's energy and position uncertainties, the full spatial-response maps, calibration nuisance covariance, the joint analysis likelihood, and backgrounds. The LZ paper itself states that the candidate is not conclusively classified as NR versus ER.

## 4. Interpretation

1. The event-level C++ path is now working end-to-end: `FullCalculation -> GetS1 -> GetS2`.
2. The WS2024 and generic NR width candidates are nearly indistinguishable in their mean S1c/S2c response at 248 keV.
3. The current pilot does not validate the high-energy NR width model against calibration data; the 2026 analysis configuration is still not available in the supplied HEPData table ZIP.
4. The candidate event is compatible with being a tail observation under the simulated NR response, but this simplified pilot cannot quantify its probability in the official LZ model.
5. Do not select a preferred width vector from this one-point comparison. Both remain candidate inputs.

## 5. Next validation gates

- Reproduce the NR band as a function of S1c over the 5.4–269.9 keV range, not just a monoenergetic 248-keV point.
- Sample the fiducial spatial distribution and apply the same position-dependent response corrections used in the 2026 analysis.
- Compare against the published NR calibration-band information and the gray efficiency envelope without tuning to the candidate event.
- Obtain or reconstruct the actual 2026 response configuration, including the NR fluctuation vector and nuisance covariance.
- Only after these checks, proceed to the two-dimensional signal PDF and likelihood layer.

## 6. Artifact

The exact CSV outputs and summary JSON are preserved in GitHub Actions artifact `lz-2026-nr-event-level-pilot`, artifact ID `14129604751`, SHA-256 digest:
`ec8325c5d152310896a683cb123383b899371ddda8a1fc820ad58b0ddabb8644`.

Artifact retention is 30 days from 2026-11-14. The source driver and summary script are committed in this branch.
