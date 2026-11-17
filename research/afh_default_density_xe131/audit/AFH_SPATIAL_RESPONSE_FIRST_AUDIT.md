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
- response index 3 calls `SigmaPJ) and gives (W_{\Sigma'});
- response index 6 calls `DeltaJ) and gives (W_\Delta);
- response index 8 is the `SigmaPJ)-`DeltaJ` interference (W_{\Sigma'\Delta}).

The density-matrix inputs in this repository contain 39 entries for Xe-129 and 67 for Xe-131.

## Numerical status

No validated numerical values for (W_\Delta) or (W_{\Sigma'\Delta}) are claimed in this report. The earlier table of (W_M), (W_{\Sigma'}), and their ratios is withdrawn pending a point-by-point native Wolfram comparison.

The Python translation is a development implementation. It must not be treated as an independent validated implementation until all of the following pass:

1. native AFH Wolfram export for response indices 1, 3, 6 and 8 at identical (q_A) values;
2. point-by-point comparison of Python and Wolfram values, with documented tolerances;
3. zero-momentum and finite-(q) checks, including all AFH normalization factors;
4. a convergence test in the multipole sum and stable evaluation of the hypergeometric radial integrals.

The factor-of-four conversion from AFH's raw isoscalar convention to the physical equal-(p/n) response must be applied exactly once, after the package-normalized response has been reproduced.

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

## Next steps

1. Run the native Wolfram exporter in an environment with the required Wolfram runtime.
2. Compare all four responses against the Python implementation and correct any remaining phase, normalization, or radial-integral discrepancies.
3. Only after the comparison passes, publish numerical (W_\Delta) and (W_{\Sigma'\Delta}) tables.
4. Match the baryon-current (F_1^{p,n}(Q^2)) and (F_2^{p,n}(Q^2)), construct the three-body particle tensor, and evaluate the complete nuclear-tensor contraction.
