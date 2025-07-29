#!/bin/bash

# Celery 테스트 스크립트
# 사용법: cd repository_root & ./background/celery-test.sh [task_name] [start_date] [end_date]

TASK_NAME=${1:-"background.celery_app.data_collection_task"}
START_DATE=${2:-"2025-06-01"}
END_DATE=${3:-"2025-08-31"}

echo "🚀 Celery 태스크 실행 중: $TASK_NAME"
echo "📅 데이터 수집 기간: $START_DATE ~ $END_DATE"
echo "📋 명령어: FRED_START_DATE=$START_DATE FRED_END_DATE=$END_DATE docker-compose exec background celery -A background.celery_app call $TASK_NAME"
echo ""

# 태스크 파라미터로 날짜 전달
TASK_ID=$(docker-compose exec background celery -A background.celery_app call $TASK_NAME --args='["'$START_DATE'", "'$END_DATE'"]')

echo "✅ 태스크 실행됨: $TASK_ID"
echo ""
echo "📊 로그 확인하려면 다음 명령어 사용:"
echo "docker-compose logs background -f"
echo ""
echo "🔄 다른 유용한 명령어들:"
echo "# 모든 태스크 목록 확인"
echo "docker-compose exec background celery -A background.celery_app inspect active"
echo ""
echo "# 워커 상태 확인"
echo "docker-compose exec background celery -A background.celery_app inspect ping"
echo ""
echo "💡 다른 기간으로 실행하려면:"
echo "./background/celery-test.sh background.celery_app.data_collection_task 2025-01-01 2025-12-31" 
