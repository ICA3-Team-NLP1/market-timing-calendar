from pydantic import BaseModel


class ChatMessage(BaseModel):
    """채팅 메시지 모델"""

    role: str  # "user" 또는 "assistant"
    content: str  # 메시지 내용


class ConversationRequest(BaseModel):
    """사용자 대화내역 기반 질문 요청

    사용자가 챗봇과 이전에 나눈 대화 내역을 바탕으로
    연속적인 질문을 할 때 사용하는 요청 모델
    """

    history: list[ChatMessage] = []  # 이전 대화 내역
    question: str  # 사용자의 새로운 질문
    safety_level: str = None  # 필터링 안전 수준 (선택사항)


class EventExplainRequest(BaseModel):
    """특정 이벤트(금융일정)에 대한 설명 요청

    특정 금융 이벤트나 경제 지표에 대한 설명을 요청할 때 사용하는 모델
    대화 내역 없이 단발성 질문으로 사용됨
    """

    release_id: str  # Events 테이블의 release_id (예: CPILFESL, UNRATE 등)
    safety_level: str = None  # 필터링 안전 수준 (선택사항)


class SafetyCheckRequest(BaseModel):
    """컨텐츠 안전성 검사 요청"""

    content: str  # 검사할 컨텐츠
