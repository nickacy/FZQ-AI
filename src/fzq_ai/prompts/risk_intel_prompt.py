# fzq_ai/prompts/risk_intel_prompt.py

from fzq_ai.prompts.template import PromptTemplate

RISK_INTEL_TEMPLATE = PromptTemplate(
    """
你是一名风险分析专家，请根据以下主题生成风险评估：

主题：$query

相关新闻：
$context

请输出：
1. 主要风险点
2. 潜在影响
3. 未来 30 天的风险趋势预测
"""
)
