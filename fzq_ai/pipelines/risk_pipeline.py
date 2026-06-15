# fzq_ai/pipelines/risk_pipeline.py

from __future__ import annotations
from typing import List, Dict, Any, Optional

from fzq_ai.domain.models import ServiceResult,  Article, ServiceResult
from fzq_ai.pipelines.news_fetcher import fetch_all_news


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
                "election", "government", "sanction", "policy",
                "parliament", "protest", "coup", "regime",
            ],
            "economic": [
                "inflation", "recession", "market", "stock",
                "bond", "unemployment", "gdp", "tariff",
            ],
            "military": [
                "war", "conflict", "attack", "missile",
                "strike", "troop", "drone", "airstrike", "invasion",
            ],
            "social": [
                "riot", "violence", "crime", "unrest",
                "migration", "refugee", "protesters", "clash",
            ],
            "technology": [
                "cyber", "hack", "data breach", "ai",
                "chip", "sanctioned technology", "export control",
            ],
        }

    def run(
        self,
        topic: str = "",
        articles: Optional[List[Article]] = None,
        summary: str | None = None,
    ) -> ServiceResult:
        """
        风险扫描分析。
        - 如果传入 articles，直接分析
        - 如果只传入 topic，则根据 topic 抓取新闻后分析
        - 返回可读的文本结果
        """
        if articles is None:
            articles = fetch_all_news(topic)

        if not articles:
            return "暂无数据，无法进行风险扫描。请提供文章数据或有效的搜索关键词。"

        category_scores: Dict[str, int] = {k: 0 for k in self.risk_keywords.keys()}
        high_risk_items: List[Dict[str, Any]] = []

        for a in articles:
            text = (a.title_original + " " + (a.content_original or "")).lower()
            detected: List[str] = []

            for cat, kws in self.risk_keywords.items():
                if any(k.lower() in text for k in kws):
                    detected.append(cat)
                    category_scores[cat] += 1

            score = min(len(detected) * 25, 100) if detected else 0

            if score >= 50:
                high_risk_items.append({
                    "title": a.title_original,
                    "source": a.source_name,
                    "region": a.region,
                    "risk_categories": detected,
                    "risk_score": score,
                })

        total_score = sum(
            min(len(
                [cat for cat, kws in self.risk_keywords.items()
                 if any(k.lower() in (a.title_original + " " + (a.content_original or "")).lower() for k in kws)]
            ) * 25, 100)
            for a in articles
        )
        avg_score = round(total_score / max(len(articles), 1), 2)

        # 构建可读输出
        lines = ["# ⚠️ 风险扫描报告\n"]
        lines.append(f"**综合风险评分**: {avg_score} / 100\n")

        lines.append("## 各类别风险强度\n")
        category_labels = {
            "political": "🔄 政治风险",
            "economic": "💰 经济风险",
            "military": "⚔️ 军事风险",
            "social": "👥 社会风险",
            "technology": "🔬 科技风险",
        }
        for cat, label in category_labels.items():
            count = category_scores.get(cat, 0)
            bar = "█" * min(count, 20)
            lines.append(f"- {label}: {bar} ({count} 次命中)")

        lines.append("")
        lines.append("## 高风险条目（评分 ≥ 50）\n")
        if high_risk_items:
            for item in high_risk_items:
                lines.append(
                    f"- **{item['title']}** [{item['source']}] "
                    f"风险评分: {item['risk_score']}, "
                    f"类别: {', '.join(item['risk_categories'])}"
                )
        else:
            lines.append("- 暂无高风险条目\n")

        if avg_score >= 70:
            lines.append("\n### ⚠️ 研判：当前整体风险水平偏高，需重点关注相关地区局势演变。")
        elif avg_score >= 40:
            lines.append("\n### ⚠️ 研判：当前存在一定风险信号，建议持续跟踪。")
        else:
            lines.append("\n### ✅ 研判：当前整体风险水平较低，仍需保持基础监测。")

        return "\n".join(lines)


if __name__ == "__main__":
    print("Running RiskPipeline test...")
    pipeline = RiskPipeline()
    result = pipeline.run(topic="geopolitical risk")
    print("Result:")
    print(result)
