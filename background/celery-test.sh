#!/bin/bash

# Celery 테스트 스크립트
# 사용법: cd repository_root & ./background/celery-test.sh [task_name]

TASK_NAME=${1:-"background.celery_app.data_collection_task"}

echo "🚀 Celery 태스크 실행 중: $TASK_NAME"
echo "📋 명령어: sudo docker-compose exec background celery -A background.celery_app call $TASK_NAME"
echo ""

# 태스크 실행
TASK_ID=$(sudo docker-compose exec background celery -A background.celery_app call $TASK_NAME)

echo "✅ 태스크 실행됨: $TASK_ID"
echo ""
echo "📊 로그 확인하려면 다음 명령어 사용:"
echo "sudo docker-compose logs background -f"
echo ""
echo "🔄 다른 유용한 명령어들:"
echo "# 모든 태스크 목록 확인"
echo "sudo docker-compose exec background celery -A background.celery_app inspect active"
echo ""
echo "# 워커 상태 확인"
echo "sudo docker-compose exec background celery -A background.celery_app inspect ping" 