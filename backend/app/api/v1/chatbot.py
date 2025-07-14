from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.deps import get_or_create_user
from app.models.users import Users
from app.utils.llm_client import LLMClient
from app.constants import UserLevel


chatbot_router = APIRouter()

# Temporary system prompts per level
SYSTEM_PROMPTS = {
    UserLevel.BEGINNER: "당신은 주식 투자를 처음 접한 사용자를 돕는 친절한 조력자입니다.",
    UserLevel.INTERMEDIATE: "당신은 투자 경험이 어느 정도 있는 사용자를 위한 조력자입니다.",
    UserLevel.ADVANCED: "당신은 고급 투자 지식을 가진 사용자를 위한 전문 조력자입니다.",
}


class ChatMessage(BaseModel):
    role: str
    content: str


class ConversationRequest(BaseModel):
    history: List[ChatMessage] = []
    question: str


class EventExplainRequest(BaseModel):
    event_info: str


class EventFollowupRequest(BaseModel):
    history: List[ChatMessage] = []
    question: str


def _build_messages(level: UserLevel, history: List[ChatMessage], question: str):
    system_prompt = SYSTEM_PROMPTS.get(level, SYSTEM_PROMPTS[UserLevel.BEGINNER])
    messages = [{"role": "system", "content": system_prompt}]
    messages += [msg.dict() for msg in history]
    messages.append({"role": "user", "content": question})
    return messages


@chatbot_router.post("/conversation")
async def conversation(
    req: ConversationRequest, db_user: Users = Depends(get_or_create_user)
):
    messages = _build_messages(db_user.level, req.history, req.question)
    llm = LLMClient()

    async def stream():
        async for chunk in llm.stream_chat(messages):
            yield chunk

    return StreamingResponse(stream(), media_type="text/plain")


@chatbot_router.post("/event/explain")
async def explain_event(
    req: EventExplainRequest, db_user: Users = Depends(get_or_create_user)
):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPTS.get(db_user.level)},
        {"role": "user", "content": req.event_info},
    ]
    llm = LLMClient()
    answer = await llm.chat(messages)
    return {"answer": answer}


@chatbot_router.post("/event/followup")
async def event_followup(
    req: EventFollowupRequest, db_user: Users = Depends(get_or_create_user)
):
    messages = _build_messages(db_user.level, req.history, req.question)
    llm = LLMClient()
    answer = await llm.chat(messages)
    return {"answer": answer}
