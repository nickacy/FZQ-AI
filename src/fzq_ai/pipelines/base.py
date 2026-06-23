# src/fzq_ai/pipelines/base.py
# v13 BasePipeline – unified metrics, trace_id, sync/async execution

from __future__ import annotations

import time
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from fzq_ai.monitor.metrics import metrics


class BasePipeline(ABC):
    """
    v13 BasePipeline

    - 所有 Pipeline 必须继承此类
    - 统一 run() / run_async() 执行路径
    - 统一 metrics 记录
    - 统一 trace_id 贯通
    """

    pipeline_name: str = "base"

    # ---------------- Required override ----------------

    @abstractmethod
    async def run_async(self, context: Dict[str, Any], trace_id: Optional[str] = None) -> Any:
        """
        子类必须实现的异步执行方法。
        context: pipeline 输入上下文
        trace_id: 全链路追踪 ID
        """
        raise NotImplementedError

    # ---------------- Sync wrapper ----------------

    def run(self, context: Dict[str, Any], trace_id: Optional[str] = None) -> Any:
        """
        同步执行包装器（内部自动调用 async）。
        """
        return asyncio.run(self.run_async(context, trace_id=trace_id))

    # ---------------- v13 新增：统一 metrics 包装器 ----------------

    async def run_with_metrics(self, context: Dict[str, Any], trace_id: Optional[str] = None) -> Any:
        """
        v13 统一执行入口：
        - 自动记录 pipeline 执行耗时
        - 自动记录成功/失败
        - 自动写入 metrics.jsonl
        """
        start = time.time()
        success = True
        result = None

        try:
            result = await self.run_async(context, trace_id=trace_id)
        except Exception as e:
            success = False
            result = {"error": str(e)}

        duration_ms = (time.time() - start) * 1000

        # 写入 metrics
        metrics.record(
            name=self.pipeline_name,
            duration_ms=duration_ms,
            extra={
                "trace_id": trace_id,
                "success": success,
            },
        )

        return result
