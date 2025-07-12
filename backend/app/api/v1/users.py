from fastapi import APIRouter, Depends, HTTPException, status, Request, Path

from app.api.deps import get_or_create_user
from app.models.users import Users
from app.crud.crud_users import crud_users


user_router = APIRouter()


@user_router.get("/me")
async def get_user(db_user: Users = Depends(get_or_create_user)):
    """현재 사용자 정보 조회"""
    return db_user


@user_router.get("/{uid}")
async def get_user_by_uid(
    request: Request,
    uid: str = Path(title="User UID"),
    _: Users = Depends(get_or_create_user),
):
    """사용자 정보 조회"""
    session = request.state.db_session
    db_user = crud_users.get(session, uid=uid)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="찾을 수 없는 유저 입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db_user
