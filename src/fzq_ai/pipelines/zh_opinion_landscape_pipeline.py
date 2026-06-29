from __future__ import annotations
from typing import Any, Dict

from fzq_ai.llm.model_router import ModelRouter


class ZhOpinionLandscapePipeline:
    def __init__(self):
        self.router = ModelRouter()

    async def run(self, req: Dict[str, Any]) -> Dict[str, Any]:
        provider = self.router.select("zh_opinion_landscape")

        model_req = {
            "task_type": "zh_opinion_landscape",
            "trace_id": req.get("trace_id"),
            "messages": [
                {"role": "system", "content": "你是一个专业舆情分析专家。"},
                {"role": "user", "content": req["input"]},
            ],
        }

        result = await provider.run(model_req)

        return {
            "task": "zh_opinion_landscape",
            "input": req["input"],
            "output": result["output"],
            "model": result["model"],
            "provider": result["provider"],
            "tokens": result["total_tokens"],
        }
