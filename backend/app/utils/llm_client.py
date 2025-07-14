from __future__ import annotations

from typing import AsyncGenerator, List, Dict

from app.core.config import settings

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate



class LLMClient:
    """Simple abstraction over OpenAI and Anthropic chat APIs."""

    def __init__(self) -> None:
        self.provider = settings.ACTIVE_LLM_PROVIDER.lower()
        self.model = settings.ACTIVE_LLM_MODEL
        if self.provider == "openai":
            self.llm = ChatOpenAI(model=self.model, api_key=settings.OPENAI_API_KEY)
        elif self.provider == "anthropic":
            self.llm = ChatAnthropic(model=self.model, api_key=settings.ANTHROPIC_API_KEY)
        else:
            raise ValueError("Unsupported LLM provider")

    async def stream_chat(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Yield assistant message chunks using LCEL."""
        prompt = ChatPromptTemplate.from_messages([(m["role"], m["content"]) for m in messages])
        chain = prompt | self.llm
        async for chunk in chain.astream({}):
            if chunk.content:
                yield chunk.content

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Return full assistant message."""
        prompt = ChatPromptTemplate.from_messages([(m["role"], m["content"]) for m in messages])
        chain = prompt | self.llm
        result = await chain.ainvoke({})
        return result.content if hasattr(result, "content") else str(result)
