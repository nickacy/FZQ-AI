# src/fzq_ai/llm/orchestrator/linter/prompt_linter.py

from __future__ import annotations
from typing import Any, Dict

from fzq_ai.llm.orchestrator.linter.schema_checker import SchemaChecker
from fzq_ai.llm.orchestrator.linter.json_checker import JsonChecker
from fzq_ai.llm.orchestrator.linter.detectors import RiskDetector
from fzq_ai.llm.orchestrator.linter.report import LintReport


class PromptLinter:
    """
    Prompt Linter v2
    - Schema 对齐检查
    - JSON 格式检查
    - Prompt 风险点检测
    - 自动生成修复建议
    """

    def __init__(self):
        self.schema_checker = SchemaChecker()
        self.json_checker = JsonChecker()
        self.risk_detector = RiskDetector()

    def lint(self, prompt: str, schema: Any) -> Dict[str, Any]:
        report = LintReport(prompt)

        # 1. Schema 对齐检查
        schema_issues = self.schema_checker.check(prompt, schema)
        report.add("schema", schema_issues)

        # 2. JSON 格式检查
        json_issues = self.json_checker.check(prompt)
        report.add("json", json_issues)

        # 3. Prompt 风险点检测
        risk_issues = self.risk_detector.detect(prompt)
        report.add("risk", risk_issues)

        return report.to_dict()
