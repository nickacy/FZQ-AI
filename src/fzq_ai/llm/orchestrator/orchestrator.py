# src/fzq_ai/llm/orchestrator/orchestrator.py

from __future__ import annotations
from typing import Dict, Any

from fzq_ai.llm.orchestrator.strategies import ModelStrategy
from fzq_ai.llm.orchestrator.validators import OutputValidator
from fzq_ai.llm.orchestrator.repair import JsonRepairer
from fzq_ai.llm.orchestrator.audit import ConsistencyAuditor


class MultiModelOrchestrator:
    """
    V14 Multi-Model Orchestrator (MOC v1)
    - 主模型生成
    - 校验模型检查结构化输出
    - 修复模型修复 JSON / Schema mismatch
    - 审计模型检查逻辑一致性
    """

    def __init__(self, strategy: ModelStrategy):
        self.strategy = strategy
        self.validator = OutputValidator()
        self.repairer = JsonRepairer()
        self.auditor = ConsistencyAuditor()

    async def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute multi-model orchestration pipeline.
        """
        # 1. 主模型生成
        primary_model = self.strategy.primary(task)
        primary_output = await primary_model.run(task)

        # 2. 校验结构化输出
        if not self.validator.is_valid(primary_output):
            # 3. 修复 JSON / Schema mismatch
            repaired = self.repairer.repair(primary_output)
        else:
            repaired = primary_output

        # 4. 审计逻辑一致性
        audit_report = await self.auditor.audit(repaired, task)

        return {
            "output": repaired,
            "audit": audit_report,
            "model_used": primary_model.name,
        }
