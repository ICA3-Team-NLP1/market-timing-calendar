import logging
from typing import Any
from datetime import datetime
from mem0 import Memory

from app.core.config import settings

logger = logging.getLogger(__name__)


class Mem0Service:
    """mem0를 사용한 대화 메모리 관리 서비스(오픈 소스)"""

    def __init__(self):
        """mem0 설정 및 초기화"""
        self.config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": settings.MEM0_LLM_MODEL,
                    "temperature": settings.MEM0_TEMPERATURE,
                    "max_tokens": settings.MEM0_MAX_TOKENS,
                    "api_key": settings.OPENAI_API_KEY,
                },
            },
            "vector_store": settings.MEM0_VECTOR_STORE,
            "version": "v1.1",
        }

        try:
            self.memory = Memory.from_config(self.config)
            logger.info("✅ mem0 서비스 초기화 완료")
        except Exception as e:
            logger.error(f"❌ mem0 서비스 초기화 실패: {e}")
            self.memory = None

    async def add_conversation_message(
        self, user_id: str, messages: list[str], session_id: str | None = None
    ) -> dict[str, Any]:
        """
        대화 메시지를 mem0에 추가

        Args:
            user_id: 사용자 ID
            messages: 메시지 내용
            session_id: 세션 ID (선택적)

        Returns:
            mem0 추가 결과
        """
        if not self.memory:
            logger.error("mem0가 초기화되지 않았습니다")
            return {"success": False, "error": "mem0 not initialized"}

        try:
            # 메타데이터 구성
            metadata = {"timestamp": datetime.now().isoformat(), "session_id": session_id}

            # mem0에 메시지 추가
            result = self.memory.add(messages, user_id=user_id, metadata=metadata)

            logger.debug(f"📝 mem0에 {len(messages)}개 메시지 추가: {messages[0].get('content')[:50] if messages else ''}...")
            return {"success": True, "result": result}

        except Exception as e:
            logger.error(f"❌ mem0 메시지 추가 실패: {e}")
            return {"success": False, "error": str(e)}

    async def search_relevant_memories(self, user_id: str, query: str) -> list[dict[str, Any]]:
        """
        현재 질문과 관련된 이전 메모리 검색

        Args:
            user_id: 사용자 ID
            query: 검색 쿼리

        Returns:
            관련 메모리 리스트
        """
        if not self.memory:
            logger.error("mem0가 초기화되지 않았습니다")
            return []

        try:
            limit = settings.MEM0_RELEVANT_MEMORY_LIMIT
            res = self.memory.search(query, user_id=user_id, limit=limit)
            memories = res.get("results", [])

            logger.debug(f"🔍 mem0 검색 완료: {len(memories)}개 메모리 발견")
            return memories

        except Exception as e:
            logger.error(f"❌ mem0 메모리 검색 실패: {e}")
            return []

    async def get_user_memories(self, user_id: str) -> list[dict[str, Any]]:
        """
        사용자의 모든 메모리 조회

        Args:
            user_id: 사용자 ID

        Returns:
            사용자 메모리 리스트
        """
        if not self.memory:
            logger.error("mem0가 초기화되지 않았습니다")
            return []

        try:
            res = self.memory.get_all(user_id=user_id)
            memories = res.get("results", [])
            logger.debug(f"📋 사용자 {user_id}의 총 {len(memories)}개 메모리 조회")
            return memories

        except Exception as e:
            logger.error(f"❌ 사용자 메모리 조회 실패: {e}")
            return []

    async def update_memory(self, memory_id: str, new_content: str) -> dict[str, Any]:
        """
        기존 메모리 업데이트

        Args:
            memory_id: 메모리 ID
            new_content: 새로운 내용
            user_id: 사용자 ID

        Returns:
            업데이트 결과
        """
        if not self.memory:
            logger.error("mem0가 초기화되지 않았습니다")
            return {"success": False, "error": "mem0 not initialized"}

        try:
            result = self.memory.update(memory_id=memory_id, data=new_content)

            logger.debug(f"🔄 메모리 업데이트 완료: {memory_id}")
            return {"success": True, "result": result}

        except Exception as e:
            logger.error(f"❌ 메모리 업데이트 실패: {e}")
            return {"success": False, "error": str(e)}

    async def delete_memory(self, memory_id: str) -> dict[str, Any]:
        """
        메모리 삭제

        Args:
            memory_id: 삭제할 메모리 ID

        Returns:
            삭제 결과
        """
        if not self.memory:
            logger.error("mem0가 초기화되지 않았습니다")
            return {"success": False, "error": "mem0 not initialized"}

        try:
            result = self.memory.delete(memory_id=memory_id)
            logger.debug(f"🗑️ 메모리 삭제 완료: {memory_id}")
            return {"success": True, "result": result}

        except Exception as e:
            logger.error(f"❌ 메모리 삭제 실패: {e}")
            return {"success": False, "error": str(e)}

    async def reset_user_memory(self, user_id: str) -> dict[str, Any]:
        """
        사용자의 모든 메모리 초기화 (개발/테스트용)

        Args:
            user_id: 사용자 ID

        Returns:
            초기화 결과
        """
        if not self.memory:
            logger.error("mem0가 초기화되지 않았습니다")
            return {"success": False, "error": "mem0 not initialized"}

        try:
            # 사용자의 모든 메모리 조회
            memories = await self.get_user_memories(user_id)
            deleted_count = 0

            # 각 메모리 삭제
            for memory in memories:
                delete_result = await self.delete_memory(memory["id"])
                if delete_result["success"]:
                    deleted_count += 1

            logger.info(f"🔄 사용자 {user_id}의 {deleted_count}개 메모리 초기화 완료")
            return {"success": True, "message": f"{deleted_count}개의 메모리가 삭제되었습니다."}

        except Exception as e:
            logger.error(f"❌ 사용자 메모리 초기화 실패: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def build_memory_context(memories: list[dict[str, Any]]) -> str:
        """
        메모리 리스트를 컨텍스트 문자열로 변환

        Args:
            memories: 메모리 리스트

        Returns:
            컨텍스트 문자열
        """
        if not memories:
            return ""

        context_parts = []
        for i, memory in enumerate(memories, 1):
            memory_text = memory.get("memory", "")
            score = memory.get("score", 0)
            context_parts.append(f"{i}. {memory_text} (관련도: {score:.2f})")

        return "\n".join(context_parts)


mem0_service = Mem0Service()
