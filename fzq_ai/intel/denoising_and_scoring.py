# fzq_ai/intel/denoising_and_scoring.py

from __future__ import annotations
from typing import List, Dict
import re
import math


class DenoisingEngine:
    """
    Phase 5.3 去噪引擎：
    - 去除广告、模板化句子、重复句子
    - 去除 HTML 标签
    - 去除无意义字符
    """

    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""

        # 去 HTML
        text = re.sub(r"<[^>]+>", "", text)

        # 去广告关键词
        blacklist = [
            "click here", "read more", "subscribe", "广告", "赞助",
            "follow us", "breaking:", "update:"
        ]
        for b in blacklist:
            text = text.replace(b, "")

        # 去重复空格
        text = re.sub(r"\s+", " ", text).strip()

        return text


class CredibilityScorer:
    """
    Phase 5.3 可信度评分：
    - 来源可信度（基础分）
    - 情绪化程度（扣分）
    - 夸张词汇（扣分）
    - 信息密度（加分）
    """

    SOURCE_BASE = {
        "Reuters": 0.90,
        "BBC World": 0.88,
        "NHK Japan": 0.85,
        "Yonhap News": 0.82,
        "RT Russia": 0.55,
        "Telesur": 0.60,
        "News24 Africa": 0.75,
        "Xinhua English": 0.80,
        "Global Times": 0.65,
    }

    EMOTION_WORDS = [
        "shocking", "outrage", "furious", "disaster", "crisis",
        "令人震惊", "愤怒", "灾难", "危机"
    ]

    EXAGGERATION = [
        "never before", "史无前例", "前所未有", "彻底崩溃"
    ]

    @staticmethod
    def score(article) -> float:
        base = CredibilityScorer.SOURCE_BASE.get(article.source_name, 0.70)

        text = article.content_original.lower()

        # 情绪化扣分
        emo_hits = sum(w in text for w in CredibilityScorer.EMOTION_WORDS)
        base -= emo_hits * 0.05

        # 夸张扣分
        ex_hits = sum(w in text for w in CredibilityScorer.EXAGGERATION)
        base -= ex_hits * 0.05

        # 信息密度（越长越可信）
        length_factor = min(len(text) / 800, 1.0)
        base += 0.1 * length_factor

        return max(0.0, min(1.0, base))


class BiasScorer:
    """
    Phase 5.3 偏见评分：
    - 情绪化词汇（加偏见）
    - 立场词汇（加偏见）
    - 单一视角（加偏见）
    """

    BIAS_WORDS = [
        "clearly", "obviously", "显然", "毫无疑问",
        "must", "必须", "should", "应该",
    ]

    @staticmethod
    def score(article) -> float:
        text = article.content_original.lower()

        hits = sum(w in text for w in BiasScorer.BIAS_WORDS)

        bias = min(0.1 + hits * 0.1, 1.0)
        return bias


class PropagandaTagger:
    """
    Phase 5.3 宣传标签：
    - 检测是否存在宣传性语言
    """

    TAGS = {
        "emotional": ["shocking", "furious", "令人震惊", "愤怒"],
        "nationalistic": ["our country", "敌对势力", "国家安全"],
        "fear": ["危机", "威胁", "恐惧"],
    }

    @staticmethod
    def tag(article) -> List[str]:
        text = article.content_original.lower()
        tags = []

        for tag, words in PropagandaTagger.TAGS.items():
            if any(w in text for w in words):
                tags.append(tag)

        return tags
