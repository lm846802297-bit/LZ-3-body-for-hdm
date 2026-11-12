# AME2020 natural-xenon direct exact-q recalculation

**Date:** 2026-11-12  
**Execution:** local Python only; no GitHub Actions / CI used  
**Input branch HEAD:** fd325c13e0aa82f7c829fa85a3ee3a744e5d8e03

## Scope

Recomputed the selected-point seven-isotope natural-xenon three-body halo fold using direct AFH finite-sum responses at the exact spatial momentum transfer. The response input contains 56 points: 7 isotopes × 4 recoil energies (101, 200, 267, 542 keV) × 2 mass schemes (NIST nuclear and AME2020/CODATA-2022 nuclear).

Primary results use direct exact-q values independently checked against 60-digit mpmath. The historical 2401-node PCHIP values are retained only as a diagnostic. The seven AFH-supported isotopes are Xe-128, 129, 130, 131, 132, 134 and 136; their natural abundance coverage is 0.998158 and is not renormalized. Xe-124 and Xe-126 remain absent from the AFH central prediction.

The exact momentum is q_A = sqrt(2 m_A E_R + E_R^2). The output is a selected-point differential rate, not a continuous recoil spectrum or detector-level LZ prediction.

## Numerical method

- Existing Eq. (6) spin-trace kernel.
- Baseline kernel quadrature: 8 × 8 × 4 in (W²,z,φ*).
- Speed Gauss-Legendre orders: 32 and 64.
- Independent kernel check: 16 × 16 × 8 at three anchors for all seven isotopes (21 comparisons).
- Pole-width prescription for χ₂ → χ₁s, under the existing Dirac χ₂ / real scalar / pure off-diagonal scalar coupling assumptions.
- mχ₁ = 1 TeV, mV = 10 GeV, coupling-product squared = 10⁻⁸, g₂ = 1, ρχ = 0.3 GeV cm⁻³.
- v₀ = 220 km/s, vE = 232 km/s, vesc = 544 km/s; untruncated-MB diagnostic integrated to 1600 km/s.
- Rates are in events/(kg day keV), before detector response, efficiency, exposure, cuts or likelihood.

## Local numerical acceptance

| Check | Maximum relative difference |
|---|---:|
| Recomputed NIST/PCHIP baseline vs archived NIST natural-Xe totals (32 speed nodes) | 3.432 × 10⁻¹² |
| 32 vs 64 speed-node total rates | 3.303 × 10⁻⁶ |
| 32 vs 64 speed-node isotope contributions | 3.330 × 10⁻⁶ |
| Kernel 8×8×4 vs 16×16×8, 21 AME2020 anchor checks | 2.108 × 10⁻⁴ |

The NIST historical PCHIP baseline is reproduced before interpreting the AME2020 mass update.

## Seven-isotope direct exact-q rates

64-node totals; the last column is (AME2020/NIST − 1) × 10⁶.

| Benchmark | ER [keV] | Halo | NIST direct exact-q | AME2020 direct exact-q | Δ [ppm] |
|---|---:|---|---:|---:|---:|
| red_ms200_dm1 | 101 | SHM | 5.281054e-11 | 5.281010e-11 | −8.425 |
| red_ms200_dm1 | 101 | MB | 8.600908e-11 | 8.600796e-11 | −13.031 |
| green_ms300_dm1 | 101 | SHM | 2.599523e-22 | 2.627063e-22 | +10594.376 |
| green_ms300_dm1 | 101 | MB | 1.383664e-12 | 1.383664e-12 | +0.305 |
| black_ms360_dm1 | 101 | SHM | 0 | 0 | 0 |
| black_ms360_dm1 | 101 | MB | 6.223611e-14 | 6.223676e-14 | +10.502 |
| blue_ms300_dm10 | 101 | SHM | 2.167543e-24 | 2.190507e-24 | +10594.242 |
| blue_ms300_dm10 | 101 | MB | 1.107897e-14 | 1.107897e-14 | +0.170 |
| green_ms300_dm1 | 200 | SHM | 1.813604e-11 | 1.813645e-11 | +22.497 |
| green_ms300_dm1 | 200 | MB | 1.646153e-10 | 1.646160e-10 | +4.330 |
| green_ms300_dm1 | 267 | SHM | 2.727153e-13 | 2.727278e-13 | +46.060 |
| green_ms300_dm1 | 267 | MB | 1.787243e-12 | 1.787274e-12 | +17.118 |
| green_ms300_dm1 | 542 | SHM | 1.456132e-15 | 1.456312e-15 | +123.812 |
| green_ms300_dm1 | 542 | MB | 8.170925e-14 | 8.171409e-14 | +59.247 |

The large relative shifts at 101 keV in the green/blue truncated-SHM cases are endpoint-tail effects: only Xe-136 is open and vmin ≈ 775.806 km/s, close to the 776 km/s lab cutoff. The absolute rates are extremely small (≈10⁻²² and ≈10⁻²⁴ events/(kg day keV)); this is not a typical mass-scheme correction.

## PCHIP interpolation impact

The maximum selected response residual, defined as |R_PCHIP/R_exact − 1|, is 8.8306 × 10⁻³ for NIST masses and 8.7994 × 10⁻³ for AME2020 masses (Xe-128, 542 keV).

Despite this local response discrepancy, the maximum shift in the seven-isotope total rate is 15.995 ppm (NIST) and 15.999 ppm (AME2020), for the green 267 keV untruncated-MB point. The PCHIP values therefore remain unsuitable as the primary precision response, even though their total-rate impact at these selected points is ppm-sized.

## Xe-131-only hybrid

The hybrid preserves the six non-Xe-131 terms at the archived NIST/PCHIP baseline and replaces only Xe-131 with its AME2020 direct exact-q 32-node partial rate. It is not a full AME2020 prediction. The maximum absolute hybrid total shift is 15.277 ppm; the complete 14-row table is archived in the numerical output bundle.

## Numerical archive

The full local bundle contains the direct-q runner, local validator, selected exact-q input table, all native result CSVs, metadata and SHA-256 manifest. The principal tables are:

- base_kernel_halo_integrals.csv (392 rows);
- seven_isotope_contributions.csv (784 rows);
- seven_isotope_halo_rates.csv (112 rows);
- speed and kernel quadrature convergence tables;
- NIST baseline reproduction, interpolation impact, mass-scheme comparison and Xe-131 hybrid tables.

The local acceptance validator passed all row-count, NIST reproduction, speed convergence, kernel convergence and SHA-256 checks. The calculation was executed locally; no CI was used.

## Scope boundary

This validates the four selected recoil energies for the seven AFH-supported isotopes. It does not establish a continuous recoil spectrum, AFH central responses for Xe-124/Xe-126, or a detector-level LZ likelihood result.
