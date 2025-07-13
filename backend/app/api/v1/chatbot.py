from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_or_create_user, get_session
from app.models.users import Users
from app.utils.llm_client import LLMClient
from app.core.prompts import SYSTEM_PROMPTS, EVENT_EXPLAIN_PROMPTS
from app.constants import UserLevel
from app.crud.crud_events import crud_events


chatbot_router = APIRouter()


class ChatMessage(BaseModel):
    """채팅 메시지 모델"""
    role: str  # "user" 또는 "assistant"
    content: str  # 메시지 내용


class ConversationRequest(BaseModel):
    """사용자 대화내역 기반 질문 요청
    
    사용자가 챗봇과 이전에 나눈 대화 내역을 바탕으로 
    연속적인 질문을 할 때 사용하는 요청 모델
    """
    history: List[ChatMessage] = []  # 이전 대화 내역
    question: str  # 사용자의 새로운 질문


class EventExplainRequest(BaseModel):
    """특정 이벤트(금융일정)에 대한 설명 요청
    
    특정 금융 이벤트나 경제 지표에 대한 설명을 요청할 때 사용하는 모델
    대화 내역 없이 단발성 질문으로 사용됨
    """
    release_id: str  # Events 테이블의 release_id (예: CPILFESL, UNRATE 등)


def _build_messages(level: UserLevel, history: List[ChatMessage], question: str) -> List[dict]:
    """대화 메시지 구성
    
    Args:
        level: 사용자 레벨
        history: 이전 대화 내역
        question: 새로운 질문
        
    Returns:
        LLM에 전달할 메시지 리스트
    """
    system_prompt = SYSTEM_PROMPTS.get(level, SYSTEM_PROMPTS[UserLevel.BEGINNER])
    messages = [{"role": "system", "content": system_prompt}]
    messages += [msg.dict() for msg in history]
    messages.append({"role": "user", "content": question})
    return messages


@chatbot_router.post("/conversation")
async def conversation(
    req: ConversationRequest, db_user: Users = Depends(get_or_create_user)
):
    """대화 내역 기반 질문 처리
    
    사용자의 이전 대화 내역을 바탕으로 연속적인 질문에 대해 스트리밍 응답을 제공합니다.
    사용자 레벨에 따라 적절한 시스템 프롬프트를 사용합니다.
    """
    messages = _build_messages(db_user.level, req.history, req.question)
    llm = LLMClient()

    async def stream():
        async for chunk in llm.stream_chat(messages):
            yield chunk

    return StreamingResponse(stream(), media_type="text/plain")


@chatbot_router.post("/event/explain")
async def explain_event(
    req: EventExplainRequest, 
    db_user: Users = Depends(get_or_create_user),
    db: Session = Depends(get_session)
):
    """금융 이벤트 설명
    
    특정 금융 이벤트나 경제 지표에 대한 설명을 스트리밍 응답으로 제공합니다.
    사용자 레벨에 따라 적절한 깊이의 설명을 제공합니다.
    """
    # release_id로 이벤트 조회
    event = crud_events.get_by_release_id(db, req.release_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with release_id '{req.release_id}' not found")
    
    # 이벤트 정보를 포맷팅하여 LLM에게 전달
    event_context = f"""이벤트 정보:
- 제목: {event.title}
- 설명: {event.description}
- 날짜: {event.date}
- 영향도: {event.impact}
- 출처: {event.source}
- Release ID: {event.release_id}

위 경제 지표/이벤트에 대해 설명해주세요."""
    
    system_prompt = EVENT_EXPLAIN_PROMPTS.get(db_user.level, EVENT_EXPLAIN_PROMPTS[UserLevel.BEGINNER])
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": event_context},
    ]
    llm = LLMClient()

    async def stream():
        async for chunk in llm.stream_chat(messages):
            yield chunk

    return StreamingResponse(stream(), media_type="text/plain")
