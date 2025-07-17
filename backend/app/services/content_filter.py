import json
import logging
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END

from app.utils.llm_client import LLMClient
from app.core.config import settings
from app.core.filter_prompts import (
    SAFETY_ANALYSIS_PROMPT,
    CONTENT_REPLACEMENT_PROMPT,
    SAFETY_RECHECK_PROMPT,
    SAFETY_THRESHOLDS,
    RISK_CATEGORIES,
    SAFE_ALTERNATIVES,
    DISCLAIMER_TEMPLATE,
)

logger = logging.getLogger(__name__)


class FilterState(TypedDict):
    """필터링 프로세스의 상태를 관리하는 타입"""

    original_content: str  # 원본 컨텐츠
    filtered_content: str  # 필터링된 컨텐츠
    is_safe: bool  # 안전 여부
    safety_score: float  # 안전도 점수 (0.0-1.0)
    filter_reason: str  # 필터링 이유
    risk_categories: List[str]  # 위험 카테고리들
    retry_count: int  # 재시도 횟수
    safety_level: str  # 안전 수준 (strict/moderate/permissive)
    needs_replacement: bool  # 컨텐츠 대체 필요 여부
    analysis_result: Dict[str, Any]  # LLM 분석 결과
    error_message: str  # 오류 메시지


class ContentFilter:
    """LangGraph 기반 컨텐츠 필터링 시스템"""

    def __init__(self):
        self.llm_client = LLMClient()
        self.safety_threshold = SAFETY_THRESHOLDS.get(settings.FILTER_SAFETY_LEVEL, SAFETY_THRESHOLDS["strict"])
        self.max_retries = settings.FILTER_MAX_RETRIES
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """필터링 workflow 그래프 구성"""
        workflow = StateGraph(FilterState)

        # 노드들 추가
        workflow.add_node("analyze", self._analyze_content)
        workflow.add_node("filter", self._apply_filter)
        workflow.add_node("replace", self._replace_content)
        workflow.add_node("recheck", self._recheck_content)
        workflow.add_node("approve", self._approve_content)
        workflow.add_node("reject", self._reject_content)

        # 시작점 연결
        workflow.add_edge(START, "analyze")

        # 조건부 엣지들 설정
        workflow.add_conditional_edges(
            "analyze", self._route_after_analysis, {"safe": "approve", "unsafe": "filter", "error": "reject"}
        )

        workflow.add_conditional_edges(
            "filter", self._route_after_filter, {"replace": "replace", "reject": "reject", "retry": "analyze"}
        )

        workflow.add_conditional_edges(
            "replace", self._route_after_replace, {"recheck": "recheck", "approve": "approve", "error": "reject"}
        )

        workflow.add_conditional_edges(
            "recheck", self._route_after_recheck, {"approve": "approve", "retry": "replace", "reject": "reject"}
        )

        # 최종 노드들을 END로 연결
        workflow.add_edge("approve", END)
        workflow.add_edge("reject", END)

        return workflow.compile()

    async def process(self, content: str, safety_level: str = None) -> FilterState:
        """컨텐츠 필터링 메인 프로세스"""
        initial_state = FilterState(
            original_content=content,
            filtered_content="",
            is_safe=False,
            safety_score=0.0,
            filter_reason="",
            risk_categories=[],
            retry_count=0,
            safety_level=safety_level or settings.FILTER_SAFETY_LEVEL,
            needs_replacement=False,
            analysis_result={},
            error_message="",
        )

        try:
            # 그래프 실행 (recursion_limit 설정으로 무한루프 방지)
            config = {"recursion_limit": 50}  # 기본 25에서 50으로 증가
            result = await self.graph.ainvoke(initial_state, config=config)
            logger.info(f"필터링 완료: is_safe={result['is_safe']}, score={result['safety_score']}")
            return result

        except Exception as e:
            logger.error(f"필터링 프로세스 오류: {e}")
            # 디버그: 에러 발생 시 기본값으로 안전한 응답 생성
            return {
                "original_content": initial_state["original_content"],
                "filtered_content": "죄송합니다. 현재 답변을 제공할 수 없습니다.",
                "is_safe": False,
                "safety_score": 0.0,
                "filter_reason": f"시스템 오류: {str(e)}",
                "risk_categories": ["system_error"],
                "retry_count": initial_state["retry_count"],
                "safety_level": initial_state["safety_level"],
                "needs_replacement": False,
                "analysis_result": {},
                "error_message": str(e),
            }

    async def _analyze_content(self, state: FilterState) -> FilterState:
        """컨텐츠 안전성 분석"""
        try:
            # 디버그: 현재 재시도 상태 로깅 (재시도 카운트는 라우팅에서 관리)
            current_retry = state.get("retry_count", 0)
            if current_retry > 0:
                logger.info(f"재시도 분석 {current_retry}/{self.max_retries}: 컨텐츠 분석")

            logger.info(f"컨텐츠 분석 시작: {len(state['original_content'])}글자")

            # LLM에게 안전성 분석 요청
            prompt = SAFETY_ANALYSIS_PROMPT.format(content=state["original_content"])
            messages = [{"role": "user", "content": prompt}]

            response = await self.llm_client.chat(messages)

            # JSON 파싱
            try:
                analysis = json.loads(response)
            except json.JSONDecodeError:
                # JSON 파싱 실패시 텍스트에서 추출 시도
                analysis = self._extract_json_from_text(response)

                # 디버그: JSON 파싱 실패시 즉시 에러 처리로 라우팅되도록 설정
                if "parsing_error" in analysis.get("risk_categories", []):
                    logger.error("JSON 파싱 실패 - 에러 처리로 라우팅")
                    state.update(
                        {
                            "analysis_result": analysis,
                            "is_safe": False,
                            "safety_score": 0.0,
                            "filter_reason": analysis.get("filter_reason", "JSON 파싱 실패"),
                            "risk_categories": analysis.get("risk_categories", ["parsing_error"]),
                            "error_message": "JSON 파싱 실패",
                        }
                    )
                    return state

            # 결과 업데이트
            state.update(
                {
                    "analysis_result": analysis,
                    "is_safe": analysis.get("is_safe", False),
                    "safety_score": float(analysis.get("safety_score", 0.0)),
                    "filter_reason": analysis.get("filter_reason", ""),
                    "risk_categories": analysis.get("risk_categories", []),
                }
            )

            logger.info(f"분석 완료: safety_score={state['safety_score']}")
            return state

        except Exception as e:
            logger.error(f"컨텐츠 분석 오류: {e}")
            state.update({"error_message": f"분석 오류: {str(e)}", "is_safe": False})
            return state

    async def _apply_filter(self, state: FilterState) -> FilterState:
        """필터링 적용 로직"""
        logger.info("필터링 적용 중...")

        # 안전도 점수에 따른 처리 결정
        if state["safety_score"] < 0.3:
            # 매우 위험한 컨텐츠 - 완전 차단
            state["needs_replacement"] = False
            state["filtered_content"] = "죄송합니다. 해당 질문에 대한 답변을 제공할 수 없습니다."

        elif state["safety_score"] < self.safety_threshold:
            # 위험한 컨텐츠 - 대체 컨텐츠 생성 필요
            state["needs_replacement"] = True

        else:
            # 안전한 컨텐츠 - 그대로 통과 (임계값 재검토)
            state["is_safe"] = True
            state["filtered_content"] = state["original_content"]

        return state

    async def _replace_content(self, state: FilterState) -> FilterState:
        """위험한 컨텐츠를 안전한 대체 컨텐츠로 교체"""
        try:
            logger.info("대체 컨텐츠 생성 중...")

            prompt = CONTENT_REPLACEMENT_PROMPT.format(
                original_content=state["original_content"],
                risk_categories=", ".join(state["risk_categories"]),
                filter_reason=state["filter_reason"],
            )

            messages = [{"role": "user", "content": prompt}]
            replacement = await self.llm_client.chat(messages)

            # 면책 조항 추가
            replacement_with_disclaimer = replacement + DISCLAIMER_TEMPLATE

            state.update({"filtered_content": replacement_with_disclaimer, "needs_replacement": False})

            logger.info("대체 컨텐츠 생성 완료")
            return state

        except Exception as e:
            logger.error(f"대체 컨텐츠 생성 오류: {e}")
            state["error_message"] = f"대체 컨텐츠 생성 실패: {str(e)}"
            return state

    async def _recheck_content(self, state: FilterState) -> FilterState:
        """대체된 컨텐츠의 안전성 재검토"""
        try:
            logger.info("대체 컨텐츠 재검토 중...")

            prompt = SAFETY_RECHECK_PROMPT.format(modified_content=state["filtered_content"])

            messages = [{"role": "user", "content": prompt}]
            response = await self.llm_client.chat(messages)

            try:
                recheck_result = json.loads(response)
            except json.JSONDecodeError:
                recheck_result = self._extract_json_from_text(response)

            state.update(
                {
                    "is_safe": recheck_result.get("is_approved", False),
                    "safety_score": float(recheck_result.get("final_safety_score", 0.0)),
                }
            )

            logger.info(f"재검토 완료: is_approved={state['is_safe']}")
            return state

        except Exception as e:
            logger.error(f"재검토 오류: {e}")
            state["error_message"] = f"재검토 실패: {str(e)}"
            return state

    def _approve_content(self, state: FilterState) -> FilterState:
        """컨텐츠 승인"""
        logger.info("컨텐츠 승인됨")
        if not state.get("filtered_content"):
            state["filtered_content"] = state["original_content"]
        state["is_safe"] = True
        return state

    def _reject_content(self, state: FilterState) -> FilterState:
        """컨텐츠 거부"""
        logger.warning(f"컨텐츠 거부됨: {state.get('filter_reason', 'Unknown')}")
        state.update({"is_safe": False, "filtered_content": "죄송합니다. 해당 요청에 대한 답변을 제공할 수 없습니다."})
        return state

    # 라우팅 메서드들
    def _route_after_analysis(self, state: FilterState) -> str:
        """분석 후 라우팅"""
        if state.get("error_message"):
            return "error"
        elif state["is_safe"] and state["safety_score"] >= self.safety_threshold:
            return "safe"
        else:
            return "unsafe"

    def _route_after_filter(self, state: FilterState) -> str:
        """필터링 후 라우팅 (재시도 횟수 제한으로 무한루프 방지)"""
        # 디버그: 현재 재시도 횟수 로깅
        current_retry = state.get("retry_count", 0)
        logger.info(f"필터링 후 라우팅 - 재시도 횟수: {current_retry}/{self.max_retries}")

        if state.get("error_message"):
            logger.info("에러 메시지 존재 - reject 경로 선택")
            return "reject"
        elif state["needs_replacement"]:
            logger.info("컨텐츠 대체 필요 - replace 경로 선택")
            return "replace"
        elif current_retry < self.max_retries:
            # 재시도 횟수 라우팅 단계에서 미리 증가 (무한루프 방지)
            state["retry_count"] = current_retry + 1
            logger.info(f"재시도 시도 {state['retry_count']}/{self.max_retries} - retry 경로 선택")
            return "retry"
        else:
            # 최대 재시도 횟수 도달시 거부
            logger.warning(f"최대 재시도 횟수({self.max_retries}) 도달, 컨텐츠 거부")
            return "reject"

    def _route_after_replace(self, state: FilterState) -> str:
        """대체 후 라우팅"""
        if state.get("error_message"):
            return "error"
        elif state.get("filtered_content"):
            return "recheck"
        else:
            return "approve"

    def _route_after_recheck(self, state: FilterState) -> str:
        """재검토 후 라우팅"""
        if state.get("error_message"):
            return "reject"
        elif state["is_safe"]:
            return "approve"
        elif state["retry_count"] < self.max_retries:
            state["retry_count"] += 1
            return "retry"
        else:
            return "reject"

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """텍스트에서 JSON 추출 시도"""
        try:
            # 가장 간단한 케이스 - 전체가 JSON
            return json.loads(text)
        except:
            try:
                # JSON 블록 찾기
                start = text.find("{")
                end = text.rfind("}") + 1
                if start != -1 and end > start:
                    return json.loads(text[start:end])
            except:
                pass

        # 기본값 반환
        return {
            "is_safe": False,
            "safety_score": 0.0,
            "risk_categories": ["parsing_error"],
            "filter_reason": "JSON 파싱 실패",
        }
