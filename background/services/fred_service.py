"""
FRED API 서비스 - 단일 책임 원칙을 준수한 데이터 수집 로직
"""
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import requests
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class FredApiConfig:
    """FRED API 설정 클래스 (Configuration Object Pattern)"""
    api_key: str
    base_url: str = 'https://api.stlouisfed.org/fred'
    file_type: str = 'json'

    @classmethod
    def from_settings(cls) -> 'FredApiConfig':
        """설정에서 생성"""
        return cls(api_key=settings.FRED_API_KEY)


@dataclass
class DateRange:
    """날짜 범위 클래스 (Value Object Pattern)"""
    start_date: str
    end_date: str

    @classmethod
    def create_around_today(cls, days_before: int = 30, days_after: int = 30) -> 'DateRange':
        """오늘 기준으로 날짜 범위 생성"""
        today = datetime.now()
        start_date = (today - timedelta(days=days_before)).strftime('%Y-%m-%d')
        end_date = (today + timedelta(days=days_after)).strftime('%Y-%m-%d')
        return cls(start_date, end_date)


@dataclass
class ReleaseInfo:
    """단일 경제 지표 발표 정보 DTO"""
    release_id: str
    date: str
    name: Optional[str] = None
    title: Optional[str] = None
    notes: Optional[str] = None
    source: Optional[str] = None
    popularity: Optional[int] = None


class FredApiClient:
    """FRED API 클라이언트 (Single Responsibility)"""

    def __init__(self, config: FredApiConfig):
        self.config = config
        # 환경변수에서 설정 가져오기 (기본값 사용)
        self.request_delay = float(os.getenv('FRED_REQUEST_DELAY', '1.0'))  # 요청 간격 (초)
        self.max_retries = int(os.getenv('FRED_MAX_RETRIES', '3'))         # 최대 재시도 횟수

    def get_release_dates(self, date_range: DateRange) -> Dict[str, Any]:
        """Release dates API 호출"""
        url = f'{self.config.base_url}/releases/dates'
        params = {
            'api_key': self.config.api_key,
            'file_type': self.config.file_type,
            'realtime_start': date_range.start_date,
            'realtime_end': date_range.end_date,
            'include_release_dates_with_no_data': "true",
        }

        logger.info(f"FRED API 호출 범위: {date_range.start_date} ~ {date_range.end_date}")
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _make_api_request_with_retry(self, url: str, params: Dict[str, Any], operation_name: str, release_id: str) -> Dict[str, Any]:
        """공통 API 요청 메서드 (재시도 로직 포함)"""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                result = response.json()
                
                # 요청 간격 추가
                time.sleep(self.request_delay)
                return result
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 점진적으로 대기 시간 증가
                    logger.warning(f"release_id={release_id} {operation_name} 실패 (429), {wait_time}초 후 재시도 {attempt + 1}/{self.max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"release_id={release_id} {operation_name} 실패: {e}")
                    return {}
            except Exception as e:
                logger.warning(f"release_id={release_id} {operation_name} 실패: {e}")
                return {}
        
        return {}

    def get_release_metadata(self, release_id: str) -> Dict[str, Any]:
        """Release 메타데이터 조회"""
        url = f'{self.config.base_url}/release'
        params = {
            'release_id': release_id,
            'api_key': self.config.api_key,
            'file_type': self.config.file_type
        }

        result = self._make_api_request_with_retry(url, params, "메타데이터 조회", release_id)
        return result.get('releases', [{}])[0] if result else {}

    def get_representative_series_info(self, release_id: str) -> Dict[str, Any]:
        """대표 시리즈 정보 조회"""
        url = f'{self.config.base_url}/release/series'
        params = {
            'release_id': release_id,
            'api_key': self.config.api_key,
            'file_type': self.config.file_type
        }

        result = self._make_api_request_with_retry(url, params, "시리즈 조회", release_id)
        series_list = result.get('seriess', []) if result else []

        # popularity 기준으로 정렬 후 가장 인기 있는 시리즈 반환
        if series_list:
            preferred = sorted(series_list, key=lambda x: x.get('popularity', 0), reverse=True)
            return preferred[0]
        else:
            return {}


class FredDataProcessor:
    """FRED 데이터 처리기 (Single Responsibility)"""

    def __init__(self, api_client: FredApiClient):
        self.api_client = api_client

    def process_release_dates(self, raw_data: Dict[str, Any]) -> List[ReleaseInfo]:
        """Release dates 데이터 처리"""
        release_dates = raw_data.get('release_dates', [])
        results = []
        
        logger.info(f"총 {len(release_dates)}개 release_dates 처리 시작")
        
        # 배치 크기 설정 (환경변수에서 가져오거나 기본값 사용)
        batch_size = int(os.getenv('FRED_BATCH_SIZE', '10'))
        
        for i, item in enumerate(release_dates):
            release_id = str(item.get('release_id'))
            date = item.get('date')
            
            logger.info(f"처리 중: {i+1}/{len(release_dates)} - release_id={release_id}")

            # 메타데이터 및 시리즈 정보 수집
            release_metadata = self.api_client.get_release_metadata(release_id)
            series_info = self.api_client.get_representative_series_info(release_id)

            release_info = ReleaseInfo(
                release_id=release_id,
                date=date,
                name=release_metadata.get("name", ""),
                title=series_info.get("title"),
                notes=series_info.get("notes"),
                source=series_info.get("source"),
                popularity=series_info.get("popularity")
            )

            results.append(release_info)
            
            # 배치 단위로 추가 대기 시간
            if (i + 1) % batch_size == 0:
                wait_time = 5  # 배치 간 5초 대기
                logger.info(f"배치 완료 ({i+1}/{len(release_dates)}). {wait_time}초 대기...")
                time.sleep(wait_time)

        logger.info(f"총 {len(results)}개 release 정보 처리 완료")
        return results


class FredService:
    """FRED 서비스 (Facade Pattern)"""

    def __init__(self, config: Optional[FredApiConfig] = None):
        self.config = config or FredApiConfig.from_settings()
        self.api_client = FredApiClient(self.config)
        self.data_processor = FredDataProcessor(self.api_client)

    def fetch_recent_releases(self, days_before: int = 30, days_after: int = 30) -> List[ReleaseInfo]:
        """최근 Release 정보 수집"""
        try:
            # 날짜 범위 생성
            date_range = DateRange.create_around_today(days_before, days_after)

            # API 호출
            raw_data = self.api_client.get_release_dates(date_range)
            logger.info(f"API 응답 받음. release_dates 개수: {len(raw_data.get('release_dates', []))}")

            # 데이터 처리
            release_infos = self.data_processor.process_release_dates(raw_data)

            return release_infos

        except Exception as e:
            logger.error(f"FRED releases/dates API 호출 실패: {e}")
            raise

        """특정 기간의 Release 정보 수집"""
    def fetch_releases_by_date_range(self, start_date: str, end_date: str) -> List[ReleaseInfo]:
        try:
            # 날짜 범위 생성
            date_range = DateRange(start_date=start_date, end_date=end_date)

            # API 호출
            raw_data = self.api_client.get_release_dates(date_range)
            logger.info(f"API 응답 받음. 기간: {start_date} ~ {end_date}, release_dates 개수: {len(raw_data.get('release_dates', []))}")

            # 데이터 처리
            release_infos = self.data_processor.process_release_dates(raw_data)

            return release_infos

        except Exception as e:
            logger.error(f"FRED releases/dates API 호출 실패: {e}")
            raise 
