import psycopg2
import argparse
import pandas as pd
import requests
import json

# API-Konfiguration für die limesurvey implementierung PrDiSy
LIMESURVEY_URL = "http://limesurvey.ddev.site/index.php/admin/remotecontrol"
USERNAME = "admin"  # Ersetzen Sie dies durch Ihren Admin-Benutzernamen
PASSWORD = "admin"  # Ersetzen Sie dies durch Ihr Passwort


###USAGE###
# Nutzung
# 1. Tabellen erstellen

# python pradisy_add_participant.py --create-tables
# 2. Teilnehmer hinzufügen

# python pradisy_add_participant.py --add-participant \
#   --patient-id "08bd93f6-0968-4260-8281-2a44f72a55fc" \
#   --patient-id "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX" \
#   --name "Anna" --surname "Schmidt" \
#   --date-of-birth "1990-01-01" --testperson False \
#   --mail "anna.schmidt@example.com" \
#   --encryption-key "sicherer_schluessel"
# 3. Neue Survey für Teilnehmer hinzufügen

# python pradisy_add_participant.py --add-survey \
#   --patient-id "08bd93f6-0968-4260-8281-2a44f72a55fc" \
#   --raw-data '{"item1": 3, "item2": 4}' \
#   --results '{"total_score": 7, "interpretation": "mild"}'


# PostgreSQL-Konfiguration
DB_CONFIG = {
    "dbname": "diagnostik",
    "user": "diagnostik_user",
    "password": "#IntroiboAdAltareDeiAdDeumQuiLaetificatAnimaMea#",
    "host": "localhost",
    "port": 5432
}

CREATE_PGCRYPTO_EXTENSION = "CREATE EXTENSION IF NOT EXISTS pgcrypto;"

CREATE_PARTICIPANTS_TABLE = """
CREATE TABLE IF NOT EXISTS pradisy_participants (
    patient_id UUID PRIMARY KEY,
    name BYTEA NOT NULL,
    surname BYTEA NOT NULL,
    date_of_birth DATE NOT NULL,
    testperson BOOLEAN DEFAULT FALSE,
    mail BYTEA NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);
"""

CREATE_SURVEY_INSTANCES_TABLE = """
CREATE TABLE IF NOT EXISTS pradisy_survey_instances (
    survey_instance_id SERIAL PRIMARY KEY,
    patient_id UUID REFERENCES pradisy_participants(patient_id) ON DELETE CASCADE,
    survey_reference INTEGER NOT NULL,
    raw_data JSONB,
    results JSONB,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);
"""

INSERT_OR_UPDATE_PARTICIPANT = """
INSERT INTO pradisy_participants (patient_id, name, surname, date_of_birth, testperson, mail)
VALUES (
    %s,
    pgp_sym_encrypt(%s, %s), -- Name verschlüsseln
    pgp_sym_encrypt(%s, %s), -- Nachname verschlüsseln
    %s,
    %s,
    pgp_sym_encrypt(%s, %s) -- E-Mail verschlüsseln
)
ON CONFLICT (patient_id)
DO UPDATE SET
    name = pgp_sym_encrypt(EXCLUDED.name, %s),
    surname = pgp_sym_encrypt(EXCLUDED.surname, %s),
    date_of_birth = EXCLUDED.date_of_birth,
    testperson = EXCLUDED.testperson,
    mail = pgp_sym_encrypt(EXCLUDED.mail, %s),
    updated_at = now();
"""

def get_session_key():
    """Holt einen Session-Key von der LimeSurvey API."""
    payload = {
        "method": "get_session_key",
        "params": [USERNAME, PASSWORD],
        "id": 1
    }
    headers = {"content-type": "application/json"}
    response = requests.post(LIMESURVEY_URL, data=json.dumps(payload), headers=headers)
    response.raise_for_status()
    return response.json()["result"]

def import_participant(session_key, participant):
    """Importiert einen Teilnehmer in die zentrale Teilnehmerdatenbank."""
    payload = {
        "method": "cpd_importParticipants",
        "params": [session_key, [participant]],
        "id": 1
    }
    headers = {"content-type": "application/json"}
    response = requests.post(LIMESURVEY_URL, data=json.dumps(payload), headers=headers)
    response.raise_for_status()
    return response.json()

def release_session_key(session_key):
    """Gibt den Session-Key frei."""
    payload = {
        "method": "release_session_key",
        "params": [session_key],
        "id": 1
    }
    headers = {"content-type": "application/json"}
    requests.post(LIMESURVEY_URL, data=json.dumps(payload), headers=headers)

def connect_db():
    """Stellt eine Verbindung zur PostgreSQL-Datenbank her."""
    return psycopg2.connect(**DB_CONFIG)

def create_tables():
    """Erstellt die notwendigen Tabellen."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(CREATE_PGCRYPTO_EXTENSION)
        cursor.execute(CREATE_PARTICIPANTS_TABLE)
        cursor.execute(CREATE_SURVEY_INSTANCES_TABLE)
    conn.commit()
    conn.close()

def add_or_update_participant(patient_id, name, surname, date_of_birth, testperson, mail, encryption_key):
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(INSERT_OR_UPDATE_PARTICIPANT, (
                patient_id,
                name, encryption_key,
                surname, encryption_key,
                date_of_birth,
                testperson,
                mail, encryption_key,
                encryption_key, encryption_key, encryption_key
            ))
        conn.commit()
        print(f"Teilnehmer {patient_id} erfolgreich hinzugefügt oder aktualisiert.")
    except Exception as e:
        conn.rollback()
        print(f"Fehler beim Hinzufügen/Aktualisieren: {e}")
    finally:
        conn.close()


# 03.01.20225
# def add_or_update_participant(patient_id, name, surname, date_of_birth, testperson, mail, encryption_key):
#     """Fügt einen neuen Teilnehmer hinzu oder aktualisiert vorhandene Daten."""
#     conn = connect_db()
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute(INSERT_OR_UPDATE_PARTICIPANT, (
#                 patient_id,
#                 name, encryption_key,
#                 surname, encryption_key,
#                 date_of_birth,
#                 testperson,
#                 mail, encryption_key,
#                 encryption_key, encryption_key, encryption_key
#             ))
#         conn.commit()
#         print(f"Teilnehmer {patient_id} erfolgreich hinzugefügt oder aktualisiert.")
#     except Exception as e:
#         conn.rollback()
#         print(f"Fehler beim Hinzufügen/Aktualisieren des Teilnehmers: {e}")
#     finally:
#         conn.close()


# 03.01.2024 
# def add_or_update_participant(patient_id, name, surname, date_of_birth, testperson, mail, encryption_key):
#     """Fügt einen neuen Teilnehmer hinzu oder aktualisiert vorhandene Daten."""
#     conn = connect_db()
#     with conn.cursor() as cursor:
#         cursor.execute(INSERT_OR_UPDATE_PARTICIPANT, (
#             patient_id,
#             name, encryption_key,  # Name verschlüsseln
#             surname, encryption_key,  # Nachname verschlüsseln
#             date_of_birth,
#             testperson,
#             mail, encryption_key,  # E-Mail verschlüsseln
#             encryption_key, encryption_key, encryption_key  # Schlüssel für Updates
#         ))
#     conn.commit()
#     conn.close()

def add_survey_for_participant(patient_id, raw_data=None, results=None):
    """Fügt einen neuen Survey für einen Teilnehmer hinzu."""
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM pradisy_survey_instances WHERE patient_id = %s
            """, (patient_id,))
            survey_count = cursor.fetchone()[0]
            survey_reference = survey_count + 1

            cursor.execute("""
                INSERT INTO pradisy_survey_instances (patient_id, survey_reference, raw_data, results)
                VALUES (%s, %s, %s, %s)
            """, (patient_id, survey_reference, raw_data, results))
        conn.commit()
        print(f"Survey-Referenz {survey_reference} für Teilnehmer {patient_id} wurde hinzugefügt.")
    finally:
        conn.close()

def list_participants():
    """Listet alle Teilnehmer in der Tabelle `pradisy_participants` auf."""
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT patient_id, pgp_sym_decrypt(name::bytea, %s), pgp_sym_decrypt(surname::bytea, %s), date_of_birth, testperson, pgp_sym_decrypt(mail::bytea, %s) FROM pradisy_participants", ("encryption_key", "encryption_key", "encryption_key"))
            participants = cursor.fetchall()
            for participant in participants:
                print(f"Patient ID: {participant[0]}, Name: {participant[1]} {participant[2]}, DOB: {participant[3]}, Testperson: {participant[4]}, Mail: {participant[5]}")
    except Exception as e:
        print(f"Fehler beim Abrufen der Teilnehmer: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verwalte die Tabellen in der PostgreSQL-Datenbank des Praxis Diagnostik Systems (PraDiSy).")
    parser.add_argument("--create-tables", action="store_true", help="Erstellt alle notwendigen Tabellen.")
    parser.add_argument("--add-participant", action="store_true", help="Fügt einen neuen Teilnehmer hinzu oder aktualisiert vorhandene Daten.")
    parser.add_argument("--add-survey", action="store_true", help="Fügt eine neue Survey-Instanz für einen Teilnehmer hinzu.")
    parser.add_argument("--patient-id", type=str, required=True, help="Eindeutige ID des Teilnehmers (UUID).")
    parser.add_argument("--name", type=str, help="Vorname des Teilnehmers.")
    parser.add_argument("--surname", type=str, help="Nachname des Teilnehmers.")
    parser.add_argument("--date-of-birth", type=str, help="Geburtsdatum des Teilnehmers (YYYY-MM-DD).")
    parser.add_argument("--testperson", type=bool, default=False, help="Gibt an, ob die Person eine Testperson ist.")
    parser.add_argument("--mail", type=str, help="E-Mail-Adresse des Teilnehmers.")
    parser.add_argument("--raw-data", type=str, help="Rohdaten der Survey als JSON-String.")
    parser.add_argument("--results", type=str, help="Auswertungsergebnisse der Survey als JSON-String.")
    parser.add_argument("--encryption-key", type=str, help="Verschlüsselungsschlüssel (erforderlich für Teilnehmer).")

    args = parser.parse_args()

    if args.create_tables:
        create_tables()
        print("Tabellen wurden erfolgreich erstellt.")

    if args.add_participant:
        if not all([args.name, args.surname, args.date_of_birth, args.mail, args.encryption_key]):
            print("Fehlende Parameter: `name`, `surname`, `date-of-birth`, `mail` und `encryption-key` sind erforderlich.")
            list_participants()
        else:
            add_or_update_participant(
                patient_id=args.patient_id,
                name=args.name,
                surname=args.surname,
                date_of_birth=args.date_of_birth,
                testperson=args.testperson,
                mail=args.mail,
                encryption_key=args.encryption_key
            )
            print(f"Teilnehmer {args.name} {args.surname} wurde hinzugefügt oder aktualisiert.")
            list_participants()

    if args.add_survey:
        if not args.patient_id:
            print("Fehlende Parameter: `patient-id` ist erforderlich, um eine Survey hinzuzufügen.")
        else:
            add_survey_for_participant(
                patient_id=args.patient_id,
                raw_data=args.raw_data,
                results=args.results
            )
