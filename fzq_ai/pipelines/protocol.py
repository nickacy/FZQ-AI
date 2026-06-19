"""
FZQ-AI Pipeline Protocol — 统一 Pipeline 接口定义

v7.0 新增：
为新旧两套 Pipeline 体系提供统一的 duck-typing 协议，
使 PipelineRegistry 可以统一处理所有 Pipeline，无论它们继承自哪个基类。

使用：
    from fzq_ai.pipelines.protocol import PipelineProtocol

    class MyPipeline(PipelineProtocol):
        async def run(self, input): ...
"""
from typing import Protocol, runtime_checkable, Any


@runtime_checkable
class PipelineProtocol(Protocol):
    """Pipeline 运行时协议（duck-typing）。

    任何实现了 run() 或 run_async() 方法的类都自动满足此协议，
    无需显式继承。

    新旧架构兼容：
    - 旧架构：BasePipeline[OutputSchema].run_async(*args, **kwargs) -> OutputSchema
    - 新架构：NewsPipeline.run(pipeline_input: PipelineInput) -> PipelineOutput
    - 未来架构：PluginPipeline.run(context: PipelineContext) -> Any
    """

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """同步执行入口（可选实现）。"""
        ...

    async def run_async(self, *args: Any, **kwargs: Any) -> Any:
        """异步执行入口（可选实现）。"""
        ...


class PipelineContext:
    """Pipeline 执行上下文（v7.0 预留，v8.0 DAG 用）。

    未来 DAG 执行时，每个节点接收一个 PipelineContext，包含：
    - input_data: 输入数据
    - upstream_outputs: 上游节点的输出
    - config: Pipeline 配置
    - metadata: 运行时元数据
    """

    def __init__(
        self,
        input_data: Any = None,
        upstream_outputs: dict = None,
        config: dict = None,
        metadata: dict = None,
    ):
        self.input_data = input_data
        self.upstream_outputs = upstream_outputs or {}
        self.config = config or {}
        self.metadata = metadata or {}

    def get_upstream(self, name: str) -> Any:
        """获取指定上游节点的输出。"""
        return self.upstream_outputs.get(name)

    def __repr__(self) -> str:
        return (
            f"PipelineContext(upstreams={list(self.upstream_outputs.keys())}, "
            f"config_keys={list(self.config.keys())})"
        )
