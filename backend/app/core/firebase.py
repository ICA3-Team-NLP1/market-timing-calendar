"""
Firebase 인증 관리
"""
from typing import Dict, Any, Optional
import firebase_admin
from firebase_admin import credentials, auth
from fastapi.logger import logger

from app.core.config import settings


class FirebaseAuthManager:
    """Firebase 인증 관리자"""

    def __init__(self):
        self.app = None
        self.initialize_firebase()

    def initialize_firebase(self):
        """Firebase 초기화"""
        try:
            if not firebase_admin._apps:
                # Firebase 서비스 계정 키 파일 경로
                firebase_key = settings.FIREBASE_SECRET_FILE

                if firebase_key:
                    # 서비스 계정 키 파일이 있는 경우
                    cred = credentials.Certificate(firebase_key)
                    self.app = firebase_admin.initialize_app(cred)
                    logger.info("Firebase 서비스 계정 키로 초기화 완료")
                else:
                    # 개발 환경에서 기본 자격증명 사용
                    logger.warning("Firebase 서비스 계정 키 파일이 없습니다. 개발 모드로 실행")
                    return
            else:
                self.app = firebase_admin.get_app()
                logger.info("기존 Firebase 앱 사용")

        except Exception as e:
            logger.error(f"Firebase 초기화 오류: {e}")
            raise

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Firebase ID 토큰 검증"""
        try:
            if not self.app:
                logger.error("Firebase가 초기화되지 않았습니다")
                return None

            # 토큰 검증
            decoded_token = auth.verify_id_token(token)

            # 사용자 정보 추출
            user_info = {
                "uid": decoded_token["uid"],
                "email": decoded_token.get("email"),
                "email_verified": decoded_token.get("email_verified", False),
                "name": decoded_token.get("name"),
                "picture": decoded_token.get("picture"),
                "firebase_claims": decoded_token,
            }

            logger.info(f"토큰 검증 성공: {user_info['email']}")
            return user_info

        except Exception as e:
            logger.error(f"토큰 검증 실패: {e}")
            return None

    def get_user_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """UID로 사용자 정보 조회"""
        try:
            if not self.app:
                return None

            user = auth.get_user(uid)

            user_info = {
                "uid": user.uid,
                "email": user.email,
                "email_verified": user.email_verified,
                "display_name": user.display_name,
                "photo_url": user.photo_url,
                "disabled": user.disabled,
                "creation_timestamp": user.user_metadata.creation_timestamp,
                "last_sign_in_timestamp": user.user_metadata.last_sign_in_timestamp,
            }

            return user_info

        except Exception as e:
            logger.error(f"사용자 정보 조회 실패: {e}")
            return None


# 전역 인스턴스
firebase_auth = FirebaseAuthManager()
