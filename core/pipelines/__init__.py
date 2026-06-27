# -*- coding: utf-8 -*-
"""
FZQ-AI Pipelines Registry (V15-Minimal)
统一 Pipeline 接口 + 注册表
"""

from __future__ import annotations
from typing import Any, Dict


class BasePipeline:
    """
    所有 Pipeline 的统一基类接口
    """

    name: str = "base"

    async def run(self, input_text: str, intent: Any, route: Any) -> Any:
        """
        所有 pipeline 必须实现的统一接口
        """
        raise NotImplementedError("Pipeline.run() must be implemented.")


# ---- 示例 Pipeline 实现（最小可运行版） ----

class ZhPolicyBriefPipeline(BasePipeline):
    name = "zh_policy_brief"

    async def run(self, input_text: str, intent: Any, route: Any) -> Dict[str, Any]:
        return {
            "type": "policy_brief",
            "summary": f"政策简报（示例）：{input_text}",
        }


class ZhRiskScanPipeline(BasePipeline):
    name = "zh_risk_scan"

    async def run(self, input_text: str, intent: Any, route: Any) -> Dict[str, Any]:
        return {
            "type": "risk_scan",
            "risks": [f"风险点（示例）：{input_text}"],
        }


class ZhOpinionLandscapePipeline(BasePipeline):
    name = "zh_opinion_landscape"

    async def run(self, input_text: str, intent: Any, route: Any) -> Dict[str, Any]:
        return {
            "type": "opinion_landscape",
            "clusters": [f"舆情集群（示例）：{input_text}"],
        }


class ZhMultiSourceMergePipeline(BasePipeline):
    name = "zh_multisource_merge"

    async def run(self, input_text: str, intent: Any, route: Any) -> Dict[str, Any]:
        return {
            "type": "multisource_merge",
            "merged": f"多源合并结果（示例）：{input_text}",
        }


# ---- PipelineRegistry ----

class PipelineRegistry:
    """
    Pipeline 注册表：
    - 负责管理所有可用 Pipeline
    - 提供按 task_type 解析 Pipeline 的能力
    """

    def __init__(self) -> None:
        self._registry: Dict[str, BasePipeline] = {}
        self._init_default_pipelines()

    def _init_default_pipelines(self) -> None:
        # 注册默认的中文 Pipeline
        self.register("zh_policy_brief", ZhPolicyBriefPipeline)
        self.register("zh_risk_scan", ZhRiskScanPipeline)
        self.register("zh_opinion_landscape", ZhOpinionLandscapePipeline)
        self.register("zh_multisource_merge", ZhMultiSourceMergePipeline)

    def register(self, name: str, pipeline_cls: type[BasePipeline]) -> None:
        self._registry[name] = pipeline_cls()

    def get(self, name: str) -> BasePipeline | None:
        return self._registry.get(name)

    def resolve_pipeline(self, task_type: str) -> BasePipeline | None:
        """
        供 TaskRouter 调用：根据 task_type 返回对应 Pipeline
        """
        return self.get(task_type)
