from __future__ import annotations
from typing import Dict, Type

from fzq_ai.pipelines.base import BasePipeline

from fzq_ai.pipelines.zh_policy_pipeline import ZhPolicyBriefPipeline
from fzq_ai.pipelines.zh_risk_scan_pipeline import ZhRiskScanPipeline
from fzq_ai.pipelines.zh_opinion_landscape_pipeline import ZhOpinionLandscapePipeline
from fzq_ai.pipelines.zh_multisource_merge_pipeline import ZhMultiSourceMergePipeline


class PipelineRegistry:
    _REGISTRY: Dict[str, Type[BasePipeline]] = {}

    @classmethod
    def register_defaults(cls):
        cls.register("zh_policy_brief", ZhPolicyBriefPipeline)
        cls.register("zh_risk_scan", ZhRiskScanPipeline)
        cls.register("zh_opinion_landscape", ZhOpinionLandscapePipeline)
        cls.register("zh_multisource_merge", ZhMultiSourceMergePipeline)

    @classmethod
    def register(cls, name: str, pipeline_cls: Type[BasePipeline]):
        if not issubclass(pipeline_cls, BasePipeline):
            raise TypeError(f"{pipeline_cls} must inherit from BasePipeline")
        cls._REGISTRY[name] = pipeline_cls

    @classmethod
    def get(cls, name: str) -> BasePipeline:
        if name not in cls._REGISTRY:
            raise KeyError(f"Pipeline '{name}' not found in registry")
        return cls._REGISTRY[name]()

    @classmethod
    def list(cls):
        return list(cls._REGISTRY.keys())

    @classmethod
    def health(cls):
        return {
            name: {"ok": True, "class": cls._REGISTRY[name].__name__}
            for name in cls._REGISTRY
        }


PipelineRegistry.register_defaults()
