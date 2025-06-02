from typing import List, Optional
from llama_index.core.workflow import Event, StartEvent
from pydantic import Field
from src.enums import ProgressEventType


class ProgressWorkflowStartEvent(StartEvent):
    date: Optional[str] = Field(description="Date of a meeting")

    attendees: Optional[List[str]] = Field(
        default_factory=list,
        description="List of attendees for the meeting",
    )
    company: Optional[str] = Field(
        default=None, description="Company name for the meeting"
    )


class CalendarDataRetrievalEvent(Event):
    date: Optional[str] = Field(description="Date of a meeting")


class CalendarDataParserEvent(Event):
    calendar_data: str = Field(description="retrieved calendar data in JSON format")


class ProgressEvent(Event):
    type: ProgressEventType
    message: str


class FinalEvent(Event):
    message: str
    response: str


class FormatEvent(Event):
    message: str
    response: str


class ResearchEvent(Event):
    calendar_events: Optional[List[str]] = Field(
        default_factory=list,
        description="List of calendar events retrieved from the calendar data",
    )

    attendees: Optional[List[str]] = Field(
        default_factory=list,
        description="List of attendees for the meeting",
    )
    company: Optional[str] = Field(
        default=None, description="Company name for the meeting"
    )
