from typing import Any

from backend.models.cohort import Cohort
from backend.models.program import Program
from backend.repositories.google_sheets import (
    find_row,
    find_rows,
    read_sheet,
)
from backend.utils.logging import get_logger

logger = get_logger(__name__)

PROGRAMS_TAB = "Programs"
COHORTS_TAB = "Cohorts"


def _row_to_program(row: dict[str, Any]) -> Program:
    return Program(**{k: v for k, v in row.items() if k in Program.model_fields})


def _row_to_cohort(row: dict[str, Any]) -> Cohort:
    return Cohort(**{k: v for k, v in row.items() if k in Cohort.model_fields})


def get_all_programs() -> list[Program]:
    rows = read_sheet(PROGRAMS_TAB)
    return [_row_to_program(r) for r in rows]


def get_program(program_id: str) -> Program | None:
    row = find_row(PROGRAMS_TAB, "program_id", program_id)
    return _row_to_program(row) if row else None


def get_program_by_name(program_name: str) -> Program | None:
    row = find_row(PROGRAMS_TAB, "program_name", program_name)
    return _row_to_program(row) if row else None


def get_cohorts(program_id: str) -> list[Cohort]:
    rows = find_rows(COHORTS_TAB, "program_id", program_id)
    return [_row_to_cohort(r) for r in rows]


def get_all_cohorts() -> list[Cohort]:
    rows = read_sheet(COHORTS_TAB)
    return [_row_to_cohort(r) for r in rows]


def get_cohort(cohort_id: str) -> Cohort | None:
    row = find_row(COHORTS_TAB, "cohort_id", cohort_id)
    return _row_to_cohort(row) if row else None


def get_cohort_by_paystack_page(page: str) -> Cohort | None:
    row = find_row(COHORTS_TAB, "paystack_page", page)
    return _row_to_cohort(row) if row else None
