# src/fzq_ai/llm/orchestrator/linter/schema_checker.py

import re

class SchemaChecker:
    """
    检查 Prompt Output Format 是否与 Pydantic Schema 对齐。
    """

    def check(self, prompt: str, schema):
        issues = []

        for field in schema.model_fields.keys():
            if field not in prompt:
                issues.append(f"字段缺失: {field}")

        # TODO: v2: 检查字段类型、嵌套结构
        return issues
