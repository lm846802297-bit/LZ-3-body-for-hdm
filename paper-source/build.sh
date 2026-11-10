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
    exit 2
  fi
done

# Build the cleaned manuscript without modifying either source TeX file.
pdflatex -interaction=nonstopmode -halt-on-error -jobname=main_build main.tex
bibtex8 main_build
pdflatex -interaction=nonstopmode -halt-on-error -jobname=main_build main.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname=main_build main.tex
