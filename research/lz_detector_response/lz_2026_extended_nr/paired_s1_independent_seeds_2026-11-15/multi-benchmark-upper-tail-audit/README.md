# Four-benchmark paired S1 upper-tail audit

**Status:** completed ten-independent-seed diagnostic; not an official LZ detector response or likelihood input.

This audit extends the black 360-keV S1 upper-tail study to all four three-body benchmarks. It reuses the same immutable 4.7-million-event paired EFT2024 NEST Parametric/Full production; no NEST events were regenerated.

## Main result

On the common \(E_R=205\)--\(269.9\) keV support, the Full/Parametric S1 ROI rate changes are:

| Benchmark | GCN | JJ55 |
|---|---:|---:|
| red (200 keV, 1 MeV) | -0.0676% | -0.0684% |
| green (300 keV, 1 MeV) | -0.0795% | -0.0805% |
| black (360 keV, 1 MeV) | -0.5983% | -0.5881% |
| blue (300 keV, 10 MeV) | -0.0794% | -0.0804% |

The S1 response difference grows with recoil energy: the 255--269.9 keV band shows about a -0.95% to -1.03% relative accepted-rate change for all four benchmarks. Black has a much larger integrated shift because approximately 59--60% of its rate on the common support lies in this highest-energy band; the other benchmarks put only about 1--2% there.

All raw events in each benchmark's full non-zero recoil support pass both S1 coincidence flags, the NEST S2 threshold, raw-S2 \(>645\) phd, and the corrected-S2 window. Thus, for these supports, WS-ROI acceptance equals the S1 \([3,600]\)-phd acceptance.

## Numerical closure and provenance

- 10 seeds; 470,000 events per seed; 4,700,000 unique raw paired events.
- Four benchmark spectra × GCN/JJ55 reweightings; 18,800 exact per-stratum closure checks.
- Maximum relative weight-closure residual: \(7.2003\times10^{-15}\), against \(5\times10^{-12}\).
- Source production: [run 43750948249](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43750948249), artifact 14176882910.
- Audit: [run 43764753139](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43764753139), artifact 14181863680.
- Audit artifact ZIP SHA-256: 4490b4e8a0631569617a5e6fb1e7037a1e5a70290fd5dd3f3e3c12d4518faa04.
- Source production ZIP SHA-256: 606397d9eac594008630a18b97f1e72fbfa1d157e34779de7ce5fd0fe5b8cb5.

## Files

- **REPORT.md:** full methodology, benchmark-by-benchmark results, S2 closure, energy dependence, interpretation, and limitations.
- **multi_benchmark_s1_upper_tail_summary.csv:** 48 summary rows.
- **multi_benchmark_s1_upper_tail_per_seed.csv:** 480 seed-level rows.
- **multi_benchmark_s1_upper_tail_thresholds.csv:** 4,800 threshold rows.
- **multi_benchmark_s1_upper_tail_metadata.json:** canonical provenance and audit metadata.
- **SHA256SUMS:** file checksums.

This is an EFT2024 NEST proxy diagnostic, not the official LZ waveform-level selected PDF. DAQ, SS/DA, official FV, Skin/OD, live-time, and their joint covariance remain outside scope. No final likelihood or exclusion result is authorized.
