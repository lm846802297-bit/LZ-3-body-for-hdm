# Xe-131 Full-Recoil Charge-Sector Kernel Scan

**Status:** native-grid charge-sector kernel scan; not an absolute differential cross section.

## 1. Scope

This scan uses the native Xe-131 AFH v6.0 responses \(W_M\), \(W_{\Phi''}\), and the signed interference response \(W_{M\Phi''}\). Spatial multipoles \(\Delta,\Sigma',\Sigma''\) are not included. This is the charge-sector comparison only.

## 2. Benchmark context

| Parameter | Value |
|---|---:|
| Target | Xe-131 |
| Nuclear mass | 121.90971983538435 GeV |
| Nucleon mass | 0.938918 GeV |
| Dark-matter mass | 1000 GeV (1 TeV) |
| Scalar mass | 300 keV |
| Fixed speed | 776 km/s |
| \(g_2\) | 1 |
| Mediator mass context | 10 GeV |
| \(\Delta m\) at 200 keV | 450 keV |
| \(\Delta m\) at 267 keV | 362 keV |
| Form-factor prescription | project isoscalar_zexp central diagnostic |

These are the benchmark parameters of the companion fixed-speed Xe-131 calculation. The plotted ordinate is a nuclear charge-sector kernel with the common three-body DM-side tensor and phase-space factor removed. Therefore the DM mass, scalar mass, mass splitting, coupling, mediator mass, and width prescription do not enter this kernel curve; the speed defines the recoil interval. This scan is not a new evaluation of the absolute fixed-benchmark \(d\sigma/dE_R\).

## 3. Native input and recoil coverage

- Native AFH source commit: [e6d9dee3527cab200ee6b21198d577b987282fac](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/commit/e6d9dee3527cab200ee6b21198d577b987282fac).
- Native file: research/afh_default_density_xe131/output/phi_response_native/afh_default_xe131_M_PhiPP_native.csv.
- Native source grid: 2401 momentum points.
- Native source blob SHA: d80e0c1e4db79e741dc3c7a905f451230056a3f4.
- Retained points in the fixed-speed kinematic window: **943 native momentum-grid points**.
- Retained recoil coverage: **109.639486-652.944547 keV**.
- Exact recoil mapping: \(E_R=\sqrt{m_A^2+q_A^2}-m_A\), equivalently \(q_A=\sqrt{2m_AE_R+E_R^2}\).

The three AFH response values in each CSV row are taken directly from the native momentum grid; no interpolation of the AFH responses is used for the 943 output rows. Finite-\(Q^2\) form factors are evaluated pointwise using the repository's isoscalar_zexp diagnostic prescription.

## 4. Matched charge-sector kernels

Define

\[
K_M=c_M^2W_M,
\]
\[
K_{M+\mathrm{int}}=c_M^2W_M+2c_Mc_{\Phi''}W_{M\Phi''},
\]
\[
K_{\mathrm{full,ch}}=K_{M+\mathrm{int}}+c_{\Phi''}^2W_{\Phi''}.
\]

The finite-\(Q^2\) matched coefficients are evaluated at each recoil point:

\[
c_M=F_1^V-\frac{Q_A^2}{8m_N^2}(F_1^V+2F_2^V),
\qquad
c_{\Phi''}=\frac{Q_A^2}{4m_N^2}(F_1^V+2F_2^V).
\]

The plotted correction ratio is

\[
R_{\rm ch}(E_R)=\frac{K_{\mathrm{full,ch}}(E_R)}{K_M(E_R)}.
\]

This directly compares the full charge-sector response against the finite-\(Q^2\), matched \(M\)-only kernel. The common three-body DM-side factor cancels pointwise in this ratio, but not in an absolute spectrum.

**Do not confuse this ratio with** the companion fixed-speed cross-section ratio \(\mathcal Q\), whose denominator is the older pointlike \(9W_M\) benchmark and whose numerator includes the three-body phase-space integral. The companion result is \(\mathcal Q(200\,\mathrm{keV})=0.77830934\) and \(\mathcal Q(267\,\mathrm{keV})=0.64921591\); those are different ratios with different denominators.

## 5. Numerical results

On the 943-point native grid:

| Quantity | Result |
|---|---:|
| Minimum sampled \(R_{\rm ch}\) | 0.86043801 at 268.264 keV |
| Maximum sampled \(R_{\rm ch}\) | 1.11839839 at 270.366 keV |

At the exact benchmark recoil values, using shape-preserving PCHIP interpolation of the native AFH responses in \(q_A\):

| \(E_R\) | Full charge / finite-\(Q^2\) \(M\)-only | Relative change |
|---:|---:|---:|
| 200 keV | 0.99655805 | -0.3442% |
| 267 keV | 0.89961039 | -10.0390% |

The signed \(M-\Phi''\) interference changes sign across the \(W_M\) cancellation region. The ratio therefore develops a dip and a bump; the correction is not uniformly suppressive. The extrema above are sampled native-grid extrema, not claims of arbitrarily precise continuous extrema.

## 6. Files

- xe131_charge_kernel_full_recoil_scan.csv: 943 native-grid recoil rows, form factors, matched coefficients, kernels, and ratios.
- xe131_charge_kernel_full_recoil_curves.svg/.pdf: normalized kernel comparison.
- xe131_charge_kernel_full_recoil_ratios.svg/.pdf: pointwise response correction ratios.
- build_xe131_full_recoil_charge_scan.py: regeneration script using the pinned native AFH CSV and existing form-factor module.

## 7. Limitations

1. This is a charge-sector kernel scan, not the full absolute three-body differential cross section. The recoil-dependent \(L_C^{(3)}\), remaining phase-space/flux factors, and coupling-normalized prefactor have not been multiplied back in.
2. isoscalar_zexp is a central finite-\(Q^2\) diagnostic, not the final model-specific universal \(u+d+s\) form-factor determination, especially for \(F_2^V(Q^2)\).
3. Spatial AFH multipoles are not included.
4. This is Xe-131 only: no natural-xenon isotope sum, halo velocity integral, detector response, or event prediction is claimed.

The supported conclusion is specific: the full charge-sector correction is small around 200 keV but reaches about a 10% local suppression near the 267 keV \(W_M\)-cancellation region. It is not yet a detector-level or absolute-spectrum prediction.

**Regeneration environment:** Python 3.12+, NumPy, pandas, and Matplotlib.