-- 사용자 테이블
CREATE TABLE "users" (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dropped_at TIMESTAMP NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NULL,
    uid VARCHAR(50) UNIQUE NULL,
    name VARCHAR(100) NOT NULL,
    level VARCHAR(20) NOT NULL, -- 초급/중급/고급
    investment_profile VARCHAR(255),
    exp INTEGER DEFAULT 0
);

-- 레벨별 제공 기능 테이블
CREATE TABLE level_feature (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dropped_at TIMESTAMP NULL,
    level VARCHAR(20) NOT NULL, -- 초급/중급/고급
    feature_name VARCHAR(100) NOT NULL,
    feature_description TEXT
);

-- 일정 테이블
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dropped_at TIMESTAMP NULL,
    release_id VARCHAR(50),
    title VARCHAR(255),
    description TEXT,
    date DATE NOT NULL,
    impact VARCHAR(20),
    source VARCHAR(50) NOT NULL
);

-- 사용자-일정 구독/캘린더 연동 테이블
CREATE TABLE user_event_subscription (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dropped_at TIMESTAMP NULL,
    user_id INTEGER NOT NULL REFERENCES "users"(id) ON DELETE CASCADE,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT idx_users_event_subscription UNIQUE (user_id, event_id) -- unique 인덱스 추가
);

-- 구글 캘린더 연동 정보 테이블
CREATE TABLE user_google_calendar (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dropped_at TIMESTAMP NULL,
    user_id INTEGER NOT NULL REFERENCES "users"(id) ON DELETE CASCADE,
    google_calendar_id VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_expiry TIMESTAMP
);

-- 이벤트 핸들링용 웹훅 이벤트 테이블
CREATE TABLE event_webhook (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dropped_at TIMESTAMP NULL,
    event_type VARCHAR(100) NOT NULL,
    event_payload JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    processed_at TIMESTAMP
);

-- 인덱스 및 제약조건 추가 (필요시)
CREATE INDEX idx_event_date ON events(date);
CREATE INDEX idx_user_event_subscription_user_id ON user_event_subscription(user_id);
CREATE INDEX idx_user_event_subscription_event_id ON user_event_subscription(event_id);
