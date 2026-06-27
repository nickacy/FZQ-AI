"""
FZQ-AI Intent Engine
意图识别引擎 — classifies user text into task type.
----------------------------------------------------
输入: 自然语言文本
输出: (task_type, confidence, language_detected)
"""

from __future__ import annotations
import re
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass, field


@dataclass
class IntentResult:
    """意图识别结果"""
    task_type: str
    confidence: float
    language: str  # "zh" | "en"
    keywords_matched: List[str] = field(default_factory=list)
    alternative: Optional[str] = None


# ── Keyword patterns per task type ────────────────────────────────

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


# ── Language detection ────────────────────────────────────────────

def _detect_language(text: str) -> str:
    """Detect if text is primarily Chinese or English."""
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    en_words = len(re.findall(r'[a-zA-Z]+', text))
    if cn_chars > en_words * 0.5:
        return "zh"
    return "en"


# ── Intent classification ────────────────────────────────────────

def classify(text: str) -> IntentResult:
    """
    Classify user input into a task type.
    输入用户文本，返回意图识别结果。
    """
    lang = _detect_language(text)
    text_lower = text.lower()

    scores: Dict[str, Tuple[float, List[str]]] = {}

    for task_type, lang_patterns in _INTENT_PATTERNS.items():
        patterns = lang_patterns.get(lang, []) + lang_patterns.get("en", [])
        matched = [p for p in patterns if p.lower() in text_lower]
        score = len(matched) / max(len(patterns), 1)
        scores[task_type] = (score, matched)

    # Sort by score
    ranked = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)

    if not ranked or ranked[0][1][0] == 0:
        # No keyword match — default to daily_report
        return IntentResult(
            task_type="daily_report",
            confidence=0.1,
            language=lang,
            keywords_matched=[],
            alternative=None,
        )

    best_type, (best_score, best_keywords) = ranked[0]
    alt_type = ranked[1][0] if len(ranked) > 1 and ranked[1][1][0] > 0 else None

    return IntentResult(
        task_type=best_type,
        confidence=round(best_score, 3),
        language=lang,
        keywords_matched=best_keywords,
        alternative=alt_type,
    )


__all__ = ["IntentResult", "classify"]
