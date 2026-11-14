# Corrected AFH-default Xe-131 four-benchmark comparison

Canonical machine-readable outputs are `figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv` (long form) and `figure2_four_benchmarks_AFH_GCN_JJ55_wide_audit.csv` (wide audit). The earlier `figure2_four_benchmarks_dsigma_AFH_GCN_JJ55.csv` is historical and superseded; see [CROSS_SECTION_FILE_INDEX.md](CROSS_SECTION_FILE_INDEX.md).

This archive gives the corrected 5 keV-grid AFH-default substitution for four fixed-speed benchmarks. The existing Eq. (6) integral I6 and particle/mediator prefactors are held fixed; only the nuclear response changes.

## Normalization

The AFH v6.0 package response has `(4 pi/(2 J_A+1))*W_M00_AFH(0)=A^2/4`. Equal physical proton/neutron couplings require four times this isoscalar package response. The physical response is normalized to `R_A(0)=A^2` to remove the small finite-decimal density-matrix offset.

## Numerical prescription

`q_response=sqrt(2*m_A*E_R+E_R^2)` is used for the AFH response, consistent with its spatial momentum-transfer definition and the exact nuclear mass shell. The NR approximation `sqrt(2*m_A*E_R)` is retained only for sensitivity comparisons. AFH is interpolated with PCHIP, without extrapolation.

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
|      200 | 9.567669856 | 10.04536595 | 10.70146183 | 0.9524461232 | 0.8940526079 |
|      265 | 0.01873812446 | 0.01809342929 | 0.02732346798 | 1.035631453 | 0.6857886586 |
|      270 | 0.001874929102 | 0.001783964806 | 6.715406078e-05 | 1.050989961 | 27.91981722 |
|      540 | 0.003743904127 | 0.005090110737 | 0.006913653172 | 0.7355250839 | 0.5415232777 |
|      545 | 0.002712192959 | 0.002483485866 | 0.002926853516 | 1.09209116 | 0.9266582504 |
|      800 | 0.0501638824 | 0.05707299958 | 0.06538958073 | 0.8789424556 | 0.7671540609 |

## NR-approximation sensitivity

For the fixed benchmark mass \(M_A=131u\), replacing exact spatial q by
\(q_{\rm NR}=\sqrt{2M_AE_R}\) changes the AFH response at the selected recoil
points by:

| \(E_R\) [keV] | \(q_{\rm exact}-q_{\rm NR}\) [keV] | \(R_A(q_{\rm NR})/R_A(q_{\rm exact})-1\) [ppm] |
|---:|---:|---:|
| 101 | 0.032487 | +21.192 |
| 200 | 0.090526 | +5.478 |
| 267 | 0.139636 | +225.018 |
| 542 | 0.403857 | +89.615 |

The exact-spatial-q results above are the adopted values. These differences
are the size of the NR response approximation at these selected points; they
are not empirical rescalings.

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
