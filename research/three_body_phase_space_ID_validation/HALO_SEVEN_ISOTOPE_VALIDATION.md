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

The full (W^2) integral uses the independently audited threshold-regularized mapping

[
W^2=W_{min}^2+(W_{max}^2-W_{min}^2)u^2,qquad 0leq uleq1,
]

implemented in `phase_space_convergence.py`. This removes the square-root endpoint behavior from direct linear-(W^2) quadrature and uses the stable (Delta W^2) point builder.

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

## Validation status

The initial 180--320 keV baseline run completed and produced an Actions artifact. Its higher-order follow-up exposed a missing comparison dependency and a need to regularize the full (W^2) integration consistently with the independent phase-space audit. The current PR version corrects both and expands the scan. The full-range results and convergence summary are pending the updated workflow.

This is a pre-detector-response rate-ratio validation. It does not yet include finite-(t_N) nucleon form factors, detector efficiency, energy resolution, exposure, cuts or likelihood.
