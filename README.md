# 📅 Market Timing Calendar

초보 투자자를 위한 경제일정 캘린더 서비스 - AI 챗봇과 함께하는 스마트 투자 가이드

---

## 📸 화면

### 메인 대시보드
<!-- 스크린샷 추가 예정 -->
![메인 대시보드](./docs/images/main-dashboard.png)

### 경제일정 상세
<!-- 스크린샷 추가 예정 -->
![경제일정 상세](./docs/images/event-detail.png)

### AI 챗봇 인터페이스
<!-- 스크린샷 추가 예정 -->
![AI 챗봇](./docs/images/chatbot.png)

---

## 🚀 설치 및 실행방법

### 필수 요구사항

- Docker & Docker Compose
- Git
- Firebase 프로젝트 (인증용)

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd market-timing-calendar
```

### 2. 환경 설정

```bash
# 백엔드 환경변수 설정
cp backend/.env.example backend/.env
# .env 파일을 열어서 필요한 값들을 설정하세요
```

### 3. Firebase 프로젝트 설정 (필수)

🔥 **중요: Firebase 서비스 계정 키는 각자 설정해야 합니다!**

#### 3.1 Firebase 프로젝트 생성
1. [Firebase Console](https://console.firebase.google.com/)에 접속
2. **새 프로젝트 생성** 또는 기존 프로젝트 선택
3. 프로젝트 이름: `market-timing-calendar` (또는 원하는 이름)

#### 3.2 Firebase Authentication 설정
1. Firebase Console → **Authentication** 메뉴
2. **로그인 방법** 탭 클릭
3. **Google** 로그인 방법 활성화
4. **이메일/비밀번호** 로그인 방법 활성화 (선택사항)

#### 3.3 Firebase 서비스 계정 키 생성 및 설정
🔐 **이 단계는 각 개발자가 개별적으로 수행해야 합니다!**

1. **서비스 계정 키 다운로드**:
   ```
   Firebase Console → 프로젝트 설정 → 서비스 계정 → "새 비공개 키 생성"
   ```

2. **JSON 파일 다운로드** 후 다음 위치에 저장:
   ```bash
   # 정확한 경로와 파일명으로 저장
   backend/secrets/firebase-key.json
   ```

3. **보안 확인**:
   ```bash
   # .gitignore에 이미 포함되어 있는지 확인
   cat .gitignore | grep secrets
   # 결과: /backend/secrets/
   ```

#### 🚨 **중요 보안 사항**
- ✅ `backend/secrets/` 폴더는 **gitignore**에 포함되어 있음
- ⚠️ **절대 firebase-key.json을 Git에 커밋하지 마세요!**

#### 3.4 프론트엔드 Firebase 설정
1. **웹 앱 추가**:
   ```
   Firebase Console → 프로젝트 설정 → 일반 → 내 앱 → 웹 앱 추가
   ```

2. **설정 정보 복사** 후 docker-compose.yml에 반영:
   ```yaml
   # docker-compose.yml에서 다음 값들 수정
   - VITE_FIREBASE_API_KEY=your-api-key
   - VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   - VITE_FIREBASE_PROJECT_ID=your-project-id
   # ... 기타 설정값들
   ```

### 4. Docker로 실행

```bash
# 빌드 및 실행
sudo docker-compose up --build -d

# 로그 확인
sudo docker-compose logs -f
```

### 5. 접속

- **메인 애플리케이션**: http://localhost:8000
- **API 문서**: http://localhost:8000/api/docs
- **헬스체크**: http://localhost:8000/api/health

### 5. 종료

```bash
sudo docker-compose down
```

---

## 🛠 개발 환경 설정

### 로컬 개발 (선택사항)

#### Frontend 개발

```bash
cd frontend
npm install
npm run dev
# http://localhost:5173
```

#### Backend 개발

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd app
python main.py
# http://localhost:8000
```

---

## 📁 프로젝트 구조

```
market-timing-calendar/
├── frontend/              # React + Vite
│   ├── src/
│   │   ├── components/    # 재사용 가능한 컴포넌트
│   │   ├── firebase.js    # Firebase 설정
│   │   └── App.jsx
│   ├── public/
│   └── package.json
├── database/
├── backend/               # FastAPI
│   ├── app/
│   │   ├── main.py        # 메인 애플리케이션
│   │   ├── constants.py   # 주요 상수
│   │   ├── api/           # API 라우터
│   │   ├── core/          # 핵심 설정
│   │   │   ├── config.py  # 환경 설정
│   │   │   └── firebase.py # Firebase Auth
│   │   ├── crud/          # CRUD 작업
│   │   ├── models/        # SQLAlchemy 모델
│   │   ├── schemas/       # Pydantic 스키마
│   │   └── utils/         # 유틸 함수
│   ├── secrets            # 보안 관련 로컬 파일(gitignore)
│   ├── tests              # pytest 코드
│   └── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

---

## 🧪 테스트 실행

### 자동 테스트 스크립트 사용 (권장)

```bash
# 테스트 스크립트 실행 - 모든 것을 자동으로 처리
./run-tests.sh
```

### 수동 테스트 실행

#### 1. 서비스 시작
```bash
# 필요한 서비스들 시작 (PostgreSQL 포함)
docker-compose up -d app postgres
```

#### 2. 테스트 실행
```bash
# 모든 테스트 실행
docker-compose exec app bash -c "
    export DATABASE_URL=\$TEST_DATABASE_URL
    python -m pytest backend/tests/ -v
"

# 특정 테스트 파일만 실행
docker-compose exec app bash -c "
    export DATABASE_URL=\$TEST_DATABASE_URL
    python -m pytest backend/tests/api/test_users_api.py -v
"

# 패턴 매칭으로 테스트 실행
docker-compose exec app bash -c "
    export DATABASE_URL=\$TEST_DATABASE_URL
    python -m pytest backend/tests/ -k 'user' -v
"
```

#### 3. 테스트 결과 확인
```bash
# 상세한 실행 결과를 보려면
docker-compose exec app bash -c "
    export DATABASE_URL=\$TEST_DATABASE_URL
    python -m pytest backend/tests/ -v --tb=long --cov=app
"
```

### 테스트 환경 정보

#### 데이터베이스 구조
- **개발용 DB**: `market_timing` (포트 5432)
- **테스트용 DB**: `market_timing_test` (포트 5432)
- **단일 PostgreSQL 인스턴스**에서 두 데이터베이스 분리 운영

---

## 🔧 주요 기능

- 📅 경제일정 캘린더
- 🤖 AI 챗봇 상담
- 📊 사용자 레벨별 큐레이션
- 🔗 Google Calendar 연동
- 📧 이메일 알림

---

## 🐛 문제 해결

### 자주 발생하는 문제

**Docker 빌드 실패 시:**
```bash
sudo docker system prune -a
sudo docker-compose build --no-cache
```

**포트 충돌 시:**
```bash
sudo docker-compose down
sudo lsof -i :8000
```

**권한 문제 시:**
```bash
sudo chown -R $USER:$USER .
```

**01-init.sql로 DB 업데이트 후 스키마가 반영되지 않을 시:**
```bash
sudo docker-compose down -v
sudo docker-compose up -d
```

---

## 🛡️ 컨텐츠 필터링 시스템

### 개요

본 프로젝트는 **LangGraph 기반의 고도화된 컨텐츠 필터링 시스템**을 통해 금융 법적 가이드라인을 준수하고 사용자에게 안전한 정보를 제공합니다.

### 🏗️ 아키텍처

```
사용자 요청 → 챗봇 API → LLM 응답 생성 → 필터링 시스템 → 안전한 응답 반환
                                    ↓
                          [LangGraph Workflow]
                          1. 컨텐츠 분석
                          2. 안전성 평가  
                          3. 필터링 적용
                          4. 대체 컨텐츠 생성
                          5. 재검토 및 승인
```

### 🔧 핵심 기능

#### 1. **다단계 필터링 Workflow**
- **분석**: LLM을 통한 컨텐츠 위험도 분석
- **필터링**: 안전도 점수 기반 자동 필터링
- **대체**: 위험한 컨텐츠의 안전한 대체 텍스트 생성
- **재검토**: 대체된 컨텐츠의 최종 안전성 검증

#### 2. **법적 가이드라인 준수**
- 투자 권유 표현 탐지 및 차단
- 과도한 수익 보장 표현 필터링
- 리스크 경고 누락 감지
- 미확인 정보 제공 방지
- 법적 면책 조항 자동 추가

#### 3. **안전 수준별 설정**
- **Strict**: 금융기관 수준의 엄격한 필터링 (임계값: 0.85)
- **Moderate**: 일반적인 수준의 필터링 (임계값: 0.70)  
- **Permissive**: 최소한의 필터링 (임계값: 0.55)

### 📊 모니터링 및 로깅

#### 실시간 메트릭
```bash
# 필터링 상태 조회
curl -X GET "http://localhost:8000/api/v1/chatbot/filter/status" \
  -H "Authorization: Bearer your-token"
```

#### 로깅 정보
- 📈 **성능 메트릭**: 처리 시간, 처리량, 성공률
- 🔍 **필터링 결과**: 안전도 점수, 위험 카테고리, 필터링 이유
- ⚠️ **위험 탐지**: 투자 권유, 수익 보장, 시장 조작 우려 등
- 📊 **사용자 패턴**: 사용자별 필터링 빈도 및 패턴

### 🚀 API 사용법

#### 1. **기본 대화 (필터링 적용)**
```bash
curl -X POST "http://localhost:8000/api/v1/chatbot/conversation?use_filter=true" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "history": [],
    "question": "투자에 대해 알려주세요",
    "safety_level": "strict"
  }'
```

#### 2. **필터링 없는 대화**
```bash
curl -X POST "http://localhost:8000/api/v1/chatbot/conversation?use_filter=false" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "history": [],
    "question": "경제 상황을 알려주세요"
  }'
```

#### 3. **상세 필터링 정보와 함께 대화**
```bash
curl -X POST "http://localhost:8000/api/v1/chatbot/conversation?use_filter=true" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "history": [],
    "question": "이 주식을 사야 할까요?",
    "safety_level": "moderate"
  }'
```

**응답 예시**:
```json
{
  "content": "투자에 대한 참고 정보를 제공해드립니다...",
  "filter_result": {
    "filtered": true,
    "safety_score": 0.65,
    "filter_reason": "투자 권유 표현이 포함되어 수정했습니다",
    "risk_categories": ["investment_advice"],
    "processing_time": 1.2,
    "retry_count": 1
  }
}
```

#### 4. **컨텐츠 안전성 검사**
```bash
curl -X POST "http://localhost:8000/api/v1/chatbot/safety/check" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "content": "이 주식을 지금 사세요! 100% 수익 보장!"
  }'
```

### ⚙️ 환경변수 설정

```bash
# 필터링 기본 설정
FILTER_ENABLED=true
FILTER_SAFETY_LEVEL=strict
FILTER_MAX_RETRIES=3

# 필터링 전용 LLM 설정
FILTER_LLM_PROVIDER=openai
FILTER_LLM_MODEL=gpt-4
```

### 🧪 테스트 실행

#### 필터링 시스템 테스트
```bash
# 컨텐츠 필터 테스트
docker-compose exec app python -m pytest backend/tests/services/test_content_filter.py -v

# API 통합 테스트
docker-compose exec app python -m pytest backend/tests/api/test_chatbot_with_filter.py -v

# 성능 테스트
docker-compose exec app python -m pytest backend/tests/performance/test_filter_performance.py -v
```

### 🔍 위험 카테고리

| 카테고리 | 설명 | 예시 |
|---------|------|------|
| `investment_advice` | 투자 권유 | "사세요", "팔아야 합니다" |
| `guaranteed_profit` | 수익 보장 | "확실한 수익", "100% 상승" |
| `missing_risk_warning` | 리스크 경고 누락 | 위험성 언급 없는 투자 조언 |
| `unverified_information` | 미확인 정보 | 출처 불분명한 시장 정보 |
| `market_manipulation` | 시장 조작 우려 | 내부자 정보, 조작 의혹 |
| `excessive_confidence` | 과도한 확신 | "무조건", "반드시" 등 |

### 📈 성능 최적화

#### 1. **병렬 처리**
- 동시 요청 처리 지원
- 비동기 LLM 호출로 처리량 향상

#### 2. **캐싱 전략**
- 유사한 컨텐츠에 대한 필터링 결과 캐싱 (추후 구현 예정)
- LLM 응답 캐싱으로 반복 요청 최적화

#### 3. **모니터링**
- 실시간 성능 메트릭 수집
- Langfuse를 통한 LLM 호출 추적
- 사용자별 필터링 패턴 분석

### 🚨 알려진 제한사항

1. **처리 지연**: 복잡한 컨텐츠의 경우 3-5초 소요 가능
2. **언어 제한**: 현재 한국어에 최적화됨
3. **컨텍스트 길이**: 매우 긴 텍스트의 경우 청킹 필요
4. **비용**: LLM API 호출로 인한 추가 비용 발생

### 🛠️ 커스터마이징

#### 필터링 프롬프트 수정
```python
# backend/app/core/filter_prompts.py
SAFETY_ANALYSIS_PROMPT = """
당신은 금융 조언 컨텐츠의 안전성을 평가하는 전문가입니다.
... 사용자 정의 프롬프트 ...
"""
```

#### 안전 임계값 조정
```python
# backend/app/core/filter_prompts.py
SAFETY_THRESHOLDS = {
    "strict": 0.90,    # 더 엄격하게
    "moderate": 0.75,  # 기본값 조정
    "permissive": 0.60 # 더 관대하게
}
```

---

## 📝 라이선스

Apache 2.0 License

---

## 👥 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
