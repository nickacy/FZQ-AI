"""
ZhOpinionLandscapePipeline
中英文双语版本
-----------------------------------------
This pipeline performs Chinese opinion landscape analysis.
该 Pipeline 用于执行中文舆论版图分析任务：
- 阵营识别
- 立场聚类
- 话语框架分析
- 关键节点账号识别
- 热度趋势分析
"""

import json
from typing import Any, Dict, List

from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.pipelines.registry import PipelineRegistry
from fzq_ai.schemas.zh_tasks.zh_opinion_landscape import ZhOpinionLandscapeOutput
from fzq_ai.clients.model_client import ModelClient
from fzq_ai.utils.prompt_loader import load_prompt_template


@PipelineRegistry.register("zh_opinion_landscape@v1", set_default=True)
class ZhOpinionLandscapePipeline(BasePipeline):
    """
    Pipeline: zh_opinion_landscape
    中文舆论版图 Pipeline（v1）
    """

    def __init__(self):
        super().__init__()
        # 可切换为 deepseek / minimax / openai
        self.model = ModelClient("glm-5.2")

        # 加载通用 System Prompt + 任务 Prompt
        self.system_prompt = load_prompt_template("fzq_ai/prompts/zh/system_zh_intel.txt")
        self.task_prompt = load_prompt_template("fzq_ai/prompts/zh/zh_opinion_landscape.txt")

    async def run_async(self, **kwargs) -> ZhOpinionLandscapeOutput:
        """
        Execute zh_opinion_landscape task.
        执行 zh_opinion_landscape 中文舆论版图任务。
        """

        items: List[Dict[str, Any]] = kwargs.get("items", [])
        platforms = list({item.get("platform", "unknown") for item in items})

        # 1. Construct input JSON
        # 构造输入 JSON
        input_payload: Dict[str, Any] = {
            "topic": kwargs.get("topic"),
            "time_range": kwargs.get("time_range"),
            "n": len(items),
            "platforms": ", ".join(platforms),
            "items_json": json.dumps(items, ensure_ascii=False, indent=2),
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
            parsed = {
                "task_type": "zh_opinion_landscape",
                "status": "parse_error",
                "raw": raw
            }

        # 5. Convert to Pydantic model
        # 转换为 Pydantic 模型
        return ZhOpinionLandscapeOutput(**parsed)
