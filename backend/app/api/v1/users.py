from fastapi import APIRouter, Depends, HTTPException, status, Request, Path

from app.api.deps import get_or_create_user
from app.models.users import Users
from app.crud.crud_users import crud_users
from app.schemas.users import LevelUpdateRequest, LevelUpdateResponse
from app.constants import UserLevel
from app.core.config import LevelConfig


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


@user_router.get("/level/info")
async def get_user_level_info(
    db_user: Users = Depends(get_or_create_user),
):
    """
    사용자의 상세 레벨 정보를 조회합니다.
    
    현재 레벨, 경험치 현황, 다음 레벨 조건 등을 반환합니다.
    """
    level_info = crud_users.get_user_level_info(db_user)
    return level_info


@user_router.get("/level/fields")
async def get_available_exp_fields():
    """
    사용 가능한 경험치 필드 목록을 반환합니다.
    
    JSON 파일에서 정의된 모든 경험치 필드와 설명을 반환합니다.
    """
    return {
        "exp_fields": LevelConfig.get_exp_fields(),
        "field_names": LevelConfig.get_exp_field_names(),
        "level_conditions": LevelConfig.get_level_up_conditions()
    }


@user_router.put("/level/update")
async def update_user_level(
    request: Request,
    level_request: LevelUpdateRequest,
    db_user: Users = Depends(get_or_create_user),
) -> LevelUpdateResponse:
    """
    사용자 레벨 현황을 업데이트합니다.
    
    이벤트 타입에 따라 경험치를 증가시키고, 레벨업 조건을 체크하여 레벨업을 처리합니다.
    JSON 파일에서 정의된 경험치 필드만 사용 가능합니다.
    """
    try:
        session = request.state.db_session
        
        # 사용자 경험치 업데이트 및 레벨업 처리
        updated_user, level_up = crud_users.update_user_exp(
            db=session, 
            user=db_user, 
            event_type=level_request.event_type
        )
        
        # 다음 레벨 조건 정보
        level_up_config = LevelConfig.get_level_up_condition(updated_user.level)
        next_level_conditions = level_up_config.get("conditions", {}) if level_up_config else None
        
        # 응답 메시지 생성
        message = None
        if level_up:
            level_names = LevelConfig.get_level_names()
            level_name = level_names.get(updated_user.level.value, str(updated_user.level))
            message = f"축하합니다! {level_name} 레벨로 승급하셨습니다!"
        
        return LevelUpdateResponse(
            success=True,
            level_up=level_up,
            current_level=updated_user.level,
            exp=updated_user.exp,
            message=message,
            next_level_conditions=next_level_conditions
        )
        
    except ValueError as e:
        # 유효하지 않은 이벤트 타입 등의 검증 오류
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"레벨 업데이트 중 오류가 발생했습니다: {str(e)}"
        )
