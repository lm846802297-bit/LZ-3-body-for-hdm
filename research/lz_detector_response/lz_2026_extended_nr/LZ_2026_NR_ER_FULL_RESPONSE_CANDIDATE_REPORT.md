# LZ 2026 NR/ER full-band and conditional 2D response candidate study

Date: 2026-11-15  
NEST source: `541b6430dae6ea289cf110c99f174a9187f7fdee`  
Status: full-S1c band and conditional response pilots completed; not an official LZ 2026 response reproduction.

## 1. HEPData and configuration provenance

The original supplied archive `HEPData-ins3199115-v1.zip` was inspected directly:
- 47 ZIP members: `submission.yaml` plus 46 table YAML files.
- `submission.yaml` has no `additional_resources` key.
- No NEST header/configuration, `NRERWidthsParam`, or calibration event cloud is in the archive.
- SHA-256: `ab02f6eacd1008a260f0eb8f441beb206069e18f10c6b7b2f44fcfd70463f1f1`.

The 46 tables comprise the three observed samples, 43 model/limit/significance tables, and the associated L01–L20 isoscalar/isovector and inelastic operator results. The observed samples have 1,710 Science, 66 PromptVeto, and 55 DelayedVeto points.

A separate public NEST candidate exists in `include/Detectors/LZ_WS2024.hh`:
- Configuration method: `LZ_Detector_2024::SetEFT2024Configuration()`.
- Added in commit `307fb27d4c2f9b48dba27529bb57bc243e0ce2dc`.
- Audited at commit `541b6430dae6ea289cf110c99f174a9187f7fdee`.
- It is not in a tagged NEST release. Independent work arXiv:2610.27105 uses this commit but explicitly says its link to the exact collaboration build is circumstantial.

The defensible label is **public LZ-specific EFT2024 configuration candidate**, not confirmed LZ 2026 production configuration.

## 2. Parameter-family contract

| Family | NR mean yields | NR/ER fluctuations | Detector settings |
|---|---|---|---|
| Printed Table S5 | 15 rounded NR parameters | Not a complete fluctuation prescription | Not defined by S5 |
| EFT2024 public candidate | 15 higher-precision NR parameters; ER vector from Table S3 implementation | 17-element combined NRERWidthsParam, including Table S4 ER double-skew parameters | EFT2024 overrides: g1=0.1104, g1_gas=0.07753555, S2 threshold=120 phe, electron lifetime=15000 us |
| WS2024 | Earlier LZ NR and ER yield vectors | 13-element WS2024 width vector | Default WS2024 detector configuration |
| Generic NEST | Generic upstream defaults | Generic 13-element width vector | For controlled comparison, generic yield/width model on EFT2024 detector overrides |

Table S5 printed NR vector:
`{11.2,1.1,0.052,-0.0533,10.8,0.53,1.4,0.31,2.5,0.50,1.39,1.74,0.0230,0.0289,74.7}`.

EFT2024 executable NR vector:
`{11.21,1.113,0.0522,-0.0533,10.8,0.53,1.41,0.31,2.5,0.5,1.39,1.74,0.023,0.0289,74.7}`.

Table S3 ER vector prints m6=0, whereas the EFT2024 executable vector uses m6=-1. In the pinned `GetYieldBetaGR`, this is a sentinel selecting the density/W-value correction branch; it is not a small numerical difference. Both ER branches were simulated separately.

The EFT2024 17-element fluctuation vector is:
`{1.076,1.061,-0.707,0.5,0.19,2.25,-0.000905,0.03174,2.588,0.3627,-0.3583,0.0,0.02377,0.06211,5.2,1.359,-2.599}`.

For ER, `RecombOmegaER` uses the Table S4 double-skew-Gaussian components (indices 7–10 and 13–16). The separate ER charge-sampling skewness is another part of `GetQuanta`: the driver leaves `SkewnessER=-999`, invoking the pinned NEST LUX Run04 energy/field-dependent formula. Do not confuse that charge-sampling skewness with the Table S4 two-component recombination-`omega` model.

## 3. Full-S1c NR band proxy

Workflow:
- [Run 43643756589](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43643756589), successful.
- Artifact ID: `14132668480`.
- SHA-256: `6fc29a0756185aae151b2fab18f40f852b6b90ee2260f99ec6d6f234c15e3c3e`.
- 200,000 events per family; common seed 20261118.
- (E_R\sim U(0.1,330)\,\mathrm{keV}).
- Uniform active-TPC cylindrical-volume position proxy.
- NEST `FullCalculation(NR)->GetS1(Parametric)->GetS2(Full)`.
- S1c bins 5 phd; report median and 10th/90th percentiles of (log_{10}S2_c).

This is a **full-S1c-range, uniform-volume response proxy**, not the actual LZ calibration-source distribution. The D-D/AmBe source geometry and calibration cloud are not in the HEPData table ZIP. The band must not be described as the collaboration's exact calibration-band construction.

### Candidate bin (540\le S1_c<545\) phd

Observed event: (S1_c=540.07916\,\mathrm{phd}), (S2_c=9267.53\,\mathrm{phd}), (log_{10}S2_c=3.9669640).

| Family | Events in bin | Q10 | Median | Q90 | Candidate minus median |
|---|---:|---:|---:|---:|---:|
| EFT2024 | 1200 | 3.982859 | 4.017353 | 4.051145 | (-1.89\sigma_{eq}) |
| Table S5 + EFT2024 widths | 1226 | 3.995373 | 4.026981 | 4.061892 | (-2.31\sigma_{eq}) |
| WS2024 | 1390 | 4.087078 | 4.127742 | 4.172742 | (-4.81\sigma_{eq}) |
| Generic NEST | 1334 | 4.136347 | 4.176245 | 4.216530 | (-6.69\sigma_{eq}) |

(sigma_{eq}=(Q_{90}-Q_{10})/2.5631) is a Gaussian-equivalent scale, not a fitted Gaussian resolution. All four samples use the same uniform-volume position prior, true-energy prior, and NEST source commit. The generic family also uses generic NR mean yields, whereas the Table S5 branch changes only the rounded NR mean-yield vector relative to EFT2024.

The EFT2024 candidate is closer to the paper's quoted 1.5-sigma NR-band displacement than WS2024 or generic, but gives about 1.9 sigma in this proxy. This remaining difference is not to be tuned away: the exact calibration-source spatial distribution, final collaboration build, and band-generation details are not confirmed.

**Correction to earlier hybrid pilot interpretation:** the earlier (-1.5\sigma) values were obtained from rounded Table S5 means combined with WS2024 or generic widths and WS2024 detector defaults. Those are hybrid checks, not evidence that two independent LZ width models reproduce the official 2026 band. The earlier result is superseded as the primary comparison.

## 4. ER fluctuation and band pilot

Workflow:
- [ER run 43642038888](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43642038888), successful.
- Artifact ID: `14132651289`.
- SHA-256: `f1a903a68c75f9c787549a64bb69c0d8b661ef0d777ffa2a769b19aee9666c69`.
- 200,000 uniform-active-TPC events for each ER family; 100,000 candidate-position events.
- Uniform true ER energy 0.1–300 keV.
- Conditional PDFs binned in 10-keV true-energy bins, 10-phd S1c bins, and 0.02-dex log10(S2c) bins.

### ER band candidate bin

| ER parameter family | Events in 540–545 phd | Median (log_{10}S2_c) | Candidate residual |
|---|---:|---:|---:|
| EFT2024 executable, m6=-1 | 631 | 4.782903 | (-6.69\sigma_{eq}) |
| Literal Table S3, m6=0 | 677 | 4.788475 | (-6.31\sigma_{eq}) |
| Generic NEST ER defaults | 700 | 4.840292 | (-9.97\sigma_{eq}) |

The EFT2024 ER pilot's (-6.69\sigma_{eq}) is numerically close to the paper's quoted 6.7-sigma displacement below the ER-band median. This is a strong cross-check of the ER model candidate, but it is not proof of the exact official calibration configuration. The ER energy and spatial priors are explicit proxies, not the calibration source distributions.

### Conditional 2D PDFs

For each true-energy bin the ER output stores normalized sparse empirical histograms:
[
P(S1_c,\log_{10}S2_c\mid E_{\rm true}\text{ bin}).
]
The 200k uniform-volume sample contains 30 energy bins over 0.1–300 keV. Both the EFT2024 and literal Table S3 alternatives are retained.

The ER PDF is conditional on the simulated true energy and positive reconstructed S1c/S2c. It is not yet folded with the three-body recoil spectrum, analysis efficiency, background PDFs, or nuisance covariance. The published NR efficiency must be applied exactly once and must not be silently folded into a PDF that already includes selection.

## 5. NR conditional 2D PDFs

A reproducible sparse-histogram exporter is provided in `summarize_lz_2026_nr_conditional_2d_pdf.py`. It constructs:
[
P(S1_c,\log_{10}S2_c\mid E_R\text{ bin})
]
for EFT2024, Table S5, WS2024, and generic NR families using the same 10-keV / 10-phd / 0.02-dex binning.

The compact full-volume NR driver exports corrected S1c/S2c but not the separate S1 coincidence flag. These NR histograms are therefore conditional on positive reconstructed observables, not official post-selection PDFs. The raw event CSVs and resulting sparse 2D histograms must be kept separate from efficiency.

## 6. Interpretation and gates

1. The strongest public configuration candidate is the EFT2024 method at NEST commit 541b643, but it is not proven to be the exact LZ 2026 production build.
2. The earlier Table-S5-plus-WS2024 hybrid result is not the preferred production candidate.
3. The EFT2024 NR band proxy gives (-1.89\sigma_{eq}), while the EFT2024 ER band proxy gives (-6.69\sigma_{eq}). The ER result matches the paper's quoted 6.7 sigma closely; the NR result remains about 0.4 sigma away from the paper's 1.5 sigma.
4. The NR and ER 2D PDFs are conditional response objects. They still need correct energy-prior integration, spatial source weighting, calibration constraints, detector nuisance covariance, and selection-efficiency handling.
5. The uniform active-TPC position prior is not the actual D-D/AmBe calibration source distribution. No official calibration event cloud is in the HEPData ZIP.
6. Do not claim official LZ likelihood reproduction. The science/prompt-veto/delayed-veto event samples are public, but complete BACCARAT signal/background templates and nuisance covariance have not been recovered.

## 7. Next computational step

Use the EFT2024 candidate as the primary response family, with Table S3 m6=0 and WS2024/generic retained as systematic alternatives. Build a three-body-signal conditional PDF by folding the model's true (dR/dE_R) with the NR conditional response, then apply the published NR efficiency once. Keep the ER 2D response as a background-separation diagnostic; do not infer an ER-tail probability from the central 10–90% band alone.
