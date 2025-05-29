from typing import List
from pydantic import BaseModel, Field
from src.models.attendee import Attendee

class Meeting(BaseModel):
    title: str = Field(
        description="Title of the meeting",
    )
    company: str = Field(
        description="Company associated with the meeting",
    )
    attendees: List[Attendee] = Field(
        default_factory=list,
        description="List of attendees for the meeting",
    )
    meeting_time: str = Field(
        description="Time of the meeting in ISO 8601 format",
    )