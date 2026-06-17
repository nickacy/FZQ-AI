# fzq_ai/pipelines/base_pipeline.py

import asyncio
from abc import ABC, abstractmethod


class BasePipeline(ABC):
    """
    Pipeline 抽象基类
    - 统一 run() / run_async() 接口
    - 子类只需要实现 async _run_async()
    """

    # 子类必须实现异步逻辑
    @abstractmethod
    async def _run_async(self, query: str):
        pass

    # 同步入口（保持旧行为）
    def run(self, query: str):
        try:
            return asyncio.run(self._run_async(query))
        except RuntimeError:
            # event loop 已存在（如 Streamlit）
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._run_async(query))

    # 异步入口（并发执行）
    async def run_async(self, query: str):
        return await self._run_async(query)
