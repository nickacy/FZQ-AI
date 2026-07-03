# src/fzq_ai/llm/prompt_templates_v24.py
# V24-Final — Prompt Templates (versioned, auditable, extensible)
"""
All task types MUST use these templates via PromptEngine.build().
Version key: "v24" → future "v25" can add new templates.
"""
from __future__ import annotations

PROMPT_TEMPLATES: dict = {
    "v24": {

        # ── Chinese tasks ──
        "zh_risk_scan": (
            "你是一名金融风险分析专家。\n"
            "任务：{intent}\n"
            "上下文：{context}\n\n"
            "请输出结构化风险扫描结果，包含：overall_risk, key_risks, risk_level, recommendations。"
        ),

        "zh_policy_brief": (
            "你是一名政策分析专家。\n"
            "任务：{intent}\n"
            "上下文：{context}\n\n"
            "请输出结构化政策简报，包含：summary, key_points, impact_analysis, recommendations。"
        ),

        "zh_opinion_landscape": (
            "你是一名舆情分析专家。\n"
            "任务：{intent}\n"
            "上下文：{context}\n\n"
            "请输出舆情分析结果，包含：sentiment_overview, key_opinions, trend_analysis, risk_signals。"
        ),

        "zh_multisource_merge": (
            "你是一名信息融合专家。\n"
            "任务：{intent}\n"
            "上下文（多源信息）：{context}\n\n"
            "请将以上多源信息融合为统一情报报告，包含：merged_summary, source_analysis, consensus, divergences。"
        ),

        # ── English tasks ──
        "en_research_brief": (
            "You are a research analyst.\n"
            "Task: {intent}\n"
            "Context: {context}\n\n"
            "Please produce a structured research brief with: summary, key findings, implications, recommendations."
        ),

        "en_risk_scan": (
            "You are a risk analysis expert.\n"
            "Task: {intent}\n"
            "Context: {context}\n\n"
            "Please output a structured risk scan with: overall_risk, key_risks, risk_level, recommendations."
        ),

        # ── Generic ──
        "news": (
            "任务：{intent}\n上下文：{context}\n\n请生成中文情报摘要。"
        ),

        "narrative": (
            "任务：{intent}\n上下文：{context}\n\n请分析叙事框架。"
        ),

        "risk": (
            "任务：{intent}\n上下文：{context}\n\n请进行风险分析。"
        ),

        "daily_report": (
            "任务：{intent}\n上下文：{context}\n\n请生成日报。"
        ),

        "code_review": (
            "Task: {intent}\nContext: {context}\n\nPlease review the code and provide feedback."
        ),

        "agent_planning": (
            "Task: {intent}\nContext: {context}\n\nPlease create an execution plan."
        ),

        "default": (
            "任务：{intent}\n上下文：{context}\n\n请输出分析结果。"
        ),
    }
}
