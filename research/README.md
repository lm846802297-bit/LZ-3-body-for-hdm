# Research archive

All research materials are kept under this directory so the repository root stays uncluttered. The current canonical archive is the repository's main branch.

## Repository file map

- [Complete repository file map](FILE_MAP.md): scientific-stage classification, directory responsibilities, canonical-result warnings, and navigation order.

## Research workflow

Read [WORKFLOW.md](WORKFLOW.md) and the mandatory [research source hierarchy](RESEARCH_GOVERNANCE_AND_SOURCE_HIERARCHY.md) before starting a new study. Use [_template/README.md](_template/README.md) for each new topic, and follow the repository PR checklist. A successful software test or workflow run validates only the code paths and assertions that it actually covers.

## Directory map

- [_template/](_template/README.md): starting point for a new study README; copy and fill it before adding a new research topic.
- [docs/](docs/README.md): cross-topic model definitions, phenomenology notes, the AFH/natural-xenon main report, appendices A–G, formula cross-reference index, source audits, and research decisions.
- [three_body_kinematic_audit/](three_body_kinematic_audit/README.md): threshold conditions, maximum scalar mass, and phase-space checks.
- [three_body_calculation_and_validation/](three_body_calculation_and_validation/README.md): Eq. (6) kernel, GCN/JJ55 natural-xenon halo-folded continuous spectra, fixed-speed Xe-131 diagnostics, the supplied 450-keV pointwise benchmark, tests, and numerical outputs. The 450-keV fixed-speed curve is a single-isotope zero-width diagnostic, not a halo or detector-level prediction.
- [afh_default_density_xe131/](afh_default_density_xe131/README.md): AFH v6.0 Xe-131 response, normalization and momentum-convention audits, AME2020/CODATA-2022 mass diagnostics, and the historical I6 mapping/quadrature audit. The latter reproduces I6 only; it does not validate the full differential cross section.
- [afh_vv_phi_xe131/](afh_vv_phi_xe131/README.md): AFH Xe-131 W_Phi'' and W_MPhi'' response audit for the VV nucleon-current branch; includes the 2401-point grid, mpmath checks, native Mathematica comparison runner, and a first M+Phi'' vector-charge matching benchmark using zero-momentum form-factor anchors. Finite-t form factors, spatial-current responses, and the all-isotope natural-xenon correction remain pending.
- [afh_default_density_natural_xenon_halo/](afh_default_density_natural_xenon_halo/README.md): 七同位素 AFH default-density 响应网格（16,807 行）、selected-q 60 位 mpmath 验证、插值审查，以及 AFH-7/Hybrid-9 的 84 点全范围反冲网格谱。最终高阶谱归档目前仅有外部 checksum；selected-point AME2020 fold 仍是独立质量方案记录。以上都不是 detector-level LZ likelihood。
- [lz_detector_response/](lz_detector_response/README.md): LZ 2026 public-input and NEST provenance, NR/ER response audits, event-level and two-dimensional three-body response folds, paired Parametric/Full S1 ten-seed statistics and bootstrap, Fig. S2 rate-level folds, and selection-stage diagnostics. The [extended NR/ER archive index](lz_detector_response/lz_2026_extended_nr/README.md) distinguishes the reproducible intermediate NEST proxy from the missing official waveform-level selected PDF and likelihood.
- [lz_inelastic_2to2_afh_reference/](lz_inelastic_2to2_afh_reference/README.md): AFH v6.0 natural-xenon O1 inelastic 2-to-2 reference-spectrum comparison against approximate points digitized from LZ Figure 1; separate from the three-body model and not an exact LZ reproduction.
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
