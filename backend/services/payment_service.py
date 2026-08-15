from datetime import datetime, timezone

from backend.repositories import fulfillments as fulfillment_store
from backend.repositories import payments as payment_store
from backend.repositories import registrations as registration_store
from backend.repositories.programs import get_cohort, get_program
from backend.utils.logging import get_logger

logger = get_logger(__name__)


async def process_verified_payment(reference: str, tx_data: dict) -> None:
    amount = tx_data.get("amount", 0)
    currency = tx_data.get("currency", "")
    status = tx_data.get("status", "")
    paid_at = tx_data.get("paid_at", "")
    customer_email = tx_data.get("customer", {}).get("email", "")

    if status != "success":
        logger.info("Transaction not success | reference=%s | status=%s", reference, status)
        return

    if payment_store.reference_exists(reference):
        logger.info("Duplicate payment | reference=%s", reference)
        return

    registration = registration_store.find_by_reference(reference)
    if not registration and customer_email:
        matches = registration_store.find_by_email(customer_email)
        if matches:
            registration = matches[0]

    if not registration:
        logger.warning("No registration found | reference=%s", reference)
        _create_unmatched_payment(reference, amount, currency, paid_at, tx_data)
        return

    cohort = get_cohort(registration.cohort_id)
    if not cohort:
        logger.warning("No cohort found | cohort_id=%s", registration.cohort_id)
        registration_store.update_payment_status(
            registration.registration_id, "MANUAL_REVIEW"
        )
        return

    expected_amount = int(cohort.expected_amount) if cohort.expected_amount else 0
    expected_currency = cohort.currency or "NGN"

    if int(amount) != expected_amount:
        logger.warning(
            "Amount mismatch | reference=%s | paid=%s expected=%s",
            reference, amount, expected_amount,
        )
        registration_store.update_payment_status(
            registration.registration_id, "MANUAL_REVIEW"
        )
        _create_payment_record(
            registration, reference, amount, currency, "MANUAL_REVIEW", paid_at, tx_data
        )
        return

    if currency.upper() != expected_currency.upper():
        logger.warning(
            "Currency mismatch | reference=%s | paid=%s expected=%s",
            reference, currency, expected_currency,
        )
        registration_store.update_payment_status(
            registration.registration_id, "MANUAL_REVIEW"
        )
        _create_payment_record(
            registration, reference, amount, currency, "MANUAL_REVIEW", paid_at, tx_data
        )
        return

    registration_store.update_payment_status(
        registration.registration_id, "PAID", reference
    )
    _create_payment_record(
        registration, reference, amount, currency, "PAID", paid_at, tx_data
    )

    from backend.services.fulfillment import fulfill_registration
    await fulfill_registration(registration.registration_id, reference)


def _create_payment_record(
    registration, reference, amount, currency, status, paid_at, tx_data
):
    now = datetime.now(timezone.utc).isoformat()
    payment_store.create_payment({
        "payment_id": f"PAY-{reference}",
        "registration_id": registration.registration_id,
        "program_id": registration.program_id,
        "cohort_id": registration.cohort_id,
        "transaction_reference": reference,
        "amount": str(amount),
        "currency": currency,
        "status": status,
        "gateway": "paystack",
        "paid_at": paid_at,
        "verified_at": now,
        "created_at": now,
        "updated_at": now,
    })


def _create_unmatched_payment(reference, amount, currency, paid_at, tx_data):
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    customer_email = tx_data.get("customer", {}).get("email", "")
    payment_store.create_payment({
        "payment_id": f"PAY-{reference}",
        "registration_id": "",
        "program_id": "",
        "cohort_id": "",
        "transaction_reference": reference,
        "amount": str(amount),
        "currency": currency,
        "status": "MANUAL_REVIEW",
        "gateway": "paystack",
        "paid_at": paid_at,
        "verified_at": now,
        "created_at": now,
        "updated_at": now,
    })
    logger.warning("Unmatched payment created | reference=%s | email=%s", reference, customer_email)
