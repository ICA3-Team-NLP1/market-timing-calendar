from datetime import date
from fastapi import APIRouter, Depends, Request, Query

from app.api.deps import get_or_create_user
from app.models.users import Users
from app.schemas.events import EventResponse
from app.crud.crud_events import crud_events


calendar_router = APIRouter()


@calendar_router.get("/events")
async def get_calendar_events(
    request: Request,
    start_date: date = Query(description="캘린더 시작일"),
    end_date: date = Query(description="캘린더 종료일"),
    db_user: Users = Depends(get_or_create_user),
) -> list[EventResponse]:
    """현재 사용자 캘린더 이벤트 조회"""
    session = request.state.session
    events = crud_events.get_user_subscription_events(
        session=session, user_ud=db_user.id, start_date=start_date, end_date=end_date
    )
    return events
