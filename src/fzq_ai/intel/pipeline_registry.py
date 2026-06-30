# src/fzq_ai/pipelines/pipeline_registry.py
# -*- coding: utf-8 -*-
"""
FZQ-AI Pipeline Registry (V19)
统一管理任务类型到具体 Pipeline 的映射
"""

from __future__ import annotations
from typing import Dict, Callable, Any

from fzq_ai.pipelines.zh_opinion_landscape_pipeline import ZhOpinionLandscapePipeline
from fzq_ai.pipelines.zh_risk_scan_pipeline import ZhRiskScanPipeline
from fzq_ai.pipelines.zh_policy_brief_pipeline import ZhPolicyBriefPipeline
from fzq_ai.pipelines.zh_multisource_merge_pipeline import ZhMultisourceMergePipeline


class PipelineRegistry:
    """
    V19 统一 Pipeline 注册表：
    - 按 task_type 选择对应 Pipeline
    - 提供简单的扩展点
    """

    def __init__(self):
        self._pipelines: Dict[str, Callable[[], Any]] = {
            "zh_opinion_landscape": ZhOpinionLandscapePipeline,
            "zh_risk_scan": ZhRiskScanPipeline,
            "zh_policy_brief": ZhPolicyBriefPipeline,
            "zh_multisource_merge": ZhMultisourceMergePipeline,
        }

    def get_pipeline(self, task_type: str) -> Any:
        factory = self._pipelines.get(task_type)
        if not factory:
            raise ValueError(f"Unknown task_type: {task_type}")
        return factory()
