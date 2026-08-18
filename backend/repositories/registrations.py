from typing import Any

from backend.models.registration import Registration
from backend.repositories.google_sheets import (
    append_row,
    find_row,
    find_rows,
    find_rows_by_multi,
    update_row,
)
from backend.utils.logging import get_logger

logger = get_logger(__name__)

TAB = "Registrations"


def _row_to_registration(row: dict[str, Any]) -> Registration:
    return Registration(
        **{k: v for k, v in row.items() if k in Registration.model_fields}
    )


def find_by_id(registration_id: str) -> Registration | None:
    row = find_row(TAB, "registration_id", registration_id)
    return _row_to_registration(row) if row else None


def find_by_email(email: str) -> list[Registration]:
    rows = find_rows(TAB, "email", email)
    return [_row_to_registration(r) for r in rows]


def find_by_reference(reference: str) -> Registration | None:
    row = find_row(TAB, "payment_reference", reference)
    return _row_to_registration(row) if row else None


def find_by_program_and_email(program_id: str, email: str) -> Registration | None:
    rows = find_rows_by_multi(TAB, {"program_id": program_id, "email": email})
    return _row_to_registration(rows[0]) if rows else None


def get_all_registrations() -> list[Registration]:
    from backend.repositories.google_sheets import read_sheet

    rows = read_sheet(TAB)
    return [_row_to_registration(r) for r in rows]


def get_registrations_by_program(program_id: str) -> list[Registration]:
    rows = find_rows(TAB, "program_id", program_id)
    return [_row_to_registration(r) for r in rows]


def get_registrations_by_cohort(cohort_id: str) -> list[Registration]:
    rows = find_rows(TAB, "cohort_id", cohort_id)
    return [_row_to_registration(r) for r in rows]


def update_payment_status(
    registration_id: str, payment_status: str, payment_reference: str = ""
) -> bool:
    data: dict[str, str] = {"payment_status": payment_status}
    if payment_reference:
        data["payment_reference"] = payment_reference
    return update_row(TAB, "registration_id", registration_id, data)


def update_fulfillment_status(registration_id: str, status: str) -> bool:
    return update_row(TAB, "registration_id", registration_id, {"fulfillment_status": status})


def create_registration(data: dict[str, Any]) -> Registration:
    append_row(TAB, data)
    return Registration(**data)
