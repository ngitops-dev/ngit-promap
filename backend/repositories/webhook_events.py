from typing import Any

from backend.repositories.google_sheets import append_row, find_row, find_rows
from backend.utils.logging import get_logger

logger = get_logger(__name__)

TAB = "WebhookEvents"


def log_event(data: dict[str, Any]) -> None:
    append_row(TAB, data)
    logger.info("Webhook event logged | event_type=%s", data.get("event_type"))


def event_exists(event_id: str) -> bool:
    return find_row(TAB, "event_id", event_id) is not None


def transaction_event_exists(transaction_reference: str) -> bool:
    rows = find_rows(TAB, "transaction_reference", transaction_reference)
    return any(r.get("status") == "PROCESSED" for r in rows)


def mark_processed(event_id: str) -> None:
    from backend.repositories.google_sheets import update_row

    update_row(TAB, "event_id", event_id, {"status": "PROCESSED"})
