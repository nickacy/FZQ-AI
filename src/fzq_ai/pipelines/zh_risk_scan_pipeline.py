"""
ZhRiskScanPipeline
中英文双语版本
-----------------------------------------
This pipeline performs Chinese risk signal scanning.
该 Pipeline 用于执行中文风险扫描任务（地缘 / 金融 / 舆情 / 合规 / 供应链 / 技术）。
"""

import json
from typing import Any, Dict, List

from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.pipelines.registry import PipelineRegistry
from fzq_ai.schemas.zh_tasks.zh_risk_scan import ZhRiskScanOutput
from fzq_ai.clients.model_client import ModelClient
from fzq_ai.utils.prompt_loader import load_prompt_template


@PipelineRegistry.register("zh_risk_scan@v1", set_default=True)
class ZhRiskScanPipeline(BasePipeline):
    """
    Pipeline: zh_risk_scan
    中文风险扫描 Pipeline（v1）
    """

    def __init__(self):
        super().__init__()
        # 可切换为 deepseek / minimax / openai
        self.model = ModelClient("glm-5.2")

        # 加载通用 System Prompt + 任务 Prompt
        self.system_prompt = load_prompt_template("fzq_ai/prompts/zh/system_zh_intel.txt")
        self.task_prompt = load_prompt_template("fzq_ai/prompts/zh/zh_risk_scan.txt")

    async def run_async(self, **kwargs) -> ZhRiskScanOutput:
        """
        Execute zh_risk_scan task.
        执行 zh_risk_scan 中文风险扫描任务。
        """

        # 1. Construct input JSON
        # 构造输入 JSON
        items: List[Dict[str, Any]] = kwargs.get("items", [])
        input_payload: Dict[str, Any] = {
            "scan_window": kwargs.get("scan_window"),
            "scope": kwargs.get("scope", []),
            "n": len(items),
            "items_json": json.dumps(items, ensure_ascii=False, indent=2),
            "entity_watchlist": kwargs.get("entity_watchlist", []),
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
                "task_type": "zh_risk_scan",
                "status": "parse_error",
                "raw": raw
            }

        # 5. Convert to Pydantic model
        # 转换为 Pydantic 模型
        return ZhRiskScanOutput(**parsed)
