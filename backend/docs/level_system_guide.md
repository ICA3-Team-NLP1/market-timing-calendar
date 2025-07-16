# JSON 기반 레벨 시스템 가이드

## 개요

이 레벨 시스템은 JSON 파일 기반으로 구성되어 있어서, 경험치 항목과 레벨업 조건을 쉽게 변경할 수 있습니다.

## 설정 변경 방법

### 1. 경험치 항목 추가/제거

`backend/app/core/level_config.json`의 `exp_fields`를 수정합니다:

```json
{
  "exp_fields": {
    "service_visits": "서비스 방문",
    "chatbot_conversations": "챗봇 대화", 
    "calendar_views": "일정 조회",
    "event_participation_score": "이벤트 참여 점수 (예시)",
    "quiz_score": "퀴즈 점수 (예시)",
    "investment_simulation_count": "투자 시뮬레이션 참여 (예시)",
    "article_reading_count": "아티클 읽기 (예시)"
  }
}
```

### 2. 레벨업 조건 변경

`level_up_conditions`를 수정합니다:

```json
{
  "level_up_conditions": {
    "BEGINNER": {
      "target_level": "INTERMEDIATE",
      "conditions": {
        "service_visits": 15,
        "chatbot_conversations": 10,
        "calendar_views": 20,
        "quiz_score": 50
      }
    },
    "INTERMEDIATE": {
      "target_level": "ADVANCED",
      "conditions": {
        "service_visits": 50,
        "chatbot_conversations": 30,
        "calendar_views": 100,
        "quiz_score": 200,
        "event_participation_score": 100
      }
    }
  }
}
```

## 현재 활성화된 경험치 항목

현재 시스템에서 실제로 사용 중인 경험치 항목:
- `service_visits`: 서비스 방문
- `chatbot_conversations`: 챗봇 대화  
- `calendar_views`: 일정 조회

## 데이터 마이그레이션

JSON 설정을 변경한 후 다음 명령으로 기존 사용자 데이터를 마이그레이션합니다:

### 1. 현재 설정 확인
```bash
cd backend
python -m app.utils.migration_utils config
```

### 2. 데이터 검증
```bash
python -m app.utils.migration_utils validate
```

### 3. 마이그레이션 실행
```bash
python -m app.utils.migration_utils migrate
```

### 4. 모든 경험치 초기화 (필요시)
```bash
python -m app.utils.migration_utils reset
```

## API 사용법

### 1. 사용 가능한 경험치 필드 조회
```http
GET /api/v1/users/level/fields
```

응답:
```json
{
  "exp_fields": {
    "service_visits": "서비스 방문",
    "chatbot_conversations": "챗봇 대화",
    "calendar_views": "일정 조회"
  },
  "field_names": ["service_visits", "chatbot_conversations", "calendar_views"],
  "level_conditions": {...}
}
```

### 2. 사용자 레벨 정보 조회
```http
GET /api/v1/users/level/info
```

응답:
```json
{
  "current_level": "BEGINNER",
  "level_display_name": "주린이",
  "exp": {
    "service_visits": 5,
    "chatbot_conversations": 3,
    "calendar_views": 8
  },
  "next_level": "INTERMEDIATE",
  "next_level_conditions": {
    "service_visits": 10,
    "chatbot_conversations": 8,
    "calendar_views": 15
  },
  "can_level_up": false
}
```

### 3. 경험치 업데이트
```http
PUT /api/v1/users/level/update
```

요청 (현재 사용 가능한 이벤트 타입):
```json
{
  "event_type": "service_visits"
}
```

응답:
```json
{
  "success": true,
  "level_up": true,
  "current_level": "INTERMEDIATE",
  "exp": {
    "service_visits": 0,
    "chatbot_conversations": 0,
    "calendar_views": 0
  },
  "message": "축하합니다! 관심러 레벨로 승급하셨습니다!",
  "next_level_conditions": {
    "service_visits": 30,
    "chatbot_conversations": 20,
    "calendar_views": 40
  }
}
```

## 프론트엔드 연동 예시

### 동적 이벤트 처리
```javascript
// 사용 가능한 이벤트 타입 조회
const getAvailableEventTypes = async () => {
  const response = await fetch('/api/v1/users/level/fields');
  const data = await response.json();
  return data.field_names;
};

// 동적 이벤트 업데이트
const updateUserLevel = async (eventType) => {
  // 유효한 이벤트 타입인지 확인
  const availableTypes = await getAvailableEventTypes();
  if (!availableTypes.includes(eventType)) {
    console.error(`Invalid event type: ${eventType}`);
    return;
  }
  
  const response = await fetch('/api/v1/users/level/update', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ event_type: eventType })
  });
  
  const data = await response.json();
  
  if (data.level_up) {
    showLevelUpNotification(data.message);
    refreshUserMenu();
  }
};

// 현재 사용 가능한 이벤트 타입
updateUserLevel('service_visits');
updateUserLevel('chatbot_conversations');
updateUserLevel('calendar_views');

// 미래 확장 예시 (아직 사용 불가)
// updateUserLevel('quiz_score');
// updateUserLevel('event_participation_score');
```

## 확장 시나리오 예시

### 시나리오 1: 퀴즈 시스템 추가 (예시)
1. `level_config.json`의 `exp_fields`에 `"quiz_score": "퀴즈 점수"` 추가
2. 레벨업 조건에 퀴즈 점수 조건 추가
3. 서버 재시작 (자동 적용)
4. 퀴즈 완료 시 `updateUserLevel('quiz_score')` 호출

### 시나리오 2: 이벤트 참여 시스템 추가 (예시)
1. `level_config.json`의 `exp_fields`에 `"event_participation_score": "이벤트 참여 점수"` 추가
2. 레벨업 조건 업데이트
3. 서버 재시작
4. 이벤트 참여 시 `updateUserLevel('event_participation_score')` 호출

### 시나리오 3: 기존 조건 변경
1. `level_config.json`의 `level_up_conditions`에서 필요한 조건 수정
2. 서버 재시작 (새로운 조건으로 자동 적용)

## 주의사항

1. **JSON 파일 수정 후 서버 재시작**: JSON 설정을 변경한 후에는 서버를 재시작해야 새로운 설정이 적용됩니다.

2. **기존 사용자 데이터**: 새로운 경험치 필드가 추가되면 API 호출 시 자동으로 해당 필드가 사용자 exp에 추가됩니다.

3. **점진적 배포**: 레벨업 조건을 크게 변경할 때는 사용자에게 사전 공지를 하고 점진적으로 적용하는 것이 좋습니다.

4. **설정 검증**: JSON 파일 형식을 올바르게 유지해야 합니다:
   ```bash
   cd backend
   python -c "import json; print(json.load(open('app/core/level_config.json')))"
   ``` 