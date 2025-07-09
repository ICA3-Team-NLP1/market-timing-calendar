from typing import Any
from fastapi.logger import logger
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.firebase import firebase_auth


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
) -> dict[str, Any]:
    """현재 로그인된 사용자 정보 반환"""
    try:
        token = credentials.credentials
        user_info = firebase_auth.verify_token(token)

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_info

    except Exception as e:
        logger.error(f"사용자 인증 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증에 실패했습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
