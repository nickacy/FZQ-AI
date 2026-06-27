# -*- coding: utf-8 -*-
"""
MultiSourceMergeAgent — 多源情报合并智能体
负责将多个来源的信息进行合并、聚合、综合分析。
"""

from __future__ import annotations

class MultiSourceMergeAgent:
    """Multi-Source Merge Agent"""

    name = "MultiSourceMergeAgent"

    def run(self, model, text: str):
        prompt = f"Merge and synthesize multi-source intelligence:\n{text}"
        return model(prompt)
