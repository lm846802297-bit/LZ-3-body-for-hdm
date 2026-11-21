# Phase-space-integrated spin-resolved three-body tensor — results

**Status:** PASS for the DM-side spin-resolved tensor construction and the
independent Dirac-trace contraction. AFH multipole coefficients remain open.

## Provenance

- Workflow: [44224510581](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44224510581)
- Source commit used by the successful calculation:
  `de33bfbc8dc1d322b6c0761c8df5d73f2dadf303`
- Artifact ID: `14392805297`
- Artifact name: `full-three-body-current-nucleon-match-and-phase-space-tensor`
- Tensor JSON SHA-256:
  `95901cb8e083c100dc05fb1ca1d79c6eb6ad320083971ef6da43bcea5b776b04`
- Tensor JSON size: 1,471,377 bytes
- Regression suite: 23 tests passed

The artifact stores the full complex q-aligned \(L_{\mu\nu}^{(3)}\) tensor,
the Pauli-resolved \(G_{\mu a,\nu b}^{(3)}\) Gram tensor, before/after
emission pieces, coherent diagram interference, and the static
Dirac--Pauli matching diagnostic.

## Benchmarks and point-nucleus kernel ratios

The table reports the dimensionless/common-prefactor-stripped integrated
point-nucleus contraction \(I_{\rm full}\) divided by its zero-width value
at the same benchmark. It is a width-sensitivity diagnostic of the current
kernel, not a physical cross-section ratio or a detector prediction.

| Benchmark | \(g_2\) | Width | \(I_{00}\) | \(I_{\rm full}/I_{\rm full}^{(0)}\) | Max Dirac-trace residual |
|---|---:|---|---:|---:|---:|
| \(\Delta m=450\) keV | 1 | zero | \(1.62555\times10^7\) | 1 | \(2.40\times10^{-10}\) |
| \(\Delta m=450\) keV | 1 | pole | \(1.54745\times10^7\) | 0.951956 | \(2.39\times10^{-10}\) |
| \(\Delta m=450\) keV | 1 | running | \(1.61040\times10^7\) | 0.990675 | \(2.40\times10^{-10}\) |
| \(\Delta m=1\) MeV | 1 | zero | \(8.79670\times10^5\) | 1 | \(4.77\times10^{-11}\) |
| \(\Delta m=1\) MeV | 1 | pole | \(8.697996\times10^5\) | 0.988779 | \(4.71\times10^{-11}\) |
| \(\Delta m=1\) MeV | 1 | running | \(8.79466\times10^5\) | 0.999768 | \(4.77\times10^{-11}\) |
| \(\Delta m=362\) keV | 0.1 | zero | \(7.51944\times10^9\) | 1 | \(1.60\times10^{-9}\) |
| \(\Delta m=362\) keV | 0.1 | pole | \(7.42376\times10^9\) | 0.987276 | \(1.59\times10^{-9}\) |
| \(\Delta m=362\) keV | 0.1 | running | \(7.42582\times10^9\) | 0.987550 | \(1.59\times10^{-9}\) |
| \(\Delta m=362\) keV | 1 | zero | \(7.51944\times10^9\) | 1 | \(1.60\times10^{-9}\) |
| \(\Delta m=362\) keV | 1 | pole | \(4.35091\times10^8\) | 0.057862 | \(4.02\times10^{-10}\) |
| \(\Delta m=362\) keV | 1 | running | \(4.85305\times10^8\) | 0.064540 | \(3.98\times10^{-10}\) |

The near-pole cases have \(m_{\chi_2}-W_{\max}=0.828984\) keV.
The corresponding pole widths are 0.322437 keV for \(g_2=0.1\) and
32.24369 keV for \(g_2=1\). The large width sensitivity for \(g_2=1\)
is therefore retained in the integrated tensor; it is not hidden by
dropping the finite-width propagator.

Quadrature orders are \(24\times16\times8\) for the two green benchmarks
and \(32\times16\times8\) for the near-pole benchmarks, for each of the
three width schemes.

## Numerical checks

| Check | Observed | Acceptance |
|---|---:|---:|
| Maximum integrated spin-tensor vs independent Dirac-trace residual | \(1.59813\times10^{-9}\) | \(<2\times10^{-9}\) |
| Gram/tensor Hermiticity residual | 0 | \(<10^{-12}\) |
| Minimum Gram eigenvalue | \(-3.19523\times10^{-14}\) | \(>-10^{-10}\) |
| Minimum spin-averaged tensor eigenvalue | \(5.74626\times10^{-4}\) | \(>-10^{-10}\) |
| q-frame orthogonality/determinant residual | \(3.15227\times10^{-16}\) | \(<10^{-12}\) |

The tiny negative Gram eigenvalue is consistent with floating-point
roundoff under the explicit PSD tolerance. The largest comparison residual
is in the near-pole transverse-spatial subtraction; the individual charge,
longitudinal, and full point-nucleus contractions agree more closely.

## Interpretation and limits

This calculation establishes the phase-space-integrated DM-side tensor
needed for the next matching step. It does **not** yet calculate
\(\mathcal R_{\alpha\beta}^{(3)}\). The following remain necessary:

1. project the finite-\(t_N\) Dirac--Pauli nucleon current onto the complete
   AFH one-body multipole basis;
2. derive the three-body coefficients for the convection and magnetization
   currents and their \(\Sigma'\)-\(\Delta\) interference;
3. determine whether the exact current generates any additional
   \(\Sigma''\) or \(\widetilde{\Phi}'\) coefficient beyond the leading
   vector-current reduction;
4. perform a dedicated quadrature-order convergence scan for every
   integrated Gram component;
5. contract the coefficients with each isotope's AFH OBDMEs.

No halo-folded natural-xenon spectrum, absolute cross section, LZ response,
or likelihood is implied by the \(I_{\rm full}\) ratios above.
