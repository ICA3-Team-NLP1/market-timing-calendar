impact_prompt = """
You are given metadata about an economic indicator. Based on its economic nature and historical significance, estimate how much it is likely to impact the financial markets, particularly the stock market.

Classify the indicator's impact into one of the following levels:
- High
- Medium
- Low

[Indicator Information]
- Title: {title}
- Release Name: {name}
- Description (Notes): {notes}
- Source: {source}

👉 Respond with one of the following exact words: "High", "Medium", or "Low".
👉 Classify as "High" if the indicator is likely to move the market significantly upon release (e.g., Nonfarm Payrolls, CPI, Fed Interest Rate).
👉 Classify as "Medium" if the indicator can influence market sentiment but usually does not cause major moves.
👉 Classify as "Low" if it rarely has a noticeable impact on the financial markets.
"""

level_prompt = '''
You are given metadata about an economic indicator. Based on the following table, classify the indicator into the most appropriate level. If the indicator does not match any row in the table, classify as UNCATEGORIZED.

| Level | Name (KR/EN) | Description |
|-------|--------------|-------------|
| 1 | BEGINNER | 시장 반응도 높고, 실생활 비유 가능하며 반복 학습이 쉬운 지표 (예: FOMC, CPI, NFP, ISM 제조업 PMI, 소매판매, 기준금리 발표, MSCI 리밸런싱, 미시간대 소비자심리지수) |
| 2 | INTERMEDIATE | 금리/물가의 구조 이해 가능 지표 + 패턴 학습에 유리 (예: Core CPI, PPI, 신규 실업수당 청구, ISM 비제조업 PMI, 내구재 주문, 컨퍼런스보드 소비자신뢰지수, 근원 PCE, 연준 베이지북, 중국 GDP, 미국 GDP 속보치) |
| 3 | ADVANCED | 글로벌 연결관계 이해 가능 + 통합적 해석·전략 도출 가능 지표 (예: JOLTs 구인건수, LEI, 시카고 연은 국가활동지수, 개인소득/지출, M2, 10Y-2Y 금리차, 은행 대출 증가율, 중국 PMI, 미국 무역수지) |
| 4 | UNCATEGORIZED | 위 표에 해당하지 않는 기타 지표 |

[Indicator Information]
- Title: {title}
- Release Name: {name}
- Description (Notes): {notes}
- Source: {source}

👉 Respond in the following JSON format:
{{
  "level": "BEGINNER | INTERMEDIATE | ADVANCED | UNCATEGORIZED",
  "level_category": "지표명 (예: CPI, FOMC, ... 또는 UNCATEGORIZED)"
}}
- level: Choose one of the exact words above.
- level_category: Fill with the most appropriate indicator name (e.g., "CPI", "FOMC", etc.), or "UNCATEGORIZED" if not matched.
'''

description_ko_prompt = '''
주어진 경제 지표의 메타데이터를 바탕으로 한국어로 간결하고 이해하기 쉬운 설명을 작성해주세요.

[지표 정보]
- 제목: {title}
- 발표기관/시리즈명: {name}
- 원문 설명: {notes}
- 출처: {source}

👉 다음 가이드라인을 따라 한국어 설명을 작성해주세요:
1. **반드시 150자 이내로** 간결하게 작성 (공백 포함)
2. 1문장으로 핵심만 요약 (긴 문장 금지)
3. 일반인도 이해할 수 있는 쉬운 용어 사용
4. 해당 지표가 무엇을 측정하는지 명확히 설명
5. 불필요한 부가 설명이나 반복 금지

👉 한국어로만 응답하고, 추가 설명이나 서론 없이 설명문만 작성해주세요.
👉 글자 수 제한을 반드시 준수하세요 (150자 이내).
'''

# get_level_prompt_with_table는 level_prompt와 동일하게 사용하도록 alias로 지정
get_level_prompt_with_table = level_prompt