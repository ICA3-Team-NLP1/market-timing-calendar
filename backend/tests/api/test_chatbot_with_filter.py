"""
필터링이 적용된 챗봇 API 통합 테스트
"""
from unittest.mock import MagicMock, patch
from fastapi import status

from app.crud.crud_users import crud_users
from app.schemas.users import UsersCreate


class TestChatbotWithFilter:
    """필터링이 적용된 챗봇 API 테스트"""

    @patch("app.api.v1.chatbot.LLMClient")
    def test_conversation_with_filter_enabled(
        self, mock_llm_client, client, session, mock_firebase_token, auth_headers
    ):
        """필터링 활성화된 대화 테스트"""
        # Given: 사용자 생성
        uid = mock_firebase_token.return_value.get("uid")
        db_user = crud_users.create(session, obj_in=UsersCreate(uid=uid, name="test-name", email="test-email"))
        session.commit()

        # Mock LLM 클라이언트 - 디버그: 안전한 스트리밍 응답 설정
        mock_llm_instance = mock_llm_client.return_value
        mock_llm_instance.stream_chat_with_filter = MagicMock()
        mock_llm_instance.stream_chat_with_filter.return_value.__aiter__.return_value = ["안전한 ", "경제 지표 ", "설명입니다."]

        request_data = {"history": [], "question": "경제 지표에 대해 알려주세요", "safety_level": "strict"}

        # When: API 호출 (필터링 활성화)
        response = client.post("/api/v1/chatbot/conversation?use_filter=true", json=request_data, headers=auth_headers)

        # Then: 성공 응답
        assert response.status_code == status.HTTP_200_OK

        # 디버그: 스트리밍 응답 검증
        content = response.text
        assert "안전한 경제 지표 설명입니다." in content

    @patch("app.api.v1.chatbot.LLMClient")
    def test_conversation_with_filter_disabled(
        self, mock_llm_client, client, session, mock_firebase_token, auth_headers
    ):
        """필터링 비활성화된 대화 테스트"""
        # Given: 사용자 생성
        uid = mock_firebase_token.return_value.get("uid")
        db_user = crud_users.create(session, obj_in=UsersCreate(uid=uid, name="test-name", email="test-email"))
        session.commit()

        # Mock LLM 클라이언트 - 디버그: 일반 스트리밍 응답 설정
        mock_llm_instance = mock_llm_client.return_value
        mock_llm_instance.stream_chat = MagicMock()
        mock_llm_instance.stream_chat.return_value.__aiter__.return_value = iter(["원본 ", "응답 ", "메시지입니다."])

        request_data = {"history": [], "question": "경제 지표에 대해 알려주세요"}

        # When: API 호출 (필터링 비활성화)
        response = client.post("/api/v1/chatbot/conversation?use_filter=false", json=request_data, headers=auth_headers)

        # Then: 성공 응답
        assert response.status_code == status.HTTP_200_OK

        # 디버그: 원본 stream_chat 메서드 호출 확인
        mock_llm_instance.stream_chat.assert_called_once()

    @patch("app.crud.crud_events.crud_events.get_by_release_id")
    @patch("app.api.v1.chatbot.LLMClient")
    def test_explain_event_with_filter(
        self, mock_llm_client, mock_get_event, client, session, mock_firebase_token, auth_headers
    ):
        """이벤트 설명 API 필터링 테스트"""
        # Given: 사용자 생성
        uid = mock_firebase_token.return_value.get("uid")
        db_user = crud_users.create(session, obj_in=UsersCreate(uid=uid, name="test-name", email="test-email"))
        session.commit()

        # Mock 이벤트 데이터 - 디버그: 실제 이벤트 객체 형태로 설정
        mock_event = {
            "title": "소비자물가지수",
            "description": "월별 소비자물가 변동률",
            "date": "2024-01-15",
            "impact": "HIGH",
            "source": "FRED",
            "release_id": "CPILFESL",
        }
        mock_get_event.return_value = type("Event", (), mock_event)

        # Mock LLM 클라이언트 - 디버그: 이벤트 설명 응답 설정
        mock_llm_instance = mock_llm_client.return_value
        mock_llm_instance.stream_chat_with_filter = MagicMock()
        mock_llm_instance.stream_chat_with_filter.return_value.__aiter__.return_value = iter(
            ["소비자물가지수는 ", "경제의 중요한 ", "지표입니다."]
        )

        request_data = {"release_id": "CPILFESL", "safety_level": "strict"}

        # When: API 호출
        response = client.post("/api/v1/chatbot/event/explain?use_filter=true", json=request_data, headers=auth_headers)

        # Then: 성공 응답
        assert response.status_code == status.HTTP_200_OK

        # 디버그: 이벤트 설명 응답 검증
        content = response.text
        assert "소비자물가지수는 경제의 중요한 지표입니다." in content

    @patch("app.services.filter_service.FilterService.check_safety_only")
    @patch("app.utils.llm_client.LLMFactory.create_llm")
    def test_safety_check_endpoint(
        self, mock_llm, mock_safety_check, client, session, mock_firebase_token, auth_headers
    ):
        """컨텐츠 안전성 검사 API 테스트"""
        # Given: 사용자 생성
        uid = mock_firebase_token.return_value.get("uid")
        db_user = crud_users.create(session, obj_in=UsersCreate(uid=uid, name="test-name", email="test-email"))
        session.commit()

        # Mock 안전성 검사 결과 - 디버그: 실제 필터링 서비스 응답 형태로 설정
        mock_safety_result = {
            "is_safe": False,
            "safety_score": 0.3,
            "risk_categories": ["investment_advice", "guaranteed_profit"],
            "filter_reason": "투자 권유 및 수익 보장 표현 포함",
            "analysis_only": True,
        }

        mock_safety_check.return_value = mock_safety_result

        request_data = {"content": "이 주식을 지금 사세요! 확실한 수익을 보장합니다!"}

        # When: API 호출
        response = client.post("/api/v1/chatbot/safety/check", json=request_data, headers=auth_headers)

        # Then: 성공 응답과 안전성 분석 결과 확인
        assert response.status_code == status.HTTP_200_OK

        result = response.json()
        assert result["is_safe"] is False
        assert result["safety_score"] == 0.3
        assert "investment_advice" in result["risk_categories"]
        assert result["analysis_only"] is True
        assert mock_llm.call_count > 0

    @patch("app.utils.llm_client.LLMFactory.create_llm")
    def test_filter_status_endpoint(self, mock_llm, client, session, mock_firebase_token, auth_headers):
        """필터링 시스템 상태 조회 API 테스트"""
        # Given: 사용자 생성
        uid = mock_firebase_token.return_value.get("uid")
        db_user = crud_users.create(session, obj_in=UsersCreate(uid=uid, name="test-name", email="test-email"))
        session.commit()

        # When: API 호출
        response = client.get("/api/v1/chatbot/filter/status", headers=auth_headers)

        # Then: 성공 응답과 상태 정보 확인
        assert response.status_code == status.HTTP_200_OK

        result = response.json()
        assert "enabled" in result
        assert "safety_level" in result
        assert "max_retries" in result
        assert "filter_model" in result
        assert mock_llm.call_count > 0
