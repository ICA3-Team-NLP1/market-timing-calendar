"""
Prompt Chaining 구조 테스트 및 사용 예시
"""
from app.core.prompts import (
    build_prompt,
    get_role_prompt,
    get_rule_prompt,
    get_style_and_restrictions,
    get_prompt_by_level_and_purpose,
    get_available_purposes,
    get_prompt_info
)
from app.constants import UserLevel


class TestPromptChaining:
    """Prompt Chaining 구조 테스트"""
    
    def test_role_prompt_generation(self):
        """역할 정의 체인 테스트"""
        beginner_role = get_role_prompt(UserLevel.BEGINNER)
        intermediate_role = get_role_prompt(UserLevel.INTERMEDIATE)
        advanced_role = get_role_prompt(UserLevel.ADVANCED)
        
        # 각 레벨별로 다른 역할 정의가 생성되는지 확인
        assert "주린이" in beginner_role
        assert "관심러" in intermediate_role
        assert "실전러" in advanced_role
        
        # 모든 역할에 공통 요소가 포함되는지 확인
        assert "캐피(Capi)" in beginner_role
        assert "캐피(Capi)" in intermediate_role
        assert "캐피(Capi)" in advanced_role
    
    def test_rule_prompt_generation(self):
        """답변 규칙 체인 테스트"""
        # BEGINNER + general
        beginner_general = get_rule_prompt(UserLevel.BEGINNER, "general")
        assert "중학생도 이해할 수 있는" in beginner_general
        assert "일상생활 비유" in beginner_general
        
        # BEGINNER + event_explanation
        beginner_event = get_rule_prompt(UserLevel.BEGINNER, "event_explanation")
        assert "💡 한줄요약" in beginner_event
        assert "🏦 쉬운 설명" in beginner_event
        
        # ADVANCED + general
        advanced_general = get_rule_prompt(UserLevel.ADVANCED, "general")
        assert "전문적인 투자 용어" in advanced_general
        assert "회귀분석" in advanced_general
    
    def test_restrictions_generation(self):
        """스타일 + 금지사항 체인 테스트"""
        beginner_restrictions = get_style_and_restrictions(UserLevel.BEGINNER)
        intermediate_restrictions = get_style_and_restrictions(UserLevel.INTERMEDIATE)
        advanced_restrictions = get_style_and_restrictions(UserLevel.ADVANCED)
        
        # 모든 레벨에 공통 금지사항이 포함되는지 확인
        assert "특정 종목 추천" in beginner_restrictions
        assert "매매 타이밍 제안" in intermediate_restrictions
        assert "수익률 보장 표현" in advanced_restrictions
        
        # BEGINNER만 추가 금지사항이 있는지 확인
        assert "복잡한 계산이나 전문 통계 사용" in beginner_restrictions
    
    def test_build_prompt_chain(self):
        """최종 프롬프트 체이닝 테스트"""
        # BEGINNER + general
        beginner_prompt = build_prompt(UserLevel.BEGINNER, "general")
        assert "캐피(Capi)" in beginner_prompt
        assert "주린이" in beginner_prompt
        assert "중학생도 이해할 수 있는" in beginner_prompt
        assert "특정 종목 추천" in beginner_prompt
        
        # ADVANCED + event_explanation
        advanced_event_prompt = build_prompt(UserLevel.ADVANCED, "event_explanation")
        assert "실전러" in advanced_event_prompt
        assert "📈 핵심 Thesis" in advanced_event_prompt
        assert "🛡️ 헤지 전략" in advanced_event_prompt
    
    def test_utility_functions(self):
        """유틸리티 함수 테스트"""
        # 사용 가능한 목적 목록 확인
        purposes = get_available_purposes()
        assert "general" in purposes
        assert "event_explanation" in purposes
        assert len(purposes) == 2
        
        # 프롬프트 정보 구조 확인
        prompt_info = get_prompt_info(UserLevel.INTERMEDIATE, "event_explanation")
        assert "role" in prompt_info
        assert "rules" in prompt_info
        assert "restrictions" in prompt_info
        assert "full_prompt" in prompt_info
        
        # 각 구성 요소가 올바르게 포함되는지 확인
        assert "관심러" in prompt_info["role"]
        assert "📊 개념 정의" in prompt_info["rules"]
        assert "특정 종목 추천" in prompt_info["restrictions"]
    
    def test_prompt_by_level_and_purpose(self):
        """레벨과 목적별 프롬프트 생성 테스트"""
        # BEGINNER + event_explanation
        beginner_event = get_prompt_by_level_and_purpose(UserLevel.BEGINNER, "event_explanation")
        assert "주린이" in beginner_event
        assert "💡 한줄요약" in beginner_event
        assert "🏦 쉬운 설명" in beginner_event
        
        # ADVANCED + general
        advanced_general = get_prompt_by_level_and_purpose(UserLevel.ADVANCED, "general")
        assert "실전러" in advanced_general
        assert "전문적인 투자 용어" in advanced_general


# ============================================================================
# 🧠 실제 사용 예시
# ============================================================================

def example_usage():
    """Prompt Chaining 사용 예시"""
    
    print("=== 📌 Prompt Chaining 사용 예시 ===\n")
    
    # 1. 기본 사용법
    print("1️⃣ 기본 사용법:")
    prompt = build_prompt(UserLevel.INTERMEDIATE, "event_explanation")
    print(f"생성된 프롬프트 길이: {len(prompt)} 문자")
    print("✅ 성공\n")
    
    # 2. 구성 요소별 접근
    print("2️⃣ 구성 요소별 접근:")
    role = get_role_prompt(UserLevel.BEGINNER)
    rules = get_rule_prompt(UserLevel.BEGINNER, "general")
    restrictions = get_style_and_restrictions(UserLevel.BEGINNER)
    
    print(f"역할 정의 길이: {len(role)} 문자")
    print(f"답변 규칙 길이: {len(rules)} 문자")
    print(f"금지사항 길이: {len(restrictions)} 문자")
    print("✅ 성공\n")
    
    # 3. 유틸리티 함수 활용
    print("3️⃣ 유틸리티 함수 활용:")
    purposes = get_available_purposes()
    print(f"사용 가능한 목적: {purposes}")
    
    prompt_info = get_prompt_info(UserLevel.ADVANCED, "event_explanation")
    print(f"프롬프트 정보 키: {list(prompt_info.keys())}")
    print("✅ 성공\n")
    
    # 4. 조건부 로직 예시
    print("4️⃣ 조건부 로직 예시:")
    user_level = UserLevel.INTERMEDIATE
    is_explanation_needed = True
    
    if is_explanation_needed:
        purpose = "event_explanation"
    else:
        purpose = "general"
    
    final_prompt = build_prompt(user_level, purpose)
    print(f"조건부 생성된 프롬프트 길이: {len(final_prompt)} 문자")
    print("✅ 성공\n")
    
    print("=== 🎉 모든 예시 완료 ===")


if __name__ == "__main__":
    example_usage() 