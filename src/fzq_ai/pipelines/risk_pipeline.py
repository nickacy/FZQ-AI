# fzq_ai/pipelines/risk_pipeline.py
# v13 RiskPipeline – 保留原业务逻辑 + 统一 v13 Pipeline 接口

from __future__ import annotations

import asyncio
from typing import Dict, Any

from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.prompts.template import PromptTemplate
from fzq_ai.pipelines.base import BasePipeline


RISK_SUMMARY_TEMPLATE = PromptTemplate("Generate a risk summary:\nTopic: $query")
RISK_FACTORS_TEMPLATE = PromptTemplate("List 5 key risk factors:\nTopic: $query")
RISK_FORECAST_TEMPLATE = PromptTemplate("Predict risk trend for next 30 days:\nTopic: $query")


class RiskPipeline(BasePipeline):
    name = "risk"

    def __init__(self):
        self.llm = LLMRouter()

    # ---------------------------------------------------------
    # v13 preprocess：构造 prompt 输入
    # ---------------------------------------------------------
    async def preprocess(self, req: Dict[str, Any]) -> Dict[str, Any]:
        query = req.get("query") or req.get("input", "")
        req["query"] = query
        req["task_type"] = "analysis"
        return req

    # ---------------------------------------------------------
    # v13 postprocess：结构化输出
    # ---------------------------------------------------------
    async def postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        # result 是 orchestrator/router 的单次输出
        # 但 risk_pipeline 是多子任务 → 我们在 preprocess 后自己执行并发任务
        return result

    # ---------------------------------------------------------
    # v13 orchestrator 会调用 pipeline.run(req)
    # 我们在这里执行并发 LLM 调用
    # ---------------------------------------------------------
    async def run(self, req: Dict[str, Any]) -> Dict[str, Any]:
        query = req.get("query", "")

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
