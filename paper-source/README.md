# LaTeX manuscript source

This directory contains the verbatim supplied source and an editorially cleaned working copy.

## Source files

- main_original.tex: byte-for-byte copy of the TeX source extracted from 3body_for_HDM.zip; retained unchanged for provenance.
- main.tex: editorially cleaned working copy. This pass changes captions, layout, section scaffolding, PDF metadata, and line breaking only. No physical formula, coupling definition, numerical input, or figure data has been changed.
- ref.bib: original BibTeX database.
- utphys28mod.bst.gz: compressed copy of the original bibliography style file.
- build.sh: verifies SHA-256 hashes, then compiles with pdflatex -> bibtex8 -> pdflatex -> pdflatex.
- figures/: the seven original figure PDFs, committed byte-for-byte.
- SHA256SUMS: checksums for the original manuscript, cleaned manuscript, bibliography, and figure assets.
- ASSET_MANIFEST.md: original asset inventory and hashes.
- EDITORIAL_STATUS.md: completed editorial changes, unresolved source-data issue, and remaining scientific content.

## Build

Run ./build.sh. The script writes main_build.pdf and does not overwrite either source TeX file. It first verifies every entry in SHA256SUMS.

## Preservation policy

The original TeX source and all seven original figure PDFs are retained unchanged. Figure 2's two inconsistent mass labels are intentionally not corrected because the plotting script and numerical inputs are absent. See EDITORIAL_STATUS.md for the evidence and unresolved questions.
