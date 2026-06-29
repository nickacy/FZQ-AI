# -*- coding: utf-8 -*-
"""
FZQ-AI Entry Adapter (V17)
Bridges the Entry Layer to the Pipeline Registry.
"""

from __future__ import annotations
import uuid
import time
from typing import Any, Dict, Optional


class AdaptedPipeline:
    """A minimal pipeline wrapper returned by the adapted registry."""

    def __init__(self, name: str, task_type: str):
        self.name = name
        self.task_type = task_type

    async def run(
        self, input_text: str = "", intent=None, route=None
    ) -> Dict[str, Any]:
        """Simulate pipeline execution. Replace with real LLM call in production."""
        trace_id = str(uuid.uuid4())
        t0 = time.perf_counter()

        # Mock output based on task_type
        outputs = {
            "zh_risk_scan": {
                "task_type": "zh_risk_scan",
                "scan_window": None,
                "risks": [],
                "overall_risk_level": None,
                "entity_watchlist": [],
                "suggested_actions": [],
                "summary": None,
                "confidence": None,
            },
            "zh_policy_brief": {
                "task_type": "zh_policy_brief",
                "doc_id": None,
                "title": None,
                "summary": None,
                "key_points": [],
                "affected_entities": [],
                "policy_category": None,
                "confidence": None,
            },
            "zh_opinion_landscape": {
                "task_type": "zh_opinion_landscape",
                "clusters": [],
                "sentiment_distribution": {},
                "key_narratives": [],
                "influencer_map": {},
                "confidence": None,
            },
            "zh_multisource_merge": {
                "task_type": "zh_multisource_merge",
                "event_id": None,
                "conflict_sources": [],
                "resolved_sources": [],
                "consistency_score": None,
                "merged_narrative": None,
                "confidence": None,
            },
        }

        data = outputs.get(
            self.task_type,
            {"task_type": self.task_type},
        )
        data["trace_id"] = trace_id
        data["duration_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        data["status"] = "success"
        data["type"] = self.task_type
        return data


class AdaptedPipelineRegistry:
    """Minimal pipeline registry adapter for the entry layer."""

    def resolve_pipeline(self, task_type: str) -> Optional[AdaptedPipeline]:
        """Resolve a pipeline for the given task_type."""
        valid_types = [
            "zh_risk_scan",
            "zh_policy_brief",
            "zh_opinion_landscape",
            "zh_multisource_merge",
        ]
        if task_type in valid_types:
            return AdaptedPipeline(name=f"{task_type}_pipeline", task_type=task_type)
        # Fallback
        return AdaptedPipeline(name="base_pipeline", task_type=task_type)
