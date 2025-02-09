#!/bin/bash

# Prüfe, ob ein Dateiname als Argument übergeben wurde
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <filename>"
  exit 1
fi

# Dateiname ohne Erweiterung
TEX_FILE="$1"

# Schritt 1: Erste Kompilation mit XeLaTeX
echo "Running XeLaTeX (1st pass)..."
xelatex -interaction=nonstopmode "$TEX_FILE.tex" || exit 1

# Schritt 2: BibTeX ausführen
echo "Running BibTeX..."
bibtex "$TEX_FILE" || exit 1

# Schritt 3: Zweite Kompilation mit XeLaTeX
echo "Running XeLaTeX (2nd pass)..."
xelatex -interaction=nonstopmode "$TEX_FILE.tex" || exit 1

# Schritt 4: Dritte Kompilation mit XeLaTeX (für Referenzen und Layout)
echo "Running XeLaTeX (3rd pass)..."
xelatex -interaction=nonstopmode "$TEX_FILE.tex" || exit 1

echo "Postprocessing completed. Output file: $TEX_FILE.pdf"
