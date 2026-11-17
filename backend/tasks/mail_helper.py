import os
import json
import smtplib
import urllib.request
from datetime import datetime
from email.mime.text import MIMEText

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTBOX = os.path.join(BASE_DIR, "outbox")

SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "1025"))  # MailHog default port
GCHAT_WEBHOOK = os.environ.get("GCHAT_WEBHOOK_URL")  # optional Google Chat webhook


def send_mail(to, subject, html):
    """Send an email using a local SMTP server (e.g. MailHog).
    A copy is always saved in backend/outbox so it can be shown in the demo even without SMTP."""
    os.makedirs(OUTBOX, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    with open(os.path.join(OUTBOX, f"{stamp}_{to}.html"), "w", encoding="utf-8") as f:
        f.write(f"<!-- To: {to} | Subject: {subject} -->\n{html}")

    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = "TrekMate <no-reply@trekmate.local>"
    msg["To"] = to
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=5) as server:
            server.send_message(msg)
        print("Mail sent to", to)
    except Exception as e:
        print("SMTP server not available, mail saved in outbox only:", e)


def send_gchat(text):
    """Send a message to a Google Chat space using its webhook URL (if configured)."""
    if not GCHAT_WEBHOOK:
        return
    try:
        req = urllib.request.Request(
            GCHAT_WEBHOOK,
            data=json.dumps({"text": text}).encode(),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print("Google Chat webhook failed:", e)