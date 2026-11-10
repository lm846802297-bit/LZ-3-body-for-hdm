# Original LaTeX source

This directory contains the paper text sources extracted from the user-supplied \`3body_for_HDM.zip\`.

## Files currently committed

- \`main.tex\`: original RevTeX 4.2 manuscript source.
- \`ref.bib\`: original BibTeX database.
- \`utphys28mod.bst.gz\`: gzip-compressed copy of the original bibliography style file.

Restore the bibliography style with:

\`\`\`bash
gzip -dc utphys28mod.bst.gz > utphys28mod.bst
\`\`\`

## Figure files still needed for a standalone build

The uploaded ZIP contains seven PDFs under \`figures/\`. Their original sizes and SHA-256 hashes are listed in [ASSET_MANIFEST.md](ASSET_MANIFEST.md). Those figure PDFs are not yet committed to this branch. A checkout of the repository therefore still needs the seven original figure files restored into \`figures/\` before LaTeX compilation can complete.

The original uploaded ZIP remains the byte-for-byte source of record in this conversation.

## Build sequence

After restoring the bibliography style and all seven figure PDFs into this directory:

\`\`\`bash
gzip -dc utphys28mod.bst.gz > utphys28mod.bst
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
\`\`\`

The source uses RevTeX 4.2 and the packages declared in the preamble. The local environment used for the initial check had \`pdflatex\` and all required packages, but did not have the \`bibtex\` executable. A first LaTeX pass against the complete source tree produced a five-page PDF, but bibliography resolution and a complete final build have not yet been verified.

## Source status

This is a research draft, not a submission-ready manuscript. The source currently contains an empty Introduction, placeholder text in the direct-detection/relic-abundance/constraints/conclusion/supplement sections, generic or incorrect figure captions, and an unfinished loop-induced \(2\to2\) subsection. Do not silently edit these when reproducing the source.
