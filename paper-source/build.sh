#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Verify the current manuscript source and all committed figure assets first.
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

# Normalize the bibliography invocation in a generated copy, preserving the uploaded source.
sed 's/\\bibliography{ref.bib}{}/\\bibliography{ref}/' main.tex > main_build.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname=main_build main_build.tex
bibtex8 main_build
pdflatex -interaction=nonstopmode -halt-on-error -jobname=main_build main_build.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname=main_build main_build.tex
