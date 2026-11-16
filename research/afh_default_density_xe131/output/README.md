# Xe-131 AFH result archive

This directory stores generated response tables, corrected cross sections, validation summaries, and versioned diagnostics.

## Canonical and validated outputs

- `afh_default_xe131_WM00.csv`: 2401-node source-translated Python AFH v6.0 Xe-131 response grid.
- `figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv`: canonical corrected long-form four-benchmark fixed-speed cross-section table. It reuses the archived 5-keV-grid I6 values and replaces the nuclear response; it is not a fresh independent 640-integral recomputation or the native Mathematica full-cross-section comparison.
- `figure2_four_benchmarks_AFH_GCN_JJ55_wide_audit.csv`: matching wide-form audit table.
- `native_exports/`: direct 2401-node native Wolfram response CSV and execution metadata emitted by `run_afh_default_xe131.wls`.
- `native_audit/`: independent native Wolfram/Python pointwise comparison archive. Its manifest reports PASS for the 2401-point Xe-131 response comparison.

## Full Eq. (6) differential-cross-section status (2026-11-16)

- The Python-only full Xe-131 fixed-speed (v=800 km/s) grid runner, under the conditional Dirac / real-scalar / pure-scalar / single-channel pole-width assumptions, has been executed and its CSV, metadata, and high-order anchors are archived as GitHub Actions artifact 14112736343. The run was produced on branch `research/python-xe131-full-dsigma-20261114` at commit `c2d0590114ad0bf90fc741278e21868af52b65cf`; the current Python runner, Eq. (6) kernel, phase-space integrator and AFH response CSV have identical Git blob SHAs to that run. It covers 652 rows (500 open, 152 closed) and 16 high-order anchors; maximum I6 relative difference is 1.66367e-11, AFH factor-four mapping residual is 3.55679e-16, and physical/no-factor-four ratio residual is zero. This confirms the factor-four transfer within the Python implementation.
- The native Wolfram 652-row full-grid run and independent pointwise Python comparator remain **pending**. The code-level review is complete, but no native full-grid CSV, comparison JSON, or SHA-256 manifest is yet archived. The Windows wrapper now generates `full_dsigma_sha256_manifest.json` and `SHA256SUMS.txt` automatically after a successful cross-code PASS. Do not report a Mathematica/Python full-dsigma cross-code PASS; the Python-only PASS above does not replace it.
- The 2401-node native response-level PASS and the historical I6 mapping audit are separate validation layers; neither substitutes for the full Eq. (6) cross-code comparison.

## Historical or diagnostic outputs

- `figure2_four_benchmarks_dsigma_AFH_GCN_JJ55.csv` is superseded because its AFH response column was copied from GCN. Do not use it for new plots or calculations.
- `ame2020_exact_spatial_xe131_partial/` contains Xe-131-only partial-rate and hybrid diagnostics. The historical PCHIP-based rates remain provisional for precision use; they are not a full seven-isotope AME2020 prediction.
- Other `metadata.json`, `minima.csv`, `figure2_dip_check.csv`, and response-comparison files provide provenance or focused diagnostics; consult the study README and each manifest before selecting a result.

The direct Mathematica exports and the independent pointwise comparison are intentionally stored in separate subdirectories: `native_exports/` contains the package's raw run products, while `native_audit/` contains the verification outputs and PASS manifest. Do not treat the former as a substitute for the latter.

- `historical_i6_mapping_audit/`: matched 776 km/s, zero-width green Xe-131 I6 comparison across legacy, linear-W2, linear-W, threshold-u2, and sine-squared mappings. The archive contains the comparison CSV, metadata, README, and SHA-256 manifest; see [HISTORICAL_I6_MAPPING_AUDIT.md](HISTORICAL_I6_MAPPING_AUDIT.md) for the numerical interpretation. This is an I6-only phase-space audit, not a full differential-cross-section validation.
