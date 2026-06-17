from fzq_ai.prompts.base.template import PromptTemplate

RISK_FACTORS_TEMPLATE = PromptTemplate(
    """
请根据以下主题列出 5 个主要风险因素：

主题：$query
"""
)
