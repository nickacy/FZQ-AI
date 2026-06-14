"""
fzq_ai.pipelines.base

BasePipeline（异步版）：
- 统一日志
- 统一错误处理
- 统一 metrics
- 支持 trace_id
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from fzq_ai.domain.models import ServiceResult
from fzq_ai.metrics.recorder import metrics

logger = logging.getLogger(__name__)


class BasePipeline(ABC):
    """
    所有 Pipeline 的异步基类。
    子类只需实现 async run()。
    """

    @abstractmethod
    async def run(
        self, input_data: Any = None, trace_id: Optional[str] = None
    ) -> ServiceResult:
        raise NotImplementedError

    async def execute(
        self, input_data: Any = None, trace_id: Optional[str] = None
    ) -> ServiceResult:
        """
        包装 run()：
        - 记录耗时
        - 记录 metrics
        - 记录日志
        """
        pipeline_name = self.__class__.__name__
        start = time.time()

        logger.info(f"[{trace_id}] {pipeline_name} started")

        try:
            result = await self.run(input_data, trace_id=trace_id)
            elapsed = time.time() - start

            metrics.record(pipeline_name, elapsed, success=result.success)
            logger.info(f"[{trace_id}] {pipeline_name} finished in {elapsed:.3f}s")

            return result

        except Exception as e:
            elapsed = time.time() - start
            metrics.record(pipeline_name, elapsed, success=False)

            logger.error(f"[{trace_id}] {pipeline_name} failed: {e}", exc_info=True)

            return ServiceResult(
                success=False,
                error=str(e),
                error_code=f"{pipeline_name}_ERROR",
                metadata={"pipeline": pipeline_name},
            )
