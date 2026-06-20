"""
Base Pipeline with Metrics Instrumentation
带自动埋点的基础 Pipeline（中英文双语）
----------------------------------------------------
All pipelines inherit from this class.
It automatically records:
- system-level metrics
- provider-level metrics
- pipeline-level metrics

所有 Pipeline 都继承本类。
本类自动记录：
- 系统级指标
- Provider 级指标
- Pipeline 级指标
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict

from fzq_ai.metrics.metrics_store import metrics_store


class BasePipeline(ABC):
    """
    Base class for all pipelines.
    所有 Pipeline 的基础类。
    """

    pipeline_name: str = "base_pipeline"

    @abstractmethod
    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Each pipeline must implement this method.
        每个 Pipeline 必须实现此方法。
        """
        pass

    # ----------------------------------------------------
    # Wrapper with automatic metrics instrumentation
    # 自动埋点包装器
    # ----------------------------------------------------
    async def run_with_metrics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute pipeline with automatic metrics recording.
        执行 Pipeline，并自动记录指标。
        """
        start_time = time.time()
        error_occurred = False
        provider_used = None

        try:
            # 执行 Pipeline 主逻辑
            result = await self.run(payload)

            # 从返回结果中提取 provider（如果有）
            provider_used = result.get("provider")

            return result

        except Exception as e:
            error_occurred = True
            raise e

        finally:
            # 计算耗时
            latency_ms = (time.time() - start_time) * 1000

            # -------- System-level metrics --------
            metrics_store.record_request(
                latency_ms=latency_ms,
                error=error_occurred
            )

            # -------- Pipeline-level metrics --------
            metrics_store.record_pipeline_call(
                pipeline_name=self.pipeline_name,
                latency_ms=latency_ms,
                error=error_occurred
            )

            # -------- Provider-level metrics --------
            if provider_used:
                metrics_store.record_provider_call(
                    provider_name=provider_used,
                    latency_ms=latency_ms,
                    success=not error_occurred
                )
