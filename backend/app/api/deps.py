from typing import Any
from fastapi.logger import logger
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.firebase import firebase_auth
from app.core.database import db
from app.crud.crud_users import crud_users
from app.schemas.users import UsersCreate


async def get_session(request: Request):
    db_session = next(db.session())
    request.state.db_session = db_session
    try:
        yield db_session
    finally:
        db_session.rollback()
        db_session.close()


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


async def get_or_create_user(
    request: Request,
    current_user=Depends(get_current_user),
    session=Depends(get_session),
) -> dict[str, Any]:
    """DB 유저 조회 or 생성"""
    uid = current_user.get("uid")
    db_user = crud_users.get(session, uid=uid)
    if not db_user:
        db_user = crud_users.create(
            session, obj_in=UsersCreate(uid=uid, name=current_user["name"], email=current_user["email"])
        )
        session.commit()
    request.state.uid = uid
    return db_user
