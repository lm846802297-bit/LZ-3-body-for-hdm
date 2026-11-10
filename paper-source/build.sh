#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Verify the verbatim manuscript source and all committed figure assets first.
sha256sum --check SHA256SUMS

if [[ ! -f utphys28mod.bst ]]; then
  gzip -dc utphys28mod.bst.gz > utphys28mod.bst
fi

for f in figures/*.pdf; do
  if [[ ! -f "$f" ]]; then
    echo "Missing source figure: $f" >&2
    exit 2
  fi
done

# Build the cleaned working manuscript; main_original.tex is never modified.
pdflatex -interaction=nonstopmode -halt-on-error -jobname=main_build main.tex
bibtex8 main_build
pdflatex -interaction=nonstopmode -halt-on-error -jobname=main_build main.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname=main_build main.tex
