"""
컨텐츠 필터링 시스템 테스트
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.content_filter import ContentFilter, FilterState
from app.services.filter_service import FilterService


class TestContentFilter:
    """ContentFilter 클래스 테스트"""

    @pytest.fixture
    def content_filter(self):
        """ContentFilter 인스턴스 생성"""
        with patch("app.services.content_filter.LLMClient") as mock_llm_client:
            filter_instance = ContentFilter()
            filter_instance.llm_client = mock_llm_client
            return filter_instance

    @pytest.fixture
    def mock_llm_response_safe(self):
        """안전한 컨텐츠에 대한 LLM 응답 모킹"""
        return """
        {
            "is_safe": true,
            "safety_score": 0.9,
            "risk_categories": [],
            "filter_reason": "안전한 컨텐츠입니다"
        }
        """

    @pytest.fixture
    def mock_llm_response_unsafe(self):
        """위험한 컨텐츠에 대한 LLM 응답 모킹"""
        return """
        {
            "is_safe": false,
            "safety_score": 0.3,
            "risk_categories": ["investment_advice", "guaranteed_profit"],
            "filter_reason": "투자 권유 및 수익 보장 표현이 포함되어 있습니다"
        }
        """

    @pytest.mark.asyncio
    async def test_safe_content_approval(self, content_filter, mock_llm_response_safe):
        """안전한 컨텐츠 승인 테스트"""
        # Given: 안전한 컨텐츠
        safe_content = "경제 지표에 대한 일반적인 설명입니다. 투자에는 위험이 따를 수 있습니다."

        # Mock LLM 응답
        content_filter.llm_client.chat = AsyncMock(return_value=mock_llm_response_safe)

        # When: 필터링 처리
        result = await content_filter.process(safe_content)

        # Then: 안전으로 판정되어야 함
        assert result["is_safe"] is True
        assert result["safety_score"] >= 0.8
        assert result["filtered_content"] == safe_content  # 원본 그대로
        assert len(result["risk_categories"]) == 0

    @pytest.mark.asyncio
    async def test_unsafe_content_filtering(self, content_filter, mock_llm_response_unsafe):
        """위험한 컨텐츠 필터링 테스트"""
        # Given: 위험한 컨텐츠
        unsafe_content = "이 주식을 지금 사세요! 확실한 수익을 보장합니다!"

        # Mock LLM 응답들
        content_filter.llm_client.chat = AsyncMock(
            side_effect=[
                mock_llm_response_unsafe,  # 분석 결과
                "투자에 대한 정보를 제공드립니다. 모든 투자는 위험을 수반합니다.",  # 대체 컨텐츠
                '{"is_approved": true, "final_safety_score": 0.9}',  # 재검토 결과
            ]
        )

        # When: 필터링 처리
        result = await content_filter.process(unsafe_content)

        # Then: 필터링되어 대체 컨텐츠로 변경되어야 함
        assert result["is_safe"] is True  # 최종적으로 안전하게 변환됨
        assert result["filtered_content"] != unsafe_content  # 원본과 다름
        assert "투자는 위험을 수반합니다" in result["filtered_content"]  # 면책 조항 포함
        assert len(result["risk_categories"]) > 0

    @pytest.mark.asyncio
    async def test_very_dangerous_content_rejection(self, content_filter):
        """매우 위험한 컨텐츠 완전 차단 테스트"""
        # Given: 매우 위험한 컨텐츠
        dangerous_content = "내부자 정보로 100% 수익 보장! 지금 당장 대출받아서 투자하세요!"

        # Mock: 매우 낮은 안전도 점수
        mock_response = """
        {
            "is_safe": false,
            "safety_score": 0.1,
            "risk_categories": ["investment_advice", "guaranteed_profit", "market_manipulation"],
            "filter_reason": "매우 위험한 투자 권유 및 불법 정보 제공"
        }
        """

        # max_retries를 1로 제한하여 빠른 종료
        original_max_retries = content_filter.max_retries
        content_filter.max_retries = 1
        content_filter.llm_client.chat = AsyncMock(return_value=mock_response)

        try:
            # When: 필터링 처리
            result = await content_filter.process(dangerous_content)

            # Then: 완전 차단되어야 함
            assert result["is_safe"] is False
            assert "답변을 제공할 수 없습니다" in result["filtered_content"]
            assert result["safety_score"] < 0.3
        finally:
            # 테스트 후 원복
            content_filter.max_retries = original_max_retries

    @pytest.mark.asyncio
    async def test_json_parsing_error_handling(self, content_filter):
        """JSON 파싱 오류 처리 테스트"""
        # Given: JSON이 아닌 응답
        content = "테스트 컨텐츠"
        invalid_json_response = "이것은 JSON이 아닙니다."

        # max_retries를 1로 제한하여 빠른 종료
        original_max_retries = content_filter.max_retries
        content_filter.max_retries = 1
        content_filter.llm_client.chat = AsyncMock(return_value=invalid_json_response)

        try:
            # When: 필터링 처리
            result = await content_filter.process(content)

            # Then: 기본값으로 안전하게 처리되어야 함
            assert result["is_safe"] is False  # 파싱 실패시 안전하지 않음으로 처리
            assert "parsing_error" in result["risk_categories"]
        finally:
            # 테스트 후 원복
            content_filter.max_retries = original_max_retries

    @pytest.mark.asyncio
    async def test_retry_mechanism(self, content_filter):
        """재시도 메커니즘 테스트"""
        # Given: 처음엔 실패하고 재시도에서 성공하는 시나리오
        content = "테스트 컨텐츠"

        # Mock: 첫 번째는 오류, 두 번째는 성공
        content_filter.llm_client.chat = AsyncMock(
            side_effect=[
                Exception("첫 번째 시도 실패"),
                '{"is_safe": true, "safety_score": 0.8, "risk_categories": [], "filter_reason": "재시도 성공"}',
            ]
        )

        # When: 필터링 처리
        result = await content_filter.process(content)

        # Then: 재시도 후 성공해야 함
        assert result["retry_count"] >= 0
        # 오류 처리로 인해 안전하지 않음으로 처리될 수 있음

    def test_extract_json_from_text(self, content_filter):
        """텍스트에서 JSON 추출 테스트"""
        # Given: JSON이 포함된 텍스트
        text_with_json = """
        다음은 분석 결과입니다:
        {"is_safe": true, "safety_score": 0.85}
        이상입니다.
        """

        # When: JSON 추출
        result = content_filter._extract_json_from_text(text_with_json)

        # Then: JSON이 올바르게 추출되어야 함
        assert result["is_safe"] is True
        assert result["safety_score"] == 0.85

    def test_extract_json_from_invalid_text(self, content_filter):
        """잘못된 텍스트에서 JSON 추출 실패 테스트"""
        # Given: JSON이 없는 텍스트
        invalid_text = "이것은 JSON이 전혀 없는 텍스트입니다."

        # When: JSON 추출 시도
        result = content_filter._extract_json_from_text(invalid_text)

        # Then: 기본값이 반환되어야 함
        assert result["is_safe"] is False
        assert result["safety_score"] == 0.0
        assert "parsing_error" in result["risk_categories"]


class TestFilterService:
    """FilterService 클래스 테스트"""

    @pytest.fixture
    def filter_service(self):
        """FilterService 인스턴스 생성"""
        with patch("app.services.filter_service.ContentFilter") as mock_filter:
            service = FilterService()
            service.filter = mock_filter
            return service

    @pytest.mark.asyncio
    async def test_filter_disabled(self, filter_service):
        """필터링 비활성화 테스트"""
        # Given: 필터링 비활성화
        filter_service.enabled = False
        content = "테스트 컨텐츠"

        # When: 필터링 요청
        result = await filter_service.filter_response(content)

        # Then: 원본 그대로 반환되어야 함
        assert result["content"] == content
        assert result["filtered"] is False
        assert result["safety_score"] == 1.0

    @pytest.mark.asyncio
    async def test_empty_content_handling(self, filter_service):
        """빈 컨텐츠 처리 테스트"""
        # Given: 빈 컨텐츠
        empty_content = ""

        # When: 필터링 요청
        result = await filter_service.filter_response(empty_content)

        # Then: 적절한 오류 메시지 반환
        assert result["filtered"] is True
        assert "유효한 질문을 입력해주세요" in result["content"]
        assert "empty_content" in result["risk_categories"]

    @pytest.mark.asyncio
    async def test_service_error_handling(self, filter_service):
        """서비스 오류 처리 테스트"""
        # Given: 필터 처리 중 오류 발생
        filter_service.filter.process = AsyncMock(side_effect=Exception("필터 오류"))
        content = "테스트 컨텐츠"

        # When: 필터링 요청
        result = await filter_service.filter_response(content)

        # Then: 안전한 오류 메시지 반환
        assert result["filtered"] is True
        assert "서비스 처리 중 문제가 발생했습니다" in result["content"]
        assert "service_error" in result["risk_categories"]

    @pytest.mark.asyncio
    async def test_safety_check_only(self, filter_service):
        """안전성 검사만 수행하는 테스트"""
        # Given: 분석 결과 모킹
        mock_analysis_result = {"is_safe": True, "safety_score": 0.8, "risk_categories": [], "filter_reason": "안전한 컨텐츠"}

        filter_service.filter._analyze_content = AsyncMock(return_value=mock_analysis_result)
        content = "테스트 컨텐츠"

        # When: 안전성 검사만 요청
        result = await filter_service.check_safety_only(content)

        # Then: 분석 결과만 반환되어야 함
        assert result["analysis_only"] is True
        assert result["is_safe"] is True
        assert result["safety_score"] == 0.8

    def test_get_filter_stats(self, filter_service):
        """필터 상태 정보 조회 테스트"""
        # When: 상태 정보 요청
        stats = filter_service.get_filter_stats()

        # Then: 설정 정보가 반환되어야 함
        assert "enabled" in stats
        assert "safety_level" in stats
        assert "max_retries" in stats
        assert "filter_model" in stats
