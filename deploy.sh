#!/bin/bash

# 전체 서비스 배포 스크립트 (메인 앱 + Background Worker)

set -e  # 오류 발생 시 스크립트 중단

# 환경 변수 설정
AWS_REGION="ap-northeast-2"
ECR_REGISTRY="692631066742.dkr.ecr.ap-northeast-2.amazonaws.com"
ECR_REPOSITORY="market-timing-calendar"
ECS_CLUSTER="market-timing-calendar"
ECS_SERVICE="market-timing-calendar-service"
BACKGROUND_SERVICE="market-timing-background-service"

echo "🚀 전체 서비스 배포 시작 (메인 앱 + Background Worker)..."

# 1. ECR 로그인
echo "📦 ECR 로그인 중..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# 2. 메인 앱 이미지 빌드 및 푸시
echo "🔨 메인 앱 이미지 빌드 중..."
docker build \
  --target production \
  -t $ECR_REGISTRY/$ECR_REPOSITORY:latest \
  .

echo "📤 메인 앱 이미지 푸시 중..."
docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

# 3. Background Worker 이미지 빌드 및 푸시
echo "🔨 Background Worker 이미지 빌드 중..."
docker build \
  -f background/Dockerfile \
  -t $ECR_REGISTRY/$ECR_REPOSITORY-background:latest \
  .

echo "📤 Background Worker 이미지 푸시 중..."
docker push $ECR_REGISTRY/$ECR_REPOSITORY-background:latest

# 4. 메인 앱 태스크 정의 등록
echo "📋 메인 앱 태스크 정의 등록 중..."
NEW_MAIN_TASK_DEF_ARN=$(aws ecs register-task-definition \
  --cli-input-json file://task-definition-main.json \
  --region $AWS_REGION \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text)

echo "새로운 메인 앱 태스크 정의: $NEW_MAIN_TASK_DEF_ARN"

# 5. Background Worker 태스크 정의 등록
echo "📋 Background Worker 태스크 정의 등록 중..."
NEW_BACKGROUND_TASK_DEF_ARN=$(aws ecs register-task-definition \
  --cli-input-json file://task-definition-background.json \
  --region $AWS_REGION \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text)

echo "새로운 Background Worker 태스크 정의: $NEW_BACKGROUND_TASK_DEF_ARN"

# 6. 메인 앱 서비스 업데이트
echo "🔄 메인 앱 서비스 업데이트 중..."
aws ecs update-service \
  --cluster $ECS_CLUSTER \
  --service $ECS_SERVICE \
  --task-definition $NEW_MAIN_TASK_DEF_ARN \
  --region $AWS_REGION

# 7. Background Worker 서비스 업데이트
echo "🔄 Background Worker 서비스 업데이트 중..."
aws ecs update-service \
  --cluster $ECS_CLUSTER \
  --service $BACKGROUND_SERVICE \
  --task-definition $NEW_BACKGROUND_TASK_DEF_ARN \
  --region $AWS_REGION

# 8. 배포 상태 확인
echo "⏳ 배포 완료 대기 중..."
sleep 30

echo "📊 배포 결과 확인 중..."

# 메인 앱 상태 확인
MAIN_STATUS=$(aws ecs describe-services \
  --cluster $ECS_CLUSTER \
  --services $ECS_SERVICE \
  --region $AWS_REGION \
  --query 'services[0].{Status:status,RunningCount:runningCount,DesiredCount:desiredCount}' \
  --output json)

echo "메인 앱 상태: $MAIN_STATUS"

# Background Worker 상태 확인
BACKGROUND_STATUS=$(aws ecs describe-services \
  --cluster $ECS_CLUSTER \
  --services $BACKGROUND_SERVICE \
  --region $AWS_REGION \
  --query 'services[0].{Status:status,RunningCount:runningCount,DesiredCount:desiredCount}' \
  --output json)

echo "Background Worker 상태: $BACKGROUND_STATUS"

echo "✅ 전체 배포 완료!"
echo "🔍 AWS ECS 콘솔에서 서비스 상태를 확인하세요." 