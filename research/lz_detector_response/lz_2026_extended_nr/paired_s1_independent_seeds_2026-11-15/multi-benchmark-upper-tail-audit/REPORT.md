# Four-benchmark paired S1 upper-tail and ROI-migration audit

**Status:** completed ten-independent-seed diagnostic; not an official LZ detector response or likelihood input.

**Benchmarks:** red (\(m_s=200\ \mathrm{keV},\Delta m=1\ \mathrm{MeV}\)); green (\(300\ \mathrm{keV},1\ \mathrm{MeV}\)); black (\(360\ \mathrm{keV},1\ \mathrm{MeV}\)); blue (\(300\ \mathrm{keV},10\ \mathrm{MeV}\))  
**Response:** EFT2024; pinned NEST commit 541b6430dae6ea289cf110c99f174a9187f7fdee  
**Source production:** [run 43750948249](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43750948249), artifact 14176882910  
**Audit run:** [run 43764753139](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43764753139)  
**Audit artifact:** [artifact 14181863680](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43764753139/artifacts/14181863680)  
**Audit artifact ZIP SHA-256:** 4490b4e8a0631569617a5e6fb1e7037a1e5a70290fd5dd3f3e3c12d4518faa04  
**Source production ZIP SHA-256:** 606397d9eac594008630a18b97f1e72fbfa1d157e34779de7ce5fd0fe5b8cb5

## 1. Scope and event sample

This follow-up extends the dedicated black 360-keV S1 upper-tail audit to all four three-body signal benchmarks. It reuses the immutable ten-seed paired Parametric/Full EFT2024 NEST production. No NEST events were regenerated, and no detector configuration or response random stream was changed.

- 10 independent production seeds.
- 470,000 paired events per seed; 4,700,000 unique raw events in total.
- 235 one-keV true-recoil strata spanning 35--269.9 keV.
- 2,000 events per stratum, split into two disjoint 1,000-event replicas.
- Four benchmark spectra are folded over the same raw event sample.
- GCN and JJ55 are evaluated separately for every benchmark.
- The calculation therefore contains 18.8 million event--benchmark pairs and 37.6 million event--benchmark--nuclear-model weight instances.

The paired response construction is unchanged: each event shares its intrinsic NR quanta, true recoil energy, true position, and S2 draw between Parametric and Full S1; the S1 modes use separate deterministic NEST random streams.

## 2. Exact event reweighting and numerical closure

For seed \(s\), benchmark \(b\), nuclear model \(M\), and one-keV stratum \(k\), each event receives

\[
w_i^{(s,b,M)} =
R_{k,\mathrm{exact}}^{(s,b,M)}
\frac{f_{b,M}(E_i)}
{\sum_{j\in k} f_{b,M}(E_j)} ,
\]

where \(R_{k,\mathrm{exact}}\) is read from the original per-seed response-by-energy-bin fold product and \(f_{b,M}(E)\) is evaluated using the same piecewise-linear interpolation routine as the original three-body fold.

The audit checks the identity

\[
\sum_{i\in k}w_i^{(s,b,M)}
=R_{k,\mathrm{exact}}^{(s,b,M)}
\]

for every seed, benchmark, nuclear model, and recoil-energy stratum.

The maximum relative residual is

\[
\delta_{\max}=7.2003\times10^{-15},
\]

well below the required \(5\times10^{-12}\) tolerance. The workflow passes all six unit tests, production-artifact manifest verification, support checks, event-count checks, output-row checks, and SHA-256 generation/verification.

## 3. Benchmark recoil supports and common comparison interval

The non-zero exact integrated-rate support derived from the original per-seed fold products is:

| Benchmark | \(m_s\) | \(\Delta m\) | Non-zero 1-keV support | Number of strata |
|---|---:|---:|---:|---:|
| red | 200 keV | 1 MeV | 35--269.9 keV | 235 |
| green | 300 keV | 1 MeV | 100--269.9 keV | 170 |
| black | 360 keV | 1 MeV | 205--269.9 keV | 65 |
| blue | 300 keV | 10 MeV | 100--269.9 keV | 170 |

All four benchmarks are also evaluated on the common interval

\[
E_R\in[205,269.9]\ \mathrm{keV},
\]

which isolates how their different recoil-spectrum weights sample the same detector-response energy region. For black, the full physical support and the common interval coincide.

The common interval contains the following fraction of each benchmark's total recoil rate:

| Benchmark | GCN | JJ55 |
|---|---:|---:|
| red | 7.96% | 8.11% |
| green | 26.46% | 26.71% |
| black | 100.00% | 100.00% |
| blue | 26.35% | 26.60% |

Within the common interval, the fraction of the signal rate in the highest 255--269.9 keV band is particularly diagnostic:

| Benchmark | GCN | JJ55 |
|---|---:|---:|
| red | 1.18% | 1.21% |
| green | 1.64% | 1.67% |
| black | 59.98% | 58.74% |
| blue | 1.64% | 1.66% |

The black benchmark is therefore much more heavily weighted toward the highest recoil-energy band. This becomes central to interpreting its larger integrated Parametric/Full rate shift.

## 4. Event-level S1 and S2 selection closure

The raw-event selection audit is performed over each benchmark's full non-zero recoil support. The counts below are unweighted generated-event counts; the physical efficiencies are calculated separately using the exact event weights.

| Benchmark | Events in support | Parametric S1 coincidence | Full S1 coincidence | NEST S2 threshold | Raw S2 \(>645\) phd | S2c window | Combined S2 ROI |
|---|---:|---:|---:|---:|---:|---:|---:|
| red | 4,700,000 | 100% | 100% | 100% | 100% | 100% | 100% |
| green | 3,400,000 | 100% | 100% | 100% | 100% | 100% | 100% |
| black | 1,300,000 | 100% | 100% | 100% | 100% | 100% | 100% |
| blue | 3,400,000 | 100% | 100% | 100% | 100% | 100% | 100% |

The minimum raw-S2 and corrected-S2 values over each full support are:

| Benchmark | Minimum \(S2_{\rm raw}\) [phd] | Minimum \(S2_c\) [phd] | Maximum \(S2_c\) [phd] |
|---|---:|---:|---:|
| red | 1,940.29 | 2,611.71 | 13,690.33 |
| green | 3,723.33 | 5,556.91 | 13,690.33 |
| black | 4,855.60 | 7,418.07 | 13,690.33 |
| blue | 3,723.33 | 5,556.91 | 13,690.33 |

All events are above the strict raw-S2 lower bound of 645 phd and inside the corrected-S2 window \(2.75\leq\log_{10}S2_c\leq4.15\). No event inside either S1 ROI fails the S2 part of the WS ROI.

Consequently, for these four benchmark supports, the WS-ROI acceptance is numerically identical to the S1 \([3,600]\)-phd acceptance. The observed Parametric/Full rate differences are caused by S1 selection migration, not by the S2 threshold or S2 ROI. This statement is specific to these spectra and the audited support; it is not a general statement about lower-energy NR events.

## 5. Integrated S1 ROI rates: full support versus common support

The table gives event-weighted S1 ROI efficiencies. The WS-ROI efficiencies are identical because the S2 selection is fully efficient in all four supports. The relative change is the mean of the ten seed-level Full/Parametric rate ratios; the interval is a 95% Student-\(t\) interval over the ten independent production seeds.

| Benchmark | Support | GCN Parametric \(\to\) Full | GCN relative change (95% CI) | JJ55 Parametric \(\to\) Full | JJ55 relative change (95% CI) |
|---|---|---:|---:|---:|---:|
| red | full | 99.8183% \(\to\) 99.8130% | -0.00535% [-0.00692, -0.00377] | 99.8124% \(\to\) 99.8069% | -0.00551% [-0.00712, -0.00390] |
| red | common 205--269.9 | 97.7261% \(\to\) 97.6600% | -0.06759% [-0.08570, -0.04947] | 97.6970% \(\to\) 97.6302% | -0.06837% [-0.08661, -0.05014] |
| green | full | 99.2762% \(\to\) 99.2556% | -0.02078% [-0.02649, -0.01507] | 99.2599% \(\to\) 99.2388% | -0.02123% [-0.02703, -0.01543] |
| green | common 205--269.9 | 97.2719% \(\to\) 97.1945% | -0.07949% [-0.10033, -0.05865] | 97.2366% \(\to\) 97.1584% | -0.08047% [-0.10150, -0.05944] |
| black | full = common | 73.9501% \(\to\) 73.5072% | -0.59833% [-0.80463, -0.39203] | 74.3246% \(\to\) 73.8871% | -0.58808% [-0.79014, -0.38601] |
| blue | full | 99.2803% \(\to\) 99.2598% | -0.02067% [-0.02635, -0.01499] | 99.2641% \(\to\) 99.2431% | -0.02112% [-0.02689, -0.01535] |
| blue | common 205--269.9 | 97.2762% \(\to\) 97.1989% | -0.07939% [-0.10020, -0.05857] | 97.2410% \(\to\) 97.1628% | -0.08036% [-0.10137, -0.05936] |

Two distinct effects are visible:

1. The full-support shifts for red, green, and blue are small because most of their rate lies below 205 keV, where the S1 upper-boundary migration is much smaller.
2. On the common 205--269.9 keV interval, red, green, and blue give similar integrated shifts of about -0.07% to -0.08%, whereas black remains near -0.59%.

The common-support difference is not a detector-configuration difference: all four use the same paired NEST events and response. It is caused by the different \(dR/dE_R\) weights within the common interval. In particular, roughly 59% of the black rate in this interval lies in 255--269.9 keV, compared with only about 1--2% for red, green, and blue.

## 6. S1 upper-tail migration at the 600-phd boundary

Since both S1 coincidence flags pass for every event in each benchmark support, the paired Full-minus-Parametric change in the fraction above 600 phd directly corresponds to the loss in the accepted \(S1_c\leq600\) fraction.

The common-support tail-fraction differences are:

| Benchmark | GCN Full-minus-Parametric \(S1_c>600\) | JJ55 Full-minus-Parametric \(S1_c>600\) |
|---|---:|---:|
| red | +0.0661 pp | +0.0668 pp |
| green | +0.0773 pp | +0.0783 pp |
| black | +0.4429 pp | +0.4375 pp |
| blue | +0.0772 pp | +0.0781 pp |

The ten-seed intervals for these differences exclude zero in all four common-support benchmarks. In full-support weighting, the corresponding changes are much smaller for red (+0.0053 pp), green (+0.0206 pp), and blue (+0.0205 pp), while black is unchanged because its full support is already the common interval.

The weighted S1 quantiles also move upward in Full mode. Across the four full-support benchmarks, the mean \(q_{95}\) shift is about 0.6--1.6 phd and the \(q_{99}\) shift is about 0.7--1.5 phd. This small upward displacement is sufficient to produce a resolved loss at the 600-phd upper boundary when the recoil spectrum has substantial weight near and above that boundary.

## 7. Energy-resolved migration

The following table shows the GCN relative S1 ROI rate change by true recoil band. The JJ55 values agree to better than 0.001 percentage point in every listed benchmark/band combination.

| True recoil band [keV] | red | green | black | blue |
|---|---:|---:|---:|---:|
| 205--225 | -0.0182% | -0.0200% | -0.0603% | -0.0200% |
| 225--240 | -0.1347% | -0.1370% | -0.1614% | -0.1370% |
| 240--255 | -0.3255% | -0.3275% | -0.2977% | -0.3275% |
| 255--269.9 | -0.9545% | -0.9614% | -1.0337% | -0.9613% |

The first band is consistent with zero at the ten-seed Monte Carlo precision. The 225--240 and 240--255 keV bands show resolved negative shifts, and the 255--269.9 keV band reaches approximately -0.95% to -1.03% for every benchmark. This establishes that the migration is energy dependent and not peculiar to the black benchmark.

## 8. Distribution-shape diagnostics on common support

All values are ensemble-mean total-variation distances in percent. Each cell lists GCN / JJ55.

| Benchmark | S1 conditional histogram TV | S1 upper-tail TV (\(S1_c>500\)) | NEST-stage 2D TV | WS-ROI 2D TV |
|---|---:|---:|---:|---:|
| red | 0.5597 / 0.5582 | 0.4608 / 0.4593 | 1.0329 / 1.0302 | 0.9998 / 0.9970 |
| green | 0.5442 / 0.5437 | 0.4410 / 0.4394 | 0.9860 / 0.9830 | 0.9504 / 0.9471 |
| black | 0.5957 / 0.5896 | 0.5832 / 0.5763 | 1.1679 / 1.1538 | 0.9425 / 0.9318 |
| blue | 0.5443 / 0.5438 | 0.4412 / 0.4396 | 0.9864 / 0.9834 | 0.9509 / 0.9476 |

The ensemble-mean WS-ROI 2D TV is at or below approximately 1% for these points, but this does not establish Parametric/Full equivalence. The NEST-stage 2D TV remains above 1% for red and black, and ensemble-mean TVs do not replace the per-seed spread or a predeclared equivalence test. The native 10-phd by 0.02-dex map remains the reference; coarsening must not be used merely to reduce TV.

## 9. Interpretation

The four-benchmark audit resolves the apparent difference between the black benchmark and the other three:

- The underlying Parametric/Full detector-response difference is present across all four benchmarks and grows toward higher \(E_R\).
- Red, green, and blue put only about 1--2% of their common-support rate in the highest 255--269.9 keV band. Most of their common-support rate lies in 205--225 keV, where the migration is small.
- Black places about 59--60% of its common-support rate in 255--269.9 keV. Its integrated rate shift is therefore much larger, near -0.59%.
- Red's full physical support begins at 35 keV, and green/blue begin at 100 keV. Their lower-energy contributions further dilute the full-support shifts to about -0.005%, -0.021%, and -0.021%, respectively.
- Green and blue have the same \(m_s=300\) keV but different \(\Delta m\). Their common-support migration results are nearly identical, indicating that the detector-mode response effect is controlled mainly by the recoil-energy weighting in this comparison.

The correct conclusion is not that only black has a Parametric/Full response difference. The difference is common, energy dependent, and convolved with a benchmark-dependent recoil spectrum.

## 10. Scope limitations

This is an EFT2024 NEST response diagnostic, not the official LZ waveform-level selected-event PDF. It does not include official waveform S1 reconstruction, DAQ trigger, SS reconstruction/data-analysis cuts, the official 4.71-tonne fiducial-volume mask, Skin/OD veto partitions, live-time migration, or their joint covariance. The source production uses a uniform active-TPC cylinder proxy rather than the official FV.

The ten-seed Student-\(t\) intervals quantify production-level Monte Carlo variation only. They do not include NEST model uncertainty, detector calibration uncertainty, or official LZ selection covariance. GCN and JJ55 are alternative recoil-spectrum foldings through the same EFT2024 response, not alternative detector configurations. No formal Parametric/Full equivalence claim, final profile likelihood, or 90% CL exclusion is provided.

## 11. Machine-readable outputs

- **multi_benchmark_s1_upper_tail_summary.csv:** 48 rows (4 benchmarks × 6 energy bands × 2 nuclear models).
- **multi_benchmark_s1_upper_tail_per_seed.csv:** 480 rows (48 summary combinations × 10 seeds).
- **multi_benchmark_s1_upper_tail_thresholds.csv:** 4,800 rows (per-seed rows × 10 S1 thresholds).
- **multi_benchmark_s1_upper_tail_metadata.json:** benchmark supports, selection audit, weight-closure residuals, provenance, and limitations.
- **SHA256SUMS:** checksums for the four machine-readable outputs plus this report and README.

The raw production artifact remains immutable. The multi-benchmark audit artifact is separate from the raw production inputs.
