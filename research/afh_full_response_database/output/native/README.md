# Native AFH v6.0 seven-isotope eight-response archive

This directory contains the native Wolfram export used to validate the Python
AFH-8 reference database. It is produced by
`research/afh_full_response_database/run_afh_full_response_database.wls` with the
AFH package at `v6/dmformfactor-V6.m`.

## Contents

- `afh_v6_xe{128,129,130,131,132,134,136}_eight_response_native.csv`:
  2401 uniform momentum nodes per isotope (`q = 0` to `0.6 GeV`, step
  `0.00025 GeV`) and eight `ResponseNuclear[y, index, 0, 0]` channels.
- `native_metadata.txt`: source path and SHA-256, Wolfram version, grid, and
  normalization convention.
- `python_validation.json`: internal consistency check of the Python reference
  database (grid, positivity, Cauchy-Schwarz, zero-momentum normalization).
- `native_comparison.json`: pointwise Python-versus-native comparison over all
  16807 rows. Status: `PASS` (`native_afh_validated: true`).
- `sha256_manifest.json`: SHA-256 fingerprints for the committed native data and
  metadata.

## Normalization and scope

The exported `W_*` columns are raw AFH isoscalar package values (`tau1=tau2=0`).
No physical equal-proton/neutron factor-four rescaling is applied. Imaginary
parts are exported separately. The archive covers the seven Xe isotopes with
AFH default density matrices (`128, 129, 130, 131, 132, 134, 136`) and does not
include a three-body tensor contraction or detector-level rate.

## Reproduce

```bash
export AFH_SOURCE_COMMIT="$(git rev-parse HEAD)"
wolframscript -file research/afh_full_response_database/run_afh_full_response_database.wls
python research/afh_full_response_database/run_afh_full_response_database.py \
  --outdir tmp_python_db
python research/afh_full_response_database/compare_native_afh_full_response.py \
  --python-csv tmp_python_db/afh_v6_full_eight_response_7isotope.csv \
  --native-dir research/afh_full_response_database/output/native \
  --out-json research/afh_full_response_database/output/native/native_comparison.json
python research/afh_full_response_database/verify_native_full_response_provenance.py
```

The largest pointwise discrepancies are at low `q`, where the absolute
tolerance dominates: `M` has `2.046e-12` absolute and `6.278e-6` relative
difference; the other seven channels are below `8.5e-14` absolute and
`6.0e-7` relative difference.

## Provenance boundary

`native_comparison.json` validates the seven-isotope eight-response database
against native Wolfram `ResponseNuclear`. It does not by itself validate the
rank-resolved spatial multipole amplitudes in
`../native-spatial-multipoles/`, which have their own archive and gate.
