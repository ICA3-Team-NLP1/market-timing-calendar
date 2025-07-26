# ===== Stage 1: Node.js 의존성 및 빌드 =====
FROM node:20 AS frontend-deps
WORKDIR /app/frontend

# 빌드 시점 환경변수 선언
ARG VITE_FIREBASE_API_KEY
ARG VITE_FIREBASE_AUTH_DOMAIN
ARG VITE_FIREBASE_PROJECT_ID
ARG VITE_FIREBASE_STORAGE_BUCKET
ARG VITE_FIREBASE_MESSAGING_SENDER_ID
ARG VITE_FIREBASE_APP_ID
ARG VITE_FIREBASE_MEASUREMENT_ID

# 환경변수 설정
ENV VITE_FIREBASE_API_KEY=$VITE_FIREBASE_API_KEY
ENV VITE_FIREBASE_AUTH_DOMAIN=$VITE_FIREBASE_AUTH_DOMAIN
ENV VITE_FIREBASE_PROJECT_ID=$VITE_FIREBASE_PROJECT_ID
ENV VITE_FIREBASE_STORAGE_BUCKET=$VITE_FIREBASE_STORAGE_BUCKET
ENV VITE_FIREBASE_MESSAGING_SENDER_ID=$VITE_FIREBASE_MESSAGING_SENDER_ID
ENV VITE_FIREBASE_APP_ID=$VITE_FIREBASE_APP_ID
ENV VITE_FIREBASE_MEASUREMENT_ID=$VITE_FIREBASE_MEASUREMENT_ID

COPY frontend/package*.json ./
RUN npm ci --only=production && npm cache clean --force

FROM node:20 AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ===== Stage 2: Python 의존성 =====
FROM python:3.11-slim AS python-deps
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ===== Stage 3: 개발 환경 =====
FROM python:3.11-slim AS development

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python 의존성 복사
COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin

# React 빌드 파일 복사
COPY --from=frontend-builder /app/frontend/dist ./static

# 백엔드 코드 복사
COPY backend/ ./

# 헬스체크용 엔드포인트
RUN echo '{"status": "healthy"}' > ./static/health.json

# 개발용 포트
EXPOSE 8000

# 개발 환경 시작 스크립트 (초기화 포함)
CMD ["python", "startup.py"]

# ===== Stage 4: 프로덕션 환경 =====
FROM python:3.11-slim AS production

# Firebase Service Account Key 빌드 아규먼트
ARG FIREBASE_SERVICE_ACCOUNT_KEY

# 최소한의 시스템 패키지
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Python 의존성 복사
COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin

# React 빌드 파일 복사
COPY --from=frontend-builder /app/frontend/dist ./static

# 백엔드 코드 복사
COPY backend/ ./

# Firebase Service Account Key 파일 생성 (GitHub Actions에서)
RUN if [ ! -z "$FIREBASE_SERVICE_ACCOUNT_KEY" ]; then \
    mkdir -p ./secrets && \
    echo "$FIREBASE_SERVICE_ACCOUNT_KEY" > ./secrets/firebase-key.json; \
fi

# 비root 사용자 생성
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# 프로덕션 시작 (초기화 포함)
CMD ["python", "startup.py"]
