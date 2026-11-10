# Original LaTeX source

This directory stores the original paper source supplied as \`3body_for_HDM.zip\`.

## Files

- \`main.tex\`: original RevTeX 4.2 manuscript source, preserved without editorial changes.
- \`ref.bib\`: original BibTeX database, preserved without editorial changes.
- \`paper-assets.tar.gz\`: bibliography style \`utphys28mod.bst\` and the seven figure PDFs under \`figures/\`.

The figure PDFs in the asset archive were rewritten with Ghostscript's \`/prepress\` PDF setting to reduce repository size. A 180-dpi rendered comparison was performed against the uploaded PDFs; the visual differences are confined to a very small fraction of pixels and the vector figure content is retained. The original uploaded ZIP remains the byte-for-byte source of record in this conversation.

## Restore and build

From this directory:

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
