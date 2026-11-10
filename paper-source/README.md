# Original LaTeX source

This directory contains the original paper text sources extracted from the user-supplied \`3body_for_HDM.zip\`.

## Files currently committed

- \`main.tex\`: original RevTeX 4.2 manuscript source.
- \`ref.bib\`: original BibTeX database.

Both text files were checked against the uploaded archive; their byte lengths match the source files.

## Source assets still to be added

The uploaded ZIP also contains:
- \`utphys28mod.bst\`: bibliography style;
- seven PDFs under \`figures/\`.

These binary assets are inventoried with SHA-256 hashes in [ASSET_MANIFEST.md](ASSET_MANIFEST.md), but are not yet committed as individual files in this branch. The original uploaded ZIP remains the complete source package in this conversation. A checkout of this repository alone is therefore not yet sufficient to compile the manuscript until those assets are added.

## Build sequence

After restoring the missing style and figure files into this directory:

\`\`\`bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
\`\`\`

The source uses RevTeX 4.2 and the packages declared in the preamble. The local environment used for the initial check had \`pdflatex\` and all required packages, but did not have the \`bibtex\` executable. The first LaTeX pass produced a five-page PDF, but bibliography resolution and a complete final build have not yet been verified.

## Source status

This is a research draft, not a submission-ready manuscript. The source currently contains an empty Introduction, placeholder text in the direct-detection/relic-abundance/constraints/conclusion/supplement sections, generic or incorrect figure captions, and an unfinished loop-induced \(2\to2\) subsection. Do not silently edit these when reproducing the source.
