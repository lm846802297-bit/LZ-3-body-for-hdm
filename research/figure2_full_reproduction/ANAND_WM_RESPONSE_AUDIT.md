# Anand coherent nuclear response audit for Figure 2

Date: 2026-11-11

## 1. Exact response used by the manuscript

The original working-manuscript line used
\[
\mathcal R_A=\frac{4\pi}{2J_A+1}W_M^{00},
\qquad \mathcal R_A(0)=A^2,
\]
but that expression was inconsistent with the raw AFH v6.0 package normalization. The cross-audit established that
\[
\frac{4\pi}{2J_A+1}W_{M,\mathrm{AFH,v6}}^{00}(0)=\frac{A^2}{4}.
\]
The source manuscript has therefore been corrected on the active research branch to use the physical equal-proton/equal-neutron response
\[
\boxed{
\mathcal R_A^{\mathrm{phys}}(E_R)
=\frac{16\pi}{2J_A+1}W_{M,\mathrm{AFH,v6}}^{00}(y),
\qquad
y=\left(\frac{b_AQ}{2}\right)^2,
\qquad
Q=\sqrt{2m_AE_R+E_R^2},
\qquad
\mathcal R_A^{\mathrm{phys}}(0)=A^2 .
}
\]
The factor four is included exactly once, while the cross-section prefactor retains the physical per-nucleon coupling \(g_{VN}\). The commonly used \(y\simeq b_A^2m_AE_R/2\) is only the \(E_R\ll m_A\) approximation.

Source: \`paper-source/main.tex\`, Section “2 -> 3 cross section”, immediately before Eq. (radiative-recoil), citing Anand, Fitzpatrick and Haxton, arXiv:1308.6288.

This fixes the interpretation: the Figure 2 calculation uses the **isoscalar coherent-charge nuclear response** in the Anand et al. formalism, mapped to the physical equal-\(p,n\) nucleon coupling. A Helm form factor is not the source prescription and must not be substituted for it.

## 2. Notation: distinguish nuclear and dark-matter responses

In the Anand formalism, \(W_X^{\tau\tau'}(y)\) are nuclear response functions, while \(R_X^{\tau\tau'}\) denote dark-matter response functions built from the non-relativistic operator coefficients.

The manuscript's \(\mathcal R_A^{\mathrm{phys}}(E_R)\) is its own shorthand for the physical coherent nuclear factor multiplying the per-nucleon coupling \(g_{VN}^2\):
\[
\mathcal R_A^{\mathrm{phys}}(E_R)
=\frac{16\pi}{2J_A+1}W_{M,\mathrm{AFH,v6}}^{00}(y).
\]
It is not one of Anand's dark-matter response coefficients \(R_X^{\tau\tau'}\).

The superscript \(00\) selects the isoscalar-isoscalar channel. The raw AFH v6.0 package response obeys
\[
R_{\mathrm{AFH,raw}}(q)
=\frac{4\pi}{2J_A+1}W_{M,\mathrm{AFH,v6}}^{00}(y),
\qquad
R_{\mathrm{AFH,raw}}(0)=\frac{A^2}{4}.
\]
The physical equal-proton/equal-neutron response is four times this package-normalized response:
\[
R_A^{\mathrm{phys}}(q)=4R_{\mathrm{AFH,raw}}(q),
\qquad
R_A^{\mathrm{phys}}(0)=A^2.
\]
The factor four maps the AFH setter convention \(c_{\rm set}=2g_{VN}\) to the physical nucleon coupling \(g_p=g_n=g_{VN}\). It must appear exactly once, either in the response or in the amplitude-level coupling contraction, never in both.

## 3. Consequence for the Figure 2 spectral shape

The cross section factorizes as
\[
\frac{d\sigma_A}{dE_R}
\propto
\frac{\mathcal R_A(E_R)}
{(m_V^2+2m_AE_R)^2}
\times \text{three-body phase-space and matrix-element integral}.
\]

For a fixed target prescription, (\mathcal R_A(E_R)) is common to all (m_s), (\Delta m), and coupling benchmarks. Therefore, nuclear-response minima can generate common recoil-energy dips in otherwise different benchmark spectra. This is a useful diagnostic, but the locations and depths must be calculated from (W_M^{00}); they must not be identified with Helm zeros by visual coincidence.

For the approximate (m_A=122\,\mathrm{GeV}) Xe-131 diagnostic mass used elsewhere in this project, the visible dip locations near 101, 267, and 542 keV correspond approximately to
\[
q=\sqrt{2m_AE_R+E_R^2}
\simeq 157,\ 255,\ 364\ \mathrm{MeV},
\]
respectively. These are target points for a direct (W_M^{00}) comparison, not yet established response zeros.

## 4. Numerical inputs that are still not fixed by the manuscript text

The formula cites Anand et al., but the current source text does not specify the numerical nuclear-structure prescription needed to regenerate the curve:

1. The target isotope or isotope mixture. The diagnostic (m_A\simeq122\,\mathrm{GeV}) is approximately Xe-131, but the Figure 2 caption does not explicitly say that the calculation uses only Xe-131 rather than natural xenon.
2. (A), (J_A), and the oscillator length (b_A) used in (y).
3. The exact Xe one-body density matrix / shell-model interaction used to generate (W_M^{00}).
4. Whether the natural-xenon isotope abundances are summed at the event-rate level, or whether a single-isotope approximation is intended.
5. The numerical normalization check that the chosen implementation gives (\mathcal R_A(0)=A^2).

These are not interchangeable details. In particular, an isotope mixture can smear isotope-specific finite-(q) minima.

## 5. Implementation cross-check path

The public `dmscatter` implementation is based on the Anand/DMFormFactor framework and contains xenon density-matrix inputs for (^{128,129,130,131,132,134,136}\mathrm{Xe}), with GCN and/or JJ55 interactions depending on isotope.

In `src/nucresponse.f90`, nuclear-response term 1 is the (M_J\)-(M_J) product, i.e. the (W_M) channel. This is the relevant term for the manuscript's coherent-charge response. The implementation can therefore serve as an independent numerical cross-check once the isotope, interaction, (b_A), and normalization convention are fixed.

Important caveat: `examples/exampleXe.py` sets all 15 non-relativistic operator coefficients to the same nonzero value for both protons and neutrons. Its accompanying `test.xe131.dat` is a combined event-rate validation spectrum, not a pure (W_M^{00}) response curve. It must not be used as if it were the isolated response required here. A pure coherent (W_M^{00}) check must switch on only the (O_1) coefficient with equal proton and neutron couplings, and compare the extracted response after checking the package's normalization conventions.

Useful implementation references:
- https://github.com/ogorton/dmscatter/blob/master/src/nucresponse.f90
- https://github.com/ogorton/dmscatter/blob/master/examples/exampleXe.py
- https://github.com/ogorton/dmscatter/tree/master/targets/Xe

## 6. Corrected execution plan

1. Do not perform a Helm-versus-Anand model choice: the manuscript has already selected Anand (W_M^{00}).
2. Recover or explicitly choose the Xe isotope(s), (J_A), (b_A), and the density-matrix interaction.
3. Compute the AFH package W_M^{00}(y), verify (4\pi/(2J_A+1))W_M^{00}(0)=A^2/4, and then form the equal-p/n physical response with the factor of four; verify R_A(0)=A^2.
4. Compare the computed response's finite-(q) minima with the common dips in Figure 2.
5. Repeat for the relevant xenon isotopes and form the abundance-weighted natural-xenon rate if that is the intended LZ target.
6. Only after this nuclear factor is fixed, combine it with the three-body (W^2,z,\varphi_*) integral and halo-speed integral.

## Status

**Source identification: confirmed from the manuscript equation.**

**Numerical Xe-131 response reproduction: completed for the AFH v6.0 built-in default matrix and independently compared with the existing GCN/JJ55 dmscatter results.**

The AFH default result is a literature-defined reference prescription. It does not establish that the original Figure 2 used this exact isotope or matrix; the manuscript still does not identify the original isotope mixture.


## 7. AFH DMFormFactor v6.0 default Xe-131 calculation

The supplied official AFH v6.0 archive was inspected directly. Its source
`dmformfactor-V6.m` contains the built-in `sdgXe131` density matrix
(67 entries), selected by

```mathematica
SetIsotope[54,131,"default","default"]
```

This selects both the AFH default Xe-131 density matrix and the AFH default
oscillator prescription. The resulting length is

[
b_{131}=2.2923417985218975 mathrm{fm}.
]

### 7.1 AFH isoscalar normalization

The package call `ResponseNuclear[y,1,0,0]` returns the AFH isoscalar
`W_M^{00}`. Its isospin convention includes a factor one half in the
isoscalar nucleon operator. Consequently,

[
rac{4pi}{2J_A+1}W_{M,mathrm{AFH}}^{00}(0)
=rac{A^2}{4},
]

not (A^2). For the physical equal-proton/equal-neutron coupling in the
manuscript, the coherent response is four times the AFH package's
isoscalar-normalized response:

[
oxed{
mathcal R_A(q)
=4,rac{4pi}{2J_A+1}W_{M,mathrm{AFH}}^{00}(q)
}
]

up to the tiny overall correction associated with the finite decimal
precision of the tabulated density-matrix coefficients. We remove only that
constant offset by normalizing the response shape to its computed q=0 value:

[
mathcal R_A(q)=A^2
rac{W_{M,mathrm{AFH}}^{00}(q)}
     {W_{M,mathrm{AFH}}^{00}(0)}.
]

The direct source translation gives
((4pi/(2J_A+1))W_M^{00}(0)=4289.8959557), compared with
(A^2/4=4290.25), a relative difference (8.25	imes10^{-5}).
The normalized equal-p/n response satisfies (mathcal R_A(0)=17161).

This is the same physical convention as the existing dmscatter calculation,
which sums the four pp, pn, np, nn response channels. It is not correct to
compare the raw AFH package (W_M^{00}) to that four-channel sum without
the factor of four.

### 7.2 AFH default response minima

| Model | q_min [MeV] | E_R,min [keV] | R_min/R(0) |
|---|---:|---:|---:|
| AFH default | 157.93578 | 102.20672 | 1.23638e-5 |
| AFH default | 256.27187 | 269.10390 | 6.34070e-8 |
| AFH default | 365.06657 | 546.08690 | 1.56194e-7 |

The first three minima lie close to the Figure 2 dip regions near 101, 267,
and 542 keV. A fourth minimum occurs at approximately 1.022 MeV recoil,
outside the three-dip region considered here.

### 7.3 Comparison with GCN and JJ55

The AFH default, GCN and JJ55 minima have similar q locations, while their
depths are model dependent. In particular, the JJ55 minima are substantially
deeper than the AFH-default minima. This is a nuclear-structure uncertainty,
not a reason to tune (b_A).

At the two Figure 2 reference energies where the fixed-speed benchmark is
open, the same previously validated three-body integral (I_6) gives:

| E_R [keV] | Model | R_A | d sigma/dE_R [cm^2/keV] |
|---:|---|---:|---:|
| 267 | AFH default | 0.005598 | 1.38050e-35 |
| 267 | GCN | 0.004841 | 1.19396e-35 |
| 267 | JJ55 | 0.009210 | 2.27134e-35 |
| 542 | AFH default | 0.003151 | 2.34020e-36 |
| 542 | GCN | 0.003843 | 2.85431e-36 |
| 542 | JJ55 | 0.005094 | 3.78276e-36 |

The comparison holds the three-body kernel fixed at
(m_{chi_1}=1) TeV, (m_s=300) keV, (Delta m=450) keV,
(m_V=10) GeV, and (v=776) km/s; only the nuclear response changes.
At 101 keV the same benchmark is kinematically closed because its open
recoil interval begins at 109.1503 keV.

### 7.4 Reproducibility and remaining scope

The full 0--0.6 GeV q-grid, extracted 67-entry density matrix, AFH-source
Python translation, Mathematica runner, normalization audit, metadata,
minima, and regression tests are archived under
`research/afh_default_density_xe131/`. Six regression tests pass, including
selected 60-digit mpmath checks of the radial/angular kernel.

This closes the AFH-default Xe-131 response calculation. It does not yet
establish the original Figure 2 isotope mixture, compute the full
natural-xenon isotope-summed three-body event rate, or perform the final
halo-speed fold.
