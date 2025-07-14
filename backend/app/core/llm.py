"""
LLM 공통 모듈 - Provider Factory와 기본 인터페이스
"""
import os
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from app.core.config import settings

# Langfuse 임포트 (선택적)
try:
    from langfuse.langchain import CallbackHandler
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    CallbackHandler = None

logger = logging.getLogger(__name__)


class LangfuseManager:
    """Langfuse 관련 공통 유틸리티"""
    
    def __init__(self, service_name: str = "llm"):
        self.service_name = service_name
        self.handler: Optional[CallbackHandler] = None
        self._initialize_handler()
    
    def _initialize_handler(self) -> None:
        """Langfuse CallbackHandler 초기화"""
        if not LANGFUSE_AVAILABLE:
            logger.info(f"[{self.service_name}] Langfuse가 설치되지 않음, 모니터링 비활성화")
            return
        
        try:
            # 필수 설정이 있는 경우에만 Langfuse handler 생성
            if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
                # Settings에서 읽은 값을 환경변수로 설정 (Langfuse가 읽을 수 있도록)
                self._set_environment_variables()
                
                # CallbackHandler 생성 및 테스트
                self.handler = CallbackHandler()
                logger.info(f"✅ [{self.service_name}] Langfuse CallbackHandler 생성 성공: {type(self.handler)}")
                
            else:
                logger.info(f"[{self.service_name}] Langfuse 키가 설정되지 않음, 모니터링 비활성화")
        except Exception as e:
            logger.warning(f"[{self.service_name}] Langfuse 초기화 실패: {e}")
            import traceback
            logger.warning(f"[{self.service_name}] 상세 오류: {traceback.format_exc()}")
    
    def _set_environment_variables(self) -> None:
        """Langfuse 환경변수 설정"""
        os.environ['LANGFUSE_PUBLIC_KEY'] = settings.LANGFUSE_PUBLIC_KEY
        os.environ['LANGFUSE_SECRET_KEY'] = settings.LANGFUSE_SECRET_KEY
        os.environ['LANGFUSE_HOST'] = settings.LANGFUSE_HOST
        
        logger.info(f"✅ [{self.service_name}] Langfuse 환경변수 설정 완료: {settings.LANGFUSE_HOST}")
        logger.info(f"🔑 [{self.service_name}] Public Key: {settings.LANGFUSE_PUBLIC_KEY[:15]}...")
    
    def get_callback_config(self) -> dict:
        """LLM 호출에 사용할 callback config 반환"""
        config = {}
        if self.handler:
            config["callbacks"] = [self.handler]
            logger.info(f"🎯 [{self.service_name}] Langfuse callback 설정됨: {type(self.handler)}")
        else:
            logger.warning(f"⚠️ [{self.service_name}] Langfuse handler가 없음 - 모니터링 불가")
        return config
    
    def flush_events(self) -> None:
        """Langfuse 이벤트를 서버로 전송 (Background 작업용)"""
        if not self.handler:
            return
            
        try:
            from langfuse import get_client
            client = get_client()
            if client:
                client.flush()
                logger.info(f"📤 [{self.service_name}] Langfuse 이벤트 서버 전송 완료")
        except Exception as e:
            logger.warning(f"⚠️ [{self.service_name}] Langfuse flush 실패: {e}")
    
    @property
    def is_available(self) -> bool:
        """Langfuse handler가 사용 가능한지 확인"""
        return self.handler is not None


class LLMProviderType(str, Enum):
    """LLM 프로바이더 타입"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class BaseLLMProvider(ABC):
    """LLM 프로바이더 인터페이스"""
    
    @abstractmethod
    def create_llm(self) -> Any:
        """LLM 인스턴스 생성"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM 프로바이더"""
    
    def __init__(self, model: str, temperature: float = 0, **kwargs):
        self.model = model
        self.temperature = temperature
        self.kwargs = kwargs
    
    def create_llm(self) -> ChatOpenAI:
        # 환경변수 설정 (background 서비스와 호환성 유지)
        if settings.OPENAI_API_KEY:
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        
        return ChatOpenAI(
            model=self.model, 
            temperature=self.temperature,
            api_key=settings.OPENAI_API_KEY,
            **self.kwargs
        )


class AnthropicProvider(BaseLLMProvider):
    """Anthropic LLM 프로바이더"""
    
    def __init__(self, model: str, temperature: float = 0, **kwargs):
        self.model = model
        self.temperature = temperature
        self.kwargs = kwargs
    
    def create_llm(self) -> ChatAnthropic:
        # 환경변수 설정 (background 서비스와 호환성 유지)
        if settings.ANTHROPIC_API_KEY:
            os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
            
        return ChatAnthropic(
            model=self.model, 
            temperature=self.temperature,
            api_key=settings.ANTHROPIC_API_KEY,
            **self.kwargs
        )


class LLMFactory:
    """LLM 팩토리 클래스 - 공통 LLM 생성 로직"""
    
    _providers = {
        LLMProviderType.OPENAI: OpenAIProvider,
        LLMProviderType.ANTHROPIC: AnthropicProvider,
    }
    
    @classmethod
    def create_provider(
        cls, 
        provider_type: str, 
        model: str, 
        temperature: float = 0,
        **kwargs
    ) -> BaseLLMProvider:
        """LLM 프로바이더 생성"""
        # provider_type이 None이거나 빈 문자열인 경우 설정에서 기본값 사용
        if not provider_type:
            provider_type = settings.ACTIVE_LLM_PROVIDER or "openai"
            logger.info(f"provider_type이 None이므로 설정값 사용: {provider_type}")
        
        # 지원하지 않는 provider인 경우 기본값 사용
        if provider_type.lower() not in [p.value for p in LLMProviderType]:
            logger.warning(f"지원하지 않는 LLM provider: {provider_type}. OpenAI를 기본값으로 사용합니다.")
            provider_type = LLMProviderType.OPENAI
        
        # model이 None인 경우 설정에서 기본값 사용
        if not model:
            model = settings.ACTIVE_LLM_MODEL
            logger.info(f"model이 None이므로 설정값 사용: {model}")
        
        provider_class = cls._providers.get(LLMProviderType(provider_type.lower()))
        if not provider_class:
            raise ValueError(f"지원하지 않는 LLM provider: {provider_type}")
        
        return provider_class(model, temperature, **kwargs)
    
    @classmethod
    def create_llm(
        cls,
        provider_type: str = None,
        model: str = None, 
        temperature: float = 0,
        **kwargs
    ) -> Any:
        """LLM 인스턴스 직접 생성 (편의 메서드)"""
        provider_type = provider_type or settings.ACTIVE_LLM_PROVIDER or "openai"
        model = model or settings.ACTIVE_LLM_MODEL
        
        provider = cls.create_provider(provider_type, model, temperature, **kwargs)
        return provider.create_llm() 