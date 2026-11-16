# Mathematica/Python full Xe-131 differential-cross-section cross-check

**Status: native Wolfram execution and 652-row pointwise Mathematica/Python comparison completed; corrected comparison metadata reports PASS.**

This review records both the source-level agreement of the native Wolfram Language runner and independent Python implementation, and the completed 652-row numerical execution. It checks matched physical inputs, phase-space measure, spin trace, width prescription, AFH response convention, cross-section prefactor and the pointwise result.

## 1. Matched inputs and output grid

| Input | Mathematica | Python comparator |
|---|---|---|
| \(m_{\chi_1}\) | 1000 GeV | 1000 GeV |
| \(m_V\) | 10 GeV | 10 GeV |
| \(m_A\) | \(131\times0.93149410242\) GeV | same |
| Incident speed | 800 km/s | 800 km/s |
| Coupling product squared | \(10^{-8}\) | \(10^{-8}\) |
| \(g_2\) for conditional pole width | 1 | 1 |
| Width | pole width | pole width |
| \(W^2\) mapping | threshold-\(u^2\) | threshold-\(u^2\) |
| Quadrature | \(16\times16\times8\) | reads each Mathematica row and repeats its order |
| Benchmarks | red, green, black, blue | same four benchmark definitions |

The requested recoil grid is \(5,10,\ldots,800\) keV plus the explicit anchors
101, 200, 267 and 542 keV. Since 200 keV is already on the regular grid,
there are 163 distinct recoil energies and 652 benchmark-energy rows.

For the green smoke point at 800 km/s with \(m_s=300\) keV, 101 keV is
kinematically open: \(W_{\max}^2-W_{\min}^2=0.0112695\) GeV\(^2\).
Do not carry over the 101-keV closed status from the separate historical
mapping audit, which used 776 km/s and zero width.

The calculation is Xe-131 at one fixed incident speed. It is not a halo fold,
natural-xenon isotope sum, detector prediction, or LZ likelihood.

## 2. Kinematics and phase-space mapping

Both implementations use exact spatial recoil momentum
\[
q=\sqrt{2m_AE_R+E_R^2},
\]
and
\[
W_{\min}^2=(m_{\chi_1}+m_s)^2,\qquad
W_{\max}^2=m_{\chi_1}^2+2p_{\chi_1}q
-2(E_{\chi_1}+m_A)E_R.
\]

For the threshold-regularized map,
\[
W^2=W_{\min}^2+\Delta W_{\max}^2u^2,\qquad
u=\frac{x+1}{2},\quad x\in[-1,1],
\]
the Jacobian is
\[
dW^2=2\Delta W_{\max}^2u\,du.
\]
The Wolfram and Python implementations use the same nodes, transformed
weights, and threshold invariant
\[
\lambda_{\rm dim}
=\frac{\Delta W^2(4m_{\chi_1}m_s+\Delta W^2)}{W^4}.
\]

Both integrate \(z\in[-1,1]\). Python maps Gauss-Legendre nodes to
\(\phi=\pi(x_\phi+1)\) and uses weights \(w_\phi/2\) for the azimuthal
average. Mathematica integrates over \([0,2\pi]\) and divides its mapped
weights by \(2\pi\); these are the same measure.

## 3. Matrix element and width

Both implementations use the Dirac representation with metric \((+---)\),
the same two scalar-emission diagrams, their interference, and the initial
spin average \(1/2\):
\[
L_{00}=\frac12\operatorname{Tr}
\left[(\slashed p'+m_{\chi_1})\Gamma
(\slashed p+m_{\chi_1})\bar\Gamma\right].
\]

The conditional pole width is the Dirac, pure-scalar, \(\chi_2\to\chi_1s\)
two-body width with \(g_2=1\), and is evaluated at
\(m_{\chi_2}=m_{\chi_1}+\Delta m\). It is not a full vector-plus-scalar
self-energy calculation. The width prescription is matched between codes.

A numerical-stability improvement was made in the Wolfram implementation:
the second propagator denominator is evaluated as
\[
d_2=W^2-m_{\chi_2}^2+i\,m_{\chi_2}\Gamma_{\rm pole},
\]
rather than reconstructing \(W^2\) from the large four-vector
\((p'+k)^2\). The code separately checks that
\((p'+k)^2=W^2\) within the kinematic tolerance. This is algebraically the
same invariant used by Python and avoids unnecessary cancellation near the
heavy-\(\chi_2\) pole.

## 4. AFH response and factor-four ledger

The native Mathematica AFH table is reused; it is not regenerated. The
Wolfram script reads its 2401-node \(q\), package-response, and physical-response
columns. At \(q=0\),
\[
C_0=\frac{A^2}{4R_{\rm package}(0)},\qquad
R_A^{\rm phys}(q)=4C_0R_{\rm package}(q).
\]
The same shape-preserving PCHIP interpolation is used in Mathematica and
SciPy. The archived 2401-node native AFH comparison has a maximum relative
difference of \(3.59\times10^{-9}\); the response comparison therefore uses
\(2\times10^{-8}\), not a tighter tolerance that would reject the already
validated source translation.

The full cross section is assembled as
\[
\frac{d\sigma_A}{dE_R}
=
\frac{m_A(g_1g_2g_{VN})^2}
{256\pi^3p_{\chi_1}^2(m_V^2+2m_AE_R)^2}
R_A^{\rm phys}(q)\,I_6.
\]
The no-factor-four control replaces \(R_A^{\rm phys}\) by
\(R_A^{\rm phys}/4\), leaving the remaining prefactor and \(I_6\) unchanged.
Thus the two cross-section outputs must differ by exactly four. The factor
four is not inserted again into the Eq. (6) prefactor.

The conversion from GeV\(^{-3}\) to cm\(^2\)/keV uses
\(0.3893793721\times10^{-33}\).

## 5. Acceptance criteria

| Quantity | Acceptance |
|---|---:|
| \(I_6\), pointwise Mathematica/Python | \(2\times10^{-7}\) relative |
| \(d\sigma_A/dE_R\), pointwise Mathematica/Python | \(2\times10^{-7}\) relative |
| AFH PCHIP response | \(2\times10^{-8}\) relative |
| \(q\), \(C_0\), factor-four mapping/ratio, per-code unit-conversion identities and kinematic identities | \(2\times10^{-12}\) relative |
| Full-grid output | exactly 652 rows |
| Cross-code comparison of converted \(d\sigma_A/dE_R\) | \(2\times10^{-7}\) relative, same as the GeV\(^{-3}\) observable |
| Native no-factor-four ratio on open points | \(d\sigma/d\sigma_{\rm no4}=4\) within \(8\times10^{-12}\) absolute |

The Python comparator independently recomputes \(I_6\) at the quadrature order recorded in every Mathematica row. It then independently interpolates the Python AFH table and assembles both the physical and no-factor-four cross sections. The converted cross-section comparison is a second representation of the same physical observable, so it uses the same \(2\times10^{-7}\) cross-code tolerance as \(d\sigma_A/dE_R\). The conversion factor itself is tested separately within each implementation against \(0.3893793721\times10^{-33}\) at \(2\times10^{-12}\).

## 6. Executed full-grid result — 2026-11-16

The native Wolfram 14.2.0 run completed all four benchmarks on the full 163-energy grid (652 rows total; 500 open and 152 closed). The Python comparator independently recomputed \(I_6\), AFH PCHIP responses and both physical/no-factor-four cross sections.

| Quantity | Maximum relative difference / residual | Acceptance |
|---|---:|---:|
| \(I_6\) | \(1.33872\times10^{-12}\) | \(2\times10^{-7}\) |
| Physical \(d\sigma_A/dE_R\) | \(2.57632\times10^{-9}\) | \(2\times10^{-7}\) |
| No-factor-four \(d\sigma_A/dE_R\) | \(2.57632\times10^{-9}\) | \(2\times10^{-7}\) |
| AFH physical/package PCHIP response | \(2.57510\times10^{-9}\) | \(2\times10^{-8}\) |
| Factor-four mapping | \(4.30300\times10^{-16}\) | \(2\times10^{-12}\) |
| Physical/no-factor-four ratio | 0 | \(2\times10^{-12}\) |
| Mathematica unit-conversion identity | \(4.44089\times10^{-16}\) | \(2\times10^{-12}\) |
| Python unit-conversion identity | 0 | \(2\times10^{-12}\) |
| Cross-code converted \(d\sigma_A/dE_R\) | \(2.57632\times10^{-9}\) | \(2\times10^{-7}\) |

The original comparator incorrectly treated the cross-code difference between the converted rates as a pure unit-conversion identity. That difference inherits the already-accepted AFH response translation difference. The corrected comparator now tests each code's own conversion identity independently at 2e-12, while comparing the converted physical observable across codes at the same 2e-7 tolerance as the unconverted observable. No physics tolerance was relaxed.

The machine-readable result is `output/full_dsigma_mathematica/mathematica_python_full_dsigma_comparison.json` (status `PASS`); the row-level comparison and refreshed SHA-256 checksums are in the same directory. This is fixed-speed Xe-131 only and is conditional on the stated Dirac / real-scalar / pure-scalar / single-channel pole-width assumptions. It is not a halo fold, natural-xenon sum or LZ likelihood.


## 7. Quick smoke test before the full grid

The PowerShell wrapper now supports a reduced benchmark/recoil selection.
From the study directory on Windows, this command checks one benchmark at
the four explicit anchor energies; phase-space openness is evaluated from the 800 km/s kinematics for this benchmark:

~~~powershell
.\run_native_full_dsigma_windows.ps1 -OutputDirectory "$env:TEMP\lz-xe131-smoke" -Benchmark "green_ms300_dm1" -ERListKeV "200" -NW 8 -NZ 8 -NPhi 4 -RequireFullGrid:$false
~~~

The WLS script deliberately appends the four explicit anchor energies even
when ERListKeV is supplied. This smoke test checks Wolfram syntax, output
generation, the independent Python comparison, and the factor-four ledger;
it is not a quadrature-convergence result. The full run uses the default
652-row grid and \(16\times16\times8\) order.

## 8. Independent kinematic preflight for the full grid

Before launching Mathematica, the complete 163-energy grid was checked
independently from
\[
W_{\min}^2=(m_{\chi_1}+m_s)^2,\qquad
W_{\max}^2=m_{\chi_1}^2+2p_{\chi_1}q
-2(E_{\chi_1}+m_A)E_R.
\]
At \(v_\chi=800\) km/s, the number of open points is:

| Benchmark | Open points | Closed points | First open \(E_R\) | Last open \(E_R\) |
|---|---:|---:|---:|---:|
| red, \(m_s=200\) keV, \(\Delta m=1\) MeV | 157 | 6 | 35 keV | 800 keV |
| green, \(m_s=300\) keV, \(\Delta m=1\) MeV | 134 | 29 | 100 keV | 750 keV |
| black, \(m_s=360\) keV, \(\Delta m=1\) MeV | 75 | 88 | 190 keV | 550 keV |
| blue, \(m_s=300\) keV, \(\Delta m=10\) MeV | 134 | 29 | 100 keV | 750 keV |
| **Total** | **500** | **152** | | |

No grid point reaches the on-shell \(\chi_2\) pole:
\[
W_{\max}^2 < m_{\chi_2}^2
\quad\text{for every benchmark and recoil energy.}
\]
The smallest pole clearance \(m_{\chi_2}-\sqrt{W_{\max}^2}\) among open
points is 0.6128 MeV for the three \(\Delta m=1\) MeV benchmarks and
9.6128 MeV for the \(\Delta m=10\) MeV benchmark. Thus the Wolfram runner's
on-shell guard should not terminate this specified grid. This is a
kinematics-only preflight, not an evaluation of \(I_6\).

For the green smoke point, all four anchor energies 101, 200, 267 and
542 keV are open; their \(W_{\max}^2-W_{\min}^2\) values are respectively
0.0112695, 0.1303047, 0.1632136 and 0.1247922 GeV\(^2\).

## 9. Scientific status

- AFH factor-four normalization: already validated at the 2401-node response
- Python-only v=800 km/s fixed-speed Xe-131 Eq. (6) and factor-four ledger under the conditional Dirac / real-scalar / pure-scalar / single-channel pole-width assumptions: PASS on 652 rows (500 open, 152 closed), 16 high-order anchors, maximum I6 relative difference 1.66367e-11, factor-four mapping residual 3.55679e-16, and physical/no-factor-four ratio residual 0. This validates the transfer within the Python implementation only.
  level by the archived native Mathematica/Python audit.
- Historical green \(I_6\) mapping audit: complete; see
  [HISTORICAL_I6_MAPPING_AUDIT.md](HISTORICAL_I6_MAPPING_AUDIT.md).
- Native Mathematica/Python full \(d\sigma_A/dE_R\): **PASS_WITH_NOTES** on 652 rows (500 open, 152 closed); max \(I_6\) difference 1.34e-12, \(d\sigma\) difference 2.58e-9, AFH response difference 2.58e-9, factor-four mapping residual 4.30e-16. Per-code unit-conversion identities pass at 2e-12; cross-code converted-rate comparison is within the 2e-7 observable tolerance.
- Detector response and final LZ likelihood: outside this Xe-131 fixed-speed cross-code validation.
  output CSV, and SHA-256 manifest have been reviewed.
- Detector response and final LZ likelihood: outside this Xe-131 fixed-speed
  cross-code validation.
