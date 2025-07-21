from __future__ import annotations

import uuid
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_or_create_user, get_session
from app.models.users import Users
from app.utils.llm_client import LLMClient
from app.core.prompts import SYSTEM_PROMPTS, EVENT_EXPLAIN_PROMPTS
from app.constants import UserLevel, ChatMessageRole
from app.crud.crud_events import crud_events
from app.crud.crud_chat import crud_chat_sessions
from app.schemas.chatbot import *
from app.schemas.chat import *
from app.services.filter_service import FilterService
from app.services.mem0_service import mem0_service
from app.services.mem0_client import mem0_client

logger = logging.getLogger(__name__)


chatbot_router = APIRouter()


def _build_messages(
    level: UserLevel, history: List[ChatMessage], question: str, memory_context: str = None
) -> List[dict]:
    """대화 메시지 구성

    Args:
        level: 사용자 레벨
        history: 이전 대화 내역
        question: 새로운 질문

    Returns:
        LLM에 전달할 메시지 리스트
    """
    system_prompt = SYSTEM_PROMPTS.get(level, SYSTEM_PROMPTS[UserLevel.BEGINNER])
    if memory_context:
        system_prompt += f"\n\n[이전 대화 기억]\n{memory_context}"
    messages = [{"role": "system", "content": system_prompt}]
    messages += [msg.dict() for msg in history]
    messages.append({"role": "user", "content": question})
    return messages


@chatbot_router.post("/conversation")
async def conversation(
    req: ConversationRequest,
    use_filter: bool = Query(True, description="필터링 사용 여부"),
    is_mem0_api: bool = True,
    db_user: Users = Depends(get_or_create_user),
    session: Session = Depends(get_session),
):
    """대화 내역 기반 질문 처리

    사용자의 이전 대화 내역을 바탕으로 연속적인 질문에 대해 스트리밍 응답을 제공합니다.
    사용자 레벨에 따라 적절한 시스템 프롬프트를 사용하며, 컨텐츠 필터링을 적용합니다.

    Args:
        req: 대화 요청 (대화 내역, 질문, 안전 수준)
        use_filter: 필터링 적용 여부 (기본값: True)
        is_mem0_api: Mem0 API 사용 여부 (기본값: True)
        db_user: 현재 사용자 정보
        session: DB session
    """
    try:
        # 세션 처리 (새 세션이면 생성, 기존 세션이면 조회)
        user_uid = db_user.uid
        user_level = db_user.level
        if req.session_id:
            chat_session = crud_chat_sessions.get(session=session, session_id=req.session_id)
            if not chat_session:
                raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        else:
            # 새로운 세션 생성
            chat_session = crud_chat_sessions.create(
                session=session,
                obj_in=ChatSessionCreate(
                    user_id=db_user.id,
                    session_id=str(uuid.uuid4()),
                ),
            )
            session.commit()
            req.session_id = chat_session.session_id

        # mem0에서 관련 메모리 검색 (use_memory가 True인 경우)
        mem0_provider = mem0_client if is_mem0_api else mem0_service
        memory_context = None
        if req.use_memory:
            relevant_memories = await mem0_provider.search_relevant_memories(user_id=db_user.uid, query=req.question)

            if relevant_memories:
                memory_context = mem0_provider.build_memory_context(relevant_memories)
                logger.debug(f"🧠 관련 메모리 {len(relevant_memories)}개 발견")

        llm_client = LLMClient()

        async def stream():
            full_response = ""
            try:
                messages = _build_messages(user_level, req.history, req.question, memory_context)
                if use_filter:
                    # 필터링 적용된 스트리밍
                    async for chunk in llm_client.stream_chat_with_filter(messages, safety_level=req.safety_level):
                        full_response += chunk
                        yield chunk
                else:
                    # 기존 방식 (필터링 없음)
                    async for chunk in llm_client.stream_chat(messages):
                        full_response += chunk
                        yield chunk

                logger.debug(f"🎯 스트리밍 완료: {len(full_response)}글자")

                # 세션 메시지 카운트 업데이트 (user + assistant = 2)
                crud_chat_sessions.increment_message_count(session=session, session_id=req.session_id, count=2)

                # mem0에 대화 내용 추가
                if req.use_memory:
                    # 사용자 메시지 추가
                    messages = [
                        {"role": ChatMessageRole.user, "content": req.question},
                        {"role": ChatMessageRole.assistant, "content": full_response},
                    ]
                    await mem0_provider.add_conversation_message(
                        user_id=user_uid, messages=messages, session_id=req.session_id
                    )
                    logger.debug("🧠 mem0에 대화 내용 저장 완료")

                session.commit()

                # 추가 메타데이터를 헤더로 전송
                yield f"\n\n<!-- SESSION_ID: {req.session_id} -->"

            except Exception as e:
                logger.error(f"❌ 스트리밍 중 오류: {e}")
                session.rollback()
                yield f"\n\n죄송합니다. 응답 생성 중 오류가 발생했습니다."

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


@chatbot_router.get("/memory/status", response_model=MemoryStatusResponse)
async def get_memory_status(is_mem0_api: bool = True, db_user: Users = Depends(get_or_create_user)):
    """사용자의 mem0 메모리 상태 조회"""
    try:
        mem0_provider = mem0_client if is_mem0_api else mem0_service
        memories = await mem0_provider.get_user_memories(db_user.uid)

        return MemoryStatusResponse(
            user_id=db_user.uid, memory_count=len(memories), memories=memories[:10]  # 최근 10개만 표시
        )

    except Exception as e:
        logger.error(f"❌ 메모리 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="메모리 상태 조회 중 오류가 발생했습니다.")


@chatbot_router.delete("/memory/reset", response_model=MemoryResetResponse)
async def reset_user_memory(is_mem0_api: bool = True, db_user: Users = Depends(get_or_create_user)):
    """사용자의 mem0 메모리 초기화 (개발/테스트용)"""
    try:
        mem0_provider = mem0_client if is_mem0_api else mem0_service
        result = await mem0_provider.reset_user_memory(db_user.uid)

        if result["success"]:
            return MemoryResetResponse(success=True, message=result["message"])
        else:
            raise HTTPException(status_code=500, detail=result["error"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 메모리 초기화 실패: {e}")
        raise HTTPException(status_code=500, detail="메모리 초기화 중 오류가 발생했습니다.")
