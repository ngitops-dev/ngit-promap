import json
import os

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from backend.utils.logging import get_logger

logger = get_logger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive.readonly",
]

CREDENTIALS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "credentials")
OAUTH_TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "gmail-token.json")
SERVICE_ACCOUNT_FILE = os.path.join(CREDENTIALS_DIR, "google-service-account.json")


def _load_oauth_token() -> Credentials | None:
    token_json = os.environ.get("GOOGLE_OAUTH_TOKEN_JSON", "")
    if token_json:
        try:
            info = json.loads(token_json)
            return Credentials.from_authorized_user_info(info, SCOPES)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("Failed to parse GOOGLE_OAUTH_TOKEN_JSON | error=%s", e)

    if os.path.exists(OAUTH_TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(OAUTH_TOKEN_FILE, SCOPES)
            token_scopes = set(creds.scopes or [])
            required_scopes = set(SCOPES)
            if not required_scopes.issubset(token_scopes):
                logger.warning(
                    "OAuth token missing required scopes | token_scopes=%s required_scopes=%s",
                    token_scopes, required_scopes,
                )
                return None
            return creds
        except Exception as e:
            logger.warning("Failed to load local OAuth token | error=%s", e)

    return None


def _load_service_account():
    from google.oauth2 import service_account

    sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    if sa_json:
        try:
            info = json.loads(sa_json)
            return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("Failed to parse GOOGLE_SERVICE_ACCOUNT_JSON | error=%s", e)

    if os.path.exists(SERVICE_ACCOUNT_FILE):
        try:
            with open(SERVICE_ACCOUNT_FILE, "r") as f:
                info = json.load(f)
            return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        except Exception as e:
            logger.warning("Failed to load local service account | error=%s", e)

    return None


def get_credentials() -> Credentials:
    creds = _load_oauth_token()

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            logger.info("OAuth token refreshed")
        except Exception as e:
            logger.warning("OAuth token refresh failed | error=%s", e)
            creds = None

    if not creds or not creds.valid:
        creds = _load_service_account()

    if not creds:
        raise ValueError(
            "No valid credentials found. "
            "Set GOOGLE_OAUTH_TOKEN_JSON env var or place files in credentials/ folder."
        )

    return creds


def get_sheets_service():
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)


def get_gmail_service():
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)
