# Xe-131 AFH M, Phi'', and M-Phi'' response export

## Status

**Native Wolfram execution archived; response-level validator PASS (2026-11-18).**
The 2,401-node Xe-131 export, metadata, validation summary, and SHA-256
manifest are committed under output/phi_response_native/. This validates
the AFH v6.0 native nuclear responses and their normalization/bookkeeping
only; it does not validate the three-body Wilson coefficients or the
complete scattering rate.

The work continues on PR #51 and uses the official AFH v6.0 package and its
built-in Xe-131 default density matrix. It does not create a second isotope
response PR.

## Why these two responses come first

For the flavor-universal VV benchmark, the leading one-body nuclear charge is
the AFH \(M\) response. The subleading spin-orbit charge operator can project
onto \(\Phi''\), and its interference with the leading charge must be
retained through \(W_{M\Phi''}\). The interference is signed; it must not be
replaced by its absolute value or dropped before the amplitude-level
combination.

The official AFH v6.0 source already exposes the required response indices:

| AFH index | Source operator | Exported quantity |
|---:|---|---|
| 1 | MJ | \(W_M^{00}\) |
| 4 | PhiPPJ | \(W_{\Phi''}^{00}\) |
| 7 | MJ--PhiPPJ | \(W_{M\Phi''}^{00}\) |

The source-level mapping is in the v6/dmformfactor-V6.m file, in
ResponseNuclear. The new runner uses these existing package routines;
it does not reimplement the AFH angular-momentum algebra.

## Exact numerical setup

- Isotope: Xe-131, \(A=131\), \(Z=54\), \(J_A=3/2\).
- Density matrix: built-in sdgXe131, 67 entries.
- Isospin selector: tau1=tau2=0, the raw AFH isoscalar package convention.
- Source: AFH/DMFormFactor v6.0, source SHA-256
  dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372.
- Density-matrix CSV SHA-256:
  f656145ba2fb9da741b77faed4c01d0dc457c955fa340928b5dbf9cee9bc5d45.
- Oscillator length: the same AFH default prescription as the existing
  \(W_M\) archive, with \(1\,\mathrm{fm}=5.0677\,\mathrm{GeV}^{-1}\).
- Momentum: \(q_A=|\mathbf P_A'-\mathbf P_A|\), not the dark-matter
  momentum difference \(q_\chi\), and not the Minkowski invariant \(t_A\).
- Grid: 2,401 points from 0 to 0.6 GeV in 0.25 MeV increments.

## Normalization: factor four exactly once

The runner exports the raw package responses from
ResponseNuclear[y,i,0,0]. It then defines

\[
R_X^{\rm raw}(q_A)=\frac{4\pi}{2J_A+1}W_{X,\rm AFH}^{00}(q_A),
\qquad X\in\{M,\Phi'',M\Phi''\}.
\]

For physical equal proton and neutron couplings, it writes

\[
R_X^{\rm phys}(q_A)=4R_X^{\rm raw}(q_A).
\]

This same linear mapping applies to the two diagonal responses and their
interference. The export deliberately does not apply the separate tiny
zero-momentum shape renormalization used by the legacy \(W_M\) table. That
keeps the new raw package output transparent and prevents a second
normalization convention from entering the interference response.

The \(M\) channel is the normalization anchor:

\[
R_M^{\rm raw}(0)\simeq A^2/4,
\qquad
R_M^{\rm phys}(0)\simeq A^2.
\]

The runner stops if the raw \(M\) zero-momentum normalization differs from
\(A^2/4\) by more than \(2\times10^{-4}\), matching the tolerance already
used for the rounded AFH density-matrix coefficients.

## Acceptance checks in the Python validator

The validator checks:

1. exact Xe-131, source, density-matrix, AFH-index, and isospin provenance;
2. the complete 2,401-node \(q_A\) grid and
   \(y=(q_A b_A/2)^2\);
3. the \(4\pi/(2J_A+1)\) conversion for all three response channels;
4. the physical factor-four mapping for \(M\), \(\Phi''\), and
   \(M\Phi''\), exactly once;
5. non-negativity of the two diagonal responses;
6. the positive-semidefinite response-matrix bound
   \[
   |R_{M\Phi''}|^2\le R_M R_{\Phi''};
   \]
7. negligible imaginary residuals in the native AFH output;
8. the \(A^2/4\to A^2\) zero-momentum charge normalization;
9. the CSV SHA-256 recorded by the native execution metadata.

The Cauchy-Schwarz check is an algebraic consistency test on the response
matrix. It is not an independent nuclear-structure calculation.

## Archived numerical findings

The committed native CSV contains 2,401 rows and 14 columns. The dedicated
validator reports PASS with zero recorded residual for the q-to-y map,
the 4pi/(2J_A+1) response conversion, the factor-four mapping, and the
imaginary parts; the diagonal responses are non-negative and the
Cauchy-Schwarz bound is satisfied. The maximum normalized interference
correlation extracted from the CSV is
\[
\max_{q_A}\frac{|R_{M\Phi''}|}{\sqrt{R_M R_{\Phi''}}}
=0.9999998602.
\]
This is a response-matrix consistency result, not an independent nuclear
model calculation.

A separate Python source translation of AFH PhiPPJ, including its four
summands and BesselElementMinus/Plus radial integrals, reproduces native
Xe-131 W_M, W_PhiPP and signed W_MPhiPP at eight q anchors. The maximum
relative differences are 2.96e-9, 1.04e-12 and 9.14e-11, respectively.
This is a selected-anchor cross-check, not an independent 2,401-point
full-grid recalculation, and it does not validate SigmaPrime or Delta.

The raw zero-momentum normalization is
\[
R_M^{\rm raw}(0)=4289.895955714992,
\qquad A^2/4=4290.25,
\]
with relative offset \(8.25230\times10^{-5}\). After the one-time factor-four
mapping, \(R_M^{\rm phys}(0)=17159.583822859968\), compared with
\(A^2=17161\). The small difference is the rounded AFH density-matrix
coefficient offset; no shape renormalization is applied to this export.

The four local minima of the sampled \(R_M\) grid give the following raw
response values:

| \(q_A\) [GeV] | \(R_M^{\rm raw}\) | \(R_{\Phi''}^{\rm raw}\) | \(R_{M\Phi''}^{\rm raw}\) | \(R_{\Phi''}/R_M\) |
|---:|---:|---:|---:|---:|
| 0.15800 | 5.31451e-2 | 7.14832e-1 | 2.62061e-2 | 13.45 |
| 0.25625 | 2.72531e-4 | 3.15623e-2 | -5.24943e-4 | 115.81 |
| 0.36500 | 6.70326e-4 | 1.51514e-3 | 2.21762e-4 | 2.26 |
| 0.49925 | 7.16871e-5 | 4.96083e-5 | -7.30759e-6 | 0.692 |

The large ratio near \(q_A=0.25625\,\mathrm{GeV}\) is driven by the deep
suppression of \(R_M\): the absolute \(R_{\Phi''}\) there is only
\(2.11\times10^{-4}\) of its q=0 value. Therefore the ratio is not a
115.8-fold enhancement of the physical cross section. The signed
\(M\)-\(\Phi''\) interference and the actual three-body coefficients must
be included before any rate-level statement is made.

## Reproduction on the Windows/Wolfram machine

From the repository root, after confirming that wolframscript is on PATH:

~~~powershell
powershell -ExecutionPolicy Bypass -File research/afh_default_density_xe131/run_native_phi_response_windows.ps1
python -m unittest research.afh_default_density_xe131.tests.test_afh_phi_response -v
~~~

The committed archive under output/phi_response_native/ contains:

- afh_default_xe131_M_PhiPP_native.csv — 2,401 response rows;
- afh_default_xe131_M_PhiPP_metadata.json — source/input hashes, Wolfram
  version, grid and normalization metadata;
- afh_default_xe131_M_PhiPP_validation.json — Python validator summary;
- sha256_manifest.json — SHA-256 digests for the CSV, metadata and
  validation summary.

The Windows wrapper writes the validation file under this canonical archive
name and regenerates the manifest. Re-running it locally should reproduce the
same numerical rows and metadata values; runtime timestamps are not part of
the native metadata.

## What this stage does not establish

- It does not determine the finite-momentum universal-flavor nucleon
  \(F_1^V(t)\) and \(F_2^V(t)\) inputs.
- It does not derive the complete three-body NR Wilson coefficients from
  \(\mathcal T_3^\mu\).
- It does not calculate \(\Delta\), \(\Sigma'\), \(\Sigma''\), or
  \(\widetilde\Phi'\) in this new run.
- It does not contract \(L_{\mu\nu}W_A^{\mu\nu}\), recompute
  \(d\sigma/dE_R\), or produce a natural-xenon halo-folded spectrum.
- It does not prove that \(W_M\) alone is accurate or inaccurate in the
  physical three-body rate.

The next physics step after the native response export is to derive the
three-body Dirac-Pauli matching coefficients and combine the response
functions with their actual coefficients. Only then can the full one-body
current be compared quantitatively with the existing \(L_{00}W_M\) baseline.
