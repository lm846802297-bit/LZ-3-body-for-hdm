# Lean 4 formalization of the LZ three-body dark-matter calculation

**Status:** expanded formalization source authored; Lean compilation is blocked by the current ChatGPT Linux network environment. No theorem in this package is marked kernel-verified until `lake build` actually succeeds.

## Scope and source hierarchy

This package is an independent mathematical proof layer for the Dirac vector-vector three-body process. It complements the project's Python and Mathematica calculations. Physical conventions follow the repository's current `main` source notes and the user-supplied `3body_for_HDM.pdf`; where the paper draft and current repository production policy differ, the current `AGENTS.md` production prescription governs the formal amplitude denominators.

Pinned baseline: `main` at `d2407050ed0f4975387bc6c05bc4509ccf375c31`.

## P0-A — Lean build

- Lean toolchain: `leanprover/lean4:v4.36.0`.
- Mathlib: `v4.36.0`.
- Reproduction: `lake update && lake build` from this directory.
- Actual status: **BLOCKED / NOT RUN**. `lean`, `lake`, and `elan` are absent; `curl -IL https://github.com/leanprover/elan/releases/latest` failed with `Could not resolve host: github.com`. The package sources have not been kernel-checked in this environment.

## P0-B — independent Python/SymPy checks

Run:

```bash
python validation/validate_p0_c_sachs.py
```

The archived run used Python 3.13.5 and SymPy 1.14.0 on the ChatGPT Linux container (AMD EPYC 9V74; 5 exposed logical CPUs; 6,090,668 KiB RAM). It produced:

- 20 exact symbolic identities with zero residual;
- 10,000 deterministic recoil-threshold samples, zero sign mismatches, maximum relative factorization residual `4.8183679268731794e-14`;
- 1,000 exact integer Gram-matrix trials (5 final states × 4 response channels), zero failures;
- five Xe-131 recoil-point checks using the canonical project masses and Sufian-2017 zero-transfer Pauli input.

Outputs: `validation/sympy_validation.json` and `validation/xe131_p_p0_a0_spotchecks.csv`. The JSON includes environment information and the script SHA-256. These are independent algebraic checks, not Lean kernel proofs or a physical validation of the matching prescription.

## P0-C — Sachs conversion and four baselines

- `ThreeBody/NucleonCurrent/SachsConversion.lean` defines `tau_N=Q_N^2/(4m_N^2)=-t_N/(4m_N^2)`, the Sachs-to-Dirac/Pauli conversion, and both reconstruction identities.
- `ThreeBody/NucleonCurrent/Baselines.lean` defines the normalized M-only P0, P, A0, and B coefficients. B uses `tauN (-tN) mN`, so the Sachs variable is tied to the invariant nucleon transfer and cannot be independently confused with the AFH spatial `Q_A^2`.
- `Normalization.lean` keeps raw `c_M^raw` and normalized `c_M^hat` separate and proves their relation under `F_i^raw=3 F_i^hat`.

The formalization preserves the project's four-level meaning:

| Baseline | Normalized form factors | Coefficient |
|---|---|---|
| P0 | `F1hat=1`, `F2hat=0` | `cMhat=1` (leading order) |
| P | `F1hat=1`, `F2hat=0` | `1+t_N/(8m_N^2)` |
| A0 | `F1hat=1`, `F2hat=kappa=F2hat(0)` | `1+t_N(1+2 kappa)/(8m_N^2)` |
| B | finite Sachs `G_E,G_M`, converted at `tau_N` | `F1hat+t_N(F1hat+2F2hat)/(8m_N^2)` |

The project reference inputs for `kappa` remain scenario-dependent; no strange-current scenarios are averaged. The finite-size AFH `W_M(y_A)` is common to all four rate-level baselines and is not encoded as a scalar nucleon form factor.

## P1 — two diagrams, Dirac algebra, and Ward structure

- `ThreeBody/Amplitude/DiracClifford.lean` introduces a (+---) Clifford-representation interface, with explicit gamma anticommutators and slash basis convention. The vector-current Ward identity is proved conditionally on the external left/right Dirac equations.
- `ThreeBody/Amplitude/TwoDiagram.lean` defines the two diagram operators in the project order: after-emission numerator times `gamma^mu` with the pole-width denominator; `gamma^mu` times before-emission numerator with zero-width denominator. It formalizes coherent addition and the exact cross-term identity in the squared amplitude.
- The leading nonrelativistic ordering kernel is formalized as `1/(omega-Delta)-1/(omega+Delta)=2 Delta/(omega^2-Delta^2)` and its `Delta=0` cancellation is stated.
- The reduced two-diagram Ward cancellation is formalized after the on-shell numerator reductions. Deriving those reductions from the full Clifford algebra and the exact three-body four-momenta remains pending; the current interface does not claim that the complete `q_A_mu T_3^mu` derivation is already kernel-verified.

The source paper specifies Dirac fermions, metric `(+---)`, `u_bar u=2m`, and coherent two-diagram summation. The repository's current production policy specifies zero width for the before-emission line and pole width for the after-emission line. This distinction is retained.

## P1 — AFH response matrix

- `ThreeBody/AFH/ResponseMatrix.lean` defines a real Gram response matrix from a common set of multipole amplitudes, its quadratic form, and the sum-of-squares representation establishing positive semidefiniteness.
- Off-diagonal entries are retained; the quadratic form includes their interference automatically.
- The M-only factorization is explicit.
- The AFH package-to-physical normalization is defined as `R_phys=4 C0 R_package`, with `C0=A^2/(4 R_package(0))`; the zero-momentum `A^2` normalization and the unique factor-four placement are stated separately.

The PSD result applies to a response matrix actually constructed as a Gram matrix over common final states/multipoles. It is not a blanket claim that arbitrary tabulated response values are PSD without checking their common-state construction. The exact AFH operator-specific OBDME and all isotope data remain numerical inputs, not generated by Lean.

## Current acceptance status

| Layer | Status |
|---|---|
| Source/convention audit | PASS |
| Python/SymPy algebra | PASS |
| Lean 4 / Mathlib compilation | BLOCKED / NOT RUN |
| Kernel-checked theorem status | PENDING |
| Full Dirac-trace derivation of two-diagram Ward contraction | PENDING |
| Concrete gamma-matrix representation instance | PENDING |
| AFH OBDME and isotope response data | Numerical workflow; outside Lean |
| Numerical phase-space, halo and detector calculations | Python/Mathematica; outside Lean |

## Reproducibility and provenance

The formalization uses no external numerical input dataset. Canonical equation sources and Git blob identities, local execution environment, source SHA-256 values, and output checksums are recorded in `provenance.json`. The Python validation outputs are native JSON and CSV. Lean caches and build products are not committed.
