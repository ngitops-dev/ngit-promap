from pydantic import BaseModel


class Program(BaseModel):
    program_id: str
    program_name: str
    description: str = ""
    status: str = "ACTIVE"
    currency: str = "NGN"
    created_at: str = ""
    updated_at: str = ""


class Cohort(BaseModel):
    cohort_id: str
    program_id: str
    cohort_name: str
    start_date: str = ""
    end_date: str = ""
    registration_deadline: str = ""
    capacity: str = "0"
    status: str = "UPCOMING"
    paystack_page: str = ""
    expected_amount: str = "0"
    currency: str = "NGN"
    whatsapp_link: str = ""
    email_template: str = ""
    payment_deadline: str = ""


class Registration(BaseModel):
    registration_id: str
    full_name: str
    email: str
    phone: str = ""
    program_id: str
    cohort_id: str
    registration_status: str = "REGISTERED"
    payment_status: str = "UNPAID"
    payment_reference: str = ""
    payment_date: str = ""
    fulfillment_status: str = "PENDING"
    created_at: str = ""
    updated_at: str = ""


class Payment(BaseModel):
    payment_id: str
    registration_id: str = ""
    program_id: str = ""
    cohort_id: str = ""
    transaction_reference: str
    amount: str = "0"
    currency: str = "NGN"
    status: str = "PENDING"
    gateway: str = "paystack"
    paid_at: str = ""
    verified_at: str = ""
    created_at: str = ""
    updated_at: str = ""


class EmailLog(BaseModel):
    email_id: str
    registration_id: str = ""
    email_type: str
    recipient: str
    subject: str
    status: str = "SENT"
    sent_at: str = ""
    error_message: str = ""


class ActivityLog(BaseModel):
    log_id: str
    user: str
    action: str
    target: str = ""
    details: str = ""
    timestamp: str = ""


class SystemHealth(BaseModel):
    fastapi: str = "disconnected"
    google_sheets: str = "disconnected"
    gmail: str = "disconnected"
    paystack: str = "disconnected"
