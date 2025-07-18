from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_or_create_user, get_session
from app.constants import UserLevel
from app.models.users import Users
from app.schemas.events import EventResponse, EventSubscriptionCreate, EventSubscriptionResponse
from app.crud.crud_events import crud_events
from app.crud.crud_users import crud_user_subscription


calendar_router = APIRouter()


@calendar_router.get("/events")
async def get_calendar_events(
    start_date: date = Query(description="캘린더 시작일"),
    end_date: date = Query(description="캘린더 종료일"),
    user_level: UserLevel | None = Query(default=None, description="유저 레벨, None 일 경우 기간 내 전체 노출"),
    db_user: Users = Depends(get_or_create_user),
    session: Session = Depends(get_session),
) -> list[EventResponse]:
    """현재 사용자 캘린더 이벤트 조회"""
    events = crud_events.get_user_subscription_events(
        session=session, user_id=db_user.id, start_date=start_date, end_date=end_date, user_level=user_level
    )
    return events


@calendar_router.get("/events/by-level")
async def get_events_by_level(
    start_date: date = Query(description="캘린더 시작일"),
    end_date: date = Query(description="캘린더 종료일"),
    db_user: Users = Depends(get_or_create_user),
    session: Session = Depends(get_session),
) -> list[EventResponse]:
    """유저 레벨에 따른 이벤트 목록 조회"""
    events = crud_events.get_events_by_level(
        session=session, start_date=start_date, end_date=end_date, user_level=db_user.level
    )
    return events


@calendar_router.post("/subscriptions")
async def create_event_subscription(
    subscription_data: EventSubscriptionCreate,
    db_user: Users = Depends(get_or_create_user),
    session: Session = Depends(get_session),
) -> EventSubscriptionResponse:
    """이벤트 구독 생성 (일정 저장)"""
    # 이벤트가 존재하는지 확인
    event = session.query(crud_events.model).filter(
        crud_events.model.id == subscription_data.event_id,
        crud_events.model.dropped_at.is_(None)
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="이벤트를 찾을 수 없습니다.")
    
    # 구독 생성
    subscription = crud_user_subscription.create_subscription(
        session=session,
        user_id=db_user.id,
        event_id=subscription_data.event_id
    )
    
    # 응답 생성
    event_response = EventResponse(
        id=event.id,
        release_id=event.release_id,
        title=event.title,
        description=event.description,
        date=event.date,
        impact=event.impact,
        level=event.level,
        popularity=event.popularity,
        description_ko=event.description_ko,
        level_category=event.level_category,
    )
    
    return EventSubscriptionResponse(
        id=subscription.id,
        event_id=subscription.event_id,
        user_id=subscription.user_id,
        subscribed_at=subscription.subscribed_at.isoformat(),
        event=event_response
    )


@calendar_router.get("/subscriptions")
async def get_user_subscriptions(
    db_user: Users = Depends(get_or_create_user),
    session: Session = Depends(get_session),
) -> list[EventSubscriptionResponse]:
    """사용자의 저장된 일정 조회"""
    subscriptions = crud_user_subscription.get_user_subscriptions(
        session=session,
        user_id=db_user.id
    )
    
    result = []
    for subscription in subscriptions:
        # 이벤트 정보 조회
        event = session.query(crud_events.model).filter(
            crud_events.model.id == subscription.event_id,
            crud_events.model.dropped_at.is_(None)
        ).first()
        
        if event:
            event_response = EventResponse(
                id=event.id,
                release_id=event.release_id,
                title=event.title,
                description=event.description,
                date=event.date,
                impact=event.impact,
                level=event.level,
                popularity=event.popularity,
                description_ko=event.description_ko,
                level_category=event.level_category,
            )
        else:
            event_response = None
        
        subscription_response = EventSubscriptionResponse(
            id=subscription.id,
            event_id=subscription.event_id,
            user_id=subscription.user_id,
            subscribed_at=subscription.subscribed_at.isoformat(),
            event=event_response
        )
        result.append(subscription_response)
    
    return result
