"""
리팩토링된 Celery 앱 - SOLID, DRY, KISS 원칙 준수
"""
import os
import logging
from datetime import datetime, timedelta
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
    
    def _get_date_range_from_env(self) -> tuple[str, str]:
        """환경변수에서 날짜 범위 가져오기"""
        # 환경변수에서 날짜 범위 가져오기
        start_date = os.getenv('FRED_START_DATE')
        end_date = os.getenv('FRED_END_DATE')
        
        # 환경변수가 없으면 기본값 사용 (오늘 기준 전후 30일)
        if not start_date or not end_date:
            today = datetime.now()
            start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = (today + timedelta(days=30)).strftime('%Y-%m-%d')
            logger.info(f"환경변수 없음. 기본값 사용: {start_date} ~ {end_date}")
        else:
            logger.info(f"환경변수에서 날짜 범위 가져옴: {start_date} ~ {end_date}")
        
        return start_date, end_date
    
    def _generate_date_list(self, start_date: str, end_date: str) -> list[str]:
        """시작일부터 종료일까지의 날짜 리스트 생성"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        date_list = []
        current = start
        while current <= end:
            date_list.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        return date_list

    def collect_and_process_data(self) -> str:
        """데이터 수집 및 처리 메인 플로우 (Template Method Pattern)"""
        try:
            # 1. 날짜 범위 결정
            start_date, end_date = self._get_date_range_from_env()
            
            # 2. 날짜 리스트 생성
            date_list = self._generate_date_list(start_date, end_date)
            logger.info(f"처리할 날짜 수: {len(date_list)}개 ({start_date} ~ {end_date})")
            
            # 3. 날짜별로 순차 처리
            all_release_infos = []
            total_saved = 0
            total_failed = 0
            total_skipped = 0
            
            for i, current_date in enumerate(date_list, 1):
                logger.info(f"처리 중: {i}/{len(date_list)} - {current_date}")
                
                try:
                    # 3-1. 해당 날짜의 FRED 데이터 수집
                    daily_release_infos = self.fred_service.fetch_releases_by_date_range(
                        start_date=current_date, 
                        end_date=current_date
                    )
                    
                    if daily_release_infos:
                        logger.info(f"{current_date}: {len(daily_release_infos)}개 release 발견")
                        
                        # 3-2. 해당 날짜의 이벤트 처리 및 저장
                        stats = self.event_service.process_releases(daily_release_infos)
                        
                        total_saved += stats.saved_count
                        total_failed += stats.failed_count
                        total_skipped += stats.skipped_count
                        
                        logger.info(f"{current_date} 처리 완료: 저장={stats.saved_count}, 실패={stats.failed_count}, 스킵={stats.skipped_count}")
                    else:
                        logger.info(f"{current_date}: release 없음")
                        
                except Exception as e:
                    logger.error(f"{current_date} 처리 실패: {e}")
                    total_failed += 1
                    continue

            # 4. 결과 반환
            return (
                f"FRED 데이터 저장 완료. "
                f"기간: {start_date} ~ {end_date}, "
                f"처리된 날짜: {len(date_list)}개, "
                f"총 저장된 이벤트: {total_saved}개, "
                f"총 실패: {total_failed}개, "
                f"총 스킵: {total_skipped}개"
            )

        except Exception as e:
            error_msg = f"데이터 수집 실패: {e}"
            logger.error(error_msg)
            return error_msg

    def collect_and_process_data_with_dates(self, start_date: str, end_date: str) -> str:
        """특정 날짜 범위로 데이터 수집 및 처리"""
        try:
            # 1. 날짜 리스트 생성
            date_list = self._generate_date_list(start_date, end_date)
            logger.info(f"처리할 날짜 수: {len(date_list)}개 ({start_date} ~ {end_date})")
            
            # 2. 날짜별로 순차 처리
            all_release_infos = []
            total_saved = 0
            total_failed = 0
            total_skipped = 0
            
            for i, current_date in enumerate(date_list, 1):
                logger.info(f"처리 중: {i}/{len(date_list)} - {current_date}")
                
                try:
                    # 2-1. 해당 날짜의 FRED 데이터 수집
                    daily_release_infos = self.fred_service.fetch_releases_by_date_range(
                        start_date=current_date, 
                        end_date=current_date
                    )
                    
                    if daily_release_infos:
                        logger.info(f"{current_date}: {len(daily_release_infos)}개 release 발견")
                        
                        # 2-2. 해당 날짜의 이벤트 처리 및 저장
                        stats = self.event_service.process_releases(daily_release_infos)
                        
                        total_saved += stats.saved_count
                        total_failed += stats.failed_count
                        total_skipped += stats.skipped_count
                        
                        logger.info(f"{current_date} 처리 완료: 저장={stats.saved_count}, 실패={stats.failed_count}, 스킵={stats.skipped_count}")
                    else:
                        logger.info(f"{current_date}: release 없음")
                        
                except Exception as e:
                    logger.error(f"{current_date} 처리 실패: {e}")
                    total_failed += 1
                    continue

            # 3. 결과 반환
            return (
                f"FRED 데이터 저장 완료. "
                f"기간: {start_date} ~ {end_date}, "
                f"처리된 날짜: {len(date_list)}개, "
                f"총 저장된 이벤트: {total_saved}개, "
                f"총 실패: {total_failed}개, "
                f"총 스킵: {total_skipped}개"
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
def data_collection_task(start_date: str = None, end_date: str = None):
    """
    리팩토링된 데이터 수집 태스크
    - Single Responsibility: 오케스트레이션만 담당
    - Dependency Injection: 서비스들을 주입받아 사용
    - KISS: 단순하고 명확한 플로우
    """
    orchestrator = ServiceFactory.create_orchestrator()
    
    # 태스크 파라미터로 전달된 날짜가 있으면 사용, 없으면 환경변수 사용
    if start_date and end_date:
        logger.info(f"태스크 파라미터에서 날짜 범위 가져옴: {start_date} ~ {end_date}")
        return orchestrator.collect_and_process_data_with_dates(start_date, end_date)
    else:
        return orchestrator.collect_and_process_data()


if __name__ == '__main__':
    # 워커 실행
    app.start() 
