# LZ 2026 NEST configuration provenance audit

Date: 2026-11-15  
Branch: `research/figure2-p0-4-mainline`

## Executive conclusion

The user-supplied HEPData v1 ZIP does **not** contain an independent NEST configuration resource. It contains `submission.yaml` and 46 table YAML files; `submission.yaml` has no `additional_resources` field. The HEPData JSON endpoint could not be independently inspected because it returned HTTP 403 in the retrieval workflow, so this conclusion is scoped to the supplied v1 archive and the 46-table HEPData collection described in the independent literature.

A much stronger public candidate was found separately in the upstream NEST repository:

- `include/Detectors/LZ_WS2024.hh`
- `LZ_Detector_2024::SetEFT2024Configuration()`
- configuration added in commit `307fb27d4c2f9b48dba27529bb57bc243e0ce2dc` (2026-08-27)
- audited at commit `541b6430dae6ea289cf110c99f174a9187f7fdee` (2026-09-09)

This is an LZ-specific executable parameter set containing the Table S5 NR mean-yield vector at higher precision, Table S3 ER mean-yield vector, and a 17-element NR/ER fluctuation vector that includes the Table S4 double-skewed-Gaussian parameters. An independent 2026 study uses this exact commit and states that the configuration is not contained in any tagged NEST release. The authors also explicitly caution that the link to the exact LZ Letter production build is circumstantial, not proven. Therefore we label it **EFT2024 public LZ configuration candidate**, not “officially confirmed LZ 2026 production configuration”.

Machine-readable source record:
`lz_2026_nest_eft2024_configuration_candidate.json`.

## 1. HEPData archive result

Archive:
- `HEPData-ins3199115-v1.zip`
- SHA-256: `ab02f6eacd1008a260f0eb8f441beb206069e18f10c6b7b2f44fcfd70463f1f1`
- DOI: `10.17182/hepdata.182472.v1`

Direct archive inspection:
- 47 members: one `submission.yaml` plus 46 table YAML files.
- `submission.yaml` has no `additional_resources` key.
- No NEST header, configuration file, `NRERWidthsParam`, or calibration sample is present in the ZIP.
- The archive contains the three observed search samples (Science, Prompt Veto, Delayed Veto) and the published limit/significance tables.

A GitHub Actions request to the HEPData record JSON and YAML endpoints returned HTTP 403. This means we did not inspect a separate record-page attachment outside the ZIP. The independent response-model paper identifies the HEPData collection as 46 tables and cites the NEST GitHub commit separately. The defensible statement is therefore: **no separate NEST configuration is present in the supplied HEPData v1 table archive; the executable candidate configuration is in the public NEST Git repository, not in that ZIP.**

Do not write that the NEST header was downloaded from HEPData.

## 2. Exact public NEST candidate

The audited NEST source is:
- Repository: https://github.com/NESTCollaboration/nest
- Commit: `541b6430dae6ea289cf110c99f174a9187f7fdee`
- File: `include/Detectors/LZ_WS2024.hh`
- Method: `LZ_Detector_2024::SetEFT2024Configuration()`

The configuration method overrides:
- `g1 = 0.1104`
- `g1_gas = 0.07753555`
- `s2_thr = 120` phe
- `eLife_us = 15000`

It selects the three EFT2024 vectors listed below. Other detector settings remain inherited from the LZ detector class initialization, so this is a complete *public class configuration*, not merely three free parameter arrays.

### 2.1 NR mean-yield parameters: Table S5 versus code

Printed Table S5 (rounded):
`{11.2, 1.1, 0.052, -0.0533, 10.8, 0.53, 1.4, 0.31, 2.5, 0.50, 1.39, 1.74, 0.0230, 0.0289, 74.7}`

EFT2024 source vector:
`{11.21, 1.113, 0.0522, -0.0533, 10.8, 0.53, 1.41, 0.31, 2.5, 0.5, 1.39, 1.74, 0.023, 0.0289, 74.7}`

The first twelve entries specify the baseline NR mean-yield model; entries 12–14 (zero-based) provide the high-energy exponent modification (a,b,E_0). The source vector is the higher-precision executable value; Table S5 is a rounded presentation. Use the executable vector for the primary candidate run and retain the printed vector as a source-table comparison.

### 2.2 ER mean-yield parameters: Table S3 versus code

Printed Table S3:
`{12.31, 84.91, 0.5707, 2.804, 34.04, 0, 82.57, 4.557, 0.2207, 0.1272}`

EFT2024 source vector:
`{12.31, 84.91, 0.5707, 2.804, 34.04, -1, 82.57, 4.557, 0.2207, 0.1272}`

This is not a rounding difference. In the pinned `GetYieldBetaGR` implementation, element 5 is a sentinel: a negative value activates the density/W-value correction branch; zero does not. Thus the executable EFT2024 configuration and the literal printed Table S3 vector are not identical. Both must be retained as explicit ER alternatives until the collaboration's convention is confirmed.

### 2.3 NR and ER fluctuation parameters: Table S4 and executable vector

EFT2024 source vector (17 elements):
`{1.076, 1.061, -0.707, 0.5, 0.19, 2.25, -0.000905, 0.03174, 2.588, 0.3627, -0.3583, 0.0, 0.02377, 0.06211, 5.2, 1.359, -2.599}`

The vector serves both NR and ER branches of `GetQuanta`.

For NR, the relevant zero-based entries are 0, 1, 2, 3, 4, 5, 11, and 12:
- (F_i=1.076+0.0,N_i) in the implemented linear parameterization;
- (F_{ex}=1.061+0.02377,N_{ex});
- the negative entry (p_2=-0.707) sets (lambda_{m Chen}=1+p_2=0.293) in the NR binomial recombination term, while the negative (omega_{m NR}) is clipped to zero by `RecombOmegaNR`;
- (p_5=2.25) is the NR recombination skewness.

For ER, the relevant entries include:
- (p_6=-0.000905), which activates the energy/field-dependent Fano correction;
- (p_7ldots p_{10}=(0.03174,2.588,0.3627,-0.3583)), first (sigma_p) component;
- (p_{13}ldots p_{16}=(0.06211,5.2,1.359,-2.599)), second (sigma_p) component.

These eight component values reproduce the Table S4 entries. The NEST implementation applies normalization factors to the skew-Gaussian components. Do not replace `RecombOmegaER` by a literal transcription of the printed Supplemental Eq. (4) without checking the normalization convention.

The ER charge-sampling skew-normal shape parameter is a separate part of `GetQuanta`; it is not either (alpha_i) from Table S4. With the default `SkewnessER=-999` path, the pinned code evaluates its LUX Run04 energy/field-dependent skewness formula. This distinction is essential for ER tails and the 2D ER PDF.

## 3. Three distinct parameter families

| Family | Mean yields | Fluctuations | Meaning |
|---|---|---|---|
| Table S5 / S3 printed values | Rounded Table S5 NR; Table S3 ER literal (m_6=0) | Not fully specified by those tables alone | Published tables; not a complete executable configuration |
| EFT2024 public LZ configuration | Full-precision NEST header vectors | Full 17-element NRERWidthsParam including Table S4 | Strongest public LZ-specific candidate; not proven to be the exact LZ 2026 production build |
| WS2024 configuration | WS2024 NR/ER mean-yield vectors | 13-element WS2024 NRERWidthsParam | Earlier LZ detector/calibration baseline; not the extended-NR 2026 fit |
| Generic NEST defaults | Upstream default NR/ER vectors | Upstream default 13-element NRERWidthsParam | Generic software defaults; not LZ-tuned |

The exact values and source paths are in the JSON record.

## 4. Consequence for previous event-level NR band results

The previous 248-keV and flat-spectrum pilots used:
- NEST commit `423b9745`;
- the rounded Table S5 NR mean-yield vector;
- the WS2024 width vector or generic default width vector;
- the default `LZ_Detector_2024` initialization (WS2024 physical overrides), without calling `SetEFT2024Configuration()`.

They were useful API and sensitivity checks, but they were **hybrid comparison runs**, not the public EFT2024 executable configuration. In particular:
- they did not use the 17-element EFT2024 fluctuation vector;
- they did not use EFT2024 `g1`, `g1_gas`, `s2_thr`, or `eLife_us`;
- their WS2024-versus-generic comparison changed only width vectors while keeping the same Table S5 mean-yield vector.

The old reports remain archived for reproducibility, but their numerical NR-band residuals must not be presented as the primary LZ 2026 response result. The next production-candidate run must use NEST commit `541b643`, call `SetEFT2024Configuration()`, and separately compare WS2024 and generic baselines.

## 5. NR calibration-band reconstruction plan

The paper defines the bands as flat-in-energy ER/NR spectra evaluated along fixed-(S1_c) lines, reporting the mean and 10th–90th percentiles in ({S1_c,log_{10}S2_c}). The NR calibration coverage is D-D up to 74 keV and AmBe up to 330 keV.

Two spatial prescriptions will be kept separate:
1. **Candidate-position diagnostic:** (rsimeq45.9) cm and (z=26.4) cm above cathode. This is only a local check.
2. **Uniform-active-TPC proxy:** uniform in volume inside the public detector class's cylindrical active geometry. This is a transparent spatial prior, not a claim to reproduce the actual D-D/AmBe calibration source distribution.

The full band will be generated for the EFT2024 candidate, WS2024, and generic NEST defaults with common energy and position seeds. The report must state the prior and detector configuration for every sample. Calibration-source position distributions and event-level calibration data are not present in the HEPData table ZIP, so the uniform-volume proxy cannot be called an exact reproduction of the collaboration's calibration sample.

## 6. ER fluctuations and 2D response plan

Use the same audited NEST commit and the EFT2024 public configuration as the primary executable candidate:
- ER mean yields from `ERYieldsParam_EFT2024`;
- ER fluctuations from indices 6–10 and 13–16 of the 17-element `NRERWidthsParam_EFT2024`;
- the NEST `RecombOmegaER` implementation, including its normalization;
- the separate ER charge skew-normal shape parameter in `GetQuanta` (default LUX Run04 energy/field-dependent path unless an explicit alternative is tested).

Run at least two ER mean-yield conventions:
- executable EFT2024 vector with (m_6=-1);
- literal Table S3 vector with (m_6=0).

Then generate event-level ((S1_c,log_{10}S2_c)) samples and construct normalized conditional PDFs. Keep the conditional PDF separate from selection efficiency; apply S1/S2 cuts exactly once. The ER band central quantiles can be compared with Fig. 2, but do not infer a physical (10^{-7})-level ER tail uncertainty from central quantiles alone.

## 7. Sources and caveats

- LZ Collaboration, arXiv:2609.02823v1, Supplemental Tables S3–S5 and Fig. 2.
- HEPData v1 table archive, DOI 10.17182/hepdata.182472.v1 (46 tables).
- NEST repository commit 307fb27 (adds EFT2024 configuration) and commit 541b643 (audited full vectors).
- Bandyopadhyay, Ramasamy, and TP, arXiv:2610.27105, especially its discussion of the 541b643 configuration, tagged-release status, and caveat that the exact collaboration build has not been established.

**No exact official LZ 2026 detector likelihood or calibration sample reproduction is claimed by this audit.**
