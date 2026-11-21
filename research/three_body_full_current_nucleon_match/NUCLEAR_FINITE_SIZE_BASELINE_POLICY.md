# Nuclear finite-size baseline and current-normalization policy

**Status:** mandatory production convention; B is the adopted primary baseline  
**Effective date:** 2026-11-19  
**Scope:** all three-body VV Xe-131 and natural-xenon calculations, AFH response contractions, absolute cross sections, halo folds, plots, result tables, and research documentation.

This document is the single source of truth for the distinction between the finite-size nuclear response, additional AFH multipoles, and single-nucleon Dirac--Pauli form factors. It supplements (and does not replace) the AFH default-density nuclear-structure policy.

## 1. Mandatory baseline

The reference calculation **must retain the finite-size AFH mass/charge response at the physical nuclear recoil momentum**. It is not a point-nucleus calculation.

For an isotope with nuclear mass \(m_A\), recoil energy \(E_R\), and initial target at rest, define
\[
Q_A^2\equiv |\mathbf q_A|^2=2m_AE_R+E_R^2,\qquad
y_A=\left(\frac{b_AQ_A}{2}\right)^2.
\]
The AFH response is evaluated at this finite \(y_A\), not at \(y_A=0\).

The original Mathematica implementation uses the equivalent normalized form
\[
\boxed{
R_{A,M}^{\rm phys}(Q_A)
=A^2\,\frac{W_M^{00}(y_A)}{W_M^{00}(0)},
\qquad R_{A,M}^{\rm phys}(0)=A^2 .
}
\]
The current native AFH archive stores the physical equal-proton/neutron response directly. Its zero-momentum normalization must likewise be \(A^2\).

The adopted production baseline is **B**, which includes the finite-\(t_N\)
single-nucleon Dirac–Pauli current and the finite-size AFH \(M\) response,
but no additional AFH response:
\[
\boxed{
\frac{d\sigma_B}{dE_R}
=\mathcal P_3(E_R,v)\,
(g_1g_2g_{VN})^2\,
L_C^{(3)}(E_R,v)\,
\widehat c_M(t_N)^2\,
R_{A,M}^{\rm phys}(Q_A).
}
\]
Here \(\mathcal P_3\) contains the remaining common phase-space, flux,
mediator, and target-mass factors. The historical A reference freezes the
effective nucleon current at zero transfer, \(\widehat c_M(0)=1\), while
retaining the same \(R_{A,M}^{\rm phys}(Q_A)\). For the original
fixed-speed Mathematica Eq. (6) path, \(L_C^{(3)}\) is replaced by the
corresponding \(I_6\) normalization; the nuclear-response convention is
unchanged. B is the denominator for subsequent C/D response corrections.

**No production baseline may replace \(W_M(y_A)\) by \(W_M(0)\), by a constant \(A^2\), or by a point-nucleus response.** The zero-recoil value \(A^2\) is a normalization check, not the finite-recoil response.

## 2. AFH factor-four ledger: independent of the quark-to-nucleon factor three

The AFH v6.0 package isoscalar response obeys
\[
R_{A,M}^{\rm raw}(Q_A)
=\frac{4\pi}{2J_A+1}W_{M,\rm AFH}^{00}(y_A),
\qquad R_{A,M}^{\rm raw}(0)=A^2/4.
\]
For equal physical proton and neutron couplings,
\[
\boxed{
R_{A,M}^{\rm phys}(Q_A)=4R_{A,M}^{\rm raw}(Q_A),
\qquad R_{A,M}^{\rm phys}(0)=A^2 .
}
\]
Apply this factor four exactly once when converting raw AFH package responses to physical equal-\(p=n\) responses. The native physical equal-\(p=n\) columns already include it; do not multiply them by four again.

This factor four is an AFH isospin-normalization conversion. It is unrelated to \(F_1^{uds}(0)=3\) and \(g_{VN}=3g_{Vq}\). Never combine the two bookkeeping operations into one unexplained normalization factor.

The same raw-to-physical factor-four conversion applies once to each AFH diagonal and mixed response used in the same physical equal-\(p=n\) contraction.

## 3. Coupling basis and the factor-three audit

For the universal \(u+d+s\) quark vector current,
\[
F_1^{uds,N}(0)=3,\qquad F_2^{uds,N}(0)=-0.552,
\qquad g_{VN}=3g_{Vq}.
\]

The paper and original Mathematica benchmark place \((g_1g_2g_{VN})^2\) in the external cross-section prefactor. **That is the mandatory production coupling basis.** When this prefactor is used, define effective-nucleon-normalized form factors
\[
\widehat F_i^N(t_N)=\frac{F_i^{uds,N}(t_N)}{3},
\qquad
\widehat F_1^N(0)=1,\quad
\widehat F_2^N(0)=-0.184.
\]
All Dirac--Pauli coefficients multiplying the \(g_{VN}\)-normalized prefactor must use \(\widehat F_1,\widehat F_2\), not the unnormalized full quark-current \(F_1,F_2\).

An equivalent quark-coupling implementation may use the full \(F_i^{uds,N}\), but then its external coupling must be \(g_{Vq}=g_{VN}/3\). The two implementations must agree:
\[
(g_{Vq})^2(F_i^{uds})^2
=(g_{VN})^2(\widehat F_i)^2.
\]

**Forbidden combination:** an external \((g_1g_2g_{VN})^2\) prefactor together with unnormalized \(F_1^{uds}(0)=3\) coefficients. That combination multiplies the absolute rate by an erroneous factor nine. Ratios in which the same factor appears in numerator and denominator can hide this error; passing ratio tests does not validate the absolute normalization.

The adopted B form-factor truncation uses the flavor-separated low-momentum
inputs from Bishara et al., Appendix A.1:
\[
F_1^{uds,N}(t_N)=3+8.392t_N+\mathcal O(t_N^2),\qquad
F_2^{uds,N}(t_N)=-0.552+\mathcal O(t_N).
\]
The Dirac slope is included at first order. The Pauli input is kept at
leading order because a validated \(F_2'\) is not specified by this input;
no Pauli slope is invented. Thus
\[
\widehat F_1(t_N)=1+\frac{8.392}{3}t_N+\mathcal O(t_N^2),\qquad
\widehat F_2(t_N)=-0.184+\mathcal O(t_N).
\]
This is the default B prescription. The isoscalar electromagnetic
\(z\)-expansion is an alternate sensitivity model only.

The AFH factor four and the quark-current factor three are independent. The
recommended implementation keeps the AFH factor four inside the physical
AFH response and the quark-current factor three inside the relation
\(g_{VN}=3g_{Vq}\), with \(\widehat F_i=F_i/3\) when \(g_{VN}\) is external.

## 4. Add other nuclear responses only on top of the finite-size baseline

At fixed three-body kinematics, isotope, AFH normalization, and B
nucleon-current prescription, the primary baseline is M-only:
\[
\boxed{\mathcal K_B=
L_C^{(3)}\widehat c_M(t_N)^2R_M^{\rm phys}(Q_A).}
\]
The separate C charge-sector extension is
\[
\mathcal K_C
=L_C^{(3)}\left[
\widehat c_M^2 R_M^{\rm phys}(Q_A)
+\widehat c_{\Phi''}^2 R_{\Phi''}^{\rm phys}(Q_A)
+2\widehat c_M\widehat c_{\Phi''}
R_{M\Phi''}^{\rm phys}(Q_A)
\right].
\]
C must never be silently substituted for B.
The leading one-body spatial extension adds the matched terms
\[
\mathcal K_{\rm sp}
=C_\Delta R_\Delta^{\rm phys}
+C_{\Sigma'}R_{\Sigma'}^{\rm phys}
+C_{\Sigma'\Delta}R_{\Sigma'\Delta}^{\rm phys}
+\cdots .
\]
Only channels actually generated by the complete three-body current matching are included. Every response is evaluated at the same physical \(Q_A\), for the same isotope and AFH input. Signed interference responses must retain their signs.

Report three distinct comparisons:
1. **B/A: single-nucleon finite-\(t_N\) correction**
   \[
   \delta_{B/A}=
   \frac{\mathcal K_{B}(\widehat F_1(t_N),\widehat F_2(t_N))}
        {\mathcal K_{A}(\widehat F_1(0),\widehat F_2(0))}-1.
   \]
2. **C/B: additional nuclear-response correction at fixed B current**
   \[
   \delta_{C/B}=
   \frac{\mathcal K_C(\widehat F_1(t_N),\widehat F_2(t_N))}
        {\mathcal K_B(\widehat F_1(t_N),\widehat F_2(t_N))}-1.
   \]
3. **C/A: total change relative to the historical finite-size AFH reference**
   \[
   \delta_{C/A}=
   \frac{\mathcal K_C(\widehat F_1(t_N),\widehat F_2(t_N))}
        {\mathcal K_A(\widehat F_1(0),\widehat F_2(0))}-1.
   \]

The first ratio B/A isolates the single-nucleon finite-\(t_N\) correction. The second ratio C/B isolates the extra AFH multipoles at fixed nucleon current. The third ratio C/A is the combined effect. Do not call C/B the total correction, and do not call C/A a pure AFH-multipole correction.

## 5. Momentum-transfer conventions

Use separate symbols and fields:
\[
q_A^\mu=(E_R,\mathbf q_A),\quad
Q_A^2=|\mathbf q_A|^2=2m_AE_R+E_R^2,\quad
t_A=q_A^2=-2m_AE_R.
\]
- AFH nuclear responses and \(y_A\) use the spatial \(Q_A^2\).
- The mediator propagator uses \(t_A\), so \(m_V^2-t_A=m_V^2+2m_AE_R\).
- In the strict free one-body impulse prescription \(q_N^\mu=q_A^\mu\), \(t_N=t_A\).
- The static-nucleon diagnostic \(q_N^0=0\) gives \(t_N=-Q_A^2\). It is a separate approximation and must be labelled as such. It is not the formal \(q_N^\mu=q_A^\mu\) result.
- The AFH nuclear response is not evaluated at \(t_N\); the nucleon form factors are not evaluated at the AFH oscillator variable \(y_A\).

The one-body impulse prescription is a declared approximation for the bound-nucleon current. It does not by itself include nuclear binding corrections, exchange currents, or two-body currents.

## 6. No duplicate nuclear shape factor

AFH \(W_M(y_A)\) already contains the finite nuclear size through the isotope OBDMEs, oscillator wave functions, Bessel functions, and multipole sums. Do not multiply an additional Helm, Fermi, Gaussian, or other whole-nucleus form factor onto an AFH response. Doing so double counts nuclear size.

Single-nucleon \(F_1^N(t_N)\) and \(F_2^N(t_N)\) are a distinct physical layer. They may be matched into the one-body current coefficients, but they do not replace or multiply away the AFH nuclear response.

## 7. Canonical code/output vocabulary

New production code and result files must use explicit names:
- **baseline_A_original_AFH_M** — historical q=0 effective nucleon-current reference, retaining finite-size \(W_M(y_A)\);
- **baseline_B_finite_tN_M** — adopted primary B baseline, \(\widehat c_M(t_N)^2L_CW_M(y_A)\);
- **extension_C_MplusPhiPP** — separate C charge-response extension, B plus \(\Phi''\) and signed \(M-\Phi''\);
- **candidate_D_full_one_body_current** — matched charge plus spatial one-body candidate, provisional until P3-C and native gates pass.

Do not use the labels **pointlike_M**, **pointlike 9 W_M**, or **point-nucleus baseline** for the finite-size AFH reference. Old archived keys with those names are legacy aliases only; they must not be propagated into new result tables, plots, or manuscript text.

Every result metadata file must record:
- **primary_baseline** = B, finite-\(t_N\) nucleon current times finite-size AFH \(W_M(y_A)\), M response only;
- **A_reference** = q=0 effective nucleon current times the same finite-size AFH \(W_M(y_A)\);
- **C_extension** = B plus the separately reported additional charge responses;
- **nuclear_response_baseline** = AFH finite-size \(W_M(y_A)\);
- **AFH_response_normalization** = physical equal-\(p=n\); factor four applied once;
- **coupling_basis** = \(g_{VN}\) effective nucleon coupling;
- **quark_to_nucleon_relation** = \(g_{VN}=3g_{Vq}\);
- **nucleon_form_factor_normalization** = \(\widehat F_i=F_i^{(u+d+s)}/3\), when finite nucleon form factors are used;
- **form_factor_prescription** = Bishara first-order Dirac slope plus leading constant Pauli term for B; isoscalar_zexp is alternate sensitivity only;
- **nuclear_momentum_argument** = \(Q_A^2=2m_AE_R+E_R^2\);
- **mediator_invariant** = \(t_A=-2m_AE_R\);
- **nucleon_transfer_scheme** = \(t_N=t_A\) (strict one-body impulse), or the explicitly selected static diagnostic.

## 8. Acceptance tests

A production calculation is not accepted unless all applicable checks pass:
1. Native AFH finite-\(Q_A\) response is used at every recoil point; the original notebook shape \(A^2W_M(y_A)/W_M(0)\) is recovered.
2. \(R_{A,M}^{\rm phys}(0)=A^2\) for every isotope.
3. Raw-to-physical AFH factor four is applied exactly once to every response channel.
4. No extra whole-nucleus Helm/other shape factor is applied on top of AFH.
5. The primary B rate uses the Bishara low-momentum \(\widehat F_1(t_N),\widehat F_2(t_N)\) prescription and AFH \(W_M(y_A)\) only; the A reference uses \(\widehat F_1(0)=1\).
6. The quark-coupling and effective-nucleon-coupling implementations agree pointwise.
7. Additional response ratios are formed against an \(M\)-only denominator with the same \(W_M(Q_A)\) and same nucleon-current prescription.
8. \(Q_A^2\), \(t_A\), and \(t_N\) are independently stored and tested.
9. The mediator denominator is \((m_V^2-t_A)^2=(m_V^2+2m_AE_R)^2\), not \((m_V^2+Q_A^2)^2\).
10. New outputs contain no ambiguous **pointlike_M** production field.

## 9. Historical outputs

Previously archived outputs whose baseline field was named **pointlike_M** or **pointlike 9 W_M** are not silently rewritten. Their underlying numerical meaning must first be checked: in several current scripts the field contains \(9L_CW_M(Q_A)\), so the AFH nuclear finite-size response is present even though the name is misleading. If the external prefactor is \((g_1g_2g_{VN})^2\), the additional factor nine is also a coupling-normalization error and the absolute result must be regenerated. Ratio-only results may remain numerically valid if the same factor cancels, but must be relabelled and revalidated.

Historical result files must be marked **SUPERSEDED_NORMALIZATION** when this audit changes their absolute normalization. New outputs must be generated from the corrected code and must carry fresh provenance hashes.