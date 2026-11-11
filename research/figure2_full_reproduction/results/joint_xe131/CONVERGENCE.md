# Xe-131 joint-kernel quadrature convergence

The comparison uses the same AFH response data and physical inputs.
Only the Eq. (6) quadrature order changes: coarse (16,16,8), fine (40,32,20).
The response model does not enter I6; GCN and JJ55 must therefore share I6.

| ER [keV] | phase space | I6 coarse [GeV²] | I6 fine [GeV²] | fine/coarse - 1 |
|---:|:---:|---:|---:|---:|
| 101 | False | 0 | 0 | 0.000e+00 |
| 200 | True | 879698.55 | 879672.05 | -3.013e-05 |
| 267 | True | 1312119.1 | 1312080.3 | -2.955e-05 |
| 542 | True | 506475.17 | 506459.6 | -3.073e-05 |

Acceptance: all open-channel points must agree within 5e-5 relative; GCN/JJ55 must give the same I6 to numerical precision.

This is a fixed-speed differential-cross-section diagnostic, not a halo-folded event rate.
