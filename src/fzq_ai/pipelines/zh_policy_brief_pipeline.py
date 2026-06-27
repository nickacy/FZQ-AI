# -*- coding: utf-8 -*-
"""
ZhPolicyBriefPipeline (V15-Final)
中文政策解读 Pipeline（保留老版本全部能力 + 对齐 V15 架构）
"""

import json
from typing import Any, Dict

from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.pipelines.registry import PipelineRegistry
from fzq_ai.schemas.zh_tasks.zh_policy_brief import ZhPolicyBriefOutput
from fzq_ai.clients.model_client import ModelClient
from fzq_ai.utils.prompt_loader import load_prompt_template


# ⭐ 自动注册（版本号体系保留）
@PipelineRegistry.register("zh_policy_brief@v1", set_default=True)
class ZhPolicyBriefPipeline(BasePipeline[ZhPolicyBriefOutput]):
    """Pipeline: zh_policy_brief - Chinese policy brief extraction."""

    name = "zh_policy_brief"

    def __init__(self):
        super().__init__()
        # ⭐ 保留你原有的模型体系（glm-5.2）
        self.model = ModelClient("glm-5.2")

        # ⭐ 保留你原有的 prompt 模板体系
        self.system_prompt = load_prompt_template(
            "fzq_ai/prompts/zh/system_zh_intel.txt"
        )
        self.task_prompt = load_prompt_template(
            "fzq_ai/prompts/zh/zh_policy_brief.txt"
        )

    # ⭐ V15 要求：统一 async 接口
    async def run_async(self, **kwargs) -> ZhPolicyBriefOutput:
        """
        输入字段（保持老版本全部能力）：
        - doc_id
        - source
        - publish_date
        - title
        - content
        - related_docs
        - user_focus
        """

        input_payload: Dict[str, Any] = {
            "doc_id": kwargs.get("doc_id"),
            "source": kwargs.get("source"),
            "publish_date": kwargs.get("publish_date"),
            "title": kwargs.get("title"),
            "content": kwargs.get("content"),
            "related_docs": kwargs.get("related_docs", []),
            "user_focus": kwargs.get("user_focus", []),
        }

        # ⭐ Prompt 结构保持你原有的格式（非常优秀）
        prompt = (
            self.system_prompt
            + "\n\n---\n\n"
            + self.task_prompt
            + "\n\n---\n\n[INPUT DATA]\n"
            + json.dumps(input_payload, ensure_ascii=False, indent=2)
        )

        # ⭐ 调用模型（保持老版本 ModelClient）
        raw = await self.model.chat_async(prompt)

        # ⭐ JSON 解析（保留老版本的兜底机制）
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {
                "task_type": "zh_policy_brief",
                "status": "parse_error",
                "raw": raw,
            }

        # ⭐ 返回强类型 Schema（V15 要求）
        return ZhPolicyBriefOutput(**parsed)
