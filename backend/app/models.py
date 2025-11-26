from sqlalchemy import Column, Integer, String, Text, DateTime
from .database import Base
from datetime import datetime

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=False, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
