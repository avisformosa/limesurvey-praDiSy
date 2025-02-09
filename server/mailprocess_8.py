import os
import sys
import argparse
import time
from pathlib import Path
import imaplib
import email
from email.header import decode_header
import re
import psycopg2
import subprocess
import shutil
import pandas as pd


# IMAP-Server-Konfiguration
# DEMOPNSTRATION PURPOSE
# IMAP_SERVER = "imap.strato.de"
# USERNAME = "diagnostik@gemeinschaftspraxis-psychotherapie-erfurt.de"
# PASSWORD = "#AspergesMeHysopoEtMundabor#"
IMAP_SERVER = "imap.strato.de"
USERNAME = "pradisy@gemeinschaftspraxis-psychotherapie-erfurt.de"
PASSWORD = "#RorateCaeliDesuper#3"

# PostgreSQL-Konfiguration
DB_CONFIG = {
    "dbname": "diagnostik",
    "user": "diagnostik_user",
    "password": "#IntroiboAdAltareDeiAdDeumQuiLaetificatAnimaMea#",
    "host": "localhost",
    "port": 5432
}

# Basis-Verzeichnis
script_path = Path(__file__).resolve()
script_dir = script_path.parent
BASE_DIR = Path("/tmp/pradisy_1.0") if "--tmpdir" in sys.argv else script_dir / "pradisy_1.0"
R_SCRIPT_DIR = script_dir / "R"

# R-Skript-Mapping relativ zum Skript-Verzeichnis
R_SCRIPTS = {
    "769569": R_SCRIPT_DIR / "survey_769569.R",  # 769569 SampleBDI two item test
    "67890": R_SCRIPT_DIR / "survey_67890.R",
}

DEFAULT_R_SCRIPT = R_SCRIPT_DIR / "default_script.R"

# Verzeichnisse für CSV-Dateien
INPUT_DIR = BASE_DIR / "tobeprocessed"
PROCESSING_DIR = BASE_DIR / "processing"
PROCESSED_DIR = BASE_DIR / "finished"
FAILED_DIR = BASE_DIR / "failed"

# Betreff-Regex
subject_pattern = re.compile(
    r"DIAG(?P<diag_id>\d+)PARTICIPANT(?P<participant_id>[a-f0-9\-]+)DATE(?P<date>\d{4}-\d{2}-\d{2})TIME(?P<time>\d{2}:\d{2}:\d{2})"
)

def log_debug(message):
    """Gibt Debug-Meldungen aus, wenn Debugging aktiv ist."""
    if "--debug" in sys.argv:
        print(f"[DEBUG] {message}")

def ensure_directories_exist():
    """Stellt sicher, dass alle Verzeichnisse existieren."""
    for directory in [INPUT_DIR, PROCESSING_DIR, PROCESSED_DIR, FAILED_DIR, R_SCRIPT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        log_debug(f"Ensured directory exists: {directory}")

def check_postgres():
    log_debug("check_postgres() is called")
    """Prüft, ob PostgreSQL läuft, und startet es falls nötig."""
    try:
        subprocess.run(["pg_isready", "-q"], check=True)
        log_debug("PostgreSQL läuft.")
    except subprocess.CalledProcessError:
        print("PostgreSQL läuft nicht. Versuche, es zu starten...")
        subprocess.run(["sudo", "port", "load", "postgresql15-server"], check=True)
        print("PostgreSQL wurde gestartet. Warte 5 Sekunden...")
        time.sleep(5)

def connect_db():
    """Verbindet sich mit PostgreSQL, nachdem überprüft wurde, ob es läuft."""
    check_postgres()
    return psycopg2.connect(**DB_CONFIG)

def create_table_if_not_exists():
    """Erstellt die Tabelle processing_status, wenn sie nicht existiert."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_status (
                email_id TEXT PRIMARY KEY,
                diag_id TEXT NOT NULL,
                participant_id TEXT NOT NULL,
                date DATE NOT NULL,
                time TIME NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT now(),
                updated_at TIMESTAMP DEFAULT now()
            );
        """)
    conn.commit()
    conn.close()
    log_debug("Tabelle processing_status erstellt.")

def insert_email_metadata(email_id, diag_id, participant_id, date, time):
    """Speichert Metadaten zur E-Mail in der Datenbank."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO processing_status (email_id, diag_id, participant_id, date, time, status)
            VALUES (%s, %s, %s, %s, %s, 'pending')
            ON CONFLICT (email_id) DO NOTHING;
        """, (email_id, diag_id, participant_id, date, time))
    conn.commit()
    conn.close()

def process_tobeprocessed():
    """Überprüft das Verzeichnis `tobeprocessed` und verarbeitet nur gültige CSV-Dateien."""
    for file_name in os.listdir(INPUT_DIR):
        file_path = os.path.join(INPUT_DIR, file_name)

        # Nur CSV-Dateien verarbeiten, keine Systemdateien wie .DS_Store
        if not file_name.endswith(".csv"):
            log_debug(f"Überspringe ungültige Datei: {file_name}")
            continue

        log_debug(f"Verarbeite Datei aus tobeprocessed: {file_name}")

        # CSV-Datei laden und participant_id sowie submitdate extrahieren
        try:
            # Semikolon als Trennzeichen und richtige Kodierung verwenden
            data = pd.read_csv(file_path, delimiter=";", encoding="utf-8")
            
            # Teilnehmer-ID und Zeitstempel aus der CSV extrahieren
            participant_id = data.get('participant_id').iloc[0]  # Annahme: Alle Zeilen haben die gleiche participant_id
            submitdate = data.get('submitdate').iloc[0]         # Zeitstempel aus der CSV
            survey_id = extract_survey_id_from_csv(file_path)   # Survey ID aus der CSV

            # Validierung der Daten
            if not participant_id or not submitdate or not survey_id:
                log_debug(f"Fehlende Informationen in Datei {file_name}. Überspringe.")
                continue

            # process_file mit allen relevanten Informationen aufrufen
            status = process_file(file_path, survey_id, participant_id, submitdate)
            log_debug(f"Verarbeitung abgeschlossen: {file_name} mit Status {status}")
        except pd.errors.ParserError as e:
            log_debug(f"Parser-Fehler bei der Verarbeitung von {file_name}: {e}")
        except KeyError as e:
            log_debug(f"Fehlender Schlüssel in der CSV {file_name}: {e}")
        except Exception as e:
            log_debug(f"Fehler beim Verarbeiten der Datei {file_name}: {e}")





def extract_survey_id_from_filename(file_name):
    """Extrahiert die survey_id aus dem Dateinamen, falls möglich."""
    match = re.search(r"(\d+)_results", file_name)
    if match:
        return match.group(1)
    log_debug(f"Konnte keine survey_id aus {file_name} extrahieren. Verwende Default-ID.")
    return None

def extract_survey_id_from_csv(file_path):
    """Extrahiert die survey_id aus einer CSV-Datei."""
    try:
        # Semikolon als Delimiter angeben
        data = pd.read_csv(file_path, delimiter=";")
        if 'survey_id' in data.columns:
            survey_id = data['survey_id'].iloc[0]  # Annahme: Alle Zeilen haben die gleiche survey_id
            log_debug(f"Extrahierte survey_id aus CSV: {survey_id}")
            return str(survey_id)
        else:
            log_debug(f"Spalte 'survey_id' nicht in CSV gefunden: {file_path}")
            return None
    except Exception as e:
        log_debug(f"Fehler beim Lesen der CSV {file_path}: {e}")
        return None


def process_file(file_path, survey_id, participant_id, timestamp):
    """Verarbeitet die Datei mit dem entsprechenden R-Skript."""
    # Wähle das R-Skript basierend auf der survey_id
    r_script = R_SCRIPTS.get(survey_id, DEFAULT_R_SCRIPT)

    if not r_script.exists():
        log_debug(f"R-Skript für Survey ID {survey_id} nicht gefunden. Überspringe.")
        return "failed"

    # Logische Pfade auflösen
    processing_path = os.path.join(PROCESSING_DIR, os.path.basename(file_path))
    shutil.move(file_path, processing_path)

    log_debug(f"Using R script: {r_script} for Survey ID: {survey_id}")
    try:
        # R-Skript mit der Datei und allen Argumenten aufrufen
        subprocess.run([
            "Rscript",
            str(r_script),      # Pfad zum R-Skript
            processing_path,    # Pfad zur CSV-Datei
            survey_id,          # survey_id als Parameter
            participant_id,     # participant_id als Parameter
            timestamp           # Zeitstempel als Parameter
        ], check=True)
        shutil.move(processing_path, os.path.join(PROCESSED_DIR, os.path.basename(file_path)))
        return "completed"
    except Exception as e:
        print(f"Error processing file {file_path} with Survey ID {survey_id}: {e}")
        shutil.move(processing_path, os.path.join(FAILED_DIR, os.path.basename(file_path)))
        return "failed"


# def process_file(file_path, survey_id):
#     """Verarbeitet die Datei mit dem entsprechenden R-Skript."""
#     # Wähle das R-Skript basierend auf der survey_id
#     r_script = R_SCRIPTS.get(survey_id, DEFAULT_R_SCRIPT)
    
#     # Logische Pfade auflösen
#     processing_path = os.path.join(PROCESSING_DIR, os.path.basename(file_path))
#     shutil.move(file_path, processing_path)

#     log_debug(f"Using R script: {r_script} for Survey ID: {survey_id}")
#     # try:
#     #     # R-Skript mit der Datei und survey_id als Parameter aufrufen
#     #     subprocess.run([
#     #         "Rscript",
#     #         str(r_script),  # Pfad zum R-Skript
#     #         processing_path,  # Pfad zur CSV-Datei
#     #         survey_id        # survey_id als Parameter
#     #     ], check=True)
#     #     shutil.move(processing_path, os.path.join(PROCESSED_DIR, os.path.basename(file_path)))
#     #     return "completed"
#     # except Exception as e:
#     #     print(f"Error processing file {file_path} with Survey ID {survey_id}: {e}")
#     #     shutil.move(processing_path, os.path.join(FAILED_DIR, os.path.basename(file_path)))
#     #     return "failed"

def save_attachment(msg, folder):
    """Speichert CSV-Anhänge einer Nachricht im angegebenen Ordner."""
    for part in msg.walk():
        # Nur Anhänge verarbeiten
        if part.get_content_maintype() == "multipart":
            continue
        if part.get_content_type() == "text/csv":
            filename = part.get_filename()
            if filename:
                filepath = os.path.join(folder, filename)
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                log_debug(f"Saved attachment: {filepath}")
                return filepath
    return None

def save_attachment_with_survey_id(msg, folder, survey_id):
    """Speichert CSV-Anhänge mit einer zusätzlichen Spalte für die survey_id."""
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        if part.get_content_type() == "text/csv":
            filename = part.get_filename()
            if filename:
                filepath = os.path.join(folder, filename)
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                log_debug(f"Saved original attachment: {filepath}")
                
                # CSV laden, bearbeiten und speichern
                try:
                    data = pd.read_csv(filepath)
                    data['survey_id'] = survey_id  # survey_id als neue Spalte hinzufügen
                    data.to_csv(filepath, index=False)
                    log_debug(f"Updated CSV with survey_id: {survey_id}")
                    return filepath
                except Exception as e:
                    log_debug(f"Fehler beim Verarbeiten der CSV {filepath}: {e}")
                    return None
    return None

# Save attachment function
def save_attachment_with_survey_id_and_email_id(msg, folder, survey_id, email_id):
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        if part.get_content_type() == "text/csv":
            filename = part.get_filename()
            if filename:
                filepath = os.path.join(folder, filename)
                # Avoid overwriting files by checking existence
                if os.path.exists(filepath):
                    log_debug(f"File {filename} already exists. Skipping.")
                    return None
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                log_debug(f"Saved attachment: {filepath}")

                # Add survey_id and email_id to the CSV
                try:
                    data = pd.read_csv(filepath, delimiter=";", encoding="utf-8")
                    data['survey_id'] = survey_id
                    data['email_id'] = email_id
                    data.to_csv(filepath, sep=";", index=False)
                    log_debug(f"Updated CSV with survey_id {survey_id} and email_id {email_id}")
                except Exception as e:
                    log_debug(f"Error processing CSV {filepath}: {e}")
                    os.remove(filepath)  # Remove faulty file
                    return None

                return filepath
    return None

# Function to extract survey_id from email subject
def extract_survey_id(subject):
    # Define regex pattern for extracting surveyId
    match = re.search(r'DIAG(\d+)PARTICIPANT', subject)
    if match:
        return match.group(1)
    return None

def check_mail():
    log_debug("Connecting to IMAP server...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(USERNAME, PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, "UNSEEN")
    mail_ids = messages[0].split()

    for mail_id in mail_ids:
        status, msg_data = mail.fetch(mail_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                email_id = msg.get("Message-ID")

                # Extract survey_id from the subject
                survey_id = extract_survey_id(subject)
                if not survey_id:
                    log_debug(f"Could not extract survey_id from subject: {subject}")
                    continue

                # Save attachment with survey_id and email_id
                filepath = save_attachment_with_survey_id_and_email_id(msg, INPUT_DIR, survey_id, email_id)
                if filepath:
                    log_debug(f"File saved: {filepath}. Verifying uniqueness...")
                    
                    # Check if file already exists in processing
                    processed_file_path = os.path.join(PROCESSING_DIR, os.path.basename(filepath))
                    if os.path.exists(processed_file_path):
                        log_debug(f"File {os.path.basename(filepath)} already processed. Skipping.")
                    else:
                        log_debug(f"File {os.path.basename(filepath)} is unique and ready for further processing.")

    mail.logout()



if __name__ == "__main__":
    log_debug("Main Skritp is runnung ...")
    ensure_directories_exist()
    create_table_if_not_exists()
    check_mail()
    # process_tobeprocessed()
