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

level_prompt = """
You are given metadata about an economic indicator. Based on its complexity and the depth of understanding required, classify the indicator into one of the following learning levels:

- BEGINNER: Indicators with high market response, easily understood through real-life analogies, and suitable for repetitive learning
- INTERMEDIATE: Indicators that require understanding of interest rates/inflation structure and are advantageous for pattern learning
- ADVANCED: Indicators that require understanding of global connections and enable comprehensive interpretation and strategy development

[Indicator Information]
- Title: {title}
- Release Name: {name}
- Description (Notes): {notes}
- Source: {source}

👉 Respond with one of the following exact words: "BEGINNER", "INTERMEDIATE", or "ADVANCED".
👉 Classify as "BEGINNER" if the indicator is easily understandable with real-life analogies and has high market response (e.g., Employment data, Consumer Price Index).
👉 Classify as "INTERMEDIATE" if it requires understanding of interest rates/inflation structure and is good for pattern learning (e.g., Producer Price Index, Retail Sales).
👉 Classify as "ADVANCED" if it requires understanding of global connections and enables comprehensive interpretation and strategy development (e.g., Trade Balance, GDP components).
"""