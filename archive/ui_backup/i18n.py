# -*- coding: utf-8 -*-
"""
FZQ-AI UI i18n (V15-Final)
简单双语文本字典
"""

TEXTS = {
    "app.title": {
        "zh": "FZQ-AI 中文情报工作台",
        "en": "FZQ-AI Chinese Intelligence Workbench",
    },
    "app.subtitle": {
        "zh": "四大中文情报任务 · 政策 / 风险 / 舆论 / 多源合并",
        "en": "Four zh-intel tasks · Policy / Risk / Opinion / Multi-source merge",
    },
    "app.task_selector": {
        "zh": "选择任务类型",
        "en": "Select task type",
    },
    "app.input_label": {
        "zh": "请输入中文情报任务说明",
        "en": "Enter task description (Chinese intelligence)",
    },
    "app.run_button": {
        "zh": "执行任务",
        "en": "Run task",
    },
    "app.result_title": {
        "zh": "任务执行结果",
        "en": "Task result",
    },
    "app.error_prefix": {
        "zh": "发生错误：",
        "en": "Error: ",
    },
    "task.zh_policy_brief": {
        "zh": "中文政策解读（zh_policy_brief）",
        "en": "Chinese Policy Brief (zh_policy_brief)",
    },
    "task.zh_risk_scan": {
        "zh": "中文风险扫描（zh_risk_scan）",
        "en": "Chinese Risk Scan (zh_risk_scan)",
    },
    "task.zh_opinion_landscape": {
        "zh": "中文舆论版图（zh_opinion_landscape）",
        "en": "Chinese Opinion Landscape (zh_opinion_landscape)",
    },
    "task.zh_multisource_merge": {
        "zh": "中文多源新闻合并（zh_multisource_merge）",
        "en": "Chinese Multi-source Merge (zh_multisource_merge)",
    },
}


def t(key: str, lang: str = "zh") -> str:
    return TEXTS.get(key, {}).get(lang, TEXTS.get(key, {}).get("en", key))
