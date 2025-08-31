from pydantic import BaseModel
from typing import Optional

class FileClassifyOut(BaseModel):
    filename: str
    category: Optional[str] = None
    confidence: Optional[float] = None
    suggestedReply: Optional[str] = None
    error: Optional[str] = None