# Numerical audit: AFH Xe-131 \(M\), \(\Phi''\), and interference

## Run identity

- Study: research/afh_vv_phi_xe131/
- AFH source: v6/dmformfactor-V6.m
- Source SHA-256: dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372
- Density-matrix SHA-256: f656145ba2fb9da741b77faed4c01d0dc457c955fa340928b5dbf9cee9bc5d45
- Matrix rows: 67; isoscalar normal-parity entries: rank 0 = 16, rank 2 = 8
- Oscillator length: 2.2923417985218975 fm
- Grid: 2401 points, 0--0.6 GeV, 0.00025 GeV spacing
- Reproduction workflow environment (GitHub Actions): Python 3.13.18, NumPy 2.5.5, SciPy 1.18.1, SymPy 1.14.0; the exact mpmath version is recorded in run_manifest.json.

## Procedure

1. Read the unmodified 67-entry Xe-131 AFH density matrix already archived in
   research/afh_default_density_xe131/input/.
2. Translate AFH v6.0 MJE, PhiPPJ, BesselElement,
   BesselElementMinus, and BesselElementPlus definitions into Python.
3. Precompute Wigner 3j/6j/9j recoupling coefficients and evaluate the
   q-dependent hypergeometric sums on the 2401-point grid.
4. Assemble W_M, W_PhiPP, and W_MPhiPP in the AFH isoscalar convention.
5. Convert the isoscalar response to equal physical proton/neutron couplings
   by multiplying by four exactly once.
6. Check the four existing mass-response minima, Cauchy--Schwarz at every
   grid node, and high-precision mpmath spot checks.
7. Provide a native Mathematica runner and exact-grid comparator. The native
   execution remains pending until it is run on a Wolfram installation.

## Regression and numerical checks

| Check | Result |
|---|---|
| 67-entry input matrix and rank inventory | PASS |
| AFH default \(b_A\) | PASS |
| Four archived \(M\)-response rank-0/rank-2 amplitudes | PASS |
| Nonzero \(W_{\Phi''}(q=0)\) | PASS |
| \(q_A=256.272\) MeV response ratios | PASS |
| Cauchy--Schwarz over all 2401 points | PASS |
| 60-digit mpmath spot-check at four minima | PASS; max relative amplitude difference \(2.13\times10^{-15}\) |
| Native Mathematica/Python pointwise comparison | PENDING |
| Full three-body coefficient matching | NOT YET PERFORMED |

The full-grid Cauchy--Schwarz maximum is
\(0.9999998601592628\), at \(q_A=470.75\) MeV. This is a normalized
correlation and is expected to be no larger than one.

## Selected-point results

Raw equal-p/n physical response divided by \(A^2\):

| \(q_A\) (MeV) | \(W_{\Phi''}/W_M\) | \(W_{M\Phi''}/W_M\) | \(|W_{M\Phi''}|/\sqrt{W_MW_{\Phi''}}\) |
|---:|---:|---:|---:|
| 157.935778 | 13.5676847 | +0.3313747 | 0.0899635 |
| 256.271868 | 115.8894642 | -1.4624900 | 0.1358535 |
| 365.066569 | 2.2555441 | +0.3599774 | 0.2396898 |
| 499.371886 | 0.69015695 | -0.0882541 | 0.1062334 |

The full numerical values and all 2401 grid points are in
output/afh_vv_phi_xe131_full_grid.csv; the four minima are in
output/afh_vv_phi_xe131_selected_points.csv.

## Normalization audit

For Xe-131, \(J_A=3/2\), so the equal-p/n physical conversion factor is

\[
4\times\frac{4\pi}{2J_A+1}=4\pi.
\]

The raw mass response at q=0 gives
\(R_M(0)/A^2=0.9999174770036694\). The legacy mass-only shape normalization
multiplies by 1.0000825298069376 to enforce exactly \(A^2\). That small
mass-only correction is not imposed on the \(\Phi''\) or mixed response.
Both raw physical and shape-comparison columns are retained in the CSV.

## Scientific interpretation

The \(\Phi''\) nuclear response does not share the deep suppression of the
second \(W_M\) minimum. Therefore a response-level \(W_M\)-only audit is not
sufficient to prove that spin-orbit nuclear structure is negligible.

The table is **not** a three-body cross-section correction. The exact
three-body coefficient multiplying each response is still unknown. In
particular, the elastic VV NREFT mapping cannot be copied into the radiative
three-body process without re-deriving the contraction with the off-shell
\(\chi_2\) propagators and the scalar momentum.

## Reproduction commands

~~~bash
python research/afh_vv_phi_xe131/afh_vv_phi_xe131.py
python -m unittest discover -s research/afh_vv_phi_xe131/tests -v
python research/afh_vv_phi_xe131/verify_phi_mpmath.py
~~~

Native Mathematica execution and comparison commands are in the study README.
