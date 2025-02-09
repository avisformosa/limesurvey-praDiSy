from imapclient import IMAPClient
import email

# IMAP-Konfiguration
IMAP_SERVER = 'imap.strato.de'
EMAIL_ACCOUNT = 'server@gemeinschaftspraxis-psychotherapie-erfurt.de'
PASSWORD = 'cAbhef-gekqer-1huvcy-&74Rtz'

# Verbinden mit dem IMAP-Server
with IMAPClient(IMAP_SERVER, ssl=True) as server:
    server.login(EMAIL_ACCOUNT, PASSWORD)
    server.select_folder('INBOX')

    # Suche nach allen E-Mails
    messages = server.search('ALL')

    # Durchsuche alle gefundenen E-Mails und gebe die Betreffzeilen aus
    for msgid in messages:
        raw_message = server.fetch([msgid], ['RFC822'])[msgid][b'RFC822']
        msg = email.message_from_bytes(raw_message)
        subject = msg['subject']
        print(f"Betreff: {subject}")
