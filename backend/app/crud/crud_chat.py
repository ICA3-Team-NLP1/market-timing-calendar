from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.chat import ChatSessions
from app.schemas.chat import ChatSessionCreate


class CRUDChatSessions(CRUDBase[ChatSessions, ChatSessionCreate, None]):
    """대화 세션 CRUD 클래스"""

    def increment_message_count(self, session: Session, session_id: str, count: int = 1) -> Optional[ChatSessions]:
        """
        세션의 메시지 카운트 증가
        """
        db_session = self.get(session=session, session_id=session_id)
        if not db_session:
            return None

        db_session.message_count += count
        db_session.updated_at = datetime.now()
        session.flush()

        return db_session


# CRUD 인스턴스 생성
crud_chat_sessions = CRUDChatSessions(ChatSessions)
