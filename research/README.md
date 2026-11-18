# Research archive

All research materials are kept under this directory so the repository root stays uncluttered. The current canonical archive is the repository's main branch.

## Repository file map

- [Complete repository file map](FILE_MAP.md): scientific-stage classification, directory responsibilities, canonical-result warnings, and navigation order.

## Research workflow

Read [WORKFLOW.md](WORKFLOW.md) before starting a new study. Use [_template/README.md](_template/README.md) for each new topic, and follow the repository PR checklist. A successful software test or workflow run validates only the code paths and assertions that it actually covers.

## Directory map

- [_template/](_template/README.md): starting point for a new study README; copy and fill it before adding a new research topic.
- [docs/](docs/README.md): cross-topic model definitions, phenomenology notes, the AFH/natural-xenon main report, appendices A–I, formula cross-reference index, source audits, and research decisions.
- [three_body_kinematic_audit/](three_body_kinematic_audit/README.md): threshold conditions, maximum scalar mass, and phase-space checks.
- [three_body_calculation_and_validation/](three_body_calculation_and_validation/README.md): Eq. (6) kernel, GCN/JJ55 natural-xenon halo-folded continuous spectra, fixed-speed Xe-131 diagnostics, the supplied 450-keV pointwise benchmark, tests, and numerical outputs. The 450-keV fixed-speed curve is a single-isotope zero-width diagnostic, not a halo or detector-level prediction.
- [afh_default_density_xe131/](afh_default_density_xe131/README.md): AFH v6.0 Xe-131 response, normalization and momentum-convention audits, AME2020/CODATA-2022 mass diagnostics, the native 2,401-node \(M,\Phi'',M\Phi''\) export (response-level validator PASS), and the historical I6 mapping/quadrature audit. The latter reproduces I6 only; it does not validate the full differential cross section.
- [afh_default_density_natural_xenon_halo/](afh_default_density_natural_xenon_halo/README.md): 七同位素 AFH v6.0 default-density 的 Python source-translation 响应网格（16,807 行；native Mathematica 七同位素重执行仍 pending）、selected-q 60 位 mpmath 验证、插值审查，以及 AFH-7/Hybrid-9 的 84 点全范围反冲网格谱。最终高阶谱归档目前仅有外部 checksum；selected-point AME2020 fold 仍是独立质量方案记录。以上都不是 detector-level LZ likelihood。
- [afh_isotope_response_equivalence/](afh_isotope_response_equivalence/README.md): AFH v6.0 七同位素 \(M\) 响应归一化/多极审计，以及完整 VV 夸克—核子匹配、三体流与 AFH 核响应讨论；PR #51 另已归档 Xe-131 native \(M,\Phi'',M\Phi''\) 响应（response-level PASS）；主讨论档案 P 节现汇总该结果、AFH-7 七同位素 benchmark 和四 benchmark 响应对照。完整三体收缩、有限 \(t_N\) 输入及 \(\Delta/\Sigma'\) 空间响应仍待完成。
- [Canonical VV–AFH discussion archive](afh_isotope_response_equivalence/docs/QUARK_TO_NUCLEON_VECTOR_CURRENT_MATCHING.md): the single long-form record for the original discussion, A–P corrections, step-by-step derivations §§27–35, AFH response-database architecture §§36–37, the complete three-body recoil-rate / response-matrix specification §§38–44, and P's quantitative AFH response benchmarks with validation boundaries. Main-report §15 provides the integrated rate-level summary; these are theory specifications, not claims that the full numerical contraction has passed.
- [PR #53 — four-component vector-current diagnostic](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/53): branch-level (L^{\mu\nu}) and coherent point-charge-current audit; it does not calculate internal nuclear currents.
- [lz_detector_response/](lz_detector_response/README.md): LZ 2026 public-input and NEST provenance, NR/ER response audits, event-level and two-dimensional three-body response folds, paired Parametric/Full S1 ten-seed statistics and bootstrap, Fig. S2 rate-level folds, and selection-stage diagnostics. The [extended NR/ER archive index](lz_detector_response/lz_2026_extended_nr/README.md) distinguishes the reproducible intermediate NEST proxy from the missing official waveform-level selected PDF and likelihood.
- [figure_packs/](figure_packs/README.md): curated scientific figure collections, indexes, manifests, checksums, and scope notes; metadata does not imply that every image binary is committed.
## Current result layers

Keep the following quantities separate:

1. **Microscopic level:** single-isotope, fixed-speed \(d\sigma_A/dE_R\).
2. **Nuclear/target level:** isotope-specific responses and natural-xenon abundance weighting.
3. **Astrophysical level:** laboratory-frame halo average \(dR/dE_R\).
4. **Detector interface:** one-dimensional efficiency-weighted expected event counts plus an intermediate NEST-based two-dimensional S1c/log10(S2c) response proxy. These are distinct result layers and must not be multiplied together as if they were independent efficiencies.
5. **Experiment likelihood:** official waveform-level selection, calibration/background nuisance parameters, detector-systematic covariance, and profile likelihood; this layer is not implemented here.

## Phase II high-energy tail audit

- [High-energy tail nuclear-model sensitivity](docs/appendices/09H_high_energy_tail_nuclear_model_sensitivity.md): efficiency-weighted 225–269.9 keV comparison of AFH-7, Hybrid-9, Helm-9, GCN and JJ55.

## Organization rules

- Keep research-specific scripts, tests, numerical tables, plots, and audit reports together under the relevant study directory.
- Keep project-level research notes in research/docs/.
- Keep the manuscript source and original figures in paper-source/.
- Record assumptions and validation boundaries alongside each result; passing software tests does not by itself settle unspecified model assumptions.
- Preserve native outputs, run manifests, source/input revisions, and checksums; do not use ZIP/TAR delivery bundles as substitutes for extracted research files.


## Figure 2 P0–P2 audit records

- [Figure 2 numerical-results master index](docs/supplements/three_body_results_master_index_2026-11-16.md): current main-branch result provenance, including the full AFH-7 response grid and 84-point spectra.
- [Phase 1 scientific content audit](docs/supplements/scientific_content_audit_2026-11-16.md): current numerical-method and documentation consistency findings.
- [Figure 2 physics-formula audit](docs/supplements/three_body_physics_formula_audit_2026-11-13.md): equation, implementation, normalization, and validation cross-checks.
- [Figure 2 scientific-status table](docs/supplements/three_body_scientific_status_2026-11-13.md): verified scope and remaining scientific boundaries.

### Mathematica three-body natural-xenon calculation

`three_body_natural_xenon/` contains the reorganized main Mathematica notebook, AFH v6 xenon response data, usage notes, and archived comparison tables. The main calculation is inline in the notebook and uses FeynCalc plus Mathematica `NIntegrate`. Optional FeynRules/FeynArts checks need those external packages and a local model-export environment; the notebook keeps their saved outputs, but the third-party packages are not bundled. The run record is explicitly marked historical because this reorganization did not rerun all calculations.
