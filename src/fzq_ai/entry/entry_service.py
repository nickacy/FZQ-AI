# src/fzq_ai/entry/entry_service.py
# -*- coding: utf-8 -*-
"""
FZQ-AI Entry Service (V20)
统一入口层：HTTP / CLI / UI 都调用这里
"""

from __future__ import annotations
from typing import Dict, Any

from fzq_ai.intel.pipeline_registry import PipelineRegistry


class EntryService:
    """
    V20 统一入口服务：
    - 接收上层请求（UI / API）
    - 根据 task_type 选择 Pipeline
    - 调用 Pipeline.run()
    - 返回统一结果结构
    """

    def __init__(self):
        self.registry = PipelineRegistry()

    async def handle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        payload 示例：
        {
            "task_type": "zh_opinion_landscape",
            "input": "...",
            "trace_id": "...",
        }
        """
        task_type = payload["task_type"]
        pipeline = self.registry.get_pipeline(task_type)

        req = {
            "input": payload["input"],
            "trace_id": payload.get("trace_id"),
        }

        result = await pipeline.run(req)

        return {
            "task_type": task_type,
            "trace_id": payload.get("trace_id"),
            "data": result,
        }
