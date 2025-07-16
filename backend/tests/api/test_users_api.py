"""
사용자 API 테스트
"""
from fastapi import status
from app.crud.crud_users import crud_users
from app.schemas.users import UsersCreate


class TestUsersAPI:
    """사용자 API 테스트 클래스"""

    def test_get_user_me_success(self, client, mock_firebase_token, auth_headers):
        """GET /users/me - 성공 케이스"""

        response = client.get("/api/v1/users/me", headers=auth_headers)

        # 응답 상태 코드 검증
        assert response.status_code == status.HTTP_200_OK

        # Mock 호출 검증 - firebase_auth 의존성 호출됨
        mock_firebase_token.assert_called_once()

    def test_get_user_me_unauthorized(self, client):
        """인증 실패 케이스"""

        # 인증 헤더 없이 요청
        response = client.get("/api/v1/users/me")

        # 401 Unauthorized 응답 확인
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_by_uid_success(self, client, mock_firebase_token, auth_headers, session):
        """GET /users/{uid} - 성공 케이스"""

        test_uid = "TEST_UID"

        crud_users.create(session, obj_in=UsersCreate(uid=test_uid, name="test-name", email="test-email"))
        session.commit()

        response = client.get(f"/api/v1/users/{test_uid}", headers=auth_headers)

        # 응답 검증
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("uid") == test_uid

    def test_get_user_by_uid_not_found(self, client, mock_firebase_token, auth_headers):
        """GET /users/{uid} - 사용자 없음 케이스"""

        response = client.get(f"/api/v1/users/NOT_FOUND", headers=auth_headers)

        # 응답 검증
        assert response.status_code == status.HTTP_404_NOT_FOUND
