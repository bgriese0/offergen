from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Document(BaseModel):
    id: int
    filename: str
    content: str
    created_at: Optional[datetime]

    class Config:
        orm_mode = True
