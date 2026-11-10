# Final editorial audit — 2026-11-11

## Figure 2 mass-label trace

The original uploaded archive 3body_for_HDM.zip was re-extracted and inventoried. It contains main.tex, seven PDF figures, ref.bib, and utphys28mod.bst. It contains no Python plotting script, notebook, CSV, JSON, or other numerical parameter input. The GitHub branch tree and its commit history likewise contain no plot source or tabulated inputs. A Library search for the Figure 2/DM_signal plotting source did not locate a matching script or dataset.

The PDF text layer gives the four Figure 2 legend entries: m_s=200 keV, delta m=1 MeV; m_s=300 keV, delta m=1 MeV; m_s=360 MeV, delta m=1 MeV; and m_s=300 MeV, delta m=10 MeV.

The horizontal axis is E_R [keV]; the model text says m_s is sub-MeV; Figs. 3–4 use an m_s [keV] axis spanning approximately 100–400 keV. Thus the last two legend labels are inconsistent with the source's own stated mass scale. There is not enough evidence to determine whether the underlying scan values are in MeV, whether a conversion factor was omitted, or whether only the legend strings are wrong. The figure is unchanged.

## Layout repairs

Controlled local tests showed:
- the unused float package was responsible for duplicate figure.N destinations in the tested RevTeX build; removing it eliminated the duplicate destination warnings;
- the tall stacked figure pairs were responsible for the stuck-float warning; converting each pair to a side-by-side full-width figure* removed it;
- the cross-section prefactor and elastic energy-transfer integral were split over aligned lines, removing both overfull boxes without changing the algebra;
- the prose introducing the unequal-temperature integral was rebalanced, removing the underfull box;
- texorpdfstring was added to the math subsection title, removing hyperref's math-token PDF-string warnings.

The final build has no duplicate PDF destinations, stuck floats, overfull/underfull hboxes, or math-token bookmark warnings. Two non-fatal notices remain and are documented rather than hidden: REVTeX assumes no affiliation because none is present in the supplied source, and nameref reports REVTeX's custom label definition.

## Metadata

The original TeX and uploaded PDF show the title 3body-for-HDM (working title only) and author Jia Liu. No affiliation, email, ORCID, or formal title is present in the uploaded TeX, PDF metadata, bibliography, or repository history. The working source now has an abstract environment and an Introduction heading with comment-only outlines. No affiliation or scientific prose has been invented. PDF metadata carries the known working title and author.

## Reproducibility

The final local build exits successfully after pdflatex -> bibtex8 -> pdflatex -> pdflatex, produces a five-page PDF, resolves all six bibliography citations, embeds all seven original figure PDFs without editing or rasterizing them, and passes all SHA-256 checks in paper-source/SHA256SUMS. The original main_original.tex and all seven figure PDFs remain byte-for-byte unchanged.
