# -*- coding: utf-8 -*-
"""
RiskScanAgent — 风险扫描智能体
负责调用风险类 Pipeline，执行风险识别、评估、预测任务。
"""

from __future__ import annotations

class RiskScanAgent:
    """Risk Scan Agent"""

    name = "RiskScanAgent"

    def run(self, model, text: str):
        """执行风险扫描任务"""
        prompt = f"Perform a geopolitical risk scan:\n{text}"
        return model(prompt)
