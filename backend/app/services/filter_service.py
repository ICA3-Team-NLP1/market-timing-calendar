import time
from typing import Dict, Any
from fastapi.logger import logger
from .content_filter import ContentFilter
from app.core.config import settings
from app.core.filter_logger import filter_logger_instance, log_filter_performance


class FilterService:
    """컨텐츠 필터링 서비스 - 비즈니스 로직 래퍼"""

    def __init__(self):
        self.filter = ContentFilter()
        self.enabled = settings.FILTER_ENABLED
        self.filter_logger = filter_logger_instance

        logger.info(f"FilterService 초기화: enabled={self.enabled}, level={settings.FILTER_SAFETY_LEVEL}")

    @log_filter_performance
    async def filter_response(self, content: str, safety_level: str = None, user_id: int = None) -> Dict[str, Any]:
        """
        컨텐츠 필터링 메인 메서드

        Args:
            content: 필터링할 컨텐츠
            safety_level: 안전 수준 (strict/moderate/permissive)
            user_id: 사용자 ID (로깅용)

        Returns:
            {
                "content": "필터링된 컨텐츠",
                "filtered": True/False,
                "safety_score": 0.0~1.0,
                "filter_reason": "필터링 이유",
                "risk_categories": ["카테고리1", "카테고리2"],
                "processing_time": 1.23,
                "retry_count": 2
            }
        """

        # 요청 로깅
        self.filter_logger.log_filter_request(
            content_length=len(content), user_id=user_id, safety_level=safety_level or settings.FILTER_SAFETY_LEVEL
        )

        # 필터링이 비활성화된 경우
        if not self.enabled:
            logger.info("필터링 비활성화됨 - 원본 컨텐츠 반환")
            result = {
                "content": content,
                "filtered": False,
                "safety_score": 1.0,
                "filter_reason": "필터링 비활성화",
                "risk_categories": [],
                "processing_time": 0.0,
                "retry_count": 0,
            }

            # 비활성화된 경우에도 로깅
            self.filter_logger.log_filter_result(result, 0.0, user_id)
            return result

        # 빈 컨텐츠 체크
        if not content or not content.strip():
            logger.warning("빈 컨텐츠 수신")
            result = {
                "content": "죄송합니다. 유효한 질문을 입력해주세요.",
                "filtered": True,
                "safety_score": 0.0,
                "filter_reason": "빈 컨텐츠",
                "risk_categories": ["empty_content"],
                "processing_time": 0.0,
                "retry_count": 0,
            }

            # 빈 컨텐츠도 로깅
            self.filter_logger.log_filter_result(result, 0.0, user_id)
            return result

        try:
            start_time = time.time()

            logger.info(f"필터링 시작: {len(content)}글자, level={safety_level or settings.FILTER_SAFETY_LEVEL}")

            # ContentFilter로 처리
            result = await self.filter.process(content, safety_level)

            processing_time = time.time() - start_time

            # 결과 포맷팅
            response = {
                "content": result.get("filtered_content", content),
                "filtered": not result.get("is_safe", True),
                "safety_score": result.get("safety_score", 0.0),
                "filter_reason": result.get("filter_reason", ""),
                "risk_categories": result.get("risk_categories", []),
                "processing_time": round(processing_time, 3),
                "retry_count": result.get("retry_count", 0),
            }

            logger.info(
                f"필터링 완료: filtered={response['filtered']}, "
                f"score={response['safety_score']}, "
                f"time={response['processing_time']}s"
            )

            # 상세 로깅 (성능 분석용)
            if result.get("analysis_result"):
                self.filter_logger.log_safety_analysis(
                    original_score=response["safety_score"],
                    final_score=response["safety_score"],  # 실제로는 원본과 최종이 다를 수 있음
                    analysis_details=result["analysis_result"],
                )

            # 필터링 결과 로깅 (데코레이터에서도 처리되지만 중복 방지를 위해 user_id 전달)
            self.filter_logger.log_filter_result(response, processing_time, user_id)

            return response

        except Exception as e:
            processing_time = time.time() - start_time if "start_time" in locals() else 0.0

            logger.error(f"필터링 서비스 오류: {e}")

            # 오류 로깅
            self.filter_logger.log_filter_error(
                error=e,
                content_length=len(content),
                user_id=user_id,
                context={"safety_level": safety_level, "processing_time": processing_time},
            )

            # 오류 발생시 안전한 기본 응답
            error_result = {
                "content": "죄송합니다. 현재 서비스 처리 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "filtered": True,
                "safety_score": 0.0,
                "filter_reason": f"서비스 오류: {str(e)}",
                "risk_categories": ["service_error"],
                "processing_time": processing_time,
                "retry_count": 0,
            }

            return error_result

    async def check_safety_only(self, content: str, user_id: int = None) -> Dict[str, Any]:
        """
        컨텐츠의 안전성만 검사 (필터링 없이)

        Args:
            content: 검사할 컨텐츠
            user_id: 사용자 ID (로깅용)

        Returns:
            안전성 분석 결과만 포함한 딕셔너리
        """

        # 안전성 검사 요청 로깅
        self.filter_logger.log_filter_request(
            content_length=len(content), user_id=user_id, safety_level="analysis_only"
        )

        if not self.enabled:
            return {"is_safe": True, "safety_score": 1.0, "risk_categories": [], "analysis_only": True}

        try:
            start_time = time.time()

            # 분석만 수행하는 간단한 상태로 초기화
            from .content_filter import FilterState

            state = FilterState(
                original_content=content,
                filtered_content="",
                is_safe=False,
                safety_score=0.0,
                filter_reason="",
                risk_categories=[],
                retry_count=0,
                safety_level=settings.FILTER_SAFETY_LEVEL,
                needs_replacement=False,
                analysis_result={},
                error_message="",
            )

            # 분석만 실행
            result = await self.filter._analyze_content(state)

            processing_time = time.time() - start_time

            analysis_result = {
                "is_safe": result.get("is_safe", False),
                "safety_score": result.get("safety_score", 0.0),
                "risk_categories": result.get("risk_categories", []),
                "filter_reason": result.get("filter_reason", ""),
                "analysis_only": True,
                "processing_time": round(processing_time, 3),
            }

            # 안전성 분석 로깅
            self.filter_logger.log_safety_analysis(
                original_score=analysis_result["safety_score"],
                final_score=analysis_result["safety_score"],
                analysis_details={
                    "analysis_only": True,
                    "risk_categories": analysis_result["risk_categories"],
                    "filter_reason": analysis_result["filter_reason"],
                },
            )

            return analysis_result

        except Exception as e:
            logger.error(f"안전성 검사 오류: {e}")

            # 오류 로깅
            self.filter_logger.log_filter_error(
                error=e, content_length=len(content), user_id=user_id, context={"operation": "safety_check_only"}
            )

            return {
                "is_safe": False,
                "safety_score": 0.0,
                "risk_categories": ["analysis_error"],
                "filter_reason": f"검사 오류: {str(e)}",
                "analysis_only": True,
                "processing_time": 0.0,
            }

    def get_filter_stats(self) -> Dict[str, Any]:
        """필터링 시스템 상태 정보 반환"""
        base_stats = {
            "enabled": self.enabled,
            "safety_level": settings.FILTER_SAFETY_LEVEL,
            "max_retries": settings.FILTER_MAX_RETRIES,
            "filter_model": settings.FILTER_LLM_MODEL,
            "filter_provider": settings.FILTER_LLM_PROVIDER or "default",
        }

        # 실시간 메트릭 추가
        runtime_metrics = self.filter_logger.get_metrics_summary()

        return {**base_stats, "runtime_metrics": runtime_metrics}

    def log_performance_summary(self):
        """성능 요약 로깅 (주기적 호출용)"""
        self.filter_logger.log_performance_metrics()

    def reset_metrics(self):
        """메트릭 초기화 (개발/테스트용)"""
        self.filter_logger.reset_metrics()
