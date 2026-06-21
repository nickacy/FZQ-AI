from fzq_ai.prompts.base.template import PromptTemplate

SENTIMENT_SUMMARY_TEMPLATE = PromptTemplate(
    """
请根据以下主题生成情绪倾向总结（正面/中性/负面）并说明原因：

主题：$query
"""
)
