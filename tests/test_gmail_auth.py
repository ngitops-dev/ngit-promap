import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive.readonly",
]

CREDENTIALS_FILE = "credentials/gmail-oauth-client.json"
TOKEN_FILE = "credentials/gmail-token.json"


def authenticate_gmail():
    creds = None

    # Load previously saved credentials
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    # If credentials don't exist or have expired
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    print("Gmail authentication successful!")
    print(f"Token saved to: {TOKEN_FILE}")


if __name__ == "__main__":
    authenticate_gmail()