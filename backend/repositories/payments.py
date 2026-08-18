from typing import Any

from backend.models.payment import Payment
from backend.repositories.google_sheets import (
    append_row,
    find_row,
    find_rows,
    read_sheet,
    update_row,
)
from backend.utils.logging import get_logger

logger = get_logger(__name__)

TAB = "Payments"


def _row_to_payment(row: dict[str, Any]) -> Payment:
    return Payment(**{k: v for k, v in row.items() if k in Payment.model_fields})


def find_by_reference(transaction_reference: str) -> Payment | None:
    row = find_row(TAB, "transaction_reference", transaction_reference)
    return _row_to_payment(row) if row else None


def find_by_id(payment_id: str) -> Payment | None:
    row = find_row(TAB, "payment_id", payment_id)
    return _row_to_payment(row) if row else None


def get_payments() -> list[Payment]:
    rows = read_sheet(TAB)
    return [_row_to_payment(r) for r in rows]


def get_payments_by_program(program_id: str) -> list[Payment]:
    rows = find_rows(TAB, "program_id", program_id)
    return [_row_to_payment(r) for r in rows]


def get_payments_by_status(status: str) -> list[Payment]:
    rows = find_rows(TAB, "status", status)
    return [_row_to_payment(r) for r in rows]


def create_payment(data: dict[str, Any]) -> Payment:
    append_row(TAB, data)
    return Payment(**data)


def update_payment(transaction_reference: str, data: dict[str, Any]) -> bool:
    return update_row(TAB, "transaction_reference", transaction_reference, data)


def reference_exists(transaction_reference: str) -> bool:
    return find_by_reference(transaction_reference) is not None
