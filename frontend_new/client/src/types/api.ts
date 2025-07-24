
export interface User {
    uid: string;
    email: string;
    email_verified: boolean;
    name?: string;
    picture?: string;
}

export interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    message?: string;
    error?: string;
}

export interface UserLevelInfo {
    current_level: string;
    exp: Record<string, number>;
    next_level_conditions?: Record<string, number>;
}

export interface CalendarEvent {
    id: number;
    release_id: string;
    title: string;
    description: string;
    date: string;
    impact: string;
    level: string;
    popularity: number;
    description_ko?: string;
    level_category?: string;
}

export interface EventSubscription {
    id: number;
    event_id: number;
    user_id: number;
    subscribed_at: string;
    event: CalendarEvent;
}

export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
}

export interface LevelUpdateRequest {
    event_type: string;
}

export interface LevelUpdateResponse {
    success: boolean;
    level_up: boolean;
    current_level: string;
    exp: Record<string, number>;
    message?: string;
    next_level_conditions?: Record<string, number>;
}
