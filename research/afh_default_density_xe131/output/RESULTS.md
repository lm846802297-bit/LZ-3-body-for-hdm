# AFH DMFormFactor v6.0 default Xe-131 response

## Input and convention

The input is the built-in `sdgXe131` default density matrix (67 entries), selected by SetIsotope with Z=54, A=131, b=default, filename=default. The oscillator length is the AFH default formula and the AFH source uses Femtometer=5.0677/GeV.

The package returns `ResponseNuclear[y,1,0,0] = W_M^{00}`. In the AFH isoscalar convention, its normalized zero-momentum response is A^2/4, not A^2. For equal physical proton and neutron couplings, the coherent response is four times the AFH isoscalar-normalized response. The density matrix's finite decimal precision gives a small q=0 deviation, removed by normalizing the shape to the exact A^2 charge.

## Zero-momentum normalization

- AFH package: 4289.895955715
- Expected AFH package value A^2/4: 4290.250000000
- Relative difference: 8.252e-05
- Equal-pn response after shape normalization: 17161.000000000
- A^2: 17161
- Shape normalization factor: 1.0000825298

## AFH default b_A

- b_A = 2.2923417985 fm
- b_A = 11.6169005324 GeV^-1

## Response minima

| q_min [MeV] | E_R,min [keV] | R/A^2 |
|---:|---:|---:|
| 157.93578 | 102.20672 | 1.236382e-05 |
| 256.27187 | 269.10390 | 6.340702e-08 |
| 365.06657 | 546.08690 | 1.561940e-07 |
| 499.37189 | 1021.79779 | 1.670632e-08 |

## Recoil-momentum convention

The response grid is tabulated in the AFH spatial momentum transfer q, with
\(y=(q b_A/2)^2\). The Figure-2 recoil-energy checks use the exact mass-shell
mapping \(q=\sqrt{2M_AE_R+E_R^2}\). The NR approximation
\(q_{\rm NR}=\sqrt{2M_AE_R}\) is only a small-recoil comparison; see Appendix G.

## Figure 2 recoil-energy points

| E_R [keV] | q [MeV] | R/A^2 |
|---:|---:|---:|
| 101.0 | 157.00066 | 1.779141e-05 |
| 267.0 | 255.26811 | 3.260744e-07 |
| 542.0 | 363.69793 | 1.836308e-07 |

## Scope and caution

This result is only the AFH default Xe-131 nuclear response. It is not the complete three-body differential cross section, not a halo-folded spectrum, and not a natural-xenon rate. The manuscript's equation identifying `4 pi W_M^{00}/(2J_A+1)` directly with a response normalized to A^2 must be corrected or its W convention explicitly redefined by a factor of four.

The GCN/JJ55 results previously archived from dmscatter are separate nuclear-structure calculations and are not substituted here.


## Comparison to the existing GCN/JJ55 runs

The AFH default minima lie close to the GCN/JJ55 minima in q, while their
depths remain nuclear-model dependent. See
`AFH_DEFAULT_VS_GCN_JJ55_COMPARISON.md` for the side-by-side response-minimum
table and the same-kernel cross-section comparison at 267 and 542 keV.

For the fixed-speed benchmark (m_chi1=1 TeV, m_s=300 keV,
Delta m=450 keV, m_V=10 GeV, v=776 km/s), the AFH-default
cross sections at 267 and 542 keV are respectively
1.3805e-35 and 2.3402e-36 cm^2/keV. The 101 keV point and the
AFH first minimum at 102.2 keV are kinematically closed for this benchmark.

