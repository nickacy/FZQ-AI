# pipelines/risk_scorer.py

class RiskScorer:
    """
    使用 DeepSeek 为新闻生成 3 个风险评分：
    1) 地缘风险（1–5）
    2) 市场影响（1–5）
    3) 社会稳定（1–5）
    """

    def __init__(self, llm):
        self.llm = llm

    def score(self, title, summary):
        prompt = f"""
你是一名全球风险分析师。请根据以下新闻内容给出三个评分（1–5）：

标题：{title}
摘要：{summary}

评分标准：
1 = 极低风险
2 = 低风险
3 = 中等风险
4 = 高风险
5 = 极高风险

请严格输出 JSON 格式：
{{
  "geopolitical_risk": x,
  "market_impact": x,
  "social_stability": x
}}
"""

        try:
            result = self.llm.ask(prompt)
            import json
            return json.loads(result)
        except:
            return {
                "geopolitical_risk": 3,
                "market_impact": 3,
                "social_stability": 3
            }
