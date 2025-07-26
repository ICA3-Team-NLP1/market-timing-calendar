# 🚀 GitHub Actions 배포 설정 가이드

## ✅ 파일 생성 완료!

다음 파일들이 생성되었습니다:
- `.github/workflows/deploy.yml` - GitHub Actions 워크플로우
- `task-definition-main.json` - 메인 앱 ECS 태스크 정의
- `task-definition-background.json` - 백그라운드 워커 ECS 태스크 정의

## 🔐 GitHub Secrets 설정 (필수)

GitHub Repository → Settings → Secrets and variables → Actions에서 다음 시크릿들을 추가하세요:

### AWS 인증 (필수)
- `AWS_ACCESS_KEY_ID`: AKIA...
- `AWS_SECRET_ACCESS_KEY`: ...

### Firebase 빌드용 (필수)
- `VITE_FIREBASE_API_KEY`: AIzaSyCaYBhQEGujz-oj-j2mvaSNHFlVnzrGztA
- `VITE_FIREBASE_AUTH_DOMAIN`: market-timing-calendar.firebaseapp.com
- `VITE_FIREBASE_PROJECT_ID`: market-timing-calendar
- `VITE_FIREBASE_STORAGE_BUCKET`: market-timing-calendar.firebasestorage.app
- `VITE_FIREBASE_MESSAGING_SENDER_ID`: 539122761808
- `VITE_FIREBASE_APP_ID`: 1:539122761808:web:016249bad69b51190d1155
- `VITE_FIREBASE_MEASUREMENT_ID`: G-5LPG8SK2EK

## 🚀 배포 방법

1. 위의 GitHub Secrets 설정
2. 코드를 main 브랜치에 push
3. GitHub Actions 자동 실행
4. 배포 완료!

## 🔍 배포 후 확인

배포가 완료되면:
- GitHub Actions 탭에서 배포 상태 확인
- AWS ECS 콘솔에서 서비스 상태 확인
- 실행 중인 태스크의 퍼블릭 IP로 웹사이트 접속

## ⚠️ 주의사항

- Firebase OAuth 설정은 나중에 실제 도메인으로 업데이트 필요
- /health 엔드포인트가 구현되어 있는지 확인 필요
- 첫 배포 시 이미지 빌드로 10-15분 소요 예상