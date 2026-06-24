# src/fzq_ai/llm/orchestrator/repair/json_repairer.py

from __future__ import annotations
import json
from typing import Any, Dict

from fzq_ai.llm.orchestrator.repair.schema_repairer import SchemaRepairer
from fzq_ai.llm.orchestrator.repair.field_filler import FieldFiller
from fzq_ai.llm.orchestrator.repair.structure_fixer import StructureFixer
from fzq_ai.llm.orchestrator.repair.report import RepairReport


class JsonRepairer:
    """
    JSON 自愈修复器 v2
    - 修复 JSON 语法
    - 修复字段缺失
    - 修复字段类型
    - 修复嵌套结构
    - 对齐 Schema
    """

    def __init__(self):
        self.schema_repairer = SchemaRepairer()
        self.field_filler = FieldFiller()
        self.structure_fixer = StructureFixer()

    def repair(self, raw_output: str, schema: Any) -> Dict[str, Any]:
        report = RepairReport(raw_output)

        # 1. 尝试直接解析 JSON
        try:
            data = json.loads(raw_output)
        except Exception:
            data = self._repair_json_syntax(raw_output)
            report.add_step("json_syntax_fix", data)

        # 2. 修复字段缺失
        data = self.field_filler.fill_missing_fields(data, schema)
        report.add_step("field_fill", data)

        # 3. 修复嵌套结构
        data = self.structure_fixer.fix_structure(data, schema)
        report.add_step("structure_fix", data)

        # 4. Schema 对齐修复
        data = self.schema_repairer.align_schema(data, schema)
        report.add_step("schema_align", data)

        return {
            "fixed": data,
            "report": report.to_dict(),
        }

    def _repair_json_syntax(self, text: str) -> Dict[str, Any]:
        """
        v2: 简单 JSON 语法修复（可扩展）
        """
        # TODO: v3: 使用 Qwen 自动修复
        try:
            text = text.replace("\n", " ").replace("\t", " ")
            text = text.replace(",}", "}").replace(",]", "]")
            return json.loads(text)
        except Exception:
            return {}
