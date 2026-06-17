from fzq_ai.prompts.base.template import PromptTemplate

KEYPOINTS_TEMPLATE = PromptTemplate(
    """
请根据以下主题生成 5 条关键要点：

主题：$query
"""
)
