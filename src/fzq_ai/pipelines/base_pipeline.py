import asyncio
from abc import ABC, abstractmethod

class BasePipeline(ABC):

    @abstractmethod
    async def run_async(self, query: str):
        pass

    def run(self, query: str):
        return asyncio.run(self.run_async(query))
