from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_or_create_user, get_session
from app.models.users import Users
from app.utils.llm_client import LLMClient
from app.core.prompts import SYSTEM_PROMPTS, EVENT_EXPLAIN_PROMPTS
from app.constants import UserLevel
from app.crud.crud_events import crud_events
from app.schemas.chatbot import *
from app.services.filter_service import FilterService


chatbot_router = APIRouter()


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
    req: ConversationRequest,
    use_filter: bool = Query(True, description="필터링 사용 여부"),
    # db_user: Users = Depends(get_or_create_user),
):
    """대화 내역 기반 질문 처리

    사용자의 이전 대화 내역을 바탕으로 연속적인 질문에 대해 스트리밍 응답을 제공합니다.
    사용자 레벨에 따라 적절한 시스템 프롬프트를 사용하며, 컨텐츠 필터링을 적용합니다.

    Args:
        req: 대화 요청 (대화 내역, 질문, 안전 수준)
        use_filter: 필터링 적용 여부 (기본값: True)
        db_user: 현재 사용자 정보
    """
    try:
        messages = _build_messages(UserLevel.BEGINNER, req.history, req.question)
        llm_client = LLMClient()

        async def stream():
            if use_filter:
                # 필터링 적용된 스트리밍
                async for chunk in llm_client.stream_chat_with_filter(messages, safety_level=req.safety_level):
                    yield chunk
            else:
                # 기존 방식 (필터링 없음)
                async for chunk in llm_client.stream_chat(messages):
                    yield chunk

        return StreamingResponse(stream(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail="대화 처리 중 오류가 발생했습니다.")


@chatbot_router.post("/event/explain")
async def explain_event(
    req: EventExplainRequest,
    use_filter: bool = Query(True, description="필터링 사용 여부"),
    db_user: Users = Depends(get_or_create_user),
    db: Session = Depends(get_session),
):
    """금융 이벤트 설명

    특정 금융 이벤트나 경제 지표에 대한 설명을 스트리밍 응답으로 제공합니다.
    사용자 레벨에 따라 적절한 깊이의 설명을 제공하며, 컨텐츠 필터링을 적용합니다.

    Args:
        req: 이벤트 설명 요청 (Events 테이블의 id, 안전 수준)
        use_filter: 필터링 적용 여부 (기본값: True)
        db_user: 현재 사용자 정보
        db: 데이터베이스 세션
    """
    try:
        # id로 이벤트 조회
        event = crud_events.get(db, id=req.id)
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with id '{req.id}' not found")

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

        llm_client = LLMClient()

        async def stream():
            if use_filter:
                # 필터링 적용된 스트리밍
                async for chunk in llm_client.stream_chat_with_filter(messages, safety_level=req.safety_level):
                    yield chunk
            else:
                # 기존 방식 (필터링 없음)
                async for chunk in llm_client.stream_chat(messages):
                    yield chunk

        return StreamingResponse(stream(), media_type="text/plain")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="이벤트 설명 처리 중 오류가 발생했습니다.")


@chatbot_router.post("/safety/check")
async def check_content_safety(req: SafetyCheckRequest, _: Users = Depends(get_or_create_user)):
    """컨텐츠 안전성 검사

    주어진 컨텐츠의 안전성을 검사하고 위험 요소를 분석합니다.
    실제 필터링은 수행하지 않고 분석 결과만 반환합니다.

    Args:
        req: 안전성 검사 요청

    Returns:
        {
            "is_safe": true/false,
            "safety_score": 0.85,
            "risk_categories": ["investment_advice", "guaranteed_profit"],
            "filter_reason": "상세한 분석 결과",
            "analysis_only": true
        }
    """
    try:

        llm_client = LLMClient()
        result = await llm_client.check_content_safety(req.content)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail="안전성 검사 처리 중 오류가 발생했습니다.")


@chatbot_router.get("/filter/status")
async def get_filter_status(_: Users = Depends(get_or_create_user)):
    """필터링 시스템 상태 조회

    현재 필터링 시스템의 설정과 상태를 조회합니다.

    Returns:
        {
            "enabled": true,
            "safety_level": "strict",
            "max_retries": 3,
            "filter_model": "gpt-4",
            "filter_provider": "openai"
        }
    """
    try:
        filter_service = FilterService()
        status = filter_service.get_filter_stats()

        return status

    except Exception as e:
        raise HTTPException(status_code=500, detail="필터 상태 조회 중 오류가 발생했습니다.")
