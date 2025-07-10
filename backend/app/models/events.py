"""
Event 모델 정의
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.sql import func
from .base import Base


class Event(Base):
    """경제 이벤트/지표 모델"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    release_id = Column(String(50), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    impact = Column(String(20), nullable=True)  # High, Medium, Low
    category_id = Column(Integer, nullable=True)
    source = Column(String(50), nullable=False, default="FRED")
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Event(id={self.id}, release_id={self.release_id}, date={self.date}, title='{self.title}')>" 