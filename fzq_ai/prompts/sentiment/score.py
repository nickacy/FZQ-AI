from fzq_ai.prompts.base.template import PromptTemplate

SENTIMENT_SCORE_TEMPLATE = PromptTemplate(
    """
请根据以下主题给出情绪倾向评分（-1 到 +1）：

主题：$query
"""
)
