# AFH selected-response regression and interpolation audit

## 2026-11-16 superseding status: direct exact-q AFH-7 grid is now archived

This audit's original conclusion remains valid for the **historical 28-row PCHIP sample path**: PCHIP interpolation near AFH response curvature/minima is not accepted as a substitute for direct finite-sum evaluation when a precision response is required. The older selected-point runner and its PCHIP samples remain historical records.

A separate full-grid path has since been added to `main` and must not be conflated with that historical PCHIP path:

- Seven AFH v6.0 default-density isotope matrices and seven 2,401-node response tables are committed under `results/full_afh_v6_default_7_isotope_response/`; the combined response table has 16,807 rows and a SHA-256 manifest.
- `run_afh7_hybrid9_continuous_spectrum.py` evaluates the AFH finite sum directly at each exact isotope-specific spatial momentum for the 84-point recoil grid; it does not use the old 28-row PCHIP sample file as the full-grid response source.
- The 84-point AFH-7/Hybrid-9 natural-xenon spectra and baseline metadata are committed under `results/afh7_hybrid9_continuous_2026-11-14/`.
- The high-order audit reports a maximum baseline-to-final spectrum difference of `6.46772e-6`, below the `1e-5` threshold. The full 1,344-row `24x8x8x4` high-order ZIP remains external/checksum-only; the committed spectrum is the `24x6x6x3` baseline plus the high-order summary.
- AFH-7 covers natural atom fraction `0.998158`. Xe-124 and Xe-126 still lack AFH v6.0 default-density matrices; Hybrid-9 uses Helm only for those two isotopes and is not AFH-9.
- A separate seven-isotope AME2020 selected-point halo fold now uses the 56 archived direct exact-q AFH finite-sum responses; its 392 kernel/halo integrals, 784 isotope contributions, 112 rate summaries and SHA-256 manifests are archived under `results/AME2020_DIRECT_EXACT_Q_RECALCULATION_2026-11-12.md` and `results/ame2020_direct_exactq_fold/`. It is a selected-point mass-scheme cross-check, not the 84-point AFH-7 spectrum or a detector-level prediction; it was calculated locally, not by CI.
- The Xe-131 AFH response layer also passed a native Wolfram 14.0.0 / Python comparison at 2,401 q nodes, with maximum relative difference `3.59e-9`. This validates the response layer only; it does not validate the complete Eq. (6) pole-width cross section.

Accordingly, the historical PCHIP warning is **not** a statement that AFH-7 full-grid spectra are absent. It is a warning against using the old interpolated 28-row sample path as if it were the new direct finite-sum grid. The selected-point legacy halo rates also use the old linear-`W^2` low-order kernel and differ from the new threshold-`u^2` AFH-7 grid by about 230–255 ppm at common points; keep those outputs separately labelled.

GCN/JJ55 spectra in `research/three_body_calculation_and_validation/results/natural_xenon_continuous_spectrum/` remain on the legacy linear-`W^2`, `8x8x4` kernel. Their `16x16x8` spot checks reach `2.18895e-4` maximum kernel-order difference across the four benchmarks. A matched threshold-`u^2` rerun is still required before precision cross-model comparisons.

**Status:** diagnostic completed; the 2401-node response grids reproduce the historical PCHIP samples, but the existing PCHIP interpolation is not yet accepted for the precision halo fold.

**Scope:** AFH v6.0 default-density responses for Xe-128, Xe-129, Xe-130, Xe-131, Xe-132, Xe-134 and Xe-136; 28 historical selected points (seven isotopes at four recoil energies); exact spatial momentum
\[
q_A=\sqrt{2m_AE_R+E_R^2}.
\]

This audit does not validate the complete AME2020 natural-xenon halo fold. It isolates the failed AFH response regression and identifies the numerical issue that must be resolved before the fold is accepted.

## 1. Source and archived inputs

- Official AFH v6.0 source archive SHA-256: `4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727`.
- Official `dmformfactor-V6.m` SHA-256: `dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372`.
- Selection: `SetIsotope[54,A,"default","default"]`.
- Extracted matrix entry counts: Xe-128 21; Xe-129 39; Xe-130 21; Xe-131 67; Xe-132 21; Xe-134 21; Xe-136 21.
- Response grid: 2401 nodes per isotope, \(q\in[0,0.6]\) GeV, step 0.00025 GeV; total 16807 response rows.
- The 28-row `input/afh_response_samples.csv` is a selected-point table. It is not the complete 16807-row response grid.

The seven matrices and the 16807-row response grid are now committed on the AME2020 research branch under:

- `input/afh_default_density_matrices/`
- `output/afh_default_xenon_responses/afh_xe_isotope_responses.csv`

Their file hashes are listed in `output/afh_default_xenon_responses/SHA256SUMS.txt`.

## 2. What the two failed CI runs actually tested

The earlier failures were not the same problem.

| Run | Failure | Result |
|---|---|---:|
| [43199233305](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43199233305) | Xe-134 raw \(q=0\) package normalization | relative offset \(2.068\times10^{-4}\) |
| [43199358358](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43199358358) | Direct off-grid AFH response compared with historical selected samples | maximum relative difference \(8.909\times10^{-3}\) |

The Xe-134 zero-momentum offset comes from the finite decimal precision of the built-in AFH OBDME coefficients. The raw value is retained in metadata; the response shape is normalized isotope by isotope to \(R_A(0)=A^2\). The adopted raw-package acceptance threshold is \(5\times10^{-4}\), above the observed largest offset and below a level that would hide an order-percent error.

The second failure required a different diagnosis.

## 3. Historical 28 samples are PCHIP values, not direct off-grid AFH evaluations

For each of the 28 points, three quantities were compared:

1. the historical value in `afh_response_samples.csv`;
2. PCHIP interpolation of the regenerated 2401-node response grid;
3. a direct evaluation of the AFH finite-sum response at the exact sample momentum.

The results are:

| Comparison | Maximum relative difference |
|---|---:|
| Regenerated PCHIP vs historical 28 samples | \(1.1864\times10^{-9}\) |
| Direct finite-sum vs independent 60-digit mpmath | \(3.26\times10^{-13}\) |
| Direct finite-sum vs 2401-node PCHIP | up to \(8.9093\times10^{-3}\) when expressed as direct/PCHIP minus one |

Thus the historical values are reproduced by the regenerated grid interpolation, not by a fresh direct evaluation at the off-grid \(q\). The original regression incorrectly compared item 3 with item 1 and treated their difference as a source or implementation mismatch.

The independent mpmath implementation reorganizes the finite Bessel-element sums by hypergeometric parameter and uses `mpmath.hyp1f1` at 60 decimal digits. It does not call SciPy's `hyp1f1`. At the 28 NIST-mass selected points, the direct SciPy finite-sum values agree with the independent mpmath values to a maximum relative difference of approximately \(3.26\times10^{-13}\).

The reproducible validator is:

```bash
python research/afh_default_density_natural_xenon_halo/verify_afh_selected_q_mpmath.py \
  --matrix-dir /path/to/afh_default_density_matrices \
  --response-csv research/afh_default_density_natural_xenon_halo/output/afh_default_xenon_responses/afh_xe_isotope_responses.csv \
  --selected-samples research/afh_default_density_natural_xenon_halo/input/afh_response_samples.csv \
  --out-dir /path/to/selected_q_mpmath
```

It produces a 56-row direct exact-q response table: seven isotopes, four recoil energies, and both NIST-nuclear and AME2020-nuclear mass schemes. It also records the PCHIP-to-exact residual and the historical PCHIP reproduction residual separately.

## 4. The 2401-node interpolation error is physically relevant

The largest selected-point interpolation residuals, expressed as \(|R_A^{\rm exact}/R_A^{\rm PCHIP}-1|\), are:

| Isotope | Recoil point | Maximum selected-point residual |
|---|---:|---:|
| Xe-128 | 542 keV | \(8.909\times10^{-3}\) |
| Xe-129 | 542 keV | \(1.688\times10^{-5}\) |
| Xe-130 | 267 keV | \(8.822\times10^{-5}\) |
| Xe-131 | 267 keV | \(3.185\times10^{-4}\) |
| Xe-132 | 101 keV | \(9.811\times10^{-4}\) |
| Xe-134 | 542 keV | \(2.001\times10^{-5}\) |
| Xe-136 | 267 keV | \(9.975\times10^{-7}\) |

The sign is point-dependent: for example, the direct Xe-128 response at 542 keV is above PCHIP, whereas the direct Xe-132 response at 101 keV is below PCHIP. This is not a universal multiplicative normalization error.

A local high-precision grid-refinement diagnostic was also performed at all 28 selected momenta. This is a local refinement of the historical PCHIP interpolation path, not a global convergence test of the separately committed direct finite-sum 16,807-row response grid.

| Local grid spacing | Maximum relative interpolation residual |
|---:|---:|
| 0.25 MeV | \(8.83\times10^{-3}\) |
| 0.125 MeV | \(3.68\times10^{-4}\) |
| 0.0625 MeV | \(1.00\times10^{-4}\) |
| 0.03125 MeV | \(7.31\times10^{-6}\) |
| 0.015625 MeV | \(1.61\times10^{-6}\) |

This is a selected-point local refinement diagnostic for the historical PCHIP path; it is not a global convergence study of PCHIP over 16,807 nodes. The new direct finite-sum AFH-7 response grid is separately committed and is not built from this interpolation.

## 5. Impact on the existing NIST natural-xenon selected-point rates

For fixed isotope, recoil energy and halo prescription, the differential rate is linear in \(R_A\). Therefore the NIST mainline isotope contributions can be reweighted by

\[
R_A^{\rm direct}/R_A^{\rm PCHIP}
\]

without repeating the three-body and halo integrals. This is a response-interpolation sensitivity diagnostic, not a new AME2020 calculation.

The maximum total natural-xenon rate shift among the 14 archived benchmark/energy/halo combinations is approximately **15.995 ppm**, at the green benchmark, \(E_R=267\) keV, untruncated-MB diagnostic. At the same point with the truncated SHM baseline, the shift is approximately **13.956 ppm**.

Other representative total-rate shifts are:

| Benchmark / recoil | Halo | Direct-q correction to old total |
|---|---|---:|
| Red, 101 keV | SHM | +1.778 ppm |
| Red, 101 keV | untruncated MB | +2.275 ppm |
| Green, 101 keV | SHM | −1.879 ppm |
| Green, 200 keV | SHM | −0.00396 ppm |
| Green, 267 keV | SHM | +13.956 ppm |
| Green, 267 keV | untruncated MB | +15.995 ppm |
| Green, 542 keV | SHM | −3.723 ppm |

The Xe-131-only AME2020 hybrid shift previously reported as at most 7.87 ppm is therefore provisional. The same interpolation issue affects Xe-131 itself: at 267 keV its selected response differs from the direct exact-q result by approximately \(3.185\times10^{-4}\). The previous Xe-131 AME2020 partial rates and the 7.87 ppm hybrid result must be recomputed with direct exact-q responses before being treated as final.

## 6. Corrected acceptance logic and remaining blocker

The response-generation regression now separates two tests:

- **Historical archive reproduction:** PCHIP from the regenerated 2401-node grid must reproduce the 28 historical PCHIP samples within \(5\times10^{-7}\). This tests reproducibility of the old archive.
- **Off-grid interpolation accuracy:** direct exact-q response is compared with PCHIP and independently checked with mpmath. This is a separate numerical-accuracy diagnostic; it must not be hidden by changing the historical regression tolerance.

The historical `run_ame2020_natural_xenon_halo_fold.py` PCHIP path remains unaccepted for precision rates. A separate `run_ame2020_direct_exactq_natural_xenon_halo_fold.py` has since recomputed the selected-point seven-isotope NIST and AME2020 folds from the 56 archived direct exact-q responses; its local outputs and manifests are recorded in the natural-xenon README. This does not promote the selected-point calculation to a continuous spectrum, and it does not make the old PCHIP path acceptable.

Additional boundaries:

- Xe-124 and Xe-126 still lack AFH v6.0 built-in default-density matrices. Their \(A^2\) values remain a coherent-charge ceiling only, not AFH central responses.
- The seven-isotope AFH abundance coverage is 0.998158; no renormalization of the seven available isotope abundances is applied.
- The selected-point 60-digit mpmath check is an independent high-precision Python validation, not a native Mathematica execution. A separate native Wolfram 14.0.0 / Python Xe-131 2,401-node response-level PASS is now archived; neither response-level check validates the full Eq. (6) pole-width cross section.
- The complete AME2020 seven-isotope halo fold and its final rate tables remain pending.

## 7. CI and archival record

- [Run 43203928812](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43203928812): uploaded the pointwise diagnostic artifact despite the original regression failure.
- [Run 43205816978](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43205816978): passed the corrected historical-PCHIP reproduction test, extracted all seven matrices, generated all 16807 response rows, and archived the native files on the research branch.
- The follow-up run adding the independent 60-digit selected-q validator is recorded in the linked workflow history. Its result must be checked before the exact-q table is treated as an archived CI-validated input.

The old PCHIP-derived selected-point rates remain superseded and should not be merged as precision results. The separate direct exact-q AME2020 selected-point fold is archived with its local outputs and manifests; it remains distinct from the AFH-7 84-point spectrum, the full Eq. (6) Mathematica/Python cross-section audit, and detector-level likelihood. Keep the PCHIP limitation attached to the historical runner rather than applying it to the direct exact-q path.
