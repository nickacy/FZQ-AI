# fzq_ai/pipelines/__init__.py
"""
Pipeline registry and all pipeline implementations.
Importing this module triggers registration of all pipelines.
"""

from fzq_ai.pipelines.registry import (
    PipelineRegistry,
    PipelineEntry,
    register_pipeline,
    get_pipeline,
    list_pipelines,
    create_pipeline,
    get_pipeline_info,
)
from fzq_ai.pipelines.protocol import PipelineProtocol, PipelineContext
from fzq_ai.pipelines.base import BasePipeline

# Import all pipelines to trigger @PipelineRegistry.register decorators
from fzq_ai.pipelines import news_pipeline          # noqa: F401
from fzq_ai.pipelines import narrative_pipeline     # noqa: F401
from fzq_ai.pipelines import risk_pipeline          # noqa: F401
from fzq_ai.pipelines import daily_report_pipeline  # noqa: F401
from fzq_ai.pipelines import sentiment_pipeline     # noqa: F401
from fzq_ai.pipelines import scenario_pipeline      # noqa: F401
from fzq_ai.pipelines import zh_risk_scan_pipeline          # noqa: F401
from fzq_ai.pipelines import zh_policy_brief_pipeline      # noqa: F401
from fzq_ai.pipelines import zh_opinion_landscape_pipeline  # noqa: F401
from fzq_ai.pipelines import zh_multisource_merge_pipeline  # noqa: F401

__all__ = [
    "PipelineRegistry",
    "PipelineEntry",
    "register_pipeline",
    "get_pipeline",
    "list_pipelines",
    "create_pipeline",
    "get_pipeline_info",
    "PipelineProtocol",
    "PipelineContext",
    "BasePipeline",
]
