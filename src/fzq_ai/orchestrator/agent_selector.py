# src/fzq_ai/orchestrator/agent_selector.py
# V24-Final — Agent Selector
"""Auto-select the best agent for a given task type."""
from typing import Optional


AGENT_MAP = {
    "zh_risk_scan":        "deepseek-risk",
    "zh_policy_brief":     "deepseek-policy",
    "zh_opinion_landscape":"glm-opinion",
    "zh_multisource_merge":"deepseek-news",
    "news":                "deepseek-news",
    "narrative":           "deepseek-policy",
    "risk":                "deepseek-risk",
    "daily_report":        "deepseek-news",
    "en_research_brief":   "openai-research",
    "en_risk_scan":        "openai-research",
    "code_review":         "deepseek-news",
    "agent_planning":      "deepseek-policy",
    "default":             "deepseek-news",
}


def select_agent(task_type: str) -> str:
    """Return agent name for a task type. Falls back to default."""
    return AGENT_MAP.get(task_type, AGENT_MAP["default"])


def select_agent_for_intent(intent_text: str) -> str:
    """Guess agent from intent text keywords."""
    kw_map = {
        "风险": "deepseek-risk", "危机": "deepseek-risk", "threat": "openai-research",
        "政策": "deepseek-policy", "法规": "deepseek-policy", "policy": "deepseek-policy",
        "舆情": "glm-opinion", "舆论": "glm-opinion", "opinion": "glm-opinion",
        "新闻": "deepseek-news", "日报": "deepseek-news", "news": "deepseek-news",
        "合并": "deepseek-news", "融合": "deepseek-news",
        "代码": "deepseek-news", "code": "deepseek-news",
    }
    for kw, agent in kw_map.items():
        if kw in intent_text:
            return agent
    return "deepseek-news"
