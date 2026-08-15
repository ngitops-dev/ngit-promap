import json

from google.oauth2 import service_account
from googleapiclient.discovery import build

from backend.config import settings
from backend.utils.logging import get_logger

logger = get_logger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive.readonly",
]


def get_credentials() -> service_account.Credentials:
    if not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON is not configured")

    info = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
    return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)


def get_sheets_service():
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)


def get_gmail_service():
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)
