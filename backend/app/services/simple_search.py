"""
SerpAPI를 활용한 웹 검색 기능
"""
import logging
import httpx
from app.core.config import settings
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


async def search_web(query: str) -> str:
    """
    SerpAPI를 활용한 웹 검색 - 실제 구글 검색 결과 반환

    Args:
        query: 검색 쿼리

    Returns:
        검색 결과 문자열
    """
    logger.info(f"🔍 SerpAPI 웹 검색: {query}")

    # API 키 체크
    if not settings.SERPAPI_API_KEY:
        return f"'{query}'에 대한 검색 실패"

    try:
        # SerpAPI 요청 파라미터
        params = {
            "engine": "google",
            "q": query,
            "api_key": settings.SERPAPI_API_KEY,
            "num": 3,  # 상위 3개 결과
            "hl": "ko",  # 한국어
            "gl": "kr",  # 한국 지역
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.SERPAPI_BASE_URL, params=params)
            response.raise_for_status()

            data = response.json()

            # 검색 결과 파싱
            search_results = _parse_serpapi_results(data, query)
            logger.info(f"✅ SerpAPI 검색 완료: {len(search_results)} 결과")

            return search_results

    except httpx.TimeoutException:
        logger.error("❌ SerpAPI 요청 타임아웃")
        return f"'{query}'에 대한 검색 실패"
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ SerpAPI HTTP 오류: {e.response.status_code}")
        return f"'{query}'에 대한 검색 실패"
    except Exception as e:
        logger.error(f"❌ SerpAPI 검색 실패: {e}")
        return f"'{query}'에 대한 검색 실패"


def _parse_serpapi_results(data: dict, query: str) -> str:
    """SerpAPI 응답 데이터를 파싱하여 문자열로 변환"""
    try:
        organic_results = data.get("organic_results", [])

        if not organic_results:
            return f"'{query}'에 대한 검색 결과를 찾을 수 없습니다."

        formatted_results = [f"🔍 '{query}' 검색 결과:\n"]

        for i, result in enumerate(organic_results[:3], 1):
            title = result.get("title", "제목 없음")
            snippet = result.get("snippet", "요약 없음")
            link = result.get("link", "")

            formatted_results.append(f"{i}. {title}")
            formatted_results.append(f"   - {snippet}")
            if link:
                formatted_results.append(f"   - 링크: {link}")
            formatted_results.append("")  # 빈 줄

        return "\n".join(formatted_results)

    except Exception as e:
        logger.error(f"❌ SerpAPI 결과 파싱 오류: {e}")
        return f"'{query}' 검색 결과 처리 중 오류가 발생했습니다."


async def search_web_with_agent(query: str) -> str:
    # langchain_openai.ChatOpenAI 사용
    try:
        llm = ChatOpenAI(model=settings.ACTIVE_LLM_MODEL, temperature=0)

        tools = load_tools(["serpapi"], llm=llm)
        agent_executor = create_react_agent(
            model=llm,
            tools=tools,
        )

        result = agent_executor.invoke({"messages": [HumanMessage(content=query)]})

        final_message = result["messages"][-1]
        return final_message.content

    except Exception as e:
        logger.error(f"❌ Agent 검색 실패: {e}")
        return f"'{query}' Agent 검색 중 오류가 발생했습니다."
