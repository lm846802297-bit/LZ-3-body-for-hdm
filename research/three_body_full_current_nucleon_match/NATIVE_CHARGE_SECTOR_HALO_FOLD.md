# Native-AFH \(M+\Phi''\) Coulomb-sector natural-xenon halo fold

## Status

**Engine implemented; production result pending the native seven-isotope AFH gate.**

This stage is deliberately downstream of the PR #58 full-current validation and
upstream of any detector-level prediction. It computes only

\[
M+\Phi''+M\Phi''
\]

with the exact three-body phase-space tensor and isotope-specific nuclear
kinematics.

The spatial \(\Delta,\Sigma',\Sigma''\) sector is not silently set to zero in
the theory record; it is excluded from this engine because its independent
fixed-speed PR #58 contraction already gives

\[
|R_{\rm spatial}/R_{\rm charge}|<7.1\times10^{-9}
\]

over the tested 84 rows. A separate native spatial-response promotion remains
the appropriate acceptance gate.

## 1. Native AFH input gate

The engine refuses to consume the provisional Python AFH eight-response table.
The native input directory must contain:

- seven native AFH CSV files, Xe-128/129/130/131/132/134/136;
- \`native-comparison.json\`;
- \`native-comparison.json\` must report
  \`status=PASS\`,
  \`native_afh_validated=true\`, and
  \`rows_compared=16807\`;
- every native CSV must contain 2,401 q nodes from 0 to 0.6 GeV;
- native imaginary residuals must be below \(2\times10^{-12}\).

This is intentional: a local response ratio near a \(W_M\) minimum is too
sensitive to interpolation and denominator cancellation to promote the
provisional seven-isotope Python table to the final spectrum.

## 2. Exact isotope kinematics

For every isotope and every requested recoil,

\[
q_A(E_R)=\sqrt{2m_AE_R+E_R^2}.
\]

The nuclear mass is obtained from the repository's canonical NIST input,

\[
m_A=[M_{\rm atom}(A)-54m_e]u.
\]

No average xenon mass is used in the isotope kinematics, and no selected
0.25-MeV AFH grid point is substituted for the exact recoil momentum.

The AFH response is evaluated at that exact \(q_A\). The engine uses PCHIP
interpolation of the **absolute** native response functions and retains a
linear-interpolation result as a numerical diagnostic. Ratios such as
\(W_{\Phi''}/W_M\) are formed only after the three absolute responses have
been interpolated.

## 3. Charge-sector contraction

The phase-space calculation supplies the full q-aligned tensor. For a
conserved one-body nuclear vector current, use

\[
q_A^\mu=(E_R,0,0,Q_A),\qquad
J_A^3=\frac{E_R}{Q_A}J_A^0.
\]

The effective Coulomb weight is therefore

\[
\boxed{
L_C^{(3)}
=L_{00}^{(3)}
-\frac{E_R}{Q_A}(L_{03}^{(3)}+L_{30}^{(3)})
+\left(\frac{E_R}{Q_A}\right)^2L_{33}^{(3)}.
}
\]

This is nuclear-current continuity, not a Ward identity imposed on the
inelastic DM transition current. The point-nucleus contraction independently
checks that \((2m_A+E_R)^2L_C\) equals the direct charge plus longitudinal
plus interference contraction.

For the static Dirac-Pauli charge matching,

\[
c_M =
F_1^V+
\frac{t_N(F_1^V+2F_2^V)}{8m_N^2},
\]

\[
c_{\Phi''}
=
\frac{Q_A^2(F_1^V+2F_2^V)}{4m_N^2},
\qquad
t_N=-Q_A^2.
\]

Therefore

\[
C_M=c_M^2L_C^{(3)},
\]

\[
C_{\Phi''}=c_{\Phi''}^2L_C^{(3)},
\]

\[
C_{M\Phi''}=2c_Mc_{\Phi''}L_C^{(3)}.
\]

The nuclear charge-sector kernel is

\[
\boxed{
{\cal K}_{\rm charge}
=
C_MR_M
+C_{\Phi''}R_{\Phi''}
+C_{M\Phi''}R_{M\Phi''}.
}
\]

The physical equal-\(p=n\) AFH response convention is used, with the factor
of four applied once in the response conversion.

## 4. Four controlled spectra

The engine records three nested Coulomb-sector quantities:

\[
R_0=W_M[F_1^V(0)]^2,
\]

\[
R_1=W_M[c_M(t_N)]^2,
\]

\[
R_2=
W_Mc_M^2+
W_{\Phi''}c_{\Phi''}^2+
2W_{M\Phi''}c_Mc_{\Phi''}.
\]

The halo-fold output reports

\[
R_1/R_0-1
\]

as the finite-\(t_N\) coherent-charge effect and

\[
R_2/R_1-1
\]

as the \(\Phi''\) correction.

The final charge-sector comparison is

\[
R_2/R_0-1.
\]

The spatial sector is kept as a separate fourth layer and is not folded into
this file until its native response inputs are independently promoted.

## 5. Form-factor prescriptions

The CLI requires an explicit prescription. Available options are:

- \`pointlike\`: \(F_1=3,\ F_2=-0.552\);
- \`bishara_linear\`: linear \(F_1\) slope diagnostic with constant \(F_2\);
- \`isoscalar_zexp\`: the current central finite-\(Q^2\) diagnostic already
  implemented in \`nucleon_vector_form_factors.py\`.

The latter two remain diagnostics until a model-specific universal
\(u+d+s\) \(F_2^V(Q^2)\) prescription is locked.

## 6. Halo fold

For each isotope the code evaluates its own

\[
v_{\min,A}(E_R),\qquad m_A,\qquad q_A(E_R),
\]

then performs the velocity integral. The natural-xenon target normalization
uses the complete nine-isotope average atomic mass, while the AFH response
sum retains the seven available isotope abundances without renormalizing
them.

The output contains both:

- truncated Standard Halo Model;
- untruncated shifted Maxwell-Boltzmann diagnostic.

The production spectrum should use the project's canonical halo convention;
the untruncated result is retained only as a sensitivity/control comparison.

## 7. Current limitation

The native AFH runner currently has to complete before a production
seven-isotope result can be promoted. Until then, the correct status is:

\[
\boxed{\text{engine ready; native AFH input gate open}}
\]

The present engine includes the charge/longitudinal sector through \(L_C\)
but still omits the transverse \(\Delta\), \(\Sigma'\), and mixed
\(\Sigma'\)-\(\Delta\) nuclear-current multipoles. It is not the full
vector-current rate. No natural-xenon percentage is inferred from the
Xe-131 local \(200\) or \(267\) keV diagnostics.


## Important scope clarification (2026-11-18)

The engine now uses the continuity-reduced Coulomb weight L_C, which
includes L00, L03, L30, and L33 under the conserved one-body nuclear
vector-current relation. It therefore does not use L00 alone.

The transverse nuclear-current multipoles, including Delta, Sigma', and
their interference, remain outside this engine. The fixed-speed spatial
sector bound quoted above applies only to its tested 84 rows; it is not a
global bound over the halo integral.

The code output explicitly sets full_current_complete=false and labels its
status COMPUTED_WITHIN_COULOMB_SECTOR_APPROXIMATION. It remains a restricted
Coulomb-sector diagnostic, not the final natural-xenon spectrum.
