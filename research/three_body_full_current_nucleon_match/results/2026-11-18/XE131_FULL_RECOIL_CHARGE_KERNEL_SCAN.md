# Xe-131 full-recoil charge-sector kernel scan

**Status:** native-grid charge-sector kernel scan; not an absolute differential cross section.

## Scope

This scan uses the native Xe-131 AFH v6.0 responses W_M, W_PhiPP, and signed W_MPhiPP. Spatial multipoles Delta, Sigma-prime, and Sigma-double-prime are not included.

## Benchmark context

| Quantity | Value |
|---|---:|
| Target | Xe-131 |
| Nuclear mass | 121.90971983538435 GeV |
| Nucleon mass | 0.938918 GeV |
| Fixed speed defining recoil window | 776 km/s |
| DM mass context | 1 TeV |
| Scalar mass context | 300 keV |
| g2 context | 1 |
| Mediator mass context | 10 GeV |
| Form-factor prescription | project isoscalar_zexp central diagnostic |

The preceding off-pole reference point used Delta m = 450 keV. These DM values are contextual: the plotted nuclear kernels factor out the common three-body DM-side phase-space tensor. Thus m_chi1, m_s, Delta m, m_V, g2, and the overall coupling product do not enter the plotted ordinate. The speed defines the recoil window. This is not a fully evaluated fixed-benchmark d sigma/dE_R.

## Native input and recoil coverage

- Native AFH source commit: e6d9dee3527cab200ee6b21198d577b987282fac
- Native file: research/afh_default_density_xe131/output/phi_response_native/afh_default_xe131_M_PhiPP_native.csv
- Native source grid: 2401 q points.
- Native source blob SHA: d80e0c1e4db79e741dc3c7a905f451230056a3f4
- Retained points in the fixed-speed kinematic window: **943 native q-grid points**.
- Retained recoil coverage: 109.639486–652.944547 keV.
- Exact mapping: E_R = sqrt(m_A^2 + q_A^2) - m_A; equivalently q_A = sqrt(2 m_A E_R + E_R^2).

The AFH response values are taken directly at native q-grid points. No interpolation of the AFH responses is used for the 943 output rows. Finite-Q2 form factors are evaluated pointwise using the repository's isoscalar_zexp prescription.

## Matched charge-sector kernels

Define K_M = c_M^2 W_M, K_M+int = c_M^2 W_M + 2 c_M c_Phi W_MPhi, and K_full,ch = K_M+int + c_Phi^2 W_Phi.

c_M = F1^V - Q_A^2 (F1^V + 2 F2^V)/(8 m_N^2),

c_Phi = Q_A^2 (F1^V + 2 F2^V)/(4 m_N^2).

The pointwise ratio is R_ch(E_R) = K_full,ch(E_R)/K_M(E_R). The common three-body factor cancels pointwise in this ratio, but not in an absolute spectrum.

Figure 1 is a normalized charge-sector kernel comparison, not absolute d sigma/dE_R. Figure 2 is the pointwise charge-sector correction ratio.

## Numerical summary

On the 943-point native grid:

| Quantity | Result |
|---|---:|
| Minimum sampled full/M ratio | 0.86043801 at 268.264 keV |
| Maximum sampled full/M ratio | 1.11839839 at 270.366 keV |

At exact recoil values, using PCHIP interpolation of native response functions in q_A:

| E_R | Full charge / M-only | Relative change |
|---:|---:|---:|
| 200 keV | 0.99655805 | -0.3442% |
| 267 keV | 0.89961039 | -10.0390% |

The signed M-Phi interference changes sign across the W_M cancellation region. The ratio therefore develops a dip and a bump; the correction is not uniformly suppressive. The extrema above are native-grid sampled extrema, not arbitrarily precise continuous extrema.

## Files

- xe131_charge_kernel_full_recoil_scan.csv: 943 native-grid recoil rows, form factors, matched coefficients, kernels, and ratios.
- xe131_charge_kernel_full_recoil_curves.svg: normalized kernel comparison.
- xe131_charge_kernel_full_recoil_ratios.svg: response correction ratios.
- build_xe131_full_recoil_charge_scan.py: regeneration script using the pinned native AFH CSV and existing form-factor module.

## Limitations

1. This is a charge-sector kernel scan, not the full absolute three-body differential cross section. The recoil-dependent three-body factor L_C^(3), remaining phase-space/flux factors, and coupling-normalized prefactor have not been multiplied back in.
2. isoscalar_zexp is a central finite-Q2 diagnostic, not the final model-specific universal u+d+s form-factor determination, especially for F2^V(Q2).
3. Spatial AFH multipoles are not included.
4. This is Xe-131 only: no natural-xenon isotope sum, halo velocity integral, detector response, or event prediction is claimed.

The supported conclusion is local and specific: the charge-sector kernel ratio is close to unity over much of the recoil range but has a pronounced dip/bump around the W_M cancellation region. It is not yet a detector-level or absolute-spectrum prediction.
