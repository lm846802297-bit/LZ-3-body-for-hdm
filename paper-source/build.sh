#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -f utphys28mod.bst ]]; then
  gzip -dc utphys28mod.bst.gz > utphys28mod.bst
fi

required_figures=(
  figures/DM_signal.pdf
  figures/3_body_contour_ms_deltam_1.pdf
  figures/3_body_contour_ms_deltam_2.pdf
  figures/3_body_contour_ms_coupling_1.pdf
  figures/3_body_contour_ms_coupling_2.pdf
  figures/LZ_3body_DM_signal.pdf
  figures/LZ_3body_DM_signal_2.pdf
)
for f in "${required_figures[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "Missing source figure: $f" >&2
    echo "Restore the figures/ directory from the original 3body_for_HDM.zip." >&2
    exit 2
  fi
done

# Keep main.tex byte-for-byte identical to the supplied source.
# The original \bibliography{ref.bib} is interpreted by BibTeX as ref.bib.bib.
# Build a temporary copy with the conventional database basename instead.
sed 's/\\bibliography{ref\.bib}{}/\\bibliography{ref}/' main.tex > main_build.tex

pdflatex -interaction=nonstopmode -halt-on-error main_build.tex
bibtex8 main_build
pdflatex -interaction=nonstopmode -halt-on-error main_build.tex
pdflatex -interaction=nonstopmode -halt-on-error main_build.tex
