# Fig. 2 source-versus-reproduction audit

**Date:** 2026-11-19  
**Status:** reproducible diagnostic; source-figure input discrepancy open.

## Finding

The independent calculation reproduces the characteristic fixed-speed 2→2 flat spectrum and 2→3 single-peaked spectrum. It does not reproduce every digitized source coordinate at nominal 780 km/s using adopted masses mχ1=1 TeV and m_T=122 GeV. The source curves were digitized from PDF vector paths, not raster pixels.

## Exact calculation

Using source Eqs. (90)–(92), define ΔW²(E_R)=W_max²(E_R)−(mχ+m_s)². Then

ΔW² = 2p_in sqrt[E_R(E_R+2m_T)] − 2(Eχ+m_T)E_R − 2mχm_s − m_s².

The 2→3 shape is proportional to ∫₀^ΔW² ds sqrt[s(4mχm_s+s)]/[(mχ+m_s)²+s], and vanishes for ΔW²≤0. The substitution s=ΔW²u² regularizes the lower endpoint. The 2→2 shape is constant on the same exact matched-threshold interval. Each channel is normalized independently.

## Numerical comparison

| Quantity | Exact, 780 km/s | Source vector path | Exact minus source |
|---|---:|---:|---:|
| 2→2 lower endpoint (keV) | 106.59121 | 108.45828 | −1.86707 |
| 2→2 upper endpoint (keV) | 670.71072 | 660.26045 | +10.45027 |
| 2→2 plateau (10^-3/keV) | 1.772674 | 1.814691 | −2.315% |
| 2→3 peak position (keV) | 328.01521 | 326.42159 | +1.59362 |
| 2→3 peak height (10^-3/keV) | 3.025467 | 3.093101 | −2.187% |

The heavy-particle limit gives endpoints 106.59252 and 670.70274 keV; maximum endpoint difference from the exact result is 0.00799 keV.

## Quadrature and normalization

- Internal recoil grid: 701 points.
- Stored output spacing: 5 keV, plus exact endpoints and peak positions.
- Gauss–Legendre order: 512.
- Maximum relative difference between orders 256 and 512: 2.34×10^-15.
- Both normalized spectra integrate to unity to numerical precision.

## Conditional speed inversion

Holding adopted masses fixed, the source 2→2 endpoints imply 777.578965 km/s in the heavy-particle endpoint relation. At this speed the exact endpoints are 108.155 and 661.015 keV; the 2→3 peak is 325.982 keV with height 3.08656×10^-3 keV^-1. The mean absolute relative residual over source red-curve points with ordinate above 0.15 falls to 0.44%, from 4.94% at 780 km/s.

This is not a fitted production input. It shows only that a small effective-speed shift, conditional on adopted masses, accounts for most of the visible discrepancy. Fig. 2 omits mχ1, so the original plotting inputs must be recovered before diagnosing the cause.

## Caption/ordinate inconsistency

The caption says “ratio of the differential recoil cross sections,” whereas the ordinate is (1/σ)dσ/dE_R with units 10^-3/keV and the panel shows two independently normalized curves. A true ratio is dimensionless and would be one curve. This is a manuscript-level caption issue, separate from the numerical phase-space check.

## Disposition

- Retain exact 780 km/s as the primary calculation.
- Retain conditional 777.579 km/s overlay as diagnostic only.
- Do not tune the primary benchmark to the source plot.
- Recover exact mχ1, target mass, and speed used by the plotting script.
- Resolve the caption and ordinate before treating Fig. 2 as a final paper figure.
