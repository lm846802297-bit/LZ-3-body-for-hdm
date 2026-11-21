# Halo-folded full three-body integral vs I(D): seven-isotope AFH validation

## Purpose

Extend the fixed-speed Xe-131 comparison to the halo-folded natural-xenon recoil rate. At each isotope and recoil energy, compare:

- Full: the complete coherent before/after scalar-radiation amplitude and the full three-body phase-space integral.
- Approximation: the threshold-amplitude factor times (I(D_{NR})).

The comparison is performed after the same halo-speed integral and the same isotope-dependent AFH response, mediator factor, nuclear mass and natural abundance have been applied to both predictions.

## Physical scope and benchmark

- AFH v6.0 default-density isotopes: Xe-128, 129, 130, 131, 132, 134 and 136.
- Xe-124 and Xe-126 are not assigned synthetic AFH responses. They are omitted from the AFH central prediction.
- Seven-isotope natural atom-fraction coverage: 0.998158; abundances are not renormalized.
- Truncated Standard Halo Model: (v_0=220), (v_E=232), (v_{esc}=544) km/s, (v_{max}=776) km/s.
- Benchmark: (m_{chi_1}=1) TeV, (m_s=300) keV, (Delta m=10) MeV, (m_V=5) GeV.
- Broad recoil scan: 5--800 keV, 10 keV coarse spacing.
- Candidate-region refinement: 180--320 keV, 1 keV spacing.
- Explicit anchors: 248 and 267 keV.
- AFH responses are evaluated directly from the pinned v6.0 density matrices at each isotope-specific exact spatial momentum (Q_A=sqrt{2m_AE_R+E_R^2}).

## Definitions

At fixed isotope, recoil energy and halo speed, the full kernel is

[
J_{full}=int_{W_{min}^2}^{W_{max}^2}dW^2,sqrt{lambda(W^2)}
int_{-1}^{1}dz,langle L^{00}angle_{phi_*}.
]

The approximation is

[
J_I=8L^{00}_{thr}I(D_{NR}),
]

where

[
I(D)=int_0^D depsilonsqrt{epsilon(epsilon+2m_s)}
]

for (D>0), and (I(D)=0) otherwise. The nonrelativistic energy budget is

[
D_{NR}=v q_{NR}-rac{q_{NR}^2}{2mu_A}-m_s,qquad
q_{NR}=sqrt{2m_AE_R},qquad
mu_A=rac{m_{chi_1}m_A}{m_{chi_1}+m_A}.
]

The exact four-vector threshold defines the common physical halo integration domain. If (D_{NR}) is negative at a point where exact kinematics is open, the approximation contributes zero there; the point is retained in the comparison.

The original fixed-speed 943-point implementation uses the exact energy excess
`epsilon = W - W_min = D_exact*t^2`. The current halo runner is being aligned to that same variable:

[
W=W_{min}+D_{exact}u^2,\qquad
W^2=(W_{min}+D_{exact}u^2)^2,
]

[
\frac{dW^2}{du}=4W D_{exact}u,\qquad 0\leq u\leq1.
]

The factorized form
`Delta_W2 = epsilon*(2*W_min + epsilon)`
is used in the stable point builder to avoid subtracting two quantities of order
`m_chi^2`. The previous PR #78 archive used the distinct
`threshold_u2` map
`W^2 = W_min^2 + (W_max^2-W_min^2)*u^2`; it remains preserved as the historical
comparison and is not overwritten. The 2026-11-20 follow-up reruns the full scan
with `threshold_energy_u2` and records both mappings' numerical difference.

The common rate weight (eta f_{lab}(v)/p_chi(v)^2) is retained. The isotope contributions are multiplied by their natural atom fraction, (m_A), the direct AFH physical (M)-response, and the vector-mediator denominator ((m_V^2+2m_AE_R)^2) before summing natural xenon.

## Quadrature convergence plan

Two full recoil scans are run on the identical grid:

| Configuration | Halo speed order per smooth segment | (W^2) order | (z) order | (phi_*) order |
|---|---:|---:|---:|---:|
| Baseline | 24 | 8 | 4 | 4 |
| Higher order | 32 | 12 | 4 | 4 |

The comparison script reports, separately for each isotope and natural xenon:

- relative shift in the full rate between quadrature settings;
- relative shift in the (I(D)) rate;
- change in the full-versus-(I(D)) error, in percentage points;
- support mismatches where one quadrature result is zero and the other is nonzero.

Both all-grid and rate-active-region maxima are recorded. The active region is defined relative to the maximum full rate, with a default floor of (10^{-8}).

The comparison uses only the Python standard library after the numerical runs; no pandas dependency is required.

## Run

From the repository root:

```bash
python research/three_body_phase_space_ID_validation/validate_halo_seven_isotope_ID.py \
  --er-min-keV 5 --er-max-keV 800 --er-step-keV 10 \
  --fine-min-keV 180 --fine-max-keV 320 --fine-step-keV 1 \
  --speed-order 24 --nw 8 --nz 4 --nphi 4 \
  --outdir results/halo-baseline
```

Run again with `--speed-order 32 --nw 12` for the higher-order result.

Outputs from each scan:
- `seven_isotope_halo_comparison.csv`: isotope-level full and approximate halo integrals and contributions.
- `natural_xenon_halo_comparison.csv`: abundance-weighted seven-isotope rate comparison.
- `metadata.json`: benchmark, halo, full recoil grid, quadrature settings and AFH source checksum.

Compare the two scan directories:

```bash
python research/three_body_phase_space_ID_validation/compare_halo_quadrature.py \
  --baseline-dir results/halo-baseline \
  --highorder-dir results/halo-highorder \
  --out-dir results/halo-quadrature-comparison
```

## Validation status and archived numerical result

The PR #78 / PR #74 full-range calculation is **completed and archived on main**. It contains 208 recoil energies per scan, 1,456 isotope-level rows, and 208 natural-xenon rows. The baseline and higher-order runs have zero support mismatches.

For the archived higher-order result:

- Natural-xenon maximum full-versus-`I(D_NR)` difference in 180--320 keV: **0.035519% at 320 keV**.
- Natural-xenon maximum over 5--800 keV: **0.352762% at 695 keV**; this endpoint-region value is kept separate from the candidate interval.
- Per-isotope candidate-region maxima range from **0.032592% (Xe-128)** to **0.037722% (Xe-136)**; all occur at 320 keV.
- Across the 1,456 isotope-energy rows, the maximum baseline-to-high-order shifts are (1.0109\times10^{-5}\%) for the full rate and (3.1057\times10^{-5}\%) for (I(D_{NR})); the maximum change in the full-versus-(I(D_{NR})) error is (2.8424\times10^{-5}) percentage points.

These values belong to the archived `threshold_u2` map. The 2026-11-20 follow-up now implements the exact fixed-speed `epsilon = D_exact*u^2` map in the shared integration module and switches the halo runner to it. The new baseline/high-order scan is **in progress**; its outputs will be stored in a new versioned result directory, leaving the PR #78 archive unchanged.

The scan retains `width_scheme="zero"` to reproduce the PR #78 far-off-pole numerical-comparison benchmark. It is not relabelled as the formal finite-pole-width production result; that work continues separately in the P3/P4 branch.

## Relation to the B baseline and detector response

The finite-nucleon B baseline and LZ 2026 Fig. S2 efficiency/exposure-weighted rate-level event yields are now archived in [the B-baseline numerical report](../nucleon_form_factor_B_baseline/B_BASELINE_NUMERICAL_RESULTS.md) and [PR #85](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/85). Those rate-level event-yield records do not apply energy-resolution smearing or construct a B-weighted two-dimensional signal PDF.

A separate NEST-based two-dimensional response fold exists under `research/lz_detector_response/`, but its archived three-body spectra predate the finite-nucleon B update and use the earlier GCN/JJ55 response comparison. The next detector-stage task is to feed the B-corrected AFH spectra into the existing event-weighted NEST response without multiplying the scalar Fig. S2 efficiency a second time. An official waveform-level LZ likelihood remains outside this rate-level calculation.
