# analysis.R

# Beispielwerte
sum_score       <- sum(1:10)  # 55
document_title  <- "Beck Depressions Inventar (BDI II)"

# Quarto-Parameter via --execute-param übergeben
params <- list(
  document_title = document_title,
  sum_score      = sum_score
)

# Quarto-Basis-Kommando
# z.B. "quarto render report.qmd --to pdf --execute-param sum_score=55"
quarto_args <- c(
  "render",
  file.path(get_script_dir(), "server/R/markdown_example/report.qmd"),      # Oder: Pfad, wenn die Datei woanders liegt
  "--to", "pdf"      # PDF-Ausgabe
)

# Parameter anhängen
for (pname in names(params)) {
  pvalue <- params[[pname]]

  # Falls es Strings sind, in Anführungszeichen setzen
  # (für Zahlen reicht pvalue ohne Quotes meistens aus – 
  #  aber wir machen es zur Sicherheit einheitlich)
  pvalue_quoted <- paste0("'", pvalue, "'")
  quarto_args <- c(quarto_args, "--execute-param", paste0(pname, "=", pvalue_quoted))
}

# Render starten
system2("quarto", quarto_args, wait = TRUE)
