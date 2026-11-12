# AFH selected-response regression and interpolation audit

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

A local high-precision grid-refinement diagnostic was also performed at all 28 selected momenta. It evaluates neighboring AFH nodes around each selected point and then applies PCHIP locally:

| Local grid spacing | Maximum relative interpolation residual |
|---:|---:|
| 0.25 MeV | \(8.83\times10^{-3}\) |
| 0.125 MeV | \(3.68\times10^{-4}\) |
| 0.0625 MeV | \(1.00\times10^{-4}\) |
| 0.03125 MeV | \(7.31\times10^{-6}\) |
| 0.015625 MeV | \(1.61\times10^{-6}\) |

This is a selected-point local refinement diagnostic, not yet a full 16807-node global convergence study. It nevertheless demonstrates that the original 0.25 MeV spacing can be inadequate near narrow response minima.

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

The selected-point fold must use the direct exact-q response table, or a separately demonstrated sufficiently refined/adaptive grid. The current `run_ame2020_natural_xenon_halo_fold.py` still interpolates the 2401-node grid with PCHIP. **Its seven-isotope rates are not accepted until that interpolation is replaced or validated.**

Additional boundaries:

- Xe-124 and Xe-126 still lack AFH v6.0 built-in default-density matrices. Their \(A^2\) values remain a coherent-charge ceiling only, not AFH central responses.
- The seven-isotope AFH abundance coverage is 0.998158; no renormalization of the seven available isotope abundances is applied.
- The selected-point mpmath check is not a native Mathematica execution and does not validate the full continuous response curve.
- The complete AME2020 seven-isotope halo fold and its final rate tables remain pending.

## 7. CI and archival record

- [Run 43203928812](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43203928812): uploaded the pointwise diagnostic artifact despite the original regression failure.
- [Run 43205816978](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43205816978): passed the corrected historical-PCHIP reproduction test, extracted all seven matrices, generated all 16807 response rows, and archived the native files on the research branch.
- The follow-up run adding the independent 60-digit selected-q validator is recorded in the linked workflow history. Its result must be checked before the exact-q table is treated as an archived CI-validated input.

No result in this audit is a reason to merge the seven-isotope AME2020 fold into `main`. The Draft PR must retain the interpolation limitation and keep the fold unaccepted until the exact-q response table is used and the rate-level checks are rerun.
