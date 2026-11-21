# Research Task Brief — Lean 4 P0 formalization

**Task ID:** 20261121-lean4-p0-formalization  
**Status:** in-progress  
**Prepared on:** 2026-11-21  
**Prepared by:** ChatGPT  
**Assigned to:** ChatGPT / project owner  
**Research topic:** Formal verification of LZ three-body kinematics and nucleon-current normalization  
**Baseline repository:** lm846802297-bit/LZ-3-body-for-hdm  
**Baseline branch and commit:** main @ d2407050ed0f4975387bc6c05bc4509ccf375c31  
**Related PR:** Not yet opened

---

## 1. Research question

Can the selected analytic identities for the reduced three-body recoil kernel and the current M-only nucleon charge-matching normalization be stated in Lean 4 and checked by its kernel?

Included: recoil-deficit factorization; minimum-speed threshold equivalence; distinction between t_N, Q_N^2, and AFH Q_A^2; raw/normalized c_M identities; P0/P zero-transfer and rate-ratio algebra.

Excluded: full Dirac-Pauli spinor derivation; complete three-body Dirac traces; two-diagram Ward identity; AFH OBDME generation; numerical phase-space, Halo, and detector calculations.

The intended claim is limited to formal proofs of the listed algebraic identities after a successful Lean build. This scaffold alone does not establish a new physical or numerical result.

## 2. Sources and provenance

| Source | Exact revision / location | Blob SHA |
|---|---|---|
| Repository AGENTS.md | main baseline, §§3–4 and 8–9 | 1a8c76fc54fa5b0101df904b5698a5b4ee3752f2 |
| Model and amplitude note | research/docs/01_model_and_amplitude.md | 8d8daf3e6d45235040c98bf3e3ed374c449baa2d |
| c_M normalization note | research/nucleon_form_factor_B_baseline/CM_RAW_NORMALIZATION_AND_AFH_M_RESPONSE.md | 04f53726979d2ab936932de3ead85e78eb3ebfb3 |
| P0/P baseline note | research/nucleon_form_factor_B_baseline/P0_VS_P_POINTLIKE_DIRAC_BASELINES.md | a618c2d209e3a19af028e670f155d322cd6ee6a6 |
| Research workflow | research/WORKFLOW.md | 31f1a62482edfd5b09976584d79d15bd29de54fb |

Lean 4 stable v4.36.0 and matching Mathlib v4.36.0 are pinned in the package. No external numerical data are used.

## 3. Git baseline

- Repository: lm846802297-bit/LZ-3-body-for-hdm
- Baseline: main @ d2407050ed0f4975387bc6c05bc4509ccf375c31
- Development branch: research/lean4-formalization-p0-20261121
- The development branch was confirmed identical to main before the first formalization commit.
- Relevant code and data inputs: none in this algebraic scaffold.
- No local changes existed before the first commit.

## 4. Conventions

- Natural units are used in the physics interpretation; Lean statements are over the real numbers and do not perform unit conversions.
- q is the positive spatial recoil-momentum magnitude in the reduced heavy-particle kernel, not a generic four-momentum.
- mu > 0 is the DM-nucleus reduced mass; mS is the scalar mass; v is incident speed.
- D = q v - q^2/(2 mu) - mS.
- v_min = q/(2 mu) + mS/q.
- q_N^mu = p_N'^mu - p_N^mu and t_N = q_N^2.
- Adopted impulse invariant: t_N = t_A = -2 m_A E_R and Q_N^2 = -t_N = 2 m_A E_R.
- AFH spatial momentum: Q_A^2 = |q_A|^2 = 2 m_A E_R + E_R^2; y_A = b_A^2 Q_A^2/4.
- The substitution t_N = -Q_A^2 is not adopted. It is represented as a separate alternative; its difference from the adopted invariant is exactly E_R^2.
- c_M_raw = F1 + t_N(F1+2F2)/(8m_N^2).
- c_M_hat = c_M_raw/3, paired with g_VN = 3 g_Vq.
- At zero transfer F1^{uds,N}(0)=3, c_M_raw(0)=3, and c_M_hat(0)=1.
- P0 has c_M_hat=1; P has c_M_hat=1-Q_N^2/(8m_N^2).
- The c_M expression is treated as the repository's current M-only rate-level definition, not as a proved derivation from the full covariant current.
- Metric and gamma-matrix conventions are not required for these scalar algebraic modules.

## 5. Assumptions and approximations

| Assumption | Source / reason | Scope and impact |
|---|---|---|
| Reduced heavy-particle recoil kernel | Project's reduced three-body kinematics | Does not replace exact relativistic phase space |
| q > 0 and mu > 0 | Needed for threshold equivalence | q=0 makes v_min undefined |
| M-only rate-level matching | Canonical repository matching note | Does not include all AFH responses |
| Impulse invariant t_N=t_A | Canonical project convention | Distinct from AFH spatial Q_A^2 |
| Real-number algebra | Initial proof layer | Units are documented, not encoded as dependent types |

## 6. Known results

The repository defines the raw/normalized c_M convention and P0/P rate-level prescription in the pinned source notes. These are project conventions whose algebraic consequences are to be checked; their physical derivation is not claimed by this task. The reduced recoil threshold formula is present in the model-and-amplitude record; its formal proof is pending.

## 7. Required derivations

1. Prove D = q(v-v_min).
2. Prove D >= 0 iff v >= v_min under q>0 and mu>0.
3. Prove Q_A^2-Q_N^2=E_R^2.
4. Prove the difference between t_N=-2m_AE_R and the alternative -Q_A^2.
5. Prove c_M_raw(0)=3, c_M_hat(0)=1, and c_M_raw=3 c_M_hat.
6. Prove P reduces to P0 at Q_N^2=0 and expand the squared P/P0 rate multiplier.
7. Keep the algebraic definition of c_M separate from its physical spinor derivation.

## 8. Checks and acceptance criteria

| Check | Method | Acceptance criterion | Status |
|---|---|---|---|
| Lean build | lake update && lake build | Exit code 0; no sorry/admit | NOT RUN |
| Threshold identities | Lean kernel and independent symbolic check | Exact equality | NOT RUN |
| Momentum distinction | Lean proof | Exact equality Q_A^2-Q_N^2=E_R^2 | NOT RUN |
| Charge normalization | Lean proof | Exact equality, no floating point | NOT RUN |
| P0/P ratio expansion | Lean proof and Python spot check | Exact symbolic equality; numerical residual < 1e-12 | NOT RUN |
| Physical derivation of c_M | Independent spinor/NR derivation | Out of scope for this first slice | N/A |
| Provenance | SHA-256 and source blob SHAs | Manifest matches committed source | NOT RUN |

## 9. Deliverables

- Lean package: research/lean4_formalization/
- Study README: research/lean4_formalization/README.md
- Formal statements: ThreeBody/Kinematics.lean and ThreeBody/NucleonCurrent/Normalization.lean
- Provenance: research/lean4_formalization/provenance.json
- Task brief: research/docs/task_briefs/20261121-lean4-p0-formalization.md

Reproduction command from the package directory: lake update && lake build.

Required conclusion level: exploratory until compilation and theorem review pass.

## 10. Unresolved questions

| Question | Competing definitions | Impact | Blocking? | Next check |
|---|---|---|---|---|
| t_N versus -Q_A^2 | Canonical t_N=t_A=-2m_AE_R versus spatial substitution -Q_A^2 | Changes form-factor argument and finite-transfer correction | Not blocking for this scaffold | Re-derive from nuclear four-transfer and metric before changing convention |
| Physical derivation of c_M | Current M-only matching definition versus full covariant Dirac-Pauli current | Limits physical scope of the theorem | Blocks a full-current claim only | Independent spinor reduction |
| Compiler environment | Lean/Lake unavailable in active Linux image | No build PASS can be claimed | Blocks PASS status | Run pinned toolchain in enabled environment |

## Execution record

Initial source files are authored. Lean compilation, Python spot checks, and the independent physical derivation are not yet complete. Update only after actual execution.

## Change log

| Date | Revision | Change |
|---|---|---|
| 2026-11-21 | 0.1 | Initial P0 formalization task |
