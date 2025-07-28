import { auth } from "../firebase";

// 🔧 더미 모드 설정 (개발자 로그인 시에만 활성화)

// 🔧 더미 데이터 정의
const dummyData = {
    // 사용자 정보
    currentUser: {
        id: 1,
        uid: "dummy_user_123",
        name: "테스트 사용자",
        email: "test@example.com",
        level: "ADVANCED", // BEGINNER, INTERMEDIATE, ADVANCED
        investment_profile: "주식 관심러",
        exp: {
            service_visits: 15,
            chatbot_conversations: 12,
            calendar_views: 25,
        },
        created_at: "2024-01-01T00:00:00",
        updated_at: "2024-01-15T00:00:00",
        dropped_at: null,
        password: null,
    },

    // 사용자 레벨 정보
    userLevelInfo: {
        current_level: "BEGINNER",
        level_display_name: "주린이",
        exp: {
            calendar_views: 1,
            service_visits: 1,
            chatbot_conversations: 1,
        },
        next_level: null,
        next_level_conditions: {},
        can_level_up: false,
        exp_field_info: {
            service_visits: {
                display_name: "서비스 방문",
                current_value: 1,
                required_for_next_level: 10,
            },
            chatbot_conversations: {
                display_name: "챗봇 대화",
                current_value: 1,
                required_for_next_level: 8,
            },
            calendar_views: {
                display_name: "일정 조회",
                current_value: 1,
                required_for_next_level: 15,
            },
        },
    },

    // 레벨 업데이트 응답
    levelUpdateResponse: {
        success: true,
        level_up: false,
        current_level: "INTERMEDIATE",
        exp: {
            service_visits: 16,
            chatbot_conversations: 12,
            calendar_views: 25,
        },
        message: null,
        next_level_conditions: {
            service_visits: 30,
            chatbot_conversations: 20,
            calendar_views: 40,
        },
    },

    // 캘린더 이벤트 (6월, 7월, 8월 데이터)
    calendarEvents: [
        // === 2025년 6월 이벤트 ===
        {
            id: 1,
            release_id: "FOMC_2025_06",
            title: "FOMC 회의 결과 발표",
            description:
                "Federal Open Market Committee regular meeting results announcement",
            description_ko:
                "연방공개시장위원회 정기 회의 결과 발표. 기준금리 결정과 통화정책 방향성이 발표됩니다.",
            date: "2025-06-18",
            impact: "HIGH",
            level: "BEGINNER",
            source: "FED",
            popularity: 9,
            level_category: "MONETARY_POLICY",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },
        {
            id: 2,
            release_id: "NONFARM_2025_06",
            title: "미국 고용 통계 발표",
            description: "US Non-farm Payrolls Report",
            description_ko:
                "미국의 비농업 고용자 수 변화를 발표하는 중요한 경제지표입니다. 노동시장 건강도를 보여줍니다.",
            date: "2025-06-06",
            impact: "HIGH",
            level: "INTERMEDIATE",
            source: "BLS",
            popularity: 8,
            level_category: "EMPLOYMENT",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },
        {
            id: 3,
            release_id: "CPI_2025_06",
            title: "소비자물가지수 발표",
            description: "Consumer Price Index (CPI) Release",
            description_ko:
                "소비자가 구매하는 상품과 서비스의 가격 변화를 측정하는 인플레이션 지표입니다.",
            date: "2025-06-12",
            impact: "MEDIUM",
            level: "BEGINNER",
            source: "BLS",
            popularity: 7,
            level_category: "INFLATION",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },
        {
            id: 4,
            release_id: "ISM_2025_06",
            title: "ISM 제조업 지수 발표",
            description: "Institute for Supply Management Manufacturing Index",
            description_ko:
                "제조업 부문의 경제 활동 수준을 나타내는 지표로, 50 이상이면 확장을 의미합니다.",
            date: "2025-06-02",
            impact: "MEDIUM",
            level: "ADVANCED",
            source: "ISM",
            popularity: 6,
            level_category: "MANUFACTURING",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },

        // === 2025년 7월 이벤트 ===
        {
            id: 5,
            release_id: "FOMC_2025_07",
            title: "FOMC 회의 결과 발표",
            description:
                "Federal Open Market Committee regular meeting results announcement",
            description_ko:
                "연방공개시장위원회 정기 회의 결과 발표. 기준금리 결정과 통화정책 방향성이 발표됩니다.",
            date: "2025-07-15",
            impact: "HIGH",
            level: "BEGINNER",
            source: "FED",
            popularity: 9,
            level_category: "MONETARY_POLICY",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },
        {
            id: 6,
            release_id: "NONFARM_2025_07",
            title: "미국 고용 통계 발표",
            description: "US Non-farm Payrolls Report",
            description_ko:
                "미국의 비농업 고용자 수 변화를 발표하는 중요한 경제지표입니다. 노동시장 건강도를 보여줍니다.",
            date: "2025-07-08",
            impact: "HIGH",
            level: "INTERMEDIATE",
            source: "BLS",
            popularity: 8,
            level_category: "EMPLOYMENT",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },
        {
            id: 7,
            release_id: "CPI_2025_07",
            title: "소비자물가지수 발표",
            description: "Consumer Price Index (CPI) Release",
            description_ko:
                "소비자가 구매하는 상품과 서비스의 가격 변화를 측정하는 인플레이션 지표입니다.",
            date: "2025-07-22",
            impact: "MEDIUM",
            level: "BEGINNER",
            source: "BLS",
            popularity: 7,
            level_category: "INFLATION",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },
        {
            id: 8,
            release_id: "GDP_2025_Q2",
            title: "GDP 성장률 발표",
            description: "Gross Domestic Product Growth Rate",
            description_ko:
                "국가 경제 규모와 성장세를 나타내는 핵심 경제지표입니다. 분기별로 발표됩니다.",
            date: "2025-07-30",
            impact: "HIGH",
            level: "ADVANCED",
            source: "BEA",
            popularity: 6,
            level_category: "ECONOMIC_GROWTH",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },
        {
            id: 9,
            release_id: "RETAIL_2025_07",
            title: "소매판매 발표",
            description: "Retail Sales Report",
            description_ko:
                "소비자 지출 동향을 보여주는 지표로, 경제 활력도를 측정할 수 있습니다.",
            date: "2025-07-03",
            impact: "MEDIUM",
            level: "INTERMEDIATE",
            source: "CENSUS",
            popularity: 5,
            level_category: "CONSUMER_SPENDING",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },
        {
            id: 10,
            release_id: "PPI_2025_07",
            title: "생산자물가지수 발표",
            description: "Producer Price Index (PPI) Release",
            description_ko:
                "생산자가 판매하는 상품의 가격 변화를 측정하여 미래 인플레이션을 예측하는 데 도움이 됩니다.",
            date: "2025-07-12",
            impact: "LOW",
            level: "ADVANCED",
            source: "BLS",
            popularity: 4,
            level_category: "INFLATION",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },

        // === 2025년 8월 이벤트 ===
        {
            id: 11,
            release_id: "JACKSON_HOLE_2025",
            title: "잭슨홀 심포지움",
            description: "Federal Reserve Economic Symposium",
            description_ko:
                "연방준비제도의 연례 경제 심포지움으로, 중앙은행 정책에 대한 중요한 시사점을 제공합니다.",
            date: "2025-08-22",
            impact: "HIGH",
            level: "ADVANCED",
            source: "FED",
            popularity: 9,
            level_category: "MONETARY_POLICY",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },
        {
            id: 12,
            release_id: "NONFARM_2025_08",
            title: "미국 고용 통계 발표",
            description: "US Non-farm Payrolls Report",
            description_ko:
                "미국의 비농업 고용자 수 변화를 발표하는 중요한 경제지표입니다. 노동시장 건강도를 보여줍니다.",
            date: "2025-08-01",
            impact: "HIGH",
            level: "INTERMEDIATE",
            source: "BLS",
            popularity: 8,
            level_category: "EMPLOYMENT",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },
        {
            id: 13,
            release_id: "CPI_2025_08",
            title: "소비자물가지수 발표",
            description: "Consumer Price Index (CPI) Release",
            description_ko:
                "소비자가 구매하는 상품과 서비스의 가격 변화를 측정하는 인플레이션 지표입니다.",
            date: "2025-08-13",
            impact: "MEDIUM",
            level: "BEGINNER",
            source: "BLS",
            popularity: 7,
            level_category: "INFLATION",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },
        {
            id: 14,
            release_id: "RETAIL_2025_08",
            title: "소매판매 발표",
            description: "Retail Sales Report",
            description_ko:
                "소비자 지출 동향을 보여주는 지표로, 경제 활력도를 측정할 수 있습니다.",
            date: "2025-08-15",
            impact: "MEDIUM",
            level: "INTERMEDIATE",
            source: "CENSUS",
            popularity: 6,
            level_category: "CONSUMER_SPENDING",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },
        {
            id: 15,
            release_id: "HOUSING_2025_08",
            title: "주택 착공 건수 발표",
            description: "Housing Starts Report",
            description_ko:
                "새로운 주택 건설 시작 건수를 나타내는 지표로, 부동산 시장과 경제 활동을 보여줍니다.",
            date: "2025-08-20",
            impact: "LOW",
            level: "BEGINNER",
            source: "CENSUS",
            popularity: 5,
            level_category: "HOUSING",
            created_at: "2024-01-01T00:00:00",
            updated_at: "2024-01-01T00:00:00",
            dropped_at: null,
        },
    ],

    // 사용자 구독 목록
    userSubscriptions: [
        {
            id: 1,
            user_id: 1,
            event_id: 1,
            subscribed_at: "2024-01-10T00:00:00",
        },
    ],

    // 이벤트 구독 생성 응답
    createSubscriptionResponse: {
        id: 2,
        user_id: 1,
        event_id: 2,
        subscribed_at: "2024-01-15T00:00:00",
    },

    // 사용자 삭제 응답
    deleteUserResponse: {
        success: true,
        message: "계정이 성공적으로 삭제되었습니다.",
    },
};

// 🔑 API 호출 시 자동으로 Firebase 토큰 포함
export const apiCall = async (url, options = {}) => {
    try {
        // 현재 로그인된 사용자 확인
        const currentUser = auth.currentUser;
        if (!currentUser) {
            throw new Error("로그인이 필요합니다");
        }

        // Firebase ID Token 자동 획득
        const idToken = await currentUser.getIdToken();

        // Authorization 헤더 자동 추가
        const headers = {
            "Content-Type": "application/json",
            Authorization: `Bearer ${idToken}`, // 🔑 토큰 자동 포함
            ...options.headers,
        };

        // API 호출
        const response = await fetch(url, {
            ...options,
            headers,
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        throw error;
    }
};

// 🔧 백엔드 API 기본 URL
const API_BASE_URL = "http://localhost:8000";

// 🔧 보호된 API 호출 함수들 (토큰 자동 포함)
export const getCurrentUser = async () => {
    if (window._replit) {
        return dummyData.currentUser;
    }
    return await apiCall(`${API_BASE_URL}/api/v1/users/me`);
};

export const getUserByUid = async (uid) => {
    if (window._replit) {
        return {
            success: true,
            user: {
                uid: uid,
                email: "test@example.com",
                email_verified: true,
                name: "테스트 사용자",
                picture: "https://via.placeholder.com/150",
            },
        };
    }
    return await apiCall(`${API_BASE_URL}/api/v1/auth/user/${uid}`);
};

// 🔧 사용자 탈퇴 API
export const deleteUser = async () => {
    if (window._replit) {
        return dummyData.deleteUserResponse;
    }
    return await apiCall(`${API_BASE_URL}/api/v1/users/me`, {
        method: "DELETE",
    });
};

// 🔧 사용자 레벨 정보 조회
export const getUserLevelInfo = async () => {
    if (window._replit) {
        return dummyData.userLevelInfo;
    }
    return await apiCall(`${API_BASE_URL}/api/v1/users/level/info`);
};

// 🔧 사용자 레벨 업데이트
export const updateUserLevel = async (eventType) => {
    if (window._replit) {
        // 더미에서는 경험치를 1 증가시켜서 응답
        const response = { ...dummyData.levelUpdateResponse };
        if (response.exp[eventType] !== undefined) {
            response.exp[eventType] += 1;
        }
        return response;
    }
    return await apiCall(`${API_BASE_URL}/api/v1/users/level/update`, {
        method: "PUT",
        body: JSON.stringify({ event_type: eventType }),
    });
};

// 🔧 캘린더 이벤트 조회
export const getCalendarEvents = async (
    startDate,
    endDate,
    userLevel = null,
) => {
    if (window._replit) {
        // 더미 모드에서는 날짜 범위에 맞는 이벤트만 필터링해서 리턴
        const filteredEvents = dummyData.calendarEvents.filter((event) => {
            const eventDate = event.date;
            return eventDate >= startDate && eventDate <= endDate;
        });
        return filteredEvents;
    }
    const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
    });
    //if (userLevel) {
    //    params.append("user_level", userLevel);
    //}
    return await apiCall(
        `${API_BASE_URL}/api/v1/calendar/events/by-level?${params}`,
    );
};

// 🔧 이벤트 구독 생성 (일정 저장)
export const createEventSubscription = async (eventId) => {
    if (window._replit) {
        return {
            ...dummyData.createSubscriptionResponse,
            event_id: eventId,
        };
    }
    return await apiCall(`${API_BASE_URL}/api/v1/calendar/subscriptions`, {
        method: "POST",
        body: JSON.stringify({ event_id: eventId }),
    });
};

// 🔧 사용자 구독 목록 조회
export const getUserSubscriptions = async () => {
    if (window._replit) {
        return dummyData.userSubscriptions;
    }
    return await apiCall(`${API_BASE_URL}/api/v1/calendar/subscriptions`);
};

// 🔧 챗봇 대화 API (스트리밍)
export const chatConversation = async (
    question,
    history = [],
    sessionId = null,
    useMemory = true,
    safetyLevel = "moderate",
) => {
    if (window._replit) {
        // 더미 스트리밍 응답 모의
        const dummyResponse = new Response(
            new ReadableStream({
                start(controller) {
                    const chunks = [
                        'data: {"content": "안녕하세요! "}\n\n',
                        'data: {"content": "질문해 주셔서 감사합니다. "}\n\n',
                        'data: {"content": "더미 모드에서 실행 중입니다."}\n\n',
                        "data: [DONE]\n\n",
                    ];

                    let i = 0;
                    const interval = setInterval(() => {
                        if (i < chunks.length) {
                            controller.enqueue(
                                new TextEncoder().encode(chunks[i]),
                            );
                            i++;
                        } else {
                            clearInterval(interval);
                            controller.close();
                        }
                    }, 100);
                },
            }),
            {
                status: 200,
                headers: { "Content-Type": "text/plain" },
            },
        );
        return dummyResponse;
    }

    const currentUser = auth.currentUser;
    if (!currentUser) {
        throw new Error("로그인이 필요합니다");
    }

    const idToken = await currentUser.getIdToken();

    const params = new URLSearchParams({
        use_filter: 'true',
        use_level_chain: 'true',
        is_mem0_api: 'true',
        chunk_size: '50'
    });

    const response = await fetch(
        `${API_BASE_URL}/api/v1/chatbot/conversation?${params}`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${idToken}`,
            },
            body: JSON.stringify({
                question,
                history,
                session_id: sessionId,
                use_memory: useMemory,
                safety_level: safetyLevel,
            }),
        },
    );

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
    }

    return response; // 스트리밍 응답 반환
};

// 🔧 이벤트 설명 API (스트리밍) - 이미 정의됨
export const explainEvent = async (eventId, safetyLevel = "moderate") => {
    if (window._replit) {
        // 더미 스트리밍 응답 모의
        const dummyResponse = new Response(
            new ReadableStream({
                start(controller) {
                    const chunks = [
                        'data: {"content": "이 이벤트는 "}\n\n',
                        'data: {"content": "경제 지표 발표로 "}\n\n',
                        'data: {"content": "시장에 중요한 영향을 미칠 수 있습니다."}\n\n',
                        "data: [DONE]\n\n",
                    ];

                    let i = 0;
                    const interval = setInterval(() => {
                        if (i < chunks.length) {
                            controller.enqueue(
                                new TextEncoder().encode(chunks[i]),
                            );
                            i++;
                        } else {
                            clearInterval(interval);
                            controller.close();
                        }
                    }, 100);
                },
            }),
            {
                status: 200,
                headers: { "Content-Type": "text/plain" },
            },
        );
        return dummyResponse;
    }

    const currentUser = auth.currentUser;
    if (!currentUser) {
        throw new Error("로그인이 필요합니다");
    }

    const idToken = await currentUser.getIdToken();

    const response = await fetch(
        `${API_BASE_URL}/api/v1/chatbot/event/explain`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${idToken}`,
            },
            body: JSON.stringify({
                id: eventId,
                safety_level: safetyLevel,
            }),
        },
    );

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
    }

    return response; // 스트리밍 응답 반환
};

// 🔧 추천 질문 생성 API
export const generateRecommendQuestion = async (
    eventDescription,
    questionCount = 3,
    stringLength = 15,
    sessionId = null,
) => {
    if (window._replit) {
        // 더미 응답
        return {
            questions: [
                "금리 인하가 왜 중요한가요?",
                "FOMC가 뭐예요?",
                "연준이 뭐예요?",
            ],
            user_level: "BEGINNER",
            total_count: 3,
        };
    }

    return await apiCall(`${API_BASE_URL}/api/v1/chatbot/recommend`, {
        method: "POST",
        body: JSON.stringify({
            event_description: eventDescription,
            question_count: questionCount,
            string_length: stringLength,
            session_id: sessionId,
        }),
    });
};
