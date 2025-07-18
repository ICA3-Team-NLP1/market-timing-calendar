from datetime import date
from pydantic import BaseModel


class EventResponse(BaseModel):
    """이벤트 응답"""

    id: int
    release_id: str | None = None
    title: str | None = None
    description: str | None = None
    date: date
    impact: str | None = None
    level: str | None = None
    popularity: int | None = None
    description_ko: str | None = None
    level_category: str | None = None

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


class EventSubscriptionCreate(BaseModel):
    """이벤트 구독 생성 (일정 저장)"""

    event_id: int

    class Config:
        from_attributes = True


class EventSubscriptionResponse(BaseModel):
    """이벤트 구독 응답"""

    id: int
    event_id: int
    user_id: int
    subscribed_at: str
    event: EventResponse | None = None

    class Config:
        from_attributes = True
