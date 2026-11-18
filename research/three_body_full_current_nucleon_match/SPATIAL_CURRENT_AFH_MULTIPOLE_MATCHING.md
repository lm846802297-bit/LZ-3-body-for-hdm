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

## 6. Transverse helicity-odd tensor check

The latest integrated tensor artifact (workflow run 44231019823, artifact
14394488484) also permits a direct check of the transverse antisymmetric
DM tensor component. In the q-aligned frame define
[
mathcal H_T=
\frac{\left|-i(L^{12}-L^{21})\right|}
 {|L^{11}+L^{22}|}.
]
Across the 12 archived combinations (four fixed-speed benchmarks and
zero/pole/running widths),
[
\boxed{\max \mathcal H_T=7.39\times10^{-16}.}
]
This is consistent with zero at floating-point precision for the
unpolarized pure-vector DM current used here.

In the standard multipole expansion, the transverse electric--magnetic
interference term is proportional to the helicity-odd factor
((\boldsymbol l\times\boldsymbol l^*)_3); see
Hoferichter--Menéndez--Schwenk, PRD 102, 074018 (2020), Appendix A,
Eq. (111). The corresponding q-aligned tensor factor is proportional to
(-i(L^{12}-L^{21})). Therefore the present numerical tensor strongly
indicates that the leading (W_{\Sigma'\Delta}) coefficient vanishes
for these pure-vector, unpolarized benchmark conditions, even though the
nuclear response (W_{\Sigma'\Delta}) itself is not zero in general.

This is an additional kinematic diagnostic, not yet a standalone AFH
acceptance gate: the exact AFH spherical projector and its normalization
must still be implemented before the mixed response is removed from any
rate formula. Keep the signed (W_{\Sigma'\Delta}) response in the
general expression until that projection is explicitly verified.

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
