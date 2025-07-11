"""
Event 모델 정의
"""
from sqlalchemy import Column, String, Date, Text, ForeignKey, Index, Enum, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..models.base import BaseModel
from ..constants import ImpactLevel, EventStatus


class EventCategory(BaseModel):
    """일정 카테고리 테이블"""

    name = Column(String(100), nullable=False)
    description = Column(Text)

    events = relationship("Events", back_populates="category", cascade="all, delete-orphan", passive_deletes=True)
    user_interest_categories = relationship(
        "UserInterestCategory", back_populates="category", cascade="all, delete-orphan", passive_deletes=True
    )
    # event_categories = relationship(
    #     "EventCategoryMap", back_populates="category", cascade="all, delete-orphan", passive_deletes=True
    # )


class Events(BaseModel):
    """경제 이벤트/지표 모델"""

    __table_args__ = (Index("idx_event_date", "date", unique=True),)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    date = Column(Date, nullable=False, index=True)
    impact = Column(Enum(ImpactLevel, native_enum=False, validate_strings=True), nullable=True)
    release_id = Column(String(50), nullable=False, index=True)
    source = Column(String(50), nullable=False, default="FRED")
    category_id = Column(ForeignKey(EventCategory.id, ondelete="CASCADE"), nullable=True)

    user_subscriptions = relationship(
        "UserEventSubscription", back_populates="events", cascade="all, delete-orphan", passive_deletes=True
    )
    category = relationship("EventCategory", back_populates="events")
    # event_categories = relationship(
    #     "EventCategoryMap", back_populates="events", cascade="all, delete-orphan", passive_deletes=True
    # )

    def __repr__(self):
        return f"<Events(id={self.id}, release_id={self.release_id}, date={self.date}, title='{self.title}')>"


# class EventCategoryMap(BaseModel):
#     """일정-카테고리 매핑 테이블 (다대다 관계용)"""
#
#     __table_args__ = Index("idx_event_category_map", "event_id", "category_id", unique=True)
#     event_id = Column(ForeignKey(Events.id, ondelete="CASCADE"), nullable=False)
#     category_id = Column(ForeignKey(EventCategory.id, ondelete="CASCADE"), nullable=False)
#
#     events = relationship("Event", back_populates="event_categories")
#     category = relationship("EventCategory", back_populates="event_categories")


class EventWebhook(BaseModel):
    event_type = Column(String(100), nullable=False)
    event_payload = Column(JSONB, nullable=False)
    level = Column(
        Enum(EventStatus, native_enum=False, validate_strings=True), nullable=False, default=EventStatus.PENDING
    )
    processed_at = Column(TIMESTAMP, nullable=True)
