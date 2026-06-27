"""
ZhOpinionLandscapePipeline
"""
import json
from typing import Any, Dict, List

from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.pipelines.registry import PipelineRegistry
from fzq_ai.schemas.zh_tasks.zh_opinion_landscape import ZhOpinionLandscapeOutput
from fzq_ai.clients.model_client import ModelClient
from fzq_ai.utils.prompt_loader import load_prompt_template


@PipelineRegistry.register("zh_opinion_landscape@v1", set_default=True)
class ZhOpinionLandscapePipeline(BasePipeline[ZhOpinionLandscapeOutput]):
    """Pipeline: zh_opinion_landscape - Chinese opinion landscape analysis."""

    def __init__(self):
        super().__init__()
        self.model = ModelClient("glm-5.2")
        self.system_prompt = load_prompt_template("fzq_ai/prompts/zh/system_zh_intel.txt")
        self.task_prompt = load_prompt_template("fzq_ai/prompts/zh/zh_opinion_landscape.txt")

    async def run_async(self, **kwargs) -> ZhOpinionLandscapeOutput:
        items: List[Dict[str, Any]] = kwargs.get("items", [])
        platforms = list({item.get("platform", "unknown") for item in items})

        input_payload: Dict[str, Any] = {
            "topic": kwargs.get("topic"),
            "time_range": kwargs.get("time_range"),
            "n": len(items),
            "platforms": ", ".join(platforms),
            "items_json": json.dumps(items, ensure_ascii=False, indent=2),
        }

        prompt = (
            self.system_prompt
            + "\n\n---\n\n"
            + self.task_prompt
            + "\n\n---\n\n[INPUT DATA]\n"
            + json.dumps(input_payload, ensure_ascii=False, indent=2)
        )

        raw = await self.model.chat_async(prompt)

        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {
                "task_type": "zh_opinion_landscape",
                "status": "parse_error",
                "raw": raw,
            }

        return ZhOpinionLandscapeOutput(**parsed)
