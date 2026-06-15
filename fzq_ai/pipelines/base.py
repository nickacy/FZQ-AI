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
    """

    @abstractmethod
    async def run(
        self, input_data: Any = None, trace_id: Optional[str] = None
        raise NotImplementedError

    async def execute(
        self, input_data: Any = None, trace_id: Optional[str] = None
        """
        """
        pipeline_name = self.__class__.__name__

        try:
            result = await self.run(input_data, trace_id=trace_id)
            elapsed = time.time() - start

            metrics.record(pipeline_name, elapsed, success=result.success)
            logger.info(f"[{trace_id}] {pipeline_name} finished in {elapsed:.3f}s")

            return result

        except Exception as e:

            return ServiceResult(
                success=False,
