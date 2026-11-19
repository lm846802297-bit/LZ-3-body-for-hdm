# Finite-size AFH baseline and single-nucleon form-factor comparison

**Updated:** 2026-11-19  
**Status:** mandatory finite-size nuclear baseline; effective-\(g_{VN}\) normalization  
**Formal nuclear input:** native AFH v6.0  
**Formal transfer:** \(t_N=t_A=-2m_AE_R\) for the declared one-body impulse prescription  
**Formal width:** asymmetric Pole width only

## 1. Three distinct physical layers

The original calculation is not a point-nucleus calculation. The paper writes the coherent nuclear replacement with a finite nuclear form factor, and the archived Mathematica rate engine evaluates the native AFH response at finite spatial recoil:
\[
Q_A^2=|\boldsymbol q_A|^2=2m_AE_R+E_R^2,\qquad
y_A=\left(\frac{Q_A b_A}{2}\right)^2,
\]
\[
\boxed{
R_{A,M}^{\rm phys}(Q_A)
=A^2\frac{W_M^{00}(y_A)}{W_M^{00}(0)},\qquad
R_{A,M}^{\rm phys}(0)=A^2.
}
\]
The physical equal-\(p=n\) native AFH response already contains the raw-to-physical factor four exactly once. It must be used at finite \(Q_A\) in every reference denominator. Do not multiply an additional Helm, Fermi, Gaussian, or other whole-nucleus shape factor onto AFH \(W_M(y_A)\).

A second, independent layer is the finite-momentum single-nucleon Dirac--Pauli current \(F_1^{q/N}(t_N),F_2^{q/N}(t_N)\). A third layer consists of additional nuclear multipoles such as \(\Phi''\), \(\Delta\), and \(\Sigma'\). These layers must not be conflated.

## 2. Coupling basis: \(g_{VN}\) is external

The original paper and Mathematica benchmark use
\[
g_{VN}=3g_{Vq},\qquad (g_1g_2g_{VN})^2
\]
in the external cross-section prefactor. The full universal \(u+d+s\) quark current has
\[
F_1^{uds,N}(0)=3,\qquad F_2^{uds,N}(0)=-0.552.
\]
For the mandatory \(g_{VN}\) coupling basis, the current coefficients must therefore use
\[
\boxed{
\widehat F_i^N(t_N)=F_i^{uds,N}(t_N)/3,\qquad
\widehat F_1^N(0)=1,\quad \widehat F_2^N(0)=-0.184.
}
\]
Using the external \(g_{VN}\) prefactor together with unnormalized \(F_1^{uds}(0)=3\) would insert a spurious factor nine. The AFH factor four is a separate isospin-normalization conversion and must not be combined with this factor-three ledger.

The equivalent quark-level convention uses \(g_{Vq}=g_{VN}/3\) with the full \(F_i^{uds}\). Both conventions must agree pointwise:
\[
(g_{Vq})^2(F_i^{uds})^2=(g_{VN})^2(\widehat F_i)^2.
\]

## 3. A/B/C hierarchy: preserve the finite-size AFH response throughout

At fixed three-body kinematics and fixed isotope, define:

- **A — mandatory AFH finite-size M-only baseline**
  \[
  A\propto (g_1g_2g_{VN})^2 L_C^{(3)}R_{A,M}^{\rm phys}(Q_A),
  \]
  with the nucleon current frozen at \(\widehat F_1(0)=1\). This is the original finite-size AFH baseline.

- **B — finite-\(t_N\) nucleon M-only result**
  \[
  B\propto (g_1g_2g_{VN})^2 L_C^{(3)}
  \widehat c_M(t_N)^2R_{A,M}^{\rm phys}(Q_A).
  \]
  Only the single-nucleon current changes; the same AFH finite-size response is retained.

- **C — charge-response extension**
  \[
  C\propto (g_1g_2g_{VN})^2 L_C^{(3)}
  \left[
  \widehat c_M^2R_M^{\rm phys}
  +2\widehat c_M\widehat c_{\Phi''}R_{M\Phi''}^{\rm phys}
  +\widehat c_{\Phi''}^2R_{\Phi''}^{\rm phys}
  \right].
  \]
  This adds \(\Phi''\) and the signed \(M-\Phi''\) interference on top of B.

The ratios have distinct meanings:
\[
\boxed{B/A-1=\text{single-nucleon finite-}t_N\text{ correction},}
\]
\[
\boxed{C/B-1=\text{additional AFH charge-response correction at fixed }\widehat F_i,}
\]
\[
\boxed{C/A-1=\text{total change relative to the original finite-size AFH baseline}.}
\]
Do not call \(C/A-1\) a pure AFH multipole correction, and do not call \(C/B-1\) the total change.

The spatial-current candidate adds only those \(\Delta,\Sigma'\), and signed \(\Sigma'-\Delta\) terms that are produced by the complete three-body current matching. It remains provisional until the native-Wolfram and P3-C amplitude-level gates pass.

## 4. Momentum-transfer conventions

For an initially resting on-shell nucleus,
\[
q_A^\mu=(E_R,\boldsymbol q_A),\qquad
t_A=q_A^2=-2m_AE_R,\qquad
Q_A^2=|\boldsymbol q_A|^2=2m_AE_R+E_R^2.
\]
- AFH \(y_A\) and spatial NR coefficients use \(Q_A^2\).
- The mediator propagator uses \(t_A\), so \((m_V^2-t_A)^2=(m_V^2+2m_AE_R)^2\).
- The formal one-body impulse prescription sets \(q_N^\mu=q_A^\mu\), hence \(t_N=t_A\).
- The separate static-nucleon diagnostic sets \(q_N^0=0\), hence \(t_N=-Q_A^2\). It is not the formal production transfer.

The AFH nuclear response is not evaluated at \(t_N\), and the nucleon form factors are not evaluated at \(y_A\).

## 5. Nucleon-current matching

For the effective-\(g_{VN}\) convention, use
\[
\widehat c_M=
\widehat F_1(t_N)
+\frac{t_N}{8m_N^2}
\left[\widehat F_1(t_N)+2\widehat F_2(t_N)\right],
\]
\[
\widehat c_{\Phi''}=
\frac{Q_A^2}{4m_N^2}
\left[\widehat F_1(t_N)+2\widehat F_2(t_N)\right].
\]
The \(t_N\) in \(\widehat c_M\) is the Lorentz invariant. The spatial \(Q_A^2\) in \(\widehat c_{\Phi''}\) is not interchangeable with it. Keep the signed \(M-\Phi''\) interference.

## 6. Form-factor prescriptions and selected-point comparison

The code computes full flavor-summed quark-current form factors first and then divides by three before using the external \(g_{VN}\) prefactor.

| Prescription | Full quark-current input | Interpretation |
|---|---|---|
| q0 anchor | \(F_1^{uds}(0)=3,\ F_2^{uds}(0)=-0.552\) | Original AFH M-only current normalization; finite-size \(W_M(Q_A)\) remains present |
| bishara_linear | \(F_1^{uds}(t_N)=3+8.392t_N+O(t_N^2),\ F_2^{uds}(0)=-0.552\) | First-order low-\(Q_N^2\) flavor-summed diagnostic |
| isoscalar_zexp | Isoscalar electromagnetic Sachs \(z\)-expansion plus strange-current inputs | Alternative finite-\(Q_N^2\) sensitivity prescription |

For the numerical table below, \(F_1^{uds}\) and \(F_2^{uds}\) are shown in the full quark-current convention, while \(\widehat c_M,\widehat c_{\Phi''}\) are normalized to the external \(g_{VN}\) coupling.

The archived Xe-131 response ratios are:
| \(E_R\) | \(W_{\Phi''}/W_M\) | \(W_{M\Phi''}/W_M\) |
|---:|---:|---:|
| 200 keV | 0.03695594 | -0.19120930 |
| 267 keV | 19.84506258 | -4.28296439 |

| \(E_R\) | Prescription | \(F_1^{uds}\) | \(F_2^{uds}\) | \(\widehat c_M\) | \(\widehat c_{\Phi''}\) | \(B/A\) | \(C/B\) | \(C/A\) |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 200 keV | bishara_linear | 2.590773 | -0.552000 | 0.860164 | 0.006853 | 0.739883 | 0.996955 | 0.737630 |
| 200 keV | isoscalar_zexp | 2.663163 | -0.468053 | 0.883741 | 0.007961 | 0.780997 | 0.996558 | 0.778309 |
| 267 keV | bishara_linear | 2.453682 | -0.552000 | 0.813741 | 0.008306 | 0.662175 | 0.914637 | 0.605649 |
| 267 keV | isoscalar_zexp | 2.563886 | -0.449775 | 0.849508 | 0.010242 | 0.721663 | 0.899610 | 0.649216 |

All ratios are dimensionless. \(B/A\) isolates the nucleon-current normalization correction. \(C/B\) isolates the additional \(\Phi''\) response and signed interference. \(C/A\) gives the total change relative to the original finite-size AFH M-only baseline.

The finite-\(Q_N^2\) single-nucleon correction changes the M-only kernel by tens of percent in these selected points. Once that correction is factored out, the additional charge response is small at 200 keV but reaches several-to-ten percent at 267 keV, where \(W_M\) is near a diffraction minimum. These selected-point diagnostics are not a natural-xenon halo-integrated result and do not include the spatial-current candidate.

## 7. Provenance and validation boundary

The archived Mathematica rate engine evaluates AFH \(W_M(y_A)\) at finite spatial \(Q_A\) and uses a constant effective nucleon coupling. This establishes that the original calculation includes finite nuclear size. It does not establish that the original rate engine separately inserted finite-\(t_N\) flavor-resolved \(F_1^{q/N},F_2^{q/N}\).

The current formal fixed-speed and P4 paths use \(t_N=t_A\) for the declared one-body impulse prescription. The static \(q_N^0=0\) results are diagnostic-only. The low-order Bishara prescription is a local first-order input, not an all-orders fit; \(F_2(0)\) does not determine \(F_2(t_N)\). Isoscalar-z-expansion is retained as an alternate sensitivity model.

The native seven-isotope AFH comparison remains a hard gate. Python-translated AFH data are not a substitute. The full spatial-current candidate is not promoted until the native response comparison and P3-C amplitude-level contraction pass.

## 8. Required reporting convention

Every fixed-speed and halo-fold result must report A, B, and C separately, with the same finite-size AFH response \(W_M(y_A)\) in every denominator. Report \(B/A\), \(C/B\), and \(C/A\) with the meanings defined above. Keep the raw AFH factor-four conversion separate from the quark-current factor-three normalization. Do not use the labels “pointlike M baseline” or “point-nucleus baseline” for A.