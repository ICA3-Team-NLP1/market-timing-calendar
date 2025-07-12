from datetime import date
from pydantic import BaseModel

class EventResponse(BaseModel):
    """이벤트 응답"""

    title: str
    description: str | None = None
    date: date
    impact: str | None = None

    class Config:
        from_attributes = True
