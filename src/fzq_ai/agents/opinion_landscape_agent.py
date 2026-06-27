# -*- coding: utf-8 -*-
"""
OpinionLandscapeAgent — 舆论分析智能体
负责舆情、叙事、公众观点分析。
"""

from __future__ import annotations

class OpinionLandscapeAgent:
    """Opinion Landscape Agent"""

    name = "OpinionLandscapeAgent"

    def run(self, model, text: str):
        prompt = f"Analyze public opinion landscape:\n{text}"
        return model(prompt)
