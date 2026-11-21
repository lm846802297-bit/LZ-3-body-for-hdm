# VV nucleon current and Xe-131 \(\Phi''\) response: physical record

## 1. Purpose and conclusion

The purpose of this note is to determine whether the Xe-131 AFH spin-orbit
response changes the vector-charge part of the radiative three-body recoil
spectrum near the deep \(W_M\) minima.

The AFH response audit establishes that \(W_{\Phi''}^{00}\) remains nonzero
and can be much larger than \(W_M^{00}\) near the second mass-response
minimum. The mixed response \(W_{M\Phi''}^{00}\) is also nonzero.

The first charge-sector matching is now derived from the nonrelativistic
Dirac--Pauli vector charge. In the explicitly labelled zero-momentum
form-factor benchmark, the second \(W_M\) minimum receives a
\(-1.839\%\) correction from adding \(\Phi''\), and a combined
\(-2.991\%\) correction when the \(t_N/(8m_N^2)\) correction to the
\(M\) coefficient is also included. These are local Xe-131 charge-sector
benchmarks, not finite-\(t\) predictions or a complete natural-xenon rate.

The exact three-body time current \(\mathcal T_3^0\) factors out of the
relative \(M+\Phi''\) charge-sector ratio. The finite-\(t\) flavour
form factors and spatial-current responses \(\Sigma'\), \(\Sigma''\), and
\(\Delta\) remain to be completed.

## 2. Quark-to-nucleon vector-current matching

Define the exact nuclear four-momentum transfer and the one-nucleon
current transfer separately:
\[
q_A^\mu=P_A'^\mu-P_A^\mu,\qquad t_A=q_A^2=E_R^2-Q_A^2=-2m_AE_R,
\]
\[
q_N^\mu=k'^\mu-k^\mu,\qquad t_N=q_N^2.
\]
In the static one-body impulse approximation used for the first AFH
benchmark,
\[
q_N^0=0,\qquad \boldsymbol q_N=\boldsymbol q_A,\qquad
t_N=-Q_A^2=t_A-E_R^2.
\]
The equality of the spatial transfers is the impulse-approximation
identification; it does not make the exact four-transfers identical.

Use the Dirac--Pauli convention
\[
\boxed{
J_N^\mu(q_N)=
\bar u_N(k')
\left[
F_1^{V,N}(t_N)\gamma^\mu+
\frac{iF_2^{V,N}(t_N)}{2m_N}
\sigma^{\mu\nu}q_{N,\nu}
\right]u_N(k).
}
\]
The plus sign here is tied to \(q_N=k'-k\). Hoferichter, Menéndez,
and Schwenk use \(q=k-k'=-q_N\) and write the equivalent vertex with
\(-iF_2\sigma^{\mu\nu}q_\nu/(2m_N)\), see their Eq. (6). The sign must
not be changed without also changing the transfer convention.

For the AFH nuclear Fourier operators, the elastic-reference convention is
\(\boldsymbol q_{\rm AFH}=-\boldsymbol q_A\). In the radiative process,
do **not** identify this nuclear momentum with the full dark-matter
momentum change:
\[
\boldsymbol p_\chi'-\boldsymbol p_\chi
=-\boldsymbol q_A-\boldsymbol k_s.
\]
The AFH nuclear multipoles are evaluated at the spatial momentum flowing
through the one-nucleon current, \(|\boldsymbol q_{\rm AFH}|=|\boldsymbol q_A|
=|\boldsymbol q_N|\); the emitted scalar momentum belongs to the
three-body dark-matter kinematics, not to the nuclear Fourier argument.

For the universal light-flavour current
\[
J_V^\mu=\bar u\gamma^\mu u+\bar d\gamma^\mu d+\bar s\gamma^\mu s,
\]
isospin symmetry and quark number imply
\[
F_1^{V,p}(0)=F_1^{V,n}(0)=3.
\]
This justifies the equal proton/neutron charge benchmark
\(g_{VN}=3g_{Vq}\) at zero momentum transfer. It does **not** imply that
the Pauli form factor vanishes, nor does it determine either form factor's
finite-\(t\) shape.

### 2.1 Zero-momentum flavour benchmark

For the model's universal light-flavour current, use the flavour-separated
zero-momentum inputs
\[
F_2^{u/p}(0)=1.609,\qquad
F_2^{d/p}(0)=-2.097,\qquad
F_2^{s/p}(0)=-0.064.
\]
Thus
\[
F_2^{V,p}(0)=F_2^{u/p}+F_2^{d/p}+F_2^{s/p}=-0.552,
\qquad F_1^{V,p}(0)=3,
\]
and
\[
\boxed{F_2^{V,p}(0)/F_1^{V,p}(0)=-0.184.}
\]
In the isospin limit the same flavour sum gives the same neutron benchmark.

These are zero-momentum anchors, not finite-\(t_N\) form factors. At the
Xe-131 response minima, \(|t_N|=Q_A^2\) is not zero. The final quantitative
calculation therefore needs finite-momentum, flavour-separated
\(F_1^{V,N}(t_N)\) and \(F_2^{V,N}(t_N)\) with the sign convention above.
The numerical benchmark below holds the zero-momentum values fixed solely
to isolate the effect of the AFH nuclear responses. In the static prescription
\(t_N=-Q_A^2\), while the exact nuclear invariant is
\(t_A=t_N+E_R^2\).

Reference for the flavour-separated inputs: Bishara et al.,
[arXiv:1707.06998](https://arxiv.org/abs/1707.06998).
## 3. Which nuclear responses are being audited?

The official AFH v6.0 source exposes the relevant responses through
ResponseNuclear:

| AFH call | Response | Role |
|---|---|---|
| ResponseNuclear[y,1,0,0] | \(W_M^{00}\) | coherent vector-charge baseline |
| ResponseNuclear[y,4,0,0] | \(W_{\Phi''}^{00}\) | spin-orbit response |
| ResponseNuclear[y,7,0,0] | \(W_{M\Phi''}^{00}\) | mass--spin-orbit interference |

The superscript \(00\) denotes the AFH isoscalar/isospin component in both
slots. For a universal equal proton/neutron vector charge, this is the
appropriate first response sector.

\(\Phi''\) is a spin-orbit nuclear response. It is not the ordinary
spin-dependent \(\Sigma'\) or \(\Sigma''\) response and should not be
identified with the total nuclear spin. Its matrix element can be nonzero
for a nucleus whose response is not well represented by a simple coherent
mass operator.

## 4. AFH normalization

The AFH isoscalar convention has

\[
R_{M,\mathrm{AFH}}(0)
=\frac{4\pi}{2J_A+1}W_M^{00}(0)
\simeq\frac{A^2}{4}.
\]

For equal physical proton and neutron couplings, the factor of four is
applied once:

\[
R_X^{(p=n)}(q)
=4\,\frac{4\pi}{2J_A+1}W_X^{00}(q),
\quad X=M,\Phi'',M\Phi''.
\]

For Xe-131, \(J_A=3/2\), so the combined factor multiplying the AFH
response is \(4\pi\). The existing \(W_M\) archive additionally applies a
small q=0 shape correction, 1.0000825298069376, to remove the finite-decimal
rounding offset of the built-in density matrix and enforce
\(R_M(0)=A^2\). That correction is **not silently applied** to
\(W_{\Phi''}\) or \(W_{M\Phi''}\) in this study. The outputs therefore
contain both:

- raw equal-p/n physical responses, with the exact factor of four; and
- a separately labelled comparison normalization using \(W_M(0)\),
  useful for comparing shapes but not a replacement for the raw response.

This separation avoids turning an \(M\)-specific q=0 convention into an
unexplained rescaling of the other response functions.

## 5. Numerical implementation

### 5.1 Inputs

- Isotope: \(^{131}\mathrm{Xe}\), \(A=131\), \(Z=54\), \(J_A=3/2\),
  \(T_{\rm iso}=|A/2-Z|=11.5\).
- Density matrix: the built-in AFH v6.0 sdgXe131 matrix, 67 entries.
  The isoscalar normal-parity contributions used here contain 16 rank-0
  entries and 8 rank-2 entries.
- Oscillator length:

  \[
  b_A=\sqrt{\frac{41.467}{45A^{-1/3}-25A^{-2/3}}}
  =2.2923417985218975\;\mathrm{fm}.
  \]

- Response variable: \(y=(b_Aq_A/2)^2\), with \(q_A\) the spatial
  nuclear momentum transfer.
- Grid: 0--0.6 GeV, \(\Delta q_A=0.25\) MeV, 2401 points.

### 5.2 Matrix elements

The Python implementation translates the AFH v6.0 definitions of
PhiPPoverall, PhiPPsummand1--PhiPPsummand4, PhiPPJ,
BesselElementMinus, and BesselElementPlus, using the AFH Wigner 3j, 6j,
and 9j recoupling structure. The q-independent angular coefficients
are precomputed once; the finite sums and confluent hypergeometric functions
are evaluated over the full momentum grid.

The mass matrix elements are evaluated in the same convention as the
already archived AFH Xe-131 \(W_M\) implementation. The four archived
mass-response minimum amplitudes are reproduced by regression tests.

The responses are assembled as

\[
W_M^{00}=\frac14\sum_{J=0,2}|M_J|^2,
\qquad
W_{\Phi''}^{00}=\frac14\sum_{J=0,2}|\Phi''_J|^2,
\]

\[
W_{M\Phi''}^{00}=\frac14\sum_{J=0,2}M_J\Phi''_J,
\]

in the real, isoscalar AFH convention used by the package. In a rate
containing both operators, the corresponding cross contribution is
proportional to \(2 C_M C_{\Phi''}W_{M\Phi''}\); the coefficients
\(C_M\) and \(C_{\Phi''}\) are not determined by the nuclear response
calculation.

## 6. Xe-131 numerical results

The table reports the raw equal-p/n physical response divided by \(A^2\),
with no \(M\)-only q=0 rescaling applied to the \(\Phi''\) or interference
columns.

| \(q_A\) (MeV) | \(E_R\) (keV) | \(R_M/A^2\) | \(R_{\Phi''}/A^2\) | \(R_{M\Phi''}/A^2\) | \(W_{\Phi''}/W_M\) |
|---:|---:|---:|---:|---:|---:|
| 157.936 | 102.207 | \(1.23628\times10^{-5}\) | \(1.67735\times10^{-4}\) | \(+4.09672\times10^{-6}\) | 13.568 |
| 256.272 | 269.104 | \(6.34018\times10^{-8}\) | \(7.34760\times10^{-6}\) | \(-9.27245\times10^{-8}\) | 115.889 |
| 365.067 | 546.087 | \(1.56181\times10^{-7}\) | \(3.52273\times10^{-7}\) | \(+5.62217\times10^{-8}\) | 2.256 |
| 499.372 | 1021.798 | \(1.67049\times10^{-8}\) | \(1.15290\times10^{-8}\) | \(-1.47428\times10^{-9}\) | 0.690 |

At the second mass minimum,

\[
\left.\frac{W_{\Phi''}}{W_M}\right|_{q_A=256.272\,\mathrm{MeV}}
=115.889.
\]

The interference-to-mass ratio there is

\[
\left.\frac{W_{M\Phi''}}{W_M}\right|_{q_A=256.272\,\mathrm{MeV}}
=-1.46249,
\]

while the normalized correlation

\[
\rho_{M\Phi''}
=\frac{|W_{M\Phi''}|}{\sqrt{W_MW_{\Phi''}}}
=0.13585.
\]

Thus the mass response is deeply suppressed at this momentum, but the
spin-orbit response is not. This is precisely why an \(M\)-only nuclear
response cannot by itself establish that all other responses are negligible.

The full-grid Cauchy--Schwarz check,

\[
|W_{M\Phi''}|^2\leq W_MW_{\Phi''},
\]

passes at all 2401 points. The largest normalized correlation is
0.9999998602 at \(q_A=470.75\) MeV.

## 7. Correct charge-sector matching for the radiative three-body current

A previous wording in this note incorrectly suggested that the subleading
elastic VV channel contains only \(\mathcal O_2\) and \(\mathcal O_5\),
while \(\mathcal O_3\) belongs only to AV. That statement is withdrawn.
The standard vector charge already contains the spin-orbit term that
generates the AFH \(\Phi''\) response.

Hoferichter, Menéndez, and Schwenk, PRD 102, 074018 (2020), Eq. (41),
give the nonrelativistically normalized one-nucleon vector charge. With
\(\boldsymbol K_N=(\boldsymbol k+\boldsymbol k')/2\),
\(\boldsymbol S_N=\boldsymbol\sigma_N/2\), and
\(\boldsymbol q_{\rm AFH}=-\boldsymbol q_N\), it can be written as
\[
\mathcal J_N^0 =
F_1^{V,N}(t_N)
+\frac{t_N}{8m_N^2}
  \left[F_1^{V,N}(t_N)+2F_2^{V,N}(t_N)\right]
+\frac{i}{2m_N^2}
  \left[F_1^{V,N}(t_N)+2F_2^{V,N}(t_N)\right]
  \boldsymbol S_N\cdot
  (\boldsymbol q_N\times\boldsymbol K_N).
\]
The normalization is
\(\mathcal J_N^\mu=\bar u_N(k')\Gamma_N^\mu u_N(k)/
[2\sqrt{E_N'E_N}]\). The scalar \(M\) coefficient in the first two
terms is HKS Eq. (41); the spin-orbit term is the one that generates
the \(\Phi''\) contribution made explicit in their Eq. (43).
The same paper states immediately below Eq. (41) that the spacelike
components do not contribute to its \(M\) and spin-orbit \(\Phi^{00}\)
responses. The latter is the vector-charge spin-orbit response represented
by AFH \(\Phi''\).

Matching this charge expansion to the AFH definition
\[
\Phi''_{JM;\tau}(q)=
i\sum_i
\left(\frac{\boldsymbol\nabla_i}{q}M_{JM}(q\boldsymbol x_i)\right)
\cdot
\left(\boldsymbol\sigma_i\times
\frac{\boldsymbol\nabla_i}{q}\right)t^\tau(i)
\]
gives, with the nonrelativistic external-state normalization fixed,
\[
\boxed{
c_M(t_N)=F_1^V(t_N)
+\frac{t_N}{8m_N^2}
 \left[F_1^V(t_N)+2F_2^V(t_N)\right],
}
\]
\[
\boxed{
c_{\Phi''}(t_N)=
\frac{Q_A^2}{4m_N^2}
\left[F_1^V(t_N)+2F_2^V(t_N)\right].
}
\]
The sign shown is for the current and AFH momentum conventions fixed in
Sec. 2. The finite-\(t_N\) argument belongs to the one-nucleon vertex;
\(Q_A=|\boldsymbol q_A|\) is the AFH spatial Fourier momentum.

For the radiative process
\[
\chi_1(p)+A(P_A)\to\chi_1(p')+A(P_A')+s(k_s),
\qquad q_A=P_A'-P_A=p-p'-k_s,
\]
the \(M+\Phi''\) **charge sector** is therefore
\[
\boxed{
\mathcal M_{M+\Phi''}^{(3)}
=\mathcal T_3^0(p,p',k_s)
\left[c_M(t_N)M+c_{\Phi''}(t_N)\Phi''\right].
}
\]
This is a genuine three-body result: the exact two-diagram,
finite-width \(\mathcal T_3^0\) is retained. Crucially, it multiplies both
charge operators in the same way. The spin-averaged three-body phase-space
factor
\[
I_{00}^{(3)}(E_R)=
\int d\Phi_3\,
\frac12\operatorname{Tr}
\left[\mathcal T_3^0\mathcal T_3^{0\dagger}\right]
\]
therefore cancels from the relative \(M+\Phi''\) correction at fixed
\(E_R\), provided the same isoscalar nucleon form factors are used for
both operators.

Define
\[
\eta(q_A)=\frac{c_{\Phi''}(t_N)}{c_M(t_N)}.
\]
The exact charge-sector ratio is
\[
\boxed{
Q_{\Phi''}(q_A)=
1+2\eta\frac{W_{M\Phi''}}{W_M}
+\eta^2\frac{W_{\Phi''}}{W_M}.
}
\]
This result does **not** require another three-body phase-space integration
for the relative correction. The absolute spectrum still requires the
existing \(I_{00}^{(3)}(E_R)\), mediator propagator, halo fold, and
detector treatment.

This factorization applies only to the \(M+\Phi''\) vector-charge sector.
The spatial current \(\mathcal T_3^i J_{N,i}\) can generate other nuclear
responses, including convection/orbital and magnetization/spin responses.
It must be matched separately before calling the result a complete
three-body nuclear calculation.

The elastic identity
\(\boldsymbol q\cdot\boldsymbol v^\perp=0\) must not be imposed on the
radiative process. In particular, the DM momentum change is
\(\boldsymbol q_\chi=\boldsymbol q_A+\boldsymbol k_s\), while the nuclear
Fourier momentum remains \(\boldsymbol q_A\). The scalar momentum and the
off-shell \(\chi_2\) propagators remain inside \(\mathcal T_3^\mu\).

## 8. First numerical charge-sector correction: zero-momentum benchmark

For a controlled first calculation, hold the flavour form factors at their
zero-momentum anchors,
\[
F_1^V=3,\qquad F_2^V=-0.552,\qquad F_1^V+2F_2^V=1.896,
\]
and use \(m_N=0.938918\) GeV. This is a diagnostic benchmark, not a
finite-\(t\) prediction.

The new script
\`research/afh_vv_phi_xe131/phi_charge_response_match.py\`
evaluates \(c_M\), \(c_{\Phi''}\), \(Q_{\Phi''}\), and the combined response
on the full 2401-point AFH grid and at the four exact selected minima.
It checks the Cauchy--Schwarz inequality and positivity of the combined
charge response at every point.

Recoil energies use the AME2020 Xe-131 neutral-atom mass converted to the
bare nuclear mass with CODATA-2022 constants. At the second \(W_M\) minimum,
\[
q_A=256.271867617\ {\rm MeV},\qquad
E_R=269.3595249\ {\rm keV},
\]
the zero-momentum benchmark gives
\[
c_M=2.98234390,\qquad
c_{\Phi''}=0.03531221,\qquad
\eta=0.01184042.
\]
Using the exact AFH selected-point responses,
\[
\frac{W_{\Phi''}}{W_M}=115.8894642,\qquad
\frac{W_{M\Phi''}}{W_M}=-1.46248999,
\]
one obtains
\[
\boxed{Q_{\Phi''}=0.9816142,}
\]
i.e. a \(-1.839\%\) correction relative to the same
nonrelativistically normalized \(M\)-only charge response. The \(t_N/(8m_N^2)\) Darwin--Foldy correction to
the \(M\) coefficient itself is another \(-1.174\%\) in the rate relative
to \(F_1^V(0)^2W_M\). Combining these two effects gives
\[
\boxed{
\frac{c_M^2W_M+2c_Mc_{\Phi''}W_{M\Phi''}
+c_{\Phi''}^2W_{\Phi''}}{F_1^V(0)^2W_M}
=0.9700939,
}
\]
or \(-2.991\%\) relative to the leading point-charge \(F_1(0)^2W_M\)
benchmark at this selected point.

The full 0--0.6 GeV grid also shows a rapid local variation around the
deep \(W_M\) cancellation: with the same zero-\(t\) form-factor anchors,
the largest sampled negative and positive \(Q_{\Phi''}-1\) are about
\(-13.61\%\) at \(q_A=255.75\) MeV and \(+11.50\%\) at
\(q_A=256.75\) MeV. The corresponding recoil energies are 268.2636 and
270.3656 keV. These are local ratios to a very small \(W_M\)
baseline, not global event-rate changes. The absolute matched response
remains nonnegative; the rapid sign change follows the signed
\(M\)-\(\Phi''\) interference as the \(W_M\) amplitude passes through its
deep minimum.

The four exact selected-point results are:

| \(q_A\) (MeV) | \(E_R\) (keV) | \(Q_{\Phi''}-1\) | Combined vs. \(F_1(0)^2W_M\) |
|---:|---:|---:|---:|
| 157.935778 | 102.303812 | +0.324% | -0.124% |
| 256.271868 | 269.359525 | -1.839% | -2.991% |
| 365.066569 | 546.605635 | +1.872% | -0.547% |
| 499.371886 | 1022.768406 | -0.663% | -5.053% |

These numbers answer the first charge-sector question, not the full
natural-xenon question. Finite-\(t\) flavour-separated \(F_1^V(t_N)\) and
\(F_2^V(t_N)\) are still required. In addition, the Xe-131 spatial-current
responses and the corresponding responses of the other abundant xenon
isotopes remain to be matched and calculated.


## 9. Two-body vector currents

The cited chiral EFT analysis finds that, through its \(\mathcal O(p^3)\)
counting, the vector two-body current appears in the AV channel rather than
the VV channel. This supports not making a two-body VV calculation the first
priority. It is not a statement that all higher-order or model-specific
multi-nucleon effects vanish.

## 10. Numerical status and limitations

- Python implementation and seven regression tests: run locally; PASS.
- 2401-point Cauchy--Schwarz response check: PASS.
- Four \(M\)-response minimum amplitudes: reproduce the archived AFH
  minima.csv values.
- 60-digit mpmath spot checks of the rank-0/rank-2 \(\Phi''\) amplitudes
  at the four selected minima: relative differences from the SciPy double
  implementation are below \(2.2\times10^{-15}\).
- Native AFH Mathematica export and pointwise comparison: **PASS** over 2401
  Xe-131 grid points with no interpolation; tolerances are \(rtol=2\times10^{-8}\)
  and \(atol=2\times10^{-10}\). Maximum scaled differences are
  \(3.80\times10^{-9}\) for \(W_M\), \(3.52\times10^{-11}\) for \(W_{\Phi\prime\prime}\), and
  \(9.05\times10^{-10}\) for \(W_{M\Phi\prime\prime}\). This validates the response
  implementation on this grid, not finite-\(t\) nucleon form factors or the full
  three-body spectrum.
- No F1/F2-dependent three-body coefficient, full three-body cross section,
  natural-xenon sum, halo fold, detector response, or manuscript edit is
  included.

## References

1. N. Anand, A. L. Fitzpatrick, and W. C. Haxton, “Model-independent
   analytic response functions for dark matter direct detection,”
   [arXiv:1308.6288](https://arxiv.org/abs/1308.6288), especially the
   definition of \(\Phi''\) in Eq. (51).
2. M. Hoferichter, J. Menéndez, and A. Schwenk, “Coherent elastic
   neutrino-nucleus scattering: EFT analysis and nuclear responses,”
   Phys. Rev. D 102, 074018 (2020),
   [DOI: 10.1103/PhysRevD.102.074018](https://doi.org/10.1103/PhysRevD.102.074018),
   especially Eqs. (6) and (41) and the discussion immediately following
   Eq. (41).
3. M. Hoferichter, P. Klos, and A. Schwenk, “Chiral power counting of one-
   and two-body currents in direct detection of dark matter,”
   [arXiv:1503.04811](https://arxiv.org/abs/1503.04811), for the
   vector-current form factors and NREFT matching discussion.
4. R. J. Hill and M. P. Solon, “Standard Model anatomy of WIMP dark matter
   direct detection. II. QCD analysis and hadronic matrix elements,”
   [arXiv:1409.8290](https://arxiv.org/abs/1409.8290), for the flavour
   decomposition of vector Dirac and Pauli form factors.
