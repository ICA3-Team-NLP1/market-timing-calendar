FROM python:3.11-slim AS celery-worker
WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && \
    apt-get install -y gcc libpq-dev curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY background/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PATH="/usr/local/bin:$PATH"

# Celery 설치 확인
RUN python -c "import celery; print('Celery version:', celery.__version__)"
RUN which celery || echo "Celery not found in PATH"

# Health check 스크립트 생성 (프로세스 확인 방식)
RUN echo '#!/bin/bash\nps aux | grep "celery.*worker" | grep -v grep || exit 1' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# 실행 명령
CMD ["bash", "-c", "celery -A background.celery_app worker --loglevel=info"]