# fzq_ai/pipelines/risk_pipeline.py
# v13 RiskPipeline 鈥?淇濈暀鍘熶笟鍔￠€昏緫 + 缁熶竴 v13 Pipeline 鎺ュ彛

from __future__ import annotations

import asyncio
from typing import Dict, Any

from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.prompts.template import PromptTemplate
from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.pipelines.registry import PipelineRegistry


RISK_SUMMARY_TEMPLATE = PromptTemplate("Generate a risk summary:\nTopic: $query")
RISK_FACTORS_TEMPLATE = PromptTemplate("List 5 key risk factors:\nTopic: $query")
RISK_FORECAST_TEMPLATE = PromptTemplate("Predict risk trend for next 30 days:\nTopic: $query")


@PipelineRegistry.register("risk@v1", set_default=True)
class RiskPipeline(BasePipeline):
    name = "risk"

    def __init__(self):
        self.llm = LLMRouter()

    # ---------------------------------------------------------
    # v13 preprocess锛氭瀯閫?prompt 杈撳叆
    # ---------------------------------------------------------
    async def preprocess(self, req: Dict[str, Any]) -> Dict[str, Any]:
        query = req.get("query") or req.get("input", "")
        req["query"] = query
        req["task_type"] = "analysis"
        return req

    # ---------------------------------------------------------
    # v13 postprocess锛氱粨鏋勫寲杈撳嚭
    # ---------------------------------------------------------
    async def postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        # result 鏄?orchestrator/router 鐨勫崟娆¤緭鍑?
        # 浣?risk_pipeline 鏄瀛愪换鍔?鈫?鎴戜滑鍦?preprocess 鍚庤嚜宸辨墽琛屽苟鍙戜换鍔?
        return result

    # ---------------------------------------------------------
    # v13 orchestrator 浼氳皟鐢?pipeline.run(req)
    # 鎴戜滑鍦ㄨ繖閲屾墽琛屽苟鍙?LLM 璋冪敤
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

