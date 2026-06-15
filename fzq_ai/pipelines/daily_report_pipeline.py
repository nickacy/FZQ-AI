# fzq_ai/pipelines/daily_report_pipeline.py

from __future__ import annotations
from typing import List, Any, Optional

from fzq_ai.domain.models import ServiceResult,  Article, ServiceResult
from fzq_ai.pipelines.news_fetcher import fetch_all_news


class DailyReportPipeline:
    """
    每日报告生成管线（专业模板版）
    - 结构化 Markdown
    - 关键事件
    - 简单叙事分区（按 region）
    - 简单风险扫描
    """

    def __init__(self, llm_router: Any = None):
        self.llm_router = llm_router

    def run(
        self,
        query: str = "",
        articles: Optional[List[Article]] = None,
        summary: str | None = None,
    ) -> ServiceResult:
        """
        生成每日情报报告。
        如果未传入 articles，则自动从 news_fetcher 抓取新闻。
        返回 Markdown 字符串，可直接供 UI 显示。
        """
        if articles is None:
            articles = fetch_all_news(query)

        if not articles:
            return "# 📫 FZQ-AI 每日情报报告\n\n暂无数据，请检查新闻源配置或稍后重试。\n"

        # 1. 关键事件（前 10 条）
        top_titles = [a.title_original for a in articles[:10]]

        # 2. 简单叙事分区
        western = []
        east_asia = []
        middle_east = []
        other = []

        for a in articles:
            region = (a.region or "").lower()
            if region in ["western", "us", "europe"]:
                western.append(a.title_original)
            elif region in ["east_asia", "japan", "korea", "china"]:
                east_asia.append(a.title_original)
            elif region in ["middle_east"]:
                middle_east.append(a.title_original)
            else:
                other.append(a.title_original)

        # 3. 风险扫描（关键词）
        risk_words = [
            "war",
            "conflict",
            "attack",
            "missile",
            "crisis",
            "sanction",
            "inflation",
        ]
        risk_hits = []

        for a in articles:
            text = (a.title_original + " " + (a.content_original or "")).lower()
            if any(w in text for w in risk_words):
                risk_hits.append(a.title_original)

        risk_score = min(len(risk_hits) * 10, 100)

        # 4. 生成 Markdown 报告
        md = "# 📫 FZQ-AI 每日情报报告\n\n"

        md += "## 🌋 今日主题概览\n"
        if summary:
            md += summary + "\n\n"
        else:
            md += "（暂无摘要）\n\n"

        md += "## 🔳 关键事件（Top 10）\n"
        for t in top_titles:
            md += f"- {t}\n"
        md += "\n"

        md += "## 🌥 多阵营叙事概况\n"

        md += "### 西方叙事\n"
        if western:
            for t in western[:5]:
                md += f"- {t}\n"
        else:
            md += "- （暂无明显西方叙事）\n"
        md += "\n"

        md += "### 东亚叙事\n"
        if east_asia:
            for t in east_asia[:5]:
                md += f"- {t}\n"
        else:
            md += "- （暂无明显东亚叙事）\n"
        md += "\n"

        md += "### 中东叙事\n"
        if middle_east:
            for t in middle_east[:5]:
                md += f"- {t}\n"
        else:
            md += "- （暂无明显中东叙事）\n"
        md += "\n"

        md += "### 其他叙事\n"
        if other:
            for t in other[:5]:
                md += f"- {t}\n"
        else:
            md += "- （暂无其他显著叙事）\n"
        md += "\n"

        md += "## ⚠️ 风险扫描\n"
        md += f"- 综合风险评分：**{risk_score} / 100**\n"
        if risk_hits:
            md += "- 触发风险关键词的事件：\n"
            for t in risk_hits[:10]:
                md += f"  - {t}\n"
        else:
            md += "- 未发现明显风险信号\n"
        md += "\n"

        md += "## 📝 综合研判（自动生成草稿）\n"
        if risk_score >= 70:
            md += "- 当前整体风险水平偏高，需重点关注相关地区局势演变。\n"
        elif risk_score >= 40:
            md += "- 当前存在一定风险信号，建议持续跟踪相关议题与事件。\n"
        else:
            md += "- 当前整体风险水平较低，但仍需保持基础监测。\n"

        md += "- 建议结合内部情报与领域专家判断进行进一步分析。\n\n"

        md += "---\n由 FZQ-AI 自动生成（语义新闻 + 基础叙事 + 风险扫描）\n"

        return md


if __name__ == "__main__":
    print("Running DailyReportPipeline test...")
    pipeline = DailyReportPipeline()
    result = pipeline.run()
    print("Result:")
    print(result)
