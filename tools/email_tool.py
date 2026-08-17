import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Dict, Any, List, Optional
from loguru import logger
from config import settings


def send_email(
    to_email: str,
    subject: str,
    body: str,
    attachments: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Send email with optional file attachments using SMTP."""
    sender_email = settings.smtp_email
    sender_password = settings.smtp_password

    if not sender_email or not sender_password:
        logger.warning("SMTP credentials missing in configuration.")
        return {
            "status": "error",
            "error": "SMTP credentials (SMTP_EMAIL, SMTP_PASSWORD) are missing in .env configuration."
        }

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        if attachments:
            for attach_path in attachments:
                path = Path(attach_path)
                if path.exists():
                    with open(path, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={path.name}")
                    msg.attach(part)
                else:
                    logger.warning(f"Attachment file not found: {attach_path}")

        server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        logger.info(f"Email sent successfully to {to_email} (Subject: '{subject}')")
        return {"status": "success", "to": to_email, "subject": subject}

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return {"status": "error", "error": str(e)}
