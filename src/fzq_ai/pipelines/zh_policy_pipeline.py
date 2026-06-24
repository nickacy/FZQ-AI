"""
ZhPolicyBriefPipeline
"""
import json
from typing import Any, Dict

from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.pipelines.registry import PipelineRegistry
from fzq_ai.schemas.zh_tasks.zh_policy_brief import ZhPolicyBriefOutput
from fzq_ai.clients.model_client import ModelClient
from fzq_ai.utils.prompt_loader import load_prompt_template


@PipelineRegistry.register("zh_policy_brief@v1", set_default=True)
class ZhPolicyBriefPipeline(BasePipeline[ZhPolicyBriefOutput]):
    """Pipeline: zh_policy_brief - Chinese policy brief extraction."""

    def __init__(self):
        super().__init__()
        self.model = ModelClient("glm-5.2")
        self.system_prompt = load_prompt_template("fzq_ai/prompts/zh/system_zh_intel.txt")
        self.task_prompt = load_prompt_template("fzq_ai/prompts/zh/zh_policy_brief.txt")

    async def run_async(self, **kwargs) -> ZhPolicyBriefOutput:
        input_payload: Dict[str, Any] = {
            "doc_id": kwargs.get("doc_id"),
            "source": kwargs.get("source"),
            "publish_date": kwargs.get("publish_date"),
            "title": kwargs.get("title"),
            "content": kwargs.get("content"),
            "related_docs": kwargs.get("related_docs", []),
            "user_focus": kwargs.get("user_focus", []),
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
            parsed = {"task_type": "zh_policy_brief", "status": "parse_error", "raw": raw}

        return ZhPolicyBriefOutput(**parsed)
