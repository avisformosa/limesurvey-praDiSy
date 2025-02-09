import requests
import json

# API-Konfiguration Standard passwords
LIMESURVEY_URL = "http://limesurvey.ddev.site/index.php/admin/remotecontrol"
USERNAME = "admin"  # Admin-Benutzername
PASSWORD = "admin"  # Passwort

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

def list_participants(session_key, survey_id, start=0, limit=1000):
    """
    Ruft die Teilnehmer einer bestimmten Umfrage ab.
    
    Args:
        session_key (str): Der API-Session-Key.
        survey_id (str): Die ID der Umfrage.
        start (int): Der Offset für die Teilnehmerliste.
        limit (int): Die maximale Anzahl der Teilnehmer, die zurückgegeben werden.

    Returns:
        list: Eine Liste der Teilnehmer.
    """
    payload = {
        "method": "list_participants",
        "params": [session_key, survey_id, start, limit],
        "id": 1
    }
    headers = {"content-type": "application/json"}
    response = requests.post(LIMESURVEY_URL, data=json.dumps(payload), headers=headers)
    response.raise_for_status()
    return response.json()["result"]

def release_session_key(session_key):
    """Gibt den Session-Key frei."""
    payload = {
        "method": "release_session_key",
        "params": [session_key],
        "id": 1
    }
    headers = {"content-type": "application/json"}
    requests.post(LIMESURVEY_URL, data=json.dumps(payload), headers=headers)

if __name__ == "__main__":
    try:
        # Session-Key abrufen
        session_key = get_session_key()
        print(f"Session Key erhalten: {session_key}")

        # Survey-ID definieren
        survey_id = "312499"

        # Teilnehmerliste abrufen
        participants = list_participants(session_key, survey_id)
        print(f"Teilnehmer für Survey-ID {survey_id}:")
        
        # Nur die participant_id extrahieren und ausgeben
        for participant in participants:
            participant_info = participant.get("participant_info", {})
            participant_id = participant_info.get("participant_id", "Nicht verfügbar")
            print(f"Participant ID: {participant_id}")

        # HINZUFÜGEN EINES TEILNEHMERS IN DIE CPDB    

        # Teilnehmerdaten
        participant = {
            "email": "test@example.com",
            "firstname": "John",
            "lastname": "Doe",
            "participant_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
            "language": "",
            "blacklisted": "N",
            "attributes": {
                "testperson": "Y",
                "date_of_birth": "1990-01-01"
            }
        }
        result = import_participant(session_key, participant)
        print(f"Teilnehmer importiert: {result}")
        print(f"participant_id importiert: {participant["participant_id"]}")

    finally:
        # Session-Key freigeben
        release_session_key(session_key)
