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
debug_flag <- args[5]       # Debug-Flag

# Debug-Flag in logischer Form
debug_mode <- tolower(debug_flag) == "true"



# Funktion zum Debug-Logging
debug_log <- function(message) {
  if (debug_mode) {
    cat("[DEBUG]", message, "\n")
  }
}

# Erstellung einer Item-Karte als Named List
item_labels <- list(
  BDI2Item1 = "Traurigkeit",
  BDI2Item2 = "Pessimismus",
  BDI2Item3 = "Versagensgefühle",
  BDI2Item4 = "Verlust von Freude",
  BDI2Item5 = "Schuldgefühle",
  BDI2Item6 = "Bestrafungsgefühle",
  BDI2Item7 = "Selbstablehnung",
  BDI2Item8 = "Selbstvorwürfe",
  BDI2Item9 = "Suizidgedanken",
  BDI2Item10 = "Weinen",
  BDI2Item11 = "Unruhe",
  BDI2Item12 = "Interessensverlust",
  BDI2Item13 = "Entschlusslosigkeit",
  BDI2Item14 = "Wertlosigkeit",
  BDI2Item15 = "Energieverlust",
  BDI2Item16 = "Veränderungen der Schlafgewohnheiten",
  BDI2Item17 = "Reizbarkeit",
  BDI2Item18 = "Veränderungen des Appetits",
  BDI2Item19 = "Konzentrationsschwierigkeiten",
  BDI2Item20 = "Ermüdung oder Erschöpfung",
  BDI2Item21 = "Verlust an sexuellem Interesse"
)

debug_log(
  paste0(
    "csv_path: ", csv_path, "\n",
    "survey_id: ", survey_id, "\n",
    "participant_id: ", participant_id, "\n",
    "timestamp: ", timestamp, "\n",
    "debug_flag: ", debug_flag
  )
)

# Sicherstellen, dass survey_id korrekt ist
debug_log("Überprüfe survey_id...")

if (survey_id != "769569") {
  stop("\n[ERROR] Falsche survey_id für dieses R-Skript.")
}

survey_fullname = "Beck-Depressions-Inventar"
survey_abrev = "BDI II"
survey_version = "2.0"
survey_year = "1996"
survey_ref = "\cite{beck:2005}"
survey_description = "Das Beck-Depressions-Inventar (BDI) ist ein psychologisches Testverfahren, das die Schwere depressiver Symptomatik im klinischen Bereich erfasst. Dabei soll nicht die Depression an sich, sondern lediglich der Schweregrad der Depression erfasst werden." 
# Patienteninformation:
# Name, Nachname (Geb.-Datum)
# patienten-id
# Durchführungsdatum, Durchführungsnummer  
# Durchführungsbericht: An Herr Frau xxx. wurde das survey_fullname am xxx zum yyy-ten mal durchgeführt. 
# Die Durchführungsdauer betrug. xx Stunden, xx Minuten und xx Sekunden. errechnen aus startdate submitdate der csv
# Ergebnisse 
# Es wurde ein Summenwert von sum_score ermittelt, dieser entspricht {keiner ausgeprägten depresiven Symptomatik, einer leichtgradigen, ... , an der Schwelle zur} ...}
# die Anzahl der besonders belastenden Symptombereiche wurde mit  count_3_items ermittelt. Als spezifische belastungsfaktoren wurden itemlabels angegeben (sofern bis zu 5 items = 3), sonst wenn (mehr als 5 item größer gleich 3)einen satz wie die belastungen sind ausgeprägt und erstrecken sich auf alle dimensionen des psychischen erlebens.
# Der durchschnittliche Belasuntgwert wird mit mean_score  angegebn.
# if (verlauf >= 1) Verlaufsdiagram 
# if sum_score vorher >= sum_score jetzt Im Vergleich zur vormessung vom xxx hat sich die depressive Bealstung {verbessert, verschlechter nciht verändert sich die depressive Belastung}
# Verlaufsdiagramm


# Datenbankverbindung
conn <- dbConnect(
  RPostgres::Postgres(),
  dbname = "diagnostik",
  host = "localhost",
  port = 5432,
  user = "diagnostik_user",
  password = "#IntroiboAdAltareDeiAdDeumQuiLaetificatAnimaMea#"
)

# Funktion zum Ermitteln des Skriptpfads
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

# Prüfen, ob Teilnehmer existiert
participant_exists <- dbGetQuery(conn, paste0(
  "SELECT COUNT(*) FROM pradisy_participants WHERE patient_id = '", participant_id, "';"
))
if (participant_exists[1, 1] == 0) {
  stop("Participant not found in database.")
}else{
  debug_log("Teilnehmer gefunden.")
}

# Überprüfen, ob ein Eintrag mit der Kombination aus participant_id, survey_id und survey_timestamp existiert
debug_log("Überprüfe, ob der Datensatz bereits existiert...")

existing_entry <- dbGetQuery(conn, "
    SELECT COUNT(*) AS count
    FROM pradisy_survey_instances
    WHERE patient_id = $1
      AND survey_reference = $2
      AND survey_timestamp = $3",
    params = list(participant_id, survey_id, as.POSIXct(timestamp))
)

if (existing_entry$count > 0) {
    stop("Eintrag mit der gleichen Kombination aus participant_id, survey_id und survey_timestamp existiert bereits.")
} else {
    debug_log("Kein doppelter Eintrag gefunden. Fortfahren...")
}

debug_log("Hole Teilnehmerinformationen aus der Datenbank...")
participant_info <- dbGetQuery(conn, paste0(
  "SELECT pgp_sym_decrypt(name::bytea, '", encryption_key, "') AS name, ",
  "pgp_sym_decrypt(surname::bytea, '", encryption_key, "') AS surname, ",
  "education_status, gender FROM pradisy_participants ",
  "WHERE patient_id = '", participant_id, "';"
))
name <- participant_info$name[1]
surname <- participant_info$surname[1]
education_status <- participant_info$education_status[1]
gender <- participant_info$gender[1]
debug_log(paste("Name:", name, "Surname:", surname, "Education Status:", education_status, "Gender:", gender))


# 03.01.2025 2
# # Prüfen, ob der Datensatz mit gleichem Timestamp bereits existiert
# debug_log("Überprüfe, ob der Datensatz mit gleichem timestamp bereits existiert...")

# # Sicherstellen, dass der Timestamp korrekt formatiert ist
# formatted_timestamp <- format(as.POSIXct(timestamp, tz = "UTC"), "%Y-%m-%d %H:%M:%S")

# # SQL-Abfrage mit Parametern
# existing_entry_query <- "
#     SELECT COUNT(*)
#     FROM pradisy_survey_instances
#     WHERE patient_id = $1 AND survey_reference = $2 AND survey_timestamp = $3;
# "

# # Ausführen der Abfrage
# existing_entry <- dbGetQuery(conn, existing_entry_query, params = list(participant_id, survey_id, formatted_timestamp))

# # Überprüfen, ob ein Eintrag gefunden wurde
# if (existing_entry[1, 1] > 0) {
#     debug_log("Ein Eintrag mit gleichem timestamp existiert bereits.")
#     stop("Entry with the same timestamp already exists.")
# } else {
#     debug_log("Kein Eintrag mit gleichem timestamp gefunden. Fortfahren...")
# }


# 03.01.2025
# # Prüfen, ob der Datensatz mit gleichem Timestamp bereits existiert
# debug_log("Überprüfe, ob der Datensatz mit gleichem timestamp bereits existiert...")
# existing_entry <- dbGetQuery(conn, paste0(
#   "SELECT COUNT(*) FROM pradisy_survey_instances WHERE patient_id = '", participant_id,
#   "' AND survey_reference = ", survey_id, " AND created_at = '", timestamp, "';"
# ))
# if (existing_entry[1, 1] > 0) {
#   stop("Entry with the same timestamp already exists.")
# } else {
#   debug_log("Kein Eintrag mit gleichem timestamp gefunden. Fortfahren...")
# }

# CSV laden
debug_log("Lade CSV-Daten...")
data <- fread(csv_path)

# Berechnungen
debug_log("Berechne Summenscore, Anzahl der 3er-Items und Durchschnittswert...")
sum_score <- data[, sum(as.numeric(BDI2Item1), as.numeric(BDI2Item2), na.rm = TRUE)]
count_3_items <- sum(data[, .(BDI2Item1, BDI2Item2)] == 3, na.rm = TRUE)
mean_score <- mean(as.numeric(data[, .(BDI2Item1, BDI2Item2)]), na.rm = TRUE)
items_with_3 <- names(data[, .(BDI2Item1, BDI2Item2)][, lapply(.SD, function(x) x == 3)])

debug_log(paste(
  "Sum score:", sum_score,
  "Count 3 items:", count_3_items,
  "Mean score:", mean_score
))

# Ergebnisse speichern
debug_log("Speichere Ergebnisse in die Datenbank...")

query <- "INSERT INTO pradisy_survey_instances (patient_id, survey_reference, raw_data, results, survey_timestamp) 
          VALUES ($1, $2, $3, $4, $5)"
dbExecute(conn, query, params = list(
    participant_id,
    as.integer(survey_id),
    jsonlite::toJSON(data, auto_unbox = TRUE),
    jsonlite::toJSON(list(
        sum_score = sum_score,
        count_3_items = count_3_items,
        mean_score = mean_score,
        items_with_3 = items_with_3
    ), auto_unbox = TRUE),
    as.POSIXct(timestamp)
))
debug_log("Ergebnisse wurden erfolgreich in die Datenbank gespeichert.")


# 03.01.2025 -2 2
# query <- "INSERT INTO pradisy_survey_instances (patient_id, survey_reference, raw_data, results, survey_timestamp) 
#           VALUES ($1, $2, $3, $4, $5)"

# dbExecute(conn, query, params = list(
#     participant_id,  # $1
#     as.integer(survey_id),  # $2
#     jsonlite::toJSON(data, auto_unbox = TRUE),  # $3
#     jsonlite::toJSON(list(
#         sum_score = sum_score,
#         count_3_items = count_3_items,
#         mean_score = mean_score,
#         items_with_3 = items_with_3
#     ), auto_unbox = TRUE),  # $4
#     as.POSIXct(timestamp)  # $5
# ))


# 03.01.2025
# # Ergebnisse speichern
# debug_log("Speichere Ergebnisse in die Datenbank...")

# # JSON für raw_data und results erstellen
# raw_data_json <- jsonlite::toJSON(data, auto_unbox = TRUE)
# results_json <- jsonlite::toJSON(list(
#   sum_score = sum_score,
#   count_3_items = count_3_items,
#   mean_score = mean_score,
#   items_with_3 = items_with_3
# ), auto_unbox = TRUE)

# # Datenbankeintrag sicher durchführen
# query <- "
#   INSERT INTO pradisy_survey_instances (patient_id, survey_reference, raw_data, results)
#   VALUES ($1, $2, $3, $4);
# "

# # Parameter in der richtigen Reihenfolge binden
# dbExecute(conn, query, params = list(
#   participant_id,
#   survey_id,
#   raw_data_json,
#   results_json
# ))

# debug_log("Ergebnisse wurden erfolgreich in die Datenbank gespeichert.")



# # Verlauf abrufen

# Lese Verlaufsdaten aus der Datenbank
verlaufsdaten <- dbGetQuery(conn, paste0(
    "SELECT survey_timestamp, raw_data, results FROM pradisy_survey_instances WHERE patient_id = '", participant_id,
    "' AND survey_reference = ", survey_id, ";"
))

# Funktion zum Speichern der Verlaufsdaten in einer hierarchischen Ordnerstruktur
save_verlaufsdaten <- function(data, participant_id, survey_id) {
    # Basisverzeichnis relativ zum R-Skript festlegen
    script_dir <- get_script_dir()
    base_dir <- file.path(script_dir, "../pradisy_1.0/results")
    
    # Ordner für die participant_id erstellen
    participant_dir <- file.path(base_dir, participant_id)
    if (!dir.exists(participant_dir)) {
        dir.create(participant_dir, recursive = TRUE)
        debug_log(paste("Ordner erstellt:", participant_dir))
    }
    
    # Pfad für die CSV-Datei basierend auf der survey_id
    file_path <- file.path(participant_dir, paste0(survey_id, ".csv"))
    
    # Verlaufsdaten als CSV speichern
    if (exists("verlaufsdaten") && nrow(verlaufsdaten) > 0) {
        fwrite(verlaufsdaten, file = file_path)
        debug_log(paste("Verlaufsdaten gespeichert in:", file_path))
    } else {
        debug_log("Keine Verlaufsdaten vorhanden. Speicherung übersprungen.")
    }
}

  # save_verlaufsdaten <- function(data, participant_id) {
  #     # Basisverzeichnis relativ zum R-Skript festlegen
  #     script_path <- normalizePath(commandArgs(trailingOnly = FALSE)[grep("--file=", commandArgs(trailingOnly = FALSE))])
  #     script_dir <- dirname(gsub("--file=", "", script_path))
  #     base_dir <- file.path(script_dir, "../pradisy_1.0/results")
  #     debug_log(script_dir)
  #     debug_log(base_dir)

  #     # Ordner für die participant_id erstellen
  #     participant_dir <- file.path(base_dir, participant_id)
  #     if (!dir.exists(participant_dir)) {
  #         dir.create(participant_dir, recursive = TRUE)
  #         debug_log(paste("Ordner erstellt:", participant_dir))
  #     }
      
  #     # Pfad für die CSV-Datei
  #     file_path <- file.path(participant_dir, "verlaufsdaten.csv")
      
  #     # Verlaufsdaten als CSV speichern
  #     if (exists("verlaufsdaten") && nrow(verlaufsdaten) > 0) {
  #         fwrite(verlaufsdaten, file = file_path)
  #         debug_log(paste("Verlaufsdaten gespeichert in:", file_path))
  #     } else {
  #         debug_log("Keine Verlaufsdaten vorhanden. Speicherung übersprungen.")
  #     }
  # }

# Überprüfen, ob Verlaufsdaten existieren
if (nrow(verlaufsdaten) > 0) {
    # Konvertiere in data.table
    verlaufsdaten <- as.data.table(verlaufsdaten)
    
    # JSON-Inhalte in Spalten aufteilen
    verlaufsdaten[, `:=`(
        raw_data_parsed = lapply(raw_data, fromJSON),
        results_parsed = lapply(results, fromJSON)
    )]
    
    # raw_data-Parsen in Spalten erweitern
    raw_data_dt <- rbindlist(verlaufsdaten$raw_data_parsed, fill = TRUE)
    
    # results-Parsen in Spalten erweitern
    results_dt <- rbindlist(verlaufsdaten$results_parsed, fill = TRUE)
    
    # Kombiniere alle Daten in einen einzigen data.table
    verlaufsdaten <- cbind(
        time = verlaufsdaten$survey_timestamp,
        raw_data_dt,
        results_dt
    )
  debug_log(capture.output(print(verlaufsdaten)))
  debug_log(capture.output(print(raw_data_dt)))
  debug_log(capture.output(print(results_dt)))
  # Speichere die Verlaufsdaten als CSV
  if (exists("verlaufsdaten") && nrow(verlaufsdaten) > 0) {
      debug_log("Speichere Verlaufsdaten als CSV...")
      fwrite(verlaufsdaten, file = "verlaufsdaten.csv")
  } else {
      debug_log("Keine Verlaufsdaten vorhanden. Überspringe Speicherung.")
  }

  # Speichere raw_data_dt als CSV
  if (exists("raw_data_dt") && nrow(raw_data_dt) > 0) {
      debug_log("Speichere raw_data_dt als CSV...")
      fwrite(raw_data_dt, file = "raw_data_dt.csv")
  } else {
      debug_log("Keine raw_data_dt vorhanden. Überspringe Speicherung.")
  }

  # Speichere results_dt als CSV
  if (exists("results_dt") && nrow(results_dt) > 0) {
      debug_log("Speichere results_dt als CSV...")
      fwrite(results_dt, file = "results_dt.csv")
  } else {
      debug_log("Keine results_dt vorhanden. Überspringe Speicherung.")
  }

  save_verlaufsdaten(verlaufsdaten, participant_id, survey_id)


# Aufruf der Funktion im nicht-Debugging-Fall
if (!debug_mode) {
        save_verlaufsdaten(verlaufsdaten, participant_id, survey_id)
}


} else {
    debug_log("Keine Verlaufsdaten gefunden.")
}


# verlaufsdaten <- dbGetQuery(conn, paste0(
#     "SELECT survey_timestamp, raw_data, results FROM pradisy_survey_instances WHERE patient_id = '", participant_id,
#     "' AND survey_reference = ", survey_id, ";"
# ))

# if (nrow(verlaufsdaten) > 0) {
#     verlaufsdaten <- as.data.table(verlaufsdaten)
#     verlaufsdaten[, raw_data := lapply(raw_data, fromJSON)]
#     verlaufsdaten[, results := lapply(results, fromJSON)]
#     debug_log("Rohdaten aus der Datenbank:")
#     debug_log(capture.output(print(verlaufsdaten)))

# } else {
#     debug_log("Keine Verlaufsdaten gefunden.")
# }
# 03.01.2025
# debug_log("Lese Verlaufsdaten aus der Datenbank...")

# query <- "SELECT survey_timestamp, raw_data, results
#           FROM pradisy_survey_instances
#           WHERE patient_id = $1 AND survey_reference = $2
#           ORDER BY survey_timestamp ASC"

# result <- dbGetQuery(conn, query, params = list(participant_id, survey_id))

# # Verarbeitung der Rohdaten und Ergebnisse
# if (nrow(result) > 0) {
#     debug_log("Daten erfolgreich abgerufen. Konvertiere in data.table...")
#     history <- data.table(
#         timestamp = as.POSIXct(result$survey_timestamp),
#         item_values = lapply(result$raw_data, fromJSON),
#         results = lapply(result$results, fromJSON)
#     )
#     print(history)
# } else {
#     stop("Keine Verlaufsdaten gefunden.")
# }


# history <- dbGetQuery(conn, paste0(
#   "SELECT timestamp, results->>'sum_score' AS sum_score FROM pradisy_data WHERE participant_id = '",
#   participant_id, "' AND survey_id = '", survey_id, "';"
# ))
# history$timestamp <- as.POSIXct(history$timestamp)
# history$sum_score <- as.numeric(history$sum_score)

# # Verlauf darstellen
# plot <- ggplot(history, aes(x = timestamp, y = sum_score)) +
#   geom_line() + geom_point() +
#   labs(title = "Verlauf des Summenscores", x = "Zeit", y = "Summenscore")

# # PDF-Bericht erstellen
# rmarkdown::render(
#   "report_template.Rmd",
#   output_file = paste0("report_", participant_id, "_", survey_id, ".pdf"),
#   params = list(
#     participant_id = participant_id,
#     timestamp = timestamp,
#     sum_score = sum_score,
#     count_3_items = count_3_items,
#     mean_score = mean_score,
#     items_with_3 = items_with_3,
#     plot = plot
#   )
# )

survey_titl <- "BDI II"

knitr::include_graphics(praxis_logo)
cat("# Ergebnisprotokoll Psychodiagnostik: ", survey_title, "\n\n")
cat("**Ergebnisse:**\n")
cat("Summenwert: ", sum_score, "\n")
rmarkdown::render("survey_769569.Rmd")


# # Verbindung schließen
# dbDisconnect(conn)
