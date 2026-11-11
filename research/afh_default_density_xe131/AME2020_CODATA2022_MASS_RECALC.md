# Xenon nuclear-mass update: AME2020 + CODATA 2022

## Status and scope

This branch adopts an improved nuclear-mass prescription for new three-body
kinematics and the Xe-131 AFH partial halo-fold calculation. The historical
\`A_u\` and \`nist_nuclear\` schemes remain available unchanged so archived results
can still be reproduced.

The new scheme is

\[
m_A = \left[M_{\rm atom}(A)-Z\,m_e\right]u + B_e(Z)/c^2,
\]

with NIST neutral-atom isotope masses, the AME2020 total electronic-binding
correction, and CODATA-2022 constants. For xenon, \(Z=54\).

The approximate AME2020 binding-energy expression is

\[
B_e(Z)=14.4381 Z^{2.39}
       +1.55468\times10^{-6}Z^{5.35}\ {\rm eV},
\]

which gives

\[
B_e(54)=202378.277717\ {\rm eV}
       =202.378277717\ {\rm keV}.

The AME2020 paper presents this as an approximate binding-energy formula and
notes that the precision of calculated total electronic binding energies is
not established as precisely as the atomic-mass measurements. Accordingly,
this correction is included for a more complete mass conversion, but its
uncertainty is not silently treated as zero.
\]

CODATA-2022 constants used here are

\[
u c^2=931.49410372\ {\rm MeV},\qquad
m_e c^2=0.51099895069\ {\rm MeV},\qquad
m_e=5.485799090441\times10^{-4}u.
\]

The implementation is in
\`research/figure2_full_reproduction/isotope_mass_schemes.py\`, scheme name
\`ame2020_nuclear\`.

## Nine-isotope mass table

Masses are in GeV. Natural fractions are NIST atom fractions; all nine
fractions sum to one.

| Isotope | Atom fraction | New nuclear mass [GeV] |
|---|---:|---:|
| Xe-124 | 0.000952 | 115.390216249108 |
| Xe-126 | 0.000890 | 117.251719934394 |
| Xe-128 | 0.019102 | 119.113993406409 |
| Xe-129 | 0.264006 | 120.046651748374 |
| Xe-130 | 0.040710 | 120.976961446070 |
| Xe-131 | 0.212324 | 121.909922383801 |
| Xe-132 | 0.269086 | 122.840551153345 |
| Xe-134 | 0.104357 | 124.704694017030 |
| Xe-136 | 0.088573 | 126.569377379796 |

For Xe-131, the new mass is 121.909922383801 GeV. The legacy \(131u\)
approximation is 122.025727417020 GeV. The NIST-atom-minus-electron-rest-mass
scheme with the historical constants gives 121.909719835384 GeV. The new
mass therefore differs from that legacy NIST nuclear mass by about
202.548 keV; the small difference from 202.378 keV also includes the update
from CODATA-2018 to CODATA-2022 constants.

## Xe-131 three-body kinematics

Benchmark:

\[
m_{\chi_1}=1000\ {\rm GeV},\quad
m_s=300\ {\rm keV},\quad
\Delta m=450\ {\rm keV},\quad
v_{\max}=776\ {\rm km/s}.
\]

Using the new Xe-131 nuclear mass and the exact recoil momentum

\[
q_{\rm kin}=\sqrt{2m_AE_R+E_R^2},
\]

the global minimum incident speed is

\[
v_{\min}^{\rm global}=704.4577073\ {\rm km/s}
\]

at

\[
E_R=267.4011263\ {\rm keV}.
\]

At \(v=776\ {\rm km/s}\), the open recoil interval is

\[
109.3818258\ {\rm keV}
\le E_R \le
653.7041043\ {\rm keV}.
\]

The maximum available invariant mass is reached near
\(E_R=324.4726\) keV and satisfies

\[
\max(W_{\max}-m_{\chi_1})=364.02836\ {\rm keV}.
\]

Thus the \(\chi_2\) pole remains kinematically inaccessible for
\(\Delta m=450\) keV, with a gap of approximately 85.97164 keV.

At \(E_R=101\) keV and \(m_s=300\) keV, the isotope-specific thresholds are:

| Isotope | \(v_{\min}\) [km/s] |
|---|---:|
| Xe-124 | 810.299874 |
| Xe-126 | 804.208205 |
| Xe-128 | 798.260344 |
| Xe-129 | 795.334767 |
| Xe-130 | 792.451024 |
| Xe-131 | 789.592969 |
| Xe-132 | 786.775240 |
| Xe-134 | 781.228224 |
| Xe-136 | 775.805285 |

For the truncated SHM endpoint of 776 km/s, only Xe-136 is kinematically
open at this recoil energy. Its threshold lies only about 0.195 km/s below
the endpoint.

## Nuclear-response momentum convention

The AFH response convention follows the manuscript's nuclear variable

[
y=\frac{b_A^2m_AE_R}{2},
]

so the response momentum is

[
q_{\rm response}=\sqrt{2m_AE_R}.
]

The exact target mass-shell momentum

[
q_{\rm kin}=\sqrt{2m_AE_R+E_R^2}
]

is kept separately in the three-body kinematic limits and phase-space
construction. This distinction is intentional: the AME2020 recalculation
changes the nuclear mass in both expressions but does not silently change the
nuclear-response convention.

The existing Xe-131 response-substitution calculation also uses the
nonrelativistic (q_{\rm response}) definition. By contrast, the previously
archived AFH natural-xenon halo-fold samples record the exact (q_{\rm kin})
as their response input. That convention mismatch must be resolved before
those natural-xenon rates are treated as a strict like-for-like comparison.
The new Xe-131 partial calculation follows the manuscript definition above.

The AFH table itself is stored as a function of (q); its 2401-point grid and
the AFH default (b_A) prescription are unchanged. The new mass changes the
mapping from (E_R) to (q_{\rm response}), not the underlying AFH density
matrix.

## Rate calculation and numerical checks

\`run_ame2020_xe131_halo_partial.py\` computes the Xe-131 contribution to the
rate per kg of natural xenon, using the Xe-131 natural abundance 0.212324 and
the NIST abundance-weighted mean atomic molar mass 131.2927614479 g/mol.

It computes the same Xe-131 partial rate under three nuclear-mass schemes:
- legacy (A u);
- NIST atomic mass minus 54 electron rest masses, with electronic binding neglected;
- the recommended AME2020 binding-energy correction with CODATA-2022 constants.

The AME2020/CODATA-2022 result is the reference result. The other two
prescriptions are retained as controlled comparisons; the mass dependence is
propagated through (m_A), (q_{m response}), (v_{min}), the three-body
kernel, and the propagator denominator.

It uses:
- the full 2401-point AFH v6.0 default Xe-131 response curve;
- the new AME2020/CODATA-2022 nuclear mass in the three-body kernel;
- the exact recoil momentum for AFH response interpolation;
- truncated SHM as the baseline (\(v_0=220\), \(v_E=232\),
  \(v_{\rm esc}=544\) km/s, \(v_{\max}=776\) km/s);
- untruncated boosted Maxwell-Boltzmann only as a high-speed-tail diagnostic;
- the conditional pole width for \(\chi_2\to\chi_1s\), with \(g_2=1\);
- 16/32-node speed quadrature and 8x8x4 / 16x16x8 kernel cross-checks.

The calculation outputs are archived under
\`output/ame2020_cod2022_xe131_partial/\`.

**Important limitation:** this is the Xe-131 isotope term only, not the total
natural-xenon rate. The branch does not contain the original 16,807-row
all-isotope AFH response input \`afh_xe_isotope_responses.csv\`; the existing
natural-xenon archive retains only 28 selected response samples. Those
samples are insufficient to reconstruct all isotope response curves at the
new momentum-transfer points. No missing isotope response is inferred or
invented here.

The rate is before detector efficiency, resolution, exposure, cuts,
backgrounds, and likelihood. Native Mathematica execution of AFH v6.0 also
remains a separate validation task.
