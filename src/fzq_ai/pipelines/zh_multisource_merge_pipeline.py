"""
ZhMultiSourceMergePipeline
"""
import json
from typing import Any, Dict, List

from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.pipelines.registry import PipelineRegistry
from fzq_ai.schemas.zh_tasks.zh_multisource_merge import ZhMultiSourceMergeOutput
from fzq_ai.clients.model_client import ModelClient
from fzq_ai.utils.prompt_loader import load_prompt_template


@PipelineRegistry.register("zh_multisource_merge@v1", set_default=True)
class ZhMultiSourceMergePipeline(BasePipeline[ZhMultiSourceMergeOutput]):
    """Pipeline: zh_multisource_merge - Multi-source news merging."""

    def __init__(self):
        super().__init__()
        self.model = ModelClient("glm-5.2")
        self.system_prompt = load_prompt_template("fzq_ai/prompts/zh/system_zh_intel.txt")
        self.task_prompt = load_prompt_template("fzq_ai/prompts/zh/zh_multisource_merge.txt")

    async def run_async(self, **kwargs) -> ZhMultiSourceMergeOutput:
        sources: List[Dict[str, Any]] = kwargs.get("sources", [])

        input_payload: Dict[str, Any] = {
            "event_topic": kwargs.get("event_topic"),
            "n": len(sources),
            "sources_json": json.dumps(sources, ensure_ascii=False, indent=2),
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
                "task_type": "zh_multisource_merge",
                "status": "parse_error",
                "raw": raw,
            }

        return ZhMultiSourceMergeOutput(**parsed)
