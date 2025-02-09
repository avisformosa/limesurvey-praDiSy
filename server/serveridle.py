from imapclient import IMAPClient
import time

IMAP_SERVER = 'imap.strato.de'
EMAIL_ACCOUNT = 'server@gemeinschaftspraxis-psychotherapie-erfurt.de'
PASSWORD = 'cAbhef-gekqer-1huvcy-74Rtz'

with IMAPClient(IMAP_SERVER, ssl=True) as server:
    server.login(EMAIL_ACCOUNT, PASSWORD)
    server.select_folder('INBOX')

    while True:
        server.idle()
        print("Warte auf neue E-Mails...")
        responses = server.idle_check(timeout=300)
        if responses:
            print("Neue E-Mail empfangen!")
            # Hier kannst du deine Verarbeitung der neuen E-Mails vornehmen
        server.idle_done()
