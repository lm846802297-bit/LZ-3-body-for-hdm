# AFH v6.0 full response database for natural xenon

**Status: provisional Python implementation; native seven-isotope validation pending.**

This study extends the existing AFH isotope-response archive from the charge
and selected spatial channels to the complete set of eight response functions
defined by `ResponseNuclear` in AFH DMFormFactor v6.0.

## 1. Isotopes and coverage

The database covers the seven xenon isotopes for which the repository has
AFH v6.0 default density matrices:

| Isotope | Nuclear spin | Density-matrix entries |
|---|---:|---:|
| Xe-128 | 0 | input CSV |
| Xe-129 | 1/2 | 39 |
| Xe-130 | 0 | input CSV |
| Xe-131 | 3/2 | 67 |
| Xe-132 | 0 | input CSV |
| Xe-134 | 0 | input CSV |
| Xe-136 | 0 | input CSV |

The seven-isotope set covers 99.8158% of the natural xenon atom fraction.
Xe-124 and Xe-126 are not silently assigned a different isotope's response
or represented as AFH default-density calculations.

## 2. The eight AFH responses

The index mapping is taken directly from `v6/dmformfactor-V6.m`:

| AFH index | Operator / response | Type |
|---:|---|---|
| 1 | `M`, \(W_M\) | diagonal |
| 2 | `SigmaPPJ`, \(W_{\Sigma''}\) | diagonal |
| 3 | `SigmaPJ`, \(W_{\Sigma'}\) | diagonal |
| 4 | `PhiPPJ`, \(W_{\Phi''}\) | diagonal |
| 5 | `PhiTPJ`, \(W_{\widetilde{\Phi}'}\) | diagonal |
| 6 | `DeltaJ`, \(W_\Delta\) | diagonal |
| 7 | \(M\)-\(\Phi''\) | signed interference |
| 8 | \(\Sigma'\)-\(\Delta\) | signed interference |

The new Python implementation adds the source-defined
\(\Sigma''\) and \(\widetilde{\Phi}'\) matrix elements. In particular,
\[
\Sigma''_J =
\frac{\sqrt{J+1}\,M^{\Sigma}_{J,J+1}
      +\sqrt{J}\,M^{\Sigma}_{J,J-1}}{\sqrt{2J+1}},
\qquad
\widetilde{\Phi}'_J=\Phi'_J+\frac12\Sigma_J.
\]
The \(\Delta_J\) implementation continues to use the same-rank
`MJLDivQ[...,jcap=L,lcap=L]` component called by `DeltaJ`;
it does not substitute the distinct `DeltaPrime` combination.

## 3. Momentum grid and normalization

The standard database uses 2,401 points:
\[
q_A\in[0,0.6]\ \mathrm{GeV},\qquad
\Delta q_A=0.00025\ \mathrm{GeV}=0.25\ \mathrm{MeV}.
\]
For each isotope,
\[
y_A=\left(\frac{q_A b_A}{2}\right)^2,\qquad
b_A=\sqrt{\frac{41.467}
 {45A^{-1/3}-25A^{-2/3}}}\ \mathrm{fm},
\]
with \(b_A\) converted to \(\mathrm{GeV}^{-1}\) before evaluating \(y_A\).

The raw columns reproduce the AFH package convention
\[
W_X^{\rm raw}=\texttt{ResponseNuclear}[y,i,0,0].
\]
The converted response columns are
\[
R_X^{\rm raw}=\frac{4\pi}{2J_A+1}W_X^{\rm raw},
\qquad
R_X^{\rm physical}=4R_X^{\rm raw}.
\]
The factor of four maps the raw isoscalar package convention
(\(A^2/4\) at zero momentum) to equal physical proton and neutron
couplings (\(A^2\)). It is applied exactly once, only in the physical
columns. Signed interference terms are not replaced by absolute values.

## 4. Files

- `run_afh_full_response_database.py`: seven-isotope Python generator.
- `validate_afh_full_response_database.py`: grid, positivity,
  Cauchy-Schwarz, zero-momentum and normalization checks.
- `compare_native_afh_full_response.py`: pointwise comparison
  against native AFH exports, including imaginary residuals.
- `run_afh_full_response_database.wls`: native Wolfram exporter
  calling AFH `ResponseNuclear` for indices 1 through 8.
- `tests/`: regression tests.

## 5. Reproduction

```bash
python -m pip install numpy scipy sympy

python -m unittest discover \
  -s research/afh_full_response_database/tests -p 'test_*.py' -v

python research/afh_full_response_database/run_afh_full_response_database.py \
  --outdir /tmp/afh-full-response

python research/afh_full_response_database/validate_afh_full_response_database.py \
  --csv /tmp/afh-full-response/afh_v6_full_eight_response_7isotope.csv \
  --out-json /tmp/afh-full-response/validation.json

wolframscript -file \
  research/afh_full_response_database/run_afh_full_response_database.wls

python research/afh_full_response_database/compare_native_afh_full_response.py \
  --python-csv /tmp/afh-full-response/afh_v6_full_eight_response_7isotope.csv \
  --native-dir /path/to/native/afh/exports \
  --out-json /tmp/afh-full-response/native_comparison.json
```

## 6. Acceptance gates

A Python internal-consistency PASS is not a native AFH validation. The
database is promoted to native-validated only after all 16,807 isotope/q
rows and all eight response functions agree pointwise with the AFH v6.0
Wolfram `ResponseNuclear` outputs within documented tolerances, and the
native imaginary residuals are negligible.

The database is a nuclear-response input only. It does not include finite-\(t\)
nucleon form factors, three-body Wilson coefficients, the
\(L_{\mu\nu}^{(3)}W_A^{\mu\nu}\) contraction, halo integration, or detector
response. No three-body event-rate correction is claimed here.
