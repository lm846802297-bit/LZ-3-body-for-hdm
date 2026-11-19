# Three-body momentum-variable convention

This note defines the momentum variables used by the \(\chi_1+A\to\chi_1+A+s\)
calculation. It applies to the target-rest-frame kinematics, the Eq. (6)
amplitude kernel, the phase-space integrators, and nuclear-response inputs.

## Process, frame, and metric

The process is
\[
\chi_1(p)+A(P_A)\longrightarrow \chi_1(p')+A(P_A')+s(k_s),
\]
with the initial nucleus at rest,
\[
P_A^\mu=(m_A,\mathbf 0),
\]
and metric signature \(g_{\mu\nu}=\mathrm{diag}(+1,-1,-1,-1)\).

Use lower-case \(q_A^\mu\) for a four-vector and upper-case \(Q_A\) for its
non-negative spatial magnitude. They are not interchangeable.

## Canonical variables

| Symbol | Definition | Meaning |
|---|---|---|
| \(q_A^\mu\) | \(P_A'^\mu-P_A^\mu\) | Nuclear four-momentum transfer |
| \(q_\chi^\mu\) | \(p^\mu-p'^\mu\) | Dark-matter four-momentum loss |
| \(k_s^\mu\) | \(k^\mu\) | Emitted-scalar four-momentum |
| \(E_R\) | \(P_A'^0-m_A=q_A^0\) | Nuclear recoil energy |
| \(Q_A\) | \(|\mathbf q_A|\) | Spatial nuclear recoil momentum magnitude |

In the target-rest frame,
\[
q_A^\mu=(E_R,\mathbf q_A),\qquad Q_A=|\mathbf q_A|.
\]

## Exact kinematic identities

Four-momentum conservation gives
\[
p+P_A=p'+P_A'+k_s,
\]
and therefore
\[
\boxed{q_\chi^\mu=q_A^\mu+k_s^\mu}.
\]

The two-body subsystem used to parameterize the three-body phase space is
\[
\boxed{K^\mu=p^\mu-q_A^\mu=p'^\mu+k_s^\mu},
\qquad W^2=K^2.
\]

The nuclear on-shell condition \(P_A'^2=P_A^2=m_A^2\) implies
\[
q_A^2=-2m_AE_R,
\]
whereas the positive Euclidean spatial magnitude obeys
\[
\boxed{Q_A^2=E_R(E_R+2m_A)}.
\]
Thus
\[
Q_A=\sqrt{E_R(E_R+2m_A)}
\simeq\sqrt{2m_AE_R}
\]
in the small-recoil limit \(E_R\ll m_A\).

The invariant transfer \(t_A=q_A^2=-2m_AE_R\) is negative; \(Q_A^2\)
is the squared spatial magnitude and is positive. Do not identify either
quantity with \(q_\chi^2\) or \(|\mathbf q_\chi|^2\).

## Nuclear response versus particle propagators

All nuclear responses use the spatial nuclear recoil magnitude \(Q_A\). In
particular, the oscillator variable is
\[
\boxed{y=\frac{b_A^2Q_A^2}{4}
      =\left(\frac{b_AQ_A}{2}\right)^2}.
\]
The small-recoil expression \(Q_A\simeq\sqrt{2m_AE_R}\) is an approximation,
not the default exact response momentum. Legacy table columns named
q_GeV, q_response_GeV, or q_kinematics_exact_GeV continue to store this same
\(Q_A\) scalar for schema and archive compatibility.

The two internal \(\chi_2\) momenta in the before/after scalar-emission
diagrams are
\[
r_{\rm before}^\mu=p^\mu-k_s^\mu,\qquad
r_{\rm after}^\mu=p'^\mu+k_s^\mu=K^\mu.
\]
Their propagator denominators are built from their own four-momenta:
\[
D_{\rm before}=r_{\rm before}^2-m_{\chi_2}^2,
\qquad
D_{\rm after}=r_{\rm after}^2-m_{\chi_2}^2
              =W^2-m_{\chi_2}^2,
\]
with the selected width prescription added to the appropriate denominator.
Neither denominator is formed by substituting the nuclear spatial magnitude
\(Q_A\) or the dark-matter transfer \(q_\chi\).

## Three-body phase-space variables

At fixed \(E_R\), the magnitude \(Q_A\) is fixed by the nuclear mass shell.
The outer invariant \(W^2\) determines the angle between the incident
\(\chi_1\) momentum and \(\mathbf q_A\). The variables
\(z=\cos\theta_*\) and \(\phi_*\) describe the direction of the
\(\chi_1+s\) two-body decay in the \(K\)-rest frame. Consequently,
\((W^2,z,\phi_*)\) parameterize the internal three-body phase space; they
are not alternate definitions of the nuclear momentum transfer.

The three-body minimum speed must continue to be derived from the
three-body \(W_{\max}^2\ge(m_{\chi_1}+m_s)^2\) boundary. The elastic
two-body \(v_{\min}=Q_A/(2\mu_A)\) expression is not a substitute.

## Code mapping and compatibility

- eq6_kernel.Point.q_A: nuclear four-transfer \(P_A'-P_A\).
- eq6_kernel.Point.q_chi: \(p-p'\), computed from the external DM legs.
- eq6_kernel.Point.k_s: emitted-scalar four-momentum.
- eq6_kernel.Point.E_R: target-rest-frame recoil energy.
- eq6_kernel.Point.Q_A: \(|\mathbf q_A|\), used by nuclear response logic.
- eq6_kernel.chi2_internal_momenta: returns \(p-k_s\) and \(p'+k_s\).
- rate_kinematics.nuclear_recoil_momentum: returns the exact scalar \(Q_A\).
  The old momentum_transfer function remains as a backward-compatible alias.

The legacy Point.q and Point.k storage fields remain available to avoid
breaking existing callers; new code should use the explicit properties above.

## Regression coverage

The Eq. (6) and independent threshold-stable phase-space tests check:

- \(q_\chi-q_A-k_s=0\) as a four-vector identity;
- external mass shells and total four-momentum closure;
- \(q_A^2+2m_AE_R=0\) and \(Q_A^2-E_R(E_R+2m_A)=0\);
- the internal \(\chi_2\) momenta and \(r_{\rm after}^2=W^2\);
- preservation of the legacy aliases and the exact \(Q_A(E_R)\) helper.

These are kinematic and software-consistency checks. They do not change the
amplitude normalization, nuclear-response normalization, archived numerical
results, or the stated Dirac/width assumptions.
