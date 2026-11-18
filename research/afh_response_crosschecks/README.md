# AFH response cross-check utilities

This directory contains small, artifact-level comparison tools that do not
rerun the nuclear-structure calculation.

## P3-B spatial response versus independent AFH-8 Python database

The comparator is **compare_p3_spatial_vs_afh8.py**. It compares:

- the P3-B artifact from workflow run
  [44296729828](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44296729828),
  artifact 14423594659;
- the independent AFH-8 Python artifact from workflow run
  [44222087512](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44222087512),
  artifact 14391456283.

Download and extract both artifacts, then run:

~~~bash
python research/afh_response_crosschecks/compare_p3_spatial_vs_afh8.py \
  --p3-csv /path/to/afh_spatial_obdme_responses_7isotope_2401.csv \
  --afh8-csv /path/to/afh_v6_full_eight_response_7isotope.csv \
  --out-json /path/to/p3_b_independent_python_crosscheck.json
~~~

The tool checks all 16,807 isotope/q rows, exact q/y grid alignment, the
signed spatial interference, the common OBDME normalization, the factor-four
physical conversion, spin-zero isotopes, and the Cauchy--Schwarz bound. It
uses Python's standard-library CSV parser to avoid parser-induced rounding
differences in small response values.

A PASS is explicitly PASS_INDEPENDENT_PYTHON_CROSSCHECK and keeps
native_afh_validated=false. It is not a substitute for the private native
Wolfram ResponseNuclear comparison.


## Direct P3-B versus native Wolfram AFH comparison

After the native workflow artifact is available, use
**compare_p3_spatial_vs_native.py** to compare P3-B directly with the native
Wolfram exports for AFH response indices 3, 6 and 8. The script verifies the
AFH source SHA-256, all 16,807 rows, the three signed/diagonal response
channels, physical equal-p/n conversion, and native imaginary residuals.

~~~bash
python research/afh_response_crosschecks/compare_p3_spatial_vs_native.py \
  --p3-csv /path/to/afh_spatial_obdme_responses_7isotope_2401.csv \
  --p3-metadata /path/to/p3_metadata.json \
  --native-dir /path/to/native \
  --native-metadata /path/to/native/native_metadata.txt \
  --native-manifest /path/to/run_manifest.json \
  --out-json /path/to/p3_b_native_spatial_crosscheck.json
~~~

The native artifact is produced by
[research-compute-control run 44222502400](https://github.com/lm846802297-bit/research-compute-control/actions/runs/44222502400).
The direct comparator also requires the manifest to certify the pinned source
commit, AFH response-index mapping, 16,807-row native eight-response PASS,
and exact q grid.
A direct PASS is labelled PASS_NATIVE_AFH_SPATIAL_CROSSCHECK. It validates
these three P3-B channels only; it does not validate the complete three-body
tensor contraction or event rate.
