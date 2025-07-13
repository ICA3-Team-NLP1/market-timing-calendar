from celery import Celery
import time
import logging
import os

import sys
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/backend')
sys.path.insert(0, '/app/background')

import requests
from backend.app.constants import UserLevel
from backend.app.core.config import settings
from backend.app.core.database import db

# DB 초기화
db.init_db(settings.DB_INFO)

# 모델 import는 DB 초기화 후에 수행
from backend.app.models import Events
from sqlalchemy.orm import configure_mappers

# SQLAlchemy mapper 명시적 구성 (순환 참조 해결)
try:
    configure_mappers()
except Exception as e:
    print(f"Mapper configuration warning: {e}")
    # 경고는 무시하고 계속 진행

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

# 배치 처리 설정
BATCH_SIZE = int(os.getenv('LLM_BATCH_SIZE', '10'))  # 기본값을 50에서 10으로 줄임
API_DELAY = float(os.getenv('LLM_API_DELAY', '0.5'))  # API 호출 간 딜레이 (초)
MAX_RETRIES = int(os.getenv('LLM_MAX_RETRIES', '3'))  # 최대 재시도 횟수

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
    # Context manager를 사용하여 세션 관리
    try:
        with db.session as session:
            saved_count = 0
            failed_count = 0
            total_items = len(data.get('release_dates', []))
            logger.info(f"총 {total_items}개 release_dates 처리 시작")

            for idx, item in enumerate(data.get('release_dates', []), 1):
                release_id = str(item.get('release_id'))  # 문자열로 변환
                date = item.get('date')

                if idx % BATCH_SIZE == 0:  # 배치 크기마다 진행상황 로그
                    logger.info(f"진행상황: {idx}/{total_items} 처리 중... (성공: {saved_count}, 실패: {failed_count})")

                # 기존 데이터 체크 (중복 방지)
                existing = session.query(Events).filter_by(
                    release_id=release_id,
                    date=date
                ).first()

                if not existing:
                    logger.debug(f"새 이벤트 생성: release_id={release_id}, date={date}")
                    
                    try:
                        # 추가 정보 확보: release 이름, 대표 시리즈 title/notes 등 가져오기
                        release_info = get_release_metadata(release_id)
                        series_info = get_representative_series_info(release_id)

                        # LLM 호출 시도 (오류 처리 포함)
                        impact = resolve_impact_with_ai_safe(release_info.get("name", ""), series_info)
                        level = resolve_level_with_ai_safe(release_info.get("name", ""), series_info)

                        # 이벤트 저장
                        event = Events(
                            release_id=release_id,
                            date=date,
                            title=series_info.get("title"),
                            description=series_info.get("notes"),
                            impact=impact,
                            level=level,
                            source="FRED"
                        )

                        session.add(event)
                        saved_count += 1
                        
                        # API 호출 간 딜레이 추가 (Rate limiting 방지)
                        time.sleep(API_DELAY)
                        
                    except Exception as e:
                        logger.error(f"이벤트 처리 중 오류 (release_id={release_id}): {e}")
                        failed_count += 1
                        
                        # LLM 호출 실패 시 기본값으로 저장
                        event = Events(
                            release_id=release_id,
                            date=date,
                            title=series_info.get("title") if 'series_info' in locals() else None,
                            description=series_info.get("notes") if 'series_info' in locals() else None,
                            impact="MEDIUM",  # 대문자로 변경
                            level="INTERMEDIATE",  # 이미 대문자임
                            source="FRED"
                        )
                        session.add(event)
                        saved_count += 1
                        
                else:
                    logger.debug(f"기존 이벤트 존재: release_id={release_id}, date={date}")

            logger.info(f"DB commit 시작...")
            session.commit()
            logger.info(f"DB 저장 완료. 새로 저장된 이벤트: {saved_count}개, 실패: {failed_count}개")
            return f"FRED 데이터 저장 완료. 새로 저장된 이벤트: {saved_count}개, 실패: {failed_count}개"

    except Exception as e:
        logger.error(f"DB 저장 실패: {e}")
        return f"DB 저장 실패: {e}"

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

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from background.prompts.etl_prompts import impact_prompt, level_prompt

def get_llm():
    provider = settings.ACTIVE_LLM_PROVIDER  # 예: "openai" 또는 "anthropic"
    model = settings.ACTIVE_LLM_MODEL        # 예: "gpt-4o" 또는 "claude-3-5-sonnet-latest"
    # 1. OpenAI API 키 환경변수에 세팅
    if provider == "openai":
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        return ChatOpenAI(model=model, temperature=0)
    elif provider == "anthropic":
        os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
        return ChatAnthropic(model=model, temperature=0)
    else:
        raise ValueError("지원하지 않는 LLM provider입니다.")

def resolve_impact_with_ai(release_name, series_info):
    """AI를 사용하여 series 정보를 기반으로 증시 영향도 (High/Medium/Low)를 판단"""
    # 1. llm 인스턴스 생성
    llm = get_llm()

    # 2. 프롬프트 템플릿 준비 및 LLM 체인 생성
    impact_prompt_template = ChatPromptTemplate.from_template(impact_prompt)
    impact_chain = impact_prompt_template | llm | StrOutputParser()

    # 3. series_info에서 필요한 정보 추출
    title = series_info.get("title", "")
    name = release_name
    notes = series_info.get("notes", "")
    source = series_info.get("source", "")

    logger.info(f"[임팩트 추론] LLM 예측 시작: title={title}, name={name}")

    # 4. LLM에 입력값 전달하여 임팩트 예측
    result = impact_chain.invoke({
        "title": title,
        "name": name,
        "notes": notes,
        "source": source
    })

    # 5. 결과 후처리 및 반환
    result = result.strip().upper()  # 대문자로 변환
    if result in ["HIGH", "MEDIUM", "LOW"]:
        logger.info(f"[임팩트 추론] 예측 결과: {result}")
        return result
    else:
        logger.warning(f"[임팩트 추론] 예측 결과가 임팩트 값에 없음. MEDIUM으로 반환: {result}")
        return "MEDIUM"  # 대문자로 변경


def resolve_level_with_ai(release_name, series_info):
    """AI를 사용하여 series 정보를 기반으로 학습 레벨 (BEGINNER/INTERMEDIATE/ADVANCED)을 판단"""
    # 1. llm 인스턴스 생성
    llm = get_llm()

    # 2. 프롬프트 템플릿 준비 및 LLM 체인 생성
    level_prompt_template = ChatPromptTemplate.from_template(level_prompt)
    level_chain = level_prompt_template | llm | StrOutputParser()

    # 3. series_info에서 필요한 정보 추출
    title = series_info.get("title", "")
    name = release_name
    notes = series_info.get("notes", "")
    source = series_info.get("source", "")

    logger.info(f"[레벨 추론] LLM 예측 시작: title={title}, name={name}")

    # 4. LLM에 입력값 전달하여 레벨 예측
    result = level_chain.invoke({
        "title": title,
        "name": name,
        "notes": notes,
        "source": source
    })

    # 5. 결과 후처리 및 반환
    result = result.strip().upper()  # 대문자로 변환
    if result in [level.value for level in UserLevel]:
        logger.info(f"[레벨 추론] 예측 결과: {result}")
        return result
    else:
        logger.warning(f"[레벨 추론] 예측 결과가 레벨 값에 없음. ADVANCED로 반환: {result}")
        return "ADVANCED"  # 더 합리적인 기본값으로 변경


def resolve_impact_with_ai_safe(release_name, series_info):
    """AI를 사용하여 영향도를 판단하되, 실패 시 재시도 후 기본값 반환"""
    for attempt in range(MAX_RETRIES):
        try:
            return resolve_impact_with_ai(release_name, series_info)
        except Exception as e:
            logger.warning(f"[임팩트 추론] LLM 호출 실패 (시도 {attempt + 1}/{MAX_RETRIES}): {e}")
            
            if attempt < MAX_RETRIES - 1:
                # 재시도 전 대기 시간 (지수 백오프)
                wait_time = API_DELAY * (2 ** attempt)
                logger.info(f"[임팩트 추론] {wait_time}초 후 재시도...")
                time.sleep(wait_time)
            else:
                logger.error(f"[임팩트 추론] 모든 재시도 실패, 기본값 반환")
                return "MEDIUM"  # 대문자로 변경


def resolve_level_with_ai_safe(release_name, series_info):
    """AI를 사용하여 레벨을 판단하되, 실패 시 재시도 후 기본값 반환"""
    for attempt in range(MAX_RETRIES):
        try:
            return resolve_level_with_ai(release_name, series_info)
        except Exception as e:
            logger.warning(f"[레벨 추론] LLM 호출 실패 (시도 {attempt + 1}/{MAX_RETRIES}): {e}")
            
            if attempt < MAX_RETRIES - 1:
                # 재시도 전 대기 시간 (지수 백오프)
                wait_time = API_DELAY * (2 ** attempt)
                logger.info(f"[레벨 추론] {wait_time}초 후 재시도...")
                time.sleep(wait_time)
            else:
                logger.error(f"[레벨 추론] 모든 재시도 실패, 기본값 반환")
                return "ADVANCED"  # 문자열로 직접 반환


def batch_process_with_fallback(items, batch_size=50):
    """배치 단위로 처리하되, 실패 시 더 작은 배치로 재시도"""
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        try:
            # 배치 처리 로직
            batch_results = process_batch(batch)
            results.extend(batch_results)
            
            # 배치 간 딜레이
            time.sleep(1)
            
        except Exception as e:
            logger.warning(f"배치 처리 실패, 개별 처리로 변경: {e}")
            
            # 개별 처리로 fallback
            for item in batch:
                try:
                    result = process_single_item(item)
                    results.append(result)
                    time.sleep(0.1)  # 개별 처리 시 더 짧은 딜레이
                except Exception as item_error:
                    logger.error(f"개별 아이템 처리 실패: {item_error}")
                    results.append(None)  # 실패 시 None으로 표시
    
    return results


def process_batch(batch):
    """배치 처리 함수 (구현 예정)"""
    # TODO: 여러 이벤트를 한 번에 처리하는 로직 구현
    pass


def process_single_item(item):
    """단일 아이템 처리 함수 (구현 예정)"""
    # TODO: 단일 이벤트 처리 로직 구현
    pass

if __name__ == '__main__':
    # 워커 실행
    app.start()