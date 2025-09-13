from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class AnalysisBase(BaseModel):
    text: str = Field(..., description="Original input text")

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisResponse(BaseModel):
    id: int
    created_at: datetime
    original_text: str
    summary: str
    title: Optional[str]
    topics: List[str]
    sentiment: str
    keywords: List[str]
    confidence: float | None
    model_config = ConfigDict(from_attributes=True)

class AnalyzeResult(BaseModel):
    summary: str
    title: Optional[str]
    topics: List[str]
    sentiment: str
    keywords: List[str]
    confidence: float | None

class SearchResponse(BaseModel):
    results: List[AnalysisResponse]
