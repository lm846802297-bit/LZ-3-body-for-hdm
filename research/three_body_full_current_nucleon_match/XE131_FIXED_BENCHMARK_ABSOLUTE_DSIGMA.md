# Xe-131 fixed-benchmark absolute differential cross section

**Status:** corrected coupling normalization and finite-size AFH baseline  
**Scope:** fixed-speed, single-isotope absolute \(d\sigma/dE_R\) in the native-AFH coherent charge sector \(M+\Phi''+M\Phi''\). This is not the complete six-channel nuclear-vector-current result.

## 1. Fixed benchmark

| Input | Value |
|---|---:|
| \(m_{\chi_1}\) | 1,000 GeV |
| \(m_{\chi_2}\) | 1,000.00045 GeV |
| \(\Delta m\) | 450 keV, fixed at every recoil |
| \(m_s\) | 300 keV |
| \(m_V\) | 10 GeV |
| \(v\) | 776 km/s |
| \(g_2\) (width input) | 1 |
| \((g_1g_2g_{VN})^2\) | 1 |
| width prescription | asymmetric Eq. (19) pole width |
| target | Xe-131 |

The target mass follows the current repository isotope-mass convention:
\[
m_A=(M_{\rm atom}-54m_e)u
=121.90971983538435~\mathrm{GeV}.
\]
The AFH response factor of four is already included exactly once in the physical equal-proton/neutron response; it is not applied again.

## 2. Mandatory finite-size AFH reference and A/B/C hierarchy

The reference is **not a point nucleus**. It uses the native finite-recoil AFH response
\[
Q_A^2=|\mathbf q_A|^2=2m_AE_R+E_R^2,\qquad
y_A=\left(\frac{b_AQ_A}{2}\right)^2,
\]
\[
\boxed{
R_{A,M}^{\rm phys}(Q_A)
=A^2\frac{W_M^{00}(y_A)}{W_M^{00}(0)},
\qquad R_{A,M}^{\rm phys}(0)=A^2 .
}
\]
The Python native-response archive stores the physical equal-\(p=n\) response, with the AFH raw-to-physical factor four already applied once. No additional Helm, Fermi, Gaussian, or other whole-nucleus form factor is multiplied onto \(W_M(y_A)\).

Three kernels are reported, all using the same finite-\(Q_A\) AFH \(W_M(y_A)\):

- **A — original finite-size AFH M-only reference:** \(L_C^{(3)}W_M^{\rm phys}(y_A)\), with the effective nucleon current frozen at \(\widehat F_1(0)=1\).
- **B — finite-\(t_N\) nucleon M-only result:** \(L_C^{(3)}\widehat c_M(t_N)^2W_M^{\rm phys}(y_A)\). This changes the one-nucleon current, not the nuclear shape.
- **C — charge-response extension:** B plus the \(\Phi''\) diagonal and signed \(M-\Phi''\) interference terms.

Thus
\[
\frac{B}{A}-1
\]
isolates the single-nucleon finite-\(t_N\) correction,
\[
\frac{C}{B}-1
\]
isolates the additional AFH charge-response correction at fixed nucleon form factors, and
\[
\frac{C}{A}-1
\]
is the total change relative to the original finite-size AFH M-only reference. Do not interchange these three ratios.

## 3. Coupling normalization

The original paper and Mathematica benchmark use the effective nucleon coupling in the external prefactor:
\[
g_{VN}=3g_{Vq},\qquad
(g_1g_2g_{VN})^2.
\]
The full universal \(u+d+s\) quark current has
\[
F_1^{uds}(0)=3,\qquad F_2^{uds}(0)=-0.552.
\]
Therefore this \(g_{VN}\)-normalized rate uses
\[
\boxed{
\widehat F_i(t_N)=F_i^{uds}(t_N)/3,
\qquad
\widehat F_1(0)=1,\quad \widehat F_2(0)=-0.184 .
}
\]
The current coefficients in the code use \(\widehat F_1,\widehat F_2\). The external prefactor must not be multiplied by the unnormalized \(F_1^{uds}(0)^2=9\) again. This avoids the factor-nine error that would result from mixing the \(g_{VN}\) prefactor with the full quark-current normalization.

The equivalent quark-coupling convention is \(g_{Vq}=g_{VN}/3\) with the unnormalized \(F_i^{uds}\). Both conventions must agree pointwise.

## 4. Cross-section formula

The absolute charge-sector differential cross section is
\[
\frac{d\sigma_{\rm ch}}{dE_R}
=
\frac{m_A(g_1g_2g_{VN})^2}
{256\pi^3p_{\chi_1}^2(m_V^2-t_A)^2}
L_C^{(3)}
\left[
\widehat c_M^2W_M^{\rm phys}
+2\widehat c_M\widehat c_{\Phi''}W_{M\Phi''}^{\rm phys}
+\widehat c_{\Phi''}^2W_{\Phi''}^{\rm phys}
\right].
\]
The \(M\)-only A and B kernels are obtained by retaining only the first term, with the corresponding zero-transfer or finite-\(t_N\) coefficient.

The coefficients are
\[
\widehat c_M=
\widehat F_1+
\frac{t_N(\widehat F_1+2\widehat F_2)}{8m_N^2},
\qquad
\widehat c_{\Phi''}=
\frac{Q_A^2(\widehat F_1+2\widehat F_2)}{4m_N^2}.
\]
For the formal one-body impulse prescription,
\[
q_N^\mu=q_A^\mu,\qquad
t_N=t_A=-2m_AE_R.
\]
The static-nucleon diagnostic \(q_N^0=0\), \(t_N=-Q_A^2\), is a separate approximation and is not used for this production curve.

Keep the three momentum-transfer quantities separate:
\[
Q_A^2=2m_AE_R+E_R^2,\qquad
t_A=-2m_AE_R,\qquad
t_N=t_A\quad\text{(formal one-body impulse)}.
\]
AFH \(y_A\) and spatial NR coefficients use \(Q_A^2\). The mediator propagator uses \(t_A\), with
\[
(m_V^2-t_A)^2=(m_V^2+2m_AE_R)^2,
\]
not \((m_V^2+Q_A^2)^2\). The incident momentum is \(p_{\chi_1}=m_{\chi_1}\gamma v/c\).

The continuity-reduced weight is
\[
L_C^{(3)}
=L_{00}^{(3)}
-\frac{E_R}{Q_A}(L_{03}^{(3)}+L_{30}^{(3)})
+\left(\frac{E_R}{Q_A}\right)^2L_{33}^{(3)}.
\]
This reduction is conditional on continuity of the complete nuclear one-body vector current. The DM transition current is not assumed to be conserved.

The kernel has units GeV\(^2\), the public prefactor GeV\(^{-5}\), and \(d\sigma/dE_R\) GeV\(^{-3}\). Conversion to cm\(^2\)/keV uses \(3.893793721\times10^{-34}\).

## 5. Numerical prescription

- Integrate the coherent two-diagram spin-resolved DM current over the complete \(2\to3\) phase space.
- Use the formal asymmetric Eq. (19) prescription: the first \(p-k\) propagator is zero-width \((+i0^+)\), while the second \(p'+k\) propagator carries the constant pole width evaluated at \(m_{\chi_2}\).
- Use the provenance-pinned 2,401-point native AFH v6.0 \(W_M,W_{\Phi''},W_{M\Phi''}\) archive with PCHIP interpolation.
- Use the 2-keV global recoil grid and 0.5-keV refinement around the AFH response minima, including exact kinematic endpoints.
- Compare the curve-order integral with independent higher-order anchors.
- Cross-check the spin-resolved \(L_{00}^{(3)}\) against the legacy Eq. (6) integral.

## 6. Explicit scope limits

This is an absolute **charge-sector** spectrum, not the final complete \(L_{\mu\nu}W_A^{\mu\nu}\) spectrum. Native transverse \(\Delta,\Sigma'\), and \(\Sigma'-\Delta\) response validation and the P3-C bound-nucleus amplitude-level contraction remain separate gates.

The primary finite-\(t_N\) input is the first-order flavor-resolved Bishara low-\(Q_N^2\) diagnostic; isoscalar-z-expansion is an alternate sensitivity prescription. Neither nucleon form-factor prescription replaces the finite-size AFH nuclear response.

No halo average, isotope sum, detector response, exposure, event count, or exclusion is included. The absolute normalization is the stated unit reference \((g_1g_2g_{VN})^2=1\); other coupling choices rescale the result linearly. The pole-width interpretation is conditional on Dirac \(\chi_2\), a real scalar, a pure-scalar off-diagonal Yukawa coupling, and no additional open \(\chi_2\) decay channels.