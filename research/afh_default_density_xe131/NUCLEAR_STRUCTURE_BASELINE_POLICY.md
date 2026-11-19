# Nuclear-structure baseline policy for the Xe-131 three-body VV study

**Status:** adopted project convention  
**Effective date:** 2026-11-19  
**Scope:** AFH nuclear responses used in the LZ-3-body-for-hdm three-body VV calculation

## 1. Mainline choice

The mainline nuclear-structure input is the **built-in AFH/DMFormFactor v6.0 default density matrix** for each isotope for which that package supplies a default matrix.

For Xe-131, the adopted input is the 67-entry `sdgXe131` OBDME set in `v6/dmformfactor-V6.m`, selected by

```mathematica
SetIsotope[54,131,"default","default"]
```

The official source-file SHA-256 is:

```text
dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372
```

The currently archived AFH default-density xenon set is **AFH-7**:
`A = 128, 129, 130, 131, 132, 134, 136`. Xe-124 and Xe-126 are not supplied by this AFH v6.0 default dispatch and must not be silently filled with another model while labelling the result AFH-9.

## 2. What “AFH” and “B&D” mean

These labels refer to different layers and must not be used interchangeably:

- **AFH** means the Anand–Fitzpatrick–Haxton nuclear-response formalism and its `DMFormFactor` Mathematica implementation. The package evaluates the multipole responses from supplied one-body density matrix elements (OBDMEs).
- **B&D** means the Baldridge–Dalton shell-model effective interaction used to generate the original xenon OBDMEs underlying the AFH default-density calculations.

The 2024 shell-model comparison paper explicitly identifies the original works of Fitzpatrick et al. and Anand, Fitzpatrick, and Haxton as using the Baldridge–Dalton interaction in the 50–82 major shell. It lists the orbitals as:

`1g7/2, 2d5/2, 2d3/2, 3s1/2, 1h11/2`.

The same paper's xenon discussion confirms that the original calculations [15,16] studied the stable xenon isotopes with B&D, with isotope-dependent valence-space restrictions. The AFH v6.0 package documentation/source then supplies the corresponding default density matrices used by the response routines.

Therefore, the precise description of the adopted input is:

> AFH/DMFormFactor v6.0 response formalism and default OBDMEs, with the underlying original xenon shell-model calculation based on the Baldridge–Dalton (B&D) interaction.

Do **not** describe AFH itself as a nuclear interaction. AFH is the response formalism/package; B&D is the underlying shell-model interaction provenance.

## 3. Mainline calculation rules

1. Use AFH v6.0 default OBDMEs as the sole nuclear-structure input for the AFH mainline.
2. Preserve the AFH source version, density-matrix provenance, oscillator length, isospin convention, and normalization metadata.
3. Do not mix GCN5082 or JJ55-labelled OBDMEs into an AFH response table, isotope sum, or headline prediction.
4. Do not multiply an AFH response by an additional Helm form factor. The finite-size nuclear structure is already encoded in the AFH matrix elements and response.
5. Keep the three-body particle-physics tensor and phase-space integration independent of the nuclear-structure input; combine them only in the explicitly derived response/tensor contraction.
6. Report the present seven-isotope coverage as AFH-7. Do not renormalize the seven isotope abundances to hide the missing AFH-124 and AFH-126 inputs.

## 4. Role of GCN5082 and JJ55

GCN5082 and the archived JJ55-labelled input are **separate nuclear-structure sensitivity alternatives**, not ingredients of the AFH mainline.

- **GCN5082** is a distinct effective shell-model interaction. The 2024 comparison describes it as based on the Bonn-C nucleon-nucleon potential and fitted to low-lying levels in the 50–82 region.
- **JJ55** is a valence-space/model-space label in common usage, not by itself a complete specification of a unique effective Hamiltonian. The exact interaction, truncation, solver, and OBDME provenance for the particular JJ55-labelled data must be stated from its source before it is treated as a fully specified nuclear model.

When these alternatives are shown, they must be labelled as a model-sensitivity comparison. They must not replace, average with, or be blended into the AFH mainline response.

## 5. Rules for model-sensitivity comparisons

A meaningful comparison must hold fixed, or explicitly document differences in:

- isotope and nuclear mass convention;
- exact spatial momentum transfer `q_A` and its mapping from `E_R`;
- response normalization and proton/neutron or isoscalar/isovector convention;
- oscillator length and model-space/truncation choices;
- interpolation method and treatment of diffraction minima;
- three-body phase-space kernel, mediator propagators, width prescription, and particle-physics coefficients.

If a comparison reuses a common `I6` kernel and changes only `R_A(q_A)`, describe it as a **response-only substitution/sensitivity diagnostic**. A relation such as

```text
dσ_alt/dE_R = (dσ_reference/dE_R) × [R_A_alt(q_A) / R_A_reference(q_A)]
```

is conditional on the common-kernel assumption. It is not an independent recalculation of the full three-body amplitude with the alternative nuclear wave functions.

The existing AFH/GCN/JJ55 comparison files remain useful as isolated sensitivity diagnostics. Their numerical values must not be copied into the AFH mainline outputs or described as the primary prediction.

## 6. Recommended manuscript wording

> We evaluate the xenon nuclear responses using the Anand–Fitzpatrick–Haxton (AFH) formalism as implemented in DMFormFactor v6.0, adopting its default one-body density matrix elements for the available xenon isotopes. The underlying xenon shell-model calculations used in the original AFH work employ the Baldridge–Dalton effective interaction in the 50–82 major shell. Alternative GCN5082 and JJ55-labelled nuclear inputs are considered only in separate nuclear-structure sensitivity comparisons and are not mixed into the AFH baseline.

## 7. References

1. A. L. Fitzpatrick, W. Haxton, E. Katz, N. Lubbers, and Y. Xu, *The Effective Field Theory of Dark Matter Direct Detection*, JCAP **02** (2013) 004, [arXiv:1203.3542](https://arxiv.org/abs/1203.3542).
2. N. Anand, A. L. Fitzpatrick, and W. C. Haxton, *Weakly interacting massive particle-nucleus elastic scattering response*, Phys. Rev. C **89**, 065501 (2014), [arXiv:1308.6288](https://arxiv.org/abs/1308.6288).
3. R. Abdel Khaleq, G. Busoni, C. Simenel, and A. E. Stuchbery, *Impact of shell model interactions on nuclear responses to WIMP elastic scattering*, Phys. Rev. D **109**, 075036 (2024), [doi:10.1103/PhysRevD.109.075036](https://doi.org/10.1103/PhysRevD.109.075036). See Sec. III B, Sec. IV B, and Appendix D for the B&D provenance, xenon model space, and relation between the default density matrices and the AFH package.
4. W. J. Baldridge and B. J. Dalton, *Shell-model studies for the ^132Sn region. II. Exact and statistical results for multi-proton cases*, Phys. Rev. C **18**, 539 (1978).
5. J. Menéndez, A. Poves, E. Caurier, and F. Nowacki, Nucl. Phys. A **818**, 139 (2009), the GCN5082 interaction reference cited in Ref. [3].
