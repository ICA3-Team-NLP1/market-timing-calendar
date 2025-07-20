from sqlalchemy import Column, String, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship

from .base import BaseModel


class ChatSessions(BaseModel):
    """대화 세션 모델"""

    __tablename__ = "chat_sessions"
    __table_args__ = (
        Index("idx_chat_sessions_user_id", "user_id"),
        Index("idx_chat_sessions_session_id", "session_id"),
        {"extend_existing": True},
    )

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="사용자 ID")
    session_id = Column(String(50), unique=True, nullable=False, comment="고유 세션 ID")
    message_count = Column(Integer, default=0, comment="메시지 개수")

    # 관계 설정
    user = relationship("Users", back_populates="chat_sessions")

    def __repr__(self):
        return f"<ChatSessions(id={self.id}, session_id={self.session_id}, user_id={self.user_id})>"
