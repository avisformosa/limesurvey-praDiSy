# analysis.R

# -----------------------------
# 1) Beispielberechnung in R
# -----------------------------
sum_score <- sum(1:10)       # Ergebnis = 55
document_title <- "Mein Quarto-Report"

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

# -----------------------------
# 2) Quarto-Dokument rendern
# -----------------------------
# Wir möchten die Parameter an Quarto übergeben, damit sie dort (report.qmd) verwendet werden.
# Quarto erlaubt Parameter-Übergabe via:  --execute-param <name>=<value>
# Siehe: https://quarto.org/docs/computations/params.html

# Beispiel: "quarto render report.qmd --to pdf --execute-param sum_score=55 --execute-param document_title='Mein Report'"

# Also bauen wir uns die Argumentliste zusammen:

params <- list(
  sum_score = sum_score,
  document_title = document_title
)

cat(file.path(get_script_dir(), "server/R/markdown_example/report.qmd"))

# Basiskommando, Quarto soll "report.qmd" als PDF rendern:
quarto_args <- c(
  "render",        # Befehl: quarto render
  file.path(get_script_dir(), "server/R/markdown_example/report.qmd"),    # unsere Quarto-Datei
  "--to", "pdf"    # Zieldokument: PDF
)

# Für jeden Parameter fügen wir "--execute-param" <name>=<value> an
for (pname in names(params)) {
  pvalue <- params[[pname]]
  # Wenn es ein String ist, sollten wir Anführungszeichen setzen:
  # (Bei Zahlen oder Bool-Werten kann man es direkt übergeben.)
  # Zur Sicherheit wandeln wir alles in Zeichen um und umschließen es mit Anführungszeichen:
  pvalue_quoted <- paste0("'", pvalue, "'")
  # Zusammenbauen: "--execute-param", "name='wert'"
  quarto_args <- c(quarto_args, "--execute-param", paste0(pname, "=", pvalue_quoted))
}

# Jetzt rufen wir das Quarto-CLI auf:
system2("quarto", quarto_args, wait = TRUE)

# Hinweis: Falls "quarto" nicht im Pfad liegt, musst du den kompletten Pfad angeben:
# system2("/usr/local/bin/quarto", quarto_args, wait = TRUE)