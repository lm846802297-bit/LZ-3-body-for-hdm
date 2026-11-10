# Figure 2 independent kinematic check

Date: 2026-11-11

## Question

Figure 2 of the manuscript labels two curves as \(m_s=360\,\mathrm{MeV}\) and \(m_s=300\,\mathrm{MeV}\), while the model section assumes a sub-MeV scalar. We test whether the printed three-body kinematics permit these masses, and whether the same curve labels are kinematically plausible if the units are keV.

## Source equation

The manuscript defines
\[
W_{\min}^2=(m_{\chi_1}+m_s)^2
\]
and
\[
W_{\max}^2=m_{\chi_1}^2+
2p_{\chi_1}\sqrt{2m_AE_R+E_R^2}
-2(E_{\chi_1}+m_A)E_R.
\]
At fixed recoil energy and incident speed, the three-body phase space is non-empty only if \(W_{\max}\geq W_{\min}\). Equivalently,
\[
m_s\leq m_s^{\max}(E_R,v)
=\sqrt{W_{\max}^2(E_R,v)}-m_{\chi_1}.
\]
We numerically maximize this bound over recoil energy to obtain the largest scalar mass allowed at a given incident speed.

## Inputs and scope

- \(m_{\chi_1}=1\,\mathrm{TeV}\), exactly as printed in Figure 2.
- \(m_A=122\,\mathrm{GeV}\), an approximate Xe-131 nuclear mass.
- Speeds \(544,600,770,776,800\,\mathrm{km/s}\) are used as a sensitivity grid. The manuscript does not state its halo distribution or maximum lab-frame speed, so none of these values is asserted to be the original plot input.
- The calculation uses the manuscript's printed \(W_{\max}\) expression directly.
- This is a phase-space/kinematic reproduction only. It does not calculate the differential event rate \(dR/dE_R\), its vertical normalization, the mediator propagator, nuclear response, or halo integral.

## Results

| Incident speed | Maximum allowed \(m_s\) | Recoil energy at maximum |
|---:|---:|---:|
| 544 km/s | 179.0 keV | 159.6 keV |
| 600 km/s | 217.8 keV | 194.1 keV |
| 770 km/s | 358.7 keV | 319.7 keV |
| 776 km/s | 364.3 keV | 324.7 keV |
| 800 km/s | 387.1 keV | 345.1 keV |

At \(v=776\,\mathrm{km/s}\), the recoil-energy intervals where phase space is open are:
- \(m_s=300\,\mathrm{keV}\): \(E_R\simeq109.2\)–\(654.7\,\mathrm{keV}\);
- \(m_s=360\,\mathrm{keV}\): \(E_R\simeq258.2\)–\(398.7\,\mathrm{keV}\).

At \(v=800\,\mathrm{km/s}\), they become:
- \(m_s=300\,\mathrm{keV}\): \(E_R\simeq95.3\)–\(750.1\,\mathrm{keV}\);
- \(m_s=360\,\mathrm{keV}\): \(E_R\simeq186.5\)–\(552.0\,\mathrm{keV}\).

The minimum incident speeds for any phase space are:
- \(m_s=200\,\mathrm{keV}\): \(v_{\min}^{\rm global}\simeq575.00\,\mathrm{km/s}\);
- \(m_s=300\,\mathrm{keV}\): \(v_{\min}^{\rm global}\simeq704.23\,\mathrm{km/s}\);
- \(m_s=360\,\mathrm{keV}\): \(v_{\min}^{\rm global}\simeq771.44\,\mathrm{km/s}\).

By contrast, \(m_s=300\,\mathrm{MeV}=300{,}000\,\mathrm{keV}\) and \(360\,\mathrm{MeV}=360{,}000\,\mathrm{keV}\) exceed the maximum kinematically available scalar mass by roughly three orders of magnitude. For all tested halo speeds, the phase-space interval is empty. The corresponding \(W^2\) integral in the manuscript's differential cross section must therefore vanish.

## Interpretation

This is strong independent evidence for the hypothesis that the two Figure 2 legend entries were intended to read 300 keV and 360 keV:

1. The keV interpretation is compatible with the sub-MeV model assumption.
2. At high incident speeds, the printed three-body kinematics allow 300 and 360 keV scalar emission in recoil-energy bands overlapping the broad region where the blue and black curves appear in Figure 2.
3. The MeV interpretation gives exactly zero three-body phase space and cannot produce the nonzero black/blue curves shown in the PDF under the stated \(m_{\chi_1}=1\) TeV halo-scattering setup.

The comparison of recoil-band edges is qualitative, not a fit to the plotted curve: the halo speed distribution used by the original plotting code is not supplied.

## Conclusion and decision

The independent kinematic check strongly favors a legend-unit typo (MeV written instead of keV) for the 300 and 360 benchmarks. It does not establish what the original numerical input file contained, and it does not reproduce the full event-rate spectra. The original Figure 2 PDF and its labels should remain unchanged until the author approves the correction or the original plotting inputs are recovered.

## Reproduction

Run:
\`\`\`bash
python kinematic_threshold.py
\`\`\`
Requires Python, NumPy, and SciPy. The script writes \`phase_space_threshold.csv\`.
