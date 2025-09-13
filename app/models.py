from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base
import json

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    original_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    title = Column(String(255), nullable=True)
    topics = Column(String(512), nullable=False)  # stored as comma separated values
    sentiment = Column(String(16), nullable=False)
    keywords = Column(String(255), nullable=False)  # stored as comma separated values
    confidence = Column(Float, nullable=True)

    def topics_list(self):
        return [t for t in self.topics.split(",") if t]

    def keywords_list(self):
        return [k for k in self.keywords.split(",") if k]
