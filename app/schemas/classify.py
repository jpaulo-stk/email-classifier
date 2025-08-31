from pydantic import BaseModel, Field
from typing import List
from app.enums.common import Category 

class ClassifyIn(BaseModel): 
    text: str = Field(..., min_length=1, description="Conteúdo do email para classificar")

class ClassifyOut(BaseModel):
    category: Category
    confidence: float
    suggestedReply: str

class BatchIn(BaseModel):
    texts: List[str] = Field(..., min_length=1, description="Lista de emails para classificar")