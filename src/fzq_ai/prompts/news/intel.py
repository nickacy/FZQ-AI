from fzq_ai.prompts.base.template import PromptTemplate

NEWS_INTEL_TEMPLATE = PromptTemplate(
    """
你是一名情报结构化分析专家，请根据以下新闻标题生成结构化 JSON：

主题：$query

新闻标题列表：
$context

请输出 JSON，字段包括：
- language
- regions
- events
- stats
"""
)
