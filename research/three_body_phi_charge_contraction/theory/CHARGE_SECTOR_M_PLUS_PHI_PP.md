# Three-body VV to AFH M + Phi'': charge-multipole matching

**Status:** first amplitude-level charge-sector contraction; not the complete three-body nuclear response.

## 1. Why this is the correct first contraction

The three-body amplitude has the factorized form
\[
\mathcal M_3=\mathcal T_3^\mu J^N_\mu,
\]
where \(\mathcal T_3^\mu\) is the coherent two-diagram dark-matter current
already implemented in the four-component audit, and \(J_N^\mu\) is the
one-nucleon vector current.

The scalar-emission diagrams alter \(\mathcal T_3^\mu\), not the Lorentz
structure of the nucleon matrix element. We can therefore first match the
nucleon charge multipole onto AFH M and Phi'', then contract that charge
multipole with \(\mathcal T_3^0\). This isolates a mathematically well-defined
subset of the full four-current problem.

This is not a license to replace the full current by its time component. The
spatial current will be treated separately.

## 2. Momentum and sign conventions

- q_A^mu=P'^mu-P^mu is the four-momentum delivered to the nucleus.
- q_A=|boldsymbol q_A| is the spatial nuclear momentum transfer used by AFH
  and by the response grid.
- The scalar momentum k_s, the dark-matter external momentum difference,
  and internal propagator momenta are distinct. In particular, q_A is not
  the momentum in either virtual chi2 propagator.
- The nucleon form-factor convention is translated to
  q_A=P_N'-P_N. If a source instead defines q=P_N-P_N', the Pauli-term sign
  must be translated before matching. The final F1+2F2 combination below
  uses the AFH vector-charge convention.

## 3. Nucleon vector charge and the AFH multipole

The on-shell nucleon vector current is parameterized by Dirac and Pauli form
factors. Its nonrelativistic charge multipole contains the leading vector
charge operator and the spin-orbit correction. In the AFH convention this is
\[
\boxed{
\mathcal M_{JM}^{(V,C)} =
F_1^V(t)M_{JM}
+\frac{q_A^2}{4m_N^2}
\left[F_1^V(t)+2F_2^V(t)\right]
\left(\Phi''_{JM}-\frac12M_{JM}\right)
}
\tag{1}
\]

The Phi'' operator is the spin-orbit multipole. In the long-wavelength
limit its scalar component is proportional to
\[
\Phi''_{00}(0)\propto
\sum_i\boldsymbol\sigma_i\cdot\boldsymbol\ell_i.
\]
It is therefore a scalar nuclear response and does not vanish merely because
the nuclear ground-state spin is zero. It is distinct from the spin responses
Sigma', Sigma'' and from the orbital-current response Delta.

Equation (1) is the vector-charge multipole expansion; it is not the
nonrelativistic reduction of the entire J_N^mu. The spatial convection and
magnetization currents generate additional multipoles.

## 4. Three-body coefficient map

Let
\[
r_2(t)=\frac{F_2^V(t)}{F_1^V(t)},\qquad
\eta(q_A,t)=\frac{q_A^2}{4m_N^2}\left[1+2r_2(t)\right].
\]
Equation (1) becomes
\[
\mathcal M_{JM}^{(V,C)}
=F_1^V(t)\left[
\left(1-\frac{\eta}{2}\right)M_{JM}
+\eta\Phi''_{JM}
\right].
\]
Thus
\[
C_M=F_1^V(1-\eta/2),\qquad
C_{\Phi''}=F_1^V\eta.
\]

For a fixed three-body phase-space point x, the charge-sector amplitude is
\[
\mathcal M_{3,C}(x)=
\mathcal T_3^0(x)F_1^V(t)
\left[
(1-\eta/2)M_A(q_A)+\eta\Phi_A''(q_A)
\right].
\]
The same \(\mathcal T_3^0(x)\) multiplies both nuclear charge multipoles.
After the dark-matter spin average and three-body phase-space integration,
\[
\begin{aligned}
\mathcal W_C^{(3)}(q_A)\propto I_{00}(q_A)|F_1^V|^2
\Big[&
(1-\eta/2)^2W_M^{00}\\
&+2(1-\eta/2)\eta W_{M\Phi''}^{00}\\
&+\eta^2W_{\Phi''}^{00}
\Big].
\end{aligned}
\tag{2}
\]

The normalized correction to the W_M-only charge baseline is
\[
\boxed{
R_C(q_A)=
(1-\eta/2)^2
+2(1-\eta/2)\eta\frac{W_{M\Phi''}^{00}}{W_M^{00}}
+\eta^2\frac{W_{\Phi''}^{00}}{W_M^{00}}
}
\tag{3}
\]

This is the requested amplitude-level contraction for the M+Phi'' charge
sector. It is not obtained by multiplying W_Phi''/W_M by a kinematic estimate.

## 5. Why the chi2 width cancels in this ratio

At fixed q_A, all three-body propagator and scalar-emission dependence in
this restricted sector is inside the common factor I_00. It multiplies
W_M, W_MPhi'', and W_Phi'' through the same T_3^0.

Consequently I_00 cancels in Eq. (3). The charge-sector ratio is independent
of whether the existing chi2 denominator is evaluated with zero, pole, or
diagnostic running width. The absolute charge-sector kernel still changes
with the width.

This cancellation must not be generalized to the spatial-current sectors:
their coefficients involve T_3^i, and their interference structure is
different.

## 6. Numerical conventions and normalization

The response inputs are the raw AFH isoscalar Xe-131 quantities:
- W_M00_AFH,
- W_PhiPP_AFH,
- W_MPhiPP_AFH.

For Xe-131, the source manifest records the physical combined normalization
as 4 pi, comprising the equal-p,n factor of four and the AFH 4 pi/(2J+1)
factor for J=3/2. This common factor cancels in Eq. (3). It must not be
applied a second time.

The calculation uses m_N=0.939 GeV and m_A=131u, with
u=0.93149410242 GeV.

## 7. Finite-t Pauli-form-factor uncertainty

The finite-t model-specific F2^V(t)/F1^V(t) is not fixed in the current
project. The numerical audit therefore reports
F2/F1 in {0,-0.14,-0.15,-0.17}. The zero case is a point-Dirac diagnostic.
The nonzero values are low-momentum sensitivity benchmarks only. They are
not a finite-t form-factor fit, and electromagnetic magnetic moments are
not substituted for the universal light-flavour/baryon current.

## 8. Results at the existing three-body benchmark points

Using local 8-point polynomial interpolation of the 0.25-MeV AFH grid and
F2/F1=-0.15:

| Three-body benchmark | q_A | W_Phi''/W_M | W_MPhi''/W_M | R_C | Change |
|---|---:|---:|---:|---:|---:|
| E_R=200 keV | 220.9306 MeV | 0.03719 | -0.19182 | 0.98664069 | -1.33593% |
| E_R=267 keV | 255.2681 MeV | 23.84080 | -4.63013 | 0.87210768 | -12.78923% |

For the E_R=267 keV point, changing the illustrative F2/F1 scenario from
-0.17 to -0.14 changes the correction from about -12.05% to -13.10%.
Setting F2=0 gives about -17.92%.

The exact AFH second W_M minimum is a separate point:
\[
q_A=256.271867617\ {\rm MeV},\qquad E_R=269.1038976\ {\rm keV}.
\]
Using the exact selected-point response values gives R_C=0.96881984, or
-3.11802%, for F2/F1=-0.15. The correction changes rapidly across this
diffraction structure; evaluating only at the exact minimum would not
reproduce the 267-keV three-body point.

On the 0.25-MeV grid, over 0.2<=q_A<=0.3 GeV, the sampled F2/F1=-0.15
correction ranges from about -16.08% at q_A=255.75 MeV to +11.37% at
q_A=256.75 MeV. These are grid-sampled extrema, not a continuous
minimization.

## 9. What is and is not established

Established by this calculation:
1. The AFH M, Phi'', and M-Phi'' charge responses have been combined with
   the amplitude-level coefficients.
2. The three-body temporal kernel from PR #53 has been attached to the
   charge-sector contraction at the same benchmark recoil points.
3. The response correction is independent of the chi2 width at fixed q_A
   in this charge-only sector.
4. The correction can reach the ten-percent level near the second W_M
   diffraction structure for the illustrative F2/F1 scenarios.

Not established:
- The native Mathematica Phi'' cross-check from PR #54 remains pending.
  Until it passes, the AFH interference sign and normalization remain
  provisional.
- No spatial-current T_3^i contraction has been done.
- No Sigma', Sigma'', Delta, or Phi-tilde-prime coefficient map has been
  computed.
- No absolute cross section, halo integral, natural-xenon isotope sum,
  detector response, or LZ likelihood is produced.

## 10. Next calculation

The next step is to reduce the full spatial nucleon current and contract
T_3^i with the magnetic-spin and convection-current multipoles. This will
determine the phase-space-dependent coefficients of Sigma', Sigma'', and
Delta, and whether the spinful Xe-129 and Xe-131 isotopes need to be included
in the final natural-xenon spectrum.
