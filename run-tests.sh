#!/bin/bash
# 테스트 실행 스크립트

echo "🚀 테스트 시작..."

# postgres가 실행 중인지 확인
if ! docker-compose ps postgres | grep -q "Up"; then
    echo "❌ postgres 서비스가 실행되지 않음. 서비스를 시작합니다..."
    docker-compose up -d postgres
    
    # postgres가 준비될 때까지 대기
    echo "⏳ 테스트 DB 준비 중..."
    # 이 명령어는 컨테이너 내부에서 실행되므로, 호스트의 pg_isready가 아닌 컨테이너의 것을 사용합니다.
    until docker-compose exec postgres pg_isready -U postgres -d market_timing_test -q; do
      echo "Postgres is unavailable - sleeping"
      sleep 1
    done
fi

# app이 실행 중인지 확인
if ! docker-compose ps app | grep -q "Up"; then
    echo "❌ app 서비스가 실행되지 않음. 서비스를 시작합니다..."
    docker-compose up -d app
    
    # app이 준비될 때까지 대기
    echo "⏳ 앱 서비스 준비 중..."
    sleep 5
fi

# pytest 실행. 이제 컨테이너는 시작 시점부터 올바른 환경변수를 가지고 있습니다.
echo "🧪 pytest 실행 중..."
docker-compose exec app bash -c "
    echo '🐍 Installing dependencies for testing...'
    pip install -r backend/requirements.txt
    echo '✅ 테스트 환경 변수 확인:'
    echo '   - DATABASE_URL: \$DATABASE_URL'
    echo '   - TEST_DB_HOST: \$TEST_DB_HOST'
    python -m pytest backend/tests/ -v --tb=short
"

echo "✨ 테스트 완료!"