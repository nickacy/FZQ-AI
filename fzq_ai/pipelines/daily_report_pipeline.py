# fzq_ai/pipelines/daily_report_pipeline.py

from typing import List
import asyncio

from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline
from fzq_ai.pipelines.scenario_pipeline import ScenarioPipeline

from fzq_ai.schemas.pipeline_output import (
    NewsPipelineOutput,
    NarrativePipelineOutput,
    RiskPipelineOutput,
    SentimentPipelineOutput,
    ScenarioPipelineOutput,
    DailyReportPipelineOutput,
)


class DailyReportPipeline(BasePipeline[DailyReportPipelineOutput]):
    """
    Phase 4‑2：全链路并发 DailyReportPipeline

    特点：
    - 继承 BasePipeline（统一 run / run_async）
    - 返回强类型 DailyReportPipelineOutput
    - 内部使用 asyncio.gather 并发执行 Risk / Sentiment / Scenario
    - News → Narrative 是顺序依赖（必须先跑 News）
    """

    def __init__(self) -> None:
        super().__init__()
        self.news_pipeline = NewsPipeline()
        self.narrative_pipeline = NarrativePipeline()
        self.risk_pipeline = RiskPipeline()
        self.sentiment_pipeline = SentimentPipeline()
        self.scenario_pipeline = ScenarioPipeline()

    async def run_async(
        self,
        topic: str,
        news_raw_texts: List[str],
    ) -> DailyReportPipelineOutput:
        """
        顶层异步入口：
        - 输入：topic（主题）、news_raw_texts（新闻原文列表）
        - 输出：DailyReportPipelineOutput（完整日报）
        """

        # ------------------------------------------------------------
        # 1. 先跑 NewsPipeline（必须先执行）
        # ------------------------------------------------------------
        news_result: NewsPipelineOutput = await self.news_pipeline.run_async(
            news_raw_texts=news_raw_texts
        )

        # NarrativePipeline 依赖新闻摘要
        combined_summary = "\n".join(news_result.summaries)

        # ------------------------------------------------------------
        # 2. 并发执行 Narrative / Risk / Sentiment / Scenario
        # ------------------------------------------------------------
        (
            narrative_result,
            risk_result,
            sentiment_result,
            scenario_result,
        ) = await asyncio.gather(
            self.narrative_pipeline.run_async(summary_text=combined_summary),
            self.risk_pipeline.run_async(topic=topic),
            self.sentiment_pipeline.run_async(topic=topic),
            self.scenario_pipeline.run_async(topic=topic),
        )

        # ------------------------------------------------------------
        # 3. 组装最终日报文本
        # ------------------------------------------------------------
        report_content = self._compose_report(
            topic=topic,
            news=news_result,
            narrative=narrative_result,
            risk=risk_result,
            sentiment=sentiment_result,
            scenario=scenario_result,
        )

        # ------------------------------------------------------------
        # 4. 返回强类型 Schema
        # ------------------------------------------------------------
        return DailyReportPipelineOutput(
            report_content=report_content,
            news_count=news_result.raw_input_count,
            task_status="completed",
        )

    # ------------------------------------------------------------
    # 报告组装逻辑（Phase 4‑4 会升级为 LLM 生成）
    # ------------------------------------------------------------
    def _compose_report(
        self,
        topic: str,
        news: NewsPipelineOutput,
        narrative: NarrativePipelineOutput,
        risk: RiskPipelineOutput,
        sentiment: SentimentPipelineOutput,
        scenario: ScenarioPipelineOutput,
    ) -> str:
        lines: List[str] = []

        lines.append(f"# 每日情报报告：{topic}")
        lines.append("")

        # --- 新闻摘要 ---
        lines.append("## 📰 新闻摘要")
        for idx, s in enumerate(news.summaries, start=1):
            lines.append(f"{idx}. {s}")
        lines.append("")

        # --- 叙事分析 ---
        lines.append("## 🧠 叙事分析")
        lines.append(narrative.narrative_text)
        lines.append("")

        # --- 风险分析 ---
        lines.append("## ⚠️ 风险分析")
        lines.append(risk.summary)
        lines.append("")
        lines.append("### 主要风险因素")
        lines.append(risk.factors)
        lines.append("")
        lines.append("### 风险趋势预测")
        lines.append(risk.forecast)
        lines.append("")

        # --- 情绪分析 ---
        lines.append("## 😊 情绪倾向")
        lines.append(f"情绪评分：{sentiment.score}")
        lines.append(sentiment.summary)
        lines.append("")

        # --- 情景推演 ---
        lines.append("## 🔮 情景推演")
        lines.append(scenario.scenarios)
        lines.append("")

        return "\n".join(lines)
