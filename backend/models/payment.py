from pydantic import BaseModel


class PaymentRecordStatus(str):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class Payment(BaseModel):
    payment_id: str
    registration_id: str
    program_id: str
    cohort_id: str
    transaction_reference: str
    amount: str = "0"
    currency: str = "NGN"
    status: str = PaymentRecordStatus.PENDING
    gateway: str = "paystack"
    paid_at: str = ""
    verified_at: str = ""
    created_at: str = ""
    updated_at: str = ""
