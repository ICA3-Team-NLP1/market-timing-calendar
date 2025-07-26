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
                # Firebase 서비스 계정 키 설정
                firebase_key = settings.FIREBASE_SECRET_FILE

                if firebase_key and isinstance(firebase_key, dict):
                    # 서비스 계정 키가 딕셔너리 형태로 있는 경우
                    cred = credentials.Certificate(firebase_key)
                    self.app = firebase_admin.initialize_app(cred)
                    logger.info("✅ Firebase 서비스 계정 키로 초기화 완료")
                else:
                    # 개발 환경에서 Firebase 없이 실행
                    logger.warning("⚠️ Firebase 서비스 계정 키가 없습니다. 개발 모드로 실행")
                    self.app = None
                    return
            else:
                self.app = firebase_admin.get_app()
                logger.info("✅ 기존 Firebase 앱 사용")

        except Exception as e:
            logger.error(f"❌ Firebase 초기화 오류: {e}")
            # Firebase 초기화 실패해도 앱은 계속 실행
            self.app = None
            logger.warning("⚠️ Firebase 없이 계속 실행합니다.")

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Firebase ID 토큰 검증"""
        try:
            if not self.app:
                logger.warning("⚠️ Firebase가 초기화되지 않았습니다. 토큰 검증을 건너뜁니다.")
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

            logger.info(f"✅ 토큰 검증 성공: {user_info['email']}")
            return user_info

        except Exception as e:
            logger.error(f"❌ 토큰 검증 실패: {e}")
            return None

    def get_user_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """UID로 사용자 정보 조회"""
        try:
            if not self.app:
                logger.warning("⚠️ Firebase가 초기화되지 않았습니다. 사용자 조회를 건너뜁니다.")
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
            logger.error(f"❌ 사용자 정보 조회 실패: {e}")
            return None


# 전역 인스턴스
firebase_auth = FirebaseAuthManager()
