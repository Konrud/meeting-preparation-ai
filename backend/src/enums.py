from enum import Enum


class ProgressEventType(str, Enum):
    NEW = "new"
    PROCESSING = "processing"
    PENDING = "pending"
    REJECTED = "rejected"
    APPROVED = "approved"
    FAILED = "failed"