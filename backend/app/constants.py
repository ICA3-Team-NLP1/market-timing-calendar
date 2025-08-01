from enum import Enum


class UserLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    UNCATEGORIZED = "UNCATEGORIZED"


class ImpactLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class EventStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"


class ChatMessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
