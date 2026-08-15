from pydantic import BaseModel


class FulfillmentStatus(str):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Fulfillment(BaseModel):
    fulfillment_id: str
    registration_id: str
    payment_id: str
    email_status: str = "PENDING"
    whatsapp_link_status: str = "PENDING"
    status: str = FulfillmentStatus.PENDING
    fulfilled_at: str = ""
    error_message: str = ""
