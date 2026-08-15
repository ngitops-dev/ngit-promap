from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ProgramStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Program(BaseModel):
    program_id: str
    program_name: str
    description: str = ""
    status: ProgramStatus = ProgramStatus.ACTIVE
    currency: str = "NGN"
    created_at: str = ""
    updated_at: str = ""
