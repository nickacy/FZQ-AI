from fzq_ai.prompts.base.template import PromptTemplate

SUMMARY_TEMPLATE = PromptTemplate(
    """
你是一名新闻叙事分析专家，请根据以下主题生成简短摘要：

主题：$query
"""
)
