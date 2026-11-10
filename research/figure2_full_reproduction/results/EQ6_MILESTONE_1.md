# Eq. (6) numerical audit — milestone 1

## What has actually been computed

The implementation reconstructs the final-state momenta in the target rest frame and evaluates the exact Dirac trace for the two diagrams in the manuscript. It then integrates the Eq. (6) kernel over W^2, z and the azimuthal average. The overall prefactor in Eq. (6) is kept separate.

The calculation is conditional on the manuscript's written Dirac current. It does not establish that this is the correct Dirac/Majorana realization of the underlying model.

## Kinematic and trace validation

Representative point: m_chi1=1000 GeV, m_s=0.0003 GeV, Delta m=0.001 GeV, m_A=122 GeV, E_R=0.0002 GeV, v=776 km/s, W^2 midpoint, z=0.2, phi*=1.1.

- p^2-m_chi1^2 = -2.33e-10 GeV^2.
- p'^2-m_chi1^2 = -1.16e-10 GeV^2.
- k^2-m_s^2 = 2.44e-17 GeV^2.
- P'^2-m_A^2 = 1.82e-12 GeV^2.
- maximum four-momentum closure residual = 2.14e-13 GeV.
- K^2-W^2 = -1.16e-10 GeV^2.
- Dirac trace versus explicit four-spin-state sum: relative difference below 5e-15.
- The full trace is explicitly split into before, after and interference contributions.

## Quadrature convergence

At the same point and with zero width:

| (nW,nz,nphi) | Reduced Eq. (6) integral |
|---|---:|
| (16,16,8) | 878098.5567 GeV^2 |
| (24,24,16) | 878078.8408 GeV^2 |
| (32,32,16) | 878073.8896 GeV^2 |
| (40,32,20) | 878072.0973 GeV^2 |
| (48,40,24) | 878071.2968 GeV^2 |

The last two values differ by approximately 9.1e-7 relative. This convergence statement applies only to this representative integral point and the present Dirac/zero-width setup.

## Width dependence is not fixed by the figure caption

The paper uses a pole width in the second propagator. Under the explicitly conditional assumption of Dirac fermions, a pure scalar off-diagonal Yukawa coupling, and no other open chi2 decay channel, the two-body width derived from the written scalar interaction gives, for m_chi1=1 TeV, m_s=300 keV and Delta m=1 MeV. The current main.tex does not explicitly print this width formula:

- g2=0.1: Gamma_chi2 = 1.518e-6 GeV; reduced kernel = 878077.84 GeV^2.
- g2=1: Gamma_chi2 = 1.518e-4 GeV; reduced kernel = 868227.28 GeV^2.
- g2=3: Gamma_chi2 = 1.366e-3 GeV; reduced kernel = 481505.26 GeV^2.

These are diagnostic values, not chosen benchmarks. They demonstrate that the coupling product (g1 g2 gVN)^2 alone is insufficient to determine the Breit-Wigner width and therefore insufficient to uniquely reproduce the spectrum near a propagator-sensitive region.

## Four benchmark spot checks (kinematic/matrix-element kernel only)

The following points are illustrative evaluations, not the original plot inputs:

| m_s | Delta m | E_R | v | Reduced kernel |
|---:|---:|---:|---:|---:|
| 300 keV | 1 MeV | 200 keV | 776 km/s | 878078.84 GeV^2 |
| 300 keV | 10 MeV | 200 keV | 776 km/s | 6998.22 GeV^2 |
| 360 keV | 1 MeV | 300 keV | 800 km/s | 400887.43 GeV^2 |
| 360 keV | 10 MeV | 300 keV | 800 km/s | 2967.07 GeV^2 |

The large dependence on Delta m comes from the internal chi2 denominators. Do not interpret these as rates: the overall Eq. (6) prefactor, mediator mass, xenon response and halo averaging have not been applied.

## Remaining blockers before a complete d sigma_A/dE_R result

1. Explicit Dirac/Majorana and chiral/CP definition of chi1,chi2.
2. The separate g2 value (or a justified width prescription), since the caption only gives the product of couplings.
3. The vector mediator mass m_V.
4. A numerical xenon response R_A(E_R), with isotope and nuclear-response convention fixed.
5. Independent cross-check of the trace and integration at additional phase-space points and at the integration boundaries.

No Halo velocity integral has been performed in this milestone.
