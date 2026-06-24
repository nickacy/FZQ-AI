# src/fzq_ai/llm/orchestrator/diff/field_diff.py

class FieldDiff:
    """
    字段差异分析：
    - 缺失字段
    - 多余字段
    """

    def compare(self, data, schema):
        issues = []

        schema_fields = set(schema.model_fields.keys())
        data_fields = set(data.keys())

        missing = schema_fields - data_fields
        extra = data_fields - schema_fields

        for f in missing:
            issues.append(f"缺失字段: {f}")

        for f in extra:
            issues.append(f"多余字段: {f}")

        return issues
