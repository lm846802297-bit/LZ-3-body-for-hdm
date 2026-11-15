# Historical Xe-131 I6 mapping and quadrature audit

**Status: diagnostic complete.** This is an I6-only comparison; it does not recalculate the AFH response and does not validate the full differential cross section.

## 1. Matched historical point

The archived green Xe-131 single-speed result is reproduced with exactly the original inputs:

| Input | Value |
|---|---:|
| \(m_{\chi_1}\) | 1000 GeV |
| \(m_s\) | 300 keV |
| \(\Delta m\) | 1 MeV |
| \(m_A=131u\) | 122.02572741702 GeV |
| Incident speed | 776 km/s |
| Width | zero |
| Historical quadrature | \(n_W,n_z,n_\phi=40,32,20\) |
| Recoil points | 101, 200, 267, 542 keV |

The 101-keV point is kinematically closed. The 200-, 267-, and 542-keV points are open.

## 2. Pointwise results

All \(I_6\) values below are in GeV\(^2\).

| \(E_R\) [keV] | Archived / legacy \(40\times32\times20\) | Independent linear-\(W^2\) | threshold-\(u^2\), \(40\times32\times20\) | threshold-\(u^2\), \(48\times40\times24\) | threshold-\(u^2\), \(64\times48\times32\) |
|---:|---:|---:|---:|---:|---:|
| 101 | 0 (closed) | 0 | 0 | 0 | 0 |
| 200 | 879672.0472972188 | 879672.0472502336 | 879670.1277325553 | 879670.1277308514 | 879670.1277185130 |
| 267 | 1312080.2953675970 | 1312080.2952981088 | 1312077.4870994322 | 1312077.4871147086 | 1312077.4871122500 |
| 542 | 506459.6026966326 | 506459.6026692159 | 506458.4756997828 | 506458.4757053643 | 506458.4757044113 |

## 3. Interpretation

- The legacy \`eq6_kernel.reduced_kernel\` reproduces all three archived open-point values exactly.
- The independently implemented \`phase_space_convergence.integrate_i6\` with linear-\(W^2\) mapping agrees with the archive to a maximum relative difference of \(5.42\times10^{-11}\). Linear-\(W\) agrees within \(2.32\times10^{-9}\).
- At the same \(40\times32\times20\) order, threshold-\(u^2\) and sine-squared mappings give values lower than the archive by \(2.14\)--\(2.23\times10^{-6}\).
- The threshold-\(u^2\) \(48\times40\times24\) and \(64\times48\times32\) results agree to a maximum relative difference of \(1.4027\times10^{-11}\). This is the convergence check; the old \(40\times32\times20\) archive is a reproducible finite-order result, not the high-order reference.
- The earlier \(4.11\times10^{-5}\) preliminary discrepancy is not reproduced by this matched rerun. It remains an unverified preliminary observation and must not be quoted as the current measured difference.

The small mapping-dependent shift is in the phase-space quadrature only. It is not an AFH response normalization difference: the AFH table is not read by this audit, and no factor-four operation occurs in \(I_6\).

## 4. Provenance and outputs

- Workflow: [run 43768639839](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43768639839)
- Artifact: 14182804837, \`xe131-historical-i6-mapping-audit\`
- Artifact ZIP SHA-256: \`ded60b80d67b682c83be3b58f02b26573f1f13b1146dbf0cdffbcc3854232878\`
- CSV SHA-256: \`5287ea7f928b49bfe094dce42aeaaaeafe7077579fe4200f55f9623e282eb4a2\`
- Metadata JSON SHA-256: \`477494fb91db9f624c90a05a01e98bc7d40c66b2c87c1b43f4aa01f1f02de51c\`

The committed archive contains the CSV, metadata, README, and SHA-256 manifest under \`output/historical_i6_mapping_audit/\`.

## 5. Next validation gate

The remaining task is the native Wolfram Language full-grid \(d\sigma_A/dE_R\) calculation and pointwise comparison against the independent Python calculation. The PowerShell wrapper is \`run_native_full_dsigma_windows.ps1\`. Until that run reports PASS and its output metadata and hashes are reviewed, the complete Mathematica/Python cross-section comparison remains pending.
