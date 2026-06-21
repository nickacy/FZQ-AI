from fzq_ai.prompts.base.template import PromptTemplate

STORYLINE_TEMPLATE = PromptTemplate(
    """
请根据以下主题生成一条清晰的叙事线（storyline）：

主题：$query
"""
)
