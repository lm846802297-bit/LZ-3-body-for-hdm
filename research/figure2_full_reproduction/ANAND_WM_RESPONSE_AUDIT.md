# Anand coherent nuclear response audit for Figure 2

Date: 2026-11-11

## 1. Exact response used by the manuscript

The working manuscript defines the nuclear factor explicitly as

\[
\boxed{
\mathcal R_A(E_R)=\frac{4\pi}{2J_A+1}W_M^{00}(y),
\qquad
y=\frac{b_A^2m_AE_R}{2},
\qquad
\mathcal R_A(0)=A^2 .
}
\]

Source: `paper-source/main.tex`, Section “2 -> 3 cross section”, immediately before Eq. (radiative-recoil), citing Anand, Fitzpatrick and Haxton, arXiv:1308.6288.

This fixes the interpretation: the Figure 2 calculation uses the **isoscalar coherent-charge nuclear response** (W_M^{00}) in the Anand et al. formalism. A Helm form factor is not the source prescription and must not be substituted for it.

## 2. Notation: distinguish nuclear and dark-matter responses

In the Anand formalism, (W_X^{\tau\tau'}(y)) are nuclear response functions, while (R_X^{\tau\tau'}) denote dark-matter response functions built from the non-relativistic operator coefficients.

The manuscript's (mathcal R_A(E_R)) is its own shorthand for the normalized nuclear factor
\[
\mathcal R_A(E_R)=\frac{4\pi}{2J_A+1}W_M^{00}(y),
\]
not one of Anand's dark-matter response coefficients (R_X^{\tau\tau'}).

The superscript (00) selects the isoscalar-isoscalar channel. This is consistent with the manuscript's equal proton and neutron vector couplings, (g_p=g_n=g_{VN}). At zero momentum transfer, the stated normalization is (\mathcal R_A(0)=A^2).

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
3. Compute (W_M^{00}(y)) alone and verify (\mathcal R_A(0)=A^2).
4. Compare the computed response's finite-(q) minima with the common dips in Figure 2.
5. Repeat for the relevant xenon isotopes and form the abundance-weighted natural-xenon rate if that is the intended LZ target.
6. Only after this nuclear factor is fixed, combine it with the three-body (W^2,z,\varphi_*) integral and halo-speed integral.

## Status

**Source identification: confirmed from the manuscript equation.**

**Numerical (W_M^{00}) reproduction: not yet completed.**

No claim is made here that the visible dips have already been reproduced, or that the original plotting input used a particular Xe isotope or shell-model interaction.
