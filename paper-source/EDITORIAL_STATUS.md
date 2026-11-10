# Editorial cleanup status

Date: 2026-11-11

This is an editorial and source-organization pass. It does not validate or change the physical amplitudes, propagators, widths, nuclear response, event-rate normalization, confidence-level construction, parameter inputs, or cosmological collision terms.

The supplied TeX file is preserved verbatim as main_original.tex. The working manuscript is main.tex.

## Completed

- Preserved main_original.tex byte-for-byte from the uploaded 3body_for_HDM.zip.
- Corrected the four generic figure captions using only the content visible in the original figures and TeX source.
- Removed internal drafting notes from the direct-detection section and removed placeholder-only sections from the rendered manuscript; unfinished scientific content remains itemized below.
- Restored an Introduction heading with a commented outline and added an empty abstract environment with a commented completion outline. No scientific claims have been invented.
- Retained the only source-listed author, Jia Liu, and the source title 3body-for-HDM as a provisional working title. No affiliation, email, ORCID, or confirmed formal title is present in the supplied TeX, PDF metadata, bibliography, or repository history; none has been invented.
- Added the known title and author to PDF metadata.
- Removed unused float and subfigure packages. In the controlled build, removing float eliminated the duplicate figure.N PDF destinations.
- Reorganized the two diagram images and the two pairs of contour plots into full-width, side-by-side figure* layouts. This resolved the stuck-float warning and makes panel comparisons easier.
- Split two long displayed expressions across aligned lines without changing their algebra.
- Reworded the lead-in to the elastic energy integral to remove an underfull line without changing its meaning.
- Used texorpdfstring for the math subsection heading so hyperref can create a clean PDF bookmark.
- Added SHA-256 verification to build.sh before compilation.

## Figure 2: unresolved mass-label inconsistency

The original DM_signal.pdf visibly labels the four curves as:
- m_s = 200 keV, delta m = 1 MeV;
- m_s = 300 keV, delta m = 1 MeV;
- m_s = 360 MeV, delta m = 1 MeV;
- m_s = 300 MeV, delta m = 10 MeV.

The same plot has an E_R [keV] horizontal axis. The main-text model says the scalar is sub-MeV, and Figs. 3–4 scan m_s over approximately 100–400 keV. Thus the last two legend entries are inconsistent with the stated model and the mass scale in the other plots.

The uploaded source archive contains only main.tex, seven figure PDFs, ref.bib, and utphys28mod.bst; it contains no plotting script, CSV, notebook, or numerical parameter input. The GitHub repository tree and its commit history contain no corresponding plotting/data files. A Library search for the LZ/DM_signal plotting source also did not locate a matching script or dataset. Therefore the discrepancy cannot yet be classified as a wrong plot input, wrong unit conversion, or wrong legend string. The two original legend entries are deliberately left unchanged pending the actual plotting inputs or author confirmation.

## Build and layout audit

The current working source builds through pdflatex -> bibtex8 -> pdflatex -> pdflatex and produces a five-page PDF. The latest local build has:
- no duplicate PDF destinations;
- no stuck-float warning;
- no overfull or underfull hbox warnings;
- no math-token PDF-bookmark warnings;
- all six bibliography citations resolved;
- all seven original vector PDF figures embedded without editing or rasterizing them.

Two non-fatal metadata/package notices remain: REVTeX assumes no affiliation because none is present in the source, and nameref reports that REVTeX has changed the definition of label. Neither is a page-layout or reference-resolution failure. They are retained transparently rather than hidden or patched; the affiliation notice can be resolved only after the author confirms the correct institution.

## Metadata still requiring confirmation

| Field | Evidence in supplied source | Status |
|---|---|---|
| Working title | 3body-for-HDM in TeX and uploaded PDF | Present, but clearly provisional |
| Author | Jia Liu in TeX and uploaded PDF | Present |
| Affiliation | None in TeX or uploaded PDF | Requires author confirmation |
| Email / ORCID | None in supplied source | Requires author confirmation |
| Abstract | Absent in original TeX/PDF | Scaffold only; content pending verified results |
| Introduction | Heading only in original TeX/PDF | Scaffold only; content pending |

## Remaining scientific content

1. Abstract and Introduction prose supported by completed calculations and verified LZ analysis.
2. Loop-induced 2 -> 2 calculation and its relation to the direct-detection signal.
3. Relic-abundance calculation and benchmark definition.
4. Constraints section, including the actual N_eff analysis and other applicable bounds.
5. Conclusions supported by completed results.
6. The scalar–pseudoscalar branch: its corresponding 2 -> 3 amplitude, nuclear response, cross section, and parameter scan.
7. A sourced discussion of the assumption that V remains in equilibrium with the SM through the relevant temperature range, including vector decays to hadrons/mesons where applicable.
8. Complete benchmark table and detector-level LZ treatment (efficiency, energy response, exposure, backgrounds/likelihood, and statistical construction).

## Non-goals

- No amplitude, propagator, width, trace, nuclear response, event-rate integral, cosmological collision term, or numerical scan has been validated in this pass.
- No figure data have been redrawn, rescaled, or relabeled.
- No claim is made that the manuscript is submission-ready or that the model explains the LZ event.
