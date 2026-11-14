# P0 detector response and propagator-width closure: current audit

Date: 2026-11-15
Branch: research/figure2-p0-4-mainline

## Executive status

The final LZ parameter scan remains frozen. Two P0 tracks are active:

- Track A: reconstruct the LZ 2026 NR detector response using the actual high-energy NEST model, beginning with the published Table S5 parameter set.
- Track B: close the independent-coupling and finite-width assumptions in the three-body propagator.

A new machine-readable archive of the LZ 2026 NR mean-yield parameters has been added:
`research/lz_detector_response/lz_2026_extended_nr/lz_2026_nest_nr_mean_yield_parameters.json`.

This is a verified input extraction, not a completed detector-response simulation.

## 1. LZ 2026 NR mean-yield model: verified Table S5 input

Source: LZ Collaboration, arXiv:2609.02823v1, Supplemental Material, Table S5, PDF page 17. The table gives the NEST NR mean light- and charge-yield model parameters.

The NEST parameter vector, in the order used by the current source implementation, is:

```text
NRYieldsParam = {
  11.2, 1.1, 0.052, -0.0533,
  10.8, 0.53, 1.4,
  0.31, 2.5, 0.50,
  1.39, 1.74,
  0.0230, 0.0289, 74.7
}
```

The first twelve entries are the original NR mean-yield parameter vector. The final three entries are the high-energy extension:

- a = 0.0230
- b = 0.0289
- E0 = 74.7 keV

The exponent used in the charge-yield power law is:

[
p(E)=
egin{cases}
0.5, & Ele E_0,\
0.5+aln[1+b(E-E_0)], & E>E_0.
end{cases}
]

The purpose of this modification is to describe the high-energy NR charge-yield suppression revealed by the AmBe calibration, while retaining the low-energy DD-calibrated response. It is essential for the LZ extended-NR region and must not be replaced by the older 12-parameter NEST vector.

The LZ paper states that the NR calibration covers DD recoils at lower energies and AmBe recoils up to about 330 keV. This is the relevant calibration regime for the 5.4--269.9 keV WIMP-search ROI.

## 2. Important NEST version/source pin finding

The LZ paper cites NEST v2.4.5 (2026). The public GitHub release page currently exposes a v2.4.5beta prerelease tag at commit `19bc9bc` dated 2025-12-08.

Inspection of that prerelease source shows that its `GetYieldNR` implementation does not yet contain the 15-parameter high-energy p(E) extension. Therefore the v2.4.5beta tag is not sufficient for reproducing the LZ 2026 Table S5 model.

The NEST source history identifies the exact commit that introduced the high-energy NR charge-yield suppression:

- repository: https://github.com/NESTCollaboration/nest
- commit: `423b9745a5bfbb0402514f1d7955e67445de0810`
- commit date: 2026-08-16 16:33:43 UTC
- commit message: Add energy-dependent NR charge-yield suppression (#210)
- source file: `src/NEST.cpp`
- source blob: `7e19ee148879ae80a982f91652b90c1fc9e10256`

This commit predates the LZ paper submission and contains the 15-parameter branch in `GetYieldNR`, reading a, b, and E0 from vector entries 12, 13, and 14 when the vector length is at least 15. This is a more precise source pin than the later master HEAD.

**Reproducibility rule:** pin this source commit and record its SHA. Do not silently substitute the older v2.4.5beta tag. It is a commit pin, not a claim that the commit is an official tagged v2.4.5 release. If the HEPData package or an official final v2.4.5 release supplies a more precise release commit, compare it and update the pin only after a source-level equivalence check.

## 3. What Table S5 does not provide

Table S5 is the NR **mean yield** model. It is not a complete detector response. The following must remain separate inputs:

1. NR quanta and recombination fluctuation parameters;
2. detector light collection and charge extraction parameters;
3. position-dependent electric-field and optical maps;
4. S1 and S2 single-photon/single-electron response and resolution;
5. trigger, reconstruction, and analysis selections;
6. conditional signal PDFs in {S1c, log10(S2c)};
7. nuisance constraints/covariance.

The public NEST `LZ_WS2024.hh` detector file explicitly describes WS2024/EFT2024 response settings and is not the LZ 2026 extended-NR configuration. Its 2024 parameter vectors must not be reused as if they were the 2026 configuration.

The paper's public NR efficiency curve remains a valuable independent validation target, but it is not a substitute for the conditional two-dimensional response.

## 4. NEST implementation work to perform next

### A1. Mean-yield implementation and verification

- Implement the Table S5 15-parameter vector in a small, isolated response module.
- Port the current NEST `GetYieldNR` equations exactly, including the high-energy p(E) branch, isotope mass scaling, field dependence, density dependence, and the LZ work-function convention.
- Confirm the correct LZ 2026 electric-field, density, molar-mass, and OldW13eV settings from the official release before generating final yield curves.
- Compare the independent implementation against the pinned NEST C++ implementation at a fixed grid of recoil energies and isotope masses.
- Archive photon yield, electron yield, total quanta, and all inputs.

Do not assume the 2024 detector header's 96.5 V/cm field or its OldW13eV setting applies to the 2026 analysis without explicit evidence.

### A2. Fluctuations and detector response

- Identify the NR fluctuation parameter values used by the LZ 2026 simulation from the data release or explicit supplemental information.
- If only the mean-yield vector is available, keep the fluctuation model as a separately labelled approximation; do not call it the complete LZ-tuned NEST response.
- Generate conditional `P(S1c, log10(S2c) | ER, A, detector settings)` distributions.
- Validate the median and width of the NR band against published calibration plots, including the AmBe high-energy region.
- Apply event-selection acceptance exactly once. Keep conditional response and acceptance as separately testable layers.

### A3. Validation gates

1. Mean-yield code agrees with the pinned NEST C++ source to numerical precision.
2. Quanta conservation and physical bounds hold.
3. Repeated-seed Monte Carlo distributions are stable.
4. NR-band median and width agree with the published calibration information within digitization/statistical uncertainties.
5. Integrating the conditional response through the analysis cuts reproduces the published NR efficiency curve within the documented uncertainty.
6. The rate-level efficiency-fold result is reproduced as a cross-check, with no duplicate efficiency factor.

## 5. Independent coupling and finite-width audit

The manuscript's vector-vector Lagrangian is:

[
mathcal L_{mathrm{int}}supset
g_1 V^muarchi_2gamma_muchi_1
+g_2sarchi_2chi_1+mathrm{h.c.}
]

The plotted normalization specifies only ((g_1g_2g_{VN})^2), while the propagator uses a pole width. The product normalization does not determine (g_2) separately, and the width is proportional to (|g_2|^2) under the conditional Dirac scalar-decay calculation.

The manuscript does not explicitly identify (chi_{1,2}) as Dirac or Majorana fields, does not fully specify the scalar's real/complex nature and CP/chiral structure, and does not enumerate all possible (chi_2) decay channels. Consequently, the existing (chi_2	ochi_1s) formula is a conditional Dirac result, not yet a model-independent total width.

### B1. Model-definition closure

- Determine the intended fermion nature from the underlying model/source or author clarification.
- Fix the scalar field and vertex conventions, including hermitian-conjugate/channel counting.
- Enumerate every kinematically open (chi_2) decay channel for each benchmark.
- Derive the total width consistently from those interactions.
- Keep (g_1), (g_2), and (g_{VN}) independent in the numerical input; do not infer (g_2) from the plotted product.

### B2. Propagator/self-energy closure

The source manuscript explicitly uses a constant pole-width denominator:
[
W^2-m_{chi_2}^2+i m_{chi_2}Gamma_{chi_2}.
]

The existing width-sensitivity scan is a diagnostic. It shows that for (m_s=300) keV, (Delta m=1) MeV, (E_R=200) keV, and (v=776) km/s, the constant pole-width prescription changes the reduced kernel by about -1.12% at (g_2=1) and -45.16% at (g_2=3). The diagnostic running-width ansatz gives different results, but is not a full fermionic self-energy calculation.

Next steps:

- derive the appropriate fermion self-energy (Sigma(
ot K)) from the fixed model;
- separate its scalar/vector Dirac structures and real/imaginary parts;
- specify mass and wavefunction renormalization conditions;
- compare the resulting resummed propagator with the manuscript's constant pole-width prescription;
- repeat the W-integral and halo-fold convergence tests after the model definition is fixed.

Do not choose a width scheme because it gives a preferred spectrum.

## 6. Scan freeze and reporting policy

Until Tracks A and B pass their validation gates:

- no final large parameter-space scan;
- no reinterpretation of rate-level yields as a confidence limit;
- no claim that the 248 keV candidate is explained by the model;
- no use of an efficiency-only fold as a full detector-level likelihood;
- retain current rate-level outputs as diagnostics only.

## 7. Current deliverables

- LZ Table S5 parameters: `lz_2026_extended_nr/lz_2026_nest_nr_mean_yield_parameters.json`
- Public input audit: `LZ_2026_PUBLIC_INPUTS_AUDIT.md`
- Existing finite-width audit: `research/figure2_full_reproduction/results/P0-4_PROPAGATOR_WIDTH_AUDIT_ZH.md`
- Conditional two-body width derivation: `research/docs/08_chi2_decay_width.md`

## 8. Sources

- LZ Collaboration, arXiv:2609.02823v1, especially Supplemental Material Table S5 and the detector-response/likelihood sections.
- HEPData data release, DOI: 10.17182/hepdata.182472.v1.
- NESTCollaboration/nest source, pinned commit `30811ea2f8a6de1262eef35278745226dc5d582a`.
- NEST v2.4.5beta prerelease tag `19bc9bc`, retained as a version comparison, not the selected implementation pin.


## 9. Progress update: first independent mean-yield port

The first isolated Python implementation is now committed:

- `lz_2026_extended_nr/lz_2026_nr_mean_yield.py`
- `tests/test_lz_2026_nr_mean_yield.py`
- `.github/workflows/lz-2026-nest-nr-mean-yield.yml`

The implementation ports the 15-parameter mean-yield equations from the pinned NEST source and requires the detector field, density, molar mass, isotope mass number, and OldW13eV flag explicitly. This prevents the 2024 detector settings from being silently inherited.

CI run:
- Run ID: `43626728281`
- Result: success
- Job: `mean-yield-tests`
- Tested: 15-parameter vector, high-energy exponent turn-on, non-negative/additive mean quanta, isotope mass scaling, explicit OldW13eV dependence, and invalid-input handling.

**Validation boundary:** the current tests are unit tests of the independent Python port. They are not yet a cross-language comparison against a compiled NEST executable, and they do not validate the LZ 2026 detector configuration. No final mean-yield curve or S1/S2 PDF is claimed yet.

The field, density, isotope mass scaling convention, and OldW13eV flag must be confirmed against the LZ 2026 HEPData release or collaboration documentation before producing the production response grid.


### Source-history refinement

The first audit pinned the then-current NEST master HEAD. A subsequent history check found the exact earlier commit introducing the LZ high-energy NR suppression:
`423b9745a5bfbb0402514f1d7955e67445de0810` (2026-08-16, commit message “Add energy-dependent NR charge-yield suppression”). The JSON parameter archive has been updated to this commit and its exact source blob. This avoids pinning unrelated later changes while retaining the p(E) code used by the LZ 2026 mean-yield model.
