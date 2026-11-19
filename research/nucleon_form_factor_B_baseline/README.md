# B baseline: finite nucleon form factors × finite-size AFH charge response

## Definition

This stage implements the previously selected B baseline:

[
F_1(t_N),quad F_2(t_N),quad W_M(y_A),
]

with the nucleon form factors and nuclear response kept as separate physical ingredients.

For each isotope and recoil energy,

[
Q_A^2=|mathbf q_A|^2=2m_AE_R+E_R^2,qquad t_N=-Q_A^2.
]

The quark-flavor sum for universal (u,d,s) vector coupling is reconstructed as

[
F_i^{uds,N}(t_N)=3left[
F_i^{mathrm{EM},p}(t_N)+F_i^{mathrm{EM},n}(t_N)+F_i^{s,N}(t_N)
ight],
]

where (F_i^{s,N}) is the matrix element of the unit strange current (ar sgamma^mu s). The corresponding charge-like NR coefficient is

[
c_M(t_N)=F_1^{uds,N}(t_N)
+rac{t_N}{8m_N^2}left[F_1^{uds,N}(t_N)+2F_2^{uds,N}(t_N)ight].
]

The pointlike equal-(u,d,s) normalization is (c_M(0)=3), so define

[
F_M(t_N)=c_M(t_N)/3,qquad
mathcal C_N(Q_A^2)=|F_M(t_N)|^2.
]

The postprocessor multiplies each isotope's already-computed full and (I(D)) rate contribution by (mathcal C_N(Q_A^2)), then re-sums the seven AFH isotopes. This leaves the AFH finite-size (W_M(y_A)) response intact; it does not replace it with a point-nucleus response.

## Electromagnetic proton/neutron input

The primary (G_E^{p,n}), (G_M^{p,n}) input is the low-(Q^2) z-expansion of Borah, Hill, Lee and Tomalak, Phys. Rev. D 102, 074012 (2020), arXiv:2003.13640. It is optimized for (Q^2lesssim) a few GeV(^2), includes the proton and neutron data/radius constraints, and supplies the free-coefficient covariance matrices. The fit is the separate proton/neutron default fit (not the isospin-combined fit).

The exact central coefficients and covariance matrix are pinned under `data/borah2020/`. The source copy is the GENIE-MC/Generator distribution of the Borah et al. supplemental data:
- `config/ZExpELFormFactorModel.xml`
- `data/covariances/FormFactor/Vector/ELZExpFF.dat`
- pinned source commit: `e2e04f19e96d395ac646cf3382841646b60fa1b4`

The four free coefficients for each Sachs form factor are completed by (G(0)) normalization and the four (Q^4) asymptotic sum rules, matching GENIE's `Q4limit` implementation. The magnetic coefficients stored in the source are already multiplied by the corresponding magnetic moment, so the code treats them as coefficients of the unnormalized (G_M) expansion. The full (G_E,G_M) are converted to (F_1,F_2) with
[
F_1=rac{G_E+	au G_M}{1+	au},qquad
F_2=rac{G_M-G_E}{1+	au},qquad 	au=Q^2/(4m_N^2).
]

## Strange-current input

Three separately labelled strange-current scenarios are implemented. Their current conventions are not interchangeable; see `strange_current_convention_audit.md`.

1. `sufian2017_unit_current` (historical primary benchmark): directly uses the unit-current matrix element \(\bar s\gamma^\mu s\), with \(G_M^s(0)=-0.064\) and \(\langle r_E^2\rangle_s=-0.0043\,\mathrm{fm}^2\). The magnetic form factor is frozen at its quoted zero-momentum value because the cited physical-point result does not provide a magnetic radius.
2. `alexandrou2020_charge_weighted_converted`: uses the published 2020 \(e_s\bar s\gamma^\mu s\) form factors after dividing the reported Sachs functions by \(e_s=-1/3\), as required to convert to a unit-current matrix element. The electric and magnetic radii are used in a first-order low-\(Q^2\) expansion. The magnetic expansion includes its normalization \(G_M^s(0)=\mu_s\).
3. `alexandrou2026_continuum_unit_current`: uses the newer continuum-limit physical-point results from arXiv:2603.26600. The paper states that the strange electric charge factor is not included in the reported results, so these values already use the unit-current convention. This scenario is implemented using the published electric and magnetic slopes; it is explicitly a slope-only low-\(Q^2\) representation, not a reconstruction of the full fitted z-expansion.

All three scenarios are calculated and retained separately; they are not averaged. The Sufian set remains the frozen historical benchmark, while the 2026 result is included as an updated continuum-lattice cross-check. The 2026 source uncertainties are recorded in metadata but are not yet sampled.

## Applying B to a halo/isotope artifact

The input is the isotope-level CSV from the halo workflow. No phase-space integral is rerun.

```bash
python research/nucleon_form_factor_B_baseline/apply_nucleon_form_factors_B.py \
  --input-dir path/to/halo-seven-isotope-highorder \
  --out-dir results/nucleon-form-factor-B \
  --draws 3000
```

Outputs per strange-current scenario:
- `seven_isotope_B_baseline.csv`
- `natural_xenon_B_baseline.csv`
- `metadata.json`

The Borah2020 proton/neutron coefficient covariance is propagated with correlated Monte Carlo draws across the complete (Q_A^2) grid. Strange-current central-value scenarios are kept separate from the electromagnetic fit covariance; the source uncertainties for the 2026 scenario are recorded but not yet sampled.

## Scope

This is the rate-level B baseline. It includes the finite nucleon (F_1,F_2) and AFH finite-size (W_M) response. It does not yet include additional AFH responses, detector efficiency, energy resolution, exposure, analysis cuts or likelihood.
