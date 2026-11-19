# Finite-width three-body current and recoil-spectrum results

**Run:** GitHub Actions run 44186889932, commit 6892a56d50bb3472e48c358256d0c3e6a9b5c5a4

**Status:** Python regression suite PASS; finite-width spectrum generation PASS; near-pole zero-width quadrature refined and converged.

## 1. Finite-width Ward identity

The implemented current inserts the width only in the after-emission propagator:
\[
D_1=r_1^2-m_{\chi_2}^2,\qquad
\widetilde D_2=D_2+i a,\qquad a=m_{\chi_2}\Gamma_{\chi_2}.
\]
The verified identity is
\[
q_{A\mu}\mathcal T_3^\mu
=(m_{\chi_2}-m_{\chi_1})\bar u'
\left[\frac{\slashed r_1+m_{\chi_2}}{D_1}
-\frac{\slashed r_2+m_{\chi_2}}{D_2+i a}\right]u
+\frac{i a}{D_2+i a}\bar u'u.
\]

At the 200-keV reference point:
- spin-resolved 2x2 matrices reproduce the independent \(L^{\mu\nu}\) trace to \(2.7\text{--}4.5\times10^{-16}\);
- the finite-width Ward identity residual is \(2.6\times10^{-10}\);
- the conserved point-nucleus current has \(q_A\cdot J_A=0\);
- projecting \(\mathcal T_3^\mu\) transverse changes the contracted amplitude by at most \(1.7\times10^{-16}\).

Thus the nonzero longitudinal Ward divergence does not itself change the coherent elastic rate: it is annihilated by the conserved target vector current. The finite width does change the transverse current and therefore the recoil kernel.

## 2. Fixed-speed recoil-kernel scan

Parameters:
\[
m_{\chi_1}=1~\mathrm{TeV},\quad m_s=300~\mathrm{keV},\quad
m_A=131u,\quad v=776~\mathrm{km/s},\quad m_V=10~\mathrm{GeV}.
\]
The kernel is
\[
K_{\rm point}(E_R)=
\frac{m_A I_{\rm full}(E_R)}
{[m_V^2+2m_AE_R]^2},
\]
with the nuclear form factor factored out. Ratios between width schemes at a fixed recoil energy are unchanged by a common nuclear form factor.

The zero-width result is a diagnostic baseline only. The pole width is the current manuscript Breit-Wigner prescription. The running width is the scalar-channel absorptive-width comparison.

### 200-keV anchor

| Benchmark | \(g_2\) | Pole / zero | Running / zero |
|---|---:|---:|---:|
| \(\Delta m=450\) keV | 1 | 0.951956 \((-4.804\%)\) | 0.990675 \((-0.933\%)\) |
| \(\Delta m=1\) MeV | 1 | 0.988779 \((-1.122\%)\) | 0.999768 \((-0.023\%)\) |
| \(\Delta m=362\) keV | 0.1 | 0.999942 \((-0.0058\%)\) | 0.999962 \((-0.0038\%)\) |
| \(\Delta m=362\) keV | 1 | 0.661145 \((-33.885\%)\) | 0.751202 \((-24.880\%)\) |

For the broad off-shell scans, the pole/zero ratio ranges from 0.93909 to 0.96603 for \(\Delta m=450\) keV, and from 0.98837 to 0.98949 for \(\Delta m=1\) MeV over \(E_R=130\text{--}400\) keV.

### Near-pole \(\Delta m=362\) keV scan

The first kinematic point where \(W_{\max}=m_{\chi_2}\) is \(E_R\simeq274.788\) keV at \(v=776\) km/s. Only points below this crossing are included in the off-shell scan.

| \(E_R\) | Pole clearance | Pole / zero, \(g_2=0.1\) | Pole / zero, \(g_2=1\) |
|---:|---:|---:|---:|
| 200 keV | 14.5345 keV | 0.999942 | 0.661145 |
| 267 keV | 0.828984 keV | 0.987276 | 0.057862 |
| 270 keV | 0.493341 keV | 0.965840 | 0.034589 |
| 272 keV | 0.280994 keV | 0.906733 | 0.019742 |
| 274 keV | 0.077662 keV | 0.538646 | 0.005462 |
| 274.5 keV | 0.028226 keV | 0.243538 | 0.001985 |

The pole widths are \(\Gamma_{\chi_2}=0.322437\) keV for \(g_2=0.1\) and \(32.24369\) keV for \(g_2=1\). The finite width regularizes the sharp zero-width endpoint enhancement and substantially changes the recoil-spectrum shape. This is not a small amplitude-only correction.

The separate coupling \(g_2\) matters: a fixed coupling product does not determine \(\Gamma_{\chi_2}\). The two \(g_2\) cases therefore represent distinct width benchmarks, not one unique prediction.

## 3. Spatial-current check

Across all scanned points, the full coherent point-nucleus current differs from the charge-only \(J_A^0\) contraction by only \(-3.6\) to \(-6.1\) ppm. This is the centre-of-mass convection correction for a coherent point nucleus.

It does **not** bound the internal nuclear magnetization and orbital responses. AFH \(\Sigma'\), \(\Sigma''\), and \(\Delta\) matching remains open; no conclusion that the full Xe-131 spatial response is negligible is drawn.

## 4. Numerical convergence

The near-pole zero-width integrand becomes sharply endpoint-peaked:
- at 267 keV, 48x12x6 vs 80x16x8 differs by \(1.53\times10^{-8}\);
- at 274 keV, the zero-width comparison required 80x16x8 vs 160x20x10, which differs by \(6.22\times10^{-8}\);
- at 274.5 keV, it required 160x20x10 vs 240x24x12, which differs by \(3.21\times10^{-8}\).

The pole- and running-width integrals converge at better than \(3\times10^{-10}\) in the corresponding 48x12x6 vs 80x16x8 comparisons. The high-order zero-width rows are used for the near-pole ratios above.

## 5. Scope limits

- Fixed-speed reduced point-nucleus kernel, not a halo-folded natural-xenon event rate.
- Nuclear form factor is factored out; no AFH internal spin/orbital responses.
- Scalar-only conditional width assumes Dirac \(\chi\), a real scalar, a pure scalar Yukawa vertex, and no other open \(\chi_2\) decay channels.
- Running width includes the scalar-channel absorptive contribution; the complete vector-sector real self-energy is not included.
- No detector response, efficiency, exposure, or likelihood is included.
- The on-shell-accessible interval must be treated separately from the off-shell three-body process.
