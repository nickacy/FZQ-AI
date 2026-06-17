from typing import Generic, TypeVar
from fzq_ai.schemas.base import PipelineOutputSchema

T = TypeVar("T", bound=PipelineOutputSchema)

class BasePipeline(Generic[T]):
    """所有 Pipeline 的泛型基类"""

    async def run_async(self, *args, **kwargs) -> T:
        """子类必须实现"""
        raise NotImplementedError
