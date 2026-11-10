# Original LaTeX source

This directory contains the paper source extracted from the user-supplied \`3body_for_HDM.zip\`.

## Files

- \`main.tex\`: original RevTeX 4.2 manuscript source.
- \`ref.bib\`: original BibTeX database.
- \`paper-assets.tar.gz\`: \`utphys28mod.bst\` and the seven figure PDFs under \`figures/\`.

The \`main.tex\` and \`ref.bib\` files are preserved as supplied. The seven figure PDFs in \`paper-assets.tar.gz\` were re-serialized with Ghostscript's \`/prepress\` PDF setting to reduce repository size. A 180-dpi rendered comparison was performed against the uploaded PDFs; the vector content and visual appearance are retained to plotting precision. Original and stored SHA-256 values are recorded in [ASSET_MANIFEST.md](ASSET_MANIFEST.md). The original uploaded ZIP remains the byte-for-byte source of record in this conversation.

## Restore and build

From this directory, extract the bibliography style and figure files:

\`\`\`bash
tar -xzf paper-assets.tar.gz
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
\`\`\`

The source uses RevTeX 4.2 and the packages declared in the preamble. The local environment used for the initial check had \`pdflatex\` and all required packages, but did not have the \`bibtex\` executable. Therefore the first LaTeX pass produced a five-page PDF, but bibliography resolution and a complete final build have not yet been verified.

## Source status

This is a research draft, not a submission-ready manuscript. The source currently contains an empty Introduction, placeholder text in the direct-detection/relic-abundance/constraints/conclusion/supplement sections, generic or incorrect figure captions, and an unfinished loop-induced \(2\to2\) subsection. Do not silently edit these when reproducing the source.
