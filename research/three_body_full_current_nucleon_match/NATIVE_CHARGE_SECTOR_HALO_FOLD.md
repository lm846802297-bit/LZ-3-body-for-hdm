# Native-AFH Coulomb-sector and leading-static vector-current natural-xenon halo fold

## Status

**Engine implemented; production result pending the native seven-isotope AFH gate.**

This stage is deliberately downstream of the PR #58 full-current validation and
upstream of any detector-level prediction. It computes only

\[
M+\Phi''+M\Phi''
\]

with the exact three-body phase-space tensor and isotope-specific nuclear
kinematics.

The transverse \(\Delta,\Sigma'\) sector is not silently set to zero in
the theory record; it is excluded from this Coulomb-sector engine pending
the full leading-static multipole promotion. The provisional fixed-speed
PR #58 contraction gives
\[
|R_{\rm spatial}/R_{\rm Coulomb}|<7.1\times10^{-9}
\]
over the tested 84 rows only. This is not a global halo-integrated bound.
The seven-isotope native gate validates all eight response inputs, but does
not by itself validate or fold the transverse three-body coefficients.

## 1. Native AFH input gate

The engine refuses to consume the provisional Python AFH table. Pass the
extracted root of the private native artifact, which contains:

- native/ with seven CSV files, Xe-128/129/130/131/132/134/136;
- native/native_metadata.txt;
- native-comparison.json;
- run_manifest.json;
- SHA256SUMS.txt.

The comparison must report status=PASS, native_afh_validated=true, and
rows_compared=16807. All eight response channels, all 2,401 q nodes per
isotope, the pinned source commit, package identity, run metadata, and SHA-256
checksums are validated before the three Coulomb-sector response values are
read.

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

## 3. Coulomb-sector contraction

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

## 4. Adopted A/B/C hierarchy

The halo fold reports three distinct quantities, all retaining the same finite-size AFH response:

\[
R_A=L_C^{(3)}W_M^{\\rm phys}(y_A),
\]

\[
R_B=\\widehat c_M(t_N)^2L_C^{(3)}W_M^{\\rm phys}(y_A),
\]

\[
R_C=L_C^{(3)}\\left[
\\widehat c_M^2W_M^{\\rm phys}
+2\\widehat c_M\\widehat c_{\\Phi''}W_{M\\Phi''}^{\\rm phys}
+\\widehat c_{\\Phi''}^2W_{\\Phi''}^{\\rm phys}
\\right].
\]

A is the zero-transfer effective-nucleon-current reference, B is the adopted
finite-\\(t_N\\) M-only production baseline, and C is the additional charge
multipole extension. Report B/A (single-nucleon form-factor correction),
C/B (additional AFH charge-response correction at fixed nucleon current),
and C/A (combined change). Do not call A a point-nucleus response: it
contains the same finite-size AFH \\(W_M(y_A)\\) as B and C.

The spatial-current candidate is a separate provisional D extension. It is
not a completed full-current prediction until the P3-C covariant-to-AFH
nuclear-amplitude gate passes.

## 5. Nucleon form-factor prescriptions and kinematics

The CLI requires an explicit prescription:

- \`q0_anchor\`: \\(\\widehat F_1(0)=1,\\widehat F_2(0)=-0.184\\), the A reference;
- \`bishara_linear\`: adopted B low-momentum flavor-resolved Dirac slope
  with the available leading constant Pauli term;
- \`isoscalar_zexp\`: alternate finite-\\(Q_N^2\\) sensitivity model.

The external rate prefactor uses \\((g_1g_2g_{VN})^2\\), with
\\(g_{VN}=3g_{Vq}\\). Therefore the full universal quark-current form
factors must be divided by three before they enter the nucleon-current
coefficients: \\(\\widehat F_i=F_i^{uds}/3\\). The AFH raw-to-physical
factor four is independent and is applied exactly once.

For the formal one-body impulse prescription,
\\[
t_N=t_A=-2m_AE_R,\\qquad Q_N^2=-t_N.
\\]
The AFH response instead uses the spatial transfer
\\[
Q_A^2=2m_AE_R+E_R^2,\\qquad y_A=b_A^2Q_A^2/4.
\\]
The static diagnostic \\(q_N^0=0\\), giving \\(t_N=-Q_A^2\\), is
not the formal production prescription.

The mediator denominator is the Lorentz-invariant
\\[
(m_V^2-t_A)^2=(m_V^2+2m_AE_R)^2,
\\]
not \\( (m_V^2+Q_A^2)^2\\).

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

The engine now has two strictly separated input paths:

1. **Native production path:** requires the provenance-pinned native
   seven-isotope/eight-response Wolfram artifact and its 16,807-row
   pointwise comparison PASS.
2. **Provisional calculation path:** accepts only the pinned source-translated
   AFH-8 charge archive plus the independently rank-reconstructed P3-B
   spatial archive. It checks both artifact hashes, the shared AFH source
   commit, all 16,807 charge/spatial q-grid keys, C0 normalization, and the
   two response Cauchy-Schwarz bounds. Its output is explicitly marked
   `native_afh_validated=false`.

The provisional path exists to finish the end-to-end numerical workflow
before the user's local Mathematica run. It is not a substitute for native
AFH validation and cannot be promoted to a paper-final nuclear prediction.

The formal three-body width is restricted to the asymmetric Pole prescription:
the first \(p-k\) \(\chi_2\) propagator is zero-width and the second
\(p'+k\) propagator carries the constant pole width. The mediator denominator
uses the exact \((m_V^2+q_A^2)^2\), with
\(q_A^2=2m_AE_R+E_R^2\).

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


## 8. Separate Xe-131 native fixed-speed diagnostic

A separate native AFH v6.0 / Wolfram 14.2.0 Xe-131 archive has passed its
three-response integrity and response-level checks. It supports the
fixed-speed Coulomb-sector benchmark in
\`XE131_FIXED_SPEED_CHARGE_DSIGMA_RESULTS.md\`, but does not replace the
seven-isotope/eight-response gate or validate transverse multipoles.


## 2026-11-19 update: provisional AFH input path for pre-Mathematica P4 work

The engine accepts either the native AFH archive or an explicit pair of
provisional Python artifacts. The provisional pair is:
- AFH-8 charge archive: run 44222087512, artifact 14391456283;
- P3-B spatial OBDME archive: run 44432440600, artifact 14486014588.

The loader does not manufacture a native comparison manifest. It requires
both source-translated status flags, verifies the SHA-256 hashes and common
AFH v6.0 source, applies the P3-B common \(C_0(A)\) factor to charge
responses exactly once, and uses the already C0-corrected spatial responses
from P3-B. It also checks the complete seven-isotope 2,401-point q grids
and both \(M\)-\(\Phi''\) and \(\Sigma'\)-\(\Delta\) Cauchy bounds.

A provisional P4 workflow is defined in
`.github/workflows/p4-provisional-seven-isotope-halo-fold.yml`. Its selected
recoil grid is \(E_R=150,200,267,350,400\) keV, with separate speed and
three-body phase-space refinement runs. The first production benchmark uses
\(m_{\chi_1}=1\) TeV, \(m_s=200\) keV,
\(\Delta m=1\) MeV, \(m_V=10\) GeV, and the formal Pole prescription.
It records pointlike \(M\), finite-\(t_N\) \(M\), Coulomb \(M+\Phi''\),
and the leading-static six-channel candidate. Both truncated SHM and
untruncated Maxwellian folds are retained.

Until the local Mathematica comparison is run, every resulting spectrum is
labelled provisional and `native_afh_validated=false`. No GCN/JJ55
response enters this path.

## 2026-11-18 update: optional leading-static vector-current candidate mode

The previous sections describe the default Coulomb-only mode. A second,
explicitly opt-in mode is now implemented in native_charge_sector_halo_fold.py
with the flag --include-leading-static-vector-candidate. It uses the full
integrated q-aligned tensor and interpolates all eight native AFH responses.
Its six candidate nonzero channels are M, Phi'', M-Phi'', Delta, Sigma', and
Sigma'-Delta. Sigma'' and PhiTilde' remain loaded; their coefficients are
zero only at the declared leading-static one-body vector-current order.

This mode is still a candidate, not a promoted full-current result. The
exact AFH spherical-multipole phase validation and P3 direct
covariant-versus-AFH tensor comparison remain open. Both modes require the
provenance-pinned native seven-isotope/eight-response 16,807-point gate.
The current native runner is queued and has not produced an artifact.
See NATIVE_LEADING_STATIC_VECTOR_CURRENT_HALO_CANDIDATE.md for the formula,
acceptance conditions, and execution command.
