# Full three-body L00 integral vs I(D) validation

Date: 2026-11-19

## Purpose

Compare the full fixed-speed three-body integral
`J_full = integral dW^2 sqrt(lambda) integral_{-1}^{1} dz <L00>_{phi*}`
with the heavy-particle phase-space approximation
`J_I = 8 L00_threshold I(D_NR)`.

This is a **Xe-131, fixed-speed diagnostic**, not a halo-folded natural-xenon prediction or detector event rate.

## Benchmark

- m_chi1 = 1 TeV
- Delta = m_chi2 - m_chi1 = 10 MeV
- m_s = 300 keV
- m_A = 122 GeV (benchmark Xe-131 mass used in this scan)
- v = 776 km/s
- m_V = 5 GeV
- g1 = 0.1, g2 = 1.725, g_VN = 0.04857
- 943 recoil points over 109.64--652.94 keV

The couplings, mediator propagator and common nuclear response are independent of W,z,phi* at fixed recoil energy and cancel in this relative comparison.

## Definitions

`D_exact = W_max - (m_chi1 + m_s)`, with the exact four-vector boundary
`W_max^2 = m_chi1^2 - 2(E_chi1+m_A) E_R + 2 p_chi1 sqrt(E_R(E_R+2m_A))`.

The leading heavy-particle expression is
`D_NR = v q - q^2/(2 mu_A) - m_s`, where
`q = sqrt(2 m_A E_R)` and `mu_A=m_chi1*m_A/(m_chi1+m_A)`.

`I(D) = integral_0^D d epsilon sqrt(epsilon(epsilon+2 m_s))` for D>0, and zero otherwise.

The factor 8 in `J_I=8 L00_threshold I(D)` follows from
`dW^2 sqrt(lambda) -> 4 p_star d epsilon` and the z integral
`integral_{-1}^1 dz L00 -> 2 L00_threshold` at the threshold-amplitude approximation.

## Numerical method

- Full Dirac trace of the coherently summed before/after scalar-radiation diagrams.
- Full W,z,phi* dependence retained in the numerator trace and propagator denominators.
- Gauss-Legendre quadrature in transformed `t=sqrt(epsilon/D_exact)` and z; uniform midpoint quadrature in phi*.
- Production settings: 8 x 8 x 8 nodes.
- Spot checks: (16,12,12) and (24,16,16) at selected recoil points.

## Reported comparison

The local scan reported:
- At E_R near 248.06 keV: total difference about 0.0494%.
- Over 120--640 keV: maximum absolute difference about 0.0825%.
- Over the full sampled interval: maximum absolute difference about 0.6846%, driven by relative sensitivity close to the kinematic endpoints.
- Replacing D_NR by D_exact reduced the reported maximum difference to about 0.0502%.

These numbers are the outputs recorded by the local validation run; rerun the script and inspect the generated CSV/PNG before using them as a final publication result.

## Reproduction

Requirements: Python 3, NumPy, pandas, Matplotlib.

From the repository root:

```bash
python research/three_body_phase_space_ID_validation/validate_full_L00_vs_ID.py
```

Options include `--points`, `--v-kms`, `--er-min`, `--er-max`, `--nt`, `--nz`, `--nphi`, and `--out-prefix`.

The script writes a CSV and PNG into the current working directory by default. For a deterministic in-directory output:

```bash
python research/three_body_phase_space_ID_validation/validate_full_L00_vs_ID.py --out-prefix research/three_body_phase_space_ID_validation/xe131_full_L00_vs_ID_776kms
```

## Kinematic source note

The exact four-vector identity gives
`W_max^2 = m_chi^2 - 2(E_chi+m_A)E_R + 2 p_chi sqrt(E_R(E_R+2m_A))`.
This agrees with Appendix VIII, Eq. (91), of the supplied manuscript. The printed main-text Eq. (24) appears to contain an additional `+E_R^2` term; this should be reconciled against the manuscript source before citation.

## Scope

This result does not include halo velocity averaging, natural-xenon isotope summation, detector efficiency/exposure, or the adopted finite-t_N Dirac-Pauli × AFH B nuclear response. Those factors are common to this fixed-E_R DM-side relative comparison, but must be restored for an absolute rate prediction.


## Halo-folded seven-isotope extension and permanent outputs

The fixed-speed Xe-131 diagnostic above remains a separate result layer. The later PR #78/PR #74 calculation extends the full \(L^{00}\)-versus-\(I(D_{NR})\) comparison to the halo-folded seven-isotope AFH natural-xenon rate. Its native CSV/JSON outputs, both source artifact ZIPs, run provenance, and SHA-256 inventory are archived in [the halo/seven-isotope result package](results/2026-11-19-halo-seven-isotope-full-vs-ID-full-recoil-scan/README.md).

The archive contains 208 recoil points and 1,456 isotope-level rows per scan. Baseline and higher-order quadrature runs agree at the \(10^{-5}\%\) level in the active natural-xenon region, with zero support mismatches. The maximum absolute full-versus-\(I(D_{NR})\) difference in the higher-order natural-xenon rate is 0.352762% on this grid.

The PR #74 integration (including the PR #78 dependency) is merged into main at commit 070dc89cc58699633d0009c1fbaea7fa400ee337. This remains a halo-folded rate-ratio calculation, not a detector-level LZ prediction.
