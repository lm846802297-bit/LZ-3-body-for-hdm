# Original LaTeX source

This directory contains the paper text sources extracted from the user-supplied \`3body_for_HDM.zip\`.

## Files currently committed

- \`main.tex\`: original RevTeX 4.2 manuscript source, preserved byte-for-byte.
- \`ref.bib\`: original BibTeX database, preserved byte-for-byte.
- \`utphys28mod.bst.gz\`: gzip-compressed copy of the original bibliography style file.
- \`build.sh\`: reproducible build script. It creates a temporary \`main_build.tex\` to normalize the bibliography basename without editing \`main.tex\`.
- `figures/`: the seven original figure PDFs, committed byte-for-byte; see [figures/README.md](figures/README.md).
- `SHA256SUMS`: `sha256sum -c` checksums for every file stored verbatim from the original ZIP.

Restore the bibliography style with \`gzip -dc utphys28mod.bst.gz > utphys28mod.bst\`. The seven figure PDFs are already committed under `figures/`, so nothing else needs restoring. Then run:

\`\`\`bash
./build.sh
\`\`\`

The build script uses `pdflatex` and `bibtex8`; the TeX Live packages it needs (`revtex`, `bibtex8`, `textcase`, `cases`, `bbm-macros`, `jknapltx`, `subfigure`, `orcidlink`, `comment`, `epstopdf-pkg`, `float`, `tools`, `graphics`) are listed in [docs/07 §5](../docs/07_source_build_and_figure_audit.md). The exact original source command \`\\bibliography{ref.bib}{}\` makes BibTeX look for \`ref.bib.bib\`; the temporary build copy changes only this command to \`\\bibliography{ref}\`. The original source file remains unchanged.

## Figure assets

The seven figure PDFs are inventoried with their original SHA-256 hashes in [ASSET_MANIFEST.md](ASSET_MANIFEST.md) and are committed byte-for-byte under `figures/`, so a checkout can run the build script directly. Confirm the committed bytes from this directory with `sha256sum -c SHA256SUMS`.

## Source status

This is a research draft, not a submission-ready manuscript. The source currently contains an empty Introduction, placeholder text in the direct-detection/relic-abundance/constraints/conclusion/supplement sections, generic or incorrect figure captions, and an unfinished loop-induced \(2\to2\) subsection. Do not silently edit these when reproducing the source.
