# Mathematica/Python full Xe-131 differential-cross-section cross-check

**Status: code-level review complete; native Wolfram execution and pointwise PASS are still pending.**

This review checks that the native Wolfram Language runner and the independent Python implementation use the same physical inputs, phase-space measure, spin trace, width prescription, AFH response convention, and cross-section prefactor. It is not a numerical execution report.

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
| \(q\), \(C_0\), factor-four mapping/ratio, unit conversion and kinematic identities | \(2\times10^{-12}\) relative |
| Full-grid output | exactly 652 rows |
| Native no-factor-four ratio on open points | \(d\sigma/d\sigma_{\rm no4}=4\) within \(8\times10^{-12}\) absolute |

The Python comparator independently recomputes \(I_6\) at the quadrature
order recorded in every Mathematica row. It then independently interpolates
the Python AFH table and assembles both the physical and no-factor-four
cross sections. A full run is accepted only if the comparator reports
status PASS and all full-grid and normalization checks pass.

## 6. Quick smoke test before the full grid

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

## 7. Scientific status

- AFH factor-four normalization: already validated at the 2401-node response
  level by the archived native Mathematica/Python audit.
- Historical green \(I_6\) mapping audit: complete; see
  [HISTORICAL_I6_MAPPING_AUDIT.md](HISTORICAL_I6_MAPPING_AUDIT.md).
- Mathematica/Python full \(d\sigma_A/dE_R\): not yet executed. Do not report
  a cross-code PASS until the native Wolfram run, full-grid comparison JSON,
  output CSV, and SHA-256 manifest have been reviewed.
- Detector response and final LZ likelihood: outside this Xe-131 fixed-speed
  cross-code validation.
