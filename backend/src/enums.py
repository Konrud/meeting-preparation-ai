from enum import Enum


class ProgressEventType(str, Enum):
    INIT = "init"
    CALENDAR_DATA_RETRIEVAL = "calendar_data_retrieval"
    CALENDAR_DATA_PARSER = "calendar_data_parser"
    CALENDAR_EVENT = "calendar_event"
    RESEARCH = "research"
    PROCESSING = "processing"
    FORMATTING = "formatting"
    COMPLETED = "completed"
    FAILED = "failed"


class CtxKeys(str, Enum):
    MEETING_INFO = "meeting_info"
