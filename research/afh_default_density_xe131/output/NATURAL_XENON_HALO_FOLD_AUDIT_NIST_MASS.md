# Natural xenon AFH v6 halo-folded three-body rate: NIST nuclear masses

The isotope sum is performed only after evaluating each isotope with its own nuclear mass, AFH response and kinematic threshold:
dR/dER = N_T (rho_chi/m_chi) c sum_A x_A integral dv f_lab(v) (v/c) d sigma_A/dER.

## Fixed inputs
- AFH v6.0 built-in responses: Xe-128, 129, 130, 131, 132, 134, 136.
- NIST atomic isotope masses converted to nuclear masses by subtracting 54 electron masses; natural amount fractions are not renormalized.
- Available natural abundance: 0.998158; omitted Xe-124 and Xe-126: 0.001842.
- m_chi1=1 TeV, mV=10 GeV, (g1 g2 gVN)^2=1e-8, g2=1.
- rho_chi=0.3 GeV/cm^3; xenon molar mass 131.293 g/mol.
- Pole width for chi2 -> chi1 s, conditional on Dirac chi2, real scalar s, pure scalar off-diagonal Yukawa and one open channel.
- Three-body kernel 8x8x4; velocity integration compared at 16 and 32 Gauss-Legendre nodes.

## Halo alternatives
- Truncated SHM: v0=220, vE=232, vesc=544 km/s; vmax,lab=776 km/s.
- Untruncated boosted Maxwell-Boltzmann: same v0 and vE; numerical integration to 1600 km/s.
These are alternatives, not a combined band.

## Results
Units: events/(kg day keV), before detector effects.

| benchmark | ER [keV] | truncated SHM | untruncated MB |
|---|---:|---:|---:|
| Red (ms=200 keV, Delta m=1 MeV) | 101 | 5.28846e-11 | 8.61265e-11 |
| Green (ms=300 keV, Delta m=1 MeV) | 101 | 2.60336e-22 | 1.38558e-12 |
| Black (ms=360 keV, Delta m=1 MeV) | 101 | 0 | 6.23228e-14 |
| Blue (ms=300 keV, Delta m=10 MeV) | 101 | 2.17074e-24 | 1.10950e-14 |
| Green | 200 | 1.81621e-11 | 1.64835e-10 |
| Green | 267 | 2.73094e-13 | 1.78953e-12 |
| Green | 542 | 1.45810e-15 | 8.18051e-14 |

## Kinematic interpretation
At ER=101 keV, the red benchmark is open for all seven available isotopes under truncated SHM. Green and blue are only open for Xe-136; black is closed for all seven. The untruncated MB distribution admits a high-speed tail and therefore gives nonzero rates in cases where truncated SHM gives zero or strongly suppressed rates.

A mono-speed v=800 km/s calculation is outside the truncated-SHM support (776 km/s) and is only a kinematic diagnostic.

## Convergence
Maximum relative difference between 16- and 32-node speed integration: 1.0963e-4. The three-body kernel uses 8x8x4 quadrature; selected checks against 16x16x8 are archived separately.

## Limitations
No detector response, efficiency, exposure, cuts or likelihood. Xe-124 and Xe-126 are omitted because their AFH v6 built-in response matrices are unavailable. The Fig.2 caption does not determine the halo model, mV=10 GeV or g2=1. Native Mathematica execution of AFH v6 is still pending.