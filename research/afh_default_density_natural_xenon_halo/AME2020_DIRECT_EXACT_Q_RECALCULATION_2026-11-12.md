# AME2020 natural-xenon direct exact-q recalculation

**Date:** 2026-11-12  
**Execution:** local Python calculation; no GitHub Actions / CI used  
**Study branch:** `research/ame2020-mass-exact-spatial-mainline`  
**Input branch HEAD:** `fd325c13e0aa82f7c829fa85a3ee3a744e5d8e03`

## 1. Scope and status

This calculation replaces the 2401-node PCHIP response lookup in the selected-point AME2020 halo fold with archived direct AFH finite-sum responses at the exact spatial momentum transfer. It covers seven AFH default-density isotopes (Xe-128, 129, 130, 131, 132, 134, 136), four recoil energies (101, 200, 267, 542 keV), NIST and AME2020/CODATA-2022 nuclear masses, and truncated-SHM plus untruncated-MB halo prescriptions.

The primary response is **direct exact-q**. PCHIP is retained only as a historical comparison. This is a selected-point differential-rate calculation, not a continuous recoil spectrum or a detector-level LZ prediction.

## 2. Inputs and exact-q prescription

The response input contains 56 values: seven isotopes × four recoil energies × two mass schemes. Direct finite-sum values were independently checked against 60-digit `mpmath` evaluations. The response is evaluated at

\[
q_A=\sqrt{2m_AE_R+E_R^2}.
\]

No interpolation is used for the primary selected-point responses. PCHIP values from the historical 2401-node grid are carried separately as a diagnostic.

The seven AFH-supported isotopes cover natural atom fraction **0.998158**. These abundances are not renormalized. Xe-124 and Xe-126 have no AFH v6.0 default density matrices and are not included in the AFH central prediction.

### Nuclear-mass comparison

| Isotope | NIST nuclear mass [GeV] | AME2020 nuclear mass [GeV] | AME2020–NIST [ppm] |
|---|---:|---:|---:|
| Xe-128 | 119.113790862 | 119.113993177 | +1.699 |
| Xe-129 | 120.046449203 | 120.046651745 | +1.687 |
| Xe-130 | 120.976758899 | 120.976961443 | +1.674 |
| Xe-131 | 121.909719835 | 121.909922447 | +1.662 |
| Xe-132 | 122.840348604 | 122.840551151 | +1.649 |
| Xe-134 | 124.704491465 | 124.704692499 | +1.612 |
| Xe-136 | 126.569174825 | 126.569377370 | +1.600 |

## 3. Three-body and halo integration

The existing Eq. (6) spin-trace kernel is used with the pole-width prescription for \(\chi_2\to\chi_1s\), conditional on the Dirac-fermion / real-scalar / pure off-diagonal scalar coupling assumptions already recorded in the study.

- Baseline kernel quadrature: \(8\times8\times4\) in \((W^2,z,\phi^*)\).
- Speed Gauss-Legendre orders: 32 and 64.
- Independent kernel cross-check: \(16\times16\times8\), at three anchors for all seven isotopes.

Fixed inputs: \(m_{\chi_1}=1\,\mathrm{TeV}\), \(m_V=10\,\mathrm{GeV}\), coupling-product squared \(=10^{-8}\), \(g_2=1\), \(\rho_\chi=0.3\,\mathrm{GeV\,cm}^{-3}\); halo parameters \(v_0=220\), \(v_E=232\), \(v_{\rm esc}=544\) km/s. The untruncated-MB diagnostic is integrated to 1600 km/s.

Rates are in events/(kg day keV), before detector efficiency, resolution, exposure, cuts or likelihood.

## 4. Local numerical acceptance

| Check | Maximum relative difference | Result |
|---|---:|---|
| Recomputed NIST/PCHIP baseline vs archived NIST natural-Xe totals (32 speed nodes) | 3.432e-12 | Pass |
| 32 vs 64 speed-node total rates | 3.303e-06 | Pass |
| 32 vs 64 speed-node isotope contributions | 3.330e-06 | Pass |
| Kernel \(8\times8\times4\) vs \(16\times16\times8\), 21 AME2020 anchor checks | 2.108e-04 | Pass |
| Sum of seven isotope contributions vs stored 112 rate summaries | 2.028e-16 | Pass |

The NIST historical PCHIP baseline is reproduced before interpreting the AME2020 mass update.

## 5. Seven-isotope direct exact-q rates: NIST vs AME2020

The table gives the 64-node direct exact-q total over the seven AFH-supported isotopes. The final column is \((R_{\rm AME2020}/R_{\rm NIST}-1)\times10^6\).

| Benchmark | \(E_R\) [keV] | Halo | NIST direct exact-q | AME2020 direct exact-q | AME2020 vs NIST [ppm] |
|---|---:|---|---:|---:|---:|
| red_ms200_dm1 | 101 | shm_cutoff | 5.281054e-11 | 5.281010e-11 | -8.425 |
| red_ms200_dm1 | 101 | mb_untruncated | 8.600908e-11 | 8.600796e-11 | -13.031 |
| green_ms300_dm1 | 101 | shm_cutoff | 2.599523e-22 | 2.627063e-22 | +10594.376 |
| green_ms300_dm1 | 101 | mb_untruncated | 1.383664e-12 | 1.383664e-12 | +0.305 |
| black_ms360_dm1 | 101 | shm_cutoff | 0.000000e+00 | 0.000000e+00 | +0.000 |
| black_ms360_dm1 | 101 | mb_untruncated | 6.223611e-14 | 6.223676e-14 | +10.502 |
| blue_ms300_dm10 | 101 | shm_cutoff | 2.167543e-24 | 2.190507e-24 | +10594.242 |
| blue_ms300_dm10 | 101 | mb_untruncated | 1.107897e-14 | 1.107897e-14 | +0.170 |
| green_ms300_dm1 | 200 | shm_cutoff | 1.813604e-11 | 1.813645e-11 | +22.497 |
| green_ms300_dm1 | 200 | mb_untruncated | 1.646153e-10 | 1.646160e-10 | +4.330 |
| green_ms300_dm1 | 267 | shm_cutoff | 2.727153e-13 | 2.727278e-13 | +46.060 |
| green_ms300_dm1 | 267 | mb_untruncated | 1.787243e-12 | 1.787274e-12 | +17.118 |
| green_ms300_dm1 | 542 | shm_cutoff | 1.456132e-15 | 1.456312e-15 | +123.812 |
| green_ms300_dm1 | 542 | mb_untruncated | 8.170925e-14 | 8.171409e-14 | +59.247 |

The largest relative mass-scheme shift occurs for the 101 keV green/blue truncated-SHM cases. Only Xe-136 is kinematically open there and \(v_{\min}\simeq775.806\) km/s, close to the 776 km/s lab-frame cutoff. The rates are extremely small (about \(10^{-22}\) or \(10^{-24}\) events/(kg day keV)). This is an endpoint-tail sensitivity, not a typical percent-level nuclear-mass correction. Away from this near-cutoff point, shifts are generally at the ppm-to-hundreds-of-ppm level.

## 6. PCHIP versus direct exact-q response

At the response level, the maximum selected-point PCHIP/direct discrepancy (defined as \(|R_{\rm PCHIP}/R_{\rm exact}-1|\)) is:

- NIST masses: \(8.830600e-03\), Xe-128 at 542 keV;
- AME2020 masses: \(8.799406e-03\), Xe-128 at 542 keV.

The total-rate impact is smaller because the isotope terms are abundance- and kinematics-weighted:

| Benchmark | \(E_R\) [keV] | Halo | NIST direct vs PCHIP [ppm] | AME2020 direct vs PCHIP [ppm] |
|---|---:|---|---:|---:|
| red_ms200_dm1 | 101 | shm_cutoff | +1.778 | +1.719 |
| red_ms200_dm1 | 101 | mb_untruncated | +2.275 | +2.216 |
| green_ms300_dm1 | 101 | shm_cutoff | -1.879 | -1.892 |
| green_ms300_dm1 | 101 | mb_untruncated | +0.862 | +0.803 |
| black_ms360_dm1 | 101 | shm_cutoff | +0.000 | +0.000 |
| black_ms360_dm1 | 101 | mb_untruncated | -0.183 | -0.242 |
| blue_ms300_dm10 | 101 | shm_cutoff | -1.879 | -1.892 |
| blue_ms300_dm10 | 101 | mb_untruncated | +0.876 | +0.817 |
| green_ms300_dm1 | 200 | shm_cutoff | -0.004 | -0.004 |
| green_ms300_dm1 | 200 | mb_untruncated | -0.003 | -0.003 |
| green_ms300_dm1 | 267 | shm_cutoff | +13.956 | +13.957 |
| green_ms300_dm1 | 267 | mb_untruncated | +15.995 | +15.999 |
| green_ms300_dm1 | 542 | shm_cutoff | -3.723 | -3.768 |
| green_ms300_dm1 | 542 | mb_untruncated | -3.242 | -3.326 |

The maximum total-rate shift is **15.995 ppm** for NIST and **15.999 ppm** for AME2020. The 0.25 MeV response-grid interpolation can therefore be locally inaccurate near narrow minima, while its impact on these selected total rates is at the ppm level.

## 7. Xe-131-only AME2020 hybrid diagnostic

This diagnostic preserves the six non-Xe-131 terms at the archived NIST/PCHIP baseline and replaces only the Xe-131 term with the AME2020 direct exact-q 32-node partial rate. It is **not** a full AME2020 natural-xenon prediction.

| Benchmark | \(E_R\) [keV] | Halo | Hybrid total shift vs historical NIST [ppm] |
|---|---:|---|---:|
| black_ms360_dm1 | 101 | mb_untruncated | +15.208 |
| black_ms360_dm1 | 101 | shm_cutoff | n/a |
| blue_ms300_dm10 | 101 | mb_untruncated | +15.277 |
| blue_ms300_dm10 | 101 | shm_cutoff | +0.000 |
| green_ms300_dm1 | 101 | mb_untruncated | +15.277 |
| green_ms300_dm1 | 101 | shm_cutoff | +0.000 |
| green_ms300_dm1 | 200 | mb_untruncated | +1.080 |
| green_ms300_dm1 | 200 | shm_cutoff | +5.176 |
| green_ms300_dm1 | 267 | mb_untruncated | +0.283 |
| green_ms300_dm1 | 267 | shm_cutoff | +0.554 |
| green_ms300_dm1 | 542 | mb_untruncated | -11.915 |
| green_ms300_dm1 | 542 | shm_cutoff | -2.106 |
| red_ms200_dm1 | 101 | mb_untruncated | +15.206 |
| red_ms200_dm1 | 101 | shm_cutoff | +15.274 |

The maximum absolute hybrid total shift is **15.277 ppm**. This supersedes the earlier provisional PCHIP-based Xe-131-only hybrid estimate.

## 8. Reproducibility files

- `run_ame2020_direct_exactq_natural_xenon_halo_fold.py`: standalone local runner; direct exact-q is primary, PCHIP is diagnostic only.
- `base_kernel_halo_integrals.csv`: 392 isotope/benchmark/halo/mass/speed-order integrals.
- `seven_isotope_contributions.csv`: isotope-level direct exact-q and PCHIP-diagnostic rates.
- `seven_isotope_halo_rates.csv`: totals for both mass schemes, both halo prescriptions, both speed orders and both response prescriptions.
- `response_interpolation_impact.csv`, `mass_scheme_comparison.csv`, `xe131_only_ame2020_hybrid_direct_exactq.csv`.
- `speed_quadrature_convergence.csv`, `isotope_speed_quadrature_convergence.csv`, `kernel_quadrature_convergence.csv`.
- `nist_mainline_reproduction.csv`, `nuclear_mass_scheme_comparison.csv`, `metadata.json`, `SHA256SUMS.txt`.

The runner can reuse the archived local integral and kernel-crosscheck tables with `--integral-cache` and `--kernel-crosscheck-cache`; without these options it recomputes locally. No CI is required.

## 9. Scientific boundary

The selected-point direct exact-q fold is locally recomputed and passes the stated speed- and kernel-quadrature comparisons. It does not validate a continuous recoil spectrum, does not provide AFH central responses for Xe-124/Xe-126, and does not include detector effects or a likelihood. The 2401-node PCHIP rates remain historical comparison values only.

## 10. Repository archive layout and checksum audit

The native numerical bundle is intended to be committed on the PR #14 research branch under `research/afh_default_density_natural_xenon_halo/`:

- `run_ame2020_direct_exactq_natural_xenon_halo_fold.py`: standalone local calculation runner; it uses the repository's existing Eq. (6) kernel, isotope-mass module, and kinematics module.
- `validate_ame2020_direct_exactq_outputs.py`: local row-count, numerical-convergence, NIST-reproduction, non-negativity, and output-manifest validator.
- `input/afh_selected_exact_q_responses.csv`: the 56 direct exact-q AFH response values.
- `output/ame2020_direct_exactq_fold/base_kernel_halo_integrals.csv`: all 392 kernel/halo integrals.
- `output/ame2020_direct_exactq_fold/seven_isotope_contributions.csv`: all 784 isotope-level contributions.
- `output/ame2020_direct_exactq_fold/`: the remaining rate summaries, NIST/AME2020 comparisons, Xe-131 hybrid diagnostic, convergence tables, metadata, and output-level `SHA256SUMS.txt`.
- `AME2020_DIRECT_EXACT_Q_SHA256SUMS.txt`: bundle-level manifest covering this report, both Python programs, the 56-point input, and every native output file. It deliberately excludes itself, as a checksum manifest cannot hash itself.

The output-level manifest contains 12 entries and was independently checked against every listed file. The bundle-level manifest contains 17 entries. An independent summation of the seven isotope terms reproduces all 112 stored rate summaries with a maximum relative residual of 2.028e-16. The local validator passed with the archived data: 392 integrals, 784 isotope contributions, 112 total-rate summaries, 14 NIST reproduction rows, 56 speed-convergence rows, 392 isotope speed-convergence rows, 21 kernel-convergence rows, and 14 Xe-131 hybrid rows; it also checks all 56 exact-q input keys and isotope-sum closure.

From the repository root, validate the archived outputs with:

```bash
python research/afh_default_density_natural_xenon_halo/validate_ame2020_direct_exactq_outputs.py \
  --results-dir research/afh_default_density_natural_xenon_halo/output/ame2020_direct_exactq_fold
```

To rerun the selected-point fold using the archived exact-q response input and cached integral/kernel tables, use:

```bash
python research/afh_default_density_natural_xenon_halo/run_ame2020_direct_exactq_natural_xenon_halo_fold.py \
  --response-csv research/afh_default_density_natural_xenon_halo/input/afh_selected_exact_q_responses.csv \
  --integral-cache research/afh_default_density_natural_xenon_halo/output/ame2020_direct_exactq_fold/base_kernel_halo_integrals.csv \
  --kernel-crosscheck-cache research/afh_default_density_natural_xenon_halo/output/ame2020_direct_exactq_fold/kernel_quadrature_convergence.csv \
  --out-dir /tmp/ame2020_direct_exactq_reproduced
```

Omitting the two cache arguments performs the corresponding local numerical integrations again. No GitHub Actions runner is needed for either validation or recomputation.

The runner here means the local Python calculation program; it is not a self-hosted GitHub Actions Runner registration. The numerical results were computed locally, and no CI run is used as evidence for the numerical acceptance.
