# P3-B independent Python implementation cross-check

**Status: PASS — independent Python implementation consistency. Native AFH validation remains pending.**

Date: 2026-11-18

## 1. Scope

The P3-B spatial OBDME engine was compared row by row against the earlier
seven-isotope, eight-response AFH v6.0 Python database. The comparison covers
the three spatial channels needed by the leading static vector current:

- AFH index 3: \(W_{\Sigma'}\);
- AFH index 6: \(W_{\Delta}\);
- AFH index 8: signed \(W_{\Sigma'\Delta}\).

This is a cross-implementation check, not a Mathematica/Wolfram native
comparison. Both input artifacts are explicitly marked provisional with
native_afh_validated=false.

## 2. Exact artifacts and provenance

| Item | Value |
|---|---|
| P3-B grid workflow | [44296729828](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44296729828) |
| P3-B artifact | 14423594659 — provisional-afh-spatial-obdme-responses |
| P3-B CSV SHA-256 | 4e0a23c18d29df3af04a2531e75b7bffeaa3251d0efe97674b2287cf3c25e7e3 |
| Independent eight-response workflow | [44222087512](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44222087512) |
| Eight-response artifact | 14391456283 — afh-v6-seven-isotope-eight-response |
| Eight-response CSV SHA-256 | 59ea25093137a05b8ebcc158e2fe6a74fe5927599dbb16766b067aa1ad8e3caa |
| Eight-response source commit | dcefbeb7ad705b6c03f2b4689200eb1d9252e67b |
| P3-B PR head | 7304e1aefd29711ffb862cb1f9804ca5fa82814b |

Both files contain 16,807 rows: seven isotopes times 2,401 momentum nodes.
The two q_A grids are identical, from 0 to 0.6 GeV in 0.00025 GeV
increments. The maximum absolute difference in q_A and in the stored
y_A values is exactly zero.

The independent eight-response generator imports a different AFH Python
translation path (run_afh_spatial_response_audit.py) from the one used
by the P3-B engine. The two paths implement the same source-defined
MJLDivQ, MJLSigma, DeltaJ, and SigmaPJ definitions.

## 3. Source and OBDME identity

The AFH package source is the same Git blob at the P3-B PR head and the
native-workflow pinned source:

- Path: v6/dmformfactor-V6.m
- Git blob: 91b43b1a4596bebd6073ecd44c0c9464e5dd0c63
- SHA-256 recorded by the calculation metadata:
  dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372

For every isotope, the input/afh_default_density_matrices file and the
P3 archive's results/full_afh_v6_default_7_isotope_response/density_matrices
copy have identical Git blob IDs. These IDs are also identical between the
P3-B PR head and the native-workflow pinned commit dcefbeb.

| Isotope | OBDME Git blob SHA |
|---|---|
| Xe-128 | 74904ec6f3419624cfd8092385da9374bc1065b4 |
| Xe-129 | 400ba5f474bd8e84784852f942d04589ebf3dc30 |
| Xe-130 | 38ebca82063c8814d9d5e0179a431383eb64eb00 |
| Xe-131 | 6b0e59f96c9712fea28495f35dc0401cd4e3fa6c |
| Xe-132 | d4ca727a96c0d493bff96336a2fa4e6ae304f1ae |
| Xe-134 | 9a3e71561e04a4ecc77af6764601d6ae010aa853 |
| Xe-136 | 0ef0ec7ed4362e02e3533e1ba0a3aa934b7cecdf |

Thus the cross-implementation comparison uses the same AFH source and
byte-identical OBDME inputs; it is not a comparison between different
nuclear-structure datasets.

## 4. Raw AFH package response comparison

The P3-B output columns were compared directly with the corresponding
columns in the independent eight-response database:

| P3-B column | Independent database column | Max. absolute difference | Max. relative difference | Worst point |
|---|---|---:|---:|---|
| W_Delta_AFH_package | W_Delta00_AFH | \(2.78\times10^{-17}\) | \(3.20\times10^{-14}\) | Xe-129, 0.13350 GeV |
| W_SigmaPrime_AFH_package | W_SigmaPrime00_AFH | \(1.73\times10^{-17}\) | \(2.45\times10^{-13}\) | Xe-129, 0.37250 GeV |
| W_SigmaPrimeDelta_AFH_package | W_SigmaPrimeDelta00_AFH | \(1.73\times10^{-17}\) | \(1.23\times10^{-13}\) | Xe-129, 0.37250 GeV |

All 16,807 isotope/q rows matched, with zero failed points at
\(\mathrm{rtol}=5\times10^{-12}\) and
\(\mathrm{atol}=2\times10^{-14}\). The mixed response was compared with its
sign intact; it was not replaced by its absolute value. The numeric comparison
uses Python's standard-library CSV parser and float conversion; pandas' default
fast float parser is deliberately avoided for this last-digit precision audit.
The reusable comparator is
[compare_p3_spatial_vs_afh8.py](../../../afh_response_crosschecks/compare_p3_spatial_vs_afh8.py).

## 5. Physical equal-p/n normalization comparison

The independent database stores
\[
R_{X,\mathrm{physical}}^{\mathrm{DB}}
=4\,\frac{4\pi}{2J_A+1}W_X.
\]

P3-B additionally applies the common finite-decimal OBDME correction
\(C_0\), fixed only by the coherent \(M(q_A=0)=A^2\) anchor:
\[
R_{X,\mathrm{physical}}^{\mathrm{P3}}
=4C_0\,\frac{4\pi}{2J_A+1}W_X.
\]

Therefore the correct comparison is
\(R_X^{\mathrm{P3}}\) against
\(C_0R_{X,\mathrm{physical}}^{\mathrm{DB}}\). This keeps the AFH
isoscalar factor of four separate from the small OBDME rounding correction.

| Isotope | Common \(C_0\) |
|---|---:|
| Xe-128 | 1.0000924953327093 |
| Xe-129 | 1.0001103230777202 |
| Xe-130 | 1.0001260610682260 |
| Xe-131 | 1.0000825298069376 |
| Xe-132 | 1.0000445028489864 |
| Xe-134 | 1.0002068258192740 |
| Xe-136 | 1.0000015063597725 |

After this conversion, the maximum relative differences are:

| Physical response | Max. absolute difference | Max. relative difference | Worst point |
|---|---:|---:|---|
| \(R_\Delta\) | \(3.33\times10^{-16}\) | \(3.20\times10^{-14}\) | Xe-129, 0.13350 GeV |
| \(R_{\Sigma'}\) | \(4.44\times10^{-16}\) | \(2.45\times10^{-13}\) | Xe-129, 0.37250 GeV |
| \(R_{\Sigma'\Delta}\) | \(2.22\times10^{-16}\) | \(1.23\times10^{-13}\) | Xe-129, 0.37250 GeV |

The factor four is applied once. \(C_0\) is a separate, approximately
\(10^{-4}\)-level finite-decimal correction and must not be described as
another isospin factor.

## 6. Structural checks on the generated grid

- Xe-128, Xe-130, Xe-132, Xe-134 and Xe-136 have \(J_A=0\); all three
  spatial responses vanish exactly at all 2,401 nodes.
- Xe-129 and Xe-131 have finite spatial responses.
- The maximum Cauchy--Schwarz excess over the full grid is
  \(3.47\times10^{-18}\), consistent with floating-point roundoff.
- The signed \(W_{\Sigma'\Delta}\) changes sign over the momentum grid:
  - Xe-129: approximately \([-4.95951\times10^{-3},\,
    1.04324\times10^{-4}]\);
  - Xe-131: approximately \([-1.84016\times10^{-3},\,
    3.07077\times10^{-2}]\).

The sign-changing mixed response must remain signed in the subsequent
three-body contraction.

## 7. Interpretation and remaining gate

This result closes an important **Python-to-Python implementation
consistency** check for P3-B. It strongly constrains errors in the radial
Bessel derivatives, angular-momentum recoupling, OBDME summation, response
normalization and mixed-response sign.

It does **not** yet establish native AFH agreement. The independent
eight-response artifact itself records
status=PROVISIONAL_PYTHON and native_afh_validated=false.

The private native workflow in
[research-compute-control run 44222502400](https://github.com/lm846802297-bit/research-compute-control/actions/runs/44222502400)
is still queued (attempt 2). It pins the AFH source and seven OBDME inputs
identified above, exports native Wolfram
ResponseNuclear[y,index,0,0] for indices 1--8, and compares all
16,807 rows with rtol=5e-7, atol=2e-12, and native imaginary residual
tolerance 2e-12.

The direct comparison is prepared in
[compare_p3_spatial_vs_native.py](../../../afh_response_crosschecks/compare_p3_spatial_vs_native.py).
It requires the native metadata and run manifest, checks the pinned source
commit and full eight-response native PASS, then compares indices 3, 6 and 8
directly with the P3-B CSV. Only after that comparison passes should P3-B be
marked native-validated. P3-C must then contract
these nuclear multipoles with the full complex three-body tensor; the
present response-only comparison is not a rate correction or a conclusion
about the numerical size of the spatial-current contribution.


## 8. Rank-resolved multipole archive correction

A source audit found that the first P3-B grid artifact retained the three
total spatial responses but did not serialize the rank-by-rank amplitudes
returned by the engine. The earlier wording that all multipole amplitudes
were already archived was therefore too strong.

The generator has now been extended to write a second file:

afh_spatial_obdme_multipoles_7isotope_2401.csv

For every isotope, momentum node, and nonzero abnormal-parity OBDME rank,
the new file stores:

- the signed real amplitudes \(\mathcal M_{\Delta,J}\) and
  \(\mathcal M_{\Sigma',J}\);
- the rankwise diagonal contributions
  \(W_{\Delta,J}=\mathcal M_{\Delta,J}^2/4\) and
  \(W_{\Sigma',J}=\mathcal M_{\Sigma',J}^2/4\);
- the signed rankwise interference
  \(W_{\Sigma'\Delta,J}=\mathcal M_{\Sigma',J}\mathcal M_{\Delta,J}/4\);
- the corresponding physical equal-p/n rank contributions, including the
  single factor four and the common OBDME normalization \(C_0\).

The generator checks at every \((A,q_A)\) that summing the rankwise raw and
physical contributions reconstructs all three total responses. A separate
validator checks the output file hashes, full isotope/q grid, unique
\((A,q_A,J)\) keys, spin-zero isotope null channels, normalization identities,
and rank-summed reconstruction.

The new validator is
[validate_afh_spatial_multipole_archive.py](../../validate_afh_spatial_multipole_archive.py).
The CI workflow runs it before uploading the P3-B artifact.

**Current status: PASS — refreshed rank-resolved archive.** Workflow
[44303047483](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44303047483)
completed the spatial-response job and uploaded artifact 14426558224,
provisional-afh-spatial-obdme-responses. The archive contains:

| File | Rows | SHA-256 |
|---|---:|---|
| afh_spatial_obdme_responses_7isotope_2401.csv | 16,807 | 4e0a23c18d29df3af04a2531e75b7bffeaa3251d0efe97674b2287cf3c25e7e3 |
| afh_spatial_obdme_multipoles_7isotope_2401.csv | 9,604 | e83f7499cd0af4ec8f1974238f09daf4899ca1b87205ec837ae0964a2e8532c6 |

The rank coverage is Xe-129: J=1; Xe-131: J=1,2,3; and no abnormal
spatial ranks for the five spin-zero isotopes. Per-isotope C0 is also recorded
in metadata: Xe-128 1.0000924953327093; Xe-129 1.0001103230777202;
Xe-130 1.0001260610682259; Xe-131 1.0000825298069376;
Xe-132 1.0000445028489864; Xe-134 1.0002068258192740;
Xe-136 1.0000015063597723. The archive validator returned
PASS_AFH_SPATIAL_MULTIPOLE_ARCHIVE. The maximum absolute reconstruction
residuals are zero for the three raw AFH responses and at most
2.22e-16 for the three physical equal-p/n responses. The maximum rankwise
Cauchy--Schwarz excess is 3.47e-18.

The refreshed response CSV was re-compared against the independent AFH-8
Python database. All 16,807 rows pass at rtol=5e-12 and atol=2e-14; the
maximum relative differences remain 3.20e-14 for Delta,
2.45e-13 for SigmaPrime, and 1.23e-13 for SigmaPrime-Delta.

This archive remains provisional Python output. It does not promote
native_afh_validated and does not replace the queued native Wolfram gate.
