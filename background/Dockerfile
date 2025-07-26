FROM python:3.11-slim AS celery-worker
WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && \
    apt-get install -y gcc libpq-dev curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY background/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 전체 프로젝트 복사
COPY . .

# 환경변수 설정
ENV PYTHONPATH=/app
ENV PATH="/usr/local/bin:$PATH"

# Celery 설치 확인
RUN python -c "import celery; print('Celery version:', celery.__version__)"
RUN which celery || echo "Celery not found in PATH"

# 헬스체크용 스크립트 생성
RUN echo '#!/bin/bash\ncelery -A background.celery_app inspect ping || exit 1' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# CMD 명령어를 쉘 스크립트로 변경
CMD ["bash", "-c", "celery -A background.celery_app worker --loglevel=info"]