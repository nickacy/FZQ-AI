from typing import Generic, TypeVar, Optional, List, Dict, Any
from fzq_ai.schemas.base import PipelineOutputSchema

T = TypeVar("T", bound=PipelineOutputSchema)

class BasePipeline(Generic[T]):
    """所有 Pipeline 的泛型基类

    v7.0 增强：
    - 可选的自动注册支持（通过 _pipeline_name 类属性）
    - 向后兼容：不设置 _pipeline_name 则行为不变
    - 支持新旧两套架构的 bridge

    使用：
        class NewsPipeline(BasePipeline[NewsOutput]):
            _pipeline_name = "news_v1"  # 可选：自动注册到 PipelineRegistry
            _pipeline_description = "News analysis v1"
            _pipeline_tags = ["news", "analysis"]

            async def run_async(self, *args, **kwargs) -> NewsOutput:
                ...
    """

    # v7.0: 可选的注册属性（子类可覆盖）
    _pipeline_name: Optional[str] = None
    _pipeline_version: Optional[str] = None
    _pipeline_description: str = ""
    _pipeline_tags: Optional[List[str]] = None
    _pipeline_dependencies: Optional[List[str]] = None

    async def run_async(self, *args, **kwargs) -> T:
        """子类必须实现"""
        raise NotImplementedError

    def run(self, *args, **kwargs) -> T:
        """同步入口（默认调用 run_async 的同步包装）

        子类可覆盖为纯同步实现。
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 在异步上下文中，创建新任务
                return asyncio.create_task(self.run_async(*args, **kwargs))
            return loop.run_until_complete(self.run_async(*args, **kwargs))
        except RuntimeError:
            # 无事件循环，创建新的
            return asyncio.run(self.run_async(*args, **kwargs))

    # v7.0: 注册到 PipelineRegistry（可选调用）
    @classmethod
    def register(cls, name: Optional[str] = None, **kwargs: Any):
        """将本类注册到 PipelineRegistry。

        可以在模块导入时自动调用，或显式调用。

        Args:
            name: 注册名，默认使用 cls._pipeline_name 或类名
            **kwargs: 传递给 PipelineRegistry.register 的额外参数

        示例：
            # 方式1：模块导入时自动注册
            NewsPipeline.register()

            # 方式2：显式注册（覆盖参数）
            NewsPipeline.register(
                name="news_v2",
                description="Enhanced news pipeline",
                set_default=True,
            )
        """
        from fzq_ai.pipelines.registry import PipelineRegistry

        reg_name = name or cls._pipeline_name or cls.__name__
        description = kwargs.pop("description", cls._pipeline_description)
        tags = kwargs.pop("tags", cls._pipeline_tags)
        dependencies = kwargs.pop("dependencies", cls._pipeline_dependencies)

        return PipelineRegistry.register(
            reg_name,
            description=description,
            tags=tags,
            dependencies=dependencies,
            **kwargs,
        )(cls)

