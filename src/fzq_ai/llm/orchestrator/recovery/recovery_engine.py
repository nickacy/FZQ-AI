# src/fzq_ai/llm/orchestrator/recovery/recovery_engine.py

from __future__ import annotations
from typing import Dict, Any

from fzq_ai.llm.orchestrator.recovery.error_classifier import ErrorClassifier
from fzq_ai.llm.orchestrator.recovery.retry_policy import RetryPolicy
from fzq_ai.llm.orchestrator.recovery.fallback_policy import FallbackPolicy
from fzq_ai.llm.orchestrator.recovery.repair_policy import RepairPolicy
from fzq_ai.llm.orchestrator.recovery.report import RecoveryReport


class ErrorRecoveryEngine:
    """
    LLM Error Recovery Engine v1
    - 自动分类错误
    - 自动重试
    - 自动 fallback
    - 自动 JSON/Schema 修复
    """

    def __init__(self):
        self.classifier = ErrorClassifier()
        self.retry_policy = RetryPolicy()
        self.fallback_policy = FallbackPolicy()
        self.repair_policy = RepairPolicy()

    async def recover(self, provider, task, raw_output, error=None):
        report = RecoveryReport(provider, raw_output, error)

        # 1. 错误分类
        error_type = self.classifier.classify(raw_output, error)
        report.add_step("error_classified", error_type)

        # 2. 重试策略
        if self.retry_policy.should_retry(error_type):
            new_output = await provider.run(task)
            report.add_step("retry", new_output)
            return {"output": new_output, "report": report.to_dict()}

        # 3. fallback 策略
        fallback_provider = self.fallback_policy.get_fallback(provider.name)
        if fallback_provider:
            new_output = await fallback_provider.run(task)
            report.add_step("fallback", new_output)
            return {"output": new_output, "report": report.to_dict()}

        # 4. JSON/Schema 修复策略
        repaired = self.repair_policy.repair(raw_output, task)
        report.add_step("repair", repaired)

        return {"output": repaired, "report": report.to_dict()}
