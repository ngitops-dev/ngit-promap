from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_WEBHOOK_SECRET: str = ""
    PAYSTACK_BASE_URL: str = "https://api.paystack.co"

    GOOGLE_SHEET_ID: str = ""
    GOOGLE_SERVICE_ACCOUNT_JSON: str = ""
    GMAIL_SENDER: str = ""

    ADMIN_API_KEY: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
