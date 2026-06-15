# fzq_ai/intel/denoising_and_scoring.py

from __future__ import annotations
from typing import List, Dict
import re
import math

class DenoisingEngine:
    """
    """

    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""

        # 去 HTML

        # 去广告关键词
            "click here",
            "read more",
            "subscribe",
            "广告",
            "赞助",
            "follow us",
            "breaking:",
            "update:",
        for b in blacklist:

        # 去重复空格

        return text

class CredibilityScorer:
    """
    """

        "Reuters": 0.90,
        "BBC World": 0.88,
        "NHK Japan": 0.85,
        "Yonhap News": 0.82,
        "RT Russia": 0.55,
        "Telesur": 0.60,
        "News24 Africa": 0.75,
        "Xinhua English": 0.80,
        "Global Times": 0.65,

        "shocking",
        "outrage",
        "furious",
        "disaster",
        "crisis",
        "令人震惊",
        "愤怒",
        "灾难",
        "危机",

    @staticmethod
    def score(article) -> float:
        base = CredibilityScorer.SOURCE_BASE.get(article.source_name, 0.70)

        # 情绪化扣分
        emo_hits = sum(w in text for w in CredibilityScorer.EMOTION_WORDS)
        base -= emo_hits * 0.05

        # 夸张扣分
        ex_hits = sum(w in text for w in CredibilityScorer.EXAGGERATION)
        base -= ex_hits * 0.05

        # 信息密度（越长越可信）

        return max(0.0, min(1.0, base))

class BiasScorer:
    """
    """

        "clearly",
        "obviously",
        "显然",
        "毫无疑问",
        "must",
        "必须",
        "should",
        "应该",

    @staticmethod
    def score(article) -> float:
        text = article.content_original.lower()

        hits = sum(w in text for w in BiasScorer.BIAS_WORDS)

        return bias

class PropagandaTagger:
    """
    """

        "emotional": ["shocking", "furious", "令人震惊", "愤怒"],
        "nationalistic": ["our country", "敌对势力", "国家安全"],
        "fear": ["危机", "威胁", "恐惧"],

    @staticmethod
    def tag(article) -> List[str]:
        text = article.content_original.lower()
        tags = []

        for tag, words in PropagandaTagger.TAGS.items():
            if any(w in text for w in words):
                tags.append(tag)

        return tags
