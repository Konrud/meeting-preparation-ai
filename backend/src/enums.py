from enum import Enum


class ProgressEventType(str, Enum):
    INIT = "init"
    PROCESSING = "processing"
    FORMATTING = "formatting"
    COMPLETED = "completed"
    FAILED = "failed"