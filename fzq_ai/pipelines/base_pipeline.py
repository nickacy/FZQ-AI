# fzq_ai/pipelines/base_pipeline.py
"""v6.0 Unified BasePipeline - all pipelines MUST inherit this."""

import asyncio
import concurrent.futures
from abc import ABC, abstractmethod
from fzq_ai.domain.models import ServiceResult


class BasePipeline(ABC):
    """
    All Pipeline base class.
    - _run_async() -> ServiceResult (subclass implements)
    - _safe_run_async() -> ServiceResult (error handling wrapper)
    - run() -> ServiceResult (sync entry, safe across event loops)
    - run_async() -> ServiceResult (async entry, preferred)
    """

    @abstractmethod
    async def _run_async(self, *args, **kwargs) -> ServiceResult:
        """Subclass implements core async logic. MUST return ServiceResult."""
        ...

    async def _safe_run_async(self, *args, **kwargs) -> ServiceResult:
        """Unified error handling: all exceptions become ServiceResult.fail()"""
        try:
            result = await self._run_async(*args, **kwargs)
            if not isinstance(result, ServiceResult):
                return ServiceResult.ok(result)
            return result
        except Exception as e:
            return ServiceResult.fail(
                f"[{self.__class__.__name__}] {e}"
            )

    def run(self, *args, **kwargs) -> ServiceResult:
        """
        Sync entry: works whether or not an event loop is running.
        Uses ThreadPoolExecutor to avoid asyncio.run() nesting issues.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop running - use asyncio.run() directly
            return asyncio.run(self._safe_run_async(*args, **kwargs))

        # Event loop is running - use thread pool to avoid nesting
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(
                asyncio.run, self._safe_run_async(*args, **kwargs)
            )
            return future.result()

    async def run_async(self, *args, **kwargs) -> ServiceResult:
        """Async entry: preferred for use within orchestration."""
        return await self._safe_run_async(*args, **kwargs)
