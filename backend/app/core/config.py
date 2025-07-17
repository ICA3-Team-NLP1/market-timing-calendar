from os import path, environ
from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from backend.app.utils.utility import load_json_file

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
