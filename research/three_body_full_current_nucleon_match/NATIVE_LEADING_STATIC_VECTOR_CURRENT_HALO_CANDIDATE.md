# Native leading-static vector-current AFH halo-fold candidate

**Status:** code path and synthetic-fixture tests implemented; real seven-isotope
native execution is blocked by the pending native AFH gate; P3 is not passed.

## 1. Purpose and scope

This is the optional second mode of native_charge_sector_halo_fold.py,
enabled by --include-leading-static-vector-candidate. It uses the full
integrated q-aligned three-body Lorentz tensor and all eight AFH native
response channels. The leading-static one-body Dirac--Pauli current has six
candidate nonzero channels:
\[
M,\quad \Phi'',\quad M\Phi'',\quad
\Delta,\quad \Sigma',\quad \Sigma'\Delta.
\]
The native SigmaDoublePrime and PhiTildePrime responses remain loaded and
provenance-checked; their particle-side coefficients are zero only at this
declared current order.

This is not a complete full-current result. The exact AFH spherical
multipole phases, bound-current consistency, and direct covariant-versus-AFH
tensor comparison remain open.

## 2. Particle-side weights

For a conserved one-body nuclear vector current, the charge/longitudinal
weight is
\[
L_C=L_{00}-\frac{E_R}{Q_A}(L_{03}+L_{30})
+\left(\frac{E_R}{Q_A}\right)^2L_{33}.
\]
The transverse-even weight is
\[
L_T=L_{11}+L_{22}.
\]
The dark-matter transition current is not assumed conserved.

Using the current matching convention
\(q_{\rm AFH}=-q_A\), \(q_N=+q_A\), metric \((+---)\), and
\(t_N=-Q_A^2\), the candidate coefficients are
\[
\begin{aligned}
C_M&=c_M^2L_C,&
C_{\Phi''}&=c_{\Phi''}^2L_C,&
C_{M\Phi''}&=2c_Mc_{\Phi''}L_C,\\
C_\Delta&=\frac{(F_1^V)^2Q_A^2}{2m_N^2}L_T,&
C_{\Sigma'}&=\frac{(F_1^V+F_2^V)^2Q_A^2}{8m_N^2}L_T,\\
C_{\Sigma'\Delta}&=-\frac{F_1^V(F_1^V+F_2^V)Q_A^2}{2m_N^2}L_T.
\end{aligned}
\]
The SigmaPrime-Delta sign follows the documented Fourier and current
conventions but remains subject to explicit AFH spherical-multipole
phase validation before promotion.

The candidate kernel is
\[
\begin{aligned}
{\cal K}_{\rm lead}^{(3)}={}&
C_MW_M+C_{\Phi''}W_{\Phi''}+C_{M\Phi''}W_{M\Phi''}\\
&+C_\Delta W_\Delta+C_{\Sigma'}W_{\Sigma'}
+C_{\Sigma'\Delta}W_{\Sigma'\Delta}.
\end{aligned}
\]

## 3. Nuclear response checks

The AFH v6.0 source defines the interference responses through bilinear
FF[DensityMatrix,Operator1,Operator2,...] matrix elements. Accordingly,
the code checks
\[
|W_{M\Phi''}|\leq\sqrt{W_MW_{\Phi''}},\qquad
|W_{\Sigma'\Delta}|\leq\sqrt{W_{\Sigma'}W_\Delta}.
\]
These are nuclear-response Cauchy--Schwarz checks. They are kept distinct
from the particle-side coefficient identity
\[
C_{\Sigma'\Delta}=-2\sqrt{C_\Delta C_{\Sigma'}}
\]
when \(F_1^V(F_1^V+F_2^V)>0\). Neither identity substitutes for P3.

## 4. Native AFH gate

The candidate mode accepts only the extracted root of the native private
runner artifact. It requires:
- comparison status PASS and native_afh_validated=true;
- exactly 16,807 pointwise rows: seven isotopes times 2,401 q nodes;
- all eight response indices and the pinned AFH v6.0 source commit;
- the canonical q grid, run manifest, metadata, and SHA-256 checksums.

A synthetic fixture is used by unit tests to verify that this gate rejects
missing responses, modified hashes, and incorrect source provenance. It is
not a native AFH calculation and cannot satisfy the gate in production.

## 5. Run command after native artifact completion

Extract the complete artifact root, not just its native/ subdirectory.
For the E_R=200 keV benchmark, for example:

~~~powershell
python research/three_body_full_current_nucleon_match/native_charge_sector_halo_fold.py ^
  --native-dir "C:\path\to\extracted\afh-eight-response" ^
  --out "research\three_body_full_current_nucleon_match\results\native_vector_candidate_200keV.json" ^
  --ms-keV 300 --delta-m-keV 450 --ER-keV 200 ^
  --form-factor isoscalar_zexp --width-scheme pole ^
  --include-leading-static-vector-candidate
~~~

Use the matching benchmark-specific Delta m for other recoil points.
The command also produces the Coulomb-only and pointlike-M comparison
baselines, plus isotope-by-isotope and halo-model breakdowns.

## 6. Acceptance and remaining work

The current candidate output deliberately reports
full_current_complete=false and
P3_tensor_validation_complete=false. The native gate validates only
the nuclear response database. Before promotion:
1. derive the exact AFH transverse spherical multipole phases from the
   AFH v6.0 operator implementation;
2. compare direct covariant one-body-current contraction, q-frame-rotated
   contraction, and AFH multipole contraction at selected phase-space points;
3. resolve the bound-nucleon energy transfer and interaction-current
   contribution to nuclear-current continuity;
4. run the candidate fold on the actual 16,807-point native archive;
5. only then consider detector response and event-rate predictions.

The latest private native job 44222502400, attempt 2, is still QUEUED and
has no uploaded artifact. No real native seven-isotope candidate halo result
is claimed.


## 7. AFH v6.0 source-level operator audit (2026-11-18)

The pinned repository source \`v6/dmformfactor-V6.m\` was inspected directly.
The relevant definitions establish the following conventions:

1. \`DeltaJ\` (response index 6) is built from \`Deltaop\`, with
   \`Deltaop = MJLDivQ[..., jcap, jcap]\`.
2. \`SigmaPJ\` (response index 3) is built from \`SigmaPrime\`, where
   \[
   \Sigma'_J=
   -\frac{\sqrt{J}}{\sqrt{2J+1}}\,{\rm MJLSigma}_{J,J+1}
   +\frac{\sqrt{J+1}}{\sqrt{2J+1}}\,{\rm MJLSigma}_{J,J-1}.
   \]
   The corresponding \`DeltaPrime\` definition uses the same displayed
   angular-momentum combination with \`MJLDivQ\).
3. The response dispatcher maps index 8 to the ordered pair
   \`Operator1=SigmaPJ; Operator2=DeltaJ\`. The two-operator \`FF\`
   routine constructs the bilinear from the ordered operator matrix
   elements; the dispatcher then applies the same isospin projection
   combinations used for the other response channels.
4. The response index mapping in the dispatcher is:
   1 \(M\), 2 \(\Sigma''\), 3 \(\Sigma'\), 4 \(\Phi''\),
   5 \(\widetilde\Phi'\), 6 \(\Delta\), 7 \(M\)-\(\Phi''\),
   8 \(\Sigma'\)-\(\Delta\).

This source audit confirms the operator identities and the ordering of the
signed response channel. It does **not**, by itself, establish the sign of
the particle-side coefficient multiplying \(W_{\Sigma'\Delta}\): that sign
requires matching the actual one-body Dirac--Pauli current to the AFH
spherical multipoles, including the Fourier convention and the phases of
the vector spherical harmonics. Therefore the current candidate sign
\[
C_{\Sigma'\Delta}=
-\frac{F_1^V(F_1^V+F_2^V)Q_A^2}{2m_N^2}L_T
\]
remains provisional pending the direct P3 contraction.

The source also defines the \(\Sigma'\)-\(\Delta\) nuclear response as a
bilinear, not as an independently positive diagonal response. Its sign
must be retained. The numerical Cauchy--Schwarz check only tests
\[
|W_{\Sigma'\Delta}|\leq\sqrt{W_{\Sigma'}W_\Delta};
\]
it cannot validate the particle-side relative phase.

The exact source definitions were read from the pinned AFH v6.0 file at
\`v6/dmformfactor-V6.m\`, around lines 903--917 and 981--1016. The full
operator-to-current phase matching remains an explicit P3 task.
