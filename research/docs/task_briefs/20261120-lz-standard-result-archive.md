# Research Task Brief — Standardized archive for three-body phase space and AFH results

**Task ID:** `20261120-lz-standard-result-archive`  
**Status:** in-progress  
**Prepared on:** 2026-11-20  
**Prepared by:** ChatGPT  
**Assigned to:** ChatGPT  
**Research topic:** Three-body Eq. (6) phase-space and AFH natural-xenon response/rate archive  
**Baseline repository:** lm846802297-bit/LZ-3-body-for-hdm  
**Baseline branch and commit:** `main` @ `4136bddaf0683ca85830ead7705b1c7d5dcf061b`  
**Related issue / PR / task:** [PR #84](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/84)

---

## 1. Research question

**Primary question**

Add a reusable v1.0.0 result-record writer to the LZ repository and connect it to the existing three-body/AFH numerical entry points so completed runs emit a standard run manifest, result summary, validation report, convergence evidence, CSV metadata, and SHA-256 inventory.

**Scope**

- Included: archive tooling, provenance capture, CSV unit/dimension capture, validation-record generation, tests, and wiring to the AFH-7/Hybrid-9 continuous-spectrum calculation.
- Excluded: changing the Eq. (6) amplitude, phase-space measure, AFH response, isotope masses/abundances, halo model, detector efficiency, or any physics benchmark.
- Intended claim: the existing calculation outputs can be archived and independently checked in a common structure without altering their numerical values.

## 2. Source papers, files, and repositories

| Type | Exact source and version | Relevant paths / symbols | Provenance |
|---|---|---|---|
| Repository policy | LZ-3-body-for-hdm main, 2026-11-20 | `AGENTS.md`, `research/WORKFLOW.md`, `research/RESEARCH_TASK_HANDOFF_STANDARD.md` | main SHA above |
| Three-body kernel | Current main | `research/three_body_calculation_and_validation/eq6_kernel.py`, `phase_space_convergence.py` | pinned baseline SHA |
| AFH natural-xenon calculation | Current main | `research/afh_default_density_natural_xenon_halo/run_afh7_hybrid9_continuous_spectrum.py` | blob SHA `560f1e7f1eeb3d50d05ecd6766e21f723573b828` |
| AFH response calculation | Current main | `research/afh_default_density_natural_xenon_halo/run_afh_default_xenon_responses.py` | blob SHA `f70cba8781bd08d9f082527d5dd0d0e101ae5021` |
| Existing output metadata | Current main | `research/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_continuous_2026-11-14/metadata.json` | blob SHA `8b4cdc5cb6003face886b7866bdd94d584c5f225` |
| Result data standard | PR #84 branch | `research/STRUCTURED_RESULT_DATA_STANDARD.md`, `research/schemas/research-result-record-v1.0.0.schema.json` | PR #84 head |

Unavailable sources: none required for this archive-only implementation.

## 3. Git commit / version

- Repository: `lm846802297-bit/LZ-3-body-for-hdm`
- Baseline branch: `main`
- Baseline commit SHA: `4136bddaf0683ca85830ead7705b1c7d5dcf061b`
- Implementation branch: `docs/structured-result-data-standard-20261120`
- Related PR: #84
- Physics code/input revisions: the run writer must record the actual checked-out commit and hashes of the AFH source, isotope weights, response-grid inputs, and executing script.
- Working-tree state: GitHub main was inspected; changes are isolated to the PR branch.

## 4. Conventions

- Units: natural units remain internal to the physics calculation; exported columns use explicit suffix units and the standard JSON `units` map.
- Three-body kinematics: preserve separate `q_A`, `q_\chi`, `k_s`, `E_R`, and `Q_A` meanings as defined by the existing momentum-variable convention.
- AFH spatial transfer: preserve exact `q_A=\sqrt{2m_AE_R+E_R^2}`; do not replace with an NR approximation.
- Nuclear response: preserve the AFH default-density normalization and isotope availability; do not renormalize the seven supported natural-xenon abundances.
- Halo and detector layers: keep pre-detector theory rates distinct from detector-level event yields.
- Amplitude, propagator width, and phase-space conventions: unchanged from the source scripts and current approved records.

## 5. Assumptions and approximations

| Assumption / approximation | Reason and source | Validity range | Possible impact |
|---|---|---|---|
| Archive writer wraps existing metadata and outputs | This task changes provenance/serialization only | New runs using wired entry points | No change to numerical outputs |
| CSV units are mapped explicitly from column names/types | Required for machine-readable arrays | Listed runner outputs | Unknown columns must fail closed, not receive guessed units |
| Archive status begins as `local_only` | GitHub PR/main status is not known at calculation time | Every new local run | Updated only after actual commit/merge verification |

## 6. Known validated results

- Existing Eq. (6), AFH, halo-fold, and detector-fold calculations remain the frozen numerical baseline.
- The existing AFH-7/Hybrid-9 continuous run metadata records 756 response-comparison rows, 3024 isotope-kernel rows, 1344 natural-xenon spectrum rows, and 144 quadrature-crosscheck rows.
- Existing quadrature metadata reports maximum speed-order change (1.4328279531738985\times10^{-6}) and maximum kernel-order change (4.6351877891481763\times10^{-10}), against a (5\times10^{-3}) acceptance tolerance.
- These are historical outputs, not results of this new integration task.

## 7. Required independent derivation

N/A — no physics formula or amplitude is changed. The implementation must preserve the existing formulas and serialize their results without transformation other than CSV/JSON packaging.

## 8. Required numerical checks

| Check | Method | Acceptance |
|---|---|---|
| Schema | Draft 2020-12 validator | All generated records valid |
| CSV integrity | Row/header/unit/hash checks | Exact match |
| Provenance | Source/input SHA-256 | All available local inputs match |
| Numeric safety | Reject NaN/Infinity | No non-finite serialized values |
| Regression | Existing physics tests | Unchanged baseline tests pass |
| Output preservation | Compare original physics CSV/metadata bytes before/after writer | Byte-identical |

## 9. Expected output

- Reusable writer: `research/result_archive.py`
- Unit and schema tests: `research/tests/test_result_archive.py`
- Integration: AFH-7/Hybrid-9 continuous-spectrum runner; phase-space audit integration is a separate adapter if its output is invoked.
- Standard records: `run_manifest.json`, `result_summary.json`, `validation_report.json`, `SHA256SUMS.txt`, and README within each run output directory.
- PR update: extend PR #84.
- Required conclusion level: reproducible archive tooling; no new physics claim.

## 10. Unresolved questions

- None for the archive interface. Any missing or unavailable input metadata must remain explicitly missing/partial rather than inferred.
