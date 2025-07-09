from typing import Dict, Any
from fastapi.logger import logger
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.firebase import firebase_auth
from app.api.deps import get_current_user


auth_router = APIRouter()


@auth_router.get("/me")
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """현재 사용자 정보 조회"""
    return {
        "success": True,
        "user": {
            "uid": current_user["uid"],
            "email": current_user["email"],
            "email_verified": current_user["email_verified"],
            "name": current_user["name"],
            "picture": current_user["picture"],
        },
    }


@auth_router.get("/user/{uid}")
async def get_user_by_uid(uid: str, _: Dict[str, Any] = Depends(get_current_user)):
    """
    UID로 사용자 정보 조회 (관리자용)
    # TODO 관리자 권한 제한 필요
    """
    try:
        user_info = firebase_auth.get_user_by_uid(uid)

        if not user_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다")

        return {"success": True, "user": user_info}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"사용자 조회 오류: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="사용자 조회 중 오류가 발생했습니다")
