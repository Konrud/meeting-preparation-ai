from typing import Optional
from pydantic import BaseModel, Field


class Attendee(BaseModel):
    email: str = Field(
        description="Email of the attendee",
    )
    name: Optional[str] = Field(
        description="Name of the attendee",
    )
    position: Optional[str] = Field(
        default=None,
        description="Position of the attendee in the company",
    )
    info: Optional[str] = Field(
        default=None,
        description="Additional information about the attendee",
    )