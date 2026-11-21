# Native-AFH finite-size charge-sector and full-current natural-xenon halo fold

**Status:** B is the adopted primary baseline; charge-sector C is a separate extension. Production promotion waits for the native seven-isotope AFH gate and P3-C amplitude-level acceptance.  
**Formal nuclear input:** native AFH v6.0 only.  
**Formal width:** asymmetric Pole width only.  
**Coupling basis:** external \((g_1g_2g_{VN})^2\), with \(\widehat F_i=F_i^{uds}/3\).

## 1. Mandatory finite-size AFH input

The engine consumes the provenance-checked native seven-isotope/eight-response AFH bundle. It does not accept the provisional Python-translated AFH response table as a production input.

For each isotope and recoil energy,
\[
Q_A^2=|\boldsymbol q_A|^2=2m_AE_R+E_R^2,\qquad
y_A=\left(\frac{b_AQ_A}{2}\right)^2.
\]
The nuclear response is evaluated at this finite \(y_A\). The original AFH M-only reference is
\[
\boxed{
R_{A,M}^{\rm phys}(Q_A)
=A^2\frac{W_M^{00}(y_A)}{W_M^{00}(0)},\qquad
R_{A,M}^{\rm phys}(0)=A^2.
}
\]
The physical equal-\(p=n\) native response columns already include the raw-to-physical AFH factor four exactly once. Do not multiply by four again.

AFH \(W_M(y_A)\) already contains the finite nuclear size through the isotope OBDMEs, oscillator wave functions, Bessel functions, and multipole sums. Do not multiply a Helm, Fermi, Gaussian, or other whole-nucleus form factor on top of AFH.

## 2. Exact isotope kinematics and transfer ledger

For every isotope and recoil,
\[
q_A^\mu=(E_R,\boldsymbol q_A),\qquad
t_A=q_A^2=-2m_AE_R,\qquad
Q_A^2=|\boldsymbol q_A|^2=2m_AE_R+E_R^2.
\]
The isotope mass is obtained from the canonical atomic-mass input,
\[
m_A=[M_{\rm atom}(A)-54m_e]u.
\]
No average xenon mass is used in isotope kinematics.

- AFH \(y_A\) and spatial NR coefficients use \(Q_A^2\).
- The vector-mediator propagator uses \(t_A\):
  \[
  (m_V^2-t_A)^2=(m_V^2+2m_AE_R)^2.
  \]
- The formal one-body impulse prescription uses \(q_N^\mu=q_A^\mu\), hence \(t_N=t_A\).
- The static-nucleon diagnostic \(q_N^0=0\) gives \(t_N=-Q_A^2\). It is not the formal P4 production prescription.

The one-body impulse prescription is an explicit bound-nucleon approximation; it does not by itself include binding corrections, exchange currents, or two-body currents.

## 3. Coupling normalization

The original paper and Mathematica rate convention use
\[
g_{VN}=3g_{Vq},\qquad (g_1g_2g_{VN})^2
\]
in the external cross-section prefactor. The full universal quark-current form factors satisfy
\[
F_1^{uds}(0)=3,\qquad F_2^{uds}(0)=-0.552.
\]
Therefore the coefficients multiplying the external \(g_{VN}\) prefactor use
\[
\widehat F_i(t_N)=F_i^{uds}(t_N)/3,\qquad
\widehat F_1(0)=1,\quad \widehat F_2(0)=-0.184.
\]
The AFH factor four and the quark-current factor three are independent normalization operations. The code applies the former in the AFH response conversion and the latter in the definition of \(\widehat F_i\).

The adopted B form-factor prescription is the Bishara et al. Appendix A.1
low-momentum flavor sum:
\[
F_1^{uds,N}(t_N)=3+8.392t_N+\mathcal O(t_N^2),\qquad
F_2^{uds,N}(t_N)=-0.552+\mathcal O(t_N).
\]
Only the first-order Dirac slope and leading Pauli constant are used; no
unverified \(F_2'\) is introduced. In the external-\(g_{VN}\) basis this is
\[
\widehat F_1(t_N)=1+\frac{8.392}{3}t_N+\mathcal O(t_N^2),\qquad
\widehat F_2(t_N)=-0.184+\mathcal O(t_N).
\]
The alternative isoscalar_zexp option is sensitivity-only, not the B default.

## 4. Coulomb-sector contraction

For a conserved one-body nuclear vector current,
\[
q_A^\mu=(E_R,0,0,Q_A),\qquad
J_A^3=\frac{E_R}{Q_A}J_A^0.
\]
The continuity-reduced DM weight is
\[
\boxed{
L_C^{(3)}
=L_{00}^{(3)}
-\frac{E_R}{Q_A}(L_{03}^{(3)}+L_{30}^{(3)})
+\left(\frac{E_R}{Q_A}\right)^2L_{33}^{(3)}.
}
\]
This is a condition on the complete nuclear one-body vector current. It is not a Ward identity imposed on the inelastic DM transition current.

The charge coefficients use the effective-nucleon form factors:
\[
\widehat c_M=
\widehat F_1(t_N)
+\frac{t_N[\widehat F_1(t_N)+2\widehat F_2(t_N)]}{8m_N^2},
\]
\[
\widehat c_{\Phi''}
=\frac{Q_A^2[\widehat F_1(t_N)+2\widehat F_2(t_N)]}{4m_N^2}.
\]
The invariant \(t_N\) and spatial \(Q_A^2\) are intentionally different.

## 5. A/B/C response hierarchy

**B is the adopted production baseline.** The engine records three nested
charge-sector kernels, all retaining the same finite-\(Q_A\) AFH response.
B includes only the finite-\(t_N\) effective nucleon current and AFH
\(W_M\); no additional AFH response is present in B.

**A — original finite-size AFH M-only reference**
\[
\mathcal K_A=L_C^{(3)}W_M^{\rm phys}(Q_A).
\]
The effective nucleon current is frozen at \(\widehat F_1(0)=1\).

**B — finite-\(t_N\) nucleon M-only**
\[
\mathcal K_B=L_C^{(3)}\widehat c_M(t_N)^2W_M^{\rm phys}(Q_A).
\]

**C — M+\(\Phi''\) charge response**
\[
\mathcal K_C=L_C^{(3)}\left[
\widehat c_M^2W_M^{\rm phys}
+2\widehat c_M\widehat c_{\Phi''}W_{M\Phi''}^{\rm phys}
+\widehat c_{\Phi''}^2W_{\Phi''}^{\rm phys}
\right].
\]

The output reports:
\[
B/A-1:\ \text{single-nucleon finite-}t_N\text{ correction},
\]
\[
C/B-1:\ \text{additional AFH charge-response correction at fixed }\widehat F_i,
\]
\[
C/A-1:\ \text{total change relative to the original finite-size AFH baseline}.
\]
The \(C/B\) ratio is not the total change. The \(C/A\) ratio is not a pure multipole correction.

## 6. Optional leading one-body spatial-current candidate

The optional spatial mode adds only the terms produced by the current-matching implementation:
\[
\mathcal K_{\rm full}
=\mathcal K_C
+C_\Delta W_\Delta^{\rm phys}
+C_{\Sigma'}W_{\Sigma'}^{\rm phys}
+C_{\Sigma'\Delta}W_{\Sigma'\Delta}^{\rm phys}
+\cdots .
\]
The \(\Sigma'-\Delta\) interference is signed and must not be replaced by its absolute value. This candidate remains provisional until native Wolfram spatial-response comparison and the P3-C covariant-to-AFH amplitude-level gate pass.

In code and metadata, “leading-static” means the leading nonrelativistic one-body nuclear-current expansion. It does **not** mean the static-nucleon transfer \(q_N^0=0\).

## 7. Native AFH input gate

The engine validates:
- seven isotopes: Xe-128, Xe-129, Xe-130, Xe-131, Xe-132, Xe-134, Xe-136;
- 2,401 native \(q\) nodes per isotope;
- all eight AFH response channels;
- native source commit, package identity, metadata, and SHA-256 checksums;
- physical equal-\(p=n\) normalization and factor-four bookkeeping;
- absolute-response interpolation before any response ratios are formed.

The native comparison must report PASS, **native_afh_validated=true**, and the expected 16,807 total-response rows. The separate dense Xe-131 diffraction-minimum export is used to validate interpolation around the \(W_M\) minimum. Do not smooth or fit away the minimum to force agreement.

## 8. Halo fold

For each isotope the engine evaluates its own
\[
v_{\min,A}(E_R),\qquad m_A,\qquad q_A(E_R),
\]
then performs the velocity integral and abundance weighting. The natural-xenon target normalization uses the complete natural abundance convention, while the AFH response sum retains only isotopes with validated native response inputs; missing isotopes are not silently renormalized into the AFH set.

The output records the truncated Standard Halo Model and the untruncated shifted Maxwell-Boltzmann diagnostic separately. The canonical halo convention is the production result; the untruncated case is a sensitivity/control comparison.

The engine stores the finite-size AFH reference, finite-\(t_N\) M-only layer, charge-response layer, and optional spatial candidate separately. Each row records \(Q_A^2,t_A,t_N\), the coupling basis, AFH normalization, form-factor prescription, width scheme, and interpolation provenance.

## 9. Promotion boundary

The charge-sector halo fold can be reported as a separately labelled result after the native P3-B AFH gate passes. The full-vector halo spectrum must not be promoted until P3-C amplitude-level validation passes. Detector efficiency, energy resolution, exposure, event counts, and likelihood analysis are later detector-level stages.

The engine status remains:
\[
\boxed{\text{charge-sector engine implemented; native AFH/P3-C promotion gates open}.}
\]