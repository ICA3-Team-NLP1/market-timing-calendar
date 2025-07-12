from sqlalchemy import Column, String, Enum, Integer, ForeignKey, Index, TIMESTAMP, func, TEXT
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.events import Events
from app.constants import UserLevel


class Users(BaseModel):
    email = Column(String(255), nullable=False, unique=True, comment="사용자 이메일")
    password = Column(String(255), nullable=True, comment="이메일 회원가입 시, 사용자 비밀번호 해시")
    uid = Column(String(50), nullable=True, unique=True, comment="구글 소셜 로그인, Firebase Auth UID")
    name = Column(String(100), nullable=False, comment="사용자 이름")
    level = Column(Enum(UserLevel, native_enum=False, validate_strings=True), default=UserLevel.BEGINNER)
    investment_profile = Column(String(255), nullable=True)
    exp = Column(Integer, nullable=False, default=0)

    user_subscriptions = relationship(
        "UserEventSubscription", back_populates="users", cascade="all, delete-orphan", passive_deletes=True
    )
    user_google_calendar = relationship(
        "UserGoogleCalendar", back_populates="users", cascade="all, delete-orphan", passive_deletes=True
    )


class LevelFeature(BaseModel):
    """
    레벨별 제공 기능 테이블
    """

    level = Column(Enum(UserLevel, native_enum=False, validate_strings=True), nullable=False)
    feature_name = Column(String(100), nullable=False, comment="레벨별 제공 기능")
    feature_description = Column(String(100), nullable=True, comment="제공 기능 설명")


class UserEventSubscription(BaseModel):
    __table_args__ = (Index("idx_users_event_subscription", "user_id", "event_id", unique=True),)
    user_id = Column(ForeignKey(Users.id, ondelete="CASCADE"), nullable=False)
    event_id = Column(ForeignKey(Events.id, ondelete="CASCADE"), nullable=False)
    subscribed_at = Column(TIMESTAMP, nullable=False, default=func.current_timestamp())

    users = relationship("Users", back_populates="user_subscriptions")
    events = relationship("Events", back_populates="user_subscriptions")

class UserGoogleCalendar(BaseModel):
    user_id = Column(ForeignKey(Users.id, ondelete="CASCADE"), nullable=False)
    google_calendar_id = Column(String(255), nullable=False, comment="구글 캘린더 id")
    access_token = Column(TEXT, nullable=False, comment="구글 엑세스 토큰")
    refresh_token = Column(TEXT, nullable=False, comment="구글 리프레시 토큰")
    token_expiry = Column(TIMESTAMP, nullable=True, comment="구글 토큰 만료 시간")

    users = relationship("Users", back_populates="user_google_calendar")
