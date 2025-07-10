from celery import Celery
import time
import logging
import os

import sys
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/backend')

import requests
from backend.app.core.config import settings
from backend.app.models.event import Event
from backend.app.models.base import SessionLocal
# Celery 앱 생성
app = Celery('background_tasks')

# Redis URL을 환경변수에서 가져오기
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Redis 설정
app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.task
def simple_task(message):
    """간단한 테스트 태스크"""
    logger.info(f"Task started: {message}")
    time.sleep(5)  # 5초 대기
    result = f"Task completed: {message}"
    logger.info(result)
    return result

@app.task
def data_collection_task():
    """FRED releases/dates API에서 데이터를 받아 event DB에 저장하는 태스크"""
    logger.info("FRED releases/dates API 호출 시작")
    try:
        data = fetch_release_dates()
        logger.info(f"API 응답 받음. release_dates 개수: {len(data.get('release_dates', []))}")
    except Exception as e:
        logger.error(f"release_dates API 호출 실패: {e}")
        return f"API 호출 실패: {e}"

    # SQLAlchemy를 사용한 DB 저장
    db = SessionLocal()
    try:
        saved_count = 0
        total_items = len(data.get('release_dates', []))
        logger.info(f"총 {total_items}개 release_dates 처리 시작")

        for idx, item in enumerate(data.get('release_dates', []), 1):
            release_id = str(item.get('release_id'))  # 문자열로 변환
            date = item.get('date')

            if idx % 50 == 0:  # 50개마다 진행상황 로그
                logger.info(f"진행상황: {idx}/{total_items} 처리 중...")

            # 기존 데이터 체크 (중복 방지)
            existing = db.query(Event).filter_by(
                release_id=release_id,
                date=date
            ).first()

            if not existing:
                logger.debug(f"새 이벤트 생성: release_id={release_id}, date={date}")
                # 추가 정보 확보: release 이름, 대표 시리즈 title/notes 등 가져오기
                release_info = get_release_metadata(release_id)
                series_info = get_representative_series_info(release_id)

                # 이벤트 저장
                event = Event(
                    release_id=release_id,
                    date=date,
                    title=series_info.get("title"),
                    description=series_info.get("notes"),
                    impact=resolve_impact_with_ai(series_info),
                    category_id=resolve_category_id_with_ai(series_info),
                    source="FRED"
                )

                # TODO: title, description이 모두 null인 애들이 있음.
                # 그런 애들 어떻게 처리할 지 고민민
                db.add(event)
                saved_count += 1
            else:
                logger.debug(f"기존 이벤트 존재: release_id={release_id}, date={date}")

        logger.info(f"DB commit 시작...")
        db.commit()
        logger.info(f"DB 저장 완료. 새로 저장된 이벤트: {saved_count}개")
        return f"FRED 데이터 저장 완료. 새로 저장된 이벤트: {saved_count}개"

    except Exception as e:
        db.rollback()
        logger.error(f"DB 저장 실패: {e}")
        return f"DB 저장 실패: {e}"
    finally:
        db.close()

def fetch_release_dates():
    """FRED releases/dates API 호출 및 응답 반환"""
    from datetime import datetime, timedelta

    # 오늘 기준 ±30일 범위 계산
    today = datetime.now()
    start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = (today + timedelta(days=30)).strftime('%Y-%m-%d')

    FRED_URL = 'https://api.stlouisfed.org/fred/releases/dates'
    params = {
        'api_key': settings.FRED_API_KEY,
        'file_type': 'json',
        'realtime_start': start_date,
        'realtime_end': end_date,
    }
    logger.info(f"FRED API 호출 범위: {start_date} ~ {end_date}")
    response = requests.get(FRED_URL, params=params)
    response.raise_for_status()
    return response.json()

def get_release_metadata(release_id):
    """FRED release 메타데이터를 가져온다."""
    try:
        resp = requests.get(
            'https://api.stlouisfed.org/fred/release',
            params={
                'release_id': release_id,
                'api_key': settings.FRED_API_KEY,
                'file_type': 'json'
            }
        )
        return resp.json().get('releases', [{}])[0]
    except Exception as e:
        logger.warning(f"release_id={release_id} 메타데이터 조회 실패: {e}")
        return {}

def get_representative_series_info(release_id):
    """release_id에 대한 대표 시리즈 정보를 가져온다."""
    try:
        series_list = requests.get(
            'https://api.stlouisfed.org/fred/release/series',
            params={
                'release_id': release_id,
                'api_key': settings.FRED_API_KEY,
                'file_type': 'json'
            }
        ).json().get('seriess', [])

        # popularity 기준으로 정렬 후 가장 인기 있는 시리즈 반환
        preferred = sorted(series_list, key=lambda x: x.get('popularity', 0), reverse=True)
        return preferred[0] if preferred else {}

    except Exception as e:
        logger.warning(f"release_id={release_id} 시리즈 조회 실패: {e}")
        return {}

def resolve_impact_with_ai(series_info):
    """AI를 사용하여 series 정보를 기반으로 증시 영향도 (High/Medium/Low)를 판단"""
    # TODO: 이 함수는 LLM 호출로 중요도 판단하도록 수정 필요.
    # 임시 더미: 항상 'Medium' 반환 (Low/Medium/High)
    return "Medium"

def resolve_category_id_with_ai(series_info):
    """AI를 사용하여 series 정보를 기반으로 상위 카테고리 ID를 결정"""
    # TODO: 이 함수는 LLM 호출로 카테고리를 판단하도록 수정 필요.
    # 임시 더미: 항상 None 반환
    return None

if __name__ == '__main__':
    # 워커 실행
    app.start()