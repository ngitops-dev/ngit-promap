from fastapi import APIRouter, HTTPException

from backend.repositories import payments as payment_store
from backend.services.paystack import verify_transaction
from backend.utils.logging import get_logger
from datetime import datetime, timezone

logger = get_logger(__name__)

router = APIRouter()


@router.get("/payments")
async def list_payments(
    status: str | None = None,
    program_id: str | None = None,
):
    payments = payment_store.get_payments()
    if status:
        payments = [p for p in payments if p.status == status]
    if program_id:
        payments = [p for p in payments if p.program_id == program_id]
    return [p.model_dump() for p in payments]


@router.get("/payments/{payment_id}")
async def get_payment(payment_id: str):
    payment = payment_store.find_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment.model_dump()


@router.post("/payments/{reference}/verify")
async def verify_payment(reference: str):
    tx_data = verify_transaction(reference)
    if not tx_data:
        raise HTTPException(status_code=400, detail="Transaction verification failed")

    tx_status = tx_data.get("status", "")
    amount = tx_data.get("amount", 0)
    currency = tx_data.get("currency", "")

    existing = payment_store.find_by_reference(reference)
    now = datetime.now(timezone.utc).isoformat()

    if existing:
        payment_store.update_payment(reference, {
            "status": "PAID" if tx_status == "success" else "FAILED",
            "verified_at": now,
            "updated_at": now,
        })
    else:
        payment_store.create_payment({
            "payment_id": f"PAY-{reference}",
            "registration_id": "",
            "program_id": "",
            "cohort_id": "",
            "transaction_reference": reference,
            "amount": str(amount),
            "currency": currency,
            "status": "PAID" if tx_status == "success" else "FAILED",
            "gateway": "paystack",
            "paid_at": tx_data.get("paid_at", ""),
            "verified_at": now,
            "created_at": now,
            "updated_at": now,
        })

    from backend.repositories import registrations as reg_store
    reg = reg_store.find_by_reference(reference)
    if reg and tx_status == "success":
        reg_store.update_payment_status(reg.registration_id, "PAID", reference)
        from backend.services.fulfillment import fulfill_registration
        await fulfill_registration(reg.registration_id, reference)

    return {
        "status": "verified" if tx_status == "success" else "failed",
        "reference": reference,
        "amount": amount,
        "currency": currency,
    }
