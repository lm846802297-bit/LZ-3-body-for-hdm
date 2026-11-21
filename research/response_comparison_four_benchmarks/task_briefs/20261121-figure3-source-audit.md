# Review of the supplied Fig. 3 and its absolute three-body event spectrum

**Task ID** 20261121-figure3-source-audit. **Prepared / assigned** 2026-11-21, Codex on the local Windows workstation. **Status** completed source and numerical audit, author-run mismatch open. **Topic** four-benchmark response comparison, natural xenon. **Repository** lm846802297-bit/LZ-3-body-for-hdm. **Baseline** codex/xe89-event-counts at `4541f1ab07ec017bd41924e69870a4124b1b0053`, clean at intake. [Related PR 89](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/89). Remote main inspected at `d2407050ed0f4975387bc6c05bc4509ccf375c31`.

## Question and sources

Do the new source ZIP, compiled manuscript and original figure agree with one another, and where does the first demonstrable disagreement with the event calculation occur? Limit the physical comparison to manuscript Fig. 3 and its radiative benchmark. Assess the blue inelastic curve as an internal shape control. The four other mass scenarios, detector folding, cosmology, and changes to the source manuscript are outside this review.

| Primary input at intake | SHA-256 | Contents used |
|---|---|---|
| Supplied 3body_for_HDM.zip | 658d9a3972e416128d30759d3963efbd417629bb3462092e7ef1c4c06a366f50 | main.tex, figure paths, natural-xenon rate and kinematics |
| Extracted main.tex | a05f68e76bf87a7a3f06c12d47840137dbdf252d046e5c5c4847e31e92ce5a94 | lines 430–504, 631–646, 762–825 |
| Supplied 3body_for_HDM.pdf | 978c35cf0f8a220ffb6f60a18cf4ccd9f1c52221db3b2ed0c3f66ecec21e83fd | Fig. 3 on PDF p. 4, Eqs. (22)–(24) on p. 7 |
| Supplied DM_signal_v2.pdf | ab3e375a2803db8860b9de46fa9a1d66b53bcc1d0e8f00a0a78ab10e1aa0d984 | Axes, mass/coupling labels, red/blue vector paths, lower-panel ratio |
| Repository inputs and earlier results | baseline above | AME2020 nuclear masses, native AFH v6 charge tables, molar/atom fractions, event_counts/output/recoil_curves |

The author’s numerical rate table and the program that produced this specific red line have not been identified at intake. No external source substitutes for the supplied figure.

## Conventions and assumptions

Dirac dark fermions, universal vector coupling and scalar Yukawa interaction. Equal proton and neutron coupling, with the labelled nucleon coupling already including the quark-to-nucleon conversion. The benchmark is `(m1,mV,ms,Delta)=(1000,5,0.000300,0.010) GeV`, `(g1,g2,gVN)=(0.1,1.725,0.04857)`. Same true recoil energy and 2.84 tonne-year exposure at efficiency one for all event comparisons. Project halo test uses rho=0.3 GeV/cm³, v0=220, vesc=544, vlab=232 km/s. The manuscript specifies those speeds in the Xe-131 equal-minimum-speed example. Their use to generate Fig. 3 itself is a hypothesis to test.

Metric (+---), time component first. Nuclear recoil four-momentum is P'-P, t=-2mA ER. Its spatial magnitude is sqrt(2mA ER+ER²). In the leading nonrelativistic kernel use q=sqrt(2mA ER) and R_M(0)=A². The reference full charge calculation averages the initial dark spin, sums final spins, retains the two vector-scalar emission orderings coherently and uses a pole width in the after-scattering propagator. No identical-particle factor. The independent heavy-particle constant-amplitude approximation uses the real leading 1/Delta propagators and the paper's I(D). General gamma-matrix phases and AFH transverse operator phases are immaterial for this check. The nuclear charge input is shared. Nucleon form factors enter the previously archived B, and additional responses enter C/D. The local density and inputs used in the original plotting program remain unconfirmed.

## Independent checks and predeclared criteria

1. Compare the ZIP member byte for byte with the stand-alone figure. Identify its compiled-page drawing by vector paths under the page placement transform (residual <0.01 PDF points). Read labels visually. Audit the two panels and compare old/new red paths after axis calibration. Plot integrals use the displayed log-linear segments. Check against linear-y trapezoids (target 1% for the populated windows). If discrete PDF strokes differ, report the measured difference.
2. Compare red, independently digitized blue and direct lower-panel ratio near 248 keV (target absolute discrepancy <0.05 for the two readings). Recover both exposure-integrated true recoil window totals and compare to the source's approximate one and six. No normalization to these totals. Compare with the frozen static charge, B and D outputs and test the normalization-independent low/high ratio.
3. Solve the exact pair-production threshold using Wmax²=(m1+ms)², with all nine isotope masses. Cross-check with the paper's nonrelativistic formula (target <0.02 km/s at 750 keV). Check whether any isotope can populate a positive high-energy red segment under the specified speed cap. This test uses no matrix element or nuclear structure.
4. Evaluate the independent leading I(D) approximation with its absolute two-body normalization, a numerically angle-integrated shifted Galactic Maxwellian, native charge tables and explicit unit conversions. Compare the windows with the archived exact static-charge result. Check quadrature refinement (target <0.1%) separately from finite-propagator/NR approximations. A shared charge or halo input is not independent evidence of the author's inputs. Reconstructing all six matched nuclear channels, detector response and a full paper plot generator is N/A for this source audit.

## Deliverables and handoff

Store the review program, numerical tables, source fingerprints, plot, run record, and conclusions under `natural_xenon_halo/event_counts/figure3_source_audit/`. Use the three supplied local paths as explicit inputs. Record environment, checks and any failed comparisons after execution. The claim is diagnostic. Proving the origin of a mismatch requires an independently identified source run or a discriminating physical test. Record current archival state separately.

## Change log

2026-11-21, initial task brief. The author supplied a revised source package and original Fig. 3 in this turn.

2026-11-21, added a matched absolute cross-check of Eq. (22) at 180, 248 and 350 keV. A pilot at 248 keV gave a finite rate. Compare the three points using a lab scalar-energy integral, original four-by-four Dirac vertices and independently angle-integrated halo PDF. Target <0.1% relative difference with the archived static-charge curve and <0.01% under quadrature refinement. This extends the check beyond the leading constant-amplitude approximation and still shares the tabulated nuclear response and assumed halo.

2026-11-21, extended the same independent integral to both full recoil windows after the three-point check completed. Predeclared window target: both the refined archived comparison and coarse/fine comparison within 0.01%. Add an independent Poppler pixel-area integration for the newly identified red/blue normalization discrepancy (target 2% agreement for each plotted area).

## Return record

The supplied PDF form stream and source graphic agree byte-for-byte. The 393 plotted red vertices are identical to the previous comparison figure. The revised blue and lower-panel ratio agree at 248 keV, but the revised red / blue area is 1.14743. Pixel extraction independently recovers each integral within 1.7%. All nine target masses together allow 100.8875–702.8930 keV for the adopted 776 km/s cap. Fig. 3 has a positive red trace at 750 keV.

The independent original-vertex Dirac trace and lab-energy integration reproduce the archived static-charge counts at relative residuals −4.03 × 10⁻¹⁰ and −2.88 × 10⁻¹⁰ in the low and candidate windows. The counts remain factors 6.824 and 4.807 below the supplied red line. Point tests, quadrature refinements, threshold roots and unit conversion checks passed the diagnostic tolerances. Validating the particular plotted absolute yield still requires the author's plotting inputs. B and D count values in the comparison are from the frozen archive, and the exact independent recalculation covered the static-charge prescription.

See the [source and calculation audit](../natural_xenon_halo/event_counts/figure3_source_audit/README.md) for input and output hashes, commands, derivations and the complete table. The research record is stored with the PR 89 event-count work. The precise archival revision is the commit that adds this return record, obtainable with `git log -1 --diff-filter=A --format=%H -- research/response_comparison_four_benchmarks/task_briefs/20261121-figure3-source-audit.md`.
