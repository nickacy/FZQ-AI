# fzq_ai/pipelines/risk_pipeline.py

import asyncio
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.prompts.template import PromptTemplate


RISK_SUMMARY_TEMPLATE = PromptTemplate(
    """
你是一名风险分析专家，请根据以下主题生成风险摘要：

主题：$query
"""
)

RISK_FACTORS_TEMPLATE = PromptTemplate(
    """
请根据以下主题列出 5 个主要风险因素：

主题：$query
"""
)

RISK_FORECAST_TEMPLATE = PromptTemplate(
    """
请根据以下主题预测未来 30 天的风险趋势（上升/下降/持平），并说明原因：

主题：$query
"""
)


class RiskPipeline:
    """
    RiskPipeline（增强版）
    - 保留旧行为（同步 run）
    - 新增 async run_async（并发执行 risk 子任务）
    """

    def __init__(self):
        self.llm = LLMRouter()

    # ---------------------------------------------------------
    # 同步入口（保持旧行为）
    # ---------------------------------------------------------
    def run(self, query: str):
        summary = asyncio.run(self.llm.route("risk_summary", RISK_SUMMARY_TEMPLATE.render(query=query)))
        factors = asyncio.run(self.llm.route("risk_factors", RISK_FACTORS_TEMPLATE.render(query=query)))
        forecast = asyncio.run(self.llm.route("risk_forecast", RISK_FORECAST_TEMPLATE.render(query=query)))

        return {
            "summary": summary,
            "factors": factors,
            "forecast": forecast,
        }

    # ---------------------------------------------------------
    # 异步入口（并发执行 risk 子任务）
    # ---------------------------------------------------------
    async def run_async(self, query: str):
        tasks = [
            self.llm.route("risk_summary", RISK_SUMMARY_TEMPLATE.render(query=query)),
            self.llm.route("risk_factors", RISK_FACTORS_TEMPLATE.render(query=query)),
            self.llm.route("risk_forecast", RISK_FORECAST_TEMPLATE.render(query=query)),
        ]

        summary, factors, forecast = await asyncio.gather(*tasks)

        return {
            "summary": summary,
            "factors": factors,
            "forecast": forecast,
        }
