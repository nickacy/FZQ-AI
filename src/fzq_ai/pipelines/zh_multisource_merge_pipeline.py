# src/fzq_ai/intel/pipelines/zh_multisource_merge_pipeline.py

from __future__ import annotations
from typing import Any, Dict

from fzq_ai.core.model_router import ModelRouter


class ZhMultisourceMergePipeline:
    def __init__(self):
        self.router = ModelRouter()

    async def run(self, req: Dict[str, Any]) -> Dict[str, Any]:
        provider = self.router.select("zh_multisource_merge")

        model_req = {
            "task_type": "zh_multisource_merge",
            "trace_id": req.get("trace_id"),
            "messages": [
                {"role": "system", "content": "你是一个专业多源信息融合专家。"},
                {"role": "user", "content": req["input"]},
            ],
        }

        result = await provider.run(model_req)

        return {
            "task": "zh_multisource_merge",
            "input": req["input"],
            "output": result["output"],
            "model": result["model"],
            "provider": result["provider"],
            "tokens": result["total_tokens"],
        }
