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


## Formal B reweighting of the PR86 seven-isotope halo scan

The adopted formal B nucleon baseline is being rerun on the newly accepted PR #93 high-order halo-folded seven-isotope scan. This is a post-processing reweighting of the completed full three-body and (I(D_{NR})) isotope contributions; it does not rerun phase-space or halo integration.

- [Formal B numerical report](FORMAL_B_REWEIGHT_OF_THRESHOLD_ENERGY_HALO_SCAN.md)
- [Task brief and frozen inputs](task_briefs/20261120-formal-B-reweight-of-threshold-energy-halo-scan.md)
- Implementation: [apply_nucleon_form_factors_B.py](../nucleon_form_factor_B_baseline/apply_nucleon_form_factors_B.py)
- Electromagnetic form-factor model: [borah2020_lowq2.py](../nucleon_form_factor_B_baseline/borah2020_lowq2.py)
- Reproduction workflow: [pr86-halo-formal-B-reweight.yml](../../.github/workflows/pr86-halo-formal-B-reweight.yml)

The local calculation covers all 1,456 isotope-energy rows and 208 natural-xenon recoil points for three separate strange-current inputs, with 3,000 Borah2020 electromagnetic covariance draws per input. At 248 keV, the formal B correction suppresses the uncorrected natural-xenon rate by 26.4--27.3%. The isotope-level full/(I(D_{NR})) ratio is unchanged to (2.23\times10^{-14}) percentage points; the maximum natural-xenon ratio change in 180--320 keV is (1.60\times10^{-5}) percentage points.

The source AFH isotope set covers 99.8158% of natural xenon atom abundance; Xe-124 and Xe-126 remain absent and the seven isotope abundances are not renormalized. These outputs are B-reweighted relative rates, not detector-folded event yields.

The independent GitHub reproduction passed in [workflow run 44672770451](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44672770451): all 19 B-baseline regression tests and all numerical gates passed. Artifact 14599834070 (SHA-256 `05368fa13890932bed0124a651de53a998570524a70d3fe33a6992d1610f1bd9`) was downloaded and verified; its numeric CSV outputs agree with the local calculation to below (4.6\times10^{-13}) maximum relative difference.


### Independent high-order halo scan validation

The full baseline/high-order halo scan was independently regenerated in [workflow run 44673037709](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44673037709). It completed all 1,456 isotope-energy rows and 208 natural-xenon recoil points with zero support mismatches. The natural-xenon Full/(I(D_{NR})) discrepancy is 0.0355190413% in 180–320 keV and 0.3527618038% over the full supported scan. The baseline-to-high-order maximum natural-xenon approximation-error shift is (1.0792\times10^{-5}) percentage points. The GitHub artifact was downloaded and compared with the archived local scan; the full halo kernel agrees within (2.82\times10^{-8}) relative and the (I(D_{NR})) kernel is identical.


### Accepted PR #93 high-order Halo source and B reweight update

The PR #93 higher-order Halo validation passed in [workflow run 44681433965](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44681433965), artifact 14607350801 (SHA-256 `a570bbf81119e8b7b87526c51b7012d056c0c07e290618bb7e12469b43571194`). It contains 1,456 isotope-energy rows and 208 natural-xenon recoil points, with speed quadrature order 32 and internal quadrature (12,4,4). Zero support mismatches were found. The active-support maximum quadrature shifts are 9.8863e-6% in the natural-xenon Full rate, 9.9873e-6% in the I(D_NR) rate, and 2.9057e-6 percentage points in the approximation-error curve.

The earlier formal-B output artifact was generated from a prior Halo source artifact and remains a historical reproduction. The current formal-B workflow is pinned to artifact 14607350801 and verifies the high-order metadata before reweighting. The new high-order-B output is the one to freeze as the formal comparison baseline.


The formal-B high-order reweight is now complete and independently reproduced in [workflow run 44689438445](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44689438445). Its output artifact is 14608091362 (SHA-256 `b9d261a68a73e480a6e4d84c3aef9c57a0fc5fc80aa1be7079170d0305b6c6c5`). All 19 baseline regression tests and all numerical gates passed. The downloaded artifact ZIP and all nine native output-file checksums were verified. This is the canonical B reweight of the accepted high-order Halo source.
