#!/bin/bash

# 사용법: ./aws-celery-cloudwatch.sh [start_date] [end_date]
# 예시: ./aws-celery-cloudwatch.sh 2025-06-01 2025-08-31

START_DATE=${1:-"2025-06-01"}
END_DATE=${2:-"2025-08-31"}

echo "🔍 AWS ECS Background Worker에서 Celery 작업 실행 중..."
echo "📅 데이터 수집 기간: $START_DATE ~ $END_DATE"

# 1. 실행 중인 태스크 찾기
echo "📋 실행 중인 Background Worker 태스크 확인 중..."
TASK_ARN=$(aws ecs list-tasks \
  --cluster market-timing-calendar \
  --service-name market-timing-background-service \
  --region ap-northeast-2 \
  --query 'taskArns[0]' \
  --output text)

if [ "$TASK_ARN" == "None" ] || [ -z "$TASK_ARN" ]; then
  echo "❌ 실행 중인 Background Worker 태스크를 찾을 수 없습니다."
  exit 1
fi

echo "✅ 태스크 발견: $TASK_ARN"

# 2. 실행 중인 Background Worker에 직접 Celery 작업 실행
echo "🔄 Background Worker에 Celery 작업 실행 중..."
echo ""

# 태스크 파라미터로 날짜 전달하는 Python 명령어 생성
PYTHON_COMMAND="from background.celery_app import data_collection_task; result = data_collection_task.delay('$START_DATE', '$END_DATE'); print(f'Task ID: {result.id}'); print(f'Task Status: {result.status}')"

# 임시 태스크를 실행하여 Celery 작업 전송
aws ecs run-task \
  --cluster market-timing-calendar \
  --task-definition market-timing-background \
  --region ap-northeast-2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-039ee1cea06ad607d,subnet-07754bbf4bae16102,subnet-09daf5213e683e46e,subnet-0e996f670896dfa76],securityGroups=[sg-0ae736da1af062d9d],assignPublicIp=ENABLED}" \
  --overrides "{
    \"containerOverrides\": [
      {
        \"name\": \"market-timing-background\",
        \"command\": [
          \"python\", \"-c\", \"$PYTHON_COMMAND\"
        ]
      }
    ]
  }"

echo ""
echo "✅ Celery 작업 실행 완료!"
echo "📊 CloudWatch 로그에서 결과를 확인하세요:"
echo "   https://ap-northeast-2.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-2#logsV2:log-groups/log-group/ecs/market-timing-calendar"
echo ""
echo "💡 다른 기간으로 실행하려면:"
echo "   ./aws-celery-cloudwatch.sh 2025-01-01 2025-12-31"
