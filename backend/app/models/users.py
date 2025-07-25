from sqlalchemy import Column, String, Enum, Integer, ForeignKey, Index, TIMESTAMP, func, TEXT, JSON
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from .base import BaseModel
from ..constants import UserLevel
from ..core.config import LevelConfig


class Users(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), nullable=False, unique=True, comment="사용자 이메일")
    password = Column(String(255), nullable=True, comment="이메일 회원가입 시, 사용자 비밀번호 해시")
    uid = Column(String(50), nullable=True, unique=True, comment="구글 소셜 로그인, Firebase Auth UID")
    name = Column(String(100), nullable=False, comment="사용자 이름")
    level = Column(
        Enum(UserLevel, native_enum=False, validate_strings=True), nullable=False, default=UserLevel.BEGINNER
    )
    investment_profile = Column(String(255), nullable=True)
    exp = Column(
        MutableDict.as_mutable(JSON), nullable=False, default=LevelConfig.get_default_exp, comment="레벨업을 위한 경험치 정보"
    )

    user_subscriptions = relationship(
        "UserEventSubscription", back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    user_google_calendar = relationship(
        "UserGoogleCalendar", back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    chat_sessions = relationship(
        "ChatSessions", back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )


class LevelFeature(BaseModel):
    """
    레벨별 제공 기능 테이블
    """

    __tablename__ = "level_feature"

    level = Column(Enum(UserLevel, native_enum=False, validate_strings=True), nullable=False)
    feature_name = Column(String(100), nullable=False, comment="레벨별 제공 기능")
    feature_description = Column(TEXT, nullable=True, comment="제공 기능 설명")


class UserEventSubscription(BaseModel):
    __tablename__ = "user_event_subscription"

    __table_args__ = (
        Index("idx_users_event_subscription", "user_id", "event_id", unique=True),
        {"extend_existing": True},
    )

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    subscribed_at = Column(TIMESTAMP, nullable=False, default=func.current_timestamp())

    user = relationship("Users", back_populates="user_subscriptions")
    event = relationship("Events", back_populates="user_subscriptions")


class UserGoogleCalendar(BaseModel):
    __tablename__ = "user_google_calendar"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    google_calendar_id = Column(String(255), nullable=False, comment="구글 캘린더 id")
    access_token = Column(TEXT, nullable=False, comment="구글 엑세스 토큰")
    refresh_token = Column(TEXT, nullable=False, comment="구글 리프레시 토큰")
    token_expiry = Column(TIMESTAMP, nullable=True, comment="구글 토큰 만료 시간")

    user = relationship("Users", back_populates="user_google_calendar")
