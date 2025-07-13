from datetime import date
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session

from app.api.deps import get_or_create_user, get_session
from app.models.users import Users
from app.schemas.events import EventResponse
from app.crud.crud_events import crud_events


calendar_router = APIRouter()


@calendar_router.get("/events")
async def get_calendar_events(
    start_date: date = Query(description="캘린더 시작일"),
    end_date: date = Query(description="캘린더 종료일"),
    db_user: Users = Depends(get_or_create_user),
    session: Session = Depends(get_session),
) -> list[EventResponse]:
    """현재 사용자 캘린더 이벤트 조회"""
    events = crud_events.get_user_subscription_events(
        session=session, user_id=db_user.id, start_date=start_date, end_date=end_date
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
