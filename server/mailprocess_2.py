import imaplib
import email
from email.header import decode_header

# Login to IMAP server
username = "diagnostik@gemeinschaftspraxis-psychotherapie-erfurt.de"
password = "#AspergesMeHysopoEtMundabor#"
imap_server = "imap.strato.de"

# IMAP-Konfiguration
# IMAP_SERVER = 'imap.strato.de'
# EMAIL_ACCOUNT = 'diagnostik@gemeinschaftspraxis-psychotherapie-erfurt.de'
# PASSWORD = '#AspergesMeHysopoEtMundabor#'

def check_mail():
    # Connect to the server
    # mail = imaplib.IMAP4_SSL(imap_server)
    mail = imaplib.IMAP4_SSL(imap_server, 993)
    # wirft erstmal einen ganzen Arsch voll Fehler!!! -> Little Snitch!!!
    ### mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(username, password)
    mail.select('inbox')

    # mail.login(username, password)
    # mail.select("inbox")

    # # Search for unseen emails
    status, messages = mail.search(None, 'UNSEEN')
    mail_ids = messages[0].split()

    for mail_id in mail_ids:
        # Fetch the email
        status, msg_data = mail.fetch(mail_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = decode_header(msg["Subject"])[0][0]
                sender = msg.get("From")
                
                print(f"New email from {sender}: {subject}")
                
                # Process the email content or attachments here

    mail.logout()

# Run the function (e.g., with a scheduler like cron)
check_mail()




