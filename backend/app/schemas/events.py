from datetime import date
from pydantic import BaseModel


class EventResponse(BaseModel):
    """이벤트 응답"""

    title: str
    description: str | None = None
    date: date
    impact: str | None = None
    level: str | None = None

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    """이벤트 생성"""

    title: str | None = None
    description: str | None = None
    date: date
    impact: str | None = None
    level: str | None = None
    release_id: str
    source: str

    class Config:
        from_attributes = True
