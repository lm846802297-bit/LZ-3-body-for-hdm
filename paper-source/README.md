# LaTeX manuscript source

This directory contains the current uploaded manuscript and its assets.

## Source files

- **Current authority:** use `main.tex` for current manuscript equations and citations.

- `main.tex`: unmodified manuscript source from the ZIP uploaded on 2026-11-19.
- `ref.bib`: current uploaded bibliography database.
- `utphys28mod.bst.gz`: compressed copy of the original bibliography style file.
- `build.sh`: verifies SHA-256 hashes, then compiles with `pdflatex -> bibtex8 -> pdflatex -> pdflatex`.
- `figures/`: the original figures, fixed-speed recoil spectra, and the new DM_signal_v2.pdf and ratio_supp.pdf.
- `SHA256SUMS`: checksums for the current manuscript and bibliography, bibliography style, and all eleven figure PDFs.
- `ASSET_MANIFEST.md`: original asset inventory and hashes plus the 2026-11-17 manuscript update inventory.
- `EDITORIAL_STATUS.md`: editorial history, unresolved source-data issue, and current update diagnostics.
- The AFH-7/Hybrid-9 one-dimensional LZ rate-level fold and its reproducible outputs are indexed in `research/lz_detector_response/README.md`; they are not a full detector-level likelihood.

## 2026-11-19 upload

The current main.tex and ref.bib are byte-identical to the uploaded ZIP. The ZIP adds figures/DM_signal_v2.pdf and figures/ratio_supp.pdf. Asset checksums pass. A build attempt reached BibTeX, which reported four missing bibliography keys: Su:2026rwz, Fan:2026kxx, Freese:2026sga, and PDG:2024kinematics. The generated PDF is an incomplete first pass.

## Build

Run `./build.sh`. The script writes `main_build.pdf` and does not overwrite `main.tex`. It first verifies every entry in `SHA256SUMS`. The 2026-11-19 uploaded source uses a bibliography command that is normalized only in the generated build copy. A full PDF build still requires a TeX installation with the `pdflatex.fmt` format; see `EDITORIAL_STATUS.md`.

## Preservation policy

The seven original figure PDFs are retained unchanged. Figure 2's two inconsistent mass labels are intentionally not corrected because the plotting script and numerical inputs are absent. See `EDITORIAL_STATUS.md` for the evidence and unresolved questions.
