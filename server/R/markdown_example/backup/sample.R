# analysis.R

# 1) Beispielberechnung
# ---------------------
# Angenommen, du hast eine Funktion oder einen Codeblock,
# der den Score berechnet. Hier ein Dummy-Beispiel:
sum_score <- sum(1:10)  # Ergebnis = 55

# Titel (oder sonstige Variablen) kannst du einfach als R-Objekt speichern
document_title <- "Beck Depressions Inventar (BDI II)"

# 2) R Markdown Dokument mit Parametern rendern
# --------------------------------------------
library(rmarkdown)
# library(here)

get_script_dir <- function() {
    # Versuchen, den Skriptpfad aus commandArgs zu extrahieren
    args <- commandArgs(trailingOnly = FALSE)
    file_arg <- grep("--file=", args, value = TRUE)
    if (length(file_arg) > 0) {
        # Extrahiere den Pfad und normalisiere ihn
        script_path <- gsub("--file=", "", file_arg)
        return(dirname(normalizePath(script_path)))
    } else {
        # Fallback: aktuelles Arbeitsverzeichnis
        return(getwd())
    }
}

# script_dir <- get_script_dir()
#base_dir <- file.path(script_dir, "../pradisy_1.0/results")

render(
  input = file.path(get_script_dir(), "server/R/markdown_example/sample.Rmd"),             # Name der .Rmd-Datei
  output_format = "pdf_document",   # oder "html_document" etc.
  output_file = "sample.pdf",       # Name der Ausgabedatei
  params = list(
    document_title = document_title,
    sum_score      = sum_score
  )
)

# rmarkdown::render(file.path(get_script_dir(), "server/R/markdown_example/sample.Rmd"))
