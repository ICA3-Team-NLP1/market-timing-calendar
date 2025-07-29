#!/usr/bin/env python3
"""Background LLM Service - ETL 작업용 LLM 추상화"""

import logging
import asyncio
import time
from typing import Dict, List, Optional, Any
from enum import Enum

from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import LLMFactory, BaseLLMProvider, LangfuseManager

# Langfuse observe 데코레이터 임포트
try:
    from langfuse import observe
    LANGFUSE_OBSERVE_AVAILABLE = True
except ImportError:
    LANGFUSE_OBSERVE_AVAILABLE = False
    observe = None

logger = logging.getLogger(__name__)


class InferenceType(str, Enum):
    """추론 타입 (기존 호환성 유지)"""
    IMPACT = "impact"
    LEVEL = "level"
    DESCRIPTION_KO = "description_ko"


class BackgroundLLMService:
    """Background ETL 작업용 LLM 서비스"""

    def __init__(self, task_id: str = None, langfuse_manager: Optional[LangfuseManager] = None):
        # core 모듈의 LLMFactory 사용 - 공통 로직 재사용
        self.llm = LLMFactory.create_llm()
        # Langfuse Manager 초기화 (의존성 주입 또는 기본 생성)
        self.langfuse_manager = langfuse_manager or LangfuseManager.create_for_background()
        
        # Background에서 Celery task_id 자동 감지
        if task_id:
            self.langfuse_manager.session_id = task_id

    def _create_chain(self, prompt_template: str):
        """Chain 생성 공통 로직"""
        prompt = ChatPromptTemplate.from_template(prompt_template)
        return prompt | self.llm

    @observe() if LANGFUSE_OBSERVE_AVAILABLE else lambda func: func
    async def process_with_llm_observed(self, prompt_template: str, input_data: Dict[str, Any]) -> str:
        """@observe() 데코레이터를 사용한 LLM 처리"""
        if LANGFUSE_OBSERVE_AVAILABLE and self.langfuse_manager:
            # trace 메타데이터 설정
            self.langfuse_manager.update_current_trace(
                name="background_llm_process",
                input_data={"prompt_template": prompt_template, "input_data": input_data, "service": "background_etl"}
            )

        chain = self._create_chain(prompt_template)
        config = self.langfuse_manager.get_callback_config()

        logger.info(f"🚀 Background LLM 처리 시작: {len(input_data)}개 입력")
        logger.info(f"👤 User ID: {self.langfuse_manager.user_id}, Session ID: {self.langfuse_manager.session_id}")

        result = await chain.ainvoke(input_data, config=config)

        if LANGFUSE_OBSERVE_AVAILABLE and self.langfuse_manager:
            self.langfuse_manager.update_current_trace(output_data={"status": "completed"})

        logger.info(f"📊 Background LLM 처리 완료 - Langfuse 추적됨")

        return result.content if hasattr(result, "content") else str(result)

    async def process_with_llm(self, prompt_template: str, input_data: Dict[str, Any]) -> str:
        """LLM을 사용하여 데이터 처리"""
        # @observe() 데코레이터가 사용 가능한 경우 새로운 메서드 사용
        if LANGFUSE_OBSERVE_AVAILABLE:
            return await self.process_with_llm_observed(prompt_template, input_data)

        # 기존 방식 (fallback)
        chain = self._create_chain(prompt_template)
        config = self.langfuse_manager.get_callback_config()

        logger.info(f"🚀 Background LLM 처리 시작: {len(input_data)}개 입력")
        logger.info(f"👤 User ID: {self.langfuse_manager.user_id}, Session ID: {self.langfuse_manager.session_id}")

        result = await chain.ainvoke(input_data, config=config)

        logger.info(f"📊 Background LLM 처리 완료 - Langfuse 추적됨")

        return result.content if hasattr(result, "content") else str(result)

    async def process_fred_data(self, fred_data: Dict[str, Any]) -> Dict[str, Any]:
        """FRED 데이터를 LLM으로 분석"""
        prompt_template = """
        다음 경제 데이터를 분석하여 인사이트를 제공해주세요:
        
        데이터: {data}
        
        분석 요청: {analysis_request}
        
        다음 형식으로 응답해주세요:
        - 주요 트렌드: 
        - 시장 영향: 
        - 투자자 관점: 
        """

        input_data = {
            "data": str(fred_data),
            "analysis_request": "경제 지표의 현재 상태와 향후 전망을 분석해주세요."
        }

        result = await self.process_with_llm(prompt_template, input_data)
        
        return {
            "analysis": result,
            "raw_data": fred_data,
            "processed_at": "2024-01-01"  # 실제로는 현재 시간 사용
        }

    async def process_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """이벤트 데이터를 LLM으로 분석"""
        prompt_template = """
        다음 이벤트 데이터를 분석하여 시장 영향도를 평가해주세요:
        
        이벤트: {event_data}
        
        분석 요청: {analysis_request}
        
        다음 형식으로 응답해주세요:
        - 이벤트 중요도: 
        - 시장 영향도: 
        - 투자자 주의사항: 
        """

        input_data = {
            "event_data": str(event_data),
            "analysis_request": "이 이벤트가 시장에 미칠 영향을 분석해주세요."
        }

        result = await self.process_with_llm(prompt_template, input_data)
        
        return {
            "analysis": result,
            "raw_data": event_data,
            "processed_at": "2024-01-01"  # 실제로는 현재 시간 사용
        }

    def flush_events(self):
        """Langfuse 이벤트를 서버로 전송"""
        if self.langfuse_manager:
            self.langfuse_manager.flush_events()
            logger.info(f"📤 Langfuse 이벤트 서버 전송 완료")


# 기존 코드와의 호환성을 위한 LLMInferenceService 어댑터
class LLMInferenceService:
    """기존 코드와의 호환성을 위한 어댑터 클래스"""

    def __init__(self, background_service: BackgroundLLMService = None):
        self.background_service = background_service or BackgroundLLMService()

    def infer(self, inference_type: InferenceType, release_name: str, series_info: Dict[str, Any]) -> str:
        """기존 infer 메서드 호환성 유지"""
        try:
            # 동기 방식으로 실행
            if inference_type == InferenceType.IMPACT:
                return self._infer_impact_sync(release_name, series_info)
            elif inference_type == InferenceType.LEVEL:
                return self._infer_level_sync(release_name, series_info)
            elif inference_type == InferenceType.DESCRIPTION_KO:
                return self._infer_description_ko_sync(release_name, series_info)
            else:
                logger.warning(f"지원하지 않는 추론 타입: {inference_type}")
                return "MEDIUM"  # 기본값
        except Exception as e:
            logger.error(f"추론 실패 ({inference_type}): {e}")
            return "MEDIUM"  # 기본값

    def _infer_impact_sync(self, release_name: str, series_info: Dict[str, Any]) -> str:
        """영향도 추론 (동기 방식)"""
        prompt_template = """
        다음 경제 지표의 시장 영향도를 평가해주세요.
        
        예시:
        지표명: Consumer Price Index
        제목: Consumer Price Index for All Urban Consumers: All Items
        설명: Measures the average change over time in the prices paid by urban consumers for a market basket of consumer goods and services.
        출처: U.S. Bureau of Labor Statistics
        응답: HIGH
        
        지표명: Industrial Production
        제목: Industrial Production: Manufacturing
        설명: Measures the real output of all relevant establishments located in the United States.
        출처: Board of Governors of the Federal Reserve System
        응답: MEDIUM
        
        지표명: Housing Starts
        제목: Housing Starts: Total: New Privately Owned Housing Units Started
        설명: The number of new residential construction projects that have begun during any particular month.
        출처: U.S. Census Bureau
        응답: MEDIUM
        
        지표명: {name}
        제목: {title}
        설명: {notes}
        출처: {source}
        
        다음 중 하나로만 응답해주세요: HIGH, MEDIUM, LOW
        """
        
        input_data = {
            "name": release_name,
            "title": series_info.get("title", ""),
            "notes": series_info.get("notes", ""),
            "source": series_info.get("source", "")
        }
        
        # 동기 방식으로 LLM 호출
        chain = self.background_service._create_chain(prompt_template)
        config = self.background_service.langfuse_manager.get_callback_config()

        result = chain.invoke(input_data, config=config)
        raw_response = result.content.strip().upper() if hasattr(result, "content") else str(result).strip().upper()
        
        # String parsing으로 정확한 값 추출
        return self._parse_impact_response(raw_response)
    
    def _parse_impact_response(self, response: str) -> str:
        """영향도 응답 파싱 및 정규화"""
        # 정확한 값이 있는 경우
        if response in ["HIGH", "MEDIUM", "LOW"]:
            return response
        
        # 응답에서 키워드 검색
        if "HIGH" in response:
            return "HIGH"
        elif "MEDIUM" in response:
            return "MEDIUM"
        elif "LOW" in response:
            return "LOW"
        
        # 기본값 (가장 안전한 옵션): "MEDIUM"은 균형잡힌 영향도를 나타냅니다.
        # 과대평가(HIGH)나 과소평가(LOW)의 위험을 최소화하여 잘못된 우선순위나
        # 리소스 할당으로 인한 문제를 방지합니다.
        return "MEDIUM"

    def _infer_level_sync(self, release_name: str, series_info: Dict[str, Any]) -> str:
        """레벨 추론 (JSON 응답, 동기 방식)"""
        prompt_template = """
        다음 경제 지표의 사용자 레벨을 분류해주세요:
        
        지표명: {name}
        제목: {title}
        설명: {notes}
        출처: {source}
        
        다음 JSON 형식으로 응답해주세요:
        {{
            "level": "BEGINNER|INTERMEDIATE|ADVANCED",
            "level_category": "분류명"
        }}
        """
        
        input_data = {
            "name": release_name,
            "title": series_info.get("title", ""),
            "notes": series_info.get("notes", ""),
            "source": series_info.get("source", "")
        }
        
        # 동기 방식으로 LLM 호출
        chain = self.background_service._create_chain(prompt_template)
        config = self.background_service.langfuse_manager.get_callback_config()

        result = chain.invoke(input_data, config=config)
        return result.content if hasattr(result, "content") else str(result)

    def _infer_description_ko_sync(self, release_name: str, series_info: Dict[str, Any]) -> str:
        """한글 설명 추론 (동기 방식)"""
        prompt_template = """
        다음 경제 지표에 대한 간단한 한글 설명을 작성해주세요:
        
        지표명: {name}
        제목: {title}
        설명: {notes}
        출처: {source}
        
        일반인이 이해할 수 있는 간단한 설명으로 작성해주세요.
        """
        
        input_data = {
            "name": release_name,
            "title": series_info.get("title", ""),
            "notes": series_info.get("notes", ""),
            "source": series_info.get("source", "")
        }
        
        # 동기 방식으로 LLM 호출
        chain = self.background_service._create_chain(prompt_template)
        config = self.background_service.langfuse_manager.get_callback_config()

        result = chain.invoke(input_data, config=config)
        return result.content.strip() if hasattr(result, "content") else str(result).strip()

    # 기존 async 메서드들 (호환성 유지)
    def _infer_impact(self, release_name: str, series_info: Dict[str, Any]) -> str:
        """영향도 추론 (async 방식)"""
        prompt_template = """
        다음 경제 지표의 시장 영향도를 평가해주세요.
        
        예시:
        지표명: Consumer Price Index
        제목: Consumer Price Index for All Urban Consumers: All Items
        설명: Measures the average change over time in the prices paid by urban consumers for a market basket of consumer goods and services.
        출처: U.S. Bureau of Labor Statistics
        응답: HIGH
        
        지표명: Industrial Production
        제목: Industrial Production: Manufacturing
        설명: Measures the real output of all relevant establishments located in the United States.
        출처: Board of Governors of the Federal Reserve System
        응답: MEDIUM
        
        지표명: Housing Starts
        제목: Housing Starts: Total: New Privately Owned Housing Units Started
        설명: The number of new residential construction projects that have begun during any particular month.
        출처: U.S. Census Bureau
        응답: MEDIUM
        
        지표명: {name}
        제목: {title}
        설명: {notes}
        출처: {source}
        
        다음 중 하나로만 응답해주세요: HIGH, MEDIUM, LOW
        """
        
        input_data = {
            "name": release_name,
            "title": series_info.get("title", ""),
            "notes": series_info.get("notes", ""),
            "source": series_info.get("source", "")
        }
        
        result = asyncio.run(self.background_service.process_with_llm(prompt_template, input_data))
        raw_response = result.strip().upper()
        
        # String parsing으로 정확한 값 추출
        return self._parse_impact_response(raw_response)

    def _infer_level(self, release_name: str, series_info: Dict[str, Any]) -> str:
        """레벨 추론 (JSON 응답, async 방식)"""
        prompt_template = """
        다음 경제 지표의 사용자 레벨을 분류해주세요:
        
        지표명: {name}
        제목: {title}
        설명: {notes}
        출처: {source}
        
        다음 JSON 형식으로 응답해주세요:
        {{
            "level": "BEGINNER|INTERMEDIATE|ADVANCED",
            "level_category": "분류명"
        }}
        """
        
        input_data = {
            "name": release_name,
            "title": series_info.get("title", ""),
            "notes": series_info.get("notes", ""),
            "source": series_info.get("source", "")
        }
        
        result = asyncio.run(self.background_service.process_with_llm(prompt_template, input_data))
        return result

    def _infer_description_ko(self, release_name: str, series_info: Dict[str, Any]) -> str:
        """한글 설명 추론 (async 방식)"""
        prompt_template = """
        다음 경제 지표에 대한 간단한 한글 설명을 작성해주세요:
        
        지표명: {name}
        제목: {title}
        설명: {notes}
        출처: {source}
        
        일반인이 이해할 수 있는 간단한 설명으로 작성해주세요.
        """
        
        input_data = {
            "name": release_name,
            "title": series_info.get("title", ""),
            "notes": series_info.get("notes", ""),
            "source": series_info.get("source", "")
        }
        
        result = asyncio.run(self.background_service.process_with_llm(prompt_template, input_data))
        return result.strip()


# 기존 코드와의 호환성을 위한 LLMServiceFactory 클래스
class LLMServiceFactory:
    """LLM 서비스 팩토리 (기존 코드 호환성 유지)"""

    @staticmethod
    def create_service() -> LLMInferenceService:
        """LLMInferenceService 생성 (어댑터 사용)"""
        background_service = BackgroundLLMService()
        return LLMInferenceService(background_service) 
