from pydantic import BaseModel


class RegistrationStatus(str):
    REGISTERED = "REGISTERED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class PaymentStatus(str):
    UNPAID = "UNPAID"
    PAID = "PAID"
    PENDING = "PENDING"
    FAILED = "FAILED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class Registration(BaseModel):
    registration_id: str
    full_name: str
    email: str
    phone: str = ""
    program_id: str
    cohort_id: str
    registration_status: str = RegistrationStatus.REGISTERED
    payment_status: str = PaymentStatus.UNPAID
    payment_reference: str = ""
    payment_date: str = ""
    fulfillment_status: str = "PENDING"
    created_at: str = ""
    updated_at: str = ""
