# Bibliotheken laden
library(data.table)
library(DBI)
library(RPostgres)
library(ggplot2)
library(rmarkdown)
library(jsonlite)

# Eingabeparameter
args <- commandArgs(trailingOnly = TRUE)
csv_path <- args[1]         # Pfad zur CSV-Datei
survey_id <- args[2]        # survey_id
participant_id <- args[3]   # participant_id
timestamp <- args[4]        # Zeitstempel

# Sicherstellen, dass survey_id korrekt ist
if (survey_id != "769569xxx") {
  stop("Falsche survey_id für dieses R-Skript.")
}

# Datenbankverbindung
config <- fromJSON(path.expand("~/.pradisy/config.json"))

con <- dbConnect(
  RPostgres::Postgres(),
  dbname = config$postgre_dbname,
  host = config$postgre_host,
  port = as.integer(config$postgre_port),
  user = config$postgre_user,
  password = config$postgre_password
)

# Prüfen, ob Teilnehmer existiert
participant_exists <- dbGetQuery(conn, paste0(
  "SELECT COUNT(*) FROM pradisy_participants WHERE patient_id = '", participant_id, "';"
))
if (participant_exists[1, 1] == 0) {
  stop("Participant not found in database.")
}

# Prüfen, ob der Datensatz mit gleichem timestamp bereits existiert
existing_entry <- dbGetQuery(conn, paste0(
  "SELECT COUNT(*) FROM pradisy_data WHERE participant_id = '", participant_id,
  "' AND survey_id = '", survey_id, "' AND timestamp = '", timestamp, "';"
))
if (existing_entry[1, 1] > 0) {
  stop("Entry with the same timestamp already exists.")
}

# CSV laden
data <- fread(csv_path)

# Berechnungen
sum_score <- data[, sum(BDI2Item1, BDI2Item2, na.rm = TRUE)]
count_3_items <- sum(data[, .(BDI2Item1, BDI2Item2)] == 3, na.rm = TRUE)
mean_score <- mean(data[, .(BDI2Item1, BDI2Item2)], na.rm = TRUE)
items_with_3 <- names(data[, .(BDI2Item1, BDI2Item2)][, lapply(.SD, function(x) x == 3)])

# Ergebnisse speichern
dbExecute(conn, paste0(
  "INSERT INTO pradisy_data (participant_id, survey_id, timestamp, raw_data, results) VALUES (",
  "'", participant_id, "', '", survey_id, "', '", timestamp, "', ",
  "'", jsonlite::toJSON(data), "', ",
  "'{\"sum_score\":", sum_score, ", \"count_3_items\":", count_3_items,
  ", \"mean_score\":", mean_score, ", \"items_with_3\":", jsonlite::toJSON(items_with_3), "}'"
  ");"
))

# Verlauf abrufen
history <- dbGetQuery(conn, paste0(
  "SELECT timestamp, results->>'sum_score' AS sum_score FROM pradisy_data WHERE participant_id = '",
  participant_id, "' AND survey_id = '", survey_id, "';"
))
history$timestamp <- as.POSIXct(history$timestamp)
history$sum_score <- as.numeric(history$sum_score)

# Verlauf darstellen
plot <- ggplot(history, aes(x = timestamp, y = sum_score)) +
  geom_line() + geom_point() +
  labs(title = "Verlauf des Summenscores", x = "Zeit", y = "Summenscore")

# PDF-Bericht erstellen
rmarkdown::render(
  "report_template.Rmd",
  output_file = paste0("report_", participant_id, "_", survey_id, ".pdf"),
  params = list(
    participant_id = participant_id,
    timestamp = timestamp,
    sum_score = sum_score,
    count_3_items = count_3_items,
    mean_score = mean_score,
    items_with_3 = items_with_3,
    plot = plot
  )
)

# Verbindung schließen
dbDisconnect(conn)
