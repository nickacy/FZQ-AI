from __future__ import annotations
from typing import List, Dict
from fzq_ai.store.intel_store import IntelStore
from fzq_ai.domain.models import Article, IntelBundle


class ReportAgent:
    """
    v3.0 Report Agent
    - 生成 Markdown 报告
    """

    def __init__(self, store: IntelStore):
        self.store = store

    def generate_markdown_report(self, topic: str, runs: int = 3) -> str:
        """
        从 IntelStore 中读取最近 N 次运行结果，生成 Markdown 报告
        """
        bundles: List[IntelBundle] = self.store.load_latest(topic, limit=runs)

        if not bundles:
            return f"# {topic} 报告\n\n无数据。"

        # 收集所有文章
        all_articles: List[Article] = []
        for b in bundles:
            all_articles.extend(b.articles)

        # —— 1. 区域统计 ——
        regions_seen = set(a.region for a in all_articles if a.region)
        region_summary = ", ".join(sorted(regions_seen)) if regions_seen else "无区域信息"

        # —— 2. 风险统计 ——
        risk_levels = [a.risk_level for a in all_articles if a.risk_level is not None]
        avg_risk = sum(risk_levels) / len(risk_levels) if risk_levels else 0

        # —— 3. 叙事关键词 ——
        narratives = []
        for b in bundles:
            if b.narrative_summary:
                narratives.extend(b.narrative_summary.keys())
        narrative_summary = ", ".join(sorted(set(narratives))) if narratives else "无叙事信息"

        # —— 4. 构建 Markdown ——
        md = []
        md.append(f"# {topic} 报告")
        md.append("")
        md.append(f"最近 {runs} 次运行")
        md.append("")
        md.append(f"**涉及区域：** {region_summary}")
        md.append(f"**平均风险：** {avg_risk:.2f}")
        md.append(f"**叙事关键词：** {narrative_summary}")
        md.append("")
        md.append("## 文章列表")
        md.append("")

        for a in all_articles:
            md.append(f"- **{a.title_original}** ({a.region or '未知区域'}) — 风险 {a.risk_level}")

        return "\n".join(md)
