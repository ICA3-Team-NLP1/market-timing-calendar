from sqlalchemy.orm import Session
from datetime import date

from app.crud.base import CRUDBase
from app.models.events import Events
from app.models.users import UserEventSubscription
from app.schemas.events import EventResponse
from app.constants import UserLevel


class CRUDEvents(CRUDBase[Events, None, None]):
    def get_by_release_id(self, session: Session, release_id: str) -> Events:
        """
        release_id로 이벤트 조회

        Args:
            session: DB 세션
            release_id: FRED release_id (예: CPILFESL, UNRATE 등)

        Returns:
            해당 release_id의 이벤트 객체 또는 None
        """
        return (
            session.query(Events)
            .filter(
                Events.release_id == release_id,
                Events.dropped_at.is_(None)  # 삭제되지 않은 이벤트만
            )
            .first()
        )

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

    def get_events_by_level(
        self, session: Session, start_date: date, end_date: date, user_level: UserLevel
    ) -> list[EventResponse]:
        """
        유저 레벨에 따른 이벤트 목록 반환

        Args:
            session: DB 세션
            start_date: 조회 시작 날짜
            end_date: 조회 종료 날짜
            user_level: 유저 레벨

        Returns:
            유저 레벨에 따른 이벤트 목록
        """
        # 유저 레벨에 따른 접근 가능한 이벤트 레벨 결정
        if user_level == UserLevel.BEGINNER:
            allowed_levels = [UserLevel.BEGINNER]
        elif user_level == UserLevel.INTERMEDIATE:
            allowed_levels = [UserLevel.BEGINNER, UserLevel.INTERMEDIATE]
        else:  # UserLevel.ADVANCED
            allowed_levels = [UserLevel.BEGINNER, UserLevel.INTERMEDIATE, UserLevel.ADVANCED]

        query = (
            session.query(Events)
            .filter(
                # 날짜 범위 필터
                Events.date.between(start_date, end_date),
                # 삭제되지 않은 이벤트만
                Events.dropped_at.is_(None),
                # 유저 레벨에 따른 이벤트 레벨 필터
                Events.level.in_(allowed_levels),
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
