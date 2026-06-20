"""
ZhMultiSourceMergePipeline
中英文双语版本
-----------------------------------------
This pipeline performs multi-source news merging and perspective comparison.
该 Pipeline 用于执行多源新闻去重与视角差异分析任务：
- 事件主轴抽取（5W1H）
- 多源视角差异矩阵
- 信源可靠性评分
- 一致性评分（0~1）
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
    """
    Pipeline: zh_multisource_merge
    中文多源新闻合并 Pipeline（v1）
    """

    def __init__(self):
        super().__init__()
        # 可切换为 deepseek / minimax / openai
        self.model = ModelClient("glm-5.2")

        # 加载通用 System Prompt + 任务 Prompt
        self.system_prompt = load_prompt_template("fzq_ai/prompts/zh/system_zh_intel.txt")
        self.task_prompt = load_prompt_template("fzq_ai/prompts/zh/zh_multisource_merge.txt")

    async def run_async(self, **kwargs) -> ZhMultiSourceMergeOutput:
        """
        Execute zh_multisource_merge task.
        执行 zh_multisource_merge 中文多源新闻合并任务。
        """

        sources: List[Dict[str, Any]] = kwargs.get("sources", [])

        # 1. Construct input JSON
        # 构造输入 JSON
        input_payload: Dict[str, Any] = {
            "event_topic": kwargs.get("event_topic"),
            "n": len(sources),
            "sources_json": json.dumps(sources, ensure_ascii=False, indent=2),
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
                "task_type": "zh_multisource_merge",
                "status": "parse_error",
                "raw": raw
            }

        # 5. Convert to Pydantic model
        # 转换为 Pydantic 模型
        return ZhMultiSourceMergeOutput(**parsed)
