-- 사용자 테이블
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    level VARCHAR(20) NOT NULL, -- 초급/중급/고급
    investment_profile VARCHAR(255),
    exp INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 레벨별 제공 기능 테이블
CREATE TABLE level_feature (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL, -- 초급/중급/고급
    feature_name VARCHAR(100) NOT NULL,
    feature_description TEXT
);

-- 일정 카테고리 테이블
CREATE TABLE event_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- 일정 테이블
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    release_id VARCHAR(50),
    title VARCHAR(255),
    description TEXT,
    date DATE NOT NULL,
    category_id INTEGER REFERENCES event_category(id) ON DELETE SET NULL,
    impact VARCHAR(20),
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 일정-카테고리 매핑 테이블 (다대다 관계용, 필요시)
CREATE TABLE event_category_map (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES event_category(id) ON DELETE CASCADE
);

-- 사용자-일정 구독/캘린더 연동 테이블
CREATE TABLE user_event_subscription (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 구글 캘린더 연동 정보 테이블
CREATE TABLE user_google_calendar (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    google_calendar_id VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_expiry TIMESTAMP
);

-- 이벤트 핸들링용 웹훅 이벤트 테이블
CREATE TABLE event_webhook (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    event_payload JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- 사용자 관심 카테고리 테이블
CREATE TABLE user_interest_category (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES event_category(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 및 제약조건 추가 (필요시)
CREATE INDEX idx_event_date ON events(date);
CREATE INDEX idx_user_event_subscription_user_id ON user_event_subscription(user_id);
CREATE INDEX idx_user_event_subscription_event_id ON user_event_subscription(event_id);
