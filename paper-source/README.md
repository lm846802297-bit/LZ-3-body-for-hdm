# LaTeX manuscript source

This directory contains the current uploaded manuscript and its assets.

## Source files

- **Current authority:** use `main.tex` for current manuscript equations and citations.

- `main.tex`: current uploaded manuscript source. Its BibTeX database invocation is normalized to `\\bibliography{ref}` so BibTeX reads `ref.bib` correctly. No physics content was changed in this submission pass.
- `ref.bib`: current uploaded bibliography database.
- `utphys28mod.bst.gz`: compressed copy of the original bibliography style file.
- `build.sh`: verifies SHA-256 hashes, then compiles with `pdflatex -> bibtex8 -> pdflatex -> pdflatex`.
- `figures/`: the seven original figure PDFs plus two newly uploaded fixed-speed recoil spectra.
- `SHA256SUMS`: checksums for the current manuscript and bibliography, bibliography style, and all nine figure PDFs.
- `ASSET_MANIFEST.md`: original asset inventory and hashes plus the 2026-11-17 manuscript update inventory.
- `EDITORIAL_STATUS.md`: editorial history, unresolved source-data issue, and current update diagnostics.
- The AFH-7/Hybrid-9 one-dimensional LZ rate-level fold and its reproducible outputs are indexed in `research/lz_detector_response/README.md`; they are not a full detector-level likelihood.

## Build

Run `./build.sh`. The script writes `main_build.pdf` and does not overwrite `main.tex`. It first verifies every entry in `SHA256SUMS`. The 2026-11-17 update includes a resolved PDG kinematics citation and unique equation labels. A full PDF build still requires a TeX installation with the `pdflatex.fmt` format; see `EDITORIAL_STATUS.md`.

## Preservation policy

The seven original figure PDFs are retained unchanged. Figure 2's two inconsistent mass labels are intentionally not corrected because the plotting script and numerical inputs are absent. See `EDITORIAL_STATUS.md` for the evidence and unresolved questions.
