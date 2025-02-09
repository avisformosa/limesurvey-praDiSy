import os
import pandas as pd
import email
import imaplib
from email.header import decode_header
import shutil
import psycopg2
import logging

# Logging Setup
logging.basicConfig(level=logging.DEBUG)

# Directory Setup
BASE_DIR = "pradisy_1.0"
INPUT_DIR = os.path.join(BASE_DIR, "tobeprocessed")
PROCESSING_DIR = os.path.join(BASE_DIR, "processing")
PROCESSED_DIR = os.path.join(BASE_DIR, "finished")
FAILED_DIR = os.path.join(BASE_DIR, "failed")

# IMAP Configuration
IMAP_SERVER = "imap.strato.de"
USERNAME = "pradisy@gemeinschaftspraxis-psychotherapie-erfurt.de"
PASSWORD = "#RorateCaeliDesuper#3"

# PostgreSQL Configuration
# DB_CONFIG = {
#     "dbname": "pradisy",
#     "user": "pradisy_user",
#     "password": "securepassword",
#     "host": "localhost",
#     "port": 5432
# }

DB_CONFIG = {
    "dbname": "diagnostik",
    "user": "diagnostik_user",
    "password": "#IntroiboAdAltareDeiAdDeumQuiLaetificatAnimaMea#",
    "host": "localhost",
    "port": 5432
}

def log_debug(message):
    """Log debug messages."""
    print(f"[DEBUG] {message}")

def ensure_directories_exist():
    """Ensure necessary directories exist."""
    for directory in [INPUT_DIR, PROCESSING_DIR, PROCESSED_DIR, FAILED_DIR]:
        os.makedirs(directory, exist_ok=True)
        log_debug(f"Ensured directory exists: {directory}")

# Database Functions
def connect_db():
    """Connects to the PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)

def create_table_if_not_exists():
    """Creates the mail_tracking table if it does not exist."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mail_tracking (
                email_id TEXT PRIMARY KEY,
                survey_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT NOW()
            );
        """)
    conn.commit()
    conn.close()

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

# Check mail function
def check_mail():
    log_debug("Connecting to IMAP server...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(USERNAME, PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        mail_ids = messages[0].split()

        conn = connect_db()

        for mail_id in mail_ids:
            try:
                status, msg_data = mail.fetch(mail_id, "(RFC822)")
                if status != "OK":
                    log_debug(f"Failed to fetch mail ID {mail_id}. Skipping.")
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = decode_header(msg["Subject"])[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode()
                        email_id = msg.get("Message-ID")

                        # Extract survey_id from the subject
                        survey_id = extract_survey_id_from_subject(subject)

                        # Check if email is already tracked
                        with conn.cursor() as cursor:
                            cursor.execute("SELECT status FROM mail_tracking WHERE email_id = %s", (email_id,))
                            result = cursor.fetchone()

                        if result:
                            log_debug(f"Email {email_id} is already tracked with status {result[0]}. Skipping.")
                            continue

                        # Save attachment with survey_id and email_id
                        filepath = save_attachment_with_survey_id_and_email_id(msg, INPUT_DIR, survey_id, email_id)
                        if filepath:
                            # Insert into mail_tracking table
                            with conn.cursor() as cursor:
                                cursor.execute("""
                                    INSERT INTO mail_tracking (email_id, survey_id, file_path, status)
                                    VALUES (%s, %s, %s, %s)
                                """, (email_id, survey_id, filepath, "unprocessed"))
                            conn.commit()
                            log_debug(f"Email {email_id} has been tracked and file saved: {filepath}")

                            # Mark email as seen
                            mail.store(mail_id, '+FLAGS', '\\Seen')
            except Exception as e:
                log_debug(f"Error processing mail ID {mail_id}: {e}")

        conn.close()
        mail.logout()
    except Exception as e:
        log_debug(f"Error connecting to IMAP server: {e}")

# Process tobeprocessed directory
def process_tobeprocessed():
    """Processes all files in the tobeprocessed directory."""
    conn = connect_db()
    for file_name in os.listdir(INPUT_DIR):
        file_path = os.path.join(INPUT_DIR, file_name)

        if not file_name.endswith(".csv"):
            log_debug(f"Skipping non-CSV file: {file_name}")
            continue

        log_debug(f"Processing file: {file_name}")

        # Check if file is already processed
        with conn.cursor() as cursor:
            cursor.execute("SELECT status FROM mail_tracking WHERE file_path = %s", (file_path,))
            result = cursor.fetchone()

        if result and result[0] == "processed":
            log_debug(f"File {file_name} is already processed. Skipping.")
            continue

        # Move file to processing directory
        processing_path = os.path.join(PROCESSING_DIR, file_name)
        shutil.move(file_path, processing_path)
        log_debug(f"Moved file to processing directory: {processing_path}")

        try:
            # Process file logic here
            status = "completed"  # Placeholder for actual processing logic

            # Update mail_tracking status
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE mail_tracking
                    SET status = %s
                    WHERE file_path = %s
                """, (status, processing_path))
            conn.commit()

            # Move to finished directory if successful
            if status == "completed":
                finished_path = os.path.join(PROCESSED_DIR, file_name)
                shutil.move(processing_path, finished_path)
                log_debug(f"File {file_name} has been processed and moved to finished directory.")
        except Exception as e:
            log_debug(f"Error processing file {file_name}: {e}")

    conn.close()

if __name__ == "__main__":
    ensure_directories_exist()
    create_table_if_not_exists()
    check_mail()
    # process_tobeprocessed()
