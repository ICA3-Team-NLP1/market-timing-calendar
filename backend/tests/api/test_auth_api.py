import pytest
from fastapi import status


class TestAuthAPI:
    """인증 API 테스트 클래스"""

    def test_get_me_success(self, client, mock_firebase_token, auth_headers):
        """GET /auth/me - 성공 케이스"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        # 응답 상태 코드 검증
        assert response.status_code == status.HTTP_200_OK

        # 응답 데이터 검증
        data = response.json()
        assert data["success"] is True
        assert "user" in data
        assert data["user"] == mock_firebase_token.return_value

        # Mock 호출 검증
        mock_firebase_token.assert_called_once()

    def test_get_me_unauthorized(self, client):
        """GET /auth/me - 인증 실패 케이스"""

        # 인증 헤더 없이 요청
        response = client.get("/api/v1/auth/me")

        # 401 Unauthorized 응답 확인
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
