import psycopg2
import argparse

# PostgreSQL-Konfiguration
DB_CONFIG = {
    "dbname": "diagnostik",
    "user": "diagnostik_user",
    "password": "#IntroiboAdAltareDeiAdDeumQuiLaetificatAnimaMea#",
    "host": "localhost",
    "port": 5432
}

# Tabellenstruktur für `pradisy_participants`
CREATE_PARTICIPANTS_TABLE = """
CREATE TABLE IF NOT EXISTS pradisy_participants (
    patient_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    testperson BOOLEAN DEFAULT FALSE,
    mail VARCHAR(150) UNIQUE NOT NULL,
    survey_reference INTEGER REFERENCES pradisy_surveys(survey_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);
"""

INSERT_OR_UPDATE_PARTICIPANT = """
INSERT INTO pradisy_participants (name, surname, date_of_birth, testperson, mail, survey_reference)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (mail)
DO UPDATE SET
    name = EXCLUDED.name,
    surname = EXCLUDED.surname,
    date_of_birth = EXCLUDED.date_of_birth,
    testperson = EXCLUDED.testperson,
    survey_reference = EXCLUDED.survey_reference,
    updated_at = now();
"""

def connect_db():
    """Stellt eine Verbindung zur PostgreSQL-Datenbank her."""
    return psycopg2.connect(**DB_CONFIG)

def create_table():
    """Erstellt die Tabelle `pradisy_participants`, falls sie nicht existiert."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(CREATE_PARTICIPANTS_TABLE)
    conn.commit()
    conn.close()

def add_or_update_participant(name, surname, date_of_birth, testperson, mail, survey_reference):
    """Fügt einen neuen Teilnehmer hinzu oder aktualisiert vorhandene Daten basierend auf der Mail."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(INSERT_OR_UPDATE_PARTICIPANT, (name, surname, date_of_birth, testperson, mail, survey_reference))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verwalte die Tabelle `pradisy_participants` in der PostgreSQL-Datenbank des Praxis Diaagnsotik Systems (PraDiSy).")
    parser.add_argument("--create-table", action="store_true", help="Erstellt die Tabelle `pradisy_participants`.")
    parser.add_argument("--add-participant", action="store_true", help="Fügt einen neuen Teilnehmer hinzu oder aktualisiert vorhandene Daten.")
    parser.add_argument("--name", type=str, help="Vorname des Teilnehmers.")
    parser.add_argument("--surname", type=str, help="Nachname des Teilnehmers.")
    parser.add_argument("--date-of-birth", type=str, help="Geburtsdatum des Teilnehmers (YYYY-MM-DD).")
    parser.add_argument("--testperson", type=bool, default=False, help="Gibt an, ob die Person eine Testperson ist.")
    parser.add_argument("--mail", type=str, help="E-Mail-Adresse des Teilnehmers.")
    parser.add_argument("--survey-reference", type=int, default=None, help="Referenz auf die Survey-Tabelle.")

    args = parser.parse_args()

    if args.create_table:
        create_table()
        print("Tabelle `pradisy_participants` wurde erstellt (falls sie nicht existierte).")

    if args.add_participant:
        if not all([args.name, args.surname, args.date_of_birth, args.mail]):
            print("Fehlende Parameter: `name`, `surname`, `date-of-birth` und `mail` sind erforderlich.")
        else:
            add_or_update_participant(
                name=args.name,
                surname=args.surname,
                date_of_birth=args.date_of_birth,
                testperson=args.testperson,
                mail=args.mail,
                survey_reference=args.survey_reference
            )
            print(f"Teilnehmer {args.name} {args.surname} wurde hinzugefügt oder aktualisiert.")

def import_participants_from_csv(csv_file):
    """Importiert mehrere Teilnehmer aus einer CSV-Datei."""
    conn = connect_db()
    with conn.cursor() as cursor:
        data = pd.read_csv(csv_file)
        for _, row in data.iterrows():
            cursor.execute(INSERT_OR_UPDATE_PARTICIPANT, (
                row['name'],
                row['surname'],
                row['date_of_birth'],
                row['testperson'],
                row['mail'],
                row['survey_reference']
            ))
    conn.commit()
    conn.close()
