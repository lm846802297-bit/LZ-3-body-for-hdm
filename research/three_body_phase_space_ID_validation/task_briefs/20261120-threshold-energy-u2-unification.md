# Research Task Brief — unify the exact-energy threshold map in fixed-speed and halo scans

**Task ID:** `20261120-threshold-energy-u2-unification`  
**Status:** in-progress  
**Prepared on:** 2026-11-20  
**Prepared by:** ChatGPT / GPT-6  
**Assigned to:** ChatGPT / GPT-6  
**Research topic:** three-body phase-space integration and seven-isotope halo-folded full-vs-I(D) validation  
**Baseline repository:** lm846802297-bit/LZ-3-body-for-hdm  
**Baseline branch and commit:** `main` @ `98fc6e3b3de9c7d282b6a68855b0dc50114d5618`  
**Related issue / PR / task:** PR #78, PR #74, PR #80, PR #85; new follow-up to the threshold-map audit

---

## 1. Research question

**Primary question**

Can the seven-isotope halo-folded full three-body (L^{00}) calculation use exactly the same threshold variable and Jacobian as the independent 943-point fixed-speed validation, and does the full 5–800 keV scan remain numerically converged after that change?

**Scope**

- Included:
  - Implement the exact energy-excess map (epsilon=W-W_{\min}=D_{\rm exact}u^2) in the shared phase-space integration module.
  - Use that map in the seven-isotope halo-folded full-vs-(I(D_{NR})) runner.
  - Verify the transformed Jacobian, endpoints, high-order agreement with the existing (W^2)-excess (u^2) map, and the full baseline/high-order halo scan.
  - Preserve the previous archived (W^2)-excess result and create a new versioned result record.
- Excluded:
  - Changing the amplitude, spin trace, halo distribution, isotope abundance, AFH response, mediator factor, (I(D_{NR})) definition, or zero-width setting of the historical PR #78 benchmark.
  - Promoting the zero-width diagnostic to the formal finite-pole-width production prescription.
  - Recomputing detector efficiency, exposure, energy-resolution smearing, or an LZ likelihood.
- Intended claim this task may support:
  - The fixed-speed and halo-folded calculations use the same threshold-energy variable and phase-space Jacobian, and the new halo scan is converged at the recorded recoil grid and quadrature settings.

## 2. Source papers, files, and repositories

| Type | Exact source and version | Relevant pages / equations / paths / symbols | Provenance, URL, or SHA-256 |
|---|---|---|---|
| Primary manuscript | Repository working manuscript, current main baseline | `paper-source/main.tex`, Eq. (6), Appendix VIII exact (W_{\max}^2) kinematics | Baseline commit below |
| Fixed-speed reference implementation | Current main | `research/three_body_phase_space_ID_validation/validate_full_L00_vs_ID.py`, `one_point`, `D_{exact}), `eps=D_{exact}t^2) | Baseline commit below |
| Halo implementation | Current main | `research/three_body_phase_space_ID_validation/validate_halo_seven_isotope_ID.py`, `velocity_weighted_kernels) | Baseline commit below |
| Shared phase-space implementation | Current main | `research/three_body_calculation_and_validation/phase_space_convergence.py`, `_integrate`, `integrate_i6) | Baseline commit below |
| Spin-trace / kinematics kernel | Current main | `research/three_body_calculation_and_validation/eq6_kernel.py` | Baseline commit below |
| Tests | Current main | `research/three_body_calculation_and_validation/tests/test_phase_space_convergence.py`; `research/three_body_phase_space_ID_validation/test_halo_seven_isotope_ID.py` | Baseline commit below |
| Prior halo result | PR #78 / PR #74 final integration archive | `research/three_body_phase_space_ID_validation/results/2026-11-19-halo-seven-isotope-full-vs-ID-full-recoil-scan/` | [PR #78](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/78); [PR #74](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/74) |
| Prior B baseline and detector fold | PR #80 / PR #85 | `research/nucleon_form_factor_B_baseline/` | [PR #80](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/80); [PR #85](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/85) |

Unavailable or inaccessible sources and their impact: N/A. All source files and archived native results needed for this task are present on the baseline main branch.

## 3. Git commit / version

- Repository: `lm846802297-bit/LZ-3-body-for-hdm`
- Baseline branch: `main`
- Baseline commit SHA: `98fc6e3b3de9c7d282b6a68855b0dc50114d5618`
- Relevant code paths:
  - `research/three_body_phase_space_ID_validation/validate_full_L00_vs_ID.py`
  - `research/three_body_phase_space_ID_validation/validate_halo_seven_isotope_ID.py`
  - `research/three_body_calculation_and_validation/phase_space_convergence.py`
  - `research/three_body_calculation_and_validation/eq6_kernel.py`
- Input / dataset version: AFH v6.0 default-density matrices and natural-xenon isotope weights already pinned by the existing halo runner.
- External package versions: Python 3.11 in the existing GitHub Actions workflow; NumPy, SciPy, SymPy.
- Working-tree state: new topic branch created from the exact main SHA; no inherited uncommitted changes.
- Exact revision against which results must be compared: the PR #78 / PR #74 archived baseline and higher-order CSVs on main.

## 4. Conventions

- Metric signature: (+---).
- Four-vector ordering: ((E,p_x,p_y,p_z)).
- Units: natural units; masses and energies in GeV inside the kernels; recoil scan labels in keV; speeds in km/s.
- Target frame: xenon nucleus initially at rest.
- (q_A^mu=P'^mu-P^mu) is the nuclear four-momentum transfer; (Q_A=|\mathbf q_A|=\sqrt{2m_AE_R+E_R^2}).
- (W^2=K^2=(p-q_A)^2), (W_{\min}=m_{\chi_1}+m_s), (W_{\max}=\sqrt{W_{\max}^2}) from exact four-vector kinematics.
- Fixed-speed threshold variable:
  [
  \epsilon=W-W_{\min},\qquad D_{\rm exact}=W_{\max}-W_{\min},\qquad
  \epsilon=D_{\rm exact}u^2,\quad 0\le u\le1.
  ]
- Exact Jacobian:
  [
  \frac{dW^2}{du}=2W\frac{dW}{du}=4W D_{\rm exact}u.
  ]
- Dimensionless phase-space Källén factor:
  [
  \lambda(W^2)=\frac{[W^2-(m_{\chi_1}+m_s)^2][W^2-(m_{\chi_1}-m_s)^2]}{W^4}.
  ]
- Full kernel measure:
  [
  J_{full}=\int_0^1du\,4W D_{\rm exact}u\sqrt{\lambda(W^2)}
  \int_{-1}^{1}dz\,\langle L^{00}\rangle_{\phi_*}.
  ]
- Azimuthal convention: normalized average over (\phi_*), consistent with Eq. (6) and the current shared kernel.
- Halo: truncated Standard Halo Model with (v_0=220), (v_E=232), (v_{esc}=544), and (v_{max}=776\,\mathrm{km/s}).
- Isotopes: Xe-128, 129, 130, 131, 132, 134, and 136; natural atom fractions are not renormalized; AFH coverage is 0.998158.
- Full-vs-(I(D_{NR})) comparison uses the exact four-vector physical halo domain for both kernels. The approximation is zero where (D_{NR}\le0), even if the exact domain is open.
- Width: retain `width_scheme="zero"` for direct comparison to the archived PR #78 diagnostic. This is a far-off-pole / numerical-comparison benchmark, not a replacement for the repository's formal asymmetric pole-width prescription.
- Unresolved conventions: N/A for this variable-transformation task.

## 5. Assumptions and approximations

| Assumption / approximation | Reason and source | Validity range | Possible impact / omitted contribution |
|---|---|---|---|
| Zero width in both internal propagators | Frozen PR #78 comparison benchmark | Existing (m_s=300\) keV, (Delta m=10\) MeV halo scan | Keeps the comparison identical to PR #78; does not establish formal finite-width production |
| Threshold-energy (u^2) map | Matches the independently coded fixed-speed transformation | (D_{exact}>0), (u\in[0,1]) | Changes only quadrature parameterization, not the physical integral |
| Truncated SHM | Existing PR #78 benchmark | (v_0=220), (v_E=232), (v_{esc}=544) km/s | No alternative halo model or annual modulation in this task |
| AFH-7 response coverage | AFH v6.0 default-density responses exist for seven isotopes | Natural atom fraction 0.998158 | Xe-124 and Xe-126 remain omitted without renormalization |

Model benchmark: (m_{\chi_1}=1\) TeV, (m_s=300\) keV, (Delta m=10\) MeV, (m_V=5\) GeV. The full scan covers 5–800 keV with 10-keV coarse spacing and 1-keV refinement from 180–320 keV, including 248 and 267 keV anchors.

## 6. Known validated results

| Result / claim | Exact scope and benchmark | Evidence, code/input revision | Status and tolerance |
|---|---|---|---|
| PR #78 high-order seven-isotope scan | 208 recoil points, 1,456 isotope rows; zero-width benchmark above | Archived native CSVs and RUN_MANIFEST on main; PR #78 / #74 | Reproducible and quadrature-converged on the archived (W^2)-excess (u^2) map |
| Natural-xenon full-vs-(I(D_{NR})) difference | Candidate interval 180–320 keV | High-order natural-xenon CSV | Maximum absolute difference 0.035519% at 320 keV |
| Full scan natural-xenon maximum | 5–800 keV | High-order natural-xenon CSV | 0.352762% at 695 keV; endpoint sensitivity is kept separate from candidate interval |
| Per-isotope candidate-region differences | Seven isotopes, 180–320 keV | High-order seven-isotope CSV | Maximum per isotope: 0.032592%–0.037722%, all at 320 keV |
| Prior quadrature convergence | Baseline (24; 8,4,4) vs higher order (32; 12,4,4) | Archived quadrature comparison CSV/JSON | Active-region natural-xenon full and (I(D)) shifts below (10^{-5}\%); zero support mismatches |

Relevant historical, provisional, diagnostic, or superseded results: the (W^2)-excess (u^2) mapping is retained as the prior version and must not be overwritten. The fixed-speed (epsilon=D_{exact}t^2) implementation is the exact mapping target for this follow-up.

## 7. Required independent derivation

1. Starting from (W=W_{min}+\epsilon), derive (dW^2=2W,dW) and (dW^2/du=4WD_{exact}u) for (\epsilon=D_{exact}u^2).
2. Express (W^2-W_{min}^2=\epsilon(2W_{min}+\epsilon)) in factorized form to avoid subtracting two (O(m_\chi^2)) quantities near threshold.
3. Show that the new mapped integral is mathematically identical to the original (dW^2\sqrt{\lambda}) integral and to the fixed-speed script's (t)-parameterization.
4. Compare the new energy-excess map with the previous (W^2)-excess (u^2) map at matched high-order settings; explain any finite-order difference as a quadrature-parameterization effect, not a physical approximation.

## 8. Required numerical checks

| Check | Method / independent implementation | Acceptance criterion / tolerance | Result |
|---|---|---|---|
| Dimensional and unit consistency | Derive Jacobian and confirm dimensions | (dW^2/du) has GeV(^2) | NOT RUN |
| Analytic limits / endpoints | Test (u=0,1), (D_{exact}=0), and factorized (\Delta W^2) | Exact endpoints; zero measure at threshold | NOT RUN |
| Conservation and on-shell identities | Reuse stable phase-space point builder | Existing tolerances; no regression | NOT RUN |
| Signs and normalization | Compare normalized azimuthal average and raw-(d\phi) identity | Existing Eq. (6) prefactor tests remain passing | NOT RUN |
| Independent mapping comparison | Compare energy-excess (u^2) and (W^2)-excess (u^2) maps at high order | Relative difference below (2\times10^{-8}) at selected points | NOT RUN |
| Quadrature convergence | Full baseline and high-order halo scans on identical 208-point grid | Active natural-xenon full and (I(D)) shifts below (2\times10^{-5}\%); zero support mismatches | NOT RUN |
| Regression against frozen benchmark | Compare new scan with prior archived CSVs | Report all-grid and candidate-region changes; no silent replacement | NOT RUN |
| Output integrity | Native CSV/JSON, row counts, manifest, SHA-256 | 1,456 isotope rows and 208 natural-xenon rows per scan; all hashes verified | NOT RUN |

Record actual residuals, commands, logs, and exact code/input revisions in the return record and result README.

## 9. Expected output

| Deliverable | Required path / format | Required contents and metadata | Acceptance condition |
|---|---|---|---|
| Task brief | `research/three_body_phase_space_ID_validation/task_briefs/20261120-threshold-energy-u2-unification.md` | This specification | Linked from README/PR |
| Shared integration map | `research/three_body_calculation_and_validation/phase_space_convergence.py` | New `threshold_energy_u2` mapping with stable factorized (Delta W^2) | Derivation and tests pass |
| Halo runner | `research/three_body_phase_space_ID_validation/validate_halo_seven_isotope_ID.py` | Use new mapping; record it in metadata | Full scan completes |
| Tests | Existing phase-space and halo test modules | Mapping/Jacobian/end-point and convergence tests | All relevant tests pass |
| Validation report | `research/three_body_phase_space_ID_validation/HALO_SEVEN_ISOTOPE_VALIDATION.md` | Correct status, exact map, archived result comparison | No stale “pending” claim |
| Native results | `research/three_body_phase_space_ID_validation/results/2026-11-20-threshold-energy-u2-halo-scan/` | Baseline/high-order CSVs, metadata, comparison summary, manifest, SHA256SUMS | Counts and hashes verified |
| PR / archive record | New PR to main | Focused code, tests, report, native outputs | Merge only after review of actual evidence |

**Reproduction commands and environment:** Python 3.11; run the existing unit tests, then run the same 5–800 keV scan at baseline ((24;8,4,4)) and high order ((32;12,4,4)).

**Required conclusion level:** reproducible, with numerical convergence validated for the stated zero-width benchmark and scan grid.

## 10. Unresolved questions

| Open question or discrepancy | Competing sources / conventions | Expected impact | Blocking? | Next discriminating check |
|---|---|---|---|---|
| Fixed-speed uses (epsilon=W-W_{min}), while halo runner previously used (W^2-W_{min}^2) as the squared integration variable | `validate_full_L00_vs_ID.py` vs `phase_space_convergence.py` | Finite-order quadrature differences | This is the task being resolved | Implement exact same energy-excess map and compare both mappings |
| Formal finite-width production | PR #78 zero-width diagnostic vs later pole-width work in PR #65–#67 | Changes the physical kernel when width effects matter | Not blocking this variable-map audit; must remain separately labelled | Continue the formal pole-width chain separately |

---

## Execution instructions

- Preserve the previous PR #78 archive unchanged.
- Do not change the benchmark, halo, AFH response, isotope weights, full-vs-(I(D_{NR})) definition, or width scheme.
- Implement the exact fixed-speed energy-excess variable in the shared halo kernel.
- Run and report all checks actually performed; do not infer a pass from code inspection alone.
- Keep the zero-width result labelled as the historical far-off-pole / numerical-comparison benchmark.

## Return record

- Answer and scope actually resolved: pending
- Independent derivation / key equations: pending
- Conventions confirmed or changed (with reasons): pending
- Assumptions and validity range: pending
- Numerical checks, tolerances, and actual residuals: pending
- Unresolved discrepancies and next checks: pending
- Output paths, checksums, reproduction commands: pending
- Exact completion commit SHA / PR: pending
- Final status and the precise claim it supports: pending

## Change log

| Date | Revision | Change and reason | Affected conclusions / outputs |
|---|---|---|---|
| 2026-11-20 | v1 | Created before implementation to unify the fixed-speed and halo threshold maps | No numerical result changed yet |
