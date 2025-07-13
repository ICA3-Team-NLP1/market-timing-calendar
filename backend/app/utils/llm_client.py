from __future__ import annotations

from typing import AsyncGenerator, List, Dict

from app.core.llm import LLMFactory
from langchain_core.prompts import ChatPromptTemplate


class LLMClient:
    """Simple abstraction over OpenAI and Anthropic chat APIs."""

    def __init__(self) -> None:
        # core 모듈의 LLMFactory 사용 - 공통 로직 재사용
        self.llm = LLMFactory.create_llm()

    def _create_chain(self, messages: List[Dict[str, str]]):
        """Chain 생성 공통 로직 (DRY 원칙 준수)"""
        prompt = ChatPromptTemplate.from_messages([(m["role"], m["content"]) for m in messages])
        return prompt | self.llm

    async def stream_chat(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Yield assistant message chunks using LCEL."""
        chain = self._create_chain(messages)
        async for chunk in chain.astream({}):
            if chunk.content:
                yield chunk.content

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Return full assistant message."""
        chain = self._create_chain(messages)
        result = await chain.ainvoke({})
        return result.content if hasattr(result, "content") else str(result)
