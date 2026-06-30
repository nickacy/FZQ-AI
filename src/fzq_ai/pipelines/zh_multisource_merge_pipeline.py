# src/fzq_ai/intel/pipelines/zh_multisource_merge_pipeline.py

from __future__ import annotations
from fzq_ai.pipelines.base import BasePipeline
from typing import Any, Dict

from fzq_ai.llm.model_router import ModelRouter


class ZhMultisourceMergePipeline(BasePipeline):
    def __init__(self):
        self.router = ModelRouter()

    async def run_async(self, **kwargs: Any) -> Dict[str, Any]:
        return await self.run(**kwargs)

    async def run(self, **kwargs: Any) -> Dict[str, Any]:
        req = kwargs.get("req") or kwargs.get("content") or kwargs.get("input") or kwargs.get("text")
        if isinstance(req, str):
            req = {"input": req}
        elif req is None:
            req = {"input": ""}

        provider = self.router.select("zh_multisource_merge")

        model_req = {
            "task_type": "zh_multisource_merge",
            "trace_id": req.get("trace_id") if isinstance(req, dict) else None,
            "messages": [
                {"role": "system", "content": "你是一个专业多源信息融合专家。"},
                {"role": "user", "content": req.get("input", "") if isinstance(req, dict) else str(req)},
            ],
        }

        result = await provider.run(model_req)

        return {
            "task": "zh_multisource_merge",
            "input": req.get("input", "") if isinstance(req, dict) else str(req),
            "output": result.get("output") or result.get("content", ""),
            "model": result.get("model", ""),
            "provider": result.get("provider", ""),
            "tokens": result.get("total_tokens") or result.get("usage", {}).get("total_tokens", 0),
        }

# Alias for registry compatibility
ZhMultiSourceMergePipeline = ZhMultisourceMergePipeline
