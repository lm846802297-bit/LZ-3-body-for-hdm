# Xenon isotope mass-scheme sensitivity audit

Date: 2026-11-11

## Scope

The existing joint response and three-body calculation uses
\[
m_A=A\,u,\qquad u=0.93149410242~\mathrm{GeV}.
\]
This audit compares that historical mass-number approximation with an
isotope-specific nuclear mass reconstructed from NIST relative atomic masses:
\[
m_A^{\rm nuc}\simeq
\left[M_{\rm atom}(A)-54m_e\right]u.
\]
The total electronic binding energy (order 0.1 MeV for xenon) is neglected;
its relative correction to a 120 GeV nuclear mass is below \(10^{-6}\).
The detector-mass normalization continues to use the NIST standard atomic
weight 131.293 g/mol, which is an atomic—not nuclear—mass quantity.

NIST source:
https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ascii=ascii&ele=Xe

## 1. Mass and momentum shifts

Across the nine naturally occurring isotopes, the NIST nuclear-mass
prescription is about 0.093–0.100% below \(A u\). Consequently,
\[
q_{\rm response}=\sqrt{2m_AE_R}
\]
decreases by about half that relative amount. The absolute shift is small,
but the response can be steep near a diffraction minimum.

The abundance-weighted response-only sums over the seven isotopes with
available GCN/JJ55 density matrices change as follows:

| \(E_R\) [keV] | GCN: \(R_{\rm NIST}/R_{Au}\) | JJ55: \(R_{\rm NIST}/R_{Au}\) |
|---:|---:|---:|
| 101 | 0.99785 | 0.99010 |
| 200 | 1.00646 | 1.00641 |
| 267 | 1.01309 | 1.01723 |
| 542 | 1.03562 | 1.04152 |

These are response-only sums \(\sum_A x_A\mathcal R_A\), not event rates.
The isotope-specific response ratios can differ more strongly near an
individual shell-model minimum.

## 2. Three-body threshold shift

For \(m_{\chi_1}=1\) TeV and \(m_s=0.3\) MeV, the threshold is obtained from
\[
W_{\max}^2(E_R,v_{\min})=(m_{\chi_1}+m_s)^2.
\]

For Xe-136 at the first dip point:

| Mass prescription | \(m_A\) [GeV] | \(q_{\rm response}\) [MeV] | \(v_{\min}\) [km/s] |
|---|---:|---:|---:|
| \(A u\) | 126.683198 | 159.969 | 775.478 |
| NIST nuclear | 126.569175 | 159.897 | 775.806 |

The allowed interval below the \(v_{\rm esc}+v_E=776\) km/s cutoff therefore
shrinks from 0.522 km/s to 0.194 km/s. This is a 63% reduction in interval
width. Since both the halo PDF and the three-body phase space vanish toward
their respective endpoints, the 101 keV halo-folded rate can be much more
sensitive than the 0.09% mass shift might suggest.

The qualitative cutoff classification is unchanged: among the seven
available response isotopes, only Xe-136 is open at 101 keV for either mass
prescription. At 200, 267 and 542 keV, all seven available isotopes are open.

A direct halo-folded 101 keV cross-check was then performed for the only open
isotope, Xe-136, using the truncated SHM, \(m_V=0.1\) GeV,
\(\rho_\chi=0.3\) GeV/cm\(^3\), and the zero-width kernel:

| Mass prescription | GCN rate | JJ55 rate |
|---|---:|---:|
| \(A u\) | \(6.7922\times10^{-14}\) | \(7.0131\times10^{-14}\) |
| NIST nuclear | \(2.0727\times10^{-15}\) | \(2.1410\times10^{-15}\) |

Rates are in events/(kg day keV). Thus
\[
R_{\rm NIST}/R_{Au}=0.0305,
\]
a further suppression by a factor of about 32.8 relative to the \(A u\)
baseline. The 16- versus 32-node speed-integral difference for the NIST
prescription is \(6.62\times10^{-7}\). The \(A u\) result independently
reproduces the archived halo-fold output, providing a cross-check of the
local re-evaluation.

## 3. Fixed Earth-speed sensitivity at 101 keV

The NIST-mass halo fold was also repeated at three fixed lab speeds, keeping
\(v_0=220\) km/s and \(v_{\rm esc}=544\) km/s. This is a sensitivity bracket,
not a time-averaged annual-modulation calculation.

| \(v_E\) [km/s] | \(v_{\max}\) [km/s] | Open available isotopes | GCN rate | JJ55 rate |
|---:|---:|:---|---:|---:|
| 217 | 761 | none | 0 | 0 |
| 232 | 776 | Xe-136 | \(2.0727\times10^{-15}\) | \(2.1410\times10^{-15}\) |
| 247 | 791 | Xe-131, Xe-132, Xe-134, Xe-136 | \(9.7715\times10^{-9}\) | \(1.0205\times10^{-8}\) |

Rates are in events/(kg day keV), at \(m_V=0.1\) GeV and zero width.
The 247 km/s result is the full sum over all open isotopes with available
response data—not the Xe-136-only lower bound used in the initial diagnostic.
Xe-124 and Xe-126 remain kinematically closed throughout this speed bracket.

The rate changes by approximately
\[
\frac{R(v_E=247)}{R(v_E=232)}
\simeq 4.71\times10^6\quad(\mathrm{GCN}),
\qquad
4.77\times10^6\quad(\mathrm{JJ55}).
\]
At \(v_E=217\) km/s the channel is closed for every isotope in the available
set. The 16- versus 32-node speed-quadrature differences are below
\(6.7\times10^{-7}\) for the nonzero points.

This demonstrates that the 101 keV prediction under a hard escape-speed
cutoff is exceptionally sensitive to the instantaneous lab speed. A fixed
\(v_E=232\) value cannot be interpreted as an annual average near this
kinematic endpoint.

## 4. Interpretation and prescription

- Retain the \(m_A=A u\) result as the historical baseline so existing response
  and fixed-speed outputs remain reproducible.
- Carry the NIST nuclear-mass result as a separate physical-mass sensitivity.
- Do not infer that the mass uncertainty is negligible from its sub-per-mille
  relative size: the 101 keV cutoff point is exceptionally close to the
  maximum lab speed.
- Do not alter \(b_A\) to compensate for mass effects. The AFH oscillator
  length prescription remains unchanged.
- Xe-124 and Xe-126 remain absent from the shell-model response archive.
  Their thresholds are included in this audit, but their response/event-rate
  contributions are not inferred.

## 5. Reproducibility

- isotope_mass_schemes.py: explicit \(A u\) and NIST nuclear-mass functions.
- run_isotope_mass_scheme_audit.py: response and \(v_{\min}\) comparison.
- tests/test_isotope_mass_schemes.py: threshold and mass-shift regression.
- results/isotope_mass_scheme_audit/isotope_mass_scheme_sensitivity.csv:
  isotope-by-isotope numerical output.

CI:
https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/42954180933
