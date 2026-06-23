"""
ZhPolicyBriefPipeline
中英文双语版本
-----------------------------------------
This pipeline performs Chinese policy brief extraction.
该 Pipeline 用于执行中文政策解读与要点提炼任务。
"""

import json
from typing import Any, Dict

from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.pipelines.registry import PipelineRegistry
from fzq_ai.schemas.zh_tasks.zh_policy_brief import ZhPolicyBriefOutput
from fzq_ai.clients.model_client import ModelClient
from fzq_ai.utils.prompt_loader import load_prompt_template


@PipelineRegistry.register("zh_policy_brief@v1", set_default=True)
class ZhPolicyBriefPipeline(BasePipeline):
    """
    Pipeline: zh_policy_brief
    中文政策解读 Pipeline（v1）
    """

    def __init__(self):
        super().__init__()
        self.model = ModelClient("glm-5.2")  # 可切换为 deepseek / minimax / openai
        self.system_prompt = load_prompt_template("fzq_ai/prompts/zh/system_zh_intel.txt")
        self.task_prompt = load_prompt_template("fzq_ai/prompts/zh/zh_policy_brief.txt")

    async def run_async(self, **kwargs) -> ZhPolicyBriefOutput:
        """
        Execute zh_policy_brief task.
        执行 zh_policy_brief 中文政策解读任务。
        """

        # 1. Construct input JSON
        # 构造输入 JSON
        input_payload: Dict[str, Any] = {
            "doc_id": kwargs.get("doc_id"),
            "source": kwargs.get("source"),
            "publish_date": kwargs.get("publish_date"),
            "title": kwargs.get("title"),
            "content": kwargs.get("content"),
            "related_docs": kwargs.get("related_docs", []),
            "user_focus": kwargs.get("user_focus", []),
        }

        # 2. Build final prompt
        # 构造最终 Prompt
        prompt = self.task_prompt.format(
            system_prompt=self.system_prompt,
            **input_payload
        )

        # 3. Call model
        # 调用模型
        raw = await self.model.chat_async(prompt)

        # 4. Parse JSON
        # 解析 JSON
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"task_type": "zh_policy_brief", "status": "parse_error", "raw": raw}

        # 5. Convert to Pydantic model
        # 转换为 Pydantic 模型
        return ZhPolicyBriefOutput(**parsed)
