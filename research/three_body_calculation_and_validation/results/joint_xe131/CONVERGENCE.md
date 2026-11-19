# Xe-131 joint-kernel quadrature convergence

The comparison uses identical AFH response data and physical inputs.
Only the Eq. (6) quadrature order changes: coarse (16,16,8), medium (24,24,16), fine (40,32,20).
The response model does not enter I6; GCN and JJ55 must therefore share I6.

| ER [keV] | phase space | I6 coarse [GeV²] | I6 medium [GeV²] | I6 fine [GeV²] | fine/medium - 1 |
|---:|:---:|---:|---:|---:|---:|
| 101 | False | 0 | 0 | 0 | 0.000e+00 |
| 200 | True | 879698.55 | 879678.8 | 879672.05 | -7.679e-06 |
| 267 | True | 1312119.1 | 1312090.2 | 1312080.3 | -7.532e-06 |
| 542 | True | 506475.17 | 506463.57 | 506459.6 | -7.831e-06 |

Acceptance: all open-channel points agree within 5e-5 relative across the three orders; GCN/JJ55 give the same I6 to numerical precision.

This is a fixed-speed differential-cross-section diagnostic, not a halo-folded event rate.
