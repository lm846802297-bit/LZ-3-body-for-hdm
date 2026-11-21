# Lean 4 formalization of the LZ three-body dark-matter calculation

**Status:** exploratory scaffold. Source files are authored; the Lean build has not yet run in the current ChatGPT Linux environment.

## 1. Purpose and scope

This package provides an independent mathematical proof layer for selected
analytic identities in chi_1 + A -> chi_1 + A + s. It complements, and does
not replace, the repository's Python and Mathematica calculations.

The first P0 slice formalizes:
1. recoil-deficit factorization and minimum-speed threshold equivalence;
2. the distinction between invariant nucleon transfer and AFH spatial momentum;
3. raw versus normalized nucleon charge-matching coefficients;
4. zero-transfer normalization and P0/P rate-ratio algebra.

It does not yet formalize the full Dirac algebra, the derivation of the
nonrelativistic matching coefficient from spinors, the two-diagram amplitude,
the Ward identity, AFH OBDME, or numerical phase-space integrals.

## 2. Frozen conventions

- Lean definitions use real numbers; no numerical unit conversion is performed.
- q in Kinematics.lean is the positive recoil spatial-momentum magnitude
  in the reduced heavy-particle kernel. It is not a generic four-momentum.
- mu is the positive DM-nucleus reduced mass; mS is the scalar mass; v is
  the incident speed.
- Adopted impulse-matching invariant:
  t_N = t_A = -2 m_A E_R, and Q_N^2 = -t_N = 2 m_A E_R.
- AFH spatial momentum:
  Q_A^2 = |q_A|^2 = 2 m_A E_R + E_R^2.
  Q_A^2 is not substituted for Q_N^2 in the nucleon matching.
- Raw coefficient:
  c_M_raw = F1 + t_N (F1 + 2 F2)/(8 m_N^2).
- Normalized coefficient:
  c_M_hat = c_M_raw/3, paired with g_VN = 3 g_Vq.
- Zero-transfer charge:
  F1^{uds,N}(0)=3, hence c_M_raw(0)=3 and c_M_hat(0)=1.
- P0: c_M_hat=1. P: c_M_hat=1-Q_N^2/(8 m_N^2).
- c_M is formalized only as the current M-only rate-level definition,
  not as a proved full covariant nuclear-current matching theorem.

The alternative substitution t_N=-Q_A^2 is named separately in the
kinematics module only to expose the exact E_R^2 difference. It is not
the adopted matching convention.

## 3. Files

- ThreeBody/Kinematics.lean: threshold and momentum-variable identities.
- ThreeBody/NucleonCurrent/Normalization.lean: raw/normalized coefficient
  identities and P0/P rate algebra.
- ThreeBody.lean: package root.
- lakefile.toml: Lake package and Mathlib dependency.
- lean-toolchain: pinned Lean release.

## 4. Build and reproduction

From this directory, run:

    lake update
    lake build

The toolchain is pinned to Lean v4.36.0 and Mathlib v4.36.0. The active
ChatGPT Linux execution image has no lean or lake executable and cannot
resolve GitHub DNS, so no build result is claimed in this initial scaffold.
The first local or approved-runner execution must record lean --version,
lake --version, lake build, and the resolved Mathlib revision.

## 5. Validation status

| Item | Status | Evidence |
|---|---|---|
| Source and convention audit | PASS | Project policy and canonical matching notes inspected at pinned baseline |
| Recoil-deficit factorization | NOT RUN | Lean compiler unavailable here |
| Minimum-speed equivalence | NOT RUN | Lean compiler unavailable here |
| AFH versus invariant-transfer identity | NOT RUN | Lean compiler unavailable here |
| Raw/normalized coefficient identities | NOT RUN | Lean compiler unavailable here |
| P0/P rate-ratio expansion | NOT RUN | Lean compiler unavailable here |
| Independent Python spot checks | NOT RUN | Pending compiler and theorem review |
| Physical derivation of c_M | OUT OF SCOPE | This scaffold formalizes the declared rate-level definition |

## 6. Reproducibility and provenance

- Repository: lm846802297-bit/LZ-3-body-for-hdm
- Baseline branch: main
- Baseline commit: d2407050ed0f4975387bc6c05bc4509ccf375c31
- Development branch: research/lean4-formalization-p0-20261121
- Source blob SHAs are recorded in the task brief and provenance manifest.
- No external numerical input data are consumed.

## 7. Next steps

1. Run lake update and lake build with the pinned Lean and Mathlib versions.
2. Fix elaboration issues and archive exact compiler output.
3. Add independent Python spot checks for the proven algebraic identities.
4. Extend matching only after its physical derivation and momentum convention
   have been independently audited.
5. Open a focused PR after the local build and source review.
