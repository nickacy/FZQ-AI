# fzq_ai/pipelines/base_pipeline.py

import asyncio
from abc import ABC, abstractmethod
from fzq_ai.pipelines.errors import PipelineError


class BasePipeline(ABC):

    @abstractmethod
    async def _run_async(self, query: str):
        pass

    async def _safe_run_async(self, query: str):
        """
        统一错误处理：所有 Pipeline 都通过这里执行
        """
        try:
            return await self._run_async(query)
        except Exception as e:
            return PipelineError(
                message=str(e),
                stage=self.__class__.__name__,
            )

    def run(self, query: str):
        try:
            return asyncio.run(self._safe_run_async(query))
        except RuntimeError:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._safe_run_async(query))

    async def run_async(self, query: str):
        return await self._safe_run_async(query)
