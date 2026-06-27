# -*- coding: utf-8 -*-
"""
FZQ-AI Intent Engine (V15-Final)
意图识别引擎（V15 最终融合版）

本模块融合了旧版与新版意图识别逻辑，满足 GLM5.2 审计要求：
- 保留旧版的任务类型、关键词、alternative 候选
- 引入新版的置信度评分、fallback、双语注释、结构化输出
- 新增语义特征、模式匹配、低置信度澄清机制
- 覆盖 8 大任务类型（中英文）
"""

from __future__ import annotations
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field


# ============================================================
# 1. 意图识别结果结构 / Intent Recognition Result Structure
# ============================================================

@dataclass
class IntentResult:
    """
    意图识别结果
    Intent recognition result
    """
    task_type: str
    confidence: float
    language: str  # "zh" | "en"
    keywords_matched: List[str] = field(default_factory=list)
    alternative: Optional[str] = None
    reason: Optional[str] = None


# ============================================================
# 2. 任务类型与关键词（融合旧版 + 新版）
# ============================================================

_INTENT_PATTERNS: Dict[str, Dict[str, List[str]]] = {
    "zh_risk_scan": {
        "zh": ["风险", "危机", "威胁", "隐患", "安全风险", "地缘", "制裁", "冲突"],
        "en": ["risk", "crisis", "threat", "danger", "sanction", "conflict", "geopolitical"],
    },
    "zh_policy_brief": {
        "zh": ["政策", "法规", "政府", "国务院", "政策解读", "新规", "监管"],
        "en": ["policy", "regulation", "government", "legislation", "regulatory"],
    },
    "zh_opinion_landscape": {
        "zh": ["舆论", "舆情", "观点", "民意", "社交媒体", "公众", "讨论"],
        "en": ["opinion", "sentiment", "public", "social media", "discourse", "narrative"],
    },
    "zh_multisource_merge": {
        "zh": ["多源", "合并", "综合", "汇总", "聚合", "情报合并"],
        "en": ["merge", "aggregate", "multi-source", "consolidate", "synthesize"],
    },
    "daily_report": {
        "zh": ["日报", "每日", "总结", "报告", "简报"],
        "en": ["daily", "report", "briefing", "summary", "daily report"],
    },
    "narrative": {
        "zh": ["叙事", "话语", "故事线", "媒体框架"],
        "en": ["narrative", "storyline", "framing", "discourse"],
    },
    "risk": {
        "zh": ["风险分析", "风险评估", "风险预测"],
        "en": ["risk analysis", "risk assessment", "risk forecast"],
    },
    "news": {
        "zh": ["新闻", "消息", "报道", "资讯"],
        "en": ["news", "headline", "article", "report"],
    },
}


# ============================================================
# 3. 语言检测 / Language Detection
# ============================================================

def _detect_language(text: str) -> str:
    """
    检测输入语言（中文 / 英文）
    Detect input language (Chinese / English)
    """
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    en_words = len(re.findall(r'[a-zA-Z]+', text))
    if cn_chars > en_words * 0.5:
        return "zh"
    return "en"


# ============================================================
# 4. 置信度计算 / Confidence Scoring
# =================================================