from sqlalchemy.orm import Session
from datetime import date

from app.crud.base import CRUDBase
from app.models.events import Events
from app.models.users import UserEventSubscription
from app.schemas.events import EventResponse


class CRUDEvents(CRUDBase[Events, None, None]):
    def get_user_subscription_events(
        self, session: Session, user_id: int, start_date: date, end_date: date
    ) -> list[EventResponse]:
        """
        유저가 구독 중인 이벤트 목록 반환

        Args:
            session: DB 세션
            user_id: DB User ID
            start_date: 조회 시작 날짜
            end_date: 조회 종료 날짜

        Returns:
            구독한 이벤트 목록
        """
        query = (
            session.query(Events)
            .join(UserEventSubscription, Events.id == UserEventSubscription.event_id)  # 구독 조인
            .filter(
                # 날짜 범위 필터
                Events.date.between(start_date, end_date),
                # 삭제되지 않은 이벤트만
                Events.dropped_at.is_(None),
                # 삭제되지 않은 구독만
                UserEventSubscription.dropped_at.is_(None),
                # Firebase UID로 사용자 필터
                UserEventSubscription.user_id == user_id,
            )
            .order_by(Events.date.asc())  # 날짜 순 정렬
        )

        result = query.all()
        # EventResponse 객체 생성
        events = []
        for event in result:
            event_response = EventResponse(
                title=event.title,
                description=event.description,
                date=event.date,
                impact=event.impact,
                level=event.level,
            )
            events.append(event_response)

        return events


crud_events = CRUDEvents(Events)
