# Black 360-keV paired S1 upper-tail and ROI-migration audit

**Status:** completed ten-independent-seed diagnostic; not an official LZ detector response or likelihood input.

**Benchmark:** black, production label black_ms360_dm1, \(m_s=360\ \mathrm{keV}\)  
**Response:** EFT2024, pinned NEST commit 541b6430dae6ea289cf110c99f174a9187f7fdee  
**Selection support:** \(E_R\in[205,269.9]\ \mathrm{keV}\)  
**Audit run:** [GitHub Actions run 43762406779](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43762406779)  
**Audit artifact:** [artifact 14181285817](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43762406779/artifacts/14181285817)  
**Audit artifact ZIP SHA-256:** fb1b06d77d9d4c58dd837ab9e657edbcc9e593856fbad6f30c70b1b4866bbe0d  
**Source production:** [run 43750948249](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43750948249), artifact 14176882910  
**Source production ZIP SHA-256:** 606397d9eac594008630a18b97f1e72fbbfa1d157e34779de7ce5fd0fe5b8cb5

## 1. Production and numerical closure

The audit reuses the immutable ten-seed paired Parametric/Full S1 production. No NEST events were regenerated and no detector configuration was changed.

- 10 independent production seeds.
- 470,000 events per seed; 4,700,000 events over the full 35--269.9 keV grid.
- 235 one-keV true-recoil strata; 2,000 events per stratum, split into two disjoint 1,000-event replicas.
- The black support \(205\)--\(269.9\ \mathrm{keV}\) contains 65 strata and 1,300,000 raw paired events.
- GCN and JJ55 recoil spectra are folded separately.
- Parametric and Full S1 use the same intrinsic NR quanta, true recoil energy, true position, and shared S2 draw; their S1 response draws are independent within each event pair.

The event weight in seed \(s\), nuclear model \(M\), and one-keV stratum \(k\) is

\[
w_i=R_{k,\mathrm{exact}}\,
\frac{f_M(E_i)}{\sum_{j\in k}f_M(E_j)},\qquad
f_M(E)=\left.\frac{dR_M}{dE_R}\right|_E .
\]

Here \(R_{k,\mathrm{exact}}\) is read from the original per-seed fold product and \(f_M(E_i)\) is evaluated with the same piecewise-linear interpolation routine used by the original fold. This preserves the within-bin spectral weighting while forcing the sum of event weights in each stratum to equal its exact integrated rate.

The maximum relative closure residual over all ten seeds, both nuclear models, and all 235 strata is

\[
\delta_{\mathrm{closure}}=6.3322\times10^{-15},
\]

against a required tolerance of \(5\times10^{-12}\). The prior unnormalized version of this audit had an approximately 2,000-fold normalization error; it is superseded and must not be used.

The corrected workflow passes all nine unit tests, source-artifact manifest verification, exact per-stratum weight closure, ten-seed row-count validation, black-support selection closure, CSV JSON validation, and both relocatable output/archive checksum manifests.

## 2. Selection definitions

The pinned S1 acceptance is the NEST GetS1 coincidence pass flag together with

\[
3\leq S1_c\leq600\ \mathrm{phd}.
\]

The WS ROI additionally requires the NEST GetS2 threshold pass, strict \(S2_{\mathrm{raw}}>645\ \mathrm{phd}\), and

\[
2.75\leq\log_{10}S2_c\leq4.15.
\]

All reported efficiencies are event-weighted by the exact recoil-spectrum weights above. The S1 quantiles and one-dimensional S1 histograms are conditional on the pinned S1 coincidence pass; they are not truncated at the 600-phd ROI upper boundary.

## 3. Main black-support result

The table gives the ten-seed mean efficiencies. The relative rate change is the mean of the ten seed-level Full/Parametric ratios; its 95% interval is a Student-\(t\) interval over the ten independent production seeds.

| Nuclear response | Parametric S1 ROI | Full S1 ROI | Full/Parametric change | 95% seed-level interval |
|---|---:|---:|---:|---:|
| GCN | 73.9501% | 73.5072% | -0.5983% | [-0.8046%, -0.3920%] |
| JJ55 | 74.3246% | 73.8871% | -0.5881% | [-0.7901%, -0.3860%] |

The corresponding absolute efficiency changes are \(-0.4429\) percentage points (GCN) and \(-0.4375\) percentage points (JJ55).

### 3.1 S1 upper tail

| Quantity, conditional on S1 coincidence | GCN Parametric | GCN Full | JJ55 Parametric | JJ55 Full |
|---|---:|---:|---:|---:|
| Fraction with \(S1_c>600\) phd | 26.0499% | 26.4928% | 25.6754% | 26.1129% |
| \(q_{90}\) [phd] | 647.4 | 648.8 | 646.8 | 648.1 |
| \(q_{95}\) [phd] | 673.8 | 675.4 | 673.2 | 674.7 |
| \(q_{99}\) [phd] | 723.1 | 724.5 | 722.6 | 724.1 |

The listed quantiles are the arithmetic means of the ten seed-level weighted quantiles, not quantiles of a pooled event sample. The Full mode shifts the upper S1 quantiles upward by roughly 1--2 phd. At the 600-phd boundary, this changes the fraction above the cut by \(+0.4429\) percentage points (GCN) and \(+0.4375\) percentage points (JJ55). The sign is therefore consistent with the reduction in the S1 ROI efficiency.

The paired boundary migration is larger than the net acceptance change because events cross in both directions:

| Nuclear response | Parametric \(\leq600\), Full \(>600\) | Full \(\leq600\), Parametric \(>600\) | Net Full loss |
|---|---:|---:|---:|
| GCN | 6.4630% | 6.0201% | 0.4429 percentage points |
| JJ55 | 6.3960% | 5.9585% | 0.4375 percentage points |

These migration fractions are normalized to the total raw event weight in the black support. They are not conditional percentages within the accepted ROI.

### 3.2 Threshold scan around the S1 upper boundary

The following table reports the Full-minus-Parametric change in the fraction
above each S1 threshold, conditional on the S1 coincidence pass. Values are
percentage points; intervals are 95% Student-\(t\) intervals over the ten
paired production seeds. Since both S1 coincidence flags pass for every
event in this support, these conditional differences also equal the
raw-event-weight differences.

| S1 threshold [phd] | GCN tail-fraction difference | JJ55 tail-fraction difference |
|---:|---:|---:|
| 500 | +0.3395 [0.2203, 0.4588] | +0.3436 [0.2249, 0.4623] |
| 550 | +0.4719 [0.3242, 0.6195] | +0.4709 [0.3245, 0.6173] |
| 575 | +0.4757 [0.2951, 0.6563] | +0.4708 [0.2933, 0.6484] |
| 590 | +0.4686 [0.3144, 0.6228] | +0.4637 [0.3124, 0.6149] |
| 600 | +0.4429 [0.2896, 0.5962] | +0.4375 [0.2866, 0.5884] |
| 610 | +0.4543 [0.2912, 0.6175] | +0.4477 [0.2875, 0.6079] |
| 625 | +0.4503 [0.3355, 0.5650] | +0.4432 [0.3307, 0.5556] |
| 650 | +0.2548 [0.1313, 0.3784] | +0.2506 [0.1291, 0.3721] |
| 700 | +0.1048 [0.0402, 0.1694] | +0.1028 [0.0396, 0.1661] |
| 800 | +0.0026 [-0.0071, 0.0122] | +0.0025 [-0.0070, 0.0120] |

The excess Full-mode upper-tail fraction is broad across 550--625 phd,
roughly 0.44--0.48 percentage points, rather than being an isolated
single-bin fluctuation at exactly 600 phd. It decreases above 650 phd and
is consistent with zero by 800 phd. At the actual 600-phd ROI boundary,
the positive tail-fraction difference has the opposite sign to the
accepted-rate difference: more events lie above the cut in Full mode, so
the accepted \(S1_c\leq600\) fraction is smaller.

### 3.3 Distributional differences

All TVs below use the native 10-phd S1 binning; the two-dimensional maps use 10-phd by 0.02-dex cells.

| Metric | GCN | JJ55 |
|---|---:|---:|
| Ensemble-mean conditional S1 histogram TV | 0.5957% | 0.5896% |
| Ensemble-mean S1 upper-tail TV, conditional on \(S1_c>500\) phd | 0.5832% | 0.5763% |
| NEST-stage \((S1_c,\log_{10}S2_c)\) TV | 1.1679% | 1.1538% |
| WS-ROI \((S1_c,\log_{10}S2_c)\) TV | 0.9425% | 0.9318% |
| Mean per-seed conditional S1 histogram TV | 1.4559% | 1.4378% |

The ensemble-mean S1 histogram TV is below 1%, but the mean per-seed TV is about 1.44--1.46%. The NEST-stage two-dimensional TV also remains above the 1% point-estimate engineering threshold, while the WS-ROI two-dimensional TV is just below it. These are different statistics and must not be conflated. The ensemble mean does not establish Parametric/Full equivalence.

The cluster-bootstrap TV intervals are retained in the machine-readable metadata as descriptive resampling diagnostics only. They are not detector-systematic intervals or a formal equivalence test. In particular, the percentile interval for the full S1 histogram is skewed and its lower endpoint lies slightly above the observed TV point estimate; no inference is based on that interval.

## 4. Energy-resolved migration

The Full/Parametric S1 ROI rate shift grows toward the highest recoil-energy band. The intervals below are seed-level 95% Student-\(t\) intervals.

| True recoil band [keV] | GCN change | GCN 95% interval | JJ55 change | JJ55 95% interval |
|---|---:|---:|---:|---:|
| 205--225 | -0.0603% | [-0.1404%, +0.0198%] | -0.0603% | [-0.1404%, +0.0199%] |
| 225--240 | -0.1614% | [-0.2396%, -0.0833%] | -0.1617% | [-0.2402%, -0.0833%] |
| 240--255 | -0.2977% | [-0.5047%, -0.0907%] | -0.2983% | [-0.5049%, -0.0916%] |
| 255--269.9 | -1.0337% | [-1.4421%, -0.6252%] | -1.0335% | [-1.4427%, -0.6244%] |
| Legacy tail, 225.4--269.9 | -0.6479% | [-0.8775%, -0.4182%] | -0.6372% | [-0.8625%, -0.4120%] |

The lowest band is consistent with zero at this Monte Carlo precision. The highest band shows about a 1.03% relative loss and dominates the energy dependence. The two nuclear-response choices give nearly identical migration trends.

## 5. Independent S2-window check

The audit counts the S1 and S2 selections directly in the 1,300,000 raw paired events in the black support. All 1,300,000 events pass:

- Parametric S1 coincidence;
- Full S1 coincidence;
- NEST GetS2 threshold;
- the strict raw-S2 lower bound \(S2_{\mathrm{raw}}>645\ \mathrm{phd}\);
- the corrected-S2 window \(2.75\leq\log_{10}S2_c\leq4.15\).

The observed raw-S2 minimum is 4,855.60 phd. The observed corrected-S2 range is 7,418.07--13,690.33 phd, wholly inside the allowed 562.34--14,125.38 phd interval. No event inside the Parametric or Full S1 ROI fails the S2 part of the WS ROI.

Consequently, for this high-energy black support, the WS-ROI efficiency equals the S1 [3,600]-phd efficiency. The observed mode-dependent rate change is an S1 upper-boundary migration effect; it is not caused by S2-threshold or S2-window losses. This statement is specific to this benchmark and support and must not be generalized to lower-energy benchmarks.

## 6. Interpretation

The dedicated audit resolves the mechanism behind the approximately \(-0.59\%\) black-benchmark integrated WS-ROI rate shift already seen in the ten-seed ensemble:

1. S1 coincidence is fully efficient in the black signal support.
2. The S2 threshold and both S2 ROI boundaries are fully efficient in this support.
3. Full S1 is shifted upward by roughly 1--2 phd in its upper quantiles.
4. More paired events cross from \(S1_c\leq600\) in Parametric to \(S1_c>600\) in Full than cross in the reverse direction.
5. The net loss is about 0.44 percentage points of raw signal weight, or about 0.59% relative to the Parametric accepted rate.
6. The effect increases with recoil energy and reaches about 1.03% in the 255--269.9 keV band.

This is a small but resolved S1-response-mode dependence in the present NEST proxy. It should be carried as a detector-response modeling uncertainty or addressed by a validated waveform-level response; it must not be silently removed by selecting a coarser histogram.

## 7. Scope limitations

This is an EFT2024 NEST response diagnostic, not the official LZ selected-event PDF. It does not include official waveform-level S1 reconstruction, DAQ trigger, SS reconstruction, data-analysis cuts, the official 4.71-tonne fiducial-volume mask, Skin/OD veto partitions, live-time migration, or their joint covariance. It does not provide detector-systematic uncertainty and is not a profile-likelihood input. It does not authorize a final exclusion curve or 90% CL result.

The ten-seed Student-\(t\) intervals quantify production-level Monte Carlo variation only. They do not include NEST model uncertainty, detector calibration uncertainty, or official LZ selection covariance. GCN and JJ55 are alternative nuclear-recoil spectra folded through the same EFT2024 detector-response production; they are not alternative NEST detector configurations.

## 8. Machine-readable outputs

- **black_s1_upper_tail_summary.csv:** 12 rows (2 nuclear models × 6 energy bands). Nested values are encoded as JSON strings.
- **black_s1_upper_tail_per_seed.csv:** 120 rows (10 seeds × 2 nuclear models × 6 bands).
- **black_s1_upper_tail_thresholds.csv:** 1,200 rows (10 seeds × 2 models × 6 bands × 10 S1 thresholds).
- **black_s1_upper_tail_metadata.json:** canonical structured summary, provenance, weight-closure residual, selection counts, and limitations.
- **SHA256SUMS:** checksums for the four output files.

The source production artifact is immutable. The audit artifact and archived files are separate from the raw production inputs.
