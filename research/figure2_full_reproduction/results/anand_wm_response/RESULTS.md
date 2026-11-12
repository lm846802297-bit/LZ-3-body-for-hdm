# Anand W_M response reproduction

## Scope

This run computes only the nuclear response factor. It does not compute
the three-body phase-space/matrix-element integral or the halo integral.

## Xe-131 zero-momentum normalization

| Model | J | b [fm] | R_A(0) | A^2 | Relative error |
|---|---:|---:|---:|---:|---:|
| GCN | 1.5 | 2.292342 | 17160.988 | 17161 | 7.244e-07 |
| JJ55 | 1.5 | 2.292342 | 17160.988 | 17161 | 7.244e-07 |

## Xe-131 response minima

| Model | q_min [MeV] | E_R,min [keV] | R_min/R(0) |
|---|---:|---:|---:|
| gcn | 157.2499 | 101.321 | 3.3503e-06 |
| gcn | 256.2512 | 269.061 | 4.0074e-08 |
| gcn | 366.7511 | 551.138 | 8.4102e-08 |
| jj55 | 156.7489 | 100.676 | 6.2796e-08 |
| jj55 | 256.7475 | 270.104 | 3.8628e-09 |
| jj55 | 367.9982 | 554.893 | 3.5039e-09 |

## Figure 2 dip-energy points

| Model | Figure 2 E_R [keV] | q [MeV] | R_A/R_A(0) |
|---|---:|---:|---:|
| GCN | 101 | 157.001 | 3.5105e-06 |
| GCN | 267 | 255.268 | 2.8204e-07 |
| GCN | 542 | 363.698 | 2.2392e-07 |
| JJ55 | 101 | 157.001 | 6.8309e-07 |
| JJ55 | 267 | 255.268 | 5.3657e-07 |
| JJ55 | 542 | 363.698 | 2.9675e-07 |

## Natural xenon

The abundance-weighted response-only mixture includes Xe-128, 129, 130,
131, 132, 134 and 136, covering 99.81580% of the NIST natural amount fraction.
Xe-124 and Xe-126 (combined 0.1842%) are absent from the pinned dmscatter target library.
The mixture is not the full three-body event rate: isotope-specific
m_A prefactors, kinematic limits and three-body integrals still need
to be applied before the halo fold.

## Input prescription

The oscillator length follows the default prescription explicitly
documented by Anand, Fitzpatrick and Haxton, arXiv:1308.6288, Sec. 7.2:
b_A[fm] = sqrt(41.467 / (45 A^(-1/3) - 25 A^(-2/3))).
The same formula is implemented by dmscatter and is explicitly supplied
in each control file. The original target manuscript does not state b_A;
we adopt the AFH literature default rather than fit b_A to Figure 2.

See metadata.json and the raw_runs directory for provenance.


## AFH v6.0 default Xe-131 reference

The official AFH v6.0 package includes the built-in 67-entry `sdgXe131`
default density matrix. Using `SetIsotope[54,131,"default","default"]`
gives (b_A=2.2923417985218975) fm.

The AFH package's `ResponseNuclear[y,1,0,0]` is the isoscalar
(W_M^{00}) with ((4\pi/(2J_A+1))W_M^{00}(0)=A^2/4).
For equal physical proton and neutron couplings, the coherent response is
four times the raw AFH isoscalar response. The archived AFH-default curve
is normalized by its q=0 value to (A^2), correcting only the
(8.25\times10^{-5}) finite-precision offset in the source density matrix.

AFH-default minima: 102.207, 269.104, and 546.087 keV. These lie close to
the existing GCN/JJ55 minima; depths remain model dependent. The same-kernel
cross-section comparison at 267 and 542 keV is archived in
`research/afh_default_density_xe131/output/AFH_DEFAULT_VS_GCN_JJ55_COMPARISON.md`.

**Normalization convention warning:** the manuscript currently writes
(4\pi W_M^{00}/(2J_A+1)) and (R_A(0)=A^2) together. If (W_M^{00})
is the unmodified AFH package output, this is a factor-of-four mismatch.
The physical equal-p/n response must use the four-channel sum (or an
equivalent factor of four) before the absolute three-body cross section.
