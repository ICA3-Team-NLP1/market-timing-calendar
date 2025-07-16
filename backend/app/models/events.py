"""
Event 모델 정의
"""
from sqlalchemy import Column, String, Date, Text, Integer, ForeignKey, Index, Enum, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..models.base import BaseModel
from ..constants import ImpactLevel, EventStatus, UserLevel


class Events(BaseModel):
    """경제 이벤트/지표 모델"""

    __tablename__ = "events"
    __table_args__ = (Index("idx_event_date", "date"), {"extend_existing": True})
    release_id = Column(String(50), nullable=True, index=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    date = Column(Date, nullable=False, index=True)
    impact = Column(Enum(ImpactLevel, native_enum=False, validate_strings=True), nullable=True)
    level = Column(Enum(UserLevel, native_enum=False, validate_strings=True), nullable=True)
    source = Column(String(50), nullable=False, default="FRED")
    popularity = Column(Integer, default=1)
    description_ko = Column(String(500), default="")
    level_category = Column(String(100), nullable=True, default="UNCATEGORIZED")

    # 관계 설정 - 이벤트와 연결된 사용자 구독 정보
    user_subscriptions = relationship(
        "UserEventSubscription", back_populates="event", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self):
        return f"<Events(id={self.id}, release_id={self.release_id}, date={self.date}, title='{self.title}')>"


class EventWebhook(BaseModel):
    __tablename__ = "event_webhook"

    event_type = Column(String(100), nullable=False)
    event_payload = Column(JSONB, nullable=False)
    status = Column(
        Enum(EventStatus, native_enum=False, validate_strings=True), nullable=False, default=EventStatus.PENDING
    )
    processed_at = Column(TIMESTAMP, nullable=True)
