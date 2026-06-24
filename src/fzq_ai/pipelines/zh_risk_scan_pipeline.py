"""
ZhRiskScanPipeline
"""
import json
from typing import Any, Dict, List

from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.pipelines.registry import PipelineRegistry
from fzq_ai.schemas.zh_tasks.zh_risk_scan import ZhRiskScanOutput
from fzq_ai.clients.model_client import ModelClient
from fzq_ai.utils.prompt_loader import load_prompt_template


@PipelineRegistry.register("zh_risk_scan@v1", set_default=True)
class ZhRiskScanPipeline(BasePipeline[ZhRiskScanOutput]):
    """Pipeline: zh_risk_scan - Chinese risk signal scanning."""

    def __init__(self):
        super().__init__()
        self.model = ModelClient("glm-5.2")
        self.system_prompt = load_prompt_template("fzq_ai/prompts/zh/system_zh_intel.txt")
        self.task_prompt = load_prompt_template("fzq_ai/prompts/zh/zh_risk_scan.txt")

    async def run_async(self, **kwargs) -> ZhRiskScanOutput:
        items: List[Dict[str, Any]] = kwargs.get("items", [])
        input_payload: Dict[str, Any] = {
            "scan_window": kwargs.get("scan_window"),
            "scope": kwargs.get("scope", []),
            "n": len(items),
            "items_json": json.dumps(items, ensure_ascii=False, indent=2),
            "entity_watchlist": kwargs.get("entity_watchlist", []),
        }

        # Build prompt: system prompt + task prompt + input data as JSON
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
                "task_type": "zh_risk_scan",
                "status": "parse_error",
                "raw": raw,
            }

        return ZhRiskScanOutput(**parsed)
