# AFH v6.0 default-density xenon response curves

## Scope

This directory regenerates the AFH v6.0 built-in default-density
\(W_M^{00}\) response curves for the seven xenon isotopes used by the
natural-xenon baseline:

\[
{}^{128,129,130,131,132,134,136}{\rm Xe}.
\]

The official AFH package is downloaded from the author's software page and
pinned by the SHA-256 digest recorded in the workflow. The code extracts
the built-in sdgXeA density-matrix entries selected by
SetIsotope[54,A,"default","default"], then evaluates the same AFH source
translation already validated against the complete Xe-131 curve.

The q grid is the spatial momentum transfer:
\[
q=|\mathbf q|,\qquad q\in[0,0.6]\ {\rm GeV},\qquad
\Delta q=0.25\ {\rm MeV}.
\]
For each isotope the equal-proton/equal-neutron response shape is normalized
as
\[
R_A(q)=A^2\frac{W_M^{00}(q)}{W_M^{00}(0)},\qquad R_A(0)=A^2.
\]
The response grid itself is independent of the nuclear mass scheme. The
AME2020 mass enters when mapping \(E_R\) to exact spatial q and in the
subsequent kinematics.

## Files

- run_afh_default_xenon_responses.py: parse and evaluate the seven default
  density matrices from the official AFH v6.0 package.
- test_afh_default_xenon_responses.py: check all seven 2401-point grids,
  zero-momentum normalization, non-negativity, and comparison with archived
  reference data.
- output/density_matrices/: extracted density-matrix CSVs, one per isotope.
- output/afh_default_xenon_WM00.csv: combined 16,807-row response grid.
- output/archived_28_sample_comparison.csv: comparison with the 28
  selected NIST-mass response samples already archived in the natural-xenon
  baseline.
- output/metadata.json: source archive and file hashes, isotope-specific
  matrix counts, b_A, T_iso, q grid, and validation results.

## Validation hierarchy

1. All seven source matrices must parse with contiguous indices and an
   isoscalar rank-0 component. Isoscalar rank-2 entries are retained when
   present; their absence for spin-zero isotopes is allowed and corresponds
   to a vanishing rank-2 amplitude.
2. Every isotope must have 2401 finite, nonnegative response points and
   \(R_A(0)=A^2\).
3. The generated Xe-131 curve must match the already validated 2401-point
   Xe-131 reference curve.
4. Interpolation of the generated full curves at the 28 archived NIST-mass
   q points must reproduce the archived \(R_A\) values.

The 28-point comparison is a validation of the source translation; it does
not justify reusing those NIST-q values at AME2020 q. The new full curves are
what allow the natural-xenon halo fold to evaluate each isotope at its own
AME2020 exact spatial q.

## Limitations

- This is a Python source translation of AFH v6.0, not a native Mathematica
  re-execution.
- Xe-124 and Xe-126 are not included because the AFH v6.0 default-density
  matrices used in the natural-xenon baseline are unavailable for them.
- The response grid is a nuclear response only. It does not include the
  three-body matrix-element integral, halo integral, detector response,
  exposure, backgrounds, or likelihood.

Official source: [DMFormFactor v6.0 software page](https://www.ocf.berkeley.edu/~nanand/software/dmformfactor/).
