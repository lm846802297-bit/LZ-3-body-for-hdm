# Paired S1 independent-seed 2D response archive

- Production run: https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43750948249
- Production artifact: 14176882910
- Production artifact ZIP SHA-256: 606397d9eac594008630a18b97f1e72fbbfa1d157e34779de7ce5fd0fe5b8cb5
- Binning audit run: https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43754946092
- Binning audit artifact: 14177248273
- Binning audit artifact ZIP SHA-256: ceca6a9d05cd0342da2d6e994a206111d6a2eadf4863526a7bb540bdbabd7b01
- Source commit for the NEST production: a87d95276aafc5043f943aacc42a5d5a941ce27b
- Pinned NEST commit: 541b6430dae6ea289cf110c99f174a9187f7fdee
- Seeds: 20261117, 40261117, 60261117, 80261117, 100261117, 120261117, 140261117, 160261117, 180261117, 200261117.
- Events: 470,000 per seed; 4,700,000 total across 235 one-keV strata.

The archive commits all ten per-seed fold maps, rate summaries, split-half summaries,
the ten-seed ensemble maps and metadata, and the 48-row/480-row binning-stability
summaries. The ten raw event CSVs remain in the immutable production artifact.
raw_event_artifact_SHA256SUMS.txt preserves the complete 75-file SHA-256 manifest,
including the raw event samples.

The ensemble summaries are regenerated from the archived ten per-seed fold products
using the current aggregation implementation. This corrects a stale three-seed
limitation string in the original production artifact metadata; it does not rerun
NEST, alter event samples, or change the numerical ensemble inputs. The production
ZIP digest above continues to identify the original immutable Actions artifact.


## Four-benchmark paired S1 upper-tail audit

- Audit run: https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43764753139
- Audit artifact: 14181863680
- Audit artifact ZIP SHA-256: 4490b4e8a0631569617a5e6fb1e7037a1e5a70290fd5dd3f3e3c12d4518faa04
- New archive: multi-benchmark-upper-tail-audit/REPORT.md and its four machine-readable output files.
- Same immutable ten-seed production; 4,700,000 unique events reweighted for four benchmarks.
- 18,800 exact per-stratum closure checks; maximum relative residual 7.2003e-15.
- Supports: red 35--269.9 keV; green 100--269.9 keV; black 205--269.9 keV; blue 100--269.9 keV.

The four-benchmark report shows that the response-mode migration grows toward
high recoil energy. Black has the largest integrated shift because about
59--60% of its common-support rate lies in 255--269.9 keV, compared with
about 1--2% for the other three benchmarks. The full audit and its scope
limitations are documented in the linked report.
