# fzq_ai/pipelines/base_pipeline.py

import asyncio
import time
from abc import ABC, abstractmethod
from fzq_ai.monitor.metrics import metrics


class BasePipeline(ABC):

    @abstractmethod
    async def run_async(self, query: str):
        pass

    def run(self, query: str):
        return asyncio.run(self.run_async(query))

    async def _measure(self, name: str, coro):
        start = time.time()
        result = await coro
        duration = time.time() - start
        metrics.record(name=name, duration=duration)
        return result
