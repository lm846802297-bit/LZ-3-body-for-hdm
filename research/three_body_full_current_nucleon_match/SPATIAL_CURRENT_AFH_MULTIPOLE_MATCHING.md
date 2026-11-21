# Spatial Dirac--Pauli current and AFH multipole matching

**Status:** leading one-body operator content identified; complete three-body
Wilson-coefficient projection and isotope contraction remain pending.

This note fixes the operator-level bridge between the exact phase-space
integrated three-body dark-matter current and the AFH nuclear response basis.
It is deliberately not a numerical prediction for the spatial-current rate.

## 1. Conventions that must remain separate

The nuclear transfer and the one-nucleon transfer are
\[
q_A^\mu=P_A'^\mu-P_A^\mu,\qquad
q_N^\mu=k_N'^\mu-k_N^\mu.
\]
In the static one-body impulse approximation,
\[
q_N^0=0,\qquad \boldsymbol q_N=\boldsymbol q_A,\qquad
t_N=-Q_A^2,\qquad Q_A=|\boldsymbol q_A|.
\]
The AFH Fourier convention in the current project is
\(\boldsymbol q_{\rm AFH}=-\boldsymbol q_A\). The emitted scalar momentum
is not part of the nuclear Fourier momentum:
\[
\boldsymbol p_\chi'-\boldsymbol p_\chi
=-\boldsymbol q_A-\boldsymbol k_s.
\]
The scalar momentum and both off-shell \(\chi_2\) propagators remain inside
\(\mathcal T_3^\mu\).

The nucleon vertex convention is
\[
J_N^\mu=
\bar u_N(k_N')
\left[
F_1^{V,N}(t_N)\gamma^\mu+
\frac{iF_2^{V,N}(t_N)}{2m_N}
\sigma^{\mu\nu}q_{N,\nu}
\right]u_N(k_N).
\]
The sign of the Pauli term is tied to \(q_N=k_N'-k_N\). The current used
below is divided by \(2\sqrt{E_NE_N'}\) before identifying AFH one-body
operator coefficients.

## 2. Nonrelativistic Dirac--Pauli current

Let
\[
\boldsymbol K_N=\frac{\boldsymbol k_N+\boldsymbol k_N'}{2},
\qquad \boldsymbol S_N=\frac{\boldsymbol\sigma_N}{2}.
\]
For the static elastic impulse point, the leading current is
\[
J_N^0=
c_M(t_N)+c_{\Phi''}(t_N)\,\Phi''+\cdots,
\]
with the already matched charge coefficients
\[
c_M(t_N)=F_1^V(t_N)+
\frac{t_N}{8m_N^2}\left[F_1^V(t_N)+2F_2^V(t_N)\right],
\]
\[
c_{\Phi''}(t_N)=
\frac{Q_A^2}{4m_N^2}
\left[F_1^V(t_N)+2F_2^V(t_N)\right].
\]
The corresponding leading spatial one-body current is
\[
\boxed{
\boldsymbol J_N=
\frac{F_1^V(t_N)}{m_N}\boldsymbol K_N
+\frac{i\,[F_1^V(t_N)+F_2^V(t_N)]}{2m_N}
  \left(\boldsymbol\sigma_N\times\boldsymbol q_N\right)
+\mathcal O(p^3/m_N^3).
}
\]
The plus sign and the order of the cross product are those returned by the
exact Dirac--Pauli spinor implementation in
\`full_current_nucleon_match.py\`.

The two spatial terms are distinct:

1. \(F_1^V\boldsymbol K_N/m_N\) is the convection current. Its transverse
   vector multipole is the AFH \(\Delta\) channel.
2. \(i(F_1^V+F_2^V)(\boldsymbol\sigma_N\times\boldsymbol q_N)/(2m_N)\)
   is the magnetization current. It is transverse by construction and
   projects onto the AFH \(\Sigma'\) channel at this order.

The AFH \(\Sigma'\)-\(\Delta\) mixed response is therefore required whenever
both terms are retained. It must be calculated with the signed AFH
interference response, not inferred from the two diagonal responses.

## 3. Why the leading static current does not generate all eight AFH channels

The AFH v6.0 source defines the eight responses through
\`ResponseNuclear[y,index,tau1,tau2]\`. Its operator implementation gives:

| AFH index | Response | Leading-current status |
|---:|---|---|
| 1 | \(W_M\) | present in the vector charge |
| 2 | \(W_{\Sigma''}\) | absent at this order |
| 3 | \(W_{\Sigma'}\) | present from magnetization |
| 4 | \(W_{\Phi''}\) | present in the vector charge |
| 5 | \(W_{\widetilde\Phi'}\) | absent at this order |
| 6 | \(W_\Delta\) | present from convection |
| 7 | \(W_{M\Phi''}\) | present as charge interference |
| 8 | \(W_{\Sigma'\Delta}\) | present as spatial-current interference |

The absence statements are statements about the leading static
one-body Dirac--Pauli vector current, not about the AFH nuclear responses
themselves:

- \(\boldsymbol q_N\cdot(\boldsymbol\sigma_N\times\boldsymbol q_N)=0\),
  so the leading magnetization current has no longitudinal-spin
  \(\Sigma''\) component.
- The leading convection and magnetization structures above do not contain
  the additional spin-velocity operator defining
  \(\widetilde\Phi'\). That response can arise from higher-order
  one-body currents or other interactions and must not be deleted from the
  general AFH database.

For a static on-shell equal-mass nucleon,
\[
q_{N\mu}J_N^\mu=0,\qquad
\boldsymbol q_N\cdot\boldsymbol K_N=0.
\]
Thus the leading spatial convection current is transverse as well. In a
bound nucleus the exact transfer has \(q_A^0=E_R\ne0\); longitudinal
multipoles and continuity-equation corrections are not automatically
identical to this static impulse limit. They must be assessed separately
rather than silently set to zero in a claimed exact calculation.

## 4. Three-body amplitude before the AFH projection

With metric \((+---)\), the exact radiative amplitude is
\[
\mathcal M_3=
\mathcal T_3^0J_N^0-\boldsymbol{\mathcal T}_3\cdot\boldsymbol J_N.
\]
At the operator level its leading static expansion is
\[
\begin{aligned}
\mathcal M_3={}&
\mathcal T_3^0
\left[c_M(t_N)M+c_{\Phi''}(t_N)\Phi''\right]\\
&-\frac{F_1^V(t_N)}{m_N}
  \boldsymbol{\mathcal T}_{3,\perp}\cdot\boldsymbol K_{N,\perp}\\
&-\frac{i[F_1^V(t_N)+F_2^V(t_N)]}{2m_N}
  \boldsymbol{\mathcal T}_{3,\perp}\cdot
  (\boldsymbol\sigma_N\times\boldsymbol q_N)
+\cdots.
\end{aligned}
\]
The second and third lines are the terms to be projected onto the AFH
\(\Delta\) and \(\Sigma'\) multipoles. The full
\(\boldsymbol{\mathcal T}_3\) must be retained; replacing it by an elastic
\(\boldsymbol v^\perp\), or imposing the elastic identity
\(\boldsymbol q\cdot\boldsymbol v^\perp=0\) on the three-body DM momentum
change, is not valid.

The leading allowed response structure is therefore
\[
\boxed{
M,\quad \Phi'',\quad M\!-\!\Phi'',\quad
\Delta,\quad \Sigma',\quad \Sigma'\!-\!\Delta.
}
\]
This is the six-channel leading-current set. The full eight-response
database remains useful as a completeness check and as input for higher
orders.

## 5. What the phase-space-integrated DM tensor supplies

The phase-space calculation in
\`three_body_phase_space_tensor.py\` stores
\[
G_{\mu a,\nu b}^{(3)}
=\int d\Phi_3\,c_a^\mu c_b^{\nu *},
\qquad
L_{\mu\nu}^{(3)}=\sum_aG_{\mu a,\nu a}^{(3)}.
\]
The tensor is complex and is expressed in a local frame whose third spatial
axis is \(\widehat{\boldsymbol q}_A\). It preserves all four Lorentz
components, all DM Pauli components, both scalar-emission orderings, and
their coherent interference.

This is the correct DM-side input for the next projection. It is not
sufficient to keep only \(L_{00}\), nor is it safe to replace the full
transverse block by a scalar trace before the multipole algebra has shown
which symmetric or antisymmetric transverse combinations enter the
\(\Sigma'\), \(\Delta\), and \(\Sigma'\)-\(\Delta\) terms. In particular,
the signed interference coefficient must be derived with the exact AFH
spherical-tensor phases.

The physical nuclear response has the schematic form
\[
\frac{d\Gamma}{dE_R}\ \propto\
I_{00}^{(3)}\,\mathcal C_{M,\Phi''}
+\mathcal C_{\Delta,\Sigma'}^{(3)},
\]
where the first term is the already matched charge sector and the second
term is the as-yet uncomputed spatial multipole contraction. The
\(\mathcal C\)'s are not simply \(L_{00}\), \(L_{11}+L_{22}\), or
\(r_\chi\) times a nuclear response: their normalization and interference
weights follow from the vector-spherical-harmonic projection.

## 6. Exact leading spatial coefficients from AFH Eq. (107)

The AFH Appendix A multipole decomposition gives the elastic response
coefficients in terms of the WIMP-side vectors \(\boldsymbol l_M\) and
\(\boldsymbol l_5\). In particular, Eq. (107) contains
\[
C_\Delta=
\frac12\left[
\frac{q^2}{m_N^2}\boldsymbol l_M\cdot\boldsymbol l_M^*
-\left(\frac{\boldsymbol q}{m_N}\cdot\boldsymbol l_M\right)
 \left(\frac{\boldsymbol q}{m_N}\cdot\boldsymbol l_M^*\right)
\right],
\]
\[
C_{\Sigma'}=
\frac12\left[
\boldsymbol l_5\cdot\boldsymbol l_5^*
-(\hat{\boldsymbol q}\cdot\boldsymbol l_5)
 (\hat{\boldsymbol q}\cdot\boldsymbol l_5^*)
\right],
\]
\[
C_{\Sigma'\Delta}=
\frac{\boldsymbol q}{m_N}\cdot
\operatorname{Re}\left[i\boldsymbol l_M\times\boldsymbol l_5^*\right].
\]
These are the AFH response coefficients; the last one is not the
helicity-odd coefficient in the generic transverse electric--magnetic
leptonic multipole formula.

For the static Dirac--Pauli current, the amplitude is
\[
-\boldsymbol{\mathcal T}_3\cdot\boldsymbol J_N
=-\frac{F_1^V}{m_N}\boldsymbol{\mathcal T}_3\cdot\boldsymbol K_N
-i\frac{F_1^V+F_2^V}{2m_N}
 \boldsymbol\sigma_N\cdot
 (\boldsymbol q_N\times\boldsymbol{\mathcal T}_3).
\]
The AFH Fourier convention is \(\boldsymbol q=-\boldsymbol q_A\), while
\(\boldsymbol q_N=\boldsymbol q_A\). Matching to the AFH one-body
operators therefore gives
\[
\boldsymbol l_M=-F_1^V\boldsymbol{\mathcal T}_3,\qquad
\boldsymbol l_5=
i\frac{F_1^V+F_2^V}{2m_N}
(\boldsymbol q\times\boldsymbol{\mathcal T}_3).
\]
The phase-space-integrated spin average is
\(L^{ij}=\frac{1}{2j_\chi+1}\sum_{\rm spins}
\int d\Phi_3\,\mathcal T_3^i\mathcal T_3^{j*}\).
With \(\boldsymbol q\) along the third axis, Eq. (107) then gives
\[
\boxed{
C_\Delta^{(3)}
=\frac{(F_1^V)^2Q_A^2}{2m_N^2}
 (L^{11}+L^{22}),
}
\]
\[
\boxed{
C_{\Sigma'}^{(3)}
=\frac{(F_1^V+F_2^V)^2Q_A^2}{8m_N^2}
 (L^{11}+L^{22}),
}
\]
\[
\boxed{
C_{\Sigma'\Delta}^{(3)}
=-\frac{F_1^V(F_1^V+F_2^V)Q_A^2}{2m_N^2}
 (L^{11}+L^{22}).
}
\]
The sign in the last expression follows from the simultaneous use of
\(\boldsymbol q_{\rm AFH}=-\boldsymbol q_A\),
\(\boldsymbol q_N=+\boldsymbol q_A\), and the metric
\((+---)\). It must be checked against the exact AFH spherical
matrix-element implementation before the coefficient is frozen.

The leading magnetization vector is perpendicular to \(\boldsymbol q\),
so \(C_{\Sigma''}^{(3)}=0\) at this order. The leading current also has
no transverse spin-velocity coefficient, so
\(C_{\widetilde\Phi'}^{(3)}=0\). These are operator-level statements for
the leading static vector current.

A useful algebraic check is
\[
C_{\Sigma'\Delta}^{(3)}
=-2\sqrt{C_\Delta^{(3)}C_{\Sigma'}^{(3)}}
\]
when \(F_1^V(F_1^V+F_2^V)>0\). This relation is a coefficient identity
from the fact that \(\boldsymbol l_5\) is the transverse \(90^\circ\)
rotation of \(\boldsymbol l_M\); it is not a claim that the nuclear
responses themselves saturate their Cauchy--Schwarz bound.

For the 12 integrated DM tensors, the common transverse factor obeys
\[
4.08\times10^{-8}
\leq\frac{(L^{11}+L^{22})/2}{L^{00}}
\leq2.26\times10^{-7}.
\]
The generic transverse helicity-odd component
\[
\frac{\left|-i(L^{12}-L^{21})\right|}
 {|L^{11}+L^{22}|}
\]
is at most \(7.39\times10^{-16}\), but this does **not** set
\(C_{\Sigma'\Delta}^{(3)}\) to zero. The AFH Eq. (107) coefficient above
depends on the transverse-even trace \(L^{11}+L^{22}\). The two
quantities must not be confused.

The expressions above are leading static one-body coefficients before
the common mediator/coupling factors. They are to be contracted with the
physical equal-\(p=n\) AFH response columns, with the factor of four
applied exactly once. \(F_1^V(t_N)\) and \(F_2^V(t_N)\) must ultimately
be evaluated at finite \(t_N=-Q_A^2\); zero-momentum values are only
benchmark anchors.

## 7. Mandatory next calculation

The next implementation must:

1. use the exact AFH definitions of \(\Delta_J\), \(\Sigma'_J\), and
   \(\Sigma''_J\) in `v6/dmformfactor-V6.m`, not substitute a
   differently normalized `DeltaPrime` operator;
2. derive the spherical transverse projectors and all phases in the
   convection and magnetization multipoles;
3. contract the resulting coefficients with the full complex
   q-aligned (G_{mu a,
u b}^{(3)}), retaining the coherent
   before/after interference;
4. recover the charge-sector (M+Phi'') result as a regression limit;
5. recover the static one-nucleon convection and magnetization limits from
   the exact Dirac--Pauli spinors;
6. verify positivity of the combined nuclear response and the
   Cauchy--Schwarz bounds for both (M)-(Phi'') and
   (Sigma')-(Delta);
7. perform the isotope OBDME contraction using the native AFH response
   convention, applying the equal-(p=n) factor of four exactly once;
8. only after the component-wise phase-space convergence scan passes,
   perform the natural-xenon halo fold.

## 7. References and source of conventions

- Anand, Fitzpatrick, and Haxton, Phys. Rev. C 89, 065501 (2014),
  arXiv:1308.6288: AFH response operators and normalization.
- Hoferichter, Klos, Menéndez, and Schwenk, Phys. Rev. D 94, 063505
  (2016), arXiv:1605.08043: vector-current matching, the six nuclear
  responses, and the distinction between coherent charge and spatial
  current operators.
- Hoferichter, Menéndez, and Schwenk, Phys. Rev. D 102, 074018 (2020),
  arXiv:2007.08529: nonrelativistic vector charge and multipole expansion.
- Repository source: `v6/dmformfactor-V6.m`, definitions of
  `SigmaPJ`, `SigmaPPJ`, `PhiTPJ`, and
  `DeltaJ`.


## 8. P2 particle-side multipole projection and signed phase audit

The AFH operator definitions are now matched at the operator level to the
Pauli-reduced Dirac--Pauli current. In the AFH convention,
\[
\Delta_{JM}=\boldsymbol M_{JJM}\cdot\frac{\boldsymbol\nabla}{q},
\qquad
\Sigma'_{JM}=-i\left(
\frac{\boldsymbol\nabla}{q}\times\boldsymbol M_{JJM}
\right)\cdot\boldsymbol\sigma.
\]
The AFH v6.0 implementation makes the corresponding choices explicitly:
\[
\begin{aligned}
\Delta_J&=\texttt{MJLDivQ}[\ldots,J,J],\\
\Sigma'_J&=
-\frac{\sqrt J}{\sqrt{2J+1}}\,
\texttt{MJLSigma}[\ldots,J,J+1]
+\frac{\sqrt{J+1}}{\sqrt{2J+1}}\,
\texttt{MJLSigma}[\ldots,J,J-1].
\end{aligned}
\]
The ordered response index 8 is \((\Sigma'_J,\Delta_J)\), not the
opposite ordering. These definitions are in v6/dmformfactor-V6.m around
lines 903--917 and 981--1015. The vector-spherical-harmonic definitions
are also given in Fitzpatrick et al., arXiv:1203.3542, Eq. (43).

For the amplitude
\[
\mathcal M_{\rm spatial}
=-\boldsymbol{\mathcal T}_3\cdot
\left[
\frac{F_1^V}{m_N}\boldsymbol K_N
+\frac{i(F_1^V+F_2^V)}{2m_N}
(\boldsymbol\sigma_N\times\boldsymbol q_N)
\right],
\]
use \(\boldsymbol q_{\rm AFH}=-\boldsymbol q_A=-\boldsymbol q_N\).
The AFH particle-side vectors are
\[
\boldsymbol l_M=-F_1^V\boldsymbol{\mathcal T}_3,\qquad
\boldsymbol l_5=
\frac{i(F_1^V+F_2^V)}{2m_N}
(\boldsymbol q_{\rm AFH}\times\boldsymbol{\mathcal T}_3).
\]
This follows from
\[
\boldsymbol{\mathcal T}_3\cdot
(\boldsymbol\sigma_N\times\boldsymbol q_N)
=\boldsymbol\sigma_N\cdot
(\boldsymbol q_N\times\boldsymbol{\mathcal T}_3)
\]
and the overall minus sign in the spatial contraction with metric
\((+---)\).

Inserting these vectors into AFH Appendix A Eq. (107),
\[
\begin{aligned}
C_\Delta&=\frac12\left[
\frac{q^2}{m_N^2}\boldsymbol l_M\cdot\boldsymbol l_M^*
-\left(\frac{\boldsymbol q}{m_N}\cdot\boldsymbol l_M\right)
 \left(\frac{\boldsymbol q}{m_N}\cdot\boldsymbol l_M^*\right)
\right],\\
C_{\Sigma'}&=\frac12\left[
\boldsymbol l_5\cdot\boldsymbol l_5^*
-(\hat{\boldsymbol q}\cdot\boldsymbol l_5)
 (\hat{\boldsymbol q}\cdot\boldsymbol l_5^*)
\right],\\
C_{\Sigma'\Delta}&=
\frac{\boldsymbol q}{m_N}\cdot
\operatorname{Re}\left[i\boldsymbol l_M\times\boldsymbol l_5^*\right],
\end{aligned}
\]
gives
\[
\boxed{
\begin{aligned}
C_\Delta&=\frac{(F_1^V)^2Q_A^2}{2m_N^2}L_T,\\
C_{\Sigma'}&=\frac{(F_1^V+F_2^V)^2Q_A^2}{8m_N^2}L_T,\\
C_{\Sigma'\Delta}&=
-\frac{F_1^V(F_1^V+F_2^V)Q_A^2}{2m_N^2}L_T,
\end{aligned}
\qquad L_T=L_{11}+L_{22}.
}
\]
In particular, the negative sign is fixed by the simultaneous use of
q_AFH=-q_A, q_N=+q_A, the spatial metric sign, and the AFH Eq. (107)
cross-product order. For \(F_1^V(F_1^V+F_2^V)>0\),
\[
C_{\Sigma'\Delta}=-2\sqrt{C_\Delta C_{\Sigma'}}.
\]
This is a particle-side coefficient identity; it does not imply saturation
of the nuclear-response Cauchy--Schwarz bound.

An independent amplitude-level implementation now evaluates Eq. (107)
before spin averaging, from arbitrary complex spin-channel vectors
\(\mathcal T_3^i\), and compares it with the 4x4 Lorentz-tensor
coefficient extractor. The regression tests:
- the signed \(\Sigma'\)-\(\Delta\) coefficient and its factor of two;
- invariance under rotations of the transverse axes;
- independence from the longitudinal DM-current component;
- distinction from the generic transverse helicity-odd tensor weight.

This closes the **particle-side Eq. (107) algebra and relative phase** for
the declared leading-static one-body current. It does not yet close the
full many-body spherical-multipole contraction: the direct covariant,
q-frame-rotated, and AFH OBDME contractions still have to agree pointwise
in P3. The current 84-row contraction remains provisional until the native
AFH response archive and P3 gates are tied to the same run and conventions.
