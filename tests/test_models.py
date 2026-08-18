from backend.models.program import Program, ProgramStatus
from backend.models.cohort import Cohort
from backend.models.registration import Registration
from backend.models.payment import Payment
from backend.models.fulfillment import Fulfillment


def test_program_model():
    p = Program(
        program_id="PROG001",
        program_name="AI/ML",
        description="Test program",
        status=ProgramStatus.ACTIVE,
        currency="NGN",
    )
    assert p.program_id == "PROG001"
    assert p.status == ProgramStatus.ACTIVE


def test_cohort_model():
    c = Cohort(
        cohort_id="COH001",
        program_id="PROG001",
        cohort_name="Cohort 1",
        expected_amount="5000000",
        currency="NGN",
    )
    assert c.cohort_id == "COH001"
    assert c.expected_amount == "5000000"


def test_registration_model():
    r = Registration(
        registration_id="REG001",
        full_name="Ada Johnson",
        email="ada@example.com",
        program_id="PROG001",
        cohort_id="COH001",
    )
    assert r.registration_id == "REG001"
    assert r.payment_status == "UNPAID"


def test_payment_model():
    p = Payment(
        payment_id="PAY001",
        registration_id="REG001",
        program_id="PROG001",
        cohort_id="COH001",
        transaction_reference="REF123",
        amount="5000000",
        currency="NGN",
        status="PAID",
    )
    assert p.status == "PAID"


def test_fulfillment_model():
    f = Fulfillment(
        fulfillment_id="FUL001",
        registration_id="REG001",
        payment_id="PAY001",
        status="COMPLETED",
    )
    assert f.status == "COMPLETED"
