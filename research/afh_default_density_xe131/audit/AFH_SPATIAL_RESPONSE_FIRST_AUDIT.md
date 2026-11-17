# AFH spatial-response audit: source mapping correction and validation status

## Executive status

The first Python translation contained an operator-mapping error in the `Delta` channel and its previously printed numerical table is withdrawn. Do not use those numerical values as physics results.

The correction follows the actual AFH v6.0 call chain:

```
DeltaJ -> DeltaJE -> Deltaop -> MJLDivQ[..., jcap=L, lcap=L]
```

The previous translation incorrectly used the rank-`L±1` combination called `DeltaPrime`. `DeltaPrime` is not the operator called by `DeltaJ`.

The code now evaluates the same-rank `MJLDivQ` component for `DeltaJ`. The earlier claim of an intrinsic parity contradiction is also withdrawn: the 3-j selection rule in the `lcap=L` terms is consistent with the AFH abnormal-parity wrapper.

## AFH source mapping

From `v6/dmformfactor-V6.m`:

- response index 1 calls `MJ` and gives (W_M);
- response index 3 calls `SigmaPJ` and gives (W_{\Sigma'});
- response index 6 calls `DeltaJ` and gives (W_\Delta);
- response index 8 is the `SigmaPJ`–`DeltaJ` interference (W_{\Sigma'\Delta}).

The density-matrix inputs in this repository contain 39 entries for Xe-129 and 67 for Xe-131.

## Numerical status

The native Xe-131 export of AFH indices 1, 4 and 7 now provides an independent
anchor for the shared radial/multipole implementation. A Python translation
of the source-defined \(\Phi''\) operator reproduces the native \(W_M\),
\(W_{\Phi''}\), and signed \(W_{M\Phi''}\) at eight selected points
\(q_A=0,0.05,0.10,0.158,0.25625,0.365,0.49925,0.60\) GeV. The maximum
relative differences are:

| Response | Maximum relative difference |
|---|---:|
| \(W_M\) | \(2.96\times10^{-9}\) |
| \(W_{\Phi''}\) | \(1.04\times10^{-12}\) |
| \(W_{M\Phi''}\) | \(9.14\times10^{-11}\) |

This comparison exposed and corrected a factor-of-two error in the Python
response normalization: the AFH diagonal and interference response
definitions both reduce to a \(1/4\) multipole-amplitude product in the
\(\tau_1=\tau_2=0\) convention. The factor-four conversion to physical
equal-p/n couplings is still applied only afterward, and is not included in
these raw package-response comparisons.

This does **not** validate the \(\Sigma'\), \(\Delta\), or
\(\Sigma'\Delta\) operators. No validated numerical values for
\(W_\Delta\), \(W_{\Sigma'}\), or \(W_{\Sigma'\Delta}\) are claimed.
The earlier Python selected-\(q\) spatial-response table remains withdrawn
until native Wolfram exports for indices 3, 6 and 8 are compared point by
point. A new CI pre-audit now runs the development translation on ten selected
\(q_A\) values for Xe-129 and Xe-131 and uploads a 20-row provisional CSV,
metadata, and SHA-256 manifest as an Actions artifact. This artifact proves
that the Python path executes and emits finite outputs; it does **not** turn
the \(\Sigma'\), \(\Delta\), or \(\Sigma'\Delta\) values into validated AFH
results.

The PR workflow run [44187336196](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44187336196)
completed with 5/5 spatial-response tests passing and uploaded artifact
14373574958. The test suite includes the eight-anchor Xe-131 native comparison
for \(M\), \(\Phi''\), and signed \(M\Phi''\); the new spatial-channel values
remain provisional pending native index-3/index-6/index-8 comparison.

The spatial Python translation is still a development implementation. It
must not be treated as validated until all of the following pass:

1. native AFH Wolfram export for response indices 1, 3, 6 and 8 at identical
   \(q_A\) values for both Xe-129 and Xe-131;
2. point-by-point comparison of Python and Wolfram values for the spatial
   operators, with documented tolerances;
3. zero-momentum and finite-\(q\) checks, including all AFH normalization
   factors;
4. convergence tests in the multipole sum and stable evaluation of the
   hypergeometric radial integrals.

## Current physical interpretation

A large ratio (W_{\Sigma'}/W_M) near a diffraction minimum would not by itself imply a large correction to the scattering rate. The physical coefficient of the magnetic current contains the appropriate nucleon magnetic form factor and momentum suppression, and the three-body particle tensor must be contracted with the nuclear tensor. The required comparison is the complete (L_{\mu\nu}W_A^{\mu\nu}) against the (L_{00}W_M) approximation.

The universal quark-vector assumption fixes equal zero-momentum Dirac charges for proton and neutron. It does not determine the baryon-current Pauli form factors (F_2^{p,n}). The magnetization-current coefficients therefore still require a separate matching calculation.

## Reproduction and native reference

Python development audit:

```bash
python research/afh_default_density_xe131/run_afh_spatial_response_audit.py --outdir /tmp/afh-spatial-audit
python -m unittest research/afh_default_density_xe131/tests/test_afh_spatial_response_audit.py -v
```

Native AFH/Wolfram reference export:

```bash
wolframscript -file research/afh_default_density_xe131/run_afh_spatial_response_audit.wls
```

The native runner exports the package's own `ResponseNuclear[y,{1,3,6,8},0,0]` results for Xe-129 and Xe-131. Those outputs are the reference data for validating the Python translation.

## Python full-grid result: provisional only

The Python development translation has now been evaluated on a uniform
2,401-point grid for each isotope:
\[
q_A\in[0,0.6]\ \mathrm{GeV},\qquad
\Delta q_A=0.00025\ \mathrm{GeV}=0.25\ \mathrm{MeV}.
\]
The archive contains 4,802 rows total (2,401 each for Xe-129 and Xe-131).
The full-grid workflow completed successfully, and its validator reported
**PASS** for grid identity, finite values, nonnegative diagonal responses,
and the Cauchy–Schwarz bounds for both \(M\)-\(\Phi''\) and
\(\Sigma'\)-\(\Delta\) response matrices.

**This is a Python internal-consistency PASS only.** It is not a native AFH
Wolfram comparison and does not validate the translated \(\Sigma'\), \(\Delta\),
or \(\Sigma'\Delta\) operators against AFH. Do not treat the following ratios
as physical cross-section enhancements.

| Isotope | Largest sampled \(W_{\Sigma'}/W_M\) | \(q_A\) [GeV] | Largest sampled \(W_\Delta/W_M\) | \(q_A\) [GeV] |
|---|---:|---:|---:|---:|
| Xe-129 | \(8.2606\times10^3\) | 0.50100 | 22.6797 | 0.25800 |
| Xe-131 | 4.91329 | 0.49875 | 2.04565 | 0.25625 |

These large ratios are driven by deep sampled minima of \(W_M\), not by
large absolute spatial responses. For example:

- Xe-129 at \(q_A=0.501\ \mathrm{GeV}\): \(W_M/W_M(0)=4.38\times10^{-12}\),
  while \(W_{\Sigma'}/W_{\Sigma'}(0)=1.15\times10^{-3}\). The ratio
  \(W_{\Sigma'}/W_M\) is therefore dominated by the suppressed denominator.
- Xe-131 at \(q_A=0.25625\ \mathrm{GeV}\):
  \(W_M/W_M(0)=6.35\times10^{-8}\),
  \(W_{\Sigma'}/W_{\Sigma'}(0)=5.31\times10^{-3}\), and
  \(W_\Delta/W_\Delta(0)=2.77\times10^{-3}\).

The practical implication is that the spatial responses cannot be discarded
solely because the halo velocity is small or because their ratios are small
away from diffraction minima. Their actual contribution still depends on the
three-body Wilson coefficients, nucleon form factors, signed interference,
and the full particle–nucleus tensor contraction. No rate conclusion follows
from these response ratios alone.

**Reproducibility**

- Source commit: \`bccea2f710aef62a70b2980f0a6c7f3a901f654f\`.
- Full-grid Actions run: [44192464067](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44192464067).
- Downloadable artifact: [artifact 14377421949](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44192464067/artifacts/14377421949).
- CSV SHA-256: \`08dd97f5db1d9e17d396b992290c694cd09ee88d83ad68affc2ad3ddc794d255\`.
- Metadata SHA-256: \`2dba829c5fc70b95a1acc2ee9a256cdadf80e96ab81dddc35ca8c2c24cf3b004\`.
- Validation SHA-256: \`e09c01fb89f7ca981c0b3eeff68788d3b8be842dc22cdc04adac83aee40cbf40\`.

The archive retains the raw AFH isoscalar convention
\(\tau_1=\tau_2=0\); no physical equal-\(p/n\) factor four is applied.
The factor four must be introduced once, consistently, only when mapping
these raw package responses to the physical equal-\(p/n\) coupling.

## Python/native comparator and execution state

The pointwise comparator is available at
\`research/afh_default_density_xe131/compare_afh_spatial_response.py\`.
It matches Python and native columns for \(W_M\), \(W_{\Sigma'}\),
\(W_\Delta\), and signed \(W_{\Sigma'\Delta}\), checks isotope/q-grid identity,
and enforces the response-matrix Cauchy–Schwarz bound. Synthetic regression
tests cover matching, mismatches, duplicate rows, q-grid mismatches, and
interference-bound failures.

The selected-point Linux pre-audit completed successfully on the same
11-point grid used by the native runner:
\(q_A=0,0.05,0.10,0.158,0.20,0.25625,0.30,0.365,0.45,0.49925,0.60\)
GeV for both Xe isotopes. The full-grid Python run above also completed.
Neither run replaces the native Wolfram comparison.

The native run is configured through the private control repository
\`lm846802297-bit/research-compute-control\`, with the research checkout
pinned to commit \`f29209247b4f4124549ca0ee8f164bb5add30b1b\`. The latest
native workflow run \`44190383661\` is queued and has not produced Wolfram
output. Therefore the spatial Python translation remains provisional.

## Next steps

1. Complete the pinned native Wolfram run for response indices \(1,3,6,8\)
   on both Xe isotopes and the 11-point common grid.
2. Run the pointwise comparator; inspect signs, normalizations, and residuals
   before accepting any spatial-response table.
3. Only after the native comparison passes, extend the q grid and publish
   validated \(W_\Delta\) and \(W_{\Sigma'\Delta}\) results.
4. Match finite-\(Q^2\) baryon-current \(F_1^{p,n}\) and \(F_2^{p,n}\),
   derive the three-body particle tensor coefficients, and evaluate the
   complete \(L_{\mu\nu}W_A^{\mu\nu}\) contraction.
