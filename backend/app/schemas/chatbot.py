from pydantic import BaseModel, constr


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
    safety_level: str | None = None  # 필터링 안전 수준 (선택사항)
    session_id: str | None = None  # 세션 ID (새로운 대화면 None)
    use_memory: bool = True  # mem0 메모리 사용 여부


class EventExplainRequest(BaseModel):
    """특정 이벤트(금융일정)에 대한 설명 요청

    특정 금융 이벤트나 경제 지표에 대한 설명을 요청할 때 사용하는 모델
    대화 내역 없이 단발성 질문으로 사용됨
    Events 테이블의 id를 사용하여 이벤트를 조회합니다.
    """

    id: int  # Events 테이블의 id (예: 1, 2, 3 등)
    safety_level: str | None = None  # 필터링 안전 수준 (선택사항)


class SafetyCheckRequest(BaseModel):
    """컨텐츠 안전성 검사 요청"""

    content: str  # 검사할 컨텐츠


class RecommendQuestionRequest(BaseModel):
    """추천 질문 생성 요청"""

    event_description: constr(max_length=30)  # 이벤트 설명 (30자 이내)
    question_count: int = 3  # 생성할 질문 개수 (기본값: 3)
    string_length: int = 15  # 질문 길이 제한 (기본값: 15자)
    session_id: str | None = None  # 세션 ID (새로운 대화면 None)


class RecommendQuestionResponse(BaseModel):
    """추천 질문 생성 응답"""

    questions: list[str]  # 생성된 추천 질문 목록
    user_level: str  # 사용자 레벨
    total_count: int  # 생성된 질문 개수
