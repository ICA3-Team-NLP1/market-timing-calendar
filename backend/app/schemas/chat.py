"""
대화 관련 스키마 정의
"""
from pydantic import BaseModel
from typing import Any


class ChatSessionCreate(BaseModel):
    """대화 세션 생성 스키마"""

    user_id: int
    session_id: str


class MemoryStatusResponse(BaseModel):
    """메모리 상태 응답 스키마"""

    user_id: str
    memory_count: int
    memories: list[dict[str, Any]]


class MemoryResetResponse(BaseModel):
    """메모리 초기화 응답 스키마"""

    success: bool
    message: str
