from pydantic import BaseModel, validator
from typing import Optional, Dict, List
from enum import Enum

from app.constants import UserLevel
from app.core.config import LevelConfig


class UsersCreate(BaseModel):
    uid: str
    name: str
    email: str


class LevelUpdateRequest(BaseModel):
    event_type: str

    @validator('event_type')
    def validate_event_type(cls, v):
        """설정된 경험치 필드인지 검증"""
        if not LevelConfig.is_valid_exp_field(v):
            valid_fields = ', '.join(LevelConfig.get_exp_field_names())
            raise ValueError(f'유효하지 않은 이벤트 타입입니다. 가능한 값: {valid_fields}')
        return v


class LevelUpdateResponse(BaseModel):
    success: bool
    level_up: bool
    current_level: UserLevel
    exp: Dict[str, int]
    message: Optional[str] = None
    next_level_conditions: Optional[Dict[str, int]] = None  # 다음 레벨 조건 추가


class ExpFieldInfo(BaseModel):
    """경험치 필드 정보"""
    field_name: str
    display_name: str
    current_value: int
    required_for_next_level: Optional[int] = None


class UserLevelInfo(BaseModel):
    """사용자 레벨 정보 상세"""
    current_level: UserLevel
    level_display_name: str
    exp_fields: List[ExpFieldInfo]
    can_level_up: bool
    next_level: Optional[UserLevel] = None
