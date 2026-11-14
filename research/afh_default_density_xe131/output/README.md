# Xe-131 AFH result archive

This directory stores generated response tables, corrected cross sections, validation summaries, and versioned diagnostics.

## Canonical and validated outputs

- `afh_default_xe131_WM00.csv`: 2401-node source-translated Python AFH v6.0 Xe-131 response grid.
- `figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv`: canonical corrected long-form four-benchmark cross-section table.
- `figure2_four_benchmarks_AFH_GCN_JJ55_wide_audit.csv`: matching wide-form audit table.
- `native_exports/`: direct 2401-node native Wolfram response CSV and execution metadata emitted by `run_afh_default_xe131.wls`.
- `native_audit/`: independent native Wolfram/Python pointwise comparison archive. Its manifest reports PASS for the 2401-point Xe-131 response comparison.

## Historical or diagnostic outputs

- `figure2_four_benchmarks_dsigma_AFH_GCN_JJ55.csv` is superseded because its AFH response column was copied from GCN. Do not use it for new plots or calculations.
- `ame2020_exact_spatial_xe131_partial/` contains Xe-131-only partial-rate and hybrid diagnostics. The historical PCHIP-based rates remain provisional for precision use; they are not a full seven-isotope AME2020 prediction.
- Other `metadata.json`, `minima.csv`, `figure2_dip_check.csv`, and response-comparison files provide provenance or focused diagnostics; consult the study README and each manifest before selecting a result.

The direct Mathematica exports and the independent pointwise comparison are intentionally stored in separate subdirectories: `native_exports/` contains the package's raw run products, while `native_audit/` contains the verification outputs and PASS manifest. Do not treat the former as a substitute for the latter.
