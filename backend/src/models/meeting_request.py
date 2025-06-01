from datetime import datetime
from typing import Dict, List, Optional
from typing import Any
from pydantic import BaseModel, SerializationInfo, field_serializer, ConfigDict, Field

PREVENT_DATETIME_SERIALIZATION = "prevent_datetime_serialization"


class MeetingRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date: Optional[datetime] = Field(description="Date of a meeting")
    attendees: Optional[List[str]] = Field(
        default_factory=list,
        description="List of attendees for the meeting",
    )
    company: Optional[str] = Field(
        default=None, description="Company name for the meeting"
    )

    @field_serializer("*")
    def serialize_datetime(self, value: Any, info: SerializationInfo):
        context = info.context
        is_datetime = isinstance(value, datetime)
        has_context = context is not None
        serialize_datetime_value = (
            is_datetime
            and has_context
            and (context.get(PREVENT_DATETIME_SERIALIZATION) is not True)
        )

        if serialize_datetime_value:
            return value.isoformat()
        else:
            return value
