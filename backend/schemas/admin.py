from pydantic import BaseModel


class ProgramCreate(BaseModel):
    program_name: str
    description: str = ""
    currency: str = "NGN"
    status: str = "ACTIVE"


class ProgramUpdate(BaseModel):
    program_name: str | None = None
    description: str | None = None
    currency: str | None = None
    status: str | None = None


class CohortCreate(BaseModel):
    program_id: str
    cohort_name: str
    start_date: str = ""
    end_date: str = ""
    registration_deadline: str = ""
    capacity: str = "0"
    paystack_page: str = ""
    expected_amount: str = "0"
    currency: str = "NGN"
    whatsapp_link: str = ""
    email_template: str = ""
    payment_deadline: str = ""
    status: str = "UPCOMING"


class CohortUpdate(BaseModel):
    cohort_name: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    registration_deadline: str | None = None
    capacity: str | None = None
    paystack_page: str | None = None
    expected_amount: str | None = None
    currency: str | None = None
    whatsapp_link: str | None = None
    email_template: str | None = None
    payment_deadline: str | None = None
    status: str | None = None


class RegistrationCreate(BaseModel):
    full_name: str
    email: str
    phone: str = ""
    program_id: str
    cohort_id: str


class RegistrationUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    registration_status: str | None = None
    payment_status: str | None = None
    fulfillment_status: str | None = None


class ManualVerifyRequest(BaseModel):
    reference: str
