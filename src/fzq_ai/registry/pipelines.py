# src/fzq_ai/registry/pipelines.py
from __future__ import annotations

class PipelineRegistry:
    def __init__(self):
        self._pipelines = {}

    def register(self, name: str, pipeline_cls):
        self._pipelines[name] = pipeline_cls

    def get(self, name: str):
        return self._pipelines.get(name)

    def all(self):
        return self._pipelines


global_registry = PipelineRegistry()
