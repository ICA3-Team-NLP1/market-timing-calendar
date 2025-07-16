#!/bin/bash
# 테스트 실행 스크립트

echo "🚀 테스트 시작..."

# postgres-test가 실행 중인지 확인
if ! docker-compose ps postgres | grep -q "Up"; then
    echo "❌ postgres-test 서비스가 실행되지 않음. 서비스를 시작합니다..."
    docker-compose up -d postgres
    
    # postgres-test가 준비될 때까지 대기
    echo "⏳ 테스트 DB 준비 중..."
    docker-compose exec postgres bash -c 'until pg_isready -U postgres -d market_timing_test; do sleep 1; done'
fi

# app이 실행 중인지 확인
if ! docker-compose ps app | grep -q "Up"; then
    echo "❌ app 서비스가 실행되지 않음. 서비스를 시작합니다..."
    docker-compose up -d app
    
    # app이 준비될 때까지 대기
    echo "⏳ 앱 서비스 준비 중..."
    sleep 5
fi

echo "🔧 테스트용 데이터베이스 URL: $TEST_DATABASE_URL"
echo "🔧 테스트용 데이터베이스 HOST: $TEST_DB_HOST"

# pytest 실행 (TEST_DATABASE_URL을 DATABASE_URL로 오버라이드)
echo "🧪 pytest 실행 중..."
docker-compose exec app bash -c "
    export DATABASE_URL=\$TEST_DATABASE_URL
    export TEST_DB_HOST=\$TEST_DB_HOST
    echo '✅ 테스트 DB URL 설정: '\$DATABASE_URL
    python -m pytest backend/tests/ -v --tb=short
"

echo "✨ 테스트 완료!"