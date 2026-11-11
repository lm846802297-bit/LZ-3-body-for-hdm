# \(\chi_2\to\chi_1s\) pole decay width

**Status:** derived-check; the analytic expression and its numerical implementation pass the unit tests listed below. This note is a conditional calculation, not yet a final statement about the full model, because the source manuscript does not specify whether \(\chi_{1,2}\) are Dirac or Majorana fields or whether additional decay channels are present.

## 1. Scope and assumptions

The vector--vector branch of the working manuscript contains

\[
\mathcal L_{\rm int}\supset g_2s\bar\chi_2\chi_1+\mathrm{h.c.}
\]

and inserts

\[
\Gamma_{\chi_2}=\Gamma(\chi_2\to\chi_1s)
\]

at the pole mass in the second internal-fermion propagator. The calculation below assumes:

1. \(\chi_1\) and \(\chi_2\) are Dirac spin-\(1/2\) fermions;
2. the transition is a pure scalar Yukawa interaction with coupling \(g_2\);
3. the scalar final state is the single state denoted by \(s\);
4. no other \(\chi_2\) decay channel contributes to the total width.

Under these assumptions the width below is both the partial width to \(\chi_1s\) and the total width used in the propagator. If other channels are open, the propagator must use the sum of all partial widths. If the fermions are Majorana, or if the interaction has a different chiral/CP structure, the Feynman rule and possible channel-counting factors must be re-derived before using this result.

All masses in the numerical code are in GeV; \(g_2\) is dimensionless.

## 2. Matrix element

Write

\[
M\equiv m_{\chi_2}=m_{\chi_1}+\Delta m.
\]

For the directed decay \(\chi_2(p_2)\to\chi_1(p_1)+s(k)\), the spin-averaged matrix element is

\[
\overline{|\mathcal M|^2}
=\frac{|g_2|^2}{2}
\operatorname{Tr}\!\left[(\slashed p_1+m_{\chi_1})(\slashed p_2+M)\right]
=2|g_2|^2(p_1\cdot p_2+m_{\chi_1}M).
\]

Using \(p_1\cdot p_2=(M^2+m_{\chi_1}^2-m_s^2)/2\), this becomes

\[
\boxed{
\overline{|\mathcal M|^2}
=|g_2|^2\left[(M+m_{\chi_1})^2-m_s^2\right].
}
\]

The hermitian-conjugate term supplies the conjugate transition; it is not an additional factor of two in this one directed Dirac decay amplitude.

## 3. Exact two-body width

The standard two-body formula is

\[
\Gamma=\frac{|\mathbf p_*|}{8\pi M^2}\overline{|\mathcal M|^2},
\qquad
|\mathbf p_*|=\frac{\lambda^{1/2}(M^2,m_{\chi_1}^2,m_s^2)}{2M},
\]

where the dimensionful Källén function is

\[
\lambda(x,y,z)=x^2+y^2+z^2-2xy-2xz-2yz.
\]

Therefore

\[
\boxed{
\Gamma_{\chi_2\to\chi_1s}
=\frac{|g_2|^2}{16\pi M^3}
\lambda^{1/2}(M^2,m_{\chi_1}^2,m_s^2)
\left[(M+m_{\chi_1})^2-m_s^2\right].
}
\tag{1}
\]

The channel is open only if

\[
\boxed{\Delta m>m_s.}
\]

At and below threshold the partial width is zero.

### Numerically stable form

For \(M=m_{\chi_1}+\Delta m\), factorize the Källén function:

\[
\begin{aligned}
\lambda(M^2,m_{\chi_1}^2,m_s^2)
&=\left[M^2-(m_{\chi_1}+m_s)^2\right]
  \left[M^2-(m_{\chi_1}-m_s)^2\right]\\
&=(\Delta m^2-m_s^2)
  \left[(2m_{\chi_1}+\Delta m)^2-m_s^2\right].
\end{aligned}
\]

Substitution gives the equivalent expression used by the code:

\[
\boxed{
\Gamma_{\chi_2\to\chi_1s}
=\frac{|g_2|^2}{16\pi(m_{\chi_1}+\Delta m)^3}
\sqrt{\Delta m^2-m_s^2}
\left[(2m_{\chi_1}+\Delta m)^2-m_s^2\right]^{3/2}.
}
\tag{2}
\]

This factorized form avoids subtracting nearly equal quantities of order \(m_{\chi_1}^4\) when \(m_{\chi_1}\) is at the TeV scale and \(\Delta m,m_s\) are at the keV--MeV scale.

## 4. Heavy-fermion limit

For \(m_{\chi_1}\gg\Delta m,m_s\), Eq. (2) reduces to

\[
\boxed{
\Gamma_{\chi_2\to\chi_1s}
\simeq\frac{|g_2|^2}{2\pi}
\sqrt{\Delta m^2-m_s^2}.
}
\tag{3}
\]

The approximation retains the exact threshold factor. It must not be used to continue the width into the closed region \(m_s\geq\Delta m\).

## 5. Numerical benchmarks

For the manuscript's reference dark-matter mass

\[
m_{\chi_1}=1\;\mathrm{TeV},\qquad \Delta m=1\;\mathrm{MeV},
\]

the exact result is:

| \(m_s\) | Channel | \(\Gamma_{\chi_2}/|g_2|^2\) |
|---:|:---:|---:|
| 200 keV | open | 155.9391263 keV |
| 300 keV | open | 151.8239116 keV |
| 360 keV | open | 148.4837480 keV |
| 300 MeV | closed | 0 |
| 360 MeV | closed | 0 |

For \(m_s=300\,\mathrm{keV}\), the coupling dependence is:

| \(|g_2|\) | \(\Gamma_{\chi_2}\) |
|---:|---:|
| 0.1 | 1.5182391 keV |
| 1 | 151.8239116 keV |
| 2 | 607.2956463 keV |
| 3 | 1366.4152042 keV |

At the benchmark \((m_{\chi_1},\Delta m,m_s,|g_2|)=(1\,\mathrm{TeV},1\,\mathrm{MeV},300\,\mathrm{keV},1)\), Eq. (3) gives 151.8241393 keV. Its relative excess over the exact result is \(1.5000\times10^{-6}\).

### Consequence for the Fig. 2 mass-label audit

For \(\Delta m=1\,\mathrm{MeV}\), a literal label \(m_s=300\,\mathrm{MeV}\) or \(360\,\mathrm{MeV}\) makes \(\chi_2\to\chi_1s\) kinematically closed. The corresponding keV interpretations are open and give the nonzero widths in the table. For \(\Delta m=10\,\mathrm{MeV}\), \(m_s=300\,\mathrm{MeV}\) is also closed.

This is a kinematic consistency check, not proof of which unit was used to generate the original figure. The original plot input/script is still needed to distinguish an incorrect legend from an incorrect numerical input.

## 6. Use in the Breit--Wigner propagator

The working manuscript uses

\[
\frac{1}{W^2-m_{\chi_2}^2+i m_{\chi_2}\Gamma_{\chi_2}},
\qquad W^2=(p'+k)^2.
\]

For each parameter point, the pole width must be recomputed using that point's \(m_s,\Delta m,g_2\). The condition \(W_{\max}<m_{\chi_2}\) excludes an on-shell intermediate \(\chi_2\), but it does not by itself prove that the finite-width term is numerically irrelevant near the pole.

The plotted coupling combination \((g_1g_2g_{VN})^2\) does **not** determine \(|g_2|\) separately. Since \(\Gamma_{\chi_2}\propto|g_2|^2\), a finite-width reproduction requires an independent value of \(|g_2|\) (or an additional model relation fixing it). The value \(151.8239\,\mathrm{keV}\) is therefore the conditional coefficient at \(|g_2|=1\), not a unique width implied by the coupling-product benchmark.

## 7. Reproducibility

Implementation:

- calculations/chi2_decay_width.py
- tests/test_chi2_decay_width.py

Run the eight standard-library unit tests from the repository root:

~~~bash
python -m unittest discover -s tests -v
~~~

Run the reference benchmark:

~~~bash
python calculations/chi2_decay_width.py \
  --mchi1 1000 --delta-m 0.001 --ms 0.0003 --g2 1
~~~

The implementation returns GeV internally and prints the width in both GeV and keV. It uses the factorized exact expression and separately prints the heavy-limit approximation. The tests cover the benchmark value, \(|g_2|^2\) scaling, complex-coupling modulus, threshold closure, the keV/MeV distinction, the heavy-limit accuracy, equivalence to the unfactorized Källén expression, and invalid mass inputs.

**Validation boundary:** these tests validate the algebraic implementation under the stated Dirac scalar benchmark. They do not settle the manuscript's unspecified Dirac/Majorana assignment, the full set of open channels, or the finite-width impact on the integrated three-body recoil spectrum.
