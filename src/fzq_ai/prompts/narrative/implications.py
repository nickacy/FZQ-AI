from fzq_ai.prompts.base.template import PromptTemplate

IMPLICATIONS_TEMPLATE = PromptTemplate(
    """
请根据以下主题分析未来 30 天的潜在影响：

主题：$query
"""
)
