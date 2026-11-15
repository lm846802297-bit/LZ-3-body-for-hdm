# LZ 2026 NEST release-lineage and configuration audit

Date: 2026-11-15

**Status:** source-level lineage audited; exact collaboration production build remains unconfirmed.

## Executive conclusion

The LZ paper's citation to **NEST v2.4.5** is consistent with the physics features present in the later public NEST development line, but the public GitHub tag v2.4.5beta at commit 19bc9bc is too early to reproduce the final LZ model described in the Supplemental Material.

The important distinction is that the model features and LZ-specific candidate configuration were added to the public development branch after that beta tag:

- two-component skew-Gaussian ER recombination fluctuations;
- four extra ER-width parameters and their later normalization/ordering fixes;
- the high-energy NR charge-yield exponent p(E);
- the LZ SetEFT2024Configuration method and its full-precision parameter vectors.

The earliest public commit in this lineage that contains the LZ EFT2024 detector configuration is 307fb27 (2026-08-27), six days before arXiv:2609.02823v1 was submitted on 2026-09-02. Commit 541b643 (2026-09-09), used for the present reproducible calculations, adds static getters and changes the parameter vectors to inline static storage; its diff from 307fb27 does not modify src/NEST.cpp or the physical parameter values.

This chronology makes the public EFT2024 configuration a **strong, physically consistent candidate** for the model described in the paper. It still does not prove that the collaboration's internal production executable was built from exactly 307fb27, 541b643, or an identical private fork.

## 1. What the LZ paper actually specifies

The LZ paper states that the detector and model response parameters from NEST v2.4.5 are tuned to ER and NR calibration data, and that the best-fit NEST parameters are supplied in the Data Release. The Supplemental Material explicitly distinguishes the older v2.4.0 response from the final v2.4.5 model:

1. The ER recombination-width model changes from a single skewed Gaussian to a sum of two skew-Gaussian components in x = log10(Nq), with the eight fitted parameters listed in Table S4.
2. The NR charge-yield exponent changes from a constant p to
   \[
   p(E)=0.5+a\ln[1+b(E-E_0)]
   \quad (E>E_0),
   \]
   with p=0.5 below E0. The parameters a, b, E0 are included in Table S5.
3. Tables S3, S4, and S5 give the ER mean-yield, ER recombination-fluctuation, and NR mean-yield parameters, respectively.

Primary paper source: [LZ Collaboration, arXiv:2609.02823v1](https://arxiv.org/abs/2609.02823), main text and Supplemental Material, especially pp. 15–17.

## 2. Public Git history between the beta tag and the LZ candidate

The public NEST repository's v2.4.5beta tag points to commit 19bc9bc063c62961d2f190beec2db16a9e279aa1 (2025-12-08). A direct source comparison from this tag to 541b6430dae6ea289cf110c99f174a9187f7fdee reports 23 intervening commits.

The physics-relevant changes are:

| Commit | UTC date | Public commit message / source-level change | Relevance to the LZ paper |
|---|---|---|---|
| [a5648b2](https://github.com/NESTCollaboration/nest/commit/a5648b23c5c1dd8a2ee6f976b05f1e121c7f1048) | 2026-01-25 | Introduces two (skew-)Gaussian ER recombination fluctuations plus a constant | Required for the two-component ER model in Supplemental Eq. (4) |
| [9ea980a](https://github.com/NESTCollaboration/nest/commit/9ea980a180942e966502b9937f925eeea1579127) | 2026-04-30 | Adds four additional NRERWidthsParam controls for the ER recombination Gaussians | Allows the eight Table S4 component parameters to be supplied |
| [b881d80](https://github.com/NESTCollaboration/nest/commit/b881d80a0bb70ad4d295dd4d1be487d9e134472f) | 2026-05-27 | Updates skew parameters | Part of the later ER fluctuation fit |
| [dc4c1dd](https://github.com/NESTCollaboration/nest/commit/dc4c1dd271820be566d0076502b07db82d1471cb) | 2026-05-27 | Renormalizes skew amplitudes to their maxima | Affects the implemented normalization of the ER fluctuation model |
| [3b81ca1](https://github.com/NESTCollaboration/nest/commit/3b81ca11f68611b385ade7c6eb18a5355afbc265) | 2026-05-28 | Reorders the ER fluctuation variables | Establishes the current parameter ordering |
| [1c1919e](https://github.com/NESTCollaboration/nest/commit/1c1919efeb65efdc6801c738f2633503b8ed305d) | 2026-05-28 | Fixes the second Gaussian mode after parameter overrides | Corrects a real implementation bug in the double-Gaussian branch |
| [423b974](https://github.com/NESTCollaboration/nest/commit/423b9745a5bfbb0402514f1d7955e67445de0810) | 2026-08-16 | Adds energy-dependent NR charge-yield suppression | Implements the high-energy p(E) extension in Supplemental Eq. (5) |
| [307fb27](https://github.com/NESTCollaboration/nest/commit/307fb27d4c2f9b48dba27529bb57bc243e0ce2dc) | 2026-08-27 | Adds SetEFT2024Configuration() and full-precision LZ EFT2024 vectors | Provides the public LZ-specific detector/model candidate |
| [541b643](https://github.com/NESTCollaboration/nest/commit/541b6430dae6ea289cf110c99f174a9187f7fdee) | 2026-09-09 | Adds static getters and inline static storage for the WS2024/EFT2024 vectors | API/provenance change; no change to src/NEST.cpp or the physical values relative to 307fb27 |

The tag-to-commit comparison is available at [GitHub compare: 19bc9bc...541b643](https://github.com/NESTCollaboration/nest/compare/19bc9bc...541b6430dae6ea289cf110c99f174a9187f7fdee). The narrower comparison [307fb27...541b643](https://github.com/NESTCollaboration/nest/compare/307fb27d4c2f9b48dba27529bb57bc243e0ce2dc...541b6430dae6ea289cf110c99f174a9187f7fdee) changes only include/Detectors/LZ_WS2024.hh: static getters are added and the vectors become inline static. There are no changes to the NEST physics implementation between these two commits.

## 3. Direct source comparison: v2.4.5beta versus 541b643

The source comparison was made directly against the pinned NEST files, not inferred from release notes.

| Feature | 19bc9bc (v2.4.5beta) | 541b643 |
|---|---|---|
| LZ_Detector_2024 class | Present | Present |
| SetEFT2024Configuration() | Absent | Present |
| 15-entry NR yield vector and high-energy p(E) parameters | No 15-entry NR extension in GetYieldNR | Present |
| ER recombination fluctuation | Single skew-Gaussian branch | Two skew-Gaussian components in log10(Nq), with optional second-component parameters |
| EFT2024 17-entry NRERWidthsParam | Absent | Present |
| EFT2024 detector overrides | Absent | Present |

At 19bc9bc, the LZ_WS2024.hh class uses the WS2024 parameter family. Its RecombOmegaER implementation has the older single-skew-Gaussian form, and the default width vector has 13 entries. The 15-entry NR-yield branch and the double-Gaussian ER branch required by the 2026 Supplemental Material are absent.

Therefore, compiling the public v2.4.5beta tag and merely copying Table S3–S5 numbers into it is **not** an equivalent implementation of the final model. The code logic itself is different.

## 4. Why 541b643 is a plausible candidate, but not proof

The chronology matters:

- The two-component ER model and high-energy NR p(E) logic were public before the LZ paper was submitted.
- The LZ EFT2024 detector configuration was added on 2026-08-27, before the paper's 2026-09-02 arXiv submission.
- The 2026-09-09 541b643 commit adds getters/storage changes only; it does not change the response physics relative to 307fb27.

Thus the fact that 541b643 itself postdates the paper submission does not imply that the physics model postdates the analysis. The public model/configuration lineage was already present in 307fb27.

Nevertheless, the paper cites a software version, not a Git commit hash. The public source history does not reveal the collaboration's exact internal build, local patches, compiler flags, calibration event selection, or detector maps. The independent study [arXiv:2610.27105](https://arxiv.org/abs/2610.27105) also treats the link between the public 541b643 configuration and the exact LZ production build as circumstantial, not established.

## 5. Independent detector-gain consistency check

The public SetEFT2024Configuration() method changes the WS2024 detector class as follows:

| Parameter | Inherited WS2024 initialization | EFT2024 override |
|---|---:|---:|
| g1 | 0.1122 phd/photon | 0.1104 phd/photon |
| g1,gas | 0.076404 phd/gas photon | 0.07753555 phd/gas photon |
| NEST S2 threshold | 783 phe | 120 phe |
| Electron lifetime | 9000 μs | 15000 μs |

Other detector properties remain inherited from LZ_Detector_2024::Initialization(), including the 8 mm gas gap, 8.301178 kV/cm gas field, 175.9 K temperature, 1.86 bar pressure, 96.5 V/cm drift field, 150 ns S1 coincidence window, threefold PMT coincidence, and 481 active PMTs. OldW13eV also remains true.

Using the pinned CalculateG2 implementation and the inherited WS2024 gas conditions gives:
- gas electroluminescence yield: 613.1904 photons per extracted electron;
- extraction efficiency: 0.726195;
- EFT2024 single-electron size: 613.1904 × 0.07753555 = 47.5441 phd/electron;
- EFT2024 g2 = 0.726195 × 47.5441 = 34.5263 phd/electron.

The paper reports g1=0.110±0.002 phd/photon and g2=34.5±1.1 phd/electron. The candidate differs by 0.20 standard deviations in g1 and 0.024 standard deviations in g2. This is a strong detector-gain consistency check, but it is not a unique fingerprint of the production build.

The EFT2024 NEST S2 threshold of 120 phe is also much lower than the published raw-S2 WS ROI cut of 645 phd. With P_dphe=0.214, 120 phe corresponds to about 98.85 phd before lifetime/position correction. The explicit 645 phd raw-S2 ROI therefore dominates this NEST threshold; it must not be counted as a second independent efficiency loss.

## 6. Response-band cross-check does not uniquely select a configuration

The present uniform-volume full-S1c band proxy gives the following residuals for the event of interest in the 540 ≤ S1c < 545 phd bin:

| Candidate family | Candidate minus median, Gaussian-equivalent |
|---|---:|
| EFT2024 full-precision vector | −1.89 sigma_eq |
| Rounded Table S5 mean vector + EFT2024 widths | −2.31 sigma_eq |
| WS2024 | −4.81 sigma_eq |
| Generic NEST | −6.69 sigma_eq |

The paper quotes −1.5 sigma relative to its calibrated NR band. EFT2024 is the closest public candidate in this proxy, but it remains about 0.39 sigma away. The calibration-source spatial prior, source deployment geometry, and exact band-generation details are not available in the supplied HEPData archive. This difference must not be removed by tuning or by changing the energy prior without provenance.

The separate three-body ROI study also shows that the rounded Table S5 exponent can give a substantially different high-energy S1c acceptance from the full-precision EFT2024 vector. This is a genuine model/provenance dependence, not MC statistical noise.

## 7. Required interpretation and policy

1. Pin 541b6430dae6ea289cf110c99f174a9187f7fdee for the current reproducible **public EFT2024 candidate** because it contains the full implementation and exposes the exact vectors. The physics implementation is already present at 307fb27.
2. Keep the rounded Table S5 vector as a separate alternative. Do not silently substitute its one-decimal beta=1.1 for the full-precision public value 1.113.
3. Keep the Table S3 literal m6=0 and executable EFT2024 m6=−1 ER mean-yield conventions as separate alternatives; the latter is a sentinel selecting the density/W-value correction branch in GetYieldBetaGR.
4. Retain WS2024 and generic NEST as controlled comparison families, not as interchangeable estimates of the same LZ 2026 response.
5. Do not label any of these as the exact LZ 2026 production configuration without a collaboration-provided commit/configuration or an equivalent independent calibration closure.
6. Do not begin the final profile likelihood until the response provenance, calibration spatial prior, and full LZ selection model are resolved.

## 8. Reproduction references

- [LZ 2026 paper, arXiv:2609.02823v1](https://arxiv.org/abs/2609.02823)
- [NEST public v2.4.5beta tag](https://github.com/NESTCollaboration/nest/tree/19bc9bc063c62961d2f190beec2db16a9e279aa1)
- [NEST EFT2024 configuration commit 307fb27](https://github.com/NESTCollaboration/nest/commit/307fb27d4c2f9b48dba27529bb57bc243e0ce2dc)
- [NEST audited commit 541b643](https://github.com/NESTCollaboration/nest/commit/541b6430dae6ea289cf110c99f174a9187f7fdee)
- [Independent public-configuration provenance discussion, arXiv:2610.27105](https://arxiv.org/abs/2610.27105)
