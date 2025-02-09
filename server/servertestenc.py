import imaplib
import email

# IMAP-Konfiguration
IMAP_SERVER = 'imap.strato.de'
EMAIL_ACCOUNT = 'server@gemeinschaftspraxis-psychotherapie-erfurt.de'
password_variants = [
    'cAbhef-gekqer-1huvcy-&74Rtz',
    r'cAbhef-gekqer-1huvcy-&74Rtz',  # raw string
    'cAbhef-gekqer-1huvcy-\&74Rtz',  # escaped &
    'cAbhef-gekqer-1huvcy-%2674Rtz',  # URL-encoded
]

for password in password_variants:
    try:
        print(f"Versuche Login mit Passwort: {password}")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
        mail.login(EMAIL_ACCOUNT, password)
        print("Login erfolgreich!")
        mail.select('inbox')
        status, email_ids = mail.search(None, 'ALL')
        email_ids = email_ids[0].split()

        for e_id in email_ids:
            status, data = mail.fetch(e_id, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            subject = msg['subject']
            print(f"Betreff: {subject}")

        mail.logout()
        break
    except imaplib.IMAP4.error as e:
        print(f"Fehler bei Login-Versuch mit Passwort: {password}. Fehler: {e}")
