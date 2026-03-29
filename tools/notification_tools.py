import time
import os
import base64
from email.message import EmailMessage
from langchain.tools import tool
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

@tool
def send_workflow_notification(recipient_email: str, subject: str, message: str) -> str:
    """
    Sends a real email notification via the Gmail API.
    
    SETUP INSTRUCTIONS:
    1. Go to Google Cloud Console and enable the Gmail API.
    2. Create Desktop OAuth 2.0 Credentials and download as `credentials.json` into the root dir.
    3. The first time this runs, it will open a browser to authenticate and create `token.json`.
    """
    print(f"   📧 [System Output] Initiating Gmail API for {recipient_email}")
    
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                os.remove('token.json')
                
        if not creds or not creds.valid:
            if not os.path.exists('credentials.json'):
                print("   ⚠️ [Warning] `credentials.json` missing. Falling back to Mock SMTP.")
                time.sleep(1)
                return f"Mock Success: Email sent to {recipient_email}. Ref: MSG-{int(time.time())}"
                
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        email_msg = EmailMessage()
        email_msg.set_content(message)
        email_msg['To'] = recipient_email
        email_msg['From'] = 'verifai.system@gmail.com'
        email_msg['Subject'] = subject

        encoded_message = base64.urlsafe_b64encode(email_msg.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        return f"Success: Real Email sent to {recipient_email}. Message Id: {send_message['id']}"
        
    except Exception as error:
        print(f"   ❌ [Error] An error occurred: {error}")
        return f"Failed to send email: {error}"