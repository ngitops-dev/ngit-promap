from fastapi import APIRouter, HTTPException, Query

from backend.repositories import registrations as reg_store
from backend.schemas.admin import RegistrationCreate, RegistrationUpdate, ResendConfirmationRequest
from backend.services.fulfillment import resend_confirmation
from backend.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/registrations")
async def list_registrations(
    program_id: str | None = None,
    cohort_id: str | None = None,
    payment_status: str | None = None,
    email: str | None = None,
):
    if program_id:
        regs = reg_store.get_registrations_by_program(program_id)
    elif cohort_id:
        regs = reg_store.get_registrations_by_cohort(cohort_id)
    else:
        regs = reg_store.get_all_registrations()

    if payment_status:
        regs = [r for r in regs if r.payment_status == payment_status]
    if email:
        regs = [r for r in regs if email.lower() in r.email.lower()]

    return [r.model_dump() for r in regs]


@router.get("/registrations/{registration_id}")
async def get_registration(registration_id: str):
    reg = reg_store.find_by_id(registration_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    return reg.model_dump()


@router.post("/registrations")
async def create_registration(data: RegistrationCreate):
    from datetime import datetime, timezone
    from backend.repositories.google_sheets import get_next_id

    now = datetime.now(timezone.utc).isoformat()
    reg_id = get_next_id("Registrations", "registration_id", "REG")
    row = {
        "registration_id": reg_id,
        "full_name": data.full_name,
        "email": data.email,
        "phone": data.phone,
        "program_id": data.program_id,
        "cohort_id": data.cohort_id,
        "registration_status": "REGISTERED",
        "payment_status": "UNPAID",
        "payment_reference": "",
        "payment_date": "",
        "fulfillment_status": "PENDING",
        "created_at": now,
        "updated_at": now,
    }
    reg_store.create_registration(row)
    return row


@router.put("/registrations/{registration_id}")
async def update_registration(registration_id: str, data: RegistrationUpdate):
    reg = reg_store.find_by_id(registration_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    from backend.repositories.google_sheets import update_row
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    update_row("Registrations", "registration_id", registration_id, updates)
    return {"status": "updated"}


@router.post("/registrations/{registration_id}/resend-confirmation")
async def resend_confirmation_email(registration_id: str, body: ResendConfirmationRequest = None):
    reg = reg_store.find_by_id(registration_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    if reg.payment_status != "PAID":
        raise HTTPException(status_code=400, detail="Registration is not paid")
    email_override = body.email if body else None
    whatsapp_override = body.whatsapp_link if body else None
    success = await resend_confirmation(registration_id, email=email_override, whatsapp_link=whatsapp_override)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email")
    return {"status": "sent"}
