# -*- coding: utf-8 -*-
"""
FZQ-AI Pipelines Registry (V19)
统一桥接到 src/fzq_ai/pipelines 下的真实 Pipeline 实现
"""

from __future__ import annotations
from typing import Dict, Optional

from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.pipelines.zh_policy_brief_pipeline import ZhPolicyBriefPipeline
from fzq_ai.pipelines.zh_risk_scan_pipeline import ZhRiskScanPipeline
from fzq_ai.pipelines.zh_opinion_landscape_pipeline import ZhOpinionLandscapePipeline
from fzq_ai.pipelines.zh_multisource_merge_pipeline import ZhMultiSourceMergePipeline


class PipelineRegistry:
    """
    Pipeline 注册表：
    - 管理所有可用 Pipeline
    - 提供按 task_type 解析 Pipeline 的能力
    - 统一走 src/fzq_ai/pipelines 下的实现
    """

    def __init__(self) -> None:
        self._registry: Dict[str, BasePipeline] = {}
        self._init_default_pipelines()

    def _init_default_pipelines(self) -> None:
        self.register("zh_policy_brief", ZhPolicyBriefPipeline())
        self.register("zh_risk_scan", ZhRiskScanPipeline())
        self.register("zh_opinion_landscape", ZhOpinionLandscapePipeline())
        self.register("zh_multisource_merge", ZhMultiSourceMergePipeline())

    def register(self, name: str, pipeline: BasePipeline) -> None:
        self._registry[name] = pipeline

    def resolve_pipeline(self, task_type: str) -> Optional[BasePipeline]:
        return self._registry.get(task_type)
