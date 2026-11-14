# LZ 2026 flat-spectrum NR band pilot at the candidate position

**Status:** two 200,000-event-per-sample NEST simulations completed successfully. The output reproduces the reported candidate's approximate displacement from the NR median at the correct approximate reconstructed location. This remains a candidate-model cross-check, not an exact reconstruction of the collaboration's final band.

## 1. Source prescription and position

The LZ paper says Fig. 2's ER and NR bands are formed from flat-in-energy recoil spectra and evaluated along lines of fixed S1c, with the mean and 10th–90th percentiles in ({S1_c,\log_{10}S2_c}). The NR calibration coverage is stated as D-D neutrons from 0–74 keV and AmBe neutrons from 0–330 keV. The caption does not explicitly state the exact flat-energy simulation interval used for the displayed band.

The event's reconstructed position is reported as 26.4 cm above the cathode. Fig. 3 places it near (r^2=(45.9\,\mathrm{cm})^2). The pilot therefore uses:
- (r=459\,\mathrm{mm}), represented by (x=459\,\mathrm{mm}, y=0);
- (z=264\,\mathrm{mm}) above the cathode;
- the LZ WS2024 detector class's position-dependent `FitS1` and `FitS2` corrections;
- the LZ 2026 Table S5 NR mean-yield vector;
- two NR width choices: LZ WS2024 tuned and generic NEST defaults.

Azimuthal variation, reconstructed-position resolution, the full fiducial-volume distribution, and the collaboration's exact 2026 response parameter file are not included.

## 2. Reproducibility

- Workflow: [LZ 2026 flat-spectrum NR band pilot](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43638132096)
- Run ID: `43638132096`
- Head commit: `3a31f318c6600bd2094c162972e051f289542ddf`
- NEST source commit: `423b9745a5bfbb0402514f1d7955e67445de0810`
- Events: 200,000 per sample, common seed 20261117
- S1c bin width: 5 phd
- Summary uses the candidate bin (540\le S1_c<545\,\mathrm{phd}).
- Candidate: (S1_c=540.07916\,\mathrm{phd}), (S2_c=9267.53\,\mathrm{phd}), (log_{10}S2_c=3.9669640).

Two flat-energy priors were simulated because the paper's caption does not explicitly specify the interval:
1. Analysis-window prior: uniform (E_R\in[5.4,269.9]\,\mathrm{keV}).
2. Full AmBe calibration-range prior: uniform (E_R\in[0.1,330]\,\mathrm{keV}).

## 3. Candidate-bin results

All entries below are quantiles of (log_{10}(S2_c/\mathrm{phd})) in the 5-phd S1c bin containing the candidate.

| Energy prior | Width vector | Events in bin | 10% | Median | 90% | Candidate residual |
|---|---|---:|---:|---:|---:|---:|
| 5.4–269.9 keV | WS2024 | 1200 | 3.975677 | 4.015085 | 4.055889 | (-1.54\sigma_{eq}) |
| 5.4–269.9 keV | Generic | 1203 | 3.978357 | 4.016471 | 4.057095 | (-1.61\sigma_{eq}) |
| 0.1–330 keV | WS2024 | 1286 | 3.979066 | 4.019308 | 4.060329 | (-1.65\sigma_{eq}) |
| 0.1–330 keV | Generic | 1249 | 3.978159 | 4.018567 | 4.061470 | (-1.59\sigma_{eq}) |

Here (sigma_{eq}=(Q_{90}-Q_{10})/2.5631) is a Gaussian-equivalent width inferred from the central 80% interval. It is a descriptive scale, not a fitted Gaussian resolution.

The four values span (-1.54) to (-1.65\sigma_{eq}), close to the paper's statement that the event lies 1.5 sigma below the median NR band at the same S1c.

## 4. Interpretation

1. The event's location relative to the NR median is reproduced at the correct approximate reconstructed radius and depth, not only at the detector center.
2. Both width candidates give similar NR-band quantiles; neither is preferred by this comparison.
3. Changing the assumed flat-energy interval from the analysis window to the full AmBe range shifts the band median by about 0.004–0.005 dex and changes the inferred residual by at most about 0.1 (sigma_{eq}).
4. The paper's Fig. 2 caption does not state the exact energy prior or all detector-response inputs; the best-fit NEST parameters are said to be in the Data Release. Until that complete configuration is recovered, this agreement is a strong cross-check but not proof of exact reproduction.
5. This calculation uses a single reconstructed position, not the calibration samples' spatial distribution or full fiducial-volume averaging. It also omits the 2026 nuisance covariance and full BACCARAT/likelihood chain.

## 5. Artifact

- Artifact name: `lz-2026-flat-spectrum-nr-band-pilot`
- Artifact ID: `14130821456`
- SHA-256: `4fd583cb3f7cf0eaeff6be3b06be1a51d1739b3db3cdac9fc5ad6a0a0a113559`
- Retention: 30 days from 2026-11-14.

## 6. Next gate

Before calling the NR band reproduced:
- recover the exact best-fit NEST response parameters from the full Data Release, especially the final NR fluctuation vector and any position/time-dependent settings;
- determine the exact flat-energy generation interval and spatial sampling used for Fig. 2;
- compare the entire band over S1c, not only the candidate bin;
- validate against the 0–330 keV AmBe calibration distribution and published 10th–90th percentiles without tuning to the candidate.
