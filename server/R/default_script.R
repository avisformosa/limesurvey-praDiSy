# Lade notwendige Bibliotheken
library(DBI)
library(RPostgres)
library(data.table)
library(jsonlite)

# Argumente vom Python-Skript
args <- commandArgs(trailingOnly = TRUE)
csv_path <- args[1]
diag_id <- args[2]
participant_id <- args[3]
date <- args[4]
time <- args[5]

# PostgreSQL-Verbindung
config <- fromJSON(path.expand("~/.pradisy/config.json"))

con <- dbConnect(
  RPostgres::Postgres(),
  dbname = config$postgre_dbname,
  host = config$postgre_host,
  port = as.integer(config$postgre_port),
  user = config$postgre_user,
  password = config$postgre_password
)

# CSV-Datei lesen
data <- fread(csv_path)

# Beispielverarbeitung
print(paste("Processing CSV for Participant:", participant_id))
data[, participant_id := participant_id]
data[, diag_id := diag_id]

# In PostgreSQL schreiben
dbWriteTable(con, "survey_results", data, append = TRUE, row.names = FALSE)

# Verbindung schließen
dbDisconnect(con)
