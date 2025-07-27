# AWS 환경 생성 가이드

## 개요
Market Timing Calendar 애플리케이션을 위한 AWS 환경 설정 가이드입니다.

## 사전 요구사항
- AWS CLI 설치 및 설정
- Docker 설치
- jq 설치 (JSON 파싱용)

## 1. ECR (Elastic Container Registry) 설정

### 1.1 ECR 리포지토리 생성
```bash
# 메인 앱 리포지토리
aws ecr create-repository \
  --repository-name market-timing-calendar \
  --region ap-northeast-2

# Background Worker 리포지토리
aws ecr create-repository \
  --repository-name market-timing-calendar-background \
  --region ap-northeast-2
```

### 1.2 ECR 로그인
```bash
aws ecr get-login-password --region ap-northeast-2 | \
docker login --username AWS --password-stdin 692631066742.dkr.ecr.ap-northeast-2.amazonaws.com
```

## 2. ECS (Elastic Container Service) 설정

### 2.1 ECS 클러스터 생성
```bash
aws ecs create-cluster \
  --cluster-name market-timing-calendar \
  --region ap-northeast-2
```

### 2.2 IAM 역할 생성

#### ECS Task Execution Role
```bash
# 신뢰 정책 생성
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# 역할 생성
aws iam create-role \
  --role-name ecsTaskExecutionRole-market-timing-calendar \
  --assume-role-policy-document file://trust-policy.json

# 정책 연결
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole-market-timing-calendar \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# 추가 권한 (Secrets Manager, ECR)
aws iam put-role-policy \
  --role-name ecsTaskExecutionRole-market-timing-calendar \
  --policy-name additional-permissions \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "secretsmanager:GetSecretValue",
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ],
        "Resource": "*"
      }
    ]
  }'
```

## 3. Secrets Manager 설정

### 3.1 필수 시크릿 생성
```bash
# 데이터베이스 URL
aws secretsmanager create-secret \
  --name market-timing-calendar/database-url \
  --description "Database URL for Market Timing Calendar" \
  --secret-string "postgresql://username:password@host:port/database" \
  --region ap-northeast-2

# Redis URL
aws secretsmanager create-secret \
  --name market-timing-calendar/redis-url \
  --description "Redis URL for Market Timing Calendar" \
  --secret-string "redis://market-timing-calendar-redis.bzqsot.0001.apn2.cache.amazonaws.com:6379/0" \
  --region ap-northeast-2

# FRED API Key
aws secretsmanager create-secret \
  --name market-timing-calendar/fred-api-key \
  --description "FRED API Key for Market Timing Calendar" \
  --secret-string "your-fred-api-key" \
  --region ap-northeast-2

# OpenAI API Key
aws secretsmanager create-secret \
  --name market-timing-calendar/openai-api-key \
  --description "OpenAI API Key for Market Timing Calendar" \
  --secret-string "your-openai-api-key" \
  --region ap-northeast-2

# Anthropic API Key
aws secretsmanager create-secret \
  --name market-timing-calendar/anthropic-api-key \
  --description "Anthropic API Key for Market Timing Calendar" \
  --secret-string "your-anthropic-api-key" \
  --region ap-northeast-2

# Active LLM Provider
aws secretsmanager create-secret \
  --name market-timing-calendar/active-llm-provider \
  --description "Active LLM Provider for Market Timing Calendar" \
  --secret-string "openai" \
  --region ap-northeast-2

# Active LLM Model
aws secretsmanager create-secret \
  --name market-timing-calendar/active-llm-model \
  --description "Active LLM Model for Market Timing Calendar" \
  --secret-string "gpt-4" \
  --region ap-northeast-2

# Langfuse Public Key
aws secretsmanager create-secret \
  --name market-timing-calendar/langfuse-public-key \
  --description "Langfuse Public Key for Market Timing Calendar" \
  --secret-string "your-langfuse-public-key" \
  --region ap-northeast-2

# Langfuse Secret Key
aws secretsmanager create-secret \
  --name market-timing-calendar/langfuse-secret-key \
  --description "Langfuse Secret Key for Market Timing Calendar" \
  --secret-string "your-langfuse-secret-key" \
  --region ap-northeast-2

# Langfuse Host
aws secretsmanager create-secret \
  --name market-timing-calendar/langfuse-host \
  --description "Langfuse Host for Market Timing Calendar" \
  --secret-string "https://cloud.langfuse.com" \
  --region ap-northeast-2

# FastAPI Environment
aws secretsmanager create-secret \
  --name market-timing-calendar/fastapi-env \
  --description "FastAPI Environment for Market Timing Calendar" \
  --secret-string "prod" \
  --region ap-northeast-2

# Mem0 API Key
aws secretsmanager create-secret \
  --name market-timing-calendar/mem0-api-key \
  --description "Mem0 API Key for Market Timing Calendar" \
  --secret-string "your-mem0-api-key" \
  --region ap-northeast-2

# JWT Secret
aws secretsmanager create-secret \
  --name market-timing-calendar/jwt-secret-cd5mGk \
  --description "JWT Secret for Market Timing Calendar" \
  --secret-string "your-jwt-secret" \
  --region ap-northeast-2

# Encryption Key
aws secretsmanager create-secret \
  --name market-timing-calendar/encryption-key \
  --description "Encryption Key for Market Timing Calendar" \
  --secret-string "your-encryption-key" \
  --region ap-northeast-2
```

## 4. ElastiCache Redis 설정

### 4.1 Redis 서브넷 그룹 생성
```bash
aws elasticache create-subnet-group \
  --subnet-group-name market-timing-calendar-redis \
  --subnet-ids subnet-039ee1cea06ad607d subnet-07754bbf4bae16102 \
  --description "Redis subnet group for Market Timing Calendar" \
  --region ap-northeast-2
```

### 4.2 Redis 클러스터 생성
```bash
aws elasticache create-replication-group \
  --replication-group-id market-timing-calendar-redis \
  --replication-group-description "Redis cluster for Market Timing Calendar" \
  --subnet-group-name market-timing-calendar-redis \
  --security-group-ids sg-0ae736da1af062d9d \
  --cache-node-type cache.t3.micro \
  --num-cache-clusters 1 \
  --region ap-northeast-2
```

## 5. 태스크 정의 등록

### 5.1 메인 앱 태스크 정의
```bash
aws ecs register-task-definition \
  --cli-input-json file://task-definition-main.json \
  --region ap-northeast-2
```

### 5.2 Background Worker 태스크 정의
```bash
aws ecs register-task-definition \
  --cli-input-json file://task-definition-background.json \
  --region ap-northeast-2
```

## 6. ECS 서비스 생성

### 6.1 메인 앱 서비스 생성
```bash
aws ecs create-service \
  --cluster market-timing-calendar \
  --service-name market-timing-calendar-service \
  --task-definition market-timing-app \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-039ee1cea06ad607d,subnet-07754bbf4bae16102,subnet-09daf5213e683e46e,subnet-0e996f670896dfa76],securityGroups=[sg-0ae736da1af062d9d],assignPublicIp=ENABLED}" \
  --region ap-northeast-2
```

### 6.2 Background Worker 서비스 생성
```bash
aws ecs create-service \
  --cluster market-timing-calendar \
  --service-name market-timing-background-service \
  --task-definition market-timing-background \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-039ee1cea06ad607d,subnet-07754bbf4bae16102,subnet-09daf5213e683e46e,subnet-0e996f670896dfa76],securityGroups=[sg-0ae736da1af062d9d],assignPublicIp=ENABLED}" \
  --region ap-northeast-2
```

## 7. 배포

### 7.1 전체 배포
```bash
./deploy.sh
```

### 7.2 개별 배포
```bash
# 메인 앱만 배포
./deploy-app.sh

# Background Worker만 배포
./deploy-background.sh
```

### 7.3 Celery 작업 실행
```bash
# CloudWatch를 통한 Celery 작업 실행
./aws-celery-cloudwatch.sh

```

## 8. 상태 확인

### 8.1 리소스 상태 확인
```bash
./check-resources.sh
```

### 8.2 로그 확인

#### 8.2.1 CloudWatch 콘솔에서 로그 확인
AWS CloudWatch 콘솔에서 로그를 확인할 수 있습니다:
- **URL**: https://ap-northeast-2.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-2#logsV2:log-groups
- **로그 그룹**: `/ecs/market-timing-calendar`

#### 8.2.2 CLI를 통한 로그 확인
```bash
# 메인 앱 로그
aws logs tail /ecs/market-timing-calendar --follow --region ap-northeast-2

# Background Worker 로그
aws logs tail /ecs/market-timing-calendar --follow --region ap-northeast-2
```

#### 8.2.3 로그스트림 필터링
실제 로그스트림 이름을 기반으로 필터링할 수 있습니다:

**실제 로그스트림 이름 패턴:**
- **메인 앱**: `fastapi-main-app/market-timing-calendar/태스크ID`
- **Background Worker**: `background-celery/market-timing-background/태스크ID`

```bash
# 메인 앱 태스크 로그 확인
aws logs describe-log-streams \
  --log-group-name /ecs/market-timing-calendar \
  --log-stream-name-prefix fastapi-main-app \
  --region ap-northeast-2

# Background Worker 태스크 로그 확인
aws logs describe-log-streams \
  --log-group-name /ecs/market-timing-calendar \
  --log-stream-name-prefix background-celery \
  --region ap-northeast-2
```

## 9. 환경 변수

### 9.1 필수 환경 변수
- `DATABASE_URL`: PostgreSQL 데이터베이스 URL
- `REDIS_URL`: Redis 연결 URL
- `FASTAPI_ENV`: 환경 설정 (prod/development/production)
- `FRED_API_KEY`: FRED API 키
- `OPENAI_API_KEY`: OpenAI API 키
- `ANTHROPIC_API_KEY`: Anthropic API 키
- `ACTIVE_LLM_PROVIDER`: 활성 LLM 제공자
- `ACTIVE_LLM_MODEL`: 활성 LLM 모델
- `LANGFUSE_PUBLIC_KEY`: Langfuse 공개 키
- `LANGFUSE_SECRET_KEY`: Langfuse 비밀 키
- `LANGFUSE_HOST`: Langfuse 호스트
- `MEM0_API_KEY`: Mem0 API 키
- `JWT_SECRET`: JWT 비밀 키
- `ENCRYPTION_KEY`: 암호화 키

### 9.2 AWS 리소스 정보
- **Account ID**: 692631066742
- **Region**: ap-northeast-2
- **ECR Registry**: 692631066742.dkr.ecr.ap-northeast-2.amazonaws.com
- **ECS Cluster**: market-timing-calendar
- **Main Service**: market-timing-calendar-service
- **Background Service**: market-timing-background-service
- **Redis Endpoint**: market-timing-calendar-redis.bzqsot.0001.apn2.cache.amazonaws.com:6379

## 10. 트러블슈팅

### 10.1 일반적인 문제들
1. **태스크 시작 실패**: IAM 역할 권한 확인
2. **이미지 풀 실패**: ECR 로그인 상태 확인
3. **데이터베이스 연결 실패**: Secrets Manager 설정 확인
4. **Redis 연결 실패**: ElastiCache 보안 그룹 설정 확인
5. **mem0 데이터 디렉토리 권한 문제**: Dockerfile에서 권한 설정 확인

### 10.2 헬스체크
메인 앱은 `/health` 엔드포인트를 제공합니다:
```bash
curl https://your-app-url/health
```

### 10.3 Background Worker 상태 확인
```bash
# 실행 중인 Background Worker 태스크 확인
aws ecs list-tasks \
  --cluster market-timing-calendar \
  --service-name market-timing-background-service \
  --region ap-northeast-2
```

## 11. 비용 최적화

### 11.1 리소스 크기 조정
- CPU/Memory: 현재 512/1024MB (필요시 조정)
- Redis: cache.t3.micro (필요시 업그레이드)
- ECS 서비스: desired-count 조정 가능

### 11.2 모니터링
- CloudWatch 메트릭 설정
- 비용 알림 설정
- 사용량 모니터링

## 12. 최신 업데이트 사항

### 12.1 Dockerfile 개선사항
- 비root 사용자 생성 및 홈 디렉토리 설정
- mem0 데이터 디렉토리 생성 및 권한 설정
- 보안 강화

### 12.2 Background Worker 개선사항
- Celery 작업 실행 스크립트 추가 (`aws-celery-cloudwatch.sh`)
- 헬스체크 스크립트 추가
- 로깅 개선

### 12.3 환경 변수 관리
- Secrets Manager를 통한 중앙화된 환경 변수 관리
- 모든 API 키 및 민감한 정보를 Secrets Manager로 이동
- 환경별 설정 분리 (test/prod/production) 