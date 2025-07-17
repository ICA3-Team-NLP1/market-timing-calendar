"""
필터링 시스템 전용 로깅 및 모니터링
"""
import logging
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps

# 전용 로거 생성
filter_logger = logging.getLogger("filter_system")


class FilterLogger:
    """필터링 시스템 전용 로깅 클래스"""

    def __init__(self):
        self.logger = filter_logger
        self._setup_logger()

        # 메트릭 저장소 (실제로는 Redis나 DB에 저장)
        self.metrics = {
            "total_requests": 0,
            "filtered_requests": 0,
            "processing_times": [],
            "error_count": 0,
            "safety_scores": [],
        }

    def _setup_logger(self):
        """로거 설정"""
        if not self.logger.handlers:
            # 콘솔 핸들러
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # 포맷터 설정
            formatter = logging.Formatter(
                "%(asctime)s - [FILTER] - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.INFO)

    def log_filter_request(self, content_length: int, user_id: Optional[int] = None, safety_level: str = "strict"):
        """필터링 요청 로깅"""
        self.logger.info(
            f"🔍 필터링 요청 | " f"사용자: {user_id or 'anonymous'} | " f"컨텐츠 길이: {content_length}자 | " f"안전 수준: {safety_level}"
        )
        self.metrics["total_requests"] += 1

    def log_filter_result(self, result: Dict[str, Any], processing_time: float, user_id: Optional[int] = None):
        """필터링 결과 로깅"""
        is_filtered = result.get("filtered", False)
        safety_score = result.get("safety_score", 0.0)
        risk_categories = result.get("risk_categories", [])

        # 상태에 따른 로그 레벨 결정
        if is_filtered:
            log_level = logging.WARNING
            status_emoji = "⚠️"
            self.metrics["filtered_requests"] += 1
        else:
            log_level = logging.INFO
            status_emoji = "✅"

        # 로그 메시지 구성
        self.logger.log(
            log_level,
            f"{status_emoji} 필터링 완료 | "
            f"사용자: {user_id or 'anonymous'} | "
            f"필터링됨: {is_filtered} | "
            f"안전도: {safety_score:.2f} | "
            f"처리시간: {processing_time:.3f}초 | "
            f"위험요소: {', '.join(risk_categories) if risk_categories else 'None'}",
        )

        # 메트릭 업데이트
        self.metrics["processing_times"].append(processing_time)
        self.metrics["safety_scores"].append(safety_score)

        # 처리시간이 너무 긴 경우 경고
        if processing_time > 5.0:
            self.logger.warning(f"🐌 처리시간 지연 | " f"처리시간: {processing_time:.3f}초 | " f"사용자: {user_id}")

    def log_filter_error(
        self,
        error: Exception,
        content_length: int,
        user_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """필터링 오류 로깅"""
        self.logger.error(
            f"❌ 필터링 오류 | "
            f"사용자: {user_id or 'anonymous'} | "
            f"컨텐츠 길이: {content_length}자 | "
            f"오류: {str(error)} | "
            f"컨텍스트: {json.dumps(context or {}, ensure_ascii=False)}"
        )
        self.metrics["error_count"] += 1

    def log_safety_analysis(self, original_score: float, final_score: float, analysis_details: Dict[str, Any]):
        """안전성 분석 상세 로깅"""
        score_improvement = final_score - original_score

        self.logger.info(
            f"🔬 안전성 분석 | "
            f"원본 점수: {original_score:.2f} | "
            f"최종 점수: {final_score:.2f} | "
            f"개선도: {score_improvement:+.2f} | "
            f"분석: {json.dumps(analysis_details, ensure_ascii=False)}"
        )

    def log_performance_metrics(self):
        """성능 메트릭 로깅 (주기적 호출용)"""
        if self.metrics["total_requests"] == 0:
            return

        # 통계 계산
        processing_times = self.metrics["processing_times"]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        max_processing_time = max(processing_times) if processing_times else 0

        safety_scores = self.metrics["safety_scores"]
        avg_safety_score = sum(safety_scores) / len(safety_scores) if safety_scores else 0

        filter_rate = (self.metrics["filtered_requests"] / self.metrics["total_requests"]) * 100
        error_rate = (self.metrics["error_count"] / self.metrics["total_requests"]) * 100

        self.logger.info(
            f"📊 필터링 성능 메트릭 | "
            f"총 요청: {self.metrics['total_requests']} | "
            f"필터링률: {filter_rate:.1f}% | "
            f"오류율: {error_rate:.1f}% | "
            f"평균 처리시간: {avg_processing_time:.3f}초 | "
            f"최대 처리시간: {max_processing_time:.3f}초 | "
            f"평균 안전도: {avg_safety_score:.2f}"
        )

    def get_metrics_summary(self) -> Dict[str, Any]:
        """메트릭 요약 반환"""
        processing_times = self.metrics["processing_times"]
        safety_scores = self.metrics["safety_scores"]

        return {
            "total_requests": self.metrics["total_requests"],
            "filtered_requests": self.metrics["filtered_requests"],
            "filter_rate": (self.metrics["filtered_requests"] / max(self.metrics["total_requests"], 1)) * 100,
            "error_count": self.metrics["error_count"],
            "error_rate": (self.metrics["error_count"] / max(self.metrics["total_requests"], 1)) * 100,
            "avg_processing_time": sum(processing_times) / len(processing_times) if processing_times else 0,
            "max_processing_time": max(processing_times) if processing_times else 0,
            "avg_safety_score": sum(safety_scores) / len(safety_scores) if safety_scores else 0,
            "min_safety_score": min(safety_scores) if safety_scores else 0,
            "timestamp": datetime.now().isoformat(),
        }

    def reset_metrics(self):
        """메트릭 초기화"""
        self.metrics = {
            "total_requests": 0,
            "filtered_requests": 0,
            "processing_times": [],
            "error_count": 0,
            "safety_scores": [],
        }
        self.logger.info("📊 필터링 메트릭 초기화됨")


# 전역 필터 로거 인스턴스
filter_logger_instance = FilterLogger()


def log_filter_performance(func):
    """필터링 성능 로깅 데코레이터"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = await func(*args, **kwargs)
            processing_time = time.time() - start_time

            # 결과가 딕셔너리이고 필터링 결과를 포함하는 경우
            if isinstance(result, dict) and "filtered" in result:
                filter_logger_instance.log_filter_result(result, processing_time, kwargs.get("user_id"))

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            filter_logger_instance.log_filter_error(
                e,
                len(str(args[0]) if args else ""),
                kwargs.get("user_id"),
                {"function": func.__name__, "processing_time": processing_time},
            )
            raise

    return wrapper


class FilterMetricsCollector:
    """필터링 메트릭 수집기"""

    @staticmethod
    def collect_langfuse_metrics(
        content: str, filter_result: Dict[str, Any], langfuse_manager, session_id: Optional[str] = None
    ):
        """Langfuse에 필터링 메트릭 전송"""
        try:
            # Langfuse에 필터링 결과 추적
            if hasattr(langfuse_manager, "handler") and langfuse_manager.handler:

                # 필터링 관련 메타데이터 구성
                filter_metadata = {
                    "filter_applied": filter_result.get("filtered", False),
                    "safety_score": filter_result.get("safety_score", 0.0),
                    "processing_time": filter_result.get("processing_time", 0.0),
                    "risk_categories": filter_result.get("risk_categories", []),
                    "retry_count": filter_result.get("retry_count", 0),
                    "content_length": len(content),
                    "timestamp": datetime.now().isoformat(),
                }

                # Langfuse 이벤트 생성 (실제 구현은 Langfuse API에 따라 다름)
                filter_logger_instance.logger.info(
                    f"📊 Langfuse 메트릭 전송 | "
                    f"세션: {session_id} | "
                    f"메타데이터: {json.dumps(filter_metadata, ensure_ascii=False)}"
                )

        except Exception as e:
            filter_logger_instance.logger.warning(f"⚠️ Langfuse 메트릭 전송 실패: {e}")

    @staticmethod
    def collect_api_metrics(endpoint: str, method: str, response_time: float, status_code: int, filter_applied: bool):
        """API 호출 메트릭 수집"""
        filter_logger_instance.logger.info(
            f"🌐 API 메트릭 | "
            f"엔드포인트: {method} {endpoint} | "
            f"응답시간: {response_time:.3f}초 | "
            f"상태코드: {status_code} | "
            f"필터 적용: {filter_applied}"
        )
