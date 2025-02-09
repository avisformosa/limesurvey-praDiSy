import psycopg2
import argparse
import pandas as pd
import requests
import json

# Standardpfad zur Konfigurationsdatei
CONFIG_PATH = os.path.expanduser("~/.pradisy/config.json")

def load_config():
    """
    Lädt die Zugangsdaten aus der Konfigurationsdatei `~/.pradisy/config.json`.
    Falls die Datei nicht existiert, wird eine Fehlermeldung ausgegeben.
    """
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"❌ Die Konfigurationsdatei {CONFIG_PATH} wurde nicht gefunden!")
    
    with open(CONFIG_PATH, "r") as file:
        return json.load(file)


# Lade die Konfiguration
config = load_config()

# API-Konfiguration für die LimeSurvey-Implementierung
LIMESURVEY_URL = config["remote_url"]
USERNAME = config["remote_user"]
PASSWORD = config["remote_password"]

# PostgreSQL-Konfiguration
DB_CONFIG = {
    "dbname": config["postgre_dbname"],
    "user": config["postgre_user"],
    "password": config["postgre_password"],
    "host": config["postgre_host"],
    "port": config["postgre_port"]
}

CREATE_PGCRYPTO_EXTENSION = "CREATE EXTENSION IF NOT EXISTS pgcrypto;"

CREATE_PARTICIPANTS_TABLE = """
CREATE TABLE IF NOT EXISTS pradisy_participants (
    patient_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name BYTEA NOT NULL,
    surname BYTEA NOT NULL,
    date_of_birth DATE NOT NULL,
    testperson BOOLEAN DEFAULT FALSE,
    mail BYTEA NOT NULL UNIQUE,
    education_status VARCHAR(150),  -- Bildungsstatus
    gender VARCHAR(50),             -- Geschlecht
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);
"""


# 03.01.2025
# CREATE_PARTICIPANTS_TABLE = """
# CREATE TABLE IF NOT EXISTS pradisy_participants (
#     patient_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     name VARCHAR(512) NOT NULL,
#     surname VARCHAR(512) NOT NULL,
#     date_of_birth DATE NOT NULL,
#     testperson BOOLEAN DEFAULT FALSE,
#     mail VARCHAR(512) NOT NULL UNIQUE,
#     created_at TIMESTAMP DEFAULT now(),
#     updated_at TIMESTAMP DEFAULT now()
# );
# """

CREATE_SURVEY_INSTANCES_TABLE = """
CREATE TABLE IF NOT EXISTS pradisy_survey_instances (
    survey_instance_id SERIAL PRIMARY KEY,
    patient_id UUID REFERENCES pradisy_participants(patient_id) ON DELETE CASCADE,
    survey_reference INTEGER NOT NULL,
    raw_data JSONB,
    results JSONB,
    survey_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);
"""


# 03.01.2025
# CREATE_SURVEY_INSTANCES_TABLE = """
# CREATE TABLE IF NOT EXISTS pradisy_survey_instances (
#     survey_instance_id SERIAL PRIMARY KEY,
#     patient_id UUID REFERENCES pradisy_participants(patient_id) ON DELETE CASCADE,
#     survey_reference INTEGER NOT NULL,
#     raw_data JSONB,
#     results JSONB,
#     created_at TIMESTAMP DEFAULT now(),
#     updated_at TIMESTAMP DEFAULT now()
# );
# """

# 03.01.2025
# CREATE_PARTICIPANTS_TABLE = """
# CREATE TABLE IF NOT EXISTS pradisy_participants (
#     patient_id UUID PRIMARY KEY,
#     name BYTEA NOT NULL,
#     surname BYTEA NOT NULL,
#     date_of_birth DATE NOT NULL,
#     testperson BOOLEAN DEFAULT FALSE,
#     mail BYTEA NOT NULL UNIQUE,
#     created_at TIMESTAMP DEFAULT now(),
#     updated_at TIMESTAMP DEFAULT now()
# );
# """

# CREATE_SURVEY_INSTANCES_TABLE = """
# CREATE TABLE IF NOT EXISTS pradisy_survey_instances (
#     survey_instance_id SERIAL PRIMARY KEY,
#     patient_id UUID REFERENCES pradisy_participants(patient_id) ON DELETE CASCADE,
#     survey_reference INTEGER NOT NULL,
#     raw_data JSONB,
#     results JSONB,
#     created_at TIMESTAMP DEFAULT now(),
#     updated_at TIMESTAMP DEFAULT now()
# );
# """

INSERT_OR_UPDATE_PARTICIPANT = """
INSERT INTO pradisy_participants (patient_id, name, surname, date_of_birth, testperson, mail, education_status, gender)
VALUES (
    %s,
    pgp_sym_encrypt(%s, %s), -- Name verschlüsseln
    pgp_sym_encrypt(%s, %s), -- Nachname verschlüsseln
    %s,
    %s,
    pgp_sym_encrypt(%s, %s), -- E-Mail verschlüsseln
    %s,  -- Bildungsstatus
    %s   -- Geschlecht
)
ON CONFLICT (patient_id)
DO UPDATE SET
    name = pgp_sym_encrypt(EXCLUDED.name, %s),
    surname = pgp_sym_encrypt(EXCLUDED.surname, %s),
    date_of_birth = EXCLUDED.date_of_birth,
    testperson = EXCLUDED.testperson,
    mail = pgp_sym_encrypt(EXCLUDED.mail, %s),
    education_status = EXCLUDED.education_status,
    gender = EXCLUDED.gender,
    updated_at = now();
"""


# 03.01.2025
# INSERT_OR_UPDATE_PARTICIPANT = """
# INSERT INTO pradisy_participants (patient_id, name, surname, date_of_birth, testperson, mail)
# VALUES (
#     %s,
#     pgp_sym_encrypt(%s, %s), -- Name verschlüsseln
#     pgp_sym_encrypt(%s, %s), -- Nachname verschlüsseln
#     %s,
#     %s,
#     pgp_sym_encrypt(%s, %s) -- E-Mail verschlüsseln
# )
# ON CONFLICT (patient_id)
# DO UPDATE SET
#     name = pgp_sym_encrypt(EXCLUDED.name, %s),
#     surname = pgp_sym_encrypt(EXCLUDED.surname, %s),
#     date_of_birth = EXCLUDED.date_of_birth,
#     testperson = EXCLUDED.testperson,
#     mail = pgp_sym_encrypt(EXCLUDED.mail, %s),
#     updated_at = now();
# """

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

def add_participant_to_limesurvey(participant_id):
    """Fügt einen Teilnehmer mit nur der `participant_id` zur LimeSurvey-CPDB hinzu."""
    session_key = get_session_key()
    try:
        participant = {
            "participant_id": participant_id,
            "blacklisted": "N",
            "language": "",
            "cock": "NO" # JUST EXAMPLE OF ADDITIONAL VISIBLE ATTRIBUTES
            # "attributes": {
            #     "date_of_birth": "1990-01-01",
            #     "cock": "NO"
            # }
        }

        response = import_participant(session_key, participant)
        result = response.get("result", {})
        error = response.get("error")

        if error:
            print(f"Fehler beim Hinzufügen von Teilnehmer {participant_id} zu LimeSurvey: {error}")
        elif result.get("ImportCount", 0) > 0:
            print(f"Teilnehmer {participant_id} wurde erfolgreich zu LimeSurvey hinzugefügt.")
        elif result.get("UpdateCount", 0) > 0:
            print(f"Teilnehmer {participant_id} wurde erfolgreich in LimeSurvey aktualisiert.")
        else:
            print(f"Unbekanntes Ergebnis beim Hinzufügen von Teilnehmer {participant_id} zu LimeSurvey: {response}")
    except Exception as e:
        print(f"Fehler beim Hinzufügen von Teilnehmer {participant_id} zu LimeSurvey: {e}")
    finally:
        release_session_key(session_key)

def get_participant_from_cpdb(session_key, participant_id):
    """
    Holt einen Teilnehmer aus der zentralen Teilnehmerdatenbank (CPDB).
    
    Args:
        session_key (str): Der API-Session-Key.
        participant_id (str): Die UUID des Teilnehmers.
        
    Returns:
        dict: Die Teilnehmerdaten, falls gefunden.
    """
    payload = {
        "method": "cpd_get_participants",
        "params": [
            session_key,
            {
                "participant_id": participant_id
            }
        ],
        "id": 1
    }
    headers = {"content-type": "application/json"}
    response = requests.post(LIMESURVEY_URL, data=json.dumps(payload), headers=headers)
    response.raise_for_status()
    result = response.json().get("result")
    if result:
        return result[0]  # Es wird eine Liste zurückgegeben
    else:
        raise ValueError(f"Teilnehmer mit ID {participant_id} nicht gefunden.")


# 03.01.2025
# def add_participant_to_limesurvey(participant_id):
#     """Fügt einen Teilnehmer mit nur der `participant_id` zur LimeSurvey-CPDB hinzu."""
#     session_key = get_session_key()
#     try:
#         participant = {
#             "participant_id": participant_id,
#             "blacklisted": "N",
#             "language": ""
#         }

#         response = import_participant(session_key, participant)
#         if response.get("status") == "success":
#             print(f"Teilnehmer {participant_id} erfolgreich zu LimeSurvey hinzugefügt.")
#         else:
#             print(f"Fehler beim Hinzufügen von Teilnehmer {participant_id} zu LimeSurvey: {response}")
#     except Exception as e:
#         print(f"Fehler beim Hinzufügen von Teilnehmer {participant_id} zu LimeSurvey: {e}")
#     finally:
#         release_session_key(session_key)

def release_session_key(session_key):
    """Gibt den Session-Key frei."""
    payload = {
        "method": "release_session_key",
        "params": [session_key],
        "id": 1
    }
    headers = {"content-type": "application/json"}
    requests.post(LIMESURVEY_URL, data=json.dumps(payload), headers=headers)

# Funktionen für die PostgreSQL-Verwaltung
def connect_db():
    """Stellt eine Verbindung zur PostgreSQL-Datenbank her."""
    return psycopg2.connect(**DB_CONFIG)

def create_tables():
    """Erstellt die notwendigen Tabellen, falls sie nicht existieren."""
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(CREATE_PGCRYPTO_EXTENSION)
            cursor.execute(CREATE_PARTICIPANTS_TABLE)
            cursor.execute(CREATE_SURVEY_INSTANCES_TABLE)
        conn.commit()
        print("Tabellen wurden erfolgreich erstellt.")
    except Exception as e:
        conn.rollback()
        print(f"Fehler beim Erstellen der Tabellen: {e}")
    finally:
        conn.close()

def add_or_update_participant(patient_id, name, surname, date_of_birth, testperson, mail, education_status, gender, encryption_key):
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
                education_status,
                gender,
                encryption_key, encryption_key, encryption_key
            ))
        conn.commit()
        print(f"Teilnehmer {patient_id} erfolgreich hinzugefügt oder aktualisiert.")
    except Exception as e:
        conn.rollback()
        print(f"Fehler beim Hinzufügen/Aktualisieren: {e}")
    finally:
        conn.close()


# 03.01.2025
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
#         # Hinzufügen zu LimeSurvey
#         add_participant_to_limesurvey(patient_id)

#     except Exception as e:
#         conn.rollback()
#         print(f"Fehler beim Hinzufügen/Aktualisieren: {e}")
#     finally:
#         conn.close()

# List CPDB is not jet implemented
# def list_participants(encryption_key):
#     """
#     Listet alle Teilnehmer in der PostgreSQL-Datenbank auf und überprüft, 
#     ob sie in der LimeSurvey zentralen Teilnehmerdatenbank (CPDB) enthalten sind.
#     """
#     conn = connect_db()
#     try:
#         with conn.cursor() as cursor:
#             # Alle Teilnehmer aus der PostgreSQL-Datenbank abrufen
#             cursor.execute("""
#                 SELECT patient_id, pgp_sym_decrypt(name::bytea, %s), pgp_sym_decrypt(surname::bytea, %s), 
#                 date_of_birth, testperson, pgp_sym_decrypt(mail::bytea, %s) 
#                 FROM pradisy_participants
#             """, (encryption_key, encryption_key, encryption_key))
#             participants = cursor.fetchall()

#             # Session-Key von LimeSurvey abrufen
#             session_key = get_session_key()

#             print("PostgreSQL-Teilnehmer:")
#             for participant in participants:
#                 patient_id = participant[0]
#                 try:
#                     # Überprüfung in LimeSurvey CPDB
#                     cpdb_participant = get_participant_from_cpdb(session_key, patient_id)
#                     is_in_cpdb = True if cpdb_participant else False
#                 except ValueError:
#                     is_in_cpdb = False

#                 print(
#                     f"Patient ID: {patient_id}, Name: {participant[1]} {participant[2]}, "
#                     f"DOB: {participant[3]}, Testperson: {participant[4]}, "
#                     f"Mail: {participant[5]}, In LimeSurvey CPDB: {'Ja' if is_in_cpdb else 'Nein'}"
#                 )

#             # Session-Key freigeben
#             release_session_key(session_key)

#     except Exception as e:
#         print(f"Fehler beim Abrufen der Teilnehmer: {e}")
#     finally:
#         conn.close()


# 03.01.2025
def list_participants(encryption_key):
    """Listet alle Teilnehmer in der Tabelle `pradisy_participants` auf."""
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    patient_id, 
                    pgp_sym_decrypt(name::bytea, %s) AS name, 
                    pgp_sym_decrypt(surname::bytea, %s) AS surname, 
                    date_of_birth, 
                    testperson, 
                    pgp_sym_decrypt(mail::bytea, %s) AS mail 
                FROM pradisy_participants
            """, (encryption_key, encryption_key, encryption_key))
            participants = cursor.fetchall()
            for participant in participants:
                print(f"Patient ID: {participant[0]}, Name: {participant[1]} {participant[2]}, DOB: {participant[3]}, Testperson: {participant[4]}, Mail: {participant[5]}")
    except Exception as e:
        print(f"Fehler beim Abrufen der Teilnehmer: {e}")
    finally:
        conn.close()


# 03.01.2025
# def list_participants(encryption_key):
#     """Listet alle Teilnehmer in der Tabelle `pradisy_participants` auf."""
#     conn = connect_db()
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute("""
#                 SELECT 
#                     patient_id,
#                     pgp_sym_decrypt(name::bytea, %s) AS name,
#                     pgp_sym_decrypt(surname::bytea, %s) AS surname,
#                     date_of_birth,
#                     testperson,
#                     pgp_sym_decrypt(mail::bytea, %s) AS mail
#                 FROM pradisy_participants
#             """, (encryption_key, encryption_key, encryption_key))
#             participants = cursor.fetchall()
#             print("Teilnehmerliste:")
#             for participant in participants:
#                 print(f"Patient ID: {participant[0]}, Name: {participant[1]} {participant[2]}, DOB: {participant[3]}, Testperson: {participant[4]}, Mail: {participant[5]}")
#     except Exception as e:
#         print(f"Fehler beim Abrufen der Teilnehmer: {e}")
#     finally:
#         conn.close()

# ###USAGE###
# Nutzung
# 1. Tabellen erstellen
# python pradisy_add_participant.py --create-tables --encryption-key "sicherer_schluessel"
#
# 2. Teilnehmer hinzufügen
# python pradisy_add_participant.py --add-participant \
#   --patient-id "08bd93f6-0968-4260-8281-2a44f72a55fc" \
#   --name "Anna" --surname "Schmidt" \
#   --date-of-birth "1990-01-01" --testperson False \
#   --mail "anna.schmidt@example.com" \
#   --encryption-key "sicherer_schluessel"
#
# 3. Teilnehmer auflisten
# python pradisy_add_participant.py --list-participants --encryption-key "sicherer_schluessel"

# Main
if __name__ == "__main__":

    try:
        config = load_config()
        print("✅ Konfiguration erfolgreich geladen!")
    except Exception as e:
        print(f"❌ Fehler beim Laden der Konfiguration: {e}")
        sys.exit(1)  # Beende das Skript, wenn die Konfiguration fehlt


    parser = argparse.ArgumentParser(description="Verwalte die Tabellen in der PostgreSQL-Datenbank des Praxis Diagnostik Systems (PraDiSy).")
    parser.add_argument("--create-tables", action="store_true", help="Erstellt alle notwendigen Tabellen, falls sie fehlen.")
    parser.add_argument("--add-participant", action="store_true", help="Fügt einen neuen Teilnehmer hinzu oder aktualisiert vorhandene Daten.")
    parser.add_argument("--list-participants", action="store_true", help="Listet alle Teilnehmer auf.")
    parser.add_argument("--patient-id", type=str, help="Eindeutige ID des Teilnehmers (UUID).")
    parser.add_argument("--name", type=str, help="Vorname des Teilnehmers.")
    parser.add_argument("--surname", type=str, help="Nachname des Teilnehmers.")
    parser.add_argument("--date-of-birth", type=str, help="Geburtsdatum des Teilnehmers (YYYY-MM-DD).")
    parser.add_argument("--testperson", type=bool, default=False, help="Gibt an, ob die Person eine Testperson ist.")
    parser.add_argument("--mail", type=str, help="E-Mail-Adresse des Teilnehmers.")
    # parser.add_argument("--encryption-key", type=str, required=True, help="Verschlüsselungsschlüssel (erforderlich für Teilnehmer).")
    parser.add_argument("--encryption-key", type=str, help="Verschlüsselungsschlüssel (erforderlich für Teilnehmer).")
    parser.add_argument("--education-status", type=str, help="Bildungsstatus des Teilnehmers.")
    parser.add_argument("--gender", type=str, help="Geschlecht des Teilnehmers.")


    args = parser.parse_args()

    if args.create_tables:
        create_tables()
        print("Tabellen wurden erfolgreich erstellt.")

    if args.add_participant:
        if not all([args.name, args.surname, args.date_of_birth, args.mail, args.encryption_key]):
            print("Fehlende Parameter: `name`, `surname`, `date-of-birth`, `mail` und `encryption-key` sind erforderlich.")
        else:
            add_or_update_participant(
                patient_id=args.patient_id,
                name=args.name,
                surname=args.surname,
                date_of_birth=args.date_of_birth,
                testperson=args.testperson,
                mail=args.mail,
                education_status=args.education_status,
                gender=args.gender,
                encryption_key=args.encryption_key
            )
            # add_or_update_participant(
            #     patient_id=args.patient_id,
            #     name=args.name,
            #     surname=args.surname,
            #     date_of_birth=args.date_of_birth,
            #     testperson=args.testperson,
            #     mail=args.mail,
            #     encryption_key=args.encryption_key
            # )
            print(f"Teilnehmer {args.name} {args.surname} wurde hinzugefügt oder aktualisiert.")

    if args.list_participants:
        if not args.encryption_key:
            print("Der Verschlüsselungsschlüssel (`--encryption-key`) ist erforderlich, um Teilnehmer anzuzeigen.")
        else:
            list_participants(args.encryption_key)


    # 03.01.2025 222
    # if args.list_participants:
    #     list_participants()


    # 03.01.2025
    # if args.create_tables:
    #     create_tables()

    # if args.list_participants:
    #     list_participants(args.encryption_key)

    # if args.add_participant:
    #     if not all([args.patient_id, args.name, args.surname, args.date_of_birth, args.mail, args.encryption_key]):
    #         print("Fehlende Parameter: `patient-id`, `name`, `surname`, `date-of-birth`, `mail` und `encryption-key` sind erforderlich.")
    #     else:
    #         add_or_update_participant(
    #             patient_id=args.patient_id,
    #             name=args.name,
    #             surname=args.surname,
    #             date_of_birth=args.date_of_birth,
    #             testperson=args.testperson,
    #             mail=args.mail,
    #             encryption_key=args.encryption_key
    #         )
