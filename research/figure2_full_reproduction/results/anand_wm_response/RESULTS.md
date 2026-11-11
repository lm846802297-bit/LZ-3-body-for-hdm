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
