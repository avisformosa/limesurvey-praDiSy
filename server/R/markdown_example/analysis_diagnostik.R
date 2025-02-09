# analysis.R

# -----------------------------
# 1) Beispielberechnung in R
# -----------------------------
sum_score       <- sum(1:10)              # Ergebnis = 55
document_title  <- "Mein Quarto-Report"
patient_name    <- "Max Mustermann der Erste"
test_abrev   <- "SCL90-R"
datum        <- "07.02.2025"
pat_name     <- "Müller"
pat_surname  <- "Klaus"
pat_gebdat   <- "05.05.1999"

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
# Quarto CLI erlaubt Parameter per --execute-param <name>=<value>.
# Wir wollen sum_score, document_title, patient_name übergeben.
# Siehe: https://quarto.org/docs/computations/params.html

# params <- list(
#   sum_score       = sum_score,
#   document_title  = document_title,
#   patient_name    = patient_name
# )
# Quarto-Parameter erweitern

# Gegebene Datums-/Zeitwerte
time1 <- as.POSIXct("2025-01-03 12:59:10")
time2 <- as.POSIXct("2025-01-03 10:59:05")

formatted_date <- format(time2, "%e. %B %Y")

# Berechnung der Differenz in Sekunden
time_diff <- as.numeric(difftime(time1, time2, units = "secs"))

# Konvertierung in Minuten und Sekunden
minutes <- floor(time_diff / 60)
seconds <- time_diff %% 60

# Formatierung als "mm:ss"
time_formatted <- sprintf("%02d:%02d", minutes, seconds)

# Ausgabe
cat("Verstrichene Zeit:", time_formatted, "\n")

params <- list(
  sum_score       = sum_score,
  document_title  = document_title,
  patient_name    = patient_name,
  test_name       = "Beck-Depressions-Inventar",
  test_abrev      = "BDI-II",
  test_date       = formatted_date,  
  test_duration   = time_formatted,  
  datum           = "07.02.2025",
  pat_name        = "Klaus",
  pat_surname     = "Müller",
  pat_gebdat      = "05.05.1999",
  pat_gender      = "männlich"  
)

# Baue den Pfad zur .qmd-Datei zusammen:
qmd_file <- file.path(get_script_dir(), "server/R/markdown_example/diagnostik.qmd")
# script_dir <- "/path/to/server/R/markdown_example"
script_dir_org <- file.path(getwd())
script_dir <- file.path(getwd(), "server/R/markdown_example")
tex_file <- "diagnostik"

# Basiskommando: "quarto render <qmd_file> --to pdf"
quarto_args <- c(
  "render",
  qmd_file,
  "--to", "pdf"
)

# Hänge nun für jeden Parameter --execute-param an
for (pname in names(params)) {
  pvalue <- params[[pname]]
  # Strings in einfache Quotes packen, z.B. 'Max Mustermann'
  pvalue_quoted <- paste0("'", pvalue, "'")
  # Syntax: --execute-param name='Wert'
  quarto_args <- c(quarto_args, "--execute-param", paste0(pname, "=", pvalue_quoted))
}

# Letzten Endes rufen wir so system2 auf:
system2("quarto", quarto_args, wait = TRUE)
# system2("bash", args = c(file.path(get_script_dir(), "server/R/markdown_example/postprocess.sh"), file.path(get_script_dir(), "server/R/markdown_example/diagnostik")), wait = TRUE)
setwd(script_dir)
system2("bash", args = c("postprocess.sh", tex_file), wait = TRUE)
system2("open", "diagnostik.pdf", wait = TRUE)
setwd(script_dir_org)
#system2("bash", args = c(file.path(get_script_dir(), "server/R/markdown_example/postprocess.sh"), file.path(get_script_dir(), "server/R/markdown_example/diagnostik")), wait = FALSE)
#system2("open", file.path(get_script_dir(), "server/R/markdown_example/diagnostik.pdf"), wait = TRUE)

# Das war's! Nun werden sum_score, document_title, patient_name
# aus R an Quarto (diagnostik.qmd) übergeben.
