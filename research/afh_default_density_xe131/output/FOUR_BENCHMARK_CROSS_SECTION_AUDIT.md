# Xe-131: four benchmark differential cross sections

Canonical filenames and the superseded historical CSV are indexed in
[CROSS_SECTION_FILE_INDEX.md](CROSS_SECTION_FILE_INDEX.md). Use
`figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv` for the canonical
long-form table and `figure2_four_benchmarks_AFH_GCN_JJ55_wide_audit.csv` for
the wide comparison. Do not use the historical
`figure2_four_benchmarks_dsigma_AFH_GCN_JJ55.csv`.

## Fixed inputs

- Target: Xe-131, \(m_A=122.02572742\) GeV.
- \(m_{\chi_1}=1\) TeV; \(m_V=10\) GeV; \(g_2=1\).
- \((g_1g_2g_{VN})^2=10^{-8}\).
- Fixed incident speed: \(v=800\) km/s.
- Recoil grid: 5--800 keV in 5-keV steps.
- Nuclear responses: AFH v6.0 default Xe-131, GCN, JJ55.
- AFH default oscillator length: \(b_{131}=2.2923417985218975\) fm.

## Four benchmarks

| Curve | \(m_s\) | \(\Delta m\) | First open grid point |
|---|---:|---:|---:|
| Red | 200 keV | 1 MeV | 35 keV |
| Green | 300 keV | 1 MeV | 100 keV |
| Black | 360 keV | 1 MeV | 190 keV |
| Blue | 300 keV | 10 MeV | 100 keV |

## AFH normalization

The raw AFH isoscalar output satisfies
\[
\frac{4\pi}{2J_A+1}W_{M,\mathrm{AFH}}^{00}(0)\simeq\frac{A^2}{4}.
\]
For equal physical proton/neutron couplings, the response entering the cross section is four times this raw AFH response, normalized to \(R_A(0)=A^2=17161\). The factor of four is included exactly once.

## AFH response momentum

AFH uses \(y=(q b_A/2)^2\), where q is the spatial momentum transfer. The
four-benchmark response interpolation uses the exact recoil momentum
\(q=\sqrt{2M_AE_R+E_R^2}\), consistent with the exact nuclear mass shell and
the three-body kinematics. The relation \(q_{\rm NR}=\sqrt{2M_AE_R}\) is a
small-recoil approximation; its effect near the Xe-131 response minima is
quantified in research/docs/appendices/09G_recoil_momentum_convention_audit.md.

## Integration and cross-section assembly

The three-body integral \(I_6\) is independent of the nuclear response and therefore common to AFH, GCN and JJ55 at fixed benchmark and \(E_R\). The archived \(I_6\) grid is reused; only \(R_A(E_R)\) changes. This is an exact factorization of the stated cross-section formula, not a second independent integral for each nuclear model.

The cross section is evaluated as
\[
\frac{d\sigma_A}{dE_R}=
\frac{m_A(g_1g_2g_{VN})^2}{256\pi^3p_{\chi_1}^2}
\frac{R_A(E_R)I_6(E_R)}{(m_V^2+2m_AE_R)^2}.
\]

The AFH response is interpolated from the 2401-point source-derived table with PCHIP and no extrapolation. GCN/JJ55 retain their previously validated response tables.

## Numerical checks

- Full table: 1920 rows (4 benchmarks × 3 nuclear responses × 160 recoil points).
- Reconstructing every open-point cross section from the displayed \(R_A\) and \(I_6\) gives maximum relative residual \( 0.00e+00\).
- The AFH physical response satisfies \(R_A(0)=A^2\).
- Independent quadrature spot checks at 12 points compare 24×24×12 with 32×32×16; the maximum relative difference is \(5.996\times10^{-6}\).
- The archived 16×16×8 \(I_6\) grid differs from the 32×32×16 spot checks by at most about \(3\times10^{-5}\) at the tested representative points.

## Important scope limits

- \(v=800\) km/s is a fixed-speed Figure-2 reproduction diagnostic, not a halo-averaged prediction or a typical halo speed.
- The pole width is conditional on Dirac fermions, a real scalar and a pure scalar off-diagonal Yukawa interaction; it is not a complete model self-energy.
- This file contains differential cross sections only. No event-rate spectra, natural-xenon isotope sum, halo velocity integration, detector response or likelihood are included.
- The AFH-native Mathematica runner is prepared, but a Wolfram kernel is not installed in the current execution environment; native Mathematica/Python point-by-point validation remains pending.