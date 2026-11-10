# Original LaTeX source

This directory contains the paper text sources extracted from the user-supplied \`3body_for_HDM.zip\`.

## Files currently committed

- \`main.tex\`: original RevTeX 4.2 manuscript source, preserved byte-for-byte.
- \`ref.bib\`: original BibTeX database, preserved byte-for-byte.
- \`utphys28mod.bst.gz\`: gzip-compressed copy of the original bibliography style file.
- \`build.sh\`: reproducible build script. It creates a temporary \`main_build.tex\` to normalize the bibliography basename without editing \`main.tex\`.

Restore the bibliography style with \`gzip -dc utphys28mod.bst.gz > utphys28mod.bst\`. Then restore the seven figure PDFs listed in [figures/README.md](figures/README.md) from the original ZIP and run:

\`\`\`bash
./build.sh
\`\`\`

The build script uses \`pdflatex\` and \`bibtex8\`. The exact original source command \`\\bibliography{ref.bib}{}\` makes BibTeX look for \`ref.bib.bib\`; the temporary build copy changes only this command to \`\\bibliography{ref}\`. The original source file remains unchanged.

## Figure assets

The seven figure PDFs are inventoried with their original SHA-256 hashes in [ASSET_MANIFEST.md](ASSET_MANIFEST.md). Their binary files are not yet committed to this branch, so a checkout still needs the original \`figures/\` directory restored before the build script can run.

## Source status

This is a research draft, not a submission-ready manuscript. The source currently contains an empty Introduction, placeholder text in the direct-detection/relic-abundance/constraints/conclusion/supplement sections, generic or incorrect figure captions, and an unfinished loop-induced \(2\to2\) subsection. Do not silently edit these when reproducing the source.
