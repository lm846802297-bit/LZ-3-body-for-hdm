# Research Compute Policy / 科研计算执行规范

**Status:** Author-approved normative policy  
**Effective date:** 2026-11-20  
**Applies to:** All numerical, symbolic, phenomenological, data-processing, and computational-validation work in this research project.

## 1. Decision / 总体决策

The project uses a three-part architecture with strictly separated responsibilities:

1. **Primary computation — the current ChatGPT-provided Linux Python environment, when available.** Run the main scientific calculations directly in the active research session using the available local Python runtime and scientific libraries (for example Python, NumPy, SciPy, SymPy, and project-specific tools). This means the session's Linux compute environment; it does **not** mean the user's Windows desktop.
2. **GitHub — canonical source and research archive.** Store versioned source code, input-data provenance, run manifests, native numerical outputs, plots, validation reports, and pull-request history. GitHub is the durable record, not the primary numerical execution engine.
3. **GitHub Actions — independent verification.** Use Actions for CI, regression tests, selected independent recalculations, cross-platform checks, and reproducibility checks against the primary results. Actions must not silently replace the primary computation or become a prerequisite for continuing research.

This division is normative for this project. Do not reopen it for each task.

## 2. Primary computation / 主计算环境

- Start the main calculation in the current ChatGPT Linux compute environment whenever the required source, inputs, dependencies, memory, CPU time, and storage are available.
- Execute the actual scientific program in that environment. Do not describe a result as locally recomputed merely because a GitHub Actions artifact was downloaded or inspected.
- The term **local computation** in this policy means execution in the active ChatGPT Linux session/container, not execution on the user's physical computer.
- The user's Windows workstation/GPU is a separate machine. Do not claim access to its filesystem, CPU, GPU, or installed software unless an explicitly authorized connection/runner has actually been established and verified.
- If the active Linux environment cannot perform a task (for example, unavailable dependency, inaccessible input, resource limit, or incompatible native software), state the exact blocker. Continue with feasible CPU/local alternatives where scientifically sound. Do not silently move the primary workload to Actions.
- Do not redesign a validated numerical method merely to use a GPU. Introduce GPU acceleration only when a measured performance need justifies it and the accelerated implementation is independently checked against the established reference.

## 3. GitHub repository responsibilities / GitHub 归档职责

GitHub is the canonical versioned archive for:

- source code and exact source revisions;
- input data or immutable source locations, versions, and checksums;
- run configuration, command line, parameters, units, conventions, numerical grids, quadrature orders, tolerances, and boundary conditions;
- software/runtime and dependency versions;
- native, directly usable output files (CSV, JSON/JSONL, HDF5, ROOT, TXT, or the relevant native format);
- plots, tables, audit reports, logs/checkpoints needed to reproduce or resume substantial runs;
- SHA-256 manifests and the associated pull request/review history.

Every result used to support a scientific claim, figure, benchmark, limit, or milestone must be archived in its relevant research repository. Extract transfer ZIP/TAR bundles before committing; preserve native files and meaningful directory structure. Do not leave the only copy in a temporary session, local workspace, chat attachment, or expiring Actions artifact.

Use a task branch and pull request unless the project owner explicitly directs otherwise. Do not push research changes directly to `main` by default. After upload, retrieve the committed files and verify paths, sizes, counts, and checksums. Keep archival status separate from scientific validation status.

## 4. Actions responsibilities / Actions 独立验证职责

GitHub Actions may be used for:

- syntax, unit, regression, and integration tests;
- independent recalculation of selected benchmark points or reduced grids;
- independent implementation or platform cross-checks;
- source/data fingerprint checks and artifact-integrity verification;
- automated checks that protect the repository from regressions.

For an Actions calculation, record its exact source commit, inputs, command, settings, environment, logs, outputs, and artifact identity. Compare its result with the primary computation under matched physical assumptions and numerical conventions.

Actions status is evidence only for the checks actually executed. A green workflow does not by itself establish a physical result; a failed or unavailable workflow does not invalidate an independently completed primary calculation. Do not wait for queued, unavailable, cancelled, or infrastructure-failed Actions runs before continuing research. Report the exact status truthfully.

Actions must not be the default or sole location for the main parameter scan, long numerical integration, production of the authoritative result, or archival of the only copy of a result. A Windows self-hosted runner or other remote runner is not the user's local machine; use it only for an explicitly authorized, trusted, scoped verification task and follow its security rules.

## 5. Run provenance and acceptance / 运行来源与验收

For every substantial run, record at minimum:

1. repository, branch, exact source commit, and relevant source-file/blob identities;
2. input provenance, version, file sizes, and SHA-256 hashes;
3. exact command/entry point and all physical and numerical parameters;
4. runtime, operating system, Python and dependency versions, and relevant hardware/resource information;
5. output paths, formats, row/record counts, units, and SHA-256 checksums;
6. tests and validation actually performed, their tolerances, and their results;
7. known differences between the primary run and any independent Actions run.

Scientific acceptance must be based on the appropriate physics and numerical evidence: analytic identities, dimensions and units, conservation laws, limiting cases, detailed balance/Ward identities where applicable, independent implementations, energy/angular/radial convergence, interpolation error, integration error estimates, and uncertainty analysis. Choose checks according to the claim; do not treat a generic test count as proof of physical correctness.

Report four statuses separately: **computed**, **archived**, **numerically validated**, and **physically validated**. Do not promote a result from one status to another without the corresponding evidence.

## 6. Failure and fallback rules / 失败与备用规则

- A GitHub outage, Actions queue, CI failure, or artifact-download failure must not stop a feasible primary calculation in the current Linux environment.
- A primary-environment limitation must be reported specifically; do not claim that a calculation ran if it did not.
- If a primary result cannot be reproduced in Actions, first compare source SHA, input hashes, dependency versions, floating-point precision, conventions, and tolerances. Diagnose the discrepancy rather than tuning the primary result to force agreement.
- If Actions cannot run, record it as unavailable/blocked/unrun and proceed with the scientific checks that can be performed locally.
- If the ChatGPT Linux environment is unavailable or insufficient, do not silently treat Actions as the replacement primary environment. State the blocker and use an explicitly approved alternative execution environment, recording that change in the run manifest.

## 7. Security and scope / 安全与适用范围

- Never commit credentials, access tokens, private keys, personal data, or machine-specific secrets.
- Never run untrusted pull-request code or arbitrary user-supplied commands on a persistent self-hosted runner.
- Pin cross-repository workflows and research checkouts to reviewed full commit SHAs; use least-privilege credentials.
- This policy defines execution and evidence management. It does not change the scientific model, physical assumptions, numerical acceptance thresholds, or repository-specific archival and merge rules. Where another project rule is stricter and compatible, follow the stricter rule. If a genuine conflict exists, record it and resolve it explicitly rather than silently overriding either rule.

---

## 中文摘要

本项目固定采用：

- **主计算：** 当前 ChatGPT 会话提供的 Linux Python 计算环境；直接运行主积分、扫描、收敛分析和作图。这里的“本地”不是用户的 Windows 电脑。
- **GitHub：** 保存源码、输入来源、运行清单、原生结果、图表、审计记录和校验和，作为长期、可追溯的研究档案。
- **GitHub Actions：** 仅承担 CI、回归测试、选定基准点独立复算和跨平台交叉验证，不替代主计算，也不作为继续科研的前置条件。

每项重要计算都必须记录精确源码版本、输入及哈希、命令、参数、环境、输出和实际执行的验证。分别报告计算完成、结果归档、数值验证和物理验证状态。Actions 失败不应阻断可行的主计算；主计算环境不可用时，必须明确说明并记录经批准的备用环境，不能悄悄把 Actions 改作主计算环境。
