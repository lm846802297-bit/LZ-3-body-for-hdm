# Editorial cleanup status

Date: 2026-11-11

## Scope of this pass

This pass cleans the manuscript presentation only. It does not supply missing scientific analysis and does not modify the displayed interaction terms, amplitudes, cross-section formulae, phase-space limits, cosmological equations, numerical inputs, or figure data.

The exact supplied TeX source is preserved as `main_original.tex`. The cleaned working manuscript is `main.tex`.

## Changes made

- Removed the empty Introduction heading rather than leaving a blank section.
- Removed internal drafting notes from the direct-detection section.
- Replaced the four generic figure captions using only the content and parameter labels visible in the corresponding figures and manuscript text.
- Corrected the spelling of “heaver” to “heavier”.
- Removed empty or placeholder-only manuscript sections/subsections from the rendered manuscript: loop-induced `2 -> 2`, relic abundance, constraints, conclusion, and the generic supplement heading.
- Promoted the existing post-freeze-out evolution material to Appendix A.
- Removed the inline reminder about adding a reference for vector decays into mesons; the reminder is recorded below.
- Standardized the BibTeX database command to `\\bibliography{ref}`.
- Retained the original manuscript verbatim as `main_original.tex`.

## Outstanding manuscript content

The following items are not completed by this editorial pass and must not be represented as completed results:

1. Abstract and Introduction.
2. Loop-induced `2 -> 2` calculation and its relation to the direct-detection signal.
3. Relic-abundance calculation and benchmark definition.
4. Constraints section, including the actual `N_{\\rm eff}` analysis and other applicable bounds.
5. Conclusions supported by completed results.
6. The scalar–pseudoscalar branch: the source currently gives its interaction ansatz but does not provide its corresponding `2 -> 3` amplitude, nuclear response, cross section, or parameter scan.
7. A sourced discussion of the assumption that `V` remains in equilibrium with the SM through the relevant temperature range, including vector decays to hadrons/mesons where applicable.
8. Complete benchmark table and detector-level LZ treatment (efficiency, energy response, exposure, backgrounds/likelihood, and statistical construction).

## Figure-specific follow-up items

- Figure 2 is an event-rate spectrum versus `E_R`, not a Feynman-diagram figure. Its legend appears to list two scalar masses as “300 MeV” and “360 MeV”, while the vertical axis is in keV and the model text describes a sub-MeV scalar. This possible unit/label inconsistency is deliberately not corrected here; it requires checking the plotting input or original analysis.
- Figures 3 and 4 show confidence-level contours. The captions identify their axes and panel benchmarks without asserting what the numerical contour statistic represents. The statistical definition and construction of the quoted confidence levels still require verification.

## Non-goals

- No amplitude, propagator, width, trace, nuclear response, event-rate integral, cosmological collision term, or numerical scan has been validated in this pass.
- No plot has been redrawn, rescaled, or edited.
- No claim is made that the manuscript is submission-ready.
