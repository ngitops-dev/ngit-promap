from datetime import datetime, timezone

from backend.repositories import fulfillments as fulfillment_store
from backend.repositories import registrations as registration_store
from backend.repositories.programs import get_cohort
from backend.services import gmail
from backend.utils.logging import get_logger

logger = get_logger(__name__)

PAYMENT_CONFIRMATION_TEMPLATE = """
Hello {full_name},

Your payment for {program_name} ({cohort_name}) has been confirmed!

Amount: {currency} {amount}

Join your participant community:
{whatsapp_link}

Welcome to the program!

Best regards,
NGiT Academy
"""


async def fulfill_registration(registration_id: str, payment_reference: str) -> None:
    if fulfillment_store.is_already_fulfilled(registration_id):
        logger.info("Already fulfilled | registration_id=%s", registration_id)
        return

    registration = registration_store.find_by_id(registration_id)
    if not registration:
        logger.error("Registration not found | registration_id=%s", registration_id)
        return

    cohort = get_cohort(registration.cohort_id)
    program = get_program(registration.program_id) if registration.program_id else None

    now = datetime.now(timezone.utc).isoformat()
    fulfillment_id = f"FUL-{registration_id}"

    fulfillment_store.create_fulfillment({
        "fulfillment_id": fulfillment_id,
        "registration_id": registration_id,
        "payment_id": f"PAY-{payment_reference}",
        "email_status": "PROCESSING",
        "whatsapp_link_status": "PENDING",
        "status": "PROCESSING",
        "fulfilled_at": "",
        "error_message": "",
    })

    registration_store.update_fulfillment_status(registration_id, "PROCESSING")

    program_name = program.program_name if program else registration.program_id
    cohort_name = cohort.cohort_name if cohort else registration.cohort_id
    whatsapp_link = cohort.whatsapp_link if cohort else ""
    amount = cohort.expected_amount if cohort else ""
    currency = cohort.currency if cohort else "NGN"

    subject = f"Your {program_name} Payment is Confirmed"
    body = PAYMENT_CONFIRMATION_TEMPLATE.format(
        full_name=registration.full_name,
        program_name=program_name,
        cohort_name=cohort_name,
        currency=currency,
        amount=amount,
        whatsapp_link=whatsapp_link,
    )

    email_sent = gmail.send_email(registration.email, subject, body)

    if email_sent:
        fulfillment_store.update_fulfillment(fulfillment_id, {
            "email_status": "SENT",
            "whatsapp_link_status": "SENT" if whatsapp_link else "NO_LINK",
            "status": "COMPLETED",
            "fulfilled_at": now,
        })
        registration_store.update_fulfillment_status(registration_id, "COMPLETED")
        logger.info(
            "Fulfillment completed | registration_id=%s | email=%s",
            registration_id,
            registration.email,
        )
    else:
        fulfillment_store.update_fulfillment(fulfillment_id, {
            "email_status": "FAILED",
            "status": "FAILED",
            "error_message": "Email sending failed",
        })
        registration_store.update_fulfillment_status(registration_id, "FAILED")
        logger.error(
            "Fulfillment email failed | registration_id=%s",
            registration_id,
        )


async def resend_confirmation(
    registration_id: str,
    email: str | None = None,
    whatsapp_link: str | None = None,
) -> bool:
    registration = registration_store.find_by_id(registration_id)
    if not registration:
        return False

    cohort = get_cohort(registration.cohort_id)
    program = get_program(registration.program_id) if registration.program_id else None

    program_name = program.program_name if program else registration.program_id
    cohort_name = cohort.cohort_name if cohort else registration.cohort_id
    default_whatsapp = cohort.whatsapp_link if cohort else ""
    amount = cohort.expected_amount if cohort else ""
    currency = cohort.currency if cohort else "NGN"

    final_whatsapp = whatsapp_link if whatsapp_link else default_whatsapp
    recipient = email if email else registration.email

    subject = f"Your {program_name} Payment is Confirmed"
    body = PAYMENT_CONFIRMATION_TEMPLATE.format(
        full_name=registration.full_name,
        program_name=program_name,
        cohort_name=cohort_name,
        currency=currency,
        amount=amount,
        whatsapp_link=final_whatsapp,
    )

    return gmail.send_email(recipient, subject, body)
