from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import status

from app.crud.crud_users import crud_users
from app.crud.crud_chat import crud_chat_sessions
from app.schemas.chat import ChatSessionCreate
from app.schemas.users import UsersCreate


class TestChatWithMemory:
    """mem0 플랫폼 API 기반 대화 기능 테스트"""

    def test_chat_session_creation(self, client, session, mock_firebase_token, auth_headers):
        """대화 세션 생성 테스트"""
        # Given: 사용자 생성
        uid = mock_firebase_token.return_value.get("uid")
        db_user = crud_users.create(session, obj_in=UsersCreate(uid=uid, name="test-name", email="test-email"))
        db_chat_session = crud_chat_sessions.create(
            session, obj_in=ChatSessionCreate(user_id=db_user.id, session_id="test-session-id")
        )
        session.commit()

        # When: 새로운 대화 시작 (session_id 없음)
        request_data = {
            "question": "안녕하세요, 투자에 대해 알려주세요",
            "use_memory": True,
            "session_id": "test-session-id",
        }

        with patch("app.api.v1.chatbot.mem0_client") as mock_mem0:
            # Mock mem0 플랫폼 API 서비스
            mock_mem0.search_relevant_memories = AsyncMock(return_value=[])
            mock_mem0.add_conversation_message = AsyncMock(return_value={"success": True})
            mock_mem0.build_memory_context = MagicMock(return_value="")

            with patch("app.api.v1.chatbot.LLMClient") as mock_llm:
                # Mock LLM 스트리밍
                mock_llm_instance = mock_llm.return_value
                mock_llm_instance.stream_chat_with_filter = MagicMock()
                mock_llm_instance.stream_chat_with_filter.return_value.__aiter__.return_value = [
                    "안녕하세요! ",
                    "투자에 대해 ",
                    "설명드리겠습니다.",
                ]

                # API 호출
                response = client.post(
                    "/api/v1/chatbot/conversation?use_filter=true", json=request_data, headers=auth_headers
                )

        # Then: 성공 응답
        assert response.status_code == status.HTTP_200_OK
        assert "투자에 대해 설명드리겠습니다" in response.text

    def test_memory_status_endpoint(self, client, session, mock_firebase_token, auth_headers):
        """메모리 상태 조회 테스트 (플랫폼 API)"""
        # Given: 사용자 생성
        uid = mock_firebase_token.return_value.get("uid")
        db_user = crud_users.create(session, obj_in=UsersCreate(uid=uid, name="test-name", email="test-email"))
        session.commit()

        # 플랫폼 API 응답 구조에 맞는 메모리 데이터
        fake_memories = [
            {
                "id": "mem-1",
                "memory": "테스트 메모리 1",
                "metadata": {"session_id": "session-1", "timestamp": "2024-01-01T00:00:00Z"},
                "created_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": "mem-2",
                "memory": "테스트 메모리 2",
                "metadata": {"session_id": "session-2", "timestamp": "2024-01-01T01:00:00Z"},
                "created_at": "2024-01-01T01:00:00Z",
            },
        ]

        with patch("app.api.v1.chatbot.mem0_client") as mock_mem0:
            mock_mem0.get_user_memories = AsyncMock(return_value=fake_memories)

            # API 호출
            response = client.get("/api/v1/chatbot/memory/status", headers=auth_headers)

        # Then: 성공 응답
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == uid
        assert data["memory_count"] == 2
        assert len(data["memories"]) == 2

        # 플랫폼 API 구조 확인
        first_memory = data["memories"][0]
        assert "memory" in first_memory
        assert "metadata" in first_memory
        assert "created_at" in first_memory

    def test_memory_reset_endpoint(self, client, session, mock_firebase_token, auth_headers):
        """메모리 초기화 테스트 (플랫폼 API)"""
        # Given: 사용자 생성
        uid = mock_firebase_token.return_value.get("uid")
        db_user = crud_users.create(session, obj_in=UsersCreate(uid=uid, name="test-name", email="test-email"))
        session.commit()

        with patch("app.api.v1.chatbot.mem0_client") as mock_mem0:
            mock_mem0.reset_user_memory = AsyncMock(
                return_value={"success": True, "message": "사용자 user-123의 메모리가 초기화되었습니다."}
            )

            # API 호출
            response = client.delete("/api/v1/chatbot/memory/reset", headers=auth_headers)

        # Then: 성공 응답
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "메모리가 초기화" in data["message"]
