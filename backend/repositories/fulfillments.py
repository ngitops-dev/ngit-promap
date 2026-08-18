from typing import Any

from backend.models.fulfillment import Fulfillment
from backend.repositories.google_sheets import (
    append_row,
    find_row,
    find_rows,
    update_row,
)
from backend.utils.logging import get_logger

logger = get_logger(__name__)

TAB = "Fulfillments"


def _row_to_fulfillment(row: dict[str, Any]) -> Fulfillment:
    return Fulfillment(
        **{k: v for k, v in row.items() if k in Fulfillment.model_fields}
    )


def find_by_registration(registration_id: str) -> Fulfillment | None:
    row = find_row(TAB, "registration_id", registration_id)
    return _row_to_fulfillment(row) if row else None


def find_by_id(fulfillment_id: str) -> Fulfillment | None:
    row = find_row(TAB, "fulfillment_id", fulfillment_id)
    return _row_to_fulfillment(row) if row else None


def create_fulfillment(data: dict[str, Any]) -> Fulfillment:
    append_row(TAB, data)
    return Fulfillment(**data)


def update_fulfillment(fulfillment_id: str, data: dict[str, Any]) -> bool:
    return update_row(TAB, "fulfillment_id", fulfillment_id, data)


def is_already_fulfilled(registration_id: str) -> bool:
    f = find_by_registration(registration_id)
    return f is not None and f.status == "COMPLETED"
