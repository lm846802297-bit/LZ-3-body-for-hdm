# Research Task Brief — predicting the revised Fig. 3 red spectrum

**Task ID** 20261121-figure3-red-reproduction. **Prepared and assigned** 2026-11-21, Codex, local Windows. **Status** completed numerical reproduction under two identified sets of assumptions. **Repository** lm846802297-bit/LZ-3-body-for-hdm. **Topic** natural-xenon event counts. **Baseline** codex/xe89-event-counts at b9c9a3dcd702b28017cd6266153e9a218058a4c6 (clean). Remote main d2407050ed0f4975387bc6c05bc4509ccf375c31. [PR 89](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/89).

## Question and scope

Can an absolute calculation predict the supplied revised Fig. 3 red event spectrum, and can the companion blue shape constrain unspecified inputs without calibrating the red signal? Report the Xe-131 cross section at fixed speed and its speed fold at 248 keV. This is a paper reproduction diagnostic using the static nuclear charge in its Eq. (22). The project B result, six-channel current matching, detector efficiencies, and cosmology do not change.

## Pinned sources and known results

| Input | Version and use |
|---|---|
| Supplied 3body_for_HDM.zip, SHA-256 658d9a3972e416128d30759d3963efbd417629bb3462092e7ef1c4c06a366f50 | main.tex a05f68e76bf87a7a3f06c12d47840137dbdf252d046e5c5c4847e31e92ce5a94. Natural-xenon Eq. (12), exact Eqs. (22)–(24), Fig. 3 and mass/coupling labels. |
| Supplied 3body_for_HDM.pdf, 978c35cf0f8a220ffb6f60a18cf4ccd9f1c52221db3b2ed0c3f66ecec21e83fd | page 4, red radiative signal, blue matched inelastic signal |
| Supplied DM_signal_v2.pdf, ab3e375a2803db8860b9de46fa9a1d66b53bcc1d0e8f00a0a78ab10e1aa0d984 | unchanged 393 red vertices, blue shape from upper frame only, unequal plotted absolute areas |
| figure3_source_audit/ at baseline above | Archived vertices, direct Dirac-trace code, reference windows 5.98977633 and 0.97361766 red versus 0.87778716 and 0.20253635 static |
| Mass, isotope and native AFH tables at same commit | AME2020/CODATA2022 nuclear masses, nine atom fractions and seven independent native DMFormFactor-v6 M tables fixed at R(0)=A² |
| [Independent direct-detection halo study](https://arxiv.org/html/2609.02608v2) | Illustrative fixed mean and full-year sinusoidal speed comparison, v0=238, vesc=544, mean vlab=250.2, annual amplitude 14.9 km/s. Does not identify the authors' Fig. 3 halo. |

Original figure-generating notebook, raw isotope spectra and runtime configuration are not in the supplied bundle. Investigate available related archives without assigning the original figure to a different notebook solely by model name.

## Conventions and inputs

Dirac spin-1/2, off-diagonal vector coupling and pure scalar Yukawa interaction, vector mediator used as an effective exchange field at these momenta. No specific gauge completion is required for the stated current. Single open pole decay. Scalar emission before scattering has +i0, after scattering has +i m2 Gamma(pole). Both amplitudes have a common positive coupling product and are summed before squaring. Average over one incoming dark spin doublet and sum final spins. Nuclear response provides its initial spin average. Metric (+---), nuclear transfer P'-P, invariant t=-2mA ER, q_lab²=2mA ER+ER², nuclear response evaluated at q_nuc²=2mA ER in the manuscript convention. g1=0.1, g2=1.725, gVN=0.04857 already a nucleon coupling, masses in GeV (1000, 5, 0.000300, 0.010) for (m1,mV,ms,gap). Equal p/n, cM=1. No nucleon finite-t correction in the paper baseline. E_R is true energy in keV, event density is events/keV at 2.84 tonne-year and efficiency one. Rho=0.3 GeV/cm³ for all absolute comparisons. The freedom to scale the plotted blue two-body curve supplies one nuisance normalization for BLUE ONLY. The absolute red-rate prediction has no fitted vertical scale.

## Discriminating tests and tolerances

1. Predict the red signal with the manuscript-example Galactic-cut SHM (220,544,232 km/s), and with independently specified 238/544/250.2 fixed and annual velocities. For the approximate 800 km/s edge indication, test Galactic cut versus a hard laboratory cut at 800 while keeping v0 and vlab fixed. Atmospheric/detector smearing is outside scope. Hold masses, couplings, native nuclear radii and target normalization fixed.
2. Test whether the blue shape predicts the red under a Galactic-cut SHM and a laboratory-cut boosted Maxwellian. Use a train/held-out energy split of the blue curve, no red ordinates in the objective. Compare AFH-seven, nine-isotope variants using the project's existing Helm prescription where appropriate. Orthogonal model checks may be added with justification. Record identifiability or boundary solutions. Fitted astrophysical parameters are diagnostic, not author-identified. Avoid fitting couplings or nuclear form-factor lengths.
3. Measure shape on a uniform energy grid, separately from support and absolute yield. Predeclared reproduction targets: each of the 100–200 and 215.5–280.5 keV windows within 5% of the graph, integrated absolute error divided by total red yield <5%, 90th percentile of pointwise relative errors <10% on 120–700 keV where the red spectrum exceeds 1e-5 events/keV, and positive support at 750 keV. Tabulate actual residuals even if a gate fails. For holdout inference mark whether the inputs were externally specified or inferred from the companion blue data.
4. Check the absolute Xe-131 dσ/dER at 248 keV versus speed with the lab-energy/Dirac trace and an independent pair-rest-frame integral. Provide a per-isotope table before/after the halo and abundance weighting. Target agreement <0.1% for nonzero cross sections. Refine speed/phase quadrature, check halo normalization, compare direct exact finite-width results to any accelerated evaluation at representative energies and speeds (<0.1% for populated points). Check endpoint support before comparing tails.
5. Archive program, explicit parameters, spectra, intermediate numbers, source hashes and run environment with a publication-readable overlay and data/model ratio. Record primary local execution, numerical and physical status separately. Changes to previously archived scientific data and manuscript are outside scope.

## Unresolved inputs and return

The fitted blue normalization cannot measure the local density or fix the physical normalization of the incoming high-speed tail independently of a model. If a parameterized realization matches the red, distinguish numerical agreement from provenance and uniqueness. Hand back actual tables and residuals, the first unresolved stage and the code/input revisions. Record any failed result and amendments below.

**Return, 2026-11-21.** At 2.84 tonne-year and unit efficiency, published halo parameters with AFH masses and Eq. (22) give 6.12533 / 0.98687 events in the two windows, with integrated absolute discrepancy 1.99%. The blue-only 250.2 km/s profile and the leading contact formula give 5.99901 / 0.97195 and 0.26%. The digitized red graph gives 5.98978 / 0.97362. Both predictions pass the prespecified criteria. The largest whole-window difference against independently integrated kernels is below 0.006%. The source ZIP, standalone figure and compiled paper match the previous input hashes. The original author's run settings remain unknown. The return includes diagnostic failures, different blue block splits and per-isotope fixed-speed and halo results. [Report, figures and numerical records](../natural_xenon_halo/event_counts/figure3_red_reproduction/README.md)

## Change log

2026-11-21. Initial brief before new numerical comparisons.

2026-11-21. The blue held-out test identified the AFH mass prescription as a discriminating input. The upstream v6 implementation sets mN=0.938272 GeV and uses A mN in both reduced mass and recoil momentum (dmformfactor-V6.m lines 1287, 1304, 1405). Extend the comparison to separate its use in the nuclear momentum from its use in kinematics, using fixed discrete masses only. Add the independently published halo (238,544,254) km/s from [arXiv:2609.06153v2](https://arxiv.org/html/2609.06153v2), with all masses/couplings fixed. Compare the manuscript's leading constant-amplitude I(D) prescription (contact and finite mediator) with Eq. (22), including at the previously specified 250.2 km/s blue-only profile. These are hypothesis tests after the initial run. Keep previous results and disclose the selection.
