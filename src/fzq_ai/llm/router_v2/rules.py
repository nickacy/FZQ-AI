# src/fzq_ai/llm/router_v2/rules.py

TASK_RULES = {
    "zh_multisource_merge": ["glm-5.2", "qwen", "deepseek"],
    "zh_policy_brief": ["glm-5.2", "deepseek"],
    "zh_opinion_landscape": ["deepseek", "glm-5.2"],
    "zh_risk_scan": ["glm-5.2", "deepseek"],
}

LENGTH_RULES = [
    # (min_length, max_length, providers)
    (6000, 999999, ["kimi", "glm-5.2"]),
    (2000, 6000, ["glm-5.2", "deepseek"]),
    (0, 2000, ["glm-5.2", "deepseek", "qwen"]),
]

STRUCTURE_RULES = {
    "structured": ["glm-5.2", "qwen"],
    "reasoning": ["deepseek", "glm-5.2"],
    "json_repair": ["qwen"],
}
