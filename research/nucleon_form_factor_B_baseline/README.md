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

The primary (G_E^{p,n}), (G_M^{p,n}) input is the low-(Q^2) z-expansion of Borah, Hill, Lee and Tomalak, Phys. Rev. D 102, 074012 (2020), arXiv:2003.13640. It is optimized for (Q^2lesssim) a few GeV(^2), includes the proton and neutron data/radius constraints, and supplies the free-coefficient covariance matrices.

The exact central coefficients and covariance matrix are pinned under `data/ye2020/`. The source copy is the GENIE-MC/Generator distribution of the Ye et al. supplemental data:
- `config/ZExpELFormFactorModel.xml`
- `data/covariances/FormFactor/Vector/ELZExpFF.dat`
- pinned source commit: `e2e04f19e96d395ac646cf3382841646b60fa1b4`

The four free coefficients for each Sachs form factor are completed by (G(0)) normalization and the four (Q^4) asymptotic sum rules, matching GENIE's `Q4limit` implementation. The full (G_E,G_M) are converted to (F_1,F_2) with
[
F_1=rac{G_E+	au G_M}{1+	au},qquad
F_2=rac{G_M-G_E}{1+	au},qquad 	au=Q^2/(4m_N^2).
]

## Strange-current input

Two separately labelled strange-current scenarios are implemented. Their current conventions are not interchangeable; see `strange_current_convention_audit.md`.

1. `sufian2017_unit_current` (primary): directly uses the unit-current matrix element (ar sgamma^mu s), with (G_M^s(0)=-0.064) and (langle r_E^2angle_s=-0.0043,mathrm{fm}^2). The magnetic form factor is frozen at its quoted zero-momentum value because this source does not provide a magnetic radius in the cited result.
2. `alexandrou2020_charge_weighted_converted` (alternative): uses the published 2020 (e_sar sgamma^mu s) form factors after dividing the reported Sachs functions and slopes by (e_s=-1/3), as required to convert to a unit-current matrix element. The published magnetic and electric radii are used in a first-order low-(Q^2) expansion.

The two scenarios are both calculated and retained; they are not averaged.

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

The Ye2020 proton/neutron coefficient covariance is propagated with correlated Monte Carlo draws across the complete (Q_A^2) grid. The strange-current scenario uncertainty is kept separate from the Ye2020 electromagnetic fit covariance.

## Scope

This is the rate-level B baseline. It includes the finite nucleon (F_1,F_2) and AFH finite-size (W_M) response. It does not yet include additional AFH responses, detector efficiency, energy resolution, exposure, analysis cuts or likelihood.
