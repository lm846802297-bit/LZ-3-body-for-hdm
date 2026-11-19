# Native AFH gate and Coulomb-sector halo-fold dependency

**Updated: 2026-11-19**

## 1. Acceptance state

The seven-isotope/eight-response native AFH comparison remains a hard input
gate for the natural-xenon Coulomb-sector halo engine. Keep these distinct:

| Layer | Evidence | State |
|---|---|---|
| Seven-isotope/eight-response Python reference database | Run 44244699196, artifact 14400843100 | PASS for Python internal checks only |
| Seven-isotope/eight-response native Wolfram comparison | Private control run 44222502400, attempt 2 | QUEUED; no artifact |
| Single-isotope Xe-131 native charge-response archive | Xe-131 workflow run 44262472992, artifact 14408816831 | PASS for \(M,\Phi'',M\Phi''\) only |
| Native Coulomb-sector halo engine | Requires the seven-isotope native artifact root | Implemented; production fold blocked by native gate |
| Full leading-static vector-current halo rate | Requires transverse multipoles and P3 tensor validation | Not yet complete |

The Python reference database has 16,807 rows (seven isotopes times 2,401
q points). Its positivity, normalization, and interference checks do not
constitute native Wolfram validation.

The private native job is in
lm846802297-bit/research-compute-control, workflow
xe131-afh-spatial-native.yml, job native-afh-eight-response, run
44222502400 attempt 2. It targets the self-hosted labels Windows, X64, and
research-gpu. The latest observed state is QUEUED and the run has no
uploaded artifact. The seven-isotope native gate therefore remains OPEN.

## 2. Pinned seven-isotope native source

The private control workflow pins the LZ research checkout to
\`dcefbeb7ad705b6c03f2b4689200eb1d9252e67b\`, with AFH DMFormFactor v6.0.

The isotope set is exactly
\[
[128,129,130,131,132,134,136],
\]
and the eight response indices are:

| Index | Response |
|---:|---|
| 1 | \(M\) |
| 2 | \(\Sigma''\) |
| 3 | \(\Sigma'\) |
| 4 | \(\Phi''\) |
| 5 | \(\widetilde\Phi'\) |
| 6 | \(\Delta\) |
| 7 | signed \(M\Phi''\) |
| 8 | signed \(\Sigma'\Delta\) |

The q grid is 2,401 points per isotope from 0 to 0.6 GeV in 0.00025 GeV
steps, for exactly 16,807 pointwise rows.

## 3. Native artifact layout and acceptance

The private control workflow uploads an artifact root containing:

- \`native/\` with seven CSV exports, Xe-128/129/130/131/132/134/136;
- \`native/native_metadata.txt\`;
- \`native-comparison.json\`;
- \`run_manifest.json\`;
- \`SHA256SUMS.txt\`.

The halo engine must receive the extracted artifact root, not merely
\`native/\`. Before loading responses it verifies:

1. comparison status PASS, native_afh_validated=true, rows_compared=16807;
2. all seven isotope CSVs contain 2,401 points on the exact q grid;
3. all eight response names are present in the pointwise comparison and the
   failure list is empty;
4. comparison tolerances are no looser than rtol=5e-7, atol=2e-12, and
   imaginary residual 2e-12;
5. run manifest source commit, AFH package, isotope set, response map, q grid,
   Wolfram/Python versions, and control-run identity match the pin;
6. native metadata and all seven CSVs exist;
7. SHA-256 checksums of the comparison, manifest, metadata, and seven CSVs
   match SHA256SUMS.txt;
8. every response value is finite and imaginary residuals are negligible.

A native PASS validates the nuclear response database only. It does not
validate the three-body particle-side coefficients or the full
\(L_{\mu\nu}^{(3)}W_A^{\mu\nu}\) contraction.

## 4. What the current halo engine computes

The engine consumes the complete native artifact root but, in its current
restricted mode, reads the three charge-sector responses \(W_M\),
\(W_{\Phi''}\), and signed \(W_{M\Phi''}\). Its leptonic Coulomb weight is
\[
L_C^{(3)}=L_{00}^{(3)}
-\frac{E_R}{Q_A}(L_{03}^{(3)}+L_{30}^{(3)})
+\left(\frac{E_R}{Q_A}\right)^2L_{33}^{(3)}.
\]
Thus it includes the nuclear longitudinal current through the conserved
one-body nuclear-current relation, conditional on that continuity
assumption. It is not an \(L_{00}\)-only calculation.

The engine computes \(M+\Phi''+M\Phi''\) with exact isotope-specific
\(q_A(E_R)\), finite-\(t_N\) form factors, and the full three-body
phase-space tensor. It omits the transverse \(\Delta\), \(\Sigma'\), and
\(\Sigma'\)-\(\Delta\) multipoles. Its status is
\`COMPUTED_WITHIN_COULOMB_SECTOR_APPROXIMATION\`, with
\`full_current_complete=false\`.

The provisional fixed-speed Python AFH contraction gives
\[
\max |R_{\rm spatial}/R_{\rm Coulomb}|=7.09596\times10^{-9}
\]
over 84 tested rows only. This is not a global halo-integrated bound and is
not a reason to omit the spatial terms from the final kernel.

## 5. Separate single-isotope Xe-131 native charge archive

The independent Xe-131 archive used for the fixed-speed diagnostic is
AFH v6.0 / Wolfram 14.2.0 and contains 2,401 q nodes for the three native
charge responses \(M,\Phi'',M\Phi''\). It is pinned to archive commit
\`e6d9dee3527cab200ee6b21198d577b987282fac\`; the original native export
commit is \`54e1ff10bba0cbffe7acc6af428014415c708475\`.

The archive checks:
- AFH source SHA-256
  \`dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372\`;
- density-matrix CSV SHA-256
  \`f656145ba2fb9da741b77faed4c01d0dc457c955fa340928b5dbf9cee9bc5d45\`;
- canonical-LF CSV SHA-256
  \`b1b65708cd103058c3bcaea50bf65550d5671a88e97000b94f2536fbc60a59ff\`;
- canonical metadata and validation SHA-256 values
  \`ad8231ec92c71faf12631534871e192bc3000601514c2a369fc84d963bfa9887\`
  and
  \`6d199ac9fd4d7fdace93292d1dded1c98d9f49c2836244ee9d2e3ddd334e8333\`.

The fixed-speed Xe-131 result is a Coulomb-sector ratio only, not a halo
fold or a substitute for the seven-isotope/eight-response gate. The q=0
nucleon-form-factor M-only result is now a secondary normalization
reference; the primary AFH correction uses the finite-\(t_N\) M-only
kernel with the same \(F_1,F_2\) prescription:

| \(E_R\) | \(q_A\) (GeV) | Form factor | \(R_{\rm charge}/R_{t_N,M}\) | \(R_{\rm charge}/R_{q=0,M}\) |
|---:|---:|---|---:|---:|
| 200 keV | 0.220825560 | bishara_linear | 0.99695540 | 0.737630 |
| 200 keV | 0.220825560 | isoscalar_zexp | 0.99655805 | 0.778309 |
| 267 keV | 0.255146745 | bishara_linear | 0.91463689 | 0.605649 |
| 267 keV | 0.255146745 | isoscalar_zexp | 0.89961039 | 0.649216 |

The common integrated \(L_C^{(3)}\) cancels in these normalized ratios.
The dual-form-factor fixed-speed workflow passed (run 44443361283,
artifact 14491448839; 7/7 regression tests).



At 267 keV, PCHIP-versus-linear interpolation changes the ratio by
\(7.47\times10^{-4}\), so the deep-\(W_M\)-minimum interpolation sensitivity
is retained. The common integrated \(L_C^{(3)}\) cancels in this ratio.

## 6. Latest independent workflow validations

- PR #58 full-current run 44262472963: both jobs succeeded. The full-current
  job passed 69 regression tests plus 11 native Coulomb-engine tests. It
  generated 12 integrated tensor rows; the independent Dirac-trace residual
  is \(1.59813\times10^{-9}\), minimum Gram eigenvalue
  \(-3.19523\times10^{-14}\), and maximum q-frame rotation residual
  \(3.15227\times10^{-16}\).
- AFH coefficient extraction: 12 benchmarks; maximum
  \(C_{\Sigma'\Delta}\) Cauchy-identity residual
  \(1.72121\times10^{-16}\); maximum continuity correction
  \(5.12783\times10^{-6}\).
- Provisional seven-isotope contraction: 84 rows, all total kernels positive;
  maximum spatial/Coulomb ratio \(7.09596\times10^{-9}\). This is explicitly
  \`PROVISIONAL_AFH_CONTRACTION_PASS\`, not native validation.
- Component-wise phase-space convergence: run 44262472963 passed all nine
  stress scans, comparing all 256 complex Gram entries, all 16 complex
  Lorentz-tensor entries, and point-nucleus contractions. The worst final
  Frobenius difference is \(1.50126\times10^{-8}\), active-component
  difference \(1.56728\times10^{-5}\), and point-nucleus contraction
  difference \(1.51171\times10^{-8}\).
- Xe-131 fixed-speed native Coulomb-sector run 44262472992 passed, artifact
  14408816831.

The full seven-isotope native run 44222502400 remains QUEUED. No native
seven-isotope PASS, full vector-current halo fold, natural-xenon spectrum,
or detector-level prediction is claimed.


## 2026-11-18 update: optional leading-static candidate fold

In addition to the default Coulomb-sector engine, the repository now has an
opt-in leading-static vector-current candidate mode. It reads all eight native
AFH response columns and combines M, Phi'', M-Phi'', Delta, Sigma', and the
signed Sigma'-Delta interference. The two interference-response
Cauchy-Schwarz inequalities are checked independently from the
particle-side Sigma'-Delta coefficient identity.

This is a gated candidate only. Its unit tests use a synthetic
provenance-shaped fixture to test the loader and computation path; this is
not a native AFH calculation. The native 16,807-point runner remains queued,
and P3 has not passed. No real native seven-isotope candidate halo result is
claimed. See NATIVE_LEADING_STATIC_VECTOR_CURRENT_HALO_CANDIDATE.md.


## 2026-11-18 update: C0-consistent P3-C response contraction

The latest P3-C fixed-speed response contraction is recorded in
[P3_C_C0_CONSISTENT_CONTRACTION.md](P3_C_C0_CONSISTENT_CONTRACTION.md).
Workflow 44305980766 passed 100 full-current tests and 16 native
charge-engine tests, generated the seven-isotope spatial archive, and
contracted 12 particle-side benchmark/width sets with seven isotopes
(84 rows). All total kernels are positive and the maximum spatial/charge
ratio is \(7.0959581690\times10^{-9}\). The corrected normalization applies
the P3-B common \(C_0(A)\) to the AFH-8 charge responses; P3-B spatial
responses already contain \(C_0(A)\). The equal-\(p=n\) factor four is
applied once.

This remains a provisional Python response-level result. It does not
promote native_afh_validated, and it does not close the P3-B direct
many-body covariant/q-frame/AFH amplitude comparison.

The earlier private run 44222502400 attempt 2 was cancelled without an
artifact. The current native P3-B workflow is
[44346207069](https://github.com/lm846802297-bit/research-compute-control/actions/runs/44346207069),
opened from control-repository PR #2 and pinned to the reviewed source
commit 5afc500a3102b857dd16e29432db8e6e068d65d1. Its job is QUEUED with
no assigned self-hosted runner. Until it uploads a native comparison
artifact with all 16,807 total-response rows and all 9,604 rank-resolved
multipole rows passing, the seven-isotope native gate remains OPEN.


## 2026-11-19 update: current PR #65 and native P3-B queue

The formal three-body pipeline has been refreshed to the asymmetric Pole
prescription: the first \(p-k\) propagator is zero-width and the second
\(p'+k\) propagator carries the constant \(\Gamma_{\chi_2}(m_{\chi_2})\).
The latest full-current workflow is
[44432440600](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44432440600)
(artifact 14486904025), and its seven-isotope response-level contraction
contains 28 rows (four benchmarks × seven isotopes), all positive. Its
maximum spatial/charge ratio is \(7.0304970964\times10^{-9}\). This does
not close P3-C because the output is still a response-level contraction,
not a direct covariant-vs-AFH nuclear-amplitude comparison.

The current P3-B native comparison is prepared in
[research-compute-control PR #2](https://github.com/lm846802297-bit/research-compute-control/pull/2).
Its run
[44346207069](https://github.com/lm846802297-bit/research-compute-control/actions/runs/44346207069)
is pinned to:
- native AFH exporter/source commit
  `5afc500a3102b857dd16e29432db8e6e068d65d1`;
- LZ P3-B spatial response artifact from run `44337928314`,
  artifact `14443055701`;
- AFH source SHA-256
  `dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372`.

The native job is queued and has no assigned self-hosted runner at the
latest check. P3-B therefore remains OPEN. Its acceptance target is the
full 16,807-row seven-isotope/eight-response comparison plus 9,604
rank-resolved Xe-129/Xe-131 multipole rows, with the comparator's pinned
normalization, phase, and imaginary-residual tolerances. The 121-point
Xe-131 dense charge export is also required to resolve the diffraction
minimum before finalizing the fixed-speed recoil interpolation.

The current interpolation audit is more informative than the old
PCHIP-versus-linear warning: degree-8 and degree-10 local Chebyshev
interpolants agree to numerical precision, but PCHIP differs from Cheb10
by up to 1.6847% in \(W_M\) near
\(q_A=0.25633847\) GeV. The normalized full/q=0-reference ratio changes by
at most 0.1182% in the selected scan. This is a local interpolation
stability result, not a native AFH validation; the dense native Xe-131
export remains the deciding comparison.

P4 is not yet a production result. The existing
`native_charge_sector_halo_fold.py` already requires a provenance-checked
native seven-isotope/eight-response bundle, defaults to Pole width, and
can report both the Coulomb-sector rate and an explicitly unpromoted
leading-static full-vector candidate. The full-vector result must remain a
candidate until P3-C passes. The seven-isotope set covers 99.8158% of the
natural xenon atom fraction; the omitted Xe-124/Xe-126 abundance must remain
explicit in every rate table.


## 2026-11-19 update: P3-C spatial amplitude-level subgate

The new Xe-131 spatial amplitude-level calculation is recorded in
[P3_C_C0_CONSISTENT_CONTRACTION.md](P3_C_C0_CONSISTENT_CONTRACTION.md)
and its detailed report
[P3C_SPATIAL_AMPLITUDE_LEVEL_HELICITY_RESULTS.md](P3C_SPATIAL_AMPLITUDE_LEVEL_HELICITY_RESULTS.md).
Using the pole-only full-current artifact 14486904025 and spatial response
artifact 14486014588, the Cartesian Eq. (107) contraction and the
helicity-resolved \(\Delta_J+\Sigma'_J\) amplitude reconstruction agree
to a maximum relative residual of \(6.09\times10^{-16}\) over four Xe-131
benchmarks. The maximum Eq. (107)-coefficient residual is
\(8.53\times10^{-16}\).

The selected-point interpolation comparison finds at most
\(5.53\times10^{-6}\) relative difference between PCHIP interpolation of
signed rank amplitudes and the existing linear interpolation of total
responses. This supports interpolating signed multipole amplitudes before
reconstructing responses, but is not a global interpolation acceptance.

This is a **spatial amplitude-level subgate PASS only**. The calculation
still uses provisional Python AFH amplitudes, does not rank-resolve the
charge \(M,\Phi''\) amplitudes, and does not yet compare against an
independently integrated coordinate-space bound-nucleus current. Full
P3-C remains OPEN. The full-current workflow now runs this check and
archives its JSON output; the CI rerun on the new PR branch will provide
the reproducible hosted test result.


The PR #66 CI rerun regenerated the spatial archive with the same response
and multipole CSV SHA-256 values as the PR #65 archive. The private native
workflow remains pinned to artifact 14443055701; its input files are
byte-identical to the PR #66 spatial artifact 14486014588.
