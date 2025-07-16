"""
Event 저장 서비스 - 데이터베이스 저장 로직
"""
import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.models import Events
from app.core.database import db
from .fred_service import ReleaseInfo
from .llm_service import LLMInferenceService, InferenceType

logger = logging.getLogger(__name__)


@dataclass
class ProcessingStats:
    """처리 통계 클래스 (Value Object)"""
    total_items: int = 0
    saved_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    updated_count: int = 0

    @property
    def success_rate(self) -> float:
        """성공률 계산"""
        if self.total_items == 0:
            return 0.0
        return (self.saved_count / self.total_items) * 100


@dataclass
class EventData:
    """이벤트 데이터 DTO (LLM 서비스와 데이터베이스 간의 결합도 감소)"""
    release_id: str
    date: str
    title: Optional[str] = None
    description: Optional[str] = None
    description_ko: Optional[str] = None
    popularity: Optional[int] = None
    impact: str = "MEDIUM"
    level: str = "ADVANCED"
    source: str = "FRED"
    level_category: Optional[str] = None  # 레벨 분류 (지표명)


class EventMapper:
    """FRED API 응답을 내부 EventData 객체로 변환"""

    def __init__(self, llm_service: LLMInferenceService):
        self.llm_service = llm_service

    def map_to_event_data(self, release_info: ReleaseInfo) -> EventData:
        """ReleaseInfo를 EventData로 변환 (LLM 기반 레벨 분류)"""
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
            # 레벨 분류 LLM 추론 (JSON 응답)
            level_json = self.llm_service.infer(
                InferenceType.LEVEL,
                release_info.name or "",
                series_info
            )
            try:
                import json
                level_info = json.loads(level_json)
                level = level_info.get("level", "UNCATEGORIZED")
                level_category = level_info.get("level_category", "UNCATEGORIZED")
            except Exception:
                level = "UNCATEGORIZED"
                level_category = "UNCATEGORIZED"
            # 한글 요약
            logger.info(f"🔍 description_ko 추론 시작 - InferenceType.DESCRIPTION_KO: {InferenceType.DESCRIPTION_KO}")
            description_ko = self.llm_service.infer(
                InferenceType.DESCRIPTION_KO,
                release_info.name or "",
                series_info
            )
            logger.info(f"✅ description_ko 추론 완료: {description_ko[:50]}...")
            return EventData(
                release_id=release_info.release_id,
                date=release_info.date,
                title=release_info.title,
                description=release_info.notes,
                description_ko=description_ko,
                popularity=release_info.popularity,
                impact=impact,
                level=level,
                source="FRED",
                level_category=level_category
            )

        except Exception as e:
            logger.error(f"매핑 중 오류 (release_id={release_info.release_id}): {e}")
            # 기본값으로 fallback
            return EventData(
                release_id=release_info.release_id,
                date=release_info.date,
                title=release_info.title,
                description=release_info.notes,
                description_ko="",
                popularity=release_info.popularity,
                impact="MEDIUM",
                level="UNCATEGORIZED",
                source="FRED",
                level_category="UNCATEGORIZED"
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
                    source=event_data.source,
                    popularity=event_data.popularity,
                    description_ko=event_data.description_ko,
                    level_category=event_data.level_category
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
                        source=event_data.source,
                        popularity=event_data.popularity,
                        description_ko=event_data.description_ko,
                        level_category=event_data.level_category
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
            f"총 {stats.total_items}개 이벤트 처리 완료. "
            f"저장: {stats.saved_count}개, 업데이트: {stats.updated_count}개, "
            f"스킵: {stats.skipped_count}개, 성공률: {stats.success_rate:.1f}%"
        )

        return stats 
