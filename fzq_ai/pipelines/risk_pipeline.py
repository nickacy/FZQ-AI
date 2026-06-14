# fzq_ai/pipelines/risk_pipeline.py

from __future__ import annotations
from typing import List, Dict, Any

from fzq_ai.domain.models import Article, ServiceResult


class RiskPipeline:
    """
    风险分析管线（专业版）
    - 多维风险：政治 / 经济 / 军事 / 社会 / 科技
    - 每篇文章打标签 + 评分
    - 汇总整体风险画像
    """

    def __init__(self, llm_router: Any = None):
        self.llm_router = llm_router
        self.risk_keywords: Dict[str, List[str]] = {
            "political": [
                "election",
                "government",
                "sanction",
                "policy",
                "parliament",
                "protest",
                "coup",
                "regime",
            ],
            "economic": [
                "inflation",
                "recession",
                "market",
                "stock",
                "bond",
                "unemployment",
                "gdp",
                "tariff",
            ],
            "military": [
                "war",
                "conflict",
                "attack",
                "missile",
                "strike",
                "troop",
                "drone",
                "airstrike",
                "invasion",
            ],
            "social": [
                "riot",
                "violence",
                "crime",
                "unrest",
                "migration",
                "refugee",
                "protesters",
                "clash",
            ],
            "technology": [
                "cyber",
                "hack",
                "data breach",
                "ai",
                "chip",
                "sanctioned technology",
                "export control",
            ],
        }

    async def run(
        self,
        articles: List[Article],
        summary: str | None = None,
    ) -> ServiceResult:

        if not articles:
            return ServiceResult.fail("RiskPipeline 需要 articles 参数")

        items: List[Dict[str, Any]] = []
        category_scores: Dict[str, int] = {k: 0 for k in self.risk_keywords.keys()}

        for a in articles:
            text = (a.title_original + " " + (a.content_original or "")).lower()
            detected: List[str] = []

            for cat, kws in self.risk_keywords.items():
                if any(k.lower() in text for k in kws):
                    detected.append(cat)
                    category_scores[cat] += 1

            if detected:
                score = min(len(detected) * 25, 100)
            else:
                score = 0

            items.append(
                {
                    "id": a.id,
                    "title": a.title_original,
                    "source": a.source_name,
                    "region": a.region,
                    "risk_categories": detected,
                    "risk_score": score,
                    "url": a.url,
                }
            )

        # 汇总整体风险
        total_score = sum(i["risk_score"] for i in items)
        avg_score = total_score / max(len(items), 1)

        # 各类别强度（按命中次数）
        category_intensity = {
            cat: count for cat, count in category_scores.items() if count > 0
        }

        result = {
            "overall_risk_score": round(avg_score, 2),
            "category_intensity": category_intensity,
            "items": items,
        }

        return ServiceResult.ok(result)
