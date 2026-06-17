from fzq_ai.prompts.base.template import PromptTemplate

RISK_SUMMARY_TEMPLATE = PromptTemplate(
    """
你是一名风险分析专家，请根据以下主题生成风险摘要：

主题：$query
"""
)
