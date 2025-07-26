from dotenv import load_dotenv
from functools import lru_cache
from os import path, environ
import os
import json
import logging
import base64
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Dict, List, Optional

from ..utils.utility import load_json_file
from ..constants import UserLevel

load_dotenv()

logger = logging.getLogger(__name__)

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
    FIREBASE_SECRET_FILE: Optional[dict] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Firebase 설정을 안전하게 로드
        self.FIREBASE_SECRET_FILE = self._load_firebase_config()
    
    def _load_firebase_config(self) -> Optional[Dict]:
        """
        Firebase 설정을 안전하게 로드합니다.
        
        우선순위:
        1. 환경변수 FIREBASE_SERVICE_ACCOUNT_KEY (base64 인코딩된 JSON)
        2. 로컬 파일 ./secrets/firebase-key.json
        3. None (개발 모드)
        """
        
        # 1. base64 인코딩된 환경변수에서 Firebase 키 확인
        firebase_key_base64 = environ.get("FIREBASE_SERVICE_ACCOUNT_KEY")
        print(f"🔍 FIREBASE_SERVICE_ACCOUNT_KEY 존재: {'YES' if firebase_key_base64 else 'NO'}")
        
        if firebase_key_base64:
            try:
                # base64 디코딩
                firebase_key_json = base64.b64decode(firebase_key_base64).decode('utf-8')
                
                # JSON 파싱
                firebase_config = json.loads(firebase_key_json)
                
                print("✅ Firebase 설정을 base64 환경변수에서 로드했습니다")
                return firebase_config
                
            except (base64.binascii.Error, UnicodeDecodeError) as e:
                print(f"❌ base64 디코딩 실패: {e}")
            except json.JSONDecodeError as e:
                print(f"❌ base64 디코딩 후 JSON 파싱 실패: {e}")
        
        # 2. 로컬 파일에서 Firebase 키 확인
        if path.exists(self.FIREBASE_SECRET_FILE_PATH):
            try:
                firebase_config = load_json_file(self.FIREBASE_SECRET_FILE_PATH)
                
                if firebase_config:
                    print("✅ Firebase 설정을 로컬 파일에서 로드했습니다")
                    return firebase_config
                    
            except Exception as e:
                print(f"❌ 로컬 Firebase 파일 읽기 실패: {e}")
        
        # 3. Firebase 설정 없음 (개발 모드)
        print("⚠️ Firebase 설정을 찾을 수 없습니다. 개발 모드로 실행합니다.")
        return None

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
