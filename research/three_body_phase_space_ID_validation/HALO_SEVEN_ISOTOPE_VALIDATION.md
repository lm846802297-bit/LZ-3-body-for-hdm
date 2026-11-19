# Halo-folded full three-body integral vs I(D): seven-isotope AFH validation

## Purpose

Extend the fixed-speed Xe-131 comparison to the halo-folded natural-xenon recoil rate. At each isotope and recoil energy, compare:

- Full: the repository's complete Eq. (6) kernel, retaining the coherent before/after scalar-radiation amplitudes and the full W^2,z,phi* integration.
- Approximation: the threshold-amplitude factor times I(D_NR), with D_NR evaluated using q_NR=sqrt(2 m_A E_R).

The comparison is made after the same halo speed integration and the same isotope-dependent AFH response, mediator factor, nuclear mass and natural abundance have been applied to both predictions.

## Physical scope

- Seven AFH v6.0 default-density isotopes: Xe-128, 129, 130, 131, 132, 134, 136.
- Xe-124 and Xe-126 are not assigned synthetic AFH responses. They are omitted from the AFH central prediction.
- The seven-isotope natural atom-fraction coverage is 0.998158; abundances are not renormalized.
- The halo is the truncated Standard Halo Model: v0=220 km/s, vE=232 km/s, vesc=544 km/s, vmax=776 km/s.
- Benchmark: mchi1=1 TeV, ms=300 keV, Delta_m=10 MeV, mV=5 GeV.
- Recoil window defaults to 180--320 keV, with a 10 keV grid and explicit 248 and 267 keV anchors.
- AFH responses are evaluated directly from the pinned v6.0 density matrices at each isotope-specific exact spatial q=sqrt(2 m_A E_R+E_R^2), not interpolated from the old sparse sample table.

## Definitions

At each (A,E_R,v), the full kernel is

`J_full = integral_{Wmin^2}^{Wmax^2} dW^2 sqrt(lambda) integral_{-1}^{1} dz <L00>_{phi*}`.

The approximation is

`J_I = 8 L00(Wmin,z=0) I(D_NR)`,

`I(D)=integral_0^D d epsilon sqrt(epsilon(epsilon+2 ms))` for D>0, otherwise zero, and

`D_NR = v q_NR - q_NR^2/(2 mu_A) - ms`,
`q_NR=sqrt(2 m_A E_R)`,
`mu_A=mchi*m_A/(mchi+m_A)`.

The exact four-vector threshold from the full kernel defines the common physical halo integration domain. If the approximate D_NR opens slightly below that exact threshold, the unphysical sub-threshold sliver is excluded rather than counted as an approximate-only physical rate.

The common speed weight beta f_lab(v)/p_chi(v)^2 is retained. At each isotope and recoil energy, the full and approximate halo integrals are then multiplied by the same abundance, m_A, direct AFH response and vector-mediator denominator before the natural-xenon sum. Therefore the final ratio tests the approximation after halo folding and isotope summation, not merely at one fixed speed.

## Run

From the repository root:

```bash
python research/three_body_phase_space_ID_validation/validate_halo_seven_isotope_ID.py
```

Optional controls:

- `--er-min-keV`, `--er-max-keV`, `--er-step-keV`
- `--speed-order`
- `--nw`, `--nz`, `--nphi`
- `--outdir`

Outputs:
- `seven_isotope_halo_comparison.csv`: isotope-level full and approximate halo integrals and contributions.
- `natural_xenon_halo_comparison.csv`: abundance-weighted seven-isotope rate comparison.
- `metadata.json`: benchmark, halo, response-source checksum and scope.

## Validation status

The script is added for execution and review. Numerical results are not promoted until the PR workflow has completed and speed/internal quadrature convergence has been checked. This is a pre-detector-response rate comparison; efficiency, resolution, exposure, cuts and likelihood are not included.
