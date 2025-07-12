from datetime import date
from pydantic import BaseModel


class EventCategoryResponse(BaseModel):
    """이벤트 카테고리 응답"""

    name: str
    description: str | None = None


class EventResponse(BaseModel):
    """이벤트 응답"""

    title: str
    description: str | None = None
    date: date
    impact: str | None = None
    category: EventCategoryResponse | None = None

    class Config:
        from_attributes = True
