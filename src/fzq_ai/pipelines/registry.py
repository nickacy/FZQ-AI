from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Type

from fzq_ai.pipelines.base import BasePipeline

# from fzq_ai.pipelines.zh_policy_brief_pipeline import ZhPolicyBriefPipeline  # [V19: lazy import in register_defaults()]
# from fzq_ai.pipelines.zh_risk_scan_pipeline import ZhRiskScanPipeline  # [V19: lazy import in register_defaults()]
# from fzq_ai.pipelines.zh_opinion_landscape_pipeline import ZhOpinionLandscapePipeline  # [V19: lazy import in register_defaults()]
# from fzq_ai.pipelines.zh_multisource_merge_pipeline import ZhMultiSourceMergePipeline  # [V19: lazy import in register_defaults()]


class PipelineRegistry:
    _REGISTRY: Dict[str, Type[BasePipeline]] = {}
    _DEFAULT: str = None

    @classmethod
    def register_defaults(cls):
        # Lazy imports to avoid circular dependency with zh_*_pipeline modules
        from fzq_ai.pipelines.zh_policy_brief_pipeline import ZhPolicyBriefPipeline
        from fzq_ai.pipelines.zh_risk_scan_pipeline import ZhRiskScanPipeline
        from fzq_ai.pipelines.zh_opinion_landscape_pipeline import ZhOpinionLandscapePipeline
        from fzq_ai.pipelines.zh_multisource_merge_pipeline import ZhMultiSourceMergePipeline
        cls.register("zh_policy_brief", ZhPolicyBriefPipeline)
        cls.register("zh_risk_scan", ZhRiskScanPipeline)
        cls.register("zh_opinion_landscape", ZhOpinionLandscapePipeline)
        cls.register("zh_multisource_merge", ZhMultiSourceMergePipeline)

    @classmethod
    def register(cls, name: str, pipeline_cls: Type[BasePipeline] = None, **kwargs):
        """Register a pipeline class. Works as decorator or direct call."""
        set_default = kwargs.get('set_default', False)
        if pipeline_cls is None:
            def decorator(pc):
                if not issubclass(pc, BasePipeline):
                    raise TypeError(f"{pc} must inherit from BasePipeline")
                cls._REGISTRY[name] = pc
                if set_default:
                    cls._DEFAULT = name
                return pc
            return decorator
        if not issubclass(pipeline_cls, BasePipeline):
            raise TypeError(f"{pipeline_cls} must inherit from BasePipeline")
        cls._REGISTRY[name] = pipeline_cls
        if set_default:
            cls._DEFAULT = name

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


@dataclass
class PipelineEntry:
    """A registered pipeline with metadata."""
    name: str
    pipeline_cls: Type[BasePipeline]
    description: str = ""
    version: str = "v1"
    is_default: bool = False


def register_pipeline(name, pipeline_cls=None, description="", version="v1", default=False):
    """Convenience function: register a pipeline class or return a decorator."""
    return PipelineRegistry.register(name, pipeline_cls, set_default=default)


def get_pipeline(name: str):
    """Get an instance of a registered pipeline by name."""
    return PipelineRegistry.get(name)


def list_pipelines():
    """List all registered pipeline names."""
    return PipelineRegistry.list()


def create_pipeline(name: str, **kwargs):
    """Create and return a pipeline instance."""
    pipeline = get_pipeline(name)
    return pipeline


def get_pipeline_info(name: str):
    """Return metadata for a registered pipeline."""
    if name not in PipelineRegistry._REGISTRY:
        raise KeyError(f"Pipeline '{name}' not found")
    cls = PipelineRegistry._REGISTRY[name]
    return {
        "name": name,
        "class": cls.__name__,
        "module": cls.__module__,
        "is_default": PipelineRegistry._DEFAULT == name,
    }


