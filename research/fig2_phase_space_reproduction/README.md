# Fixed-speed Fig. 2 reproduction: matched-threshold 2→2 and 2→3 spectra

**Status:** reproducible diagnostic; source-figure input discrepancy remains open.

## Scope

Independently reproduce the fixed-incident-speed recoil curves in source Fig. 2 for matched thresholds δ_iDM = m_s. This is a constant-amplitude phase-space benchmark, not the full three-body amplitude, nuclear-response calculation, natural-xenon halo fold, or detector prediction. The finite-size response R_A(E_R) is omitted as stated in the source caption.

## Benchmark and conventions

| Input | Value | Provenance |
|---|---:|---|
| Incident speed | 780 km/s | Fig. 2 panel title |
| Scalar mass | 300 keV | Fig. 2 panel title |
| iDM threshold | 300 keV | Matched to m_s |
| Dark-matter mass | 1 TeV | Adopted from adjacent natural-xenon benchmark; not stated in Fig. 2 caption |
| Target mass | 122 GeV | Fixed comparison input for this exact-relativistic diagnostic; not source-confirmed. The later Fig. 2 endpoint/shape inversion in [the 2026-11-19 target-mass trial](../three_body_calculation_and_validation/fig2_target_mass_reproduction_trial_20261119/README.md) indicates an effective mass near 121.04 GeV. This record retains 122 GeV as a separate comparison case, not as the inferred original input. |
| Nuclear response | Omitted | Fig. 2 caption |

The plotted ordinate is P_i(E_R) = (1/σ_i) dσ_i/dE_R, with each channel independently normalized to unit area. The common target-current factor (2m_T)^2 is independent of E_R and cancels in this normalization.

## Exact relativistic phase space

Source-PDF Eqs. (90)–(92) give

dΦ_3/dE_R = [1/(128π^3 p_in)] ∫ dW² λ^(1/2)(W²,mχ²,m_s²)/W²,

with integration from (mχ+m_s)² to W_max²(E_R), and

W_max² = mχ² − 2(Eχ+m_T)E_R + 2 p_in sqrt[E_R(E_R+2m_T)].

At fixed incident speed the prefactor cancels after unit-area normalization. The integral is evaluated with the threshold-regularized variable s = W²−(mχ+m_s)² = ΔW² u² and Gauss–Legendre quadrature. For a constant 2→2 matrix element, the recoil spectrum is flat on the exact matched-threshold interval.

The independent heavy-particle check uses source Eqs. (95)–(97): D = vq−q²/(2μ)−m_s, q = sqrt(2m_T E_R), and I(D) = ∫₀ᴰ dε sqrt[ε(ε+2m_s)], with dσ_2→3/dE_R proportional to I(D).

## Source-PDF provenance and digitization

- Source: user-provided 3body_for_HDM.pdf / 3body_for_HDM(1).pdf.
- SHA-256: b4fc7bd73265df2bc2ce1640cbf8847b63323ec1dda220f9e7903f4620b871bb.
- PDF page: 3.
- Original blue and orange curves were extracted from PDF vector drawing paths, not raster pixels.
- The PDF itself is not redistributed in this research folder.

## Files

- reproduce_fig2.py: reproduction and vector-path extraction.
- data/paper_fig2_vector_digitized.csv: vector-drawn source curve coordinates and calibrated values.
- data/fig2_spectra_780km_s.csv: 5-keV sampled spectra and kinematic diagnostics.
- data/fig2_summary.json: numerical summary and source comparison.
- figures/fig2_reproduction_overlay.svg: stated-780-km/s overlay.
- figures/fig2_effective_speed_diagnostic.svg: conditional effective-speed diagnostic.
- tests/test_reproduce_fig2.py: regression tests.
- requirements.txt: dependencies.
- run_manifest.json and SHA256SUMS.txt: run provenance and checksums.

## Reproduction

From this directory:

    python -m pip install -r requirements.txt
    python reproduce_fig2.py --quadrature-order 512 --n-grid 701
    python -m unittest discover -s tests -v

To re-extract vector paths from the source PDF, pass --source-pdf /path/to/3body_for_HDM.pdf. The script checks the recorded source-PDF SHA-256.

## Numerical results

For mχ1=1 TeV, m_T=122 GeV, m_s=300 keV, and v=780 km/s:

| Quantity | Exact calculation | Source PDF vector extraction |
|---|---:|---:|
| 2→2 lower endpoint (keV) | 106.5912 | 108.4583 |
| 2→2 upper endpoint (keV) | 670.7107 | 660.2604 |
| 2→2 normalized plateau (10^-3/keV) | 1.77267 | 1.81469 |
| 2→3 peak position (keV) | 328.0152 | 326.4216 |
| 2→3 peak height (10^-3/keV) | 3.02547 | 3.09310 |

The maximum relative difference between 256- and 512-point Gauss–Legendre quadrature is 2.34×10^-15. Exact relativistic and heavy-particle endpoints differ by at most 0.00799 keV.

The characteristic shapes are reproduced, but the 780-km/s result does not match every source vector coordinate: the source plateau is narrower, its normalized height is 2.32% higher, and its 2→3 peak is 1.59 keV lower and 2.19% higher.

## Updated interpretation of the target-mass input (2026-11-20)\n\nThe 122 GeV value in this exact-relativistic reproduction is an adopted comparison input, not a value stated in the Fig. 2 caption or independently established as the author's original target mass. The subsequent vector-path endpoint inversion and normalized red-shape fit in the linked target-mass reproduction trial give approximately 121.04 GeV; the mass-number approximation \\(130u\\) is numerically consistent at figure-reading precision, but the source paper does not explicitly identify an A=130 target. Therefore, preserve the 122 GeV calculation as a reproducible comparison benchmark and do not cite it as the recovered Fig. 2 source input.\n\n## Conditional effective-speed diagnostic

Holding the adopted masses fixed, the source 2→2 endpoints imply 777.578965 km/s through the heavy-particle endpoint relation. At this speed the exact calculation gives endpoints 108.155 and 661.015 keV, a 2→3 peak at 325.982 keV, and peak height 3.08656×10^-3 keV^-1. The mean absolute relative residual against source red-curve points above 0.15 falls from 4.94% at 780 km/s to 0.44%.

This is a diagnostic inversion only, not evidence that the original plotting script used this speed. The Fig. 2 caption omits mχ1, and the target mass is also an adopted input.

## Caption/ordinate audit

The source caption calls Fig. 2 a “ratio of the differential recoil cross sections,” but the plotted ordinate has units of inverse energy and shows two independently normalized spectra. A true ratio would be dimensionless and a single curve. This discrepancy should be resolved in a manuscript edit after the original plotting inputs are recovered.

## Status and remaining work

Validated within this diagnostic scope: exact phase-space implementation, threshold behavior, unit-area normalization, heavy-particle endpoint limit, quadrature convergence, and PDF vector-path extraction.

Not established: exact agreement at stated 780 km/s, the original unreported mχ1 input, full three-body matrix-element effects, finite-size nuclear response, natural-xenon isotope sum, halo folding, or detector-level prediction.

Next work: recover the original plotting inputs (especially mχ1 and precise speed) and resolve the caption/ordinate mismatch. The primary 780-km/s result is retained without parameter tuning.
