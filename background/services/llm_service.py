"""
LLM 서비스 - SOLID 원칙을 준수한 LLM 추론 로직
"""
import os
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# core 모듈의 공통 LLM 로직 사용
from app.core.llm import LLMFactory, BaseLLMProvider, LangfuseManager
from app.constants import UserLevel, ImpactLevel
from ..prompts.etl_prompts import impact_prompt, level_prompt, description_ko_prompt

logger = logging.getLogger(__name__)


class InferenceType(str, Enum):
    """추론 타입"""
    IMPACT = "impact"
    LEVEL = "level"
    DESCRIPTION_KO = "description_ko"


class BaseInferenceStrategy(ABC):
    """추론 전략 인터페이스 (Strategy Pattern)"""

    @abstractmethod
    def get_prompt_template(self) -> str:
        """프롬프트 템플릿 반환"""
        pass

    @abstractmethod
    def get_valid_values(self) -> list:
        """유효한 값들 반환"""
        pass

    @abstractmethod
    def get_default_value(self) -> str:
        """기본값 반환"""
        pass

    @abstractmethod
    def process_result(self, result: str) -> str:
        """결과 후처리"""
        pass


class ImpactInferenceStrategy(BaseInferenceStrategy):
    """영향도 추론 전략"""

    def get_prompt_template(self) -> str:
        return impact_prompt

    def get_valid_values(self) -> list:
        return [level.value for level in ImpactLevel]

    def get_default_value(self) -> str:
        return ImpactLevel.MEDIUM.value

    def process_result(self, result: str) -> str:
        result = result.strip().upper()
        if result in self.get_valid_values():
            return result
        return self.get_default_value()


class LevelInferenceStrategy(BaseInferenceStrategy):
    """레벨 추론 전략"""

    def get_prompt_template(self) -> str:
        return level_prompt

    def get_valid_values(self) -> list:
        return [level.value for level in UserLevel]

    def get_default_value(self) -> str:
        return UserLevel.ADVANCED.value

    def process_result(self, result: str) -> str:
        # NOTE: level_prompt가 JSON을 반환하므로, 후처리는 여기서 하지 않고
        # 이 메서드를 호출하는 쪽(EventMapper)에서 직접 처리합니다.
        # 따라서 여기서는 받은 결과를 그대로 반환합니다.
        return result


class DescriptionKoInferenceStrategy(BaseInferenceStrategy):
    """한글 설명 추론 전략"""

    def get_prompt_template(self) -> str:
        return description_ko_prompt

    def get_valid_values(self) -> list:
        return []  # 자유 형식 텍스트이므로 유효성 검사 없음

    def get_default_value(self) -> str:
        return "경제 지표 정보"  # 기본 설명

    def process_result(self, result: str) -> str:
        result = result.strip()
        if len(result) > 0:
            return result
        return self.get_default_value()


class RetryConfig:
    """재시도 설정 클래스 (Single Responsibility)"""

    def __init__(self, max_retries: int = 3, base_delay: float = 0.5):
        self.max_retries = max_retries
        self.base_delay = base_delay


class LLMInferenceService:
    """LLM 추론 서비스 (Single Responsibility + Dependency Injection)"""

    def __init__(
        self,
        provider: BaseLLMProvider,
        retry_config: Optional[RetryConfig] = None
    ):
        self.provider = provider
        self.retry_config = retry_config or RetryConfig()
        self._strategies = {
            InferenceType.IMPACT: ImpactInferenceStrategy(),
            InferenceType.LEVEL: LevelInferenceStrategy(),
            InferenceType.DESCRIPTION_KO: DescriptionKoInferenceStrategy(),
        }
        # Langfuse Manager 초기화
        self.langfuse_manager = LangfuseManager(service_name="background_etl")

    def infer(
        self,
        inference_type: InferenceType,
        release_name: str,
        series_info: Dict[str, Any]
    ) -> str:
        """안전한 추론 실행 (DRY 원칙 준수)"""
        strategy = self._strategies[inference_type]

        for attempt in range(self.retry_config.max_retries):
            try:
                return self._execute_inference(strategy, release_name, series_info)
            except Exception as e:
                logger.warning(
                    f"[{inference_type.value} 추론] LLM 호출 실패 "
                    f"(시도 {attempt + 1}/{self.retry_config.max_retries}): {e}"
                )

                if attempt < self.retry_config.max_retries - 1:
                    wait_time = self.retry_config.base_delay * (2 ** attempt)
                    logger.info(f"[{inference_type.value} 추론] {wait_time}초 후 재시도...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"[{inference_type.value} 추론] 모든 재시도 실패, 기본값 반환")
                    return strategy.get_default_value()

    def _execute_inference(
        self,
        strategy: BaseInferenceStrategy,
        release_name: str,
        series_info: Dict[str, Any]
    ) -> str:
        """실제 추론 실행 (Private 메서드로 캡슐화)"""
        llm = self.provider.create_llm()

        prompt_template = ChatPromptTemplate.from_template(strategy.get_prompt_template())
        chain = prompt_template | llm | StrOutputParser()

        # 입력 데이터 준비
        input_data = {
            "title": series_info.get("title", ""),
            "name": release_name,
            "notes": series_info.get("notes", ""),
            "source": series_info.get("source", "")
        }

        # Langfuse callback 설정 (공통 유틸리티 사용)
        config = self.langfuse_manager.get_callback_config()

        logger.info(f"🚀 LLM 예측 시작: title={input_data['title']}, name={input_data['name']}")
        logger.info(f"📝 Config: {config}")

        # LLM 호출 및 Langfuse 추적
        try:
            result = chain.invoke(input_data, config=config)
            logger.info(f"✅ LLM 호출 성공: raw_result type={type(result)}")
        except Exception as e:
            logger.error(f"❌ LLM 호출 실패: {e}")
            raise

        processed_result = strategy.process_result(result)

        logger.info(f"🎯 LLM 예측 결과: {processed_result}")

        # Background 작업이므로 수동으로 flush (중요!)
        self.langfuse_manager.flush_events()

        logger.info(f"📊 Langfuse 추적 완료 - 대시보드에서 확인 가능")

        return processed_result


class LLMServiceFactory:
    """LLM 서비스 팩토리 (Factory Pattern + Configuration)"""

    @classmethod
    def create_service(cls) -> LLMInferenceService:
        """설정을 기반으로 LLM 서비스 생성"""
        # core 모듈의 Factory 사용, temperature=0으로 ETL용 설정
        provider = LLMFactory.create_provider(
            provider_type=None,  # 기본값 사용 (settings에서 읽음)
            model=None,          # 기본값 사용 (settings에서 읽음)
            temperature=0        # ETL용으로 deterministic하게
        )

        retry_config = RetryConfig(
            max_retries=int(os.getenv('LLM_MAX_RETRIES', '3')),
            base_delay=float(os.getenv('LLM_API_DELAY', '0.5'))
        )

        return LLMInferenceService(provider, retry_config) 
