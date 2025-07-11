category_prompt = """
You are given metadata about an economic indicator. Please classify it into one of the following 20 high-level categories. If the classification is unclear, respond with "Etc".

[Categories]
- GDP
- Employment & Labor
- Inflation
- Interest Rates
- Monetary Policy
- Retail & Consumer Spending
- Manufacturing & Industry
- Housing & Real Estate
- Trade & Exports
- Business Investment
- Government Spending & Debt
- Energy
- Financial Markets
- Productivity
- Consumer Sentiment & Confidence
- Education
- Healthcare
- Agriculture
- Transportation
- Banking & Credit

[Indicator Information]
- Title: {title}
- Release Name: {name}
- Description (Notes): {notes}
- Source: {source}

👉 Based on the above information, return the **single most appropriate category name exactly as listed above** (e.g., "GDP", "Inflation", etc.).  
👉 If you are not confident in the classification, return "Etc".
"""

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