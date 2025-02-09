import imaplib
import email
# import urllib.parse
import ssl

# IMAP-Konfiguration
# IMAP_SERVER = 'imap.strato.de'
EMAIL_ACCOUNT = 'server@gemeinschaftspraxis-psychotherapie-erfurt.de'
# PASSWORD = 'cAbhef-gekqer-1huvcy-&74Rtz'
# PASSWORD = 'cAbhef-gekqer-1huvcy-\&74Rtz'
# PASSWORD = 'cAbhef-gekqer-1huvcy-%2674Rtz'
PASSWORD = 'cAbhef-gekqer-1huvcy-74Rtz'

IMAP_SERVER = 'imap.strato.de'
### EMAIL_ACCOUNT = 'test@gemeinschaftspraxis-psychotherapie-erfurt.de'
# PASSWORD = 'testmail12'
## PASSWORD = 'test-mail-12'
import base64
context = ssl.create_default_context()


# encoded_password = urllib.parse.quote(PASSWORD)
# PASSWORD = r'cAbhef-gekqer-1huvcy-&74Rtz'
encoded_password = base64.b64encode(PASSWORD.encode()).decode()

imaplib.Debug = 4

# Verbinden mit dem IMAP-Server
# mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
# mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993, ssl_context=context)

# mail.starttls()

mail.login(EMAIL_ACCOUNT, PASSWORD)
mail.select('inbox')

# Suche nach allen E-Mails
status, email_ids = mail.search(None, 'ALL')
email_ids = email_ids[0].split()

# Durchsuche alle gefundenen E-Mails und gebe die Betreffzeilen aus
for e_id in email_ids:
    status, data = mail.fetch(e_id, '(RFC822)')
    raw_email = data[0][1]
    msg = email.message_from_bytes(raw_email)
    subject = msg['subject']
    print(f"Betreff: {subject}")

# Logout vom IMAP-Server
mail.logout()
