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
- The native Wolfram 652-row full-grid run and independent Python comparator are archived in `full_dsigma_mathematica/`; the machine-readable comparator metadata reports **PASS**; the broader scientific status is **PASS_WITH_NOTES** because the result is fixed-speed Xe-131 under conditional width assumptions. The 652 rows cover four benchmarks (500 open, 152 closed) at 800 km/s. Maximum relative differences are I6 1.34e-12, dσ 1.34e-12, AFH response 3.36e-16, and cross-code converted dσ 1.34e-12. The latter is compared with the same 2e-7 observable tolerance as dσ; the per-code unit-conversion identity residuals are separately 3.35e-16 (Mathematica) and 0 (Python), each below 2e-12. `SHA256SUMS.txt` contains 14 repository-relative checksums for run inputs, source files and full-grid outputs; `green_high_order_SHA256SUMS.txt` separately contains four checksums for the Green high-order artifacts; `full_dsigma_sha256_manifest.json` records the full-grid provenance and hashes. This remains a fixed-speed Xe-131 calculation under the conditional Dirac / real-scalar / pure-scalar / single-channel pole-width assumptions, not a halo fold or detector likelihood.
- The 2401-node native response-level PASS and the historical I6 mapping audit are separate validation layers; neither substitutes for the full Eq. (6) cross-code comparison.
- The committed `SHA256SUMS.txt` verifies 14 repository-relative source/input/full-grid entries; `green_high_order_SHA256SUMS.txt` separately verifies the four Green high-order files. The committed `full_dsigma_sha256_manifest.json` records the full-run provenance and its 14 file hashes. A new run also creates a run-local manifest and checksum list in the selected output directory.

## Historical or diagnostic outputs

- `figure2_four_benchmarks_dsigma_AFH_GCN_JJ55.csv` is superseded because its AFH response column was copied from GCN. Do not use it for new plots or calculations.
- `ame2020_exact_spatial_xe131_partial/` contains Xe-131-only partial-rate and hybrid diagnostics. The historical PCHIP-based rates remain provisional for precision use; they are not a full seven-isotope AME2020 prediction.
- Other `metadata.json`, `minima.csv`, `figure2_dip_check.csv`, and response-comparison files provide provenance or focused diagnostics; consult the study README and each manifest before selecting a result.

The direct Mathematica exports and the independent pointwise comparison are intentionally stored in separate subdirectories: `native_exports/` contains the package's raw run products, while `native_audit/` contains the verification outputs and PASS manifest. Do not treat the former as a substitute for the latter.

- `historical_i6_mapping_audit/`: matched 776 km/s, zero-width green Xe-131 I6 comparison across legacy, linear-W2, linear-W, threshold-u2, and sine-squared mappings. The archive contains the comparison CSV, metadata, README, and SHA-256 manifest; see [HISTORICAL_I6_MAPPING_AUDIT.md](HISTORICAL_I6_MAPPING_AUDIT.md) for the numerical interpretation. This is an I6-only phase-space audit, not a full differential-cross-section validation.
