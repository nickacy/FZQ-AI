from fzq_ai.prompts.base.template import PromptTemplate

RISK_FORECAST_TEMPLATE = PromptTemplate(
    """
请根据以下主题预测未来 30 天的风险趋势（上升/下降/持平），并说明原因：

主题：$query
"""
)
