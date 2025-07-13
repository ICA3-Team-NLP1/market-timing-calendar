"""
FRED API 서비스 - 단일 책임 원칙을 준수한 데이터 수집 로직
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import requests
from backend.app.core.config import settings

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
    """Release 정보 클래스 (Data Transfer Object)"""
    release_id: str
    date: str
    name: Optional[str] = None
    title: Optional[str] = None
    notes: Optional[str] = None
    source: Optional[str] = None


class FredApiClient:
    """FRED API 클라이언트 (Single Responsibility)"""
    
    def __init__(self, config: FredApiConfig):
        self.config = config
    
    def get_release_dates(self, date_range: DateRange) -> Dict[str, Any]:
        """Release dates API 호출"""
        url = f'{self.config.base_url}/releases/dates'
        params = {
            'api_key': self.config.api_key,
            'file_type': self.config.file_type,
            'realtime_start': date_range.start_date,
            'realtime_end': date_range.end_date,
        }
        
        logger.info(f"FRED API 호출 범위: {date_range.start_date} ~ {date_range.end_date}")
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_release_metadata(self, release_id: str) -> Dict[str, Any]:
        """Release 메타데이터 조회"""
        url = f'{self.config.base_url}/release'
        params = {
            'release_id': release_id,
            'api_key': self.config.api_key,
            'file_type': self.config.file_type
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get('releases', [{}])[0]
        except Exception as e:
            logger.warning(f"release_id={release_id} 메타데이터 조회 실패: {e}")
            return {}
    
    def get_representative_series_info(self, release_id: str) -> Dict[str, Any]:
        """대표 시리즈 정보 조회"""
        url = f'{self.config.base_url}/release/series'
        params = {
            'release_id': release_id,
            'api_key': self.config.api_key,
            'file_type': self.config.file_type
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            series_list = response.json().get('seriess', [])
            
            # popularity 기준으로 정렬 후 가장 인기 있는 시리즈 반환
            if series_list:
                preferred = sorted(series_list, key=lambda x: x.get('popularity', 0), reverse=True)
                return preferred[0]
            return {}
        except Exception as e:
            logger.warning(f"release_id={release_id} 시리즈 조회 실패: {e}")
            return {}


class FredDataProcessor:
    """FRED 데이터 처리기 (Single Responsibility)"""
    
    def __init__(self, api_client: FredApiClient):
        self.api_client = api_client
    
    def process_release_dates(self, raw_data: Dict[str, Any]) -> List[ReleaseInfo]:
        """Release dates 데이터 처리"""
        release_dates = raw_data.get('release_dates', [])
        results = []
        
        for item in release_dates:
            release_id = str(item.get('release_id'))
            date = item.get('date')
            
            # 메타데이터 및 시리즈 정보 수집
            release_metadata = self.api_client.get_release_metadata(release_id)
            series_info = self.api_client.get_representative_series_info(release_id)
            
            release_info = ReleaseInfo(
                release_id=release_id,
                date=date,
                name=release_metadata.get("name", ""),
                title=series_info.get("title"),
                notes=series_info.get("notes"),
                source=series_info.get("source")
            )
            
            results.append(release_info)
        
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