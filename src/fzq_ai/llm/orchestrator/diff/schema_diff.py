# src/fzq_ai/llm/orchestrator/diff/schema_diff.py

from __future__ import annotations
from typing import Any, Dict

from fzq_ai.llm.orchestrator.diff.field_diff import FieldDiff
from fzq_ai.llm.orchestrator.diff.type_diff import TypeDiff
from fzq_ai.llm.orchestrator.diff.structure_diff import StructureDiff
from fzq_ai.llm.orchestrator.diff.report import DiffReport


class SchemaDiffEngine:
    """
    Schema Diff Engine v1
    - 对比 Schema 与 Prompt
    - 对比 Schema 与 模型输出
    - 自动生成差异报告
    """

    def __init__(self):
        self.field_diff = FieldDiff()
        self.type_diff = TypeDiff()
        self.structure_diff = StructureDiff()

    def diff(self, data: Dict[str, Any], schema: Any) -> Dict[str, Any]:
        report = DiffReport(data)

        # 1. 字段差异
        field_issues = self.field_diff.compare(data, schema)
        report.add("fields", field_issues)

        # 2. 类型差异
        type_issues = self.type_diff.compare(data, schema)
        report.add("types", type_issues)

        # 3. 嵌套结构差异
        structure_issues = self.structure_diff.compare(data, schema)
        report.add("structure", structure_issues)

        return report.to_dict()
