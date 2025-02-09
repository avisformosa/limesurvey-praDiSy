import imaplib
import email
import os
import subprocess
import re

# IMAP-Konfiguration
IMAP_SERVER = 'imap.strato.de'
# EMAIL_ACCOUNT = 'server@gemeinschaftspraxis-psychotherapie-erfurt.de'
EMAIL_ACCOUNT = 'diagnostik@gemeinschaftspraxis-psychotherapie-erfurt.de'
# PASSWORD = 'cAbhef-gekqer-1huvcy-&74Rtz'
PASSWORD = '#AspergesMeHysopoEtMundabor#'

# Pfad zum Speichern der CSV-Anhänge
ATTACHMENT_DIR = 'attachments'

# Verbinden mit dem IMAP-Server
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_ACCOUNT, PASSWORD)
mail.select('inbox')

# # Suche nach passenden E-Mails
# status, email_ids = mail.search(None, '(UNSEEN SUBJECT "DIAG")')
# email_ids = email_ids[0].split()

# # Durchsuche alle gefundenen E-Mails
# for e_id in email_ids:
#     status, data = mail.fetch(e_id, '(RFC822)')
#     raw_email = data[0][1]
#     msg = email.message_from_bytes(raw_email)

#     # Überprüfe Betreff auf das Muster
#     subject = msg['subject']
#     pattern = r'DIAG(?P<surveyId>\d+)PARTICIPANT(?P<participantId>[a-f0-9\-]+)DATE(?P<date>\d{4}-\d{2}-\d{2})TIME(?P<time>\d{2}:\d{2}:\d{2})'
#     match = re.match(pattern, subject)

#     if match:
#         # Speichere die CSV-Anhänge
#         for part in msg.walk():
#             if part.get_content_maintype() == 'multipart':
#                 continue
#             if part.get('Content-Disposition') is None:
#                 continue

#             filename = part.get_filename()
#             if filename.endswith('.csv'):
#                 filepath = os.path.join(ATTACHMENT_DIR, filename)
#                 with open(filepath, 'wb') as f:
#                     f.write(part.get_payload(decode=True))

#                 # R-Skript zur Verarbeitung aufrufen
#                 # r_script_path = "/path/to/your_script.R"
#                 # subprocess.run(["Rscript", r_script_path, filepath], check=True)

# # Logout vom IMAP-Server
# mail.logout()

