# Three-body phase-space tensor quadrature convergence

<badge>Numerical convergence: PASS</badge>

**Workflow run:** 44231019823  
**Source commit:** \`06cf3086422a692fe6eb81715ef8315aba95d05c\`  
**Artifact:** \`three-body-phase-space-component-convergence\`  
**Artifact ID:** 14395277591  
**Artifact SHA-256:** \`f86c44548efc271c49f2e1e5846c6485280265ba28cd4f3223f896d9eba29e73\`

## 1. Scope

This audit tests the quadrature convergence of the phase-space-integrated
three-body dark-matter Gram tensor
\[
G_{\mu a,\nu b}^{(3)}=\int d\Phi_3\,c_a^\mu c_b^{\nu *}
\]
and its spin-averaged Lorentz tensor
\[
L_{\mu\nu}^{(3)}=\sum_a G_{\mu a,\nu a}^{(3)}.
\]
It compares every complex component of the \(16\times16\) Gram matrix
(256 entries) and every complex component of the \(4\times4\) Lorentz
tensor (16 entries), together with the point-nucleus contractions.

This is a DM-side numerical convergence result. It does not by itself
establish the AFH spatial-multipole coefficients or a nuclear event rate.

## 2. Stress benchmarks

Three fixed-speed Xe-131 cases were used, each with zero, pole, and running
widths (nine benchmark/width combinations):

| Case | \(m_s\) | \(\Delta m\) | \(E_R\) | \(g_2\) | Mapping |
|---|---:|---:|---:|---:|---|
| Near pole, narrow coupling | 300 keV | 362 keV | 267 keV | 0.1 | \(\sin^2\) endpoint map |
| Near pole, larger coupling | 300 keV | 362 keV | 267 keV | 1 | \(\sin^2\) endpoint map |
| Off-pole green benchmark | 300 keV | 450 keV | 200 keV | 1 | threshold \(u^2\) map |

The first two cases stress the narrow near-pole region; the third provides
an off-pole comparison. All use \(v_\chi=776\) km/s and
\(m_\chi=1\) TeV.

## 3. Quadrature orders

Each case was evaluated at three nested orders.

| Case family | Low | Medium | High |
|---|---:|---:|---:|
| Near-pole | \(32\times16\times8\) | \(40\times24\times12\) | \(48\times32\times16\) |
| Off-pole | \(24\times16\times8\) | \(32\times24\times12\) | \(40\times32\times16\) |

The entries are \((n_W,n_z,n_\phi)\). The total number of quadrature nodes
evaluated across all nine scans and all three levels was 339,456.

The acceptance comparison is medium-to-high order. It is not an assertion
that a finite quadrature equals the exact integral; it is a direct
successive-order stability test.

## 4. Acceptance criteria and results

The acceptance thresholds were:

- Gram and Lorentz tensor relative Frobenius difference:
  \(10^{-3}\);
- largest relative difference among active components (components at least
  \(10^{-8}\) of the largest component):
  \(10^{-2}\);
- point-nucleus contraction relative difference:
  \(10^{-3}\).

<badge color="success">All nine medium-to-high comparisons PASS</badge>

| Metric | Worst observed | Tolerance |
|---|---:|---:|
| Gram Frobenius relative difference | \(1.5013\times10^{-8}\) | \(10^{-3}\) |
| Lorentz tensor Frobenius relative difference | \(1.5013\times10^{-8}\) | \(10^{-3}\) |
| Active Gram component relative difference | \(1.5673\times10^{-5}\) | \(10^{-2}\) |
| Active Lorentz component relative difference | \(1.5673\times10^{-5}\) | \(10^{-2}\) |
| Point-nucleus contraction relative difference | \(1.5118\times10^{-8}\) | \(10^{-3}\) |

The worst active-component difference occurs in the off-pole green benchmark.
The near-pole cases are even more stable at the final medium-to-high
comparison. The exact per-case and per-width results are archived in the
workflow JSON artifact.

## 5. Interpretation

The phase-space integration of the DM-side \(G_{\mu a,\nu b}^{(3)}\) and
\(L_{\mu\nu}^{(3)}\) tensors is numerically stable at the stated benchmark
points and reported quadrature orders. This removes a major numerical
uncertainty before the spatial-current multipole projection.

It does **not** complete the nuclear calculation. The following remain
separate gates:

1. derive the exact spherical projectors and phases mapping the nucleon
   convection and magnetization currents onto AFH \(\Delta\) and \(\Sigma'\);
2. contract those coefficients with the full complex phase-space Gram
   tensor, retaining the exact before/after scalar-emission interference;
3. combine with \(W_\Delta\), \(W_{\Sigma'}\), and the signed
   \(W_{\Sigma'\Delta}\) response where its kinematic coefficient is
   nonzero;
4. perform the isotope OBDME and natural-xenon halo integrations.

No AFH spatial-current rate or detector-level correction is claimed by this
convergence PASS.
