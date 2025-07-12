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
│   └── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

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

## 📝 라이선스

Apache 2.0 License

---

## 👥 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
