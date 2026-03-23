import smtplib
import os
from email.mime.text import MIMEText
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def send_workflow_notification(recipient_email: str, subject: str, message: str) -> str:
    """
    Sends an automated email notification via SMTP.
    Used for success confirmations or requesting missing documents.
    """
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    server = os.getenv("SMTP_SERVER")
    port = int(os.getenv("SMTP_PORT", 587))

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()  # Secure the connection
            smtp.login(sender, password)
            smtp.send_message(msg)
        return f"✅ Email successfully sent to {recipient_email}"
    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"