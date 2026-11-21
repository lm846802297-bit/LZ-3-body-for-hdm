# PR85 finite-nucleon B-baseline archive

**Status:** native outputs extracted and SHA-256 checked. This is a reproducible rate-level B calculation, not an LZ exclusion.

- PR: https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/85
- Source workflow: https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44590382197
- Source commit: `f6a01b7735c2373848510657826503484dd118d5`
- Artifact ID: `14564076631`; artifact digest is pinned in the request JSON.

The B baseline applies finite nucleon Dirac-Pauli form factors at (t_N=-Q_A^2), with (Q_A^2=2m_AE_R+E_R^2), while preserving the finite-size AFH (W_M(y_A)) response. The mediator propagator uses the separate invariant transfer (t_A=-2m_AE_R).

The detector fold uses the LZ 2026 Fig. S2 NR efficiency, 2.84 tonne-year exposure, and 5.4--269.9 keV ROI. The Borah 2020 proton/neutron coefficient covariance is propagated with 3000 correlated draws (seed 20261119), preserving correlations across recoil energies and isotopes.

The detector-level output does not include energy-resolution smearing, a two-dimensional S1c/log10(S2c) signal PDF, background likelihood, profile likelihood, or a confidence-level exclusion. Strange-lattice uncertainty and the LZ gray efficiency envelope are not sampled.

