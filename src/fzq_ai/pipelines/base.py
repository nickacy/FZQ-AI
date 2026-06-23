# fzq_ai/pipelines/base.py
# FZQ‑AI v13 BasePipeline（统一 metrics + trace_id + sync/async 支持）

import time
import asyncio
from abc import ABC, abstractmethod
from fzq_ai.monitor.metrics import metrics


class BasePipeline(ABC):
    """
    v13 BasePipeline
    - 支持 sync / async 两种执行方式
    - 自动记录 pipeline 级 metrics
    - 支持 trace_id 贯通
    """

    @abstractmethod
    async def run_async(self, query: str, trace_id: str = None):
        """子类必须实现的异步方法"""
        pass

    def run(self, query: str, trace_id: str = None):
        """同步执行（内部自动调用 async）"""
        return asyncio.run(self.run_async(query, trace_id=trace_id))

    # ---------------------------------------------------------
    # v13 新增：统一 metrics 包装器
    # ---------------------------------------------------------
    async def run_with_metrics(self, payload: dict):
        """
        payload 示例：
        {
            "query": "...",
            "trace_id": "abc123"
        }
        """
        query = payload.get("query")
        trace_id = payload.get("trace_id")

        start = time.time()

        try:
            result = await self.run_async(query, trace_id=trace_id)
            success = True
        except Exception as e:
            result = {"error": str(e)}
            success = False

        duration_ms = (time.time() - start) * 1000

        # 记录 metrics
        metrics.record(
            name=self.__class__.__name__,
            duration_ms=duration_ms,
            extra={"trace_id": trace_id, "success": success},
        )

        return result
