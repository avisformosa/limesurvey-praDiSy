#!/bin/bash

# Name der .tex-Datei (ersetze 'diagnostik' durch den Namen deiner Quarto-Datei ohne Erweiterung)
TEX_FILE="diagnostik"

# 1. Schritt: Erste Kompilation mit XeLaTeX
xelatex $TEX_FILE.tex

# 2. Schritt: BibTeX ausführen
bibtex $TEX_FILE

# 3. Schritt: Zweite Kompilation mit XeLaTeX
xelatex $TEX_FILE.tex

# 4. Schritt: Dritte Kompilation mit XeLaTeX (für Referenzen und Layout)
xelatex $TEX_FILE.tex
