"""
Event 저장 서비스 - 데이터베이스 저장 로직
"""
import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from backend.app.models import Events
from backend.app.core.database import db
from background.services.fred_service import ReleaseInfo
from background.services.llm_service import LLMInferenceService, InferenceType

logger = logging.getLogger(__name__)


@dataclass
class ProcessingStats:
    """처리 통계 클래스 (Value Object)"""
    total_items: int = 0
    saved_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    
    @property
    def success_rate(self) -> float:
        """성공률 계산"""
        if self.total_items == 0:
            return 0.0
        return (self.saved_count / self.total_items) * 100


@dataclass
class EventData:
    """Event 데이터 전송 객체 (DTO)"""
    release_id: str
    date: str
    title: Optional[str] = None
    description: Optional[str] = None
    impact: str = "MEDIUM"
    level: str = "ADVANCED"
    source: str = "FRED"


class EventMapper:
    """ReleaseInfo를 EventData로 변환하는 매퍼 (Single Responsibility)"""
    
    def __init__(self, llm_service: LLMInferenceService):
        self.llm_service = llm_service
    
    def map_to_event_data(self, release_info: ReleaseInfo) -> EventData:
        """ReleaseInfo를 EventData로 변환"""
        try:
            # LLM 추론 실행
            series_info = {
                "title": release_info.title,
                "notes": release_info.notes,
                "source": release_info.source
            }
            
            impact = self.llm_service.infer(
                InferenceType.IMPACT,
                release_info.name or "",
                series_info
            )
            
            level = self.llm_service.infer(
                InferenceType.LEVEL,
                release_info.name or "",
                series_info
            )
            
            return EventData(
                release_id=release_info.release_id,
                date=release_info.date,
                title=release_info.title,
                description=release_info.notes,
                impact=impact,
                level=level,
                source="FRED"
            )
            
        except Exception as e:
            logger.error(f"매핑 중 오류 (release_id={release_info.release_id}): {e}")
            # 기본값으로 fallback
            return EventData(
                release_id=release_info.release_id,
                date=release_info.date,
                title=release_info.title,
                description=release_info.notes,
                impact="MEDIUM",
                level="ADVANCED",
                source="FRED"
            )


class EventRepository:
    """Event 데이터베이스 저장소 (Repository Pattern)"""
    
    def exists(self, release_id: str, date: str) -> bool:
        """이벤트 존재 여부 확인"""
        with db.session as session:
            existing = session.query(Events).filter_by(
                release_id=release_id,
                date=date
            ).first()
            return existing is not None
    
    def save(self, event_data: EventData) -> bool:
        """이벤트 저장"""
        try:
            with db.session as session:
                event = Events(
                    release_id=event_data.release_id,
                    date=event_data.date,
                    title=event_data.title,
                    description=event_data.description,
                    impact=event_data.impact,
                    level=event_data.level,
                    source=event_data.source
                )
                
                session.add(event)
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"이벤트 저장 실패 (release_id={event_data.release_id}): {e}")
            return False
    
    def bulk_save(self, event_data_list: List[EventData]) -> int:
        """벌크 저장"""
        saved_count = 0
        
        try:
            with db.session as session:
                for event_data in event_data_list:
                    event = Events(
                        release_id=event_data.release_id,
                        date=event_data.date,
                        title=event_data.title,
                        description=event_data.description,
                        impact=event_data.impact,
                        level=event_data.level,
                        source=event_data.source
                    )
                    session.add(event)
                    saved_count += 1
                
                session.commit()
                logger.info(f"벌크 저장 완료: {saved_count}개")
                return saved_count
                
        except Exception as e:
            logger.error(f"벌크 저장 실패: {e}")
            return 0


class ProgressReporter:
    """진행 상황 보고기 (Single Responsibility)"""
    
    def __init__(self, batch_size: int = 10, api_delay: float = 0.5):
        self.batch_size = batch_size
        self.api_delay = api_delay
    
    def report_progress(self, current: int, total: int, stats: ProcessingStats):
        """진행 상황 보고"""
        if current % self.batch_size == 0 or current == total:
            logger.info(
                f"진행상황: {current}/{total} 처리 중... "
                f"(성공: {stats.saved_count}, 실패: {stats.failed_count}, 스킵: {stats.skipped_count})"
            )
    
    def add_delay(self):
        """API 호출 간 딜레이 추가"""
        time.sleep(self.api_delay)


class EventService:
    """Event 서비스 (Orchestrator Pattern)"""
    
    def __init__(
        self,
        llm_service: LLMInferenceService,
        repository: Optional[EventRepository] = None,
        progress_reporter: Optional[ProgressReporter] = None
    ):
        self.llm_service = llm_service
        self.repository = repository or EventRepository()
        self.progress_reporter = progress_reporter or ProgressReporter()
        self.mapper = EventMapper(llm_service)
    
    def process_releases(self, release_infos: List[ReleaseInfo]) -> ProcessingStats:
        """Release 정보들을 처리하여 Event로 저장"""
        stats = ProcessingStats(total_items=len(release_infos))
        
        logger.info(f"총 {stats.total_items}개 release_dates 처리 시작")
        
        for idx, release_info in enumerate(release_infos, 1):
            try:
                # 중복 체크
                if self.repository.exists(release_info.release_id, release_info.date):
                    logger.debug(f"기존 이벤트 존재: release_id={release_info.release_id}, date={release_info.date}")
                    stats.skipped_count += 1
                    continue
                
                # 데이터 변환 및 저장
                event_data = self.mapper.map_to_event_data(release_info)
                
                if self.repository.save(event_data):
                    stats.saved_count += 1
                    logger.debug(f"새 이벤트 저장: release_id={release_info.release_id}, date={release_info.date}")
                else:
                    stats.failed_count += 1
                
                # 진행 상황 보고 및 딜레이
                self.progress_reporter.report_progress(idx, stats.total_items, stats)
                self.progress_reporter.add_delay()
                
            except Exception as e:
                logger.error(f"이벤트 처리 중 오류 (release_id={release_info.release_id}): {e}")
                stats.failed_count += 1
        
        logger.info(
            f"처리 완료. 성공: {stats.saved_count}개, 실패: {stats.failed_count}개, "
            f"스킵: {stats.skipped_count}개, 성공률: {stats.success_rate:.1f}%"
        )
        
        return stats 