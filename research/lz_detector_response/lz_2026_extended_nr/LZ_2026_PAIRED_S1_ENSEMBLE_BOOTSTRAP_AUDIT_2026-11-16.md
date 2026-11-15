# LZ 2026 paired S1 ensemble-map bootstrap and exact randomization audit

**Status:** `BOOTSTRAP_AND_RANDOMIZATION_DIAGNOSTIC_ONLY`  
**Date:** 2026-11-16  
**Source production:** [GitHub Actions run 43750948249](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43750948249)  
**Source artifact:** `14176882910`  
**Source artifact SHA-256:** `606397d9eac594008630a18b97f1e72fbbfa1d157e34779de7ce5fd0fe5b8cb5`

## 1. Purpose

The ten-seed paired Parametric/Full S1 production already supplied point estimates for the total-variation (TV) distance between the two ensemble-mean 2D response maps. This audit adds uncertainty diagnostics without regenerating NEST events:

1. a paired, seed-cluster nonparametric bootstrap of the ensemble-mean-map TV;
2. leave-one-seed-out influence checks;
3. an exact paired randomization test over all within-seed Parametric/Full label swaps;
4. reproduction closure against the archived per-seed summaries, ensemble summaries, and ensemble mean-map cells.

The resampling unit is the **independent NEST production seed**, not an individual event. Parametric and Full maps from a selected seed are always kept together.

## 2. Provenance and input validation

The immutable production contains ten independent seeds:

`20261117, 40261117, 60261117, 80261117, 100261117, 120261117, 140261117, 160261117, 180261117, 200261117`.

Each seed contains 470,000 events across 235 one-keV true-recoil strata, for 4,700,000 events total. The paired production uses identical intrinsic NR quanta and true position for the two S1 modes, independent Parametric/Full S1 response draws, and one shared Full S2 draw per event. The detector configuration is `LZ_Detector_2024::SetEFT2024Configuration()` with NEST commit `541b6430dae6ea289cf110c99f174a9187f7fdee`.

The production ZIP digest matches the recorded digest above. All 75 entries in the ZIP's internal `SHA256SUMS` manifest were independently checked against their archived bytes. The analysis script additionally rechecks the hashes of the 14 required map/summary/manifest inputs before calculation.

The native observable grid is 10 phd in S1 and 0.02 dex in `log10(S2c)`. The four benchmark spectra are red (200 keV), green (300 keV), black (360 keV), and blue (300 keV, `Delta m = 10 MeV`), with GCN and JJ55 nuclear-response spectra. Both the NEST-threshold stage and WS-ROI stage are analyzed.

## 3. Definitions and methods

For seed `s`, let `P_s(i)` and `F_s(i)` be the event-weighted Parametric and Full rate-map contents in 2D cell `i`. The equal-weight ensemble maps are

\[
\bar P(i)=\frac{1}{10}\sum_{s=1}^{10}P_s(i),\qquad
\bar F(i)=\frac{1}{10}\sum_{s=1}^{10}F_s(i).
\]

The reported point statistic is

\[
\widehat T=\frac12\sum_i\left|
\frac{\bar P(i)}{\sum_j\bar P(j)}-
\frac{\bar F(i)}{\sum_j\bar F(j)}
\right|.
\]

### 3.1 Paired seed-cluster bootstrap

- 100,000 bootstrap replicates.
- Each replicate samples ten seed labels with replacement from the ten observed seeds.
- The same resampled seed indices are applied to the Parametric and Full maps, preserving the within-seed pairing.
- Each replicate recomputes the equal-weight mean rate map for each mode, renormalizes the two maps separately, and evaluates TV.
- RNG: NumPy `default_rng`, seed `2026111601`.
- The report records both the 2.5/97.5 percentile range and the reflected/basic interval.

TV is a non-negative, non-smooth L1 functional. With only ten clusters, the percentile distribution is visibly shifted above the observed point estimate. A BCa trial was also inspected, but its bias-correction tail was degenerate/extreme for several combinations; it is therefore not reported as a usable interval. The percentile and basic intervals are retained as **method-sensitivity diagnostics**, not as a formal equivalence interval.

### 3.2 Leave-one-seed-out check

For each seed, that seed is removed and the two remaining nine-seed mean maps are rebuilt. The range over ten omissions indicates whether the point estimate is controlled by one particular seed.

### 3.3 Exact paired randomization test

For each seed pair, the Parametric and Full labels are either retained or swapped. All \(2^{10}=1024\) combinations are enumerated. The test statistic is the same ensemble-mean-map TV. The inclusive p-value is the fraction of swaps with a TV at least as large as observed.

The null is exchangeability of the two mode labels at the independent-seed cluster level. This is a test for evidence of a systematic mode difference; **failure to reject is not an equivalence result**. Holm adjustments are reported for (i) all 16 benchmark/nuclear/stage combinations and (ii) the eight WS-ROI combinations.

## 4. Main WS-ROI results

All values below are percentages. `Bootstrap percentile` and `basic` are shown side by side because their difference is itself an important diagnostic of the small-sample, non-smooth statistic.

| Benchmark | Nuclear | Ensemble TV | 95% bootstrap percentile | 95% basic/reflected | Leave-one-out range | Exact p | Holm p, all 16 |
|---|---|---:|---:|---:|---:|---:|---:|
| Red, 200 keV | GCN | 0.649 | 0.703–0.998 | 0.300–0.595 | 0.656–0.690 | 0.00195 | 0.03125 |
| Red, 200 keV | JJ55 | 0.649 | 0.703–0.998 | 0.300–0.595 | 0.656–0.689 | 0.00195 | 0.03125 |
| Green, 300 keV | GCN | 0.648 | 0.707–1.038 | 0.259–0.589 | 0.648–0.698 | 0.00977 | 0.11719 |
| Green, 300 keV | JJ55 | 0.648 | 0.707–1.037 | 0.258–0.589 | 0.647–0.697 | 0.00977 | 0.11719 |
| Black, 360 keV | GCN | 0.943 | 1.051–1.598 | 0.288–0.835 | 0.955–1.011 | 0.36914 | 1.00000 |
| Black, 360 keV | JJ55 | 0.932 | 1.038–1.579 | 0.285–0.826 | 0.942–0.998 | 0.37305 | 1.00000 |
| Blue, 300 keV, `Delta m=10 MeV` | GCN | 0.648 | 0.707–1.038 | 0.259–0.589 | 0.648–0.698 | 0.00977 | 0.11719 |
| Blue, 300 keV, `Delta m=10 MeV` | JJ55 | 0.648 | 0.707–1.037 | 0.259–0.589 | 0.647–0.697 | 0.00977 | 0.11719 |

For the eight WS-ROI tests alone, the Holm-adjusted p-values are 0.01563 for the two red rows, 0.05859 for the green and blue rows, and 0.73828 for the two black rows.

### 4.1 Interpretation of the black benchmark

The black benchmark is the critical case:

- The ten-seed point estimate is below 1%: 0.943% (GCN) and 0.932% (JJ55).
- The 95% bootstrap percentile upper endpoints are 1.598% and 1.579%, respectively.
- The GCN leave-one-seed-out range reaches 1.011%; JJ55 ranges from 0.942% to 0.998%.
- The exact paired randomization p-values are 0.369 and 0.373 (Holm-adjusted WS-ROI p = 0.738).

Therefore, the ten-seed point estimate below 1% is **not robust enough to support a 1% equivalence claim**. The randomization test does not find a statistically unusual systematic 2D mode difference, but this is not proof that the modes are equivalent. The bootstrap interval method sensitivity is substantial and should not be hidden.

The mean per-seed TV is much larger than the ensemble-mean-map TV: 2.916% (95% Student-t interval 2.794–3.037%) for GCN and 2.883% (2.763–3.004%) for JJ55. These are different statistics: the former averages ten per-seed distances; the latter measures the distance between the two maps after averaging the ten seeds.

### 4.2 Red, green, and blue benchmarks

The red WS-ROI rows have exact paired-randomization p = 0.00195 and Holm-adjusted p = 0.03125 across all 16 tests. This is evidence for a small but systematic Parametric/Full map difference despite the 0.649% point TV.

Green and blue have raw p = 0.00977, but their Holm-adjusted p = 0.117 across all 16 tests (0.05859 within the eight WS-ROI tests). They do not pass a 5% family-wise threshold after correction. This is not evidence of equivalence.

## 5. NEST-stage cross-check

The black NEST-stage point TVs are 1.168% (GCN) and 1.154% (JJ55), with exact paired-randomization p-values 0.309 and 0.328. Their bootstrap percentile ranges are 1.323–1.972% and 1.309–1.950%. The full 16-row result, including the other benchmarks and both nuclear responses, is in `paired_s1_ensemble_tv_bootstrap_summary.csv` and `paired_s1_ensemble_tv_exact_paired_permutation.csv`.

## 6. Reproduction closure

The new implementation reproduces the archived quantities to floating-point precision:

| Closure | Maximum absolute difference |
|---|---:|
| Recomputed per-seed TV vs archived per-seed TV | `2.78e-17` |
| Recomputed ensemble-mean-map TV vs archived ensemble TV | `1.56e-17` |
| Recomputed mean-map cell vs archived mean-map cell | `8.27e-25` |

The code also verifies that all ten seeds contain the complete 32 mode/stage map set, that the archive's required input checksums match, and that the ensemble mean-map cells close to the seed maps.

## 7. Scientific conclusion and next step

This audit closes the **first bootstrap/statistical diagnostic pass**, not the detector-response validation. It establishes that:

1. the archived ten-seed maps and summaries are internally reproducible;
2. the black 360-keV WS-ROI point estimate below 1% is not a robust equivalence statement;
3. the red benchmark has a statistically detectable mode-shape difference under the paired seed-level randomization test;
4. the ten-seed TV uncertainty is method-sensitive because TV is non-smooth and the number of independent seed clusters is small.

The next numerical improvement should be additional independent NEST seeds, especially for the black benchmark, while retaining the same event design, energy strata, NEST configuration, and map binning. Do not use a coarser histogram merely to force the TV below a threshold.

This remains an EFT2024 NEST response diagnostic, not the official waveform-level LZ selected-event PDF. DAQ trigger, SS reconstruction/data-analysis cuts, official FV, Skin/OD veto partitions, live-time migration, and their joint covariance are not included. No detector-systematic interval, final profile likelihood, or 90% CL exclusion is authorized by this audit.

## 8. Reproduction

From the repository root:

```bash
python -m pip install numpy==2.3.5
python -m unittest research.lz_detector_response.tests.test_paired_s1_ensemble_tv_bootstrap -v
python research/lz_detector_response/paired_s1_ensemble_tv_bootstrap.py \
  --seed-root research/lz_detector_response/lz_2026_extended_nr/paired_s1_independent_seeds_2026-11-15 \
  --out-dir /tmp/lz-s1-bootstrap \
  --n-bootstrap 100000 \
  --rng-seed 2026111601
```

The output directory contains the 16-row bootstrap summary, 160-row leave-one-seed-out table, 160-row reproduction-closure table, exact paired-randomization results, metadata, and a SHA-256 manifest. The full 100,000-value-per-observable bootstrap samples are not committed; the script and fixed RNG seed reproduce the summary without storing an 82-MB raw distribution CSV.