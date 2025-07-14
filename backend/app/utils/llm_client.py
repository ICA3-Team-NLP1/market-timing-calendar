from __future__ import annotations

from typing import AsyncGenerator, List, Dict

from app.core.llm import LLMFactory, LangfuseManager
from langchain_core.prompts import ChatPromptTemplate


class LLMClient:
    """Simple abstraction over OpenAI and Anthropic chat APIs."""

    def __init__(self) -> None:
        # core 모듈의 LLMFactory 사용 - 공통 로직 재사용
        self.llm = LLMFactory.create_llm()
        # Langfuse Manager 초기화
        self.langfuse_manager = LangfuseManager(service_name="backend_chatbot")

    def _create_chain(self, messages: List[Dict[str, str]]):
        """Chain 생성 공통 로직 (DRY 원칙 준수)"""
        # Langfuse input 추적을 위해 템플릿 변수 방식 사용
        if len(messages) == 1:
            # 단일 메시지인 경우
            prompt = ChatPromptTemplate.from_template("{user_input}")
        else:
            # 다중 메시지인 경우 (대화 히스토리 포함)
            prompt = ChatPromptTemplate.from_template(
                "Previous conversation:\n{conversation_history}\n\nUser: {user_input}"
            )
        return prompt | self.llm

    def _prepare_input_data(self, messages: List[Dict[str, str]]) -> Dict[str, str]:
        """메시지를 Langfuse input 형태로 변환"""
        if not messages:
            return {"user_input": ""}
        
        # 마지막 user 메시지 찾기
        user_input = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                user_input = msg["content"]
                break
        
        if len(messages) == 1:
            return {"user_input": user_input}
        else:
            # 대화 히스토리 구성 (마지막 user 메시지 제외)
            history_parts = []
            for msg in messages[:-1]:  # 마지막 메시지 제외
                role = "User" if msg["role"] == "user" else "Assistant"
                history_parts.append(f"{role}: {msg['content']}")
            
            conversation_history = "\n".join(history_parts)
            return {
                "conversation_history": conversation_history,
                "user_input": user_input
            }

    async def stream_chat(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Yield assistant message chunks using LCEL."""
        chain = self._create_chain(messages)
        
        # 메시지 분석 및 입력 데이터 구성
        input_data = self._prepare_input_data(messages)
        
        # Langfuse callback 설정 (공통 유틸리티 사용)
        config = self.langfuse_manager.get_callback_config()
        
        print(f"🚀 Backend stream_chat 시작: {len(messages)}개 메시지")
        print(f"📝 Input data: {input_data}")
        
        async for chunk in chain.astream(input_data, config=config):
            if chunk.content:
                yield chunk.content
        
        print(f"📊 Backend stream_chat 완료 - Langfuse 추적됨")

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Return full assistant message."""
        chain = self._create_chain(messages)
        
        # 메시지 분석 및 입력 데이터 구성
        input_data = self._prepare_input_data(messages)
        
        # Langfuse callback 설정 (공통 유틸리티 사용)
        config = self.langfuse_manager.get_callback_config()
        
        print(f"🚀 Backend chat 시작: {len(messages)}개 메시지")
        print(f"📝 Input data: {input_data}")
        
        result = await chain.ainvoke(input_data, config=config)
        
        print(f"📊 Backend chat 완료 - Langfuse 추적됨")
        
        return result.content if hasattr(result, "content") else str(result)
