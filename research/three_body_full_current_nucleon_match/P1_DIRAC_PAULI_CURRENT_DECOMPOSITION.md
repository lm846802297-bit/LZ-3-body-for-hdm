# P1: one-body Dirac--Pauli current decomposition

**Status:** completed for the free on-shell one-body impulse approximation at the stated nonrelativistic order. The bound-nucleus/off-shell extension is deliberately not claimed.

## 1. Conventions

Use
\[
q_N^\mu=k_N'^\mu-k_N^\mu,\qquad
K_N^\mu=\frac{k_N'^\mu+k_N^\mu}{2},
\qquad
t_N=q_N^2,
\]
with metric \(g_{\mu\nu}=(+,-,-,-)\). In the spatial components,
\[
\boldsymbol q_N=\boldsymbol k_N'-\boldsymbol k_N,\qquad
\boldsymbol K_N=\frac{\boldsymbol k_N'+\boldsymbol k_N}{2}
=\boldsymbol\ell.
\]
The current is
\[
J_N^\mu=\bar u_N(k_N')
\left[F_1^V(t_N)\gamma^\mu+
\frac{iF_2^V(t_N)}{2m_N}\sigma^{\mu\nu}q_{N,\nu}\right]u_N(k_N).
\]
The AFH Fourier momentum used later is \(\boldsymbol q_{\rm AFH}=-\boldsymbol q_A\), whereas the nucleon vertex above uses \(\boldsymbol q_N=+\boldsymbol q_A\) in the impulse matching slice. These signs are not interchangeable.

Before matching to AFH one-body operators, divide the covariant spinor matrix element by \(2\sqrt{E_NE_N'}\). The exact code path is the nucleon_current_matrices function followed by nonrel_state_normalization.

## 2. Gordon decomposition and Pauli reduction

For on-shell equal-mass nucleons, the Gordon identity gives
\[
J_N^\mu=(F_1^V+F_2^V)\bar u_N'\gamma^\mu u_N
-\frac{F_2^V}{2m_N}(k_N'+k_N)^\mu\bar u_N'u_N.
\]
Writing \(\boldsymbol K_N=(\boldsymbol k_N'+\boldsymbol k_N)/2\), the NR-normalized current through the first nontrivial orders is
\[
\boxed{
\mathscr J_N^0=
F_1^V(t_N)+
\frac{t_N}{8m_N^2}\left[F_1^V(t_N)+2F_2^V(t_N)\right]
+\frac{i\left[F_1^V(t_N)+2F_2^V(t_N)\right]}{4m_N^2}
\boldsymbol\sigma_N\cdot
(\boldsymbol q_N\times\boldsymbol K_N)
+\mathcal O(p^4/m_N^4)
}
\]
and
\[
\boxed{
\boldsymbol{\mathscr J}_N=
\frac{F_1^V(t_N)}{m_N}\boldsymbol K_N
+\frac{i\left[F_1^V(t_N)+F_2^V(t_N)\right]}{2m_N}
(\boldsymbol\sigma_N\times\boldsymbol q_N)
+\mathcal O(p^3/m_N^3).
}
\]
Here \(\mathscr J_N^\mu=J_N^\mu/(2\sqrt{E_NE_N'})\). The \(J^0\) expression contains the Darwin--Foldy charge correction and the spin-orbit charge operator. The spatial expression contains the convection and magnetization currents.

The spatial split is
\[
\boldsymbol{\mathscr J}_{\rm conv}
=\frac{F_1^V}{m_N}\boldsymbol K_N,\qquad
\boldsymbol{\mathscr J}_{\rm mag}
=\frac{i(F_1^V+F_2^V)}{2m_N}
(\boldsymbol\sigma_N\times\boldsymbol q_N).
\]
Since
\[
\boldsymbol q_N\cdot
(\boldsymbol\sigma_N\times\boldsymbol q_N)=0,
\]
the magnetization current is exactly transverse. The convection current has both longitudinal and transverse components for a general internal momentum:
\[
\boldsymbol K_{N,\parallel}
=(\hat{\boldsymbol q}_N\cdot\boldsymbol K_N)\hat{\boldsymbol q}_N,\qquad
\boldsymbol K_{N,\perp}
=\boldsymbol K_N-\boldsymbol K_{N,\parallel}.
\]
Only the transverse convection and magnetization pieces feed the leading \(\Delta\) and \(\Sigma'\) channels. The longitudinal piece belongs to the Coulomb/longitudinal sector and must be handled with a consistent continuity equation.

## 3. Exact longitudinal relation and the two kinematic slices

For a free on-shell nucleon,
\[
q_{N\mu}J_N^\mu=0
\quad\Longrightarrow\quad
\boxed{
\mathscr J_{N,\parallel}
=\frac{q_N^0}{Q_N}\mathscr J_N^0,\qquad
Q_N=|\boldsymbol q_N|.
}
\]
Also,
\[
q_N^0=E_N'-E_N
=\frac{2\boldsymbol K_N\cdot\boldsymbol q_N}{E_N'+E_N}.
\]
Thus the exact longitudinal current is not to be approximated by \(F_1 K_{N,\parallel}/m_N\) when a percent-level relative accuracy on this small component is required. The Ward identity supplies the exact free on-shell longitudinal component.

Two distinct slices are retained:

1. **Static impulse reference:** \(q_N^0=0\), \(\boldsymbol K_N\perp\boldsymbol q_N\). This is useful for isolating the transverse convection and magnetization operators. It is not exactly conserved with the physical nuclear transfer \(q_A^0=E_R\ne0\).
2. **Energy-transfer-matched free on-shell slice:** \(q_N^\mu=q_A^\mu=(E_R,\boldsymbol q_A)\). The internal longitudinal momentum is fixed by
   \[
   K_{N,\parallel}
   =\frac{E_R(E_N'+E_N)}{2Q_A},
   \]
   equivalently by the exact expression implemented in energy_transfer_matched_internal_momentum. The free-nucleon Ward identity then holds with the physical \(q_A^\mu\).

The second slice is a kinematic consistency check, not a nuclear momentum distribution or a bound-nucleon energy-sharing prescription.

## 4. Exact-spinor comparison at the Xe-131 benchmark points

The exact Dirac--Pauli spinor current was compared with the displayed NR expansion for \(F_1=1\), \(F_2/F_1=-0.184\), and the two fixed-speed Xe-131 transfers:
\[
(Q_A,E_R)=(0.2209306022\ {\rm GeV},200\ {\rm keV}),
\quad
(0.2552681134\ {\rm GeV},267\ {\rm keV}).
\]
The free on-shell slice enforces \(q_N^0=E_R\). The transverse internal momentum is varied over \(0,50,100,200\) MeV.

| \(E_R\) | \(K_\perp\) | \(K_\parallel\) | Charge error | Transverse spatial error | Full four-current error |
|---:|---:|---:|---:|---:|---:|
| 200 keV | 0 MeV | 0.8558 MeV | 0.00538% | 0.6898% | 0.0927% |
| 200 keV | 50 MeV | 0.8570 MeV | 0.00710% | 0.8289% | 0.1194% |
| 200 keV | 100 MeV | 0.8606 MeV | 0.01308% | 1.2470% | 0.2108% |
| 200 keV | 200 MeV | 0.8748 MeV | 0.04584% | 2.9096% | 0.6978% |
| 267 keV | 0 MeV | 0.9911 MeV | 0.00957% | 0.9198% | 0.1424% |
| 267 keV | 50 MeV | 0.9925 MeV | 0.01182% | 1.0586% | 0.1726% |
| 267 keV | 100 MeV | 0.9966 MeV | 0.01943% | 1.4752% | 0.2731% |
| 267 keV | 200 MeV | 1.0129 MeV | 0.05917% | 3.1327% | 0.7846% |

Errors are Frobenius-norm relative differences, with the exact normalized spinor current in the denominator. The transverse spatial error is the relevant truncation diagnostic for the leading \(\Delta,\Sigma'\) matching. The larger relative error in the small longitudinal component is not used as a replacement for the exact continuity relation.

For all eight points, the exact free-nucleon Ward residual is below \(2\times10^{-12}\), the exact longitudinal-current/continuity residual is below \(2\times10^{-12}\), and \(|q_N^0-E_R|<2\times10^{-13}\) GeV. The corresponding regression is implemented in run_one_body_nr_matching_scan and test_one_body_nr_current_expansion.py.


## Production convention used downstream (2026-11-19)

The formal fixed-speed and P4 production slice is the energy-transfer-matched
one-body impulse prescription
\[
q_N^\mu=q_A^\mu=(E_R,\boldsymbol q_A),\qquad
t_N=t_A=-2m_AE_R.
\]
The static slice \(q_N^0=0\), \(t_N=-Q_A^2\), remains a diagnostic for
isolating transverse convection and magnetization operators; it is not the
formal production transfer. Neither slice is a complete bound-nucleon
many-body current.

Keep
\[
Q_A^2=|\boldsymbol q_A|^2=2m_AE_R+E_R^2,\qquad
t_A=-2m_AE_R
\]
separate. AFH \(y_A=(b_AQ_A/2)^2\) uses the spatial \(Q_A\), while the
mediator and formal nucleon form-factor arguments use \(t_A=t_N\).

The \(F_1^V,F_2^V\) symbols in the Pauli-reduction equations denote the
full universal \(u+d+s\) quark-current form factors:
\(F_1^V(0)=3\), \(F_2^V(0)=-0.552\). When these coefficients multiply the
paper's external \((g_1g_2g_{VN})^2\) prefactor, use
\[
\widehat F_i^V(t_N)=F_i^V(t_N)/3,\qquad
\widehat F_1^V(0)=1,\quad \widehat F_2^V(0)=-0.184.
\]
Equivalently, keep the full \(F_i^V\) and use \(g_{Vq}=g_{VN}/3\).
Do not combine full \(F_i^V(0)=3\) with an external \(g_{VN}\) prefactor.
This quark-current factor three is independent of the AFH raw-to-physical
response factor four.

The nuclear baseline remains the finite-size native AFH \(W_M(y_A)\);
the Dirac--Pauli nucleon form factors are an additional one-body current
layer and never replace or multiply away the AFH nuclear response.

## 5. What this closes, and what it does not

**Closed for P1:** the on-shell one-body Dirac--Pauli current has been decomposed into:
- Darwin--Foldy and spin-orbit charge terms;
- longitudinal convection, with the exact free on-shell continuity relation;
- transverse convection;
- transverse magnetization.

The exact spinor implementation and the leading NR expressions now have a pointwise regression at both Xe-131 benchmark transfers and four internal transverse momenta.

**Not closed:** the bound-nucleus current. A bound nucleon is not an independently on-shell external particle. Its energy transfer is not determined by \(\boldsymbol q_A\) alone; binding, the nuclear Hamiltonian, and interaction currents enter the many-body continuity equation. The free on-shell \(q_N^0=E_R\) slice must not be interpreted as a realistic bound-nucleon distribution. A fully consistent many-body vector current may require exchange currents. No off-shell form-factor prescription or two-body current has been silently introduced here.

Accordingly, P1 is complete only within the declared free on-shell one-body impulse approximation. The next step is P2: project the derived convection and magnetization operators onto the exact AFH spherical multipoles, including their signed \(\Sigma'\)-\(\Delta\) interference phase. P3 must then compare direct covariant, q-frame-rotated, and AFH multipole contractions before any full-current halo-fold claim.
