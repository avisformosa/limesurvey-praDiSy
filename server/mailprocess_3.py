import imaplib
import email
from email.header import decode_header
import re

# Login to IMAP server
# username = "diagnostik@gemeinschaftspraxis-psychotherapie-erfurt.de"
# password = "#AspergesMeHysopoEtMundabor#"
# imap_server = "imap.strato.de"
imap_server = "imap.strato.de"
username = "pradisy@gemeinschaftspraxis-psychotherapie-erfurt.de"
password = "#RorateCaeliDesuper#3"

# Debugging-Flag
DEBUG = True

# Regex für das erwartete Format
subject_pattern = re.compile(
    r"DIAG(?P<diag_id>\d+)PARTICIPANT(?P<participant_id>[a-f0-9\-]+)DATE(?P<date>\d{4}-\d{2}-\d{2})TIME(?P<time>\d{2}:\d{2}:\d{2})"
)

def parse_subject(subject):
    """Validiert den Betreff und extrahiert die Informationen."""
    match = subject_pattern.match(subject)
    if match:
        return match.groupdict()  # Gibt die extrahierten Felder als Dictionary zurück
    return None

def check_mail():
    """Prüft neue E-Mails und extrahiert Informationen aus dem Betreff."""
    try:
        # Verbindung zum Server
        mail = imaplib.IMAP4_SSL(imap_server, 993)
        mail.login(username, password)
        mail.select("inbox")

        # Suche nach ungelesenen E-Mails
        status, messages = mail.search(None, "UNSEEN")
        mail_ids = messages[0].split()

        for mail_id in mail_ids:
            # Abrufen der E-Mail
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode()  # Betreff decodieren
                    sender = msg.get("From")
                    
                    print(f"New email from {sender}: {subject}")
                    
                    # Validieren und extrahieren
                    parsed_data = parse_subject(subject)
                    if parsed_data:
                        print("Valid subject format!")
                        
                        # Debugging-Ausgabe
                        if DEBUG:
                            print("DEBUG: Extracted Variables")
                            for key, value in parsed_data.items():
                                print(f"  {key}: {value}")
                        
                        # Hier können Sie die extrahierten Daten weiterverarbeiten
                    else:
                        print("Invalid subject format.")
        
        mail.logout()

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function
check_mail()
