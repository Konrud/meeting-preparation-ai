from llama_index.core.workflow import Event
from src.enums import ProgressEventType

class ProgressEvent(Event):
    type: ProgressEventType
    message: str
    
    
class FinalEvent(Event):
    message: str
    response: str
    
class ResearchEvent(Event):
    pass