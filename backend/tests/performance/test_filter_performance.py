"""
필터링 시스템 성능 테스트
"""
import pytest
import time
import asyncio
from unittest.mock import AsyncMock, patch
from concurrent.futures import ThreadPoolExecutor

from app.services.content_filter import ContentFilter
from app.services.filter_service import FilterService


class TestFilterPerformance:
    """필터링 시스템 성능 테스트"""

    @pytest.fixture
    def mock_filter_service(self):
        """성능 테스트용 FilterService 모킹"""
        with patch("app.services.filter_service.ContentFilter") as mock_filter:
            service = FilterService()
            service.filter = mock_filter

            # 빠른 응답을 위한 mock 설정
            mock_filter.process = AsyncMock(
                return_value={
                    "is_safe": True,
                    "safety_score": 0.8,
                    "filtered_content": "안전한 테스트 응답입니다.",
                    "filter_reason": "",
                    "risk_categories": [],
                    "retry_count": 0,
                }
            )

            return service

    @pytest.mark.asyncio
    async def test_filter_latency(self, mock_filter_service):
        """필터링 지연시간 테스트"""
        # Given: 테스트 컨텐츠
        test_content = "경제 지표에 대한 일반적인 설명입니다."

        # When: 필터링 시간 측정
        start_time = time.time()
        result = await mock_filter_service.filter_response(test_content)
        end_time = time.time()

        latency = end_time - start_time

        # Then: 지연시간 검증
        assert latency < 0.1  # 100ms 이하여야 함 (모킹된 상태)
        assert result["processing_time"] >= 0

        print(f"📊 필터링 지연시간: {latency:.3f}초")

    @pytest.mark.asyncio
    async def test_concurrent_filtering(self, mock_filter_service):
        """동시 필터링 처리 성능 테스트"""
        # Given: 다양한 테스트 컨텐츠들
        test_contents = ["경제 지표 설명 1", "투자 정보 제공 2", "시장 분석 내용 3", "금융 데이터 해석 4", "경제 동향 분석 5"]

        # When: 동시 필터링 처리
        start_time = time.time()

        tasks = [mock_filter_service.filter_response(content) for content in test_contents]
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # Then: 성능 검증
        assert len(results) == len(test_contents)
        assert all(result["content"] for result in results)
        assert total_time < 0.5  # 500ms 이하 (모킹된 상태)

        avg_time_per_request = total_time / len(test_contents)
        print(f"📊 동시 처리 성능: {len(test_contents)}개 요청, 총 {total_time:.3f}초")
        print(f"📊 요청당 평균 시간: {avg_time_per_request:.3f}초")

    @pytest.mark.asyncio
    async def test_memory_usage_simulation(self, mock_filter_service):
        """메모리 사용량 시뮬레이션 테스트"""
        # Given: 다양한 크기의 컨텐츠
        small_content = "짧은 내용"
        medium_content = "중간 길이의 컨텐츠 " * 50  # ~1KB
        large_content = "긴 컨텐츠 " * 1000  # ~10KB

        test_cases = [("small", small_content), ("medium", medium_content), ("large", large_content)]

        # When: 각 크기별 처리 시간 측정
        performance_results = {}

        for size_name, content in test_cases:
            start_time = time.time()
            result = await mock_filter_service.filter_response(content)
            processing_time = time.time() - start_time

            performance_results[size_name] = {
                "content_size": len(content),
                "processing_time": processing_time,
                "success": result["filtered"] is not None,
            }

        # Then: 결과 검증 및 출력
        for size_name, metrics in performance_results.items():
            assert metrics["success"] is True
            print(f"📊 {size_name} 컨텐츠 ({metrics['content_size']}B): {metrics['processing_time']:.3f}초")

    @pytest.mark.asyncio
    async def test_error_recovery_performance(self, mock_filter_service):
        """오류 복구 성능 테스트"""
        # Given: 실패 후 성공하는 시나리오
        mock_filter_service.filter.process = AsyncMock(
            side_effect=[
                Exception("첫 번째 실패"),
                Exception("두 번째 실패"),
                {  # 세 번째에 성공
                    "is_safe": True,
                    "safety_score": 0.8,
                    "filtered_content": "복구된 응답",
                    "filter_reason": "",
                    "risk_categories": [],
                    "retry_count": 2,
                },
            ]
        )

        # When: 오류 복구 시간 측정
        start_time = time.time()
        result = await mock_filter_service.filter_response("테스트 컨텐츠")
        recovery_time = time.time() - start_time

        # Then: 복구 성능 검증
        assert "서비스 처리 중 문제가 발생했습니다" in result["content"]  # 오류 처리됨
        assert recovery_time < 1.0  # 1초 이내 복구

        print(f"📊 오류 복구 시간: {recovery_time:.3f}초")

    @pytest.mark.asyncio
    async def test_scaling_performance(self, mock_filter_service):
        """확장성 성능 테스트"""
        # Given: 점진적으로 증가하는 부하
        load_levels = [1, 5, 10, 20]
        performance_data = []

        for num_concurrent in load_levels:
            # When: 동시 요청 수를 늘려가며 테스트
            start_time = time.time()

            tasks = [mock_filter_service.filter_response(f"테스트 컨텐츠 {i}") for i in range(num_concurrent)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            total_time = time.time() - start_time

            # 성공한 요청 수 계산
            successful_results = [r for r in results if not isinstance(r, Exception)]
            success_rate = len(successful_results) / num_concurrent
            throughput = num_concurrent / total_time

            performance_data.append(
                {
                    "concurrent_requests": num_concurrent,
                    "total_time": total_time,
                    "success_rate": success_rate,
                    "throughput": throughput,
                }
            )

        # Then: 확장성 검증
        for data in performance_data:
            assert data["success_rate"] >= 0.9  # 90% 이상 성공률
            print(
                f"📊 동시 요청 {data['concurrent_requests']}개: "
                f"{data['throughput']:.1f} req/sec, "
                f"성공률 {data['success_rate']:.1%}"
            )

        # 처리량이 급격히 떨어지지 않는지 확인
        first_throughput = performance_data[0]["throughput"]
        last_throughput = performance_data[-1]["throughput"]
        degradation_ratio = last_throughput / first_throughput

        assert degradation_ratio > 0.5  # 처리량이 50% 이하로 떨어지지 않음
        print(f"📊 확장성 지수: {degradation_ratio:.2f} (1.0이 이상적)")


class TestRealWorldScenarios:
    """실제 사용 시나리오 성능 테스트"""

    @pytest.mark.asyncio
    async def test_typical_conversation_performance(self):
        """일반적인 대화 시나리오 성능 테스트"""
        # Given: 실제 대화 시나리오
        conversation_turns = [
            "안녕하세요. 경제 상황에 대해 궁금합니다.",
            "현재 인플레이션 상황은 어떤가요?",
            "투자할 때 주의해야 할 점은 무엇인가요?",
            "금리 인상이 주식 시장에 미치는 영향은?",
            "감사합니다. 많은 도움이 되었습니다.",
        ]

        with patch("app.services.filter_service.ContentFilter") as mock_filter:
            filter_service = FilterService()
            filter_service.filter = mock_filter

            # 각 턴별로 다른 응답 시간 시뮬레이션
            mock_filter.process = AsyncMock(
                side_effect=[
                    {
                        "is_safe": True,
                        "safety_score": 0.9,
                        "filtered_content": f"안전한 응답 {i}",
                        "filter_reason": "",
                        "risk_categories": [],
                        "retry_count": 0,
                    }
                    for i in range(len(conversation_turns))
                ]
            )

            # When: 대화 시뮬레이션
            conversation_start = time.time()
            results = []

            for turn in conversation_turns:
                turn_start = time.time()
                result = await filter_service.filter_response(turn)
                turn_time = time.time() - turn_start

                results.append({"turn": turn, "result": result, "turn_time": turn_time})

            total_conversation_time = time.time() - conversation_start

            # Then: 대화 성능 검증
            assert len(results) == len(conversation_turns)
            assert all(r["result"]["content"] for r in results)
            assert total_conversation_time < 5.0  # 전체 대화가 5초 이내

            avg_turn_time = total_conversation_time / len(conversation_turns)
            print(f"📊 대화 총 시간: {total_conversation_time:.3f}초")
            print(f"📊 턴당 평균 시간: {avg_turn_time:.3f}초")

    @pytest.mark.asyncio
    async def test_batch_content_processing(self):
        """배치 컨텐츠 처리 성능 테스트"""
        # Given: 배치 처리할 컨텐츠들
        batch_contents = [
            "금융 뉴스 1: 금리 변동 소식",
            "금융 뉴스 2: 주식 시장 동향",
            "금융 뉴스 3: 환율 변화 분석",
            "금융 뉴스 4: 경제 지표 발표",
            "금융 뉴스 5: 기업 실적 분석",
        ]

        with patch("app.services.filter_service.ContentFilter") as mock_filter:
            filter_service = FilterService()
            filter_service.filter = mock_filter

            mock_filter.process = AsyncMock(
                return_value={
                    "is_safe": True,
                    "safety_score": 0.85,
                    "filtered_content": "필터링된 뉴스 내용",
                    "filter_reason": "",
                    "risk_categories": [],
                    "retry_count": 0,
                }
            )

            # When: 배치 처리
            batch_start = time.time()

            # 배치 처리 (동시 실행)
            batch_tasks = [filter_service.filter_response(content) for content in batch_contents]
            batch_results = await asyncio.gather(*batch_tasks)

            batch_time = time.time() - batch_start

            # Then: 배치 성능 검증
            assert len(batch_results) == len(batch_contents)
            assert all(result["content"] for result in batch_results)

            throughput = len(batch_contents) / batch_time
            print(f"📊 배치 처리: {len(batch_contents)}개 항목, {batch_time:.3f}초")
            print(f"📊 배치 처리량: {throughput:.1f} items/sec")
