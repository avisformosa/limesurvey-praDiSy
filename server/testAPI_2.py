import requests
import json

# API-Konfiguration
LIMESURVEY_URL = "http://limesurvey.ddev.site/index.php/admin/remotecontrol"
USERNAME = "admin"  # Ersetzen Sie dies durch Ihren Admin-Benutzernamen
PASSWORD = "admin"  # Ersetzen Sie dies durch Ihr Passwort

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

def list_participants(session_key, survey_id):
    """Holt eine Liste der Teilnehmer einer bestimmten Umfrage."""
    payload = {
        "method": "list_participants",
        "params": [session_key, survey_id, 0, 1000],  # Offset 0, max 1000 Teilnehmer
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

def get_participant_properties(session_key, survey_id, token):
    """Holt die Attribute eines spezifischen Teilnehmers."""
    payload = {
        "method": "get_participant_properties",
        "params": [session_key, survey_id, token],
        "id": 1
    }
    headers = {"content-type": "application/json"}
    response = requests.post(LIMESURVEY_URL, data=json.dumps(payload), headers=headers)
    response.raise_for_status()
    return response.json()["result"]    

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


if __name__ == "__main__":
    try:
        # Session-Key abrufen
        session_key = get_session_key()

        print(f"session_key: {session_key}")

        # Teilnehmerdaten
        # participant = {
        #     "email": "test@example.com",
        #     "firstname": "John",
        #     "lastname": "Doe",
        #     "participant_id": "ddddddddd-d--d--d--d",
        #     "blacklisted": "N",
        #     "attributes": {
        #         "testperson": "Y",
        #         "date_of_birth": "1990-01-01"
        #     }
        # }

        participant = {
            "participant_id": "JoeNo",
            "blacklisted": "N",
            "language": ""
        }

        # Session-Key abrufen
        # session_key = get_session_key()
        # print(f"Session Key erhalten: {session_key}")

        # Survey-ID definieren
        survey_id = "769569"

        # Teilnehmerliste abrufen
        # participants = list_participants(session_key, survey_id)
        # print(f"Teilnehmer für Survey-ID {survey_id}:")
        # for participant in participants:
        #     print(participant)

         # Session-Key abrufen
        # session_key = get_session_key()
        # print(f"Session Key erhalten: {session_key}")

        # Survey-ID definieren
        survey_id = "769569"

        # Teilnehmerliste abrufen
        # participants = list_participants(session_key, survey_id)
        # print(f"Teilnehmer für Survey-ID {survey_id}:")

        # Weitere Attribute abrufen
        # for participant in participants:
        #     token = participant.get("token")  # Token für den Teilnehmer
        #     detailed_properties = get_participant_properties(session_key, survey_id, token)
        #     participant_id = detailed_properties.get("participant_id", "Nicht verfügbar")
        #     print(f"Token: {token}, Participant ID: {participant_id}, Details: {detailed_properties}")

        # Teilnehmer importieren ### works!!!
        # result = import_participant(session_key, participant)
        # print(f"Teilnehmer importiert: {result}")
        # print(f"participant_id importiert: {participant["participant_id"]}")
        get_participant_from_cpdb(session_key, participant["participant_id"])
        # Teilnehmer aus CPDB abrufen
        # participant_id = "ddddddddd-d--d--d--d"
        # participant = get_participant_from_cpdb(session_key, participant_id)
        # print(f"Teilnehmerdaten abgerufen: {participant}")
        

    finally:
        # Session-Key freigeben
        release_session_key(session_key)
