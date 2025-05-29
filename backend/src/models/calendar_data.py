from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional
from src.models.attendee import Attendee
from src.models.meeting import Meeting

class CalendarData(BaseModel):
    meetings: List[Meeting] = Field(
        default_factory=list,
        description="List of meetings with their details",
    )


