import logging
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from app.utils.llm_client import LLMClient
from app.constants import UserLevel
from app.core.prompts import SYSTEM_PROMPTS, SEARCH_DECISION_PROMPT
from app.services.simple_search import search_web

# Langfuse observe 데코레이터 임포트
try:
    from langfuse import observe

    LANGFUSE_OBSERVE_AVAILABLE = True
except ImportError:
    LANGFUSE_OBSERVE_AVAILABLE = False
    observe = None

logger = logging.getLogger(__name__)


class LevelChainState(TypedDict):
    """레벨별 체인 상태 - 순수 레벨별 로직"""

    user_level: UserLevel
    user_query: str
    conversation_history: list[dict[str, str]]
    memory_context: str
    final_response: str

    # 레벨별 전처리 상태
    needs_search: bool
    search_results: str
    tools_used: list[str]
    processing_step: str
    error_message: str


class BaseLevelChain:
    """레벨별 LLM 체인 - LLMClient 활용으로 Langfuse 추적 포함"""

    def __init__(self, user_level: UserLevel, user=None, langfuse_manager=None, recursion_limit=30):
        self.llm_client = LLMClient(user=user, langfuse_manager=langfuse_manager)
        self.user_level = user_level
        self.user = user
        self.langfuse_manager = langfuse_manager
        self.graph = self._build_graph()
        self.config = {"recursion_limit": recursion_limit}

    def _build_graph(self) -> StateGraph:
        """기본 더미 그래프 - 각 레벨에서 오버라이드하여 사용"""
        workflow = StateGraph(LevelChainState)

        # 🎯 간단한 더미 노드 - 실제로는 각 레벨에서 구현
        workflow.add_node("dummy_response", self._dummy_response)
        workflow.add_edge(START, "dummy_response")
        workflow.add_edge("dummy_response", END)

        return workflow.compile()

    @staticmethod
    async def _dummy_response(state: LevelChainState) -> LevelChainState:
        """더미 응답 - 실제로는 각 레벨에서 구현된 메서드가 사용됨"""
        state["final_response"] = "각 레벨에서 구현된 그래프를 사용해야 합니다."
        state["tools_used"].append("dummy")
        return state

    @staticmethod
    def _finalize_response(state: LevelChainState) -> LevelChainState:
        """공통 응답 최종화 - 모든 레벨에서 재사용"""
        logger.info(f"응답 최종화: {state.get('user_level', 'unknown')}")
        state["processing_step"] = "완료"

        if not state.get("final_response"):
            state["final_response"] = "죄송합니다. 응답을 생성할 수 없습니다."

        return state

    @staticmethod
    async def _web_search(state: LevelChainState) -> LevelChainState:
        """웹 검색"""
        try:
            logger.info("웹 검색 실행")
            state["processing_step"] = "web_search"

            search_results = await search_web(state["user_query"])
            state["search_results"] = search_results
            state["tools_used"].append("web_search")

            logger.info("웹 검색 완료")
            return state

        except Exception as e:
            logger.error(f"❌ 웹 검색 오류: {e}")
            state["search_results"] = f"검색 오류: {str(e)}"
            state["tools_used"].append("web_search_failed")
            return state

    @staticmethod
    def _route_analysis(state: LevelChainState) -> str:
        """분석 후 라우팅"""
        if state.get("error_message"):
            return "response"  # 오류 시 기본 응답
        elif state["needs_search"]:
            return "search"
        else:
            return "response"

    @ observe() if LANGFUSE_OBSERVE_AVAILABLE else lambda func: func
    async def process(
        self,
        user_level: UserLevel,
        user_query: str,
        conversation_history: list[dict[str, str]] = None,
        memory_context: str = None,
    ) -> LevelChainState:
        """레벨별 체인 처리 - Langfuse 추적 포함"""

        # Langfuse 메타데이터 설정 (LLMClient 패턴과 동일)
        if LANGFUSE_OBSERVE_AVAILABLE and self.langfuse_manager:
            self.langfuse_manager.update_current_trace(
                name="level_chain_process",
                input_data={
                    "user_level": user_level.value,
                    "query_length": len(user_query),
                    "has_memory": bool(memory_context),
                    "history_count": len(conversation_history or []),
                    "service": "level_chain",
                },
            )
        initial_state = LevelChainState(
            user_level=user_level,
            user_query=user_query,
            conversation_history=conversation_history or [],
            memory_context=memory_context or "",
            final_response="",
            needs_search=False,
            search_results="",
            tools_used=[],
            processing_step="시작",
            error_message="",
        )

        try:
            # 그래프 실행

            result = await self.graph.ainvoke(initial_state, config=self.config)

            # Langfuse 결과 업데이트 (LLMClient 패턴과 동일)
            if LANGFUSE_OBSERVE_AVAILABLE and self.langfuse_manager:
                self.langfuse_manager.update_current_trace(
                    output_data={
                        "status": "completed",
                        "tools_used": result.get("tools_used", []),
                        "response_length": len(result.get("final_response", "")),
                    }
                )

            logger.info(f"레벨별 체인 완료: level={user_level.value}, tools={result['tools_used']} (Langfuse 추적됨)")
            return result

        except Exception as e:
            logger.error(f"레벨별 체인 오류: {e}")
            # 오류 처리
            return {
                **initial_state,
                "final_response": "죄송합니다. 현재 답변을 제공할 수 없습니다.",
                "error_message": str(e),
                "processing_step": "오류",
            }

    def _get_system_prompt(self) -> str:
        # 레벨별 시스템 프롬프트 반환
        return SYSTEM_PROMPTS.get(self.user_level, "")

    async def _generate_response(self, state: LevelChainState) -> LevelChainState:
        """LLM 응답 - 기존 LLMClient 기능 그대로 활용"""
        try:
            state["processing_step"] = "LLM 응답 생성"

            # 시스템 프롬프트 준비
            system_prompt = self._get_system_prompt()

            # 메모리 컨텍스트 추가 (이전 대화 기억)
            if state["memory_context"]:
                system_prompt += f"\n\n[이전 대화 기억]\n{state['memory_context']}"

            # 🔍 실전러의 경우 검색 결과 추가 (AdvancedLevelChain에서만 해당)
            if hasattr(self, "user_level") and self.user_level == UserLevel.ADVANCED and state.get("search_results"):
                system_prompt += f"\n\n[실시간 시장 정보 및 최신 데이터]\n{state['search_results']}"
                state["tools_used"].append("llm_with_search")
            else:
                state["tools_used"].append("llm_basic")

            # 메시지 구성 (기존 LLMClient 방식과 동일)
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(state["conversation_history"])
            messages.append({"role": "user", "content": state["user_query"]})

            # 🎯 LLMClient 직접 활용 - Langfuse 추적 자동 포함!
            response = await self.llm_client.chat(messages)

            state["final_response"] = response
            return state

        except Exception as e:
            logger.error(f"응답 생성 실패: {e}")
            state["error_message"] = f"응답 생성 실패: {str(e)}"
            state["final_response"] = "죄송합니다. 현재 답변을 제공할 수 없습니다."
            return state

    async def _analyze_query(self, state: LevelChainState) -> LevelChainState:
        """AI를 통한 웹 검색 필요성 판단"""
        try:
            logger.info("AI 기반 쿼리 분석")
            state["processing_step"] = "AI 쿼리 분석"

            user_query = state["user_query"]

            # AI에게 검색 필요성 질문
            messages = [{"role": "user", "content": SEARCH_DECISION_PROMPT.format(user_query=user_query)}]
            # TODO 저렴한 모델로 교체 고려 필요
            ai_decision = await self.llm_client.chat(messages)

            # AI 응답 분석 (YES/NO 판단)
            ai_decision_clean = ai_decision.strip().upper()
            needs_search = "YES" in ai_decision_clean

            state["needs_search"] = needs_search
            state["tools_used"].append("ai_search_analysis")

            logger.info(f"AI 분석 완료: needs_search={needs_search}, AI 응답='{ai_decision_clean}'")
            return state

        except Exception as e:
            logger.error(f"AI 쿼리 분석 오류: {e}")
            state["error_message"] = f"AI 분석 오류: {str(e)}"
            # 오류 시 안전하게 검색하지 않음으로 설정
            state["needs_search"] = False
            return state


class BeginnerLevelChain(BaseLevelChain):
    """🔰 주린이 전용 체인 - 기존 LLM 체인 역할 대체"""

    def _build_graph(self) -> StateGraph:
        """주린이용 최단 워크플로우 - 복잡한 분석 없이 바로 LLM 응답"""
        workflow = StateGraph(LevelChainState)

        # 🎯 간단한 직선 플로우 - 분석이나 검색 없이 바로 LLM 호출
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("finalize", self._finalize_response)

        # 직선 연결: START → LLM 응답 → 최종화 → END
        workflow.add_edge(START, "generate_response")
        workflow.add_edge("generate_response", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()


class IntermediateLevelChain(BaseLevelChain):
    """📈 관심러 전용 체인"""

    def _build_graph(self) -> StateGraph:
        # TODO 주린이 전용 체인과 차별화 필요
        workflow = StateGraph(LevelChainState)

        # 📈 간단한 직선 플로우 - 검색 없이 기본 LLM 응답만
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("finalize", self._finalize_response)

        # 직선 연결: START → LLM 응답 → 최종화 → END
        workflow.add_edge(START, "generate_response")
        workflow.add_edge("generate_response", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()


class AdvancedLevelChain(BaseLevelChain):
    """🎯 실전러 전용 체인 - 웹 검색 기능 포함"""

    def _build_graph(self) -> StateGraph:
        """실전러용 고급 워크플로우 - 검색 키워드 감지 시 웹 검색 수행"""
        workflow = StateGraph(LevelChainState)

        # 🎯 실전러 전용 노드들
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("web_search", self._web_search)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("finalize", self._finalize_response)

        # 플로우 구성: 분석 → 조건부 검색 → LLM 응답
        workflow.add_edge(START, "analyze_query")

        # 실전러 전용 라우팅
        workflow.add_conditional_edges(
            "analyze_query",
            self._route_analysis,
            {"search": "web_search", "response": "generate_response"},
        )

        # 검색 후 고급 응답 생성
        workflow.add_edge("web_search", "generate_response")
        workflow.add_edge("generate_response", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()


class LevelChainService:
    """레벨별 LLM 체인 서비스"""

    def __init__(self, user=None, langfuse_manager=None):
        self.user = user
        self.langfuse_manager = langfuse_manager

    def get_chain(self, user_level: UserLevel) -> BaseLevelChain:
        """레벨에 맞는 체인 반환"""

        if user_level == UserLevel.BEGINNER:
            return BeginnerLevelChain(user_level=user_level, user=self.user, langfuse_manager=self.langfuse_manager)
        elif user_level == UserLevel.INTERMEDIATE:
            return IntermediateLevelChain(user_level=user_level, user=self.user, langfuse_manager=self.langfuse_manager)
        elif user_level == UserLevel.ADVANCED:
            return AdvancedLevelChain(user_level=user_level, user=self.user, langfuse_manager=self.langfuse_manager)
        else:
            raise NotImplementedError

    @ observe() if LANGFUSE_OBSERVE_AVAILABLE else lambda func: func
    async def run(
        self,
        user_level: UserLevel,
        user_query: str,
        conversation_history: list[dict[str, str]] = None,
        memory_context: str = None,
    ) -> str:
        """
        레벨별 체인 실행
        """
        level_chain = self.get_chain(user_level)

        # Langfuse 메타데이터 설정 (최상위 호출)
        if LANGFUSE_OBSERVE_AVAILABLE and self.langfuse_manager:
            self.langfuse_manager.update_current_trace(
                name="level_chain_run", input_data={"user_level": user_level.value, "service": "level_chain_service"}
            )

        # 빈 쿼리 체크
        if not user_query or not user_query.strip():
            return "죄송합니다. 유효한 질문을 입력해주세요."

        try:
            logger.info(f"레벨별 체인 시작: level={user_level.value}")

            # LevelChain으로 처리
            result = await level_chain.process(
                user_level=user_level,
                user_query=user_query,
                conversation_history=conversation_history,
                memory_context=memory_context,
            )

            final_response = result.get("final_response", "응답 생성 실패")

            logger.info(f"레벨별 체인 완료: level={user_level.value}, tools={result.get('tools_used', [])}")
            return final_response

        except Exception as e:
            logger.error(f"레벨별 체인 서비스 오류: {e}")
            return f"죄송합니다. 오류가 발생했습니다: {str(e)}"
