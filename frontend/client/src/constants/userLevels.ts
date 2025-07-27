export const DEFAULT_USER_LEVEL = "INTERMEDIATE";
export const DEFAULT_LEVEL_DISPLAY_NAME = "관심러";

export const LEVEL_DISPLAY_NAMES = {
  BEGINNER: "주린이",
  INTERMEDIATE: "관심러",
  ADVANCED: "전문가"
} as const;

export const PROGRESS_FIELD_ORDER = [
  "service_visits",
  "chatbot_conversations", 
  "calendar_views"
] as const;