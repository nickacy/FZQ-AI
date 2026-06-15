from __future__ import annotations
from typing import List
from fzq_ai.domain.models import IntelBundle, Article


class ReportAgent:
    """
    v3.0 Report Agent
    - 生成 Markdown 报告
    """

    def __init__(self, store=None):
        self.store = store

    def generate_markdown_report(self, topic: str, runs: int = 3) -> str:
        if not self.store:
            return f"# {topic} 报告\n\n无数据（store 未提供）。"

        bundles: List[IntelBundle] = self.store.load_latest(topic, limit=runs)

        if not bundles:
            return f"# {topic} 报告\n\n无数据。"

        all_articles: List[Article] = []
        for b in bundles:
            all_articles.extend(b.articles)

        regions = sorted({a.region for a in all_articles if a.region})
        region_summary = ", ".join(regions) if regions else "无区域信息"

        risk_levels = [a.risk_level for a in all_articles if a.risk_level is not None]
        avg_risk = sum(risk_levels) / len(risk_levels) if risk_levels else 0

        narratives = []
        for b in bundles:
            if b.narrative_summary:
                narratives.extend(b.narrative_summary.keys())
        narrative_summary = ", ".join(sorted(set(narratives))) if narratives else "无叙事信息"

        md = []
        md.append(f"# {topic} 报告\n")
        md.append(f"最近 {runs} 次运行\n")
        md.append(f"**涉及区域：** {region_summary}")
        md.append(f"**平均风险：** {avg_risk:.2f}")
        md.append(f"**叙事关键词：** {narrative_summary}\n")
        md.append("## 文章列表\n")

        for a in all_articles:
            md.append(f"- **{a.title_original}** — 风险 {a.risk_level}")

        return "\n".join(md)
