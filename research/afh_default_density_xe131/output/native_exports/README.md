# Native AFH Mathematica exports

This directory contains the direct products of `run_afh_default_xe131.wls`:

- `afh_default_xe131_WM00_mathematica.csv`: 2401-node AFH v6.0 native response export.
- `afh_default_xe131_mathematica_metadata.txt`: Wolfram execution settings, source identity, oscillator length, q-grid and normalization record.

These are the raw direct-run products. The separate `../native_audit/` directory contains the independent Python/Wolfram pointwise comparison, comparison summary, minima, and SHA-256 manifest. A PASS in `native_audit/` is the verification record; the direct export alone is not a comparison.

Reproduce from the study root with:

~~~powershell
.\run_native_afh_audit.ps1 -AfhSource "D:\path\to\v6.zip"
~~~

The runner writes the native exports here and the independent verification products to `../native_audit/`.
