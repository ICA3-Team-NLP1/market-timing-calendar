#!/bin/bash

# AWS 리소스 상태 확인 스크립트

set -e

AWS_REGION="ap-northeast-2"
ECR_REGISTRY="692631066742.dkr.ecr.ap-northeast-2.amazonaws.com"
ECR_REPOSITORY="market-timing-calendar"
ECS_CLUSTER="market-timing-calendar"
ECS_SERVICE="market-timing-calendar-service"
BACKGROUND_SERVICE="market-timing-background-service"

echo "🔍 AWS 리소스 상태 확인 중..."
echo "=================================="

# 1. ECS 클러스터 확인
echo "📦 ECS 클러스터 확인..."
CLUSTER_STATUS=$(aws ecs describe-clusters \
  --clusters $ECS_CLUSTER \
  --region $AWS_REGION \
  --query 'clusters[0].{Name:clusterName,Status:status,ActiveServicesCount:activeServicesCount,RunningTasksCount:runningTasksCount}' \
  --output json 2>/dev/null || echo '{"Name":"NOT_FOUND","Status":"NOT_FOUND","ActiveServicesCount":0,"RunningTasksCount":0}')

echo "클러스터 상태: $CLUSTER_STATUS"
echo ""

# 2. ECS 서비스 확인
echo "🔄 ECS 서비스 확인..."

# 메인 앱 서비스
MAIN_SERVICE_STATUS=$(aws ecs describe-services \
  --cluster $ECS_CLUSTER \
  --services $ECS_SERVICE \
  --region $AWS_REGION \
  --query 'services[0].{ServiceName:serviceName,Status:status,RunningCount:runningCount,DesiredCount:desiredCount,TaskDefinition:taskDefinition}' \
  --output json 2>/dev/null || echo '{"ServiceName":"NOT_FOUND","Status":"NOT_FOUND","RunningCount":0,"DesiredCount":0,"TaskDefinition":"NOT_FOUND"}')

echo "메인 앱 서비스: $MAIN_SERVICE_STATUS"

# Background Worker 서비스
BACKGROUND_SERVICE_STATUS=$(aws ecs describe-services \
  --cluster $ECS_CLUSTER \
  --services $BACKGROUND_SERVICE \
  --region $AWS_REGION \
  --query 'services[0].{ServiceName:serviceName,Status:status,RunningCount:runningCount,DesiredCount:desiredCount,TaskDefinition:taskDefinition}' \
  --output json 2>/dev/null || echo '{"ServiceName":"NOT_FOUND","Status":"NOT_FOUND","RunningCount":0,"DesiredCount":0,"TaskDefinition":"NOT_FOUND"}')

echo "Background Worker 서비스: $BACKGROUND_SERVICE_STATUS"
echo ""

# 3. 태스크 정의 확인
echo "📋 태스크 정의 확인..."

# 메인 앱 태스크 정의
MAIN_TASK_DEF=$(aws ecs describe-task-definition \
  --task-definition market-timing-app \
  --region $AWS_REGION \
  --query 'taskDefinition.{Family:family,Revision:revision,Status:status,Image:containerDefinitions[0].image}' \
  --output json 2>/dev/null || echo '{"Family":"NOT_FOUND","Revision":0,"Status":"NOT_FOUND","Image":"NOT_FOUND"}')

echo "메인 앱 태스크 정의: $MAIN_TASK_DEF"

# Background Worker 태스크 정의
BACKGROUND_TASK_DEF=$(aws ecs describe-task-definition \
  --task-definition market-timing-background \
  --region $AWS_REGION \
  --query 'taskDefinition.{Family:family,Revision:revision,Status:status,Image:containerDefinitions[0].image}' \
  --output json 2>/dev/null || echo '{"Family":"NOT_FOUND","Revision":0,"Status":"NOT_FOUND","Image":"NOT_FOUND"}')

echo "Background Worker 태스크 정의: $BACKGROUND_TASK_DEF"
echo ""

# 4. ECR 이미지 확인
echo "🐳 ECR 이미지 확인..."

# ECR 리포지토리 존재 확인
ECR_REPO_EXISTS=$(aws ecr describe-repositories \
  --repository-names $ECR_REPOSITORY \
  --region $AWS_REGION \
  --query 'repositories[0].repositoryName' \
  --output text 2>/dev/null || echo "NOT_FOUND")

echo "ECR 리포지토리: $ECR_REPO_EXISTS"

# 이미지 태그 확인
if [ "$ECR_REPO_EXISTS" != "NOT_FOUND" ]; then
  echo "이미지 태그 목록:"
  aws ecr describe-images \
    --repository-name $ECR_REPOSITORY \
    --region $AWS_REGION \
    --query 'imageDetails[].{Tag:imageTags[0],PushedAt:imagePushedAt}' \
    --output table 2>/dev/null || echo "이미지가 없습니다."
else
  echo "ECR 리포지토리가 존재하지 않습니다."
fi
echo ""

# 5. Secrets Manager 확인
echo "🔐 Secrets Manager 확인..."

# 필요한 시크릿 목록
SECRETS=(
  "market-timing-calendar/database-url"
  "market-timing-calendar/redis-url"
  "market-timing-calendar/fred-api-key"
  "market-timing-calendar/openai-api-key"
  "market-timing-calendar/anthropic-api-key"
  "market-timing-calendar/active-llm-provider"
  "market-timing-calendar/active-llm-model"
  "market-timing-calendar/langfuse-public-key"
  "market-timing-calendar/langfuse-secret-key"
  "market-timing-calendar/langfuse-host"
  "market-timing-calendar/fastapi-env"
  "market-timing-calendar/mem0-api-key"
  "market-timing-calendar/firebase-service-account-key"
)

echo "시크릿 존재 여부:"
for secret in "${SECRETS[@]}"; do
  SECRET_EXISTS=$(aws secretsmanager describe-secret \
    --secret-id $secret \
    --region $AWS_REGION \
    --query 'Name' \
    --output text 2>/dev/null || echo "NOT_FOUND")
  
  if [ "$SECRET_EXISTS" != "NOT_FOUND" ]; then
    echo "✅ $secret"
  else
    echo "❌ $secret"
  fi
done
echo ""

# 6. 네트워크 설정 확인
echo "🌐 네트워크 설정 확인..."

# VPC 확인
VPC_INFO=$(aws ec2 describe-vpcs \
  --filters "Name=tag:Name,Values=*market-timing*" \
  --query 'Vpcs[0].{VpcId:VpcId,CidrBlock:CidrBlock}' \
  --output json 2>/dev/null || echo '{"VpcId":"NOT_FOUND","CidrBlock":"NOT_FOUND"}')

echo "VPC 정보: $VPC_INFO"

# 서브넷 확인
if [ "$(echo $VPC_INFO | jq -r '.VpcId')" != "NOT_FOUND" ]; then
  VPC_ID=$(echo $VPC_INFO | jq -r '.VpcId')
  SUBNETS=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    --query 'Subnets[].{SubnetId:SubnetId,CidrBlock:CidrBlock,AvailabilityZone:AvailabilityZone}' \
    --output json 2>/dev/null || echo '[]')
  
  echo "서브넷 정보: $SUBNETS"
else
  echo "VPC를 찾을 수 없어 서브넷 정보를 확인할 수 없습니다."
fi

# 보안 그룹 확인
if [ "$(echo $VPC_INFO | jq -r '.VpcId')" != "NOT_FOUND" ]; then
  SECURITY_GROUPS=$(aws ec2 describe-security-groups \
    --filters "Name=vpc-id,Values=$VPC_ID" "Name=group-name,Values=*market-timing*" \
    --query 'SecurityGroups[].{GroupId:GroupId,GroupName:GroupName}' \
    --output json 2>/dev/null || echo '[]')
  
  echo "보안 그룹 정보: $SECURITY_GROUPS"
else
  echo "VPC를 찾을 수 없어 보안 그룹 정보를 확인할 수 없습니다."
fi
echo ""

# 7. 실행 중인 태스크 확인
echo "🎯 실행 중인 태스크 확인..."

# 메인 앱 태스크
MAIN_TASKS=$(aws ecs list-tasks \
  --cluster $ECS_CLUSTER \
  --service-name $ECS_SERVICE \
  --desired-status RUNNING \
  --region $AWS_REGION \
  --query 'taskArns' \
  --output text 2>/dev/null || echo "")

if [ -n "$MAIN_TASKS" ]; then
  echo "메인 앱 실행 중인 태스크: $MAIN_TASKS"
else
  echo "메인 앱 실행 중인 태스크: 없음"
fi

# Background Worker 태스크
BACKGROUND_TASKS=$(aws ecs list-tasks \
  --cluster $ECS_CLUSTER \
  --service-name $BACKGROUND_SERVICE \
  --desired-status RUNNING \
  --region $AWS_REGION \
  --query 'taskArns' \
  --output text 2>/dev/null || echo "")

if [ -n "$BACKGROUND_TASKS" ]; then
  echo "Background Worker 실행 중인 태스크: $BACKGROUND_TASKS"
else
  echo "Background Worker 실행 중인 태스크: 없음"
fi
echo ""

# 8. 요약 리포트
echo "📊 리소스 상태 요약"
echo "=================="

# 클러스터 상태
CLUSTER_NAME=$(echo $CLUSTER_STATUS | jq -r '.Name')
if [ "$CLUSTER_NAME" != "NOT_FOUND" ]; then
  echo "✅ ECS 클러스터: $CLUSTER_NAME"
else
  echo "❌ ECS 클러스터: 생성 필요"
fi

# 메인 앱 서비스
MAIN_SERVICE_NAME=$(echo $MAIN_SERVICE_STATUS | jq -r '.ServiceName')
if [ "$MAIN_SERVICE_NAME" != "NOT_FOUND" ]; then
  echo "✅ 메인 앱 서비스: $MAIN_SERVICE_NAME"
else
  echo "❌ 메인 앱 서비스: 생성 필요"
fi

# Background Worker 서비스
BACKGROUND_SERVICE_NAME=$(echo $BACKGROUND_SERVICE_STATUS | jq -r '.ServiceName')
if [ "$BACKGROUND_SERVICE_NAME" != "NOT_FOUND" ]; then
  echo "✅ Background Worker 서비스: $BACKGROUND_SERVICE_NAME"
else
  echo "❌ Background Worker 서비스: 생성 필요"
fi

# ECR 리포지토리
if [ "$ECR_REPO_EXISTS" != "NOT_FOUND" ]; then
  echo "✅ ECR 리포지토리: $ECR_REPO_EXISTS"
else
  echo "❌ ECR 리포지토리: 생성 필요"
fi

echo ""
echo "🔧 다음 단계:"
echo "1. 누락된 리소스가 있다면 생성"
echo "2. ./deploy.sh 실행하여 배포"
echo "3. ./check-resources.sh 재실행하여 상태 확인" 