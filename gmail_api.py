import os
import base64
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]

TOKEN_FILE = "credentials/token.json"
CLIENT_SECRET = "credentials/client_secret.json"


def gmail_login():
    creds = None

    # Load saved token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If token missing or invalid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET):
                raise FileNotFoundError(
                    "client_secret.json not found. Put it inside credentials/ folder."
                )

            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token
        os.makedirs("credentials", exist_ok=True)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service


def get_latest_emails(service, max_results=5):
    results = service.users().messages().list(userId="me", maxResults=max_results).execute()
    messages = results.get("messages", [])

    email_list = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()

        headers = msg_data["payload"].get("headers", [])

        subject = "No Subject"
        sender = "Unknown Sender"

        for h in headers:
            if h["name"].lower() == "subject":
                subject = h["value"]
            if h["name"].lower() == "from":
                sender = h["value"]

        snippet = msg_data.get("snippet", "")

        email_list.append({
            "id": msg["id"],
            "from": sender,
            "subject": subject,
            "snippet": snippet
        })

    return email_list


def send_email(service, to_email, subject, body_text):
    message = EmailMessage()
    message.set_content(body_text)

    message["To"] = to_email
    message["From"] = "me"
    message["Subject"] = subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    send_message = {"raw": encoded_message}

    service.users().messages().send(userId="me", body=send_message).execute()
    return True
