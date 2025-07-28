"""
리팩토링된 Celery 앱 - SOLID, DRY, KISS 원칙 준수
"""
import os
import logging
from celery import Celery

from app.core.config import settings
from app.core.database import db
from .services.llm_service import LLMServiceFactory
from .services.fred_service import FredService
from .services.event_service import EventService, ProgressReporter

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DB 초기화
db.init_db(settings.DB_INFO)

# 모델 import는 DB 초기화 후에 수행
import app.models  # 패키지 전체 import (PYTHONPATH=/app/backend 기준)

from sqlalchemy.orm import configure_mappers
configure_mappers()

# Celery 앱 생성
app = Celery('background_tasks')

# Redis 설정
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
)

# 배치 처리 설정
BATCH_SIZE = int(os.getenv('LLM_BATCH_SIZE', '10'))
API_DELAY = float(os.getenv('LLM_API_DELAY', '0.5'))


class DataCollectionOrchestrator:
    """데이터 수집 오케스트레이터 (Orchestrator Pattern + Dependency Injection)"""

    def __init__(
        self,
        fred_service: FredService,
        llm_service,
        event_service: EventService
    ):
        self.fred_service = fred_service
        self.llm_service = llm_service
        self.event_service = event_service
    
    def collect_and_process_data(self) -> str:
        """데이터 수집 및 처리 메인 플로우 (Template Method Pattern)"""
        try:
            # 1. FRED 데이터 수집
            logger.info("FRED releases/dates API 호출 시작")
            release_infos = self.fred_service.fetch_recent_releases(days_before=3, days_after=3)

            # 2. 이벤트 처리 및 저장
            stats = self.event_service.process_releases(release_infos)

            # 3. 결과 반환
            return (
                f"FRED 데이터 저장 완료. "
                f"새로 저장된 이벤트: {stats.saved_count}개, "
                f"실패: {stats.failed_count}개, "
                f"스킵: {stats.skipped_count}개"
            )

        except Exception as e:
            error_msg = f"데이터 수집 실패: {e}"
            logger.error(error_msg)
            return error_msg


class ServiceFactory:
    """서비스 팩토리 (Factory Pattern + Configuration)"""

    @staticmethod
    def create_orchestrator() -> DataCollectionOrchestrator:
        """의존성 주입을 통한 오케스트레이터 생성"""
        # LLM 서비스 생성
        llm_service = LLMServiceFactory.create_service()

        # FRED 서비스 생성
        fred_service = FredService()

        # 진행 상황 리포터 생성
        progress_reporter = ProgressReporter(
            batch_size=BATCH_SIZE,
            api_delay=API_DELAY
        )

        # Event 서비스 생성
        event_service = EventService(
            llm_service=llm_service,
            progress_reporter=progress_reporter
        )

        # 오케스트레이터 생성
        return DataCollectionOrchestrator(
            fred_service=fred_service,
            llm_service=llm_service,
            event_service=event_service
        )


@app.task
def simple_task(message):
    """간단한 테스트 태스크 (기존 유지)"""
    logger.info(f"Task started: {message}")
    import time
    time.sleep(5)
    result = f"Task completed: {message}"
    logger.info(result)
    return result


@app.task
def data_collection_task():
    """
    리팩토링된 데이터 수집 태스크
    - Single Responsibility: 오케스트레이션만 담당
    - Dependency Injection: 서비스들을 주입받아 사용
    - KISS: 단순하고 명확한 플로우
    """
    orchestrator = ServiceFactory.create_orchestrator()
    return orchestrator.collect_and_process_data()


if __name__ == '__main__':
    # 워커 실행
    app.start() 
