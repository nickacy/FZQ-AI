# -*- coding: utf-8 -*-
"""
PolicyBriefAgent — 政策解读智能体
负责调用政策类 Pipeline，执行政策分析、法规摘要任务。
"""

from __future__ import annotations

class PolicyBriefAgent:
    """Policy Brief Agent"""

    name = "PolicyBriefAgent"

    def run(self, model, text: str):
        prompt = f"Provide a policy brief:\n{text}"
        return model(prompt)
