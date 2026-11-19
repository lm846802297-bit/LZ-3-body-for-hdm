# B1/B2: Xe-131 AFH response joined to the three-body kernel

Date: 2026-11-11

## Status

**Completed as a fixed-speed, zero-width, factorized Xe-131 differential-cross-section diagnostic.**

This is not a complete reproduction of Figure 2: the mediator mass, separate g2 width input, halo prescription, and detector-level rate inputs are not fixed by the Figure 2 caption or the current direct-detection section of paper-source/main.tex.

## 1. Fixed inputs and conventions

| Input | Value / prescription |
|---|---|
| Target | Xe-131 |
| Target mass | m_A = 131 * 0.93149410242 = 122.025727417 GeV |
| Dark matter mass | m_chi1 = 1000 GeV |
| Scalar mass | m_s = 0.3 MeV |
| Fermion splitting | Delta m = 1 MeV |
| Incident speed | v = 776 km/s (single-speed diagnostic) |
| Coupling product | (g1*g2*gVN)^2 = 1e-8 |
| Width | zero-width diagnostic |
| Nuclear structure | GCN and JJ55, same AFH default b_A |
| Mediator mass | not supplied; kept explicit and unevaluated |
| Halo fold | not performed |

The AFH response is
\[
\mathcal R_A(E_R)=\frac{4\pi}{2J_A+1}W_M^{00}(y),
\qquad
y=\frac{b_A^2m_AE_R}{2}.
\]
Accordingly, the response interpolation uses
\[
q_{\rm response}=\sqrt{2m_AE_R}.
\]
The exact recoil momentum
\[
q_{\rm kin}=\sqrt{2m_AE_R+E_R^2}
\]
is retained in the three-body kinematic limits from the manuscript. These two momenta are intentionally not interchanged.

## 2. Joined cross section

The implemented factorization is
\[
\frac{d\sigma_A}{dE_R}
=
\frac{m_A(g_1g_2g_{VN})^2}{256\pi^3p_{\chi_1}^2}
\frac{\mathcal R_A(E_R)}{(m_V^2+2m_AE_R)^2}
I_6,
\]
where I_6 is evaluated by eq6_kernel.reduced_kernel.

For transparent archiving, define the coefficient before the vector propagator:
\[
C_A(E_R,v)=
\frac{m_A(g_1g_2g_{VN})^2}{256\pi^3p_{\chi_1}^2}
\mathcal R_A(E_R)I_6.
\]
Then
\[
\frac{d\sigma_A}{dE_R}
=\frac{C_A(E_R,v)}{(m_V^2+2m_AE_R)^2}.
\]
C_A has units of GeV and d sigma/dE_R has units of GeV^-3.

No value of m_V is silently inserted. The output CSV therefore archives C_A; it leaves d sigma/dE_R null unless mV_GeV is explicitly supplied.

## 3. Corrected azimuthal normalization

A comparison of the two research branches exposed a factor-of-two regression in the azimuthal quadrature. The intended average is
\[
\langle L_{00}\rangle_{\varphi_*}
=\frac{1}{2\pi}\int_0^{2\pi}d\varphi_*\,L_{00},
\]
which requires transformed Gauss-Legendre weights
\[
w_i^\varphi=\frac12w_i^{\rm GL}.
\]
The current branch had accidentally iterated over the unscaled wp rather than phiweights, doubling I_6.

The loop now uses phiweights. A regression test fixes the historical benchmark
\[
I_6(m_A=122~{\rm GeV},E_R=200~{\rm keV},v=776~{\rm km/s})
=878098.5567396~{\rm GeV}^2
\]
at (nW,nz,nphi)=(16,16,8). The original Eq. (6) convergence record is thereby restored.

## 4. Three-order quadrature convergence

For the isotope mass m_A=131 u, the three orders give:

| E_R [keV] | Phase space | I_6 coarse (16,16,8) [GeV²] | medium (24,24,16) [GeV²] | fine (40,32,20) [GeV²] | fine/medium - 1 |
|---:|:---:|---:|---:|---:|---:|
| 101 | closed | 0 | 0 | 0 | 0 |
| 200 | open | 879698.55 | 879678.80 | 879672.05 | -7.679e-6 |
| 267 | open | 1312119.07 | 1312090.18 | 1312080.30 | -7.532e-6 |
| 542 | open | 506475.17 | 506463.57 | 506459.60 | -7.831e-6 |

All open-channel points agree between the medium and fine orders to better than 8e-6 relative. The GCN and JJ55 runs give the same I_6 to numerical precision, as required because the nuclear model enters only through R_A.

The on-shell closure gaps m_chi2 - sqrt(W_max^2) are positive at all four points: approximately 0.707, 0.653, 0.639, and 0.667 keV, respectively. At 101 keV the three-body phase-space interval is nevertheless closed because W_max^2 < W_min^2.

## 5. Response and factorized coefficients

Fine-order (40,32,20) results:

| E_R [keV] | R_A GCN | R_A JJ55 | C_A GCN [GeV] | C_A JJ55 [GeV] |
|---:|---:|---:|---:|---:|
| 101 | 0.0602439 | 0.0117206 | 0 | 0 |
| 200 | 10.04537 | 10.70146 | 2.027512e-4 | 2.159935e-4 |
| 267 | 0.00484135 | 0.00921002 | 1.457485e-7 | 2.772669e-7 |
| 542 | 0.00384338 | 0.00509356 | 4.466168e-8 | 5.918929e-8 |

At a fixed recoil energy, the GCN/JJ55 ratio of C_A equals the ratio of their nuclear responses. This is an explicit cross-check that the same three-body kernel and coupling prefactor are used for both nuclear calculations.

## 6. Comparison with the three Figure 2 dips

The archived Xe-131 response minima are:

| Model | First minimum [keV] | Second minimum [keV] | Third minimum [keV] |
|---|---:|---:|---:|
| GCN | 101.321 | 269.061 | 551.138 |
| JJ55 | 100.676 | 270.104 | 554.893 |
| Figure 2 dip points | 101 | 267 | 542 |

The first two positions are close to the Figure 2 dip points. The third response minimum lies about 9–13 keV above the plotted 542 keV point. The response is already strongly suppressed at 542 keV, but the minimum is not exactly at 542 keV. We do not move b_A to force agreement.

The depths are nuclear-model dependent. For example, the first Xe-131 minimum has R_min/R_A(0) = 3.35e-6 in GCN and 6.28e-8 in JJ55. The second and third minima also differ substantially in depth. Thus the positions are qualitatively stable, while the depths are not interchangeable between shell-model inputs.

For the specific m_s=300 keV, v=776 km/s single-speed diagnostic, 101 keV is kinematically closed. Its nuclear-response dip does not by itself imply a nonzero event contribution at that speed. The halo fold must determine how much weight, if any, comes from speeds above the threshold.

## 7. What is and is not established

Established:
- AFH W_M^{00} data are connected to the manuscript's Eq. (6) kernel.
- The manuscript's non-relativistic y(E_R) response convention is respected separately from exact three-body recoil kinematics.
- The azimuthal average is normalized correctly.
- Eq. (6) is converged at the three open-channel recoil points.
- GCN and JJ55 share the same I_6, while their nuclear responses remain distinct.

Not established:
- A numerical d sigma/dE_R, because m_V is not fixed in the source input.
- A unique finite-width result, because the separate g_2 and the Dirac/Majorana realization are not specified.
- A halo-integrated rate or detector event spectrum.
- A natural-xenon result. Each isotope must first receive its own m_A, b_A, W_M^{00}, kinematic limits, and I_6; only then can the isotope contributions be abundance weighted.

## 8. Reproducibility files

- joint_xe131.py: AFH response interpolation and factorized cross section.
- run_joint_xe131.py: single-speed GCN/JJ55 calculation.
- compare_joint_xe131_convergence.py: three-order convergence and GCN/JJ55 closure.
- tests/test_eq6_kernel.py: azimuthal-normalization regression.
- tests/test_joint_xe131.py: response normalization, factorization, and kinematic closure.
- results/joint_xe131/CONVERGENCE.md and quadrature_convergence.csv: archived numerical convergence.

CI run: https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/42948219247
