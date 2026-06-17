from fzq_ai.prompts.base.template import PromptTemplate

SCENARIO_TEMPLATE = PromptTemplate(
    """
你是一名地缘政治情景分析专家，请根据以下主题生成 3 个未来 30 天的可能情景：

主题：$query

请输出：
1. 情景名称
2. 触发因素
3. 可能发展路径
4. 风险等级（低/中/高）
"""
)
