# Research documentation

## Main report

- [AFH v6.0 Xe-131 response, Eq. (6) three-body scattering, natural xenon, and LZ rate-level interface](09_afh_xe131_three_body_scattering_natural_xenon.md): current main report. Its main text now walks through the interaction and virtual-state picture, the two-diagram Dirac amplitude and interference, three-body phase space and Eq. (6) prefactor, nuclear-response minima, isotope/halo folding, and the detector-efficiency projection; full technical derivations remain in formal Appendices A–I; Appendix H is the full Eq. (6) cross-section audit record embedded in the main report, and Appendix I covers the full VV nucleon-current matching and AFH non-\(M\) response status.
- [Formula–symbol–text–code–result cross-reference](formula_symbol_code_cross_reference.md): stable F1–F13 identifiers, definitions, units, approximations, code entry points, archived outputs, and validation boundaries.
- [Research decision register](supplements/research_decision_register.md): discussion candidates, adopted conventions, and scope boundaries. This is a supplementary decision register, not a numbered main-report appendix.

## Current audit and status registers

- [Current Figure 2 results master index](supplements/three_body_results_master_index_2026-11-16.md): current main result map after PR #45: 13 groups, 91 committed SHA-256/size records plus one external high-order archive checksum (92 output records), including the full AFH-7 response grid and AFH-7/Hybrid-9 84-point spectra.
- [Current machine-readable result manifest](supplements/three_body_results_master_index_2026-11-16.json): source commit, parameters, repository paths, SHA-256 digests, byte sizes, and explicit external-archive boundaries.
- [Historical Figure 2 results index (2026-11-13)](supplements/three_body_results_master_index_2026-11-13.md): retained as the earlier nine-group/60-file snapshot.
- [Physics formula cross-audit](supplements/three_body_physics_formula_audit_2026-11-13.md): original Lagrangian, two radiation diagrams, Dirac trace, three-body phase-space Jacobian, \(256\pi^3\), AFH factor four, \(v_{\min}\), and natural-xenon rate normalization.
- [P1-PhaseSpace numerical convergence audit](supplements/phase_space_convergence_audit_2026-11-14.md): independent (W^2/W/u^2) mappings, threshold-stable Källén evaluation, angular quadrature and raw-(d\Phi_3) prefactor checks. A 2026-11-16 addendum records the AFH-7/Hybrid-9 84-point threshold-(u^2) grid and high-order convergence. GCN/JJ55 remain on the legacy linear-(W^2) path and need a matched rerun; near-pole width-scheme systematics remain open.
- [Scientific result status table](supplements/three_body_scientific_status_2026-11-13.md): current 2026-11-18 status update, separating verified, partially verified, missing-input, and not-yet-completed tasks.
- [Scientific content audit — Phase 1](supplements/scientific_content_audit_2026-11-16.md): AFH-7 full-grid status, old/new kernel comparison, GCN/JJ55 quadrature mismatch, and remaining validation boundaries.
- [Anand / AFH coherent-response audit](../three_body_calculation_and_validation/ANAND_WM_RESPONSE_AUDIT.md): source-level AFH isoscalar convention and the physical equal-\(p,n\) response mapping.
- [三体 VV 核子流与 AFH 核响应——唯一主讨论档案](../afh_isotope_response_equivalence/docs/QUARK_TO_NUCLEON_VECTOR_CURRENT_MATCHING.md)：保留原始讨论与 A–P 校订，集中维护 §§27–44 的推导、响应数据库框架、数值验收规范，以及 P 节中已经归档的 AFH 核响应 benchmark。
- [AFH 方法背景与三体散射推广说明](../afh_isotope_response_equivalence/docs/AFH_METHOD_BACKGROUND_AND_THREE_BODY_GENERALIZATION.md)：独立介绍 AFH 核响应方法、相关三体辐射文献先例，以及本项目标量辐射模型需要重新推导的三体张量和响应系数；作为唯一主讨论档案的配套背景文档，不替代原档案。

## Earlier project notes

- 01_model_and_amplitude.md: model definition, three-body amplitude, and propagator structure.
- 02_lz_recast.md: LZ data, detector response, and statistical-recast plan.
- 03_cosmology.md: freeze-out and Delta N_eff.
- 04_audit_and_roadmap.md: open issues, validation status, and research roadmap.
- 05_references.md: reference bibliography and source mapping.
- 06_original_source_audit.md: audit of the supplied manuscript source.
- 07_source_build_and_figure_audit.md: source build and figure audit.
- 08_chi2_decay_width.md: analytic derivation, benchmark, and validation boundary for chi2 -> chi1 s.
- 08_final_editorial_pass_2026-11-11.md: historical editorial pass record.

## Formal Appendices A–I

The standalone files below are navigation/citation copies of the corresponding sections embedded in the main report. When editing an appendix, update both copies in the same change and verify that their scientific content remains synchronized.

- [A — Three-body kinematics, phase-space limits, and Dirac amplitude](appendices/09A_three_body_kinematics_amplitude.md)
- [B — AFH v6.0 density matrix and nuclear response](appendices/09B_afh_v6_density_matrix_response.md)
- [C — AFH isoscalar normalization and factor-of-four mapping](appendices/09C_afh_isoscalar_factor4_normalization.md)
- [D — Natural-xenon isotopes, abundances, and target normalization](appendices/09D_natural_xenon_isotope_target.md)
- [E — Laboratory-frame halo, three-body minimum speed, and rate folding](appendices/09E_halo_velocity_vmin_folding.md)
- [F — Numerical validation, archived data, and reproduction commands](appendices/09F_numerical_validation_reproduction.md)
- [G — Exact spatial momentum and the non-relativistic recoil approximation](appendices/09G_recoil_momentum_convention_audit.md)
- H — Full Eq. (6) (d\sigma_A/dE_R) Mathematica–Python audit, embedded in §13 of the [main report](09_afh_xe131_three_body_scattering_natural_xenon.md); this does not yet have a separate standalone copy.
- [I — Three-body VV nucleon current, Dirac–Pauli matching, and non-M AFH responses](appendices/09I_three_body_vv_nucleon_current_afh_responses.md): formal derivation and status boundary for (F_1/F_2), (Phi''), (MPhi''), (Delta), (Sigma'), and the full tensor contraction.

## 450 keV benchmark records

These are deliberately separate diagnostics with different assumptions; neither should be conflated with the natural-xenon halo-folded spectra or the LZ rate-level yields.

- [Supplied pointwise L00 benchmark and conditional pole-width comparison](../three_body_calculation_and_validation/results/USER_L00_BENCHMARK_G1_G2_GVN_1_DELTA_M_450KEV.md)
- [Local acceptance record for the pointwise benchmark](../three_body_calculation_and_validation/results/USER_L00_BENCHMARK_450KEV_LOCAL_2026-11-13/LOCAL_VALIDATION_2026-11-13.md)
- [Fixed-speed Xe-131 differential curve and its limitations](../three_body_calculation_and_validation/results/USER_DSIGMA_CURVE_450KEV_LOCAL_2026-11-13.md)

## LZ detector-response documentation

- [Detector-response inputs and rate-level archive README](../lz_detector_response/README.md)
- Main report: §11.1–§11.5; numerical interface and remaining requirements: Appendix F.5.


## Phase II high-energy tail sensitivity

- [High-energy tail nuclear-model sensitivity](appendices/09H_high_energy_tail_nuclear_model_sensitivity.md): AFH-7/Hybrid-9/Helm-9/GCN/JJ55 comparison in the 225–269.9 keV efficiency-weighted candidate window. This is a one-dimensional rate-level audit, not an LZ likelihood.
- [AFH missing-isotope coverage](appendices/09H_afh_natural_xenon_missing_isotopes.md): official AFH v6.0 Xe-124/Xe-126 input gap and explicitly labelled fallback scenarios.

**Naming note:** the two standalone `09H_*.md` files above are historical topical supplements. They are not the main report's formal Appendix H, which is the full Eq. (6) audit in §13.
- [LZ 2026 AFH-7/Hybrid-9 figure pack](../figure_packs/lz_2026_afh7_hybrid9/README.md): figure atlas, source metadata, manifest and checksums.

## Figure 2 audit supplements

- [Numerical-results master index](supplements/three_body_results_master_index_2026-11-16.md)
- [Physics-formula cross-audit](supplements/three_body_physics_formula_audit_2026-11-13.md)
- [Scientific-status table](supplements/three_body_scientific_status_2026-11-13.md)
- [Scientific content audit — Phase 1](supplements/scientific_content_audit_2026-11-16.md)

## Related full-current audit

- [PR #53 — four-component three-body DM tensor and coherent point-charge-current diagnostic](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/53). This branch-level result does not include internal nuclear currents or AFH non-(M) response matching.
