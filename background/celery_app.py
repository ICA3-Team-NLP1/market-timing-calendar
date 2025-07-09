from celery import Celery
import time
import logging
import os

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
    """데이터 수집 태스크"""
    logger.info("Data collection started")
    time.sleep(10)  # 실제 데이터 수집 시뮬레이션
    logger.info("Data collection completed")
    return "Data collection finished"

if __name__ == '__main__':
    # 워커 실행
    app.start()