from pydantic import BaseModel


class CohortStatus(str):
    ACTIVE = "ACTIVE"
    UPCOMING = "UPCOMING"
    INACTIVE = "INACTIVE"


class Cohort(BaseModel):
    cohort_id: str
    program_id: str
    cohort_name: str
    start_date: str = ""
    end_date: str = ""
    registration_deadline: str = ""
    capacity: str = "0"
    status: str = CohortStatus.UPCOMING
    paystack_page: str = ""
    expected_amount: str = "0"
    currency: str = "NGN"
    whatsapp_link: str = ""
    email_template: str = ""
    payment_deadline: str = ""
