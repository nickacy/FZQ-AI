"""
ZhMultiSourceMergePipeline (GLM‑5.2 stable version)
"""
import json
import re
from typing import Any, Dict, List

from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.pipelines.registry import PipelineRegistry
from fzq_ai.schemas.zh_tasks.zh_multisource_merge import ZhMultiSourceMergeOutput
from fzq_ai.clients.model_client import ModelClient
from fzq_ai.utils.prompt_loader import load_prompt_template


@PipelineRegistry.register("zh_multisource_merge@v1", set_default=True)
class ZhMultiSourceMergePipeline(BasePipeline[ZhMultiSourceMergeOutput]):
    """Pipeline: zh_multisource_merge - Multi-source news merging."""

    name = "zh_multisource_merge"

    def __init__(self):
        super().__init__()
        self.model = ModelClient("glm-5.2")
        self.system_prompt = load_prompt_template("fzq_ai/prompts/zh/system_zh_intel.txt")
        self.task_prompt = load_prompt_template("fzq_ai/prompts/zh/zh_multisource_merge.txt")

    # ------------------------------------------------------------
    # 1. Preprocess
    # ------------------------------------------------------------
    async def preprocess(self, req: Dict[str, Any]) -> Dict[str, Any]:
        sources: List[Dict[str, Any]] = req.get("sources", [])

        input_payload = {
            "event_topic": req.get("event_topic"),
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

        return {"prompt": prompt}

    # ------------------------------------------------------------
    # 2. LLM call
    # ------------------------------------------------------------
    async def call_llm(self, req: Dict[str, Any]) -> Dict[str, Any]:
        raw = await self.model.chat_async(req["prompt"])
        return {"raw": raw}

    # ------------------------------------------------------------
    # 3. JSON Cleaner
    # ------------------------------------------------------------
    def _clean_json(self, text: str) -> str:
        """
        Clean GLM‑5.2 output:
        - remove markdown fences
        - extract first {...} block
        - fix common JSON issues
        """
        # Remove markdown code fences
        text = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()

        # Extract first JSON object
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            text = match.group(0)

        # Replace full-width braces
        text = text.replace("｛", "{").replace("｝", "}")

        # Replace full-width colon
        text = text.replace("：", ":")

        # Remove trailing commas
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)

        return text

    # ------------------------------------------------------------
    # 4. Postprocess
    # ------------------------------------------------------------
    async def postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        raw = result.get("raw", "")

        cleaned = self._clean_json(raw)

        try:
            parsed = json.loads(cleaned)
        except Exception:
            # Fallback minimal structure
            parsed = {
                "task_type": "zh_multisource_merge",
                "status": "parse_error",
                "raw": raw,
            }

        # Pydantic validation
        try:
            model = ZhMultiSourceMergeOutput(**parsed)
            return model.dict()
        except Exception:
            return {
                "task_type": "zh_multisource_merge",
                "status": "schema_error",
                "raw": raw,
                "cleaned": cleaned,
            }
