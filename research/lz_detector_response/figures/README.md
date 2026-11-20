# Formal B xenon recoil spectra

Two vector figures generated from the archived formal-B halo reweight and event-fold CSV outputs.

## Figures

- [Natural-xenon relative differential rate: A vs B](natural_xenon_relative_differential_rate_A_vs_B.svg)
- [Formal-B expected recoil events: AFH-7 benchmarks](formal_B_expected_events_vs_recoil_AFH7.svg)

## Provenance and interpretation

The A/B recoil-rate figure uses the natural-xenon CSVs from the three separate strange-current scenarios:
- Sufian 2017 unit current;
- Alexandrou 2020 charge-weighted input converted to unit current;
- Alexandrou 2026 continuum unit-current input.

The vertical axis is the source calculation's relative differential rate (arbitrary normalization), not an absolutely normalized differential cross section. It is proportional to the corresponding differential rate/cross-section shape. Absolute cross sections require the common model normalization and couplings to be restored.

The event-spectrum figure uses the rate-level AFH-7 spectra for the Sufian 2017 input and the four existing benchmarks. Counts are obtained by integrating each 1-keV recoil bin and multiplying by 2.84 tonne-year (2,840 kg × 365.25 days). These are rate-level expected counts before NEST/WS-ROI selection; they are not detector-selected counts.

## Frozen input archives

- Formal-B seven-isotope halo reweight: PR #93 workflow artifact, run 44681433980 (after merge).
- Formal-B NEST event fold: PR #92 workflow run 44681301082.
- The source AFH isotope set covers 99.8158% of natural xenon atom abundance; Xe-124 and Xe-126 are absent from the current AFH set and the included abundances are not renormalized.

## Reproduction

The figures are vector SVG files. The numerical source tables and run manifests are retained in the corresponding workflow artifacts and research reports. Do not infer absolute cross-section units from the relative-rate plot.
