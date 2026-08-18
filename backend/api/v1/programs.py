from fastapi import APIRouter, Depends, HTTPException, Query

from backend.repositories.programs import (
    get_all_cohorts,
    get_all_programs,
    get_cohort,
    get_cohorts,
    get_program,
)
from backend.repositories.registrations import (
    get_all_registrations,
    get_registrations_by_cohort,
    get_registrations_by_program,
)
from backend.schemas.admin import CohortCreate, ProgramCreate, ProgramUpdate, CohortUpdate
from backend.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/programs")
async def list_programs():
    return [p.model_dump() for p in get_all_programs()]


@router.post("/programs")
async def create_program(data: ProgramCreate):
    from backend.repositories.google_sheets import append_row, get_next_id
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    program_id = get_next_id("Programs", "program_id", "PROG")
    row = {
        "program_id": program_id,
        "program_name": data.program_name,
        "description": data.description,
        "status": data.status,
        "currency": data.currency,
        "created_at": now,
        "updated_at": now,
    }
    append_row("Programs", row)
    return row


@router.get("/programs/{program_id}")
async def get_program_detail(program_id: str):
    program = get_program(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program.model_dump()


@router.put("/programs/{program_id}")
async def update_program(program_id: str, data: ProgramUpdate):
    program = get_program(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    from backend.repositories.google_sheets import update_row
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    update_row("Programs", "program_id", program_id, updates)
    return {"status": "updated"}


@router.delete("/programs/{program_id}")
async def delete_program(program_id: str):
    program = get_program(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    from backend.repositories.google_sheets import update_row
    update_row("Programs", "program_id", program_id, {"status": "INACTIVE"})
    return {"status": "deactivated"}


@router.get("/cohorts")
async def list_cohorts(program_id: str | None = None):
    if program_id:
        return [c.model_dump() for c in get_cohorts(program_id)]
    return [c.model_dump() for c in get_all_cohorts()]


@router.post("/cohorts")
async def create_cohort(data: CohortCreate):
    from backend.repositories.google_sheets import append_row, get_next_id
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    cohort_id = get_next_id("Cohorts", "cohort_id", "COH")
    row = {
        "cohort_id": cohort_id,
        "program_id": data.program_id,
        "cohort_name": data.cohort_name,
        "start_date": data.start_date,
        "end_date": data.end_date,
        "registration_deadline": data.registration_deadline,
        "capacity": data.capacity,
        "paystack_page": data.paystack_page,
        "expected_amount": data.expected_amount,
        "currency": data.currency,
        "whatsapp_link": data.whatsapp_link,
        "email_template": data.email_template,
        "payment_deadline": data.payment_deadline,
        "status": data.status,
    }
    append_row("Cohorts", row)
    return row


@router.get("/cohorts/{cohort_id}")
async def get_cohort_detail(cohort_id: str):
    cohort = get_cohort(cohort_id)
    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found")
    return cohort.model_dump()


@router.put("/cohorts/{cohort_id}")
async def update_cohort(cohort_id: str, data: CohortUpdate):
    cohort = get_cohort(cohort_id)
    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found")
    from backend.repositories.google_sheets import update_row
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    update_row("Cohorts", "cohort_id", cohort_id, updates)
    return {"status": "updated"}
