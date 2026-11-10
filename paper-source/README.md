# LaTeX manuscript source

This directory contains both the supplied manuscript source and an editorially cleaned working copy.

## Source files

- `main_original.tex`: byte-for-byte copy of the `main.tex` extracted from the user-supplied `3body_for_HDM.zip`. It is retained unchanged for provenance.
- `main.tex`: editorially cleaned working copy. The edits in this pass are limited to section/placeholder cleanup, figure captions, a spelling correction, appendix organization, and the standard BibTeX database name. No physics formula, coupling definition, numerical input, or figure data has been changed.
- `ref.bib`: original BibTeX database.
- `utphys28mod.bst.gz`: gzip-compressed copy of the original bibliography style file.
- `build.sh`: reproducible build script; it compiles `main.tex` directly with `pdflatex -> bibtex8 -> pdflatex -> pdflatex`.
- `figures/`: the seven original figure PDFs, committed byte-for-byte.
- `SHA256SUMS`: checksums for the original manuscript, cleaned manuscript, bibliography, and figure assets.
- `EDITORIAL_STATUS.md`: items deliberately kept out of the manuscript because they require missing scientific content or independent verification.

## Build

Run:

```bash
./build.sh
```

The script expects the TeX Live packages documented in [docs/07](../docs/07_source_build_and_figure_audit.md). It writes `main_build.pdf` and does not overwrite either source TeX file.

## Preservation policy

The original TeX source and all seven original figure PDFs are retained unchanged. The cleaned `main.tex` is a separate working copy. See `SHA256SUMS` and [ASSET_MANIFEST.md](ASSET_MANIFEST.md) for integrity records.
