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

### 3. Docker로 실행

```bash
# 빌드 및 실행
sudo docker-compose up --build -d

# 로그 확인
sudo docker-compose logs -f
```

### 4. 접속

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
│   ├── public/
│   └── package.json
├── backend/               # FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── models/
│   │   └── services/
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
