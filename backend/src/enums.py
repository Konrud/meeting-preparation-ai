from enum import Enum


class ProgressEventType(str, Enum):
    INIT = "init"
    CALENDAR_DATA_RETRIEVAL = "calendar_data_retrieval"
    CALENDAR_DATA_PARSER = "calendar_data_parser"
    PROCESSING = "processing"
    FORMATTING = "formatting"
    COMPLETED = "completed"
    FAILED = "failed"
