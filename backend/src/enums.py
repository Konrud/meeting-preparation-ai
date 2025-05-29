from enum import Enum


class ProgressEventType(str, Enum):
    INIT = "init"
    CALENDAR_DATA_RETRIEVAL = "calendar_data_retrieval"
    PROCESSING = "processing"
    FORMATTING = "formatting"
    COMPLETED = "completed"
    FAILED = "failed"