# VV nucleon current and Xe-131 \(\Phi''\) response: physical record

## 1. Purpose and conclusion

The purpose of this note is to establish whether the AFH Xe-131 spin-orbit
response can be neglected at the momentum transfers where the existing
coherent mass response has deep minima.

The calculation finds that it cannot be excluded on nuclear-response grounds:
\(W_{\Phi''}^{00}\) remains nonzero and is substantially larger than
\(W_M^{00}\) near the second mass-response minimum. The mixed response
\(W_{M\Phi''}^{00}\) is also nonzero.

The result is a **target-nucleus response audit**, not a prediction for the
three-body rate. In particular, it does not prove that the present VV
three-body amplitude couples to \(\Phi''\) with a coefficient large enough
to alter the recoil spectrum. That question requires a separate reduction of
the exact three-body current.

## 2. Quark-to-nucleon vector-current matching

For a flavour-diagonal quark vector current, the nucleon matrix element is
parameterized by Dirac and Pauli form factors. In the sign convention used in
the Hoferichter--Klos--Schwenk discussion,

\[
\langle N'|J_V^\mu|N\rangle
=\bar u_N'\left[
F_1^{V,N}(t)\gamma^\mu
-\frac{iF_2^{V,N}(t)}{2m_N}\sigma^{\mu\nu}q_\nu
\right]u_N,
\qquad t=q^2.
\]

The sign of the Pauli term depends on the definition of the transfer
four-vector. The implementation must use one convention consistently in the
nucleon vertex, the three-body amplitude, and the nuclear multipoles.

For the universal light-flavour current

\[
J_V^\mu=\bar u\gamma^\mu u+\bar d\gamma^\mu d+\bar s\gamma^\mu s,
\]

isospin symmetry and quark number imply

\[
F_1^{V,p}(0)=F_1^{V,n}(0)=3.
\]

This justifies the equal proton/neutron charge benchmark
\(g_{VN}=3g_{Vq}\) at zero momentum transfer. It does **not** imply that the
Pauli form factor vanishes, nor does it determine its finite-\(t\) shape.

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
These values are zero-momentum anchors, not finite-\(t\) form factors. At the
Xe-131 response minima, \(|t|=q_A^2\) is not zero, so the quantitative
three-body matching must use finite-momentum proton and neutron form factors
with one fixed sign convention. The numerical AFH response calculation in
this study computes nuclear matrix elements only; it does not insert a
constant \(F_2/F_1\) into a three-body rate.

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

## 7. Critical EFT caveat: elastic and three-body matching are different

A previous wording in this note incorrectly suggested that the subleading
elastic VV channel contains only \(\mathcal O_2\) and \(\mathcal O_5\),
while \(\mathcal O_3\) belongs only to AV. That statement is not correct
for the standard spin-1/2 WIMP--nucleon one-body matching.

In the VV reduction, Hoferichter, Klos, and Schwenk, Eq. (25), explicitly
obtain a nucleon-spin term proportional to

\[
\frac{F_2^{V,N}(t)}{4m_N^2}
\,\boldsymbol q\cdot(i\boldsymbol\sigma_N\times\boldsymbol P),
\qquad \boldsymbol P=\boldsymbol p_N+\boldsymbol p_N'.
\]

With elastic two-body kinematics this is part of the \(\mathcal O_3\)
spin-orbit structure. In the AFH basis, \(\mathcal O_3\) contributes to
the \(\Phi''\) and \(M\Phi''\) responses. AFH's operator definition
and WIMP coefficient decomposition are given in Eqs. (48) and (51) of
Anand, Fitzpatrick, and Haxton, [arXiv:1308.6288](https://arxiv.org/abs/1308.6288).

However, this does **not** license the shortcut

\[
F_2^V\longrightarrow c_3\longrightarrow W_{\Phi''}
\]

with an elastic coefficient copied unchanged into the present process.
For our reaction,

\[
\chi_1(p)+N(k)\to\chi_1(p')+N(k')+s(k_s),
\qquad q_A=k'-k=p-p'-k_s,
\]

so the DM momentum loss is \(p-p'=q_A+k_s\), not \(q_A\). In the
nonrelativistic limit define

\[
\boldsymbol v_{\rm av}^{(3)}
=\frac{\boldsymbol p+\boldsymbol p'}{2m_\chi}
-\frac{\boldsymbol k+\boldsymbol k'}{2m_N}.
\]

Energy-momentum conservation gives

\[
\boxed{
\boldsymbol q_A\cdot\boldsymbol v_{\rm av}^{(3)}
=E_s-\frac{(\boldsymbol p+\boldsymbol p')\cdot\boldsymbol k_s}
{2m_\chi},
}
\]

rather than the elastic identity \(\boldsymbol q\cdot\boldsymbol
v^\perp=0\). Although the cross product in \(\mathcal O_3\) is
insensitive to a component parallel to \(\boldsymbol q_A\), its
transverse part and its coefficient still depend on the emitted scalar
momentum and on the full off-shell \(\chi_2\) propagators.

The required matching is therefore:

1. retain both scalar-emission orderings coherently in the exact
   \(\mathcal T_3^\mu(p,p',k_s)\);
2. use the finite-width denominators and the same width prescription as the
   recoil calculation;
3. contract with the Dirac--Pauli nucleon current using finite-\(t\)
   \(F_1^{V,N}(t)\) and \(F_2^{V,N}(t)\);
4. perform the Pauli reduction and project the resulting coefficients onto
   the AFH \(M\), \(\Phi''\), \(M\Phi''\), \(\Sigma'\), \(\Sigma''\), and
   \(\Delta\) operators;
5. integrate the coefficient products over the complete three-body phase
   space before forming the recoil spectrum.

The nonzero finite-width Ward divergence is relevant to this reduction, but
it must not be mistaken for a direct rate multiplier: the target vector
current remains conserved, and only the complete contracted amplitude is
physical. Until this generalized matching is completed, the present
\(W_{\Phi''}\) result is a nuclear-structure input, not a numerical
three-body rate correction. The \(W_M\)-only spectrum remains a baseline,
not a demonstrated complete prediction.
## 8. Two-body vector currents

The cited chiral EFT analysis finds that, through its \(\mathcal O(p^3)\)
counting, the vector two-body current appears in the AV channel rather than
the VV channel. This supports not making a two-body VV calculation the first
priority. It is not a statement that all higher-order or model-specific
multi-nucleon effects vanish.

## 9. Numerical status and limitations

- Python implementation and seven regression tests: run locally; PASS.
- 2401-point Cauchy--Schwarz response check: PASS.
- Four \(M\)-response minimum amplitudes: reproduce the archived AFH
  minima.csv values.
- 60-digit mpmath spot checks of the rank-0/rank-2 \(\Phi''\) amplitudes
  at the four selected minima: relative differences from the SciPy double
  implementation are below \(2.2\times10^{-15}\).
- Native AFH Mathematica export and pointwise comparison: provided, but
  **pending execution**. It must not be reported as passed until the native
  output and comparator manifest are archived.
- No F1/F2-dependent three-body coefficient, full three-body cross section,
  natural-xenon sum, halo fold, detector response, or manuscript edit is
  included.

## References

1. N. Anand, A. L. Fitzpatrick, and W. C. Haxton, “Model-independent
   analytic response functions for dark matter direct detection,”
   [arXiv:1308.6288](https://arxiv.org/abs/1308.6288).
2. M. Hoferichter, P. Klos, and A. Schwenk, “Chiral power counting of one-
   and two-body currents in direct detection of dark matter,”
   [arXiv:1503.04811](https://arxiv.org/abs/1503.04811), especially the
   vector-current form factors and the NREFT matching discussion.
3. R. J. Hill and M. P. Solon, “Standard Model anatomy of WIMP dark matter
   direct detection. II. QCD analysis and hadronic matrix elements,”
   [arXiv:1409.8290](https://arxiv.org/abs/1409.8290), especially the
   flavour decomposition of vector Dirac and Pauli form factors.
