# AFH default versus GCN/JJ55: Xe-131 comparison

## Response minima

The AFH default matrix is a third nuclear-structure prescription. Its minima
are close in momentum transfer to the GCN and JJ55 minima, but their depths
are model dependent.

| Minimum | Model | q_min [MeV] | E_R,min [keV] | R_min/R(0) |
|---:|---|---:|---:|---:|
| 1 | AFH default | 157.93578 | 102.20672 | 1.236382e-05 |
| 1 | GCN | 157.24993 | 101.32097 | 3.350290e-06 |
| 1 | JJ55 | 156.74892 | 100.67637 | 6.279639e-08 |
| 2 | AFH default | 256.27187 | 269.10390 | 6.340702e-08 |
| 2 | GCN | 256.25125 | 269.06059 | 4.007402e-08 |
| 2 | JJ55 | 256.74747 | 270.10365 | 3.862813e-09 |
| 3 | AFH default | 365.06657 | 546.08690 | 1.561940e-07 |
| 3 | GCN | 366.75111 | 551.13818 | 8.410237e-08 |
| 3 | JJ55 | 367.99819 | 554.89265 | 3.503921e-09 |

## Same three-body kernel at the Figure 2 reference energies

For this comparison the three-body phase-space/matrix-element integral `I6`
is held fixed to the previously validated Xe-131 run at
`m_chi1=1 TeV`, `m_s=300 keV`, `Delta m=450 keV`, `m_V=10 GeV`,
`v=776 km/s`, and the same quadrature. Only the nuclear response is changed.
Thus the cross-section differences below isolate the nuclear model.

| E_R [keV] | Model | R_A | R_A/A^2 | d sigma/dE_R [cm^2/keV] |
|---:|---|---:|---:|---:|
| 267 | AFH default | 0.005597764 | 3.261910e-07 | 1.380498e-35 |
| 267 | GCN | 0.0048413535 | 2.821137e-07 | 1.193955e-35 |
| 267 | JJ55 | 0.0092100225 | 5.366833e-07 | 2.271339e-35 |
| 542 | AFH default | 0.0031511299 | 1.836216e-07 | 2.340203e-36 |
| 542 | GCN | 0.0038433807 | 2.239602e-07 | 2.854307e-36 |
| 542 | JJ55 | 0.0050935603 | 2.968102e-07 | 3.782759e-36 |

At 101 keV, this fixed-speed benchmark is kinematically closed for all
three nuclear models: the previously computed open interval begins at
109.1503 keV. Therefore a nonzero cross section must not be inferred from
the nuclear-response dip alone.

## Interpretation

- The AFH default matrix reproduces the three common recoil-dip regions
  without tuning `b_A`.
- The minima positions are similar across AFH default, GCN and JJ55.
- The dip depths vary substantially, especially for JJ55. This is a genuine
  nuclear-structure dependence and should be retained as a model comparison,
  not removed by fitting the oscillator length.
- The three-body kernel is unchanged in the cross-section comparison, so
  the model-to-model differences are attributable to `R_A(E_R)`.

This remains a single-isotope, fixed-speed cross-section diagnostic. It is
not a natural-xenon halo-folded event rate.

