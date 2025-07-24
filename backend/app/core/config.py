from dotenv import load_dotenv
from functools import lru_cache
from os import path, environ
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Dict, List

from ..utils.utility import load_json_file
from ..constants import UserLevel

load_dotenv()

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
media_secret_dir = path.join(base_dir, "secrets")
app_dir = path.join(base_dir, "app")


class DBConnection(BaseModel):
    SQLALCHEMY_DATABASE_URL: str = ""
    SQLALCHEMY_POOL_RECYCLE: int = 900
    SQLALCHEMY_ECHO: bool = False
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 30


class LevelConfig:
    """레벨업 관련 설정 - JSON 파일 기반"""

    _config_cache = None

    @classmethod
    def _load_config(cls) -> Dict:
        """JSON 파일에서 레벨 설정을 로드합니다."""
        if cls._config_cache is None:
            config_path = path.join(path.dirname(__file__), "level_config.json")
            cls._config_cache = load_json_file(config_path)
        return cls._config_cache

    @classmethod
    def get_exp_fields(cls) -> Dict[str, str]:
        """경험치 필드 딕셔너리 반환"""
        config = cls._load_config()
        return config.get("exp_fields", {})

    @classmethod
    def get_level_up_conditions(cls) -> Dict:
        """레벨업 조건 딕셔너리 반환"""
        config = cls._load_config()
        return config.get("level_up_conditions", {})

    @classmethod
    def get_level_names(cls) -> Dict[str, str]:
        """레벨별 한국어 이름 딕셔너리 반환"""
        config = cls._load_config()
        return config.get("level_names", {})

    @classmethod
    def get_default_exp(cls) -> Dict[str, int]:
        """기본 경험치 딕셔너리 반환"""
        exp_fields = cls.get_exp_fields()
        return {field: 0 for field in exp_fields.keys()}

    @classmethod
    def get_exp_field_names(cls) -> List[str]:
        """경험치 필드명 리스트 반환"""
        exp_fields = cls.get_exp_fields()
        return list(exp_fields.keys())

    @classmethod
    def is_valid_exp_field(cls, field_name: str) -> bool:
        """유효한 경험치 필드인지 확인"""
        exp_fields = cls.get_exp_fields()
        return field_name in exp_fields

    @classmethod
    def get_level_up_condition(cls, current_level: UserLevel) -> Dict:
        """현재 레벨의 레벨업 조건 반환"""
        conditions = cls.get_level_up_conditions()
        return conditions.get(current_level.value, {})


class Settings(BaseSettings):
    """기본 설정 클래스"""

    BASE_DIR: str = base_dir

    # 기본 앱 설정
    APP_NAME: str = "Market Timing Calendar"
    APP_DESCRIPTION: str = "마켓 타이밍 캘린더 API"
    APP_VERSION: str = "1.0.0"
    OPENAPI_URL: str | None = "/api/openapi.json"
    DOCS_URL: str | None = "/api/docs"
    REDOC_URL: str | None = "/api/redoc"
    DEBUG: bool = True

    # 외부 API 설정
    FRED_API_KEY: str = ""

    # 데이터베이스 설정
    DATABASE_URL: str = environ.get("DATABASE_URL")
    DB_INFO: DBConnection = DBConnection(SQLALCHEMY_DATABASE_URL=DATABASE_URL)

    # Redis 설정 (Celery용)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Firebase 설정
    FIREBASE_SECRET_FILE_PATH: str = path.join(media_secret_dir, "firebase-key.json")
    FIREBASE_SECRET_FILE: dict = load_json_file(FIREBASE_SECRET_FILE_PATH)

    # AI 모델 설정
    ACTIVE_LLM_PROVIDER: str = ""  # "openai", "anthropic", ... (빈 문자열이면 자동으로 openai 사용)
    ACTIVE_LLM_MODEL: str = "gpt-4-turbo"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""  # Claude API 키

    # 컨텐츠 필터링 설정
    FILTER_ENABLED: bool = True
    FILTER_SAFETY_LEVEL: str = "strict"  # strict, moderate, permissive
    FILTER_MAX_RETRIES: int = 3
    FILTER_LLM_PROVIDER: str = ""  # 필터링 전용 LLM (빈 문자열이면 기본 LLM 사용)
    FILTER_LLM_MODEL: str = "gpt-4"  # 필터링용 모델 (정확성을 위해 고성능 모델 사용)

    # Langfuse 설정
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://us.cloud.langfuse.com"

    # Mem0 설정
    MEM0_RELEVANT_MEMORY_LIMIT: int = 10
    # Mem0 플랫폼 API
    MEM0_API_KEY: str = environ.get("MEM0_API_KEY", "")
    # Mem0 OOS 설정
    MEM0_LLM_MODEL: str = "gpt-4o-mini"  # 비용 효율적인 모델 사용
    MEM0_TEMPERATURE: float = 0.2
    MEM0_MAX_TOKENS: int = 1500
    MEM0_VECTOR_STORE: dict = {
        "provider": "chroma",
        "config": {
            "collection_name": "market_timing_chat_memory",
            "path": "./mem0_db",  # 로컬 저장소 경로
        },
    }

    # SerpAPI 설정
    SERPAPI_API_KEY: str = environ.get("SERPAPI_API_KEY", "")
    SERPAPI_BASE_URL: str = "https://serpapi.com/search"

    class Config:
        env_file = ".env"
        extra = "allow"  # 추가 필드 허용


class ProdSettings(Settings):
    OPENAPI_URL: str | None = None
    DOCS_URL: str | None = None
    REDOC_URL: str | None = None

    class Config:
        env_file = ".env.prod"
        extra = "allow"  # 추가 필드 허용


@lru_cache()
def get_settings():
    """
    환경 변수 세팅 함수
    """
    cfg_cls = dict(
        test=Settings,
        prod=ProdSettings,
    )
    env = cfg_cls[environ.get("FASTAPI_ENV", "test")]()
    return env


settings = get_settings()
