from fastapi import APIRouter, Header, Request

from backend.config import settings
from backend.repositories.webhook_events import event_exists, log_event, mark_processed
from backend.services.paystack import verify_transaction
from backend.utils.logging import get_logger
from backend.utils.security import verify_paystack_signature

logger = get_logger(__name__)

router = APIRouter()


@router.post("/webhooks/paystack")
async def paystack_webhook(
    request: Request,
    x_paystack_signature: str = Header(default=""),
):
    body = await request.body()

    if not verify_paystack_signature(body, x_paystack_signature, settings.PAYSTACK_WEBHOOK_SECRET):
        logger.warning("Invalid Paystack signature")
        return {"status": "error", "message": "Invalid signature"}

    import json
    try:
        event = json.loads(body)
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON"}

    event_type = event.get("event", "")
    event_id = event.get("id", "")
    data = event.get("data", {})
    reference = data.get("reference", "")

    logger.info(
        "Webhook received | event_type=%s | event_id=%s | reference=%s | full_payload=%s",
        event_type, event_id, reference, event,
    )

    log_event({
        "event_id": event_id,
        "event_type": event_type,
        "transaction_reference": reference,
        "received_at": "",
        "processed_at": "",
        "status": "RECEIVED",
        "error_message": "",
        "payload": json.dumps(event),
    })

    if event_type != "charge.success":
        logger.info("Ignoring event type=%s", event_type)
        return {"status": "received"}

    if event_id and event_exists(event_id):
        logger.info("Duplicate event_id=%s", event_id)
        return {"status": "received"}

    tx_data = verify_transaction(reference)
    if not tx_data:
        logger.error("Transaction verification failed | reference=%s", reference)
        return {"status": "error", "message": "Verification failed"}

    from backend.services.payment_service import process_verified_payment
    await process_verified_payment(reference, tx_data)

    if event_id:
        mark_processed(event_id)

    return {"status": "received"}
