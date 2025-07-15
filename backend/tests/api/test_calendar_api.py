"""
캘린더 API 테스트
"""
import pytest
from datetime import date, timedelta, datetime
from fastapi import status
from unittest.mock import Mock, patch

from app.constants import UserLevel
from app.crud.crud_events import crud_events
from app.crud.crud_users import crud_users, crud_user_subscription
from app.schemas.events import EventCreate
from app.schemas.users import UsersCreate


class TestCalendarAPI:
    """캘린더 API 테스트 클래스"""

    def test_get_calendar_events_success(self, client, session, mock_firebase_token, auth_headers):
        """GET /calendar/events - 성공 케이스"""

        uid = mock_firebase_token.return_value.get("uid")
        db_user = crud_users.create(session, obj_in=UsersCreate(uid=uid, name="test-name", email="test-email"))

        # Mock 설정
        test_events = [
            EventCreate(
                title="GDP 발표",
                date=date(2025, 1, 15),
                release_id="GDPC1",
                source="FRED",
            ),
            EventCreate(
                title="금리 결정",
                date=date(2025, 1, 16),
                release_id="FEDFUNDS",
                source="FRED",
            ),
        ]
        for e in test_events:
            db_event = crud_events.create(session=session, obj_in=e)
            crud_user_subscription.create(
                session=session,
                obj_in={"user_id": db_user.id, "event_id": db_event.id, "subscribed_at": datetime.now()},
            )
        session.commit()

        response = client.get(
            "/api/v1/calendar/events",
            params={"start_date": "2025-01-01", "end_date": "2025-01-16"},
            headers=auth_headers,
        )

        # 응답 검증
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "GDP 발표"
        assert data[1]["title"] == "금리 결정"

        # 날짜 범위 필터링 테스트
        response = client.get(
            "/api/v1/calendar/events",
            params={"start_date": "2025-01-01", "end_date": "2025-01-15"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1

    def test_get_calendar_events_success_with_level(self, client, session, mock_firebase_token, auth_headers):
        """GET /calendar/events - 레벨 필터링 성공 케이스"""
        uid = mock_firebase_token.return_value.get("uid")
        db_user = crud_users.create(session, obj_in=UsersCreate(uid=uid, name="test-name", email="test-email"))

        # Mock 설정
        test_events = [
            EventCreate(
                title="GDP 발표",
                date=date(2025, 1, 15),
                release_id="GDPC1",
                source="FRED",
                level=UserLevel.ADVANCED,
            ),
            EventCreate(
                title="금리 결정",
                date=date(2025, 1, 16),
                release_id="FEDFUNDS",
                source="FRED",
                level=UserLevel.BEGINNER,
            ),
        ]
        for e in test_events:
            db_event = crud_events.create(session=session, obj_in=e)
            crud_user_subscription.create(
                session=session,
                obj_in={"user_id": db_user.id, "event_id": db_event.id, "subscribed_at": datetime.now()},
            )
        session.commit()

        # 레벨 필터링 테스트
        response = client.get(
            "/api/v1/calendar/events",
            params={"start_date": "2025-01-01", "end_date": "2025-01-16", "user_level": UserLevel.BEGINNER.value},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["level"] == UserLevel.BEGINNER
