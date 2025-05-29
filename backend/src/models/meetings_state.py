from datetime import datetime
from typing import Dict, List, Optional
from typing import Any
from pydantic import BaseModel, SerializationInfo, field_serializer, ConfigDict, Field

PREVENT_DATETIME_SERIALIZATION = "prevent_datetime_serialization"

class MeetingsState(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    date: datetime = Field(description="Date of the meeting")
    calendar_data: str = Field(description="Calendar data in JSON format")
    calendar_events: List[Dict] = Field(
        default_factory=list, description="List of calendar events for the meeting"
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


