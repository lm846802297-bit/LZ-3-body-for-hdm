# Corrected AFH-default Xe-131 four-benchmark comparison

This archive gives the corrected 5 keV-grid AFH-default substitution for four fixed-speed benchmarks. The existing Eq. (6) integral I6 and particle/mediator prefactors are held fixed; only the nuclear response changes.

## Normalization

The AFH v6.0 package response has `(4 pi/(2 J_A+1))*W_M00_AFH(0)=A^2/4`. Equal physical proton/neutron couplings require four times this isoscalar package response. The physical response is normalized to `R_A(0)=A^2` to remove the small finite-decimal density-matrix offset.

## Numerical prescription

`q_response=sqrt(2*m_A*E_R)` is used for the nuclear response. The exact recoil momentum in the three-body kinematics remains as in the archived I6 calculation. AFH is interpolated with PCHIP, without extrapolation.

`dσ_AFH/dE_R = (dσ_GCN/dE_R) * R_A_AFH/R_A_GCN`; the event rate is scaled by the same response ratio. I6 is common to AFH, GCN and JJ55.

## First open recoil grid point

| Benchmark | m_s [keV] | Δm [MeV] | First open E_R [keV] |
|---|---:|---:|---:|
| red_ms200_dm1 | 200 | 1 | 35 |
| green_ms300_dm1 | 300 | 1 | 100 |
| black_ms360_dm1 | 360 | 1 | 190 |
| blue_ms300_dm10 | 300 | 10 | 100 |

## Selected response ratios

|   ER_keV |    R_A_AFH |     R_A_GCN |     R_A_JJ55 |   AFH/GCN |   AFH/JJ55 |
|---------:|-----------:|------------:|-------------:|----------:|-----------:|
|      200 | 9.56772    | 10.0454     | 10.7015      |  0.952451 |   0.894058 |
|      265 | 0.0187407  |  0.0180934  |  0.0273235   |  1.03577  |   0.685882 |
|      270 | 0.0018744  |  0.00178396 |  6.71541e-05 |  1.05069  |  27.9119   |
|      540 | 0.00374433 |  0.00509011 |  0.00691365  |  0.735609 |   0.541585 |
|      545 | 0.00271226 |  0.00248349 |  0.00292685  |  1.09212  |   0.926683 |
|      800 | 0.0501654  |  0.057073   |  0.0653896   |  0.878968 |   0.767177 |

## Audit of the previous archive

The previous CSV's AFH `R_A` field was exactly copied from GCN (`True`), although its AFH cross-section and rate columns had been response-scaled. This corrected file updates the AFH response values explicitly and recomputes the scaling with the archived AFH table and PCHIP interpolation.

Maximum relative change from the prior AFH cross-section values on open points: 2.740597e-04. Event-rate change: 2.740597e-04. The largest changes occur close to deep response minima.

## Checks

- 4 benchmarks × 160 recoil points × 3 models = 1920 long-format rows.
- GCN and JJ55 have identical I6 at every recoil point.
- AFH uses the same I6 and phase-space mask.
- AFH/GCN cross-section ratio equals AFH/GCN response ratio point by point.
- Physical AFH response satisfies R_A(0)=A².

## Limitations

- Fixed mono-speed v=800 km/s; no halo fold.
- I6 grid reused; not a fresh 640-point Eq. (6) integration.
- Conditional pole width, not a full self-energy.
- No detector efficiency, resolution, cuts, or likelihood.
- Native Mathematica execution remains pending.
