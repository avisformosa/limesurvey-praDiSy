import imaplib
import email
from email.header import decode_header

# IMAP-Server-Konfiguration
IMAP_SERVER = "imap.strato.de"
USERNAME = "pradisy@gemeinschaftspraxis-psychotherapie-erfurt.de"
PASSWORD = "#RorateCaeliDesuper#3"

def decode_header_value(value):
    """Dekodiert den Header-Wert (z. B. Betreff oder Absender)."""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return value

def debug_mail_handling():
    """Debugging-Skript zur Überprüfung der IMAP-Verbindung und des Mailabrufs."""
    try:
        # Verbindung zum IMAP-Server herstellen
        print(f"Verbinde mit IMAP-Server: {IMAP_SERVER}")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(USERNAME, PASSWORD)
        print("Anmeldung erfolgreich.")
        
        # Postfach auswählen
        status, messages = mail.select("inbox")
        if status != "OK":
            print(f"Fehler beim Öffnen des Postfachs: {status}")
            return
        
        print(f"Postfach geöffnet. {messages[0].decode()} Nachrichten insgesamt.")
        
        # Suche nach ungelesenen Nachrichten
        status, unseen_messages = mail.search(None, "UNSEEN")
        if status != "OK":
            print(f"Fehler beim Suchen nach ungelesenen Nachrichten: {status}")
            return
        
        unseen_ids = unseen_messages[0].split()
        print(f"{len(unseen_ids)} ungelesene Nachrichten gefunden.")
        
        # Details der ungelesenen Nachrichten abrufen
        for mail_id in unseen_ids:
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            if status != "OK":
                print(f"Fehler beim Abrufen der Nachricht {mail_id}: {status}")
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = decode_header_value(decode_header(msg.get("Subject"))[0][0])
                    sender = decode_header_value(msg.get("From"))
                    
                    print(f"Nachricht {mail_id.decode()}:")
                    print(f"  Absender: {sender}")
                    print(f"  Betreff: {subject}")
        
        # Verbindung beenden
        mail.logout()
        print("Verbindung zum IMAP-Server beendet.")
    
    except Exception as e:
        print(f"Fehler aufgetreten: {e}")

if __name__ == "__main__":
    debug_mail_handling()
